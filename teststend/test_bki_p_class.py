#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Алгоритм проверки
Тип блока	Производитель
БКИ	нет производителя
БКИ	Углеприбор
БКИ-П	Пульсар

"""

import sys
import logging

from time import sleep

from gen_func_utils import *
from my_msgbox import *
from gen_mb_client import *
from gen_mysql_connect import *
from gen_subtest import Subtest2in
from gen_exception import *

__all__ = ["TestBKIP"]


class TestBKIP:

    def __init__(self):
        self.resist = Resistor()
        self.ctrl_kl = CtrlKL()
        self.read_mb = ReadMB()
        self.mysql_conn = MySQLConnect()
        self.fault = Bug(None)
        self.subtest = Subtest2in()

        self.msg_1 = 'Переведите тумблер на блоке в режим «Предупредительный»'
        self.msg_2 = 'Переведите тумблер на блоке в режим «Аварийный»'

        logging.basicConfig(filename="C:\Stend\project_class\log\TestBKIP.log",
                            filemode="w",
                            level=logging.DEBUG,
                            encoding="utf-8",
                            format='[%(asctime)s: %(name)s: %(levelname)s] %(message)s')
        logging.getLogger('mysql').setLevel('DEBUG')
        self.logger = logging.getLogger(__name__)

    def st_test_1_bki_p(self):
        """
        Тест 1. Проверка исходного состояния блока
        """
        if self.subtest.subtest_2di(test_num=1, subtest_num=1.0, err_code_a1=30, err_code_a2=30,
                                    position_a1=True, position_a2=False, inp_1='in_a0', inp_2='in_a1'):
            return True
        return False

    def st_test_20_bki_p(self) -> bool:
        """
        Тест 2. Проверка работы блока при нормальном сопротивлении изоляции
        """
        self.logger.debug("старт теста 2.0")
        if my_msg(self.msg_1):
            self.logger.debug("от пользователя пришло подтверждение")
        else:
            self.logger.debug("от пользователя пришла отмена")
            return False
        self.ctrl_kl.ctrl_relay('KL21', True)
        self.logger.debug("включен KL21")
        sleep(2)
        self.resist.resist_kohm(220)
        sleep(2)
        if self.subtest.subtest_2di(test_num=2, subtest_num=2.0, err_code_a1=31, err_code_a2=31,
                                    position_a1=True, position_a2=False, inp_1='in_a0', inp_2='in_a1'):
            return True
        return False

    def st_test_30_bki_p(self) -> bool:
        """
        Тест 3. Проверка работы блока в режиме «Предупредительный» при снижении
        уровня сопротивлении изоляции до 100 кОм
        """
        self.logger.debug("старт теста 3.0")
        self.resist.resist_220_to_100_kohm()
        b = self.ctrl_kl.ctrl_ai_code_100()
        i = 0
        while b == 2 or i <= 10:
            sleep(0.2)
            i += 1
            b = self.ctrl_kl.ctrl_ai_code_100()
            if b == 0:
                break
            elif b == 1:
                self.mysql_conn.mysql_error(32)
                return False
        self.mysql_conn.mysql_ins_result("исправен", "3")
        return True

    def st_test_40_bki_p(self) -> bool:
        """
        Тест 4. Проверка работы блока в режиме «Аварийный» при сопротивлении изоляции 100 кОм
        """
        self.logger.debug("старт теста 4.0")
        if my_msg(self.msg_2):
            self.logger.debug("от пользователя пришло подтверждение")
        else:
            self.logger.debug("от пользователя пришла отмена")
            return False
        sleep(2)
        if self.subtest.subtest_2di(test_num=4, subtest_num=4.0, err_code_a1=33, err_code_a2=33,
                                    position_a1=True, position_a2=False, inp_1='in_a0', inp_2='in_a1'):
            return True
        self.ctrl_kl.ctrl_relay('KL21', False)
        self.logger.debug("отключен KL21")
        return False

    def st_test_50_bki_p(self) -> bool:
        """
        Тест 5. Работа блока в режиме «Аварийный» при сопротивлении изоляции
        ниже 30 кОм (Подключение на внутреннее сопротивление)
        """
        self.ctrl_kl.ctrl_relay('KL22', True)
        self.logger.debug("включен KL22")
        sleep(1)
        if self.subtest.subtest_2di(test_num=5, subtest_num=5.0, err_code_a1=34, err_code_a2=34,
                                    position_a1=False, position_a2=True, inp_1='in_a0', inp_2='in_a1'):
            self.ctrl_kl.ctrl_relay('KL21', False)
            self.logger.debug("отключен KL21")
            return True
        return False

    def st_test_bki_p(self) -> bool:
        if self.st_test_1_bki_p():
            if self.st_test_20_bki_p():
                if self.st_test_30_bki_p():
                    if self.st_test_40_bki_p():
                        if self.st_test_50_bki_p():
                            return True
        return False


if __name__ == '__main__':
    test_bki_p = TestBKIP()
    reset_test_bki_p = ResetRelay()
    mysql_conn_bki_p = MySQLConnect()
    fault = Bug(None)
    try:
        if test_bki_p.st_test_bki_p():
            mysql_conn_bki_p.mysql_block_good()
            my_msg('Блок исправен', 'green')
        else:
            mysql_conn_bki_p.mysql_block_bad()
            my_msg('Блок неисправен', 'red')
    except OSError:
        my_msg("ошибка системы", 'red')
    except SystemError:
        my_msg("внутренняя ошибка", 'red')
    except ModbusConnectException as mce:
        fault.debug_msg(mce, 'red')
        my_msg(f'{mce}', 'red')
    finally:
        reset_test_bki_p.reset_all()
        sys.exit()
