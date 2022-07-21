#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Алгоритм проверки
Тип блока Производитель
БДУ-4-2	  Нет производителя
БДУ-4-2	  ДонЭнергоЗавод
БДУ-4-2	  ИТЭП

"""

import sys
import logging

from time import sleep

from gen_func_utils import *
from my_msgbox import *
from gen_mb_client import *
from gen_mysql_connect import *
from gen_subtest import SubtestA1A2

__all__ = ["TestBDU42"]


class TestBDU42(object):

    def __init__(self):
        self.__resist = Resistor()
        self.__ctrl_kl = CtrlKL()
        self.__read_mb = ReadMB()
        self.__mysql_conn = MySQLConnect()
        # self.__fault = Bug(False)
        self.subtest = SubtestA1A2()

        logging.basicConfig(filename="C:\Stend\project_class\log\TestBDU42.log",
                            filemode="w",
                            level=logging.DEBUG,
                            encoding="utf-8",
                            format='[%(asctime)s: %(name)s: %(levelname)s] %(message)s')
        logging.getLogger('mysql').setLevel('WARNING')
        self.logger = logging.getLogger(__name__)

    def st_test_1(self) -> bool:
        """
            Тест 1. Проверка исходного состояния блока:
        """
        if self.subtest.subtest_inp_a1a2(test_num=1, subtest_num=1.0, err_code_a1=5, err_code_a2=6,
                                         position_a1=False, position_a2=False):
            return True
        return False

    def st_test_20(self) -> bool:
        """
            Тест 2. Проверка включения выключения блока от кнопки «Пуск Стоп».
            2.1. Проверка исходного состояния блока
        """
        self.__ctrl_kl.ctrl_relay('KL2', True)
        if self.subtest.subtest_inp_a1a2(test_num=2, subtest_num=2.0, err_code_a1=13, err_code_a2=14,
                                         position_a1=False, position_a2=False):
            return True
        return False

    def st_test_21(self) -> bool:
        """
            2.2. Включение блока от кнопки «Пуск»
            2.3. Проверка удержания блока во включенном состоянии при подключении Rш пульта управления:
        """

        if self.subtest.subtest_a(test_num=2, subtest_num=2.1):
            if self.subtest.subtest_b(test_num=2, subtest_num=2.2):
                return True
        return False

    def st_test_23(self) -> bool:
        """
            2.4. Выключение блока от кнопки «Стоп»
        """
        self.__ctrl_kl.ctrl_relay('KL12', False)
        sleep(2)
        if self.subtest.subtest_inp_a1a2(test_num=2, subtest_num=2.3, err_code_a1=17, err_code_a2=18,
                                         position_a1=False, position_a2=False):
            self.__ctrl_kl.ctrl_relay('KL25', False)
            self.__ctrl_kl.ctrl_relay('KL1', False)
            return True
        return False

    def st_test_30(self) -> bool:
        """
            тест 3. повторяем тесты 2.2 и 2.3
        """
        if self.subtest.subtest_a(test_num=3, subtest_num=3.0):
            if self.subtest.subtest_b(test_num=3, subtest_num=3.1):
                return True
        return False

    def st_test_32(self) -> bool:
        """
            3. Отключение исполнительного элемента при увеличении сопротивления цепи заземления
        """
        self.__resist.resist_10_to_110_ohm()
        sleep(1)
        if self.subtest.subtest_inp_a1a2(test_num=3, subtest_num=3.2, err_code_a1=19, err_code_a2=20,
                                         position_a1=False, position_a2=False):
            self.__ctrl_kl.ctrl_relay('KL12', False)
            self.__ctrl_kl.ctrl_relay('KL25', False)
            self.__ctrl_kl.ctrl_relay('KL1', False)
            return True
        return False

    def st_test_40(self) -> bool:
        """
            Тест 4. повторяем тесты 2.2 и 2.3
        """
        if self.subtest.subtest_a(test_num=4, subtest_num=4.0):
            if self.subtest.subtest_b(test_num=4, subtest_num=4.1):
                return True
        return False

    def st_test_42(self) -> bool:
        """
            Тест 4. Защита от потери управляемости при замыкании проводов ДУ
        """
        self.__ctrl_kl.ctrl_relay('KL11', True)
        sleep(1)
        if self.subtest.subtest_inp_a1a2(test_num=4, subtest_num=4.2, err_code_a1=9, err_code_a2=10,
                                         position_a1=False, position_a2=False):
            self.__ctrl_kl.ctrl_relay('KL12', False)
            self.__ctrl_kl.ctrl_relay('KL25', False)
            self.__ctrl_kl.ctrl_relay('KL1', False)
            self.__ctrl_kl.ctrl_relay('KL11', False)
            return True
        return False

    def st_test_50(self) -> bool:
        """
            Тест 5. повторяем тесты 2.2 и 2.3
        """
        if self.subtest.subtest_a(test_num=5, subtest_num=5.0):
            if self.subtest.subtest_b(test_num=5, subtest_num=5.1):
                return True
        return False

    def st_test_52(self) -> bool:
        """
            Тест 5. Защита от потери управляемости при обрыве проводов ДУ
        """
        self.__ctrl_kl.ctrl_relay('KL12', False)
        sleep(1)
        if self.subtest.subtest_inp_a1a2(test_num=5, subtest_num=5.2, err_code_a1=11, err_code_a2=12,
                                         position_a1=False, position_a2=False):
            return True
        return False

    def st_test_bdu_4_2(self) -> bool:
        """
            главная функция которая собирает все остальные
        """
        if self.st_test_1():
            if self.st_test_20():
                if self.st_test_21():
                    if self.st_test_23():
                        if self.st_test_30():
                            if self.st_test_32():
                                if self.st_test_40():
                                    if self.st_test_42():
                                        if self.st_test_50():
                                            if self.st_test_52():
                                                return True
        return False


if __name__ == '__main__':
    test_bdu_4_2 = TestBDU42()
    reset_test_bdu_4_2 = ResetRelay()
    mysql_conn_test_bdu_4_2 = MySQLConnect()
    fault = Bug(True)
    try:
        if test_bdu_4_2.st_test_bdu_4_2():
            mysql_conn_test_bdu_4_2.mysql_block_good()
            my_msg('Блок исправен', 'green')
        else:
            mysql_conn_test_bdu_4_2.mysql_block_bad()
            my_msg('Блок неисправен', 'red')
    except OSError:
        my_msg("ошибка системы", 'red')
    except SystemError:
        my_msg("внутренняя ошибка", 'red')
    except ModbusConnectException as mce:
        fault.debug_msg(mce, 'red')
        my_msg(f'{mce}', 'red')
    finally:
        reset_test_bdu_4_2.reset_all()
        sys.exit()
