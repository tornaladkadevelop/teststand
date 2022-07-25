#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Тип блока     Производитель
БДУ-1М  Нет производителя
БДУ-1М  Пульсар
"""

import sys
import logging

from time import sleep

from gen_func_utils import *
from my_msgbox import *
from gen_mb_client import *
from gen_mysql_connect import *
from gen_subtest import SubtestBDU1M

__all__ = ["TestBDU1M"]


class TestBDU1M:

    def __init__(self):
        self.resist = Resistor()
        self.ctrl_kl = CtrlKL()
        self.read_mb = ReadMB()
        self.mysql_conn = MySQLConnect()
        self.fault = Bug(False)
        self.subtest = SubtestBDU1M()
        # C:\Stend\project_class
        logging.basicConfig(filename="C:\Stend\project_class\log\TestBDU1M.log",
                            filemode="w",
                            level=logging.DEBUG,
                            encoding="utf-8",
                            format='[%(asctime)s: %(name)s: %(levelname)s] %(message)s')
        logging.getLogger('mysql').setLevel('DEBUG')
        self.logger = logging.getLogger(__name__)

    def st_test_1_bdu_1m(self) -> bool:
        """
            Тест 1. Проверка исходного состояния блока
        """
        if self.subtest.subtest_inp_a2(test_num=1, subtest_num=1.0, err_code=199, position=False):
            return True
        return False

    def st_test_20_bdu_1m(self) -> bool:
        """
            Тест 2. Проверка включения / выключения блока от кнопки «Пуск / Стоп».
        """
        self.ctrl_kl.ctrl_relay('KL22', True)
        sleep(1)
        self.ctrl_kl.ctrl_relay('KL21', True)
        sleep(1)
        self.ctrl_kl.ctrl_relay('KL2', True)
        sleep(1)
        self.ctrl_kl.ctrl_relay('KL33', True)
        sleep(1)
        self.ctrl_kl.ctrl_relay('KL32', True)
        self.logger.debug("включены KL22, KL21, KL2, KL33, KL32")
        sleep(1)
        if self.subtest.subtest_inp_a2(test_num=2, subtest_num=2.0, err_code=201, position=False):
            return True
        return False

    def st_test_21_bdu_1m(self) -> bool:
        """
            2.2. Включение блока от кнопки «Пуск»
            2.3. Проверка удержания блока во включенном состоянии при подключении Rш пульта управления:
        """
        if self.subtest.subtest_a(test_num=2, subtest_num=2.1):
            if self.subtest.subtest_b(test_num=2, subtest_num=2.2):
                return True
        return False

    def st_test_23_bdu_1m(self) -> bool:
        """
            2.4. Выключение блока от кнопки «Стоп»
        """
        self.ctrl_kl.ctrl_relay('KL12', False)
        self.logger.debug("отключен KL12")
        sleep(2)
        if self.subtest.subtest_inp_a2(test_num=2, subtest_num=2.3, err_code_a2=207, position=False):
            self.ctrl_kl.ctrl_relay('KL25', False)
            self.ctrl_kl.ctrl_relay('KL1', False)
            self.ctrl_kl.ctrl_relay('KL22', True)
            self.logger.debug("отключен KL25, KL1 и включен KL22")
            return True
        return False

    def st_test_30_bdu_1m(self) -> bool:
        """
            3. подготовительные операции (повторение тестов 2.2 и 2.3)
        """
        if self.subtest.subtest_a(test_num=3, subtest_num=3.0):
            if self.subtest.subtest_b(test_num=3, subtest_num=3.1):
                return True
        return False

    def st_test_32_bdu_1m(self) -> bool:
        """
            3. Удержание исполнительного элемента при увеличении сопротивления цепи заземления до 50 Ом
        """
        self.resist.resist_10_to_20_ohm()
        sleep(3)
        if self.subtest.subtest_inp_a2(test_num=3, subtest_num=3.2, err_code=209, position=True):
            return True
        return False

    def st_test_40_bdu_1m(self) -> bool:
        """
            Тест 4. подготовительные операции (повторение тестов 2.2 и 2.3)
        """
        if self.subtest.subtest_a(test_num=4, subtest_num=4.0):
            if self.subtest.subtest_b(test_num=4, subtest_num=4.1):
                return True
        return False

    def st_test_42_bdu_1m(self) -> bool:
        """
            Тест 4. Отключение исполнительного элемента при увеличении сопротивления
            цепи заземления на величину свыше 50 Ом
        """
        self.resist.resist_10_to_100_ohm()
        sleep(2)
        if self.subtest.subtest_inp_a2(test_num=4, subtest_num=4.2, err_code=211, position=False):
            self.ctrl_kl.ctrl_relay('KL12', False)
            self.ctrl_kl.ctrl_relay('KL25', False)
            self.logger.debug("отключен KL12, KL25")
            return True
        return False

    def st_test_50_bdu_1m(self) -> bool:
        """
            Тест 5. подготовительные операции (повторение тестов 2.2 и 2.3)
        """
        if self.subtest.subtest_a(test_num=5, subtest_num=5.0):
            if self.subtest.subtest_b(test_num=5, subtest_num=5.1):
                return True
        return False

    def st_test_52_bdu_1m(self) -> bool:
        """
            5. Защита от потери управляемости при замыкании проводов ДУ
        """
        self.ctrl_kl.ctrl_relay('KL11', True)
        self.logger.debug("включен KL11")
        sleep(2)
        if self.subtest.subtest_inp_a2(test_num=5, subtest_num=5.2, err_code=213, position=False):
            self.ctrl_kl.ctrl_relay('KL12', False)
            self.ctrl_kl.ctrl_relay('KL1', False)
            self.ctrl_kl.ctrl_relay('KL25', False)
            self.ctrl_kl.ctrl_relay('KL11', False)
            self.logger.debug("отключены KL12, KL1, KL25, KL11")
            return True
        return False

    def st_test_60_bdu_1m(self) -> bool:
        """
            Тест 6. Защита от потери управляемости при обрыве проводов ДУ
        """
        if self.subtest.subtest_a(test_num=6, subtest_num=6.0):
            if self.subtest.subtest_b(test_num=6, subtest_num=6.1):
                return True
        return False

    def st_test_62_bdu_1m(self) -> bool:
        self.ctrl_kl.ctrl_relay('KL12', False)
        self.logger.debug("отключен KL12")
        sleep(2)
        if self.subtest.subtest_inp_a2(test_num=6, subtest_num=6.2, err_code=215, position=False):
            return True
        return False

    def st_test_bdu_1m(self):
        """
            главная функция которая собирает все остальные
        """
        if self.st_test_1_bdu_1m():
            if self.st_test_20_bdu_1m():
                if self.st_test_21_bdu_1m():
                    if self.st_test_23_bdu_1m():
                        if self.st_test_30_bdu_1m():
                            if self.st_test_32_bdu_1m():
                                if self.st_test_40_bdu_1m():
                                    if self.st_test_42_bdu_1m():
                                        if self.st_test_50_bdu_1m():
                                            if self.st_test_52_bdu_1m():
                                                if self.st_test_60_bdu_1m():
                                                    if self.st_test_62_bdu_1m():
                                                        return True
        return False


if __name__ == '__main__':
    test_bdu_1m = TestBDU1M()
    mysql_conn_test_bdu_1m = MySQLConnect()
    reset_test_bdu_1m = ResetRelay()
    fault = Bug(True)
    try:
        if test_bdu_1m.st_test_bdu_1m():
            mysql_conn_test_bdu_1m.mysql_block_good()
            my_msg('Блок исправен', 'green')
        else:
            mysql_conn_test_bdu_1m.mysql_block_bad()
            my_msg('Блок неисправен', 'red')
    except OSError:
        my_msg("ошибка системы", 'red')
    except SystemError:
        my_msg("внутренняя ошибка", 'red')
    except ModbusConnectException as mce:
        fault.debug_msg(mce, 'red')
        my_msg(f'{mce}', 'red')
    finally:
        reset_test_bdu_1m.reset_all()
        sys.exit()
