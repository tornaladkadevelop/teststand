#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Алгоритм проверки
Тип блока Производитель
БДУ-4-3	Без Производителя
БДУ-4-3	Углеприбор

"""

import sys
import logging

from time import sleep

from gen_func_utils import *
from my_msgbox import *
from gen_mb_client import *
from gen_mysql_connect import *
from gen_subtest import SubtestBDU

__all__ = ["TestBDU43"]


class TestBDU43(object):

    def __init__(self):
        self.__resist = Resistor()
        self.read_di = ReadDI()
        self.__ctrl_kl = CtrlKL()
        self.__mysql_conn = MySQLConnect()
        self.sub_test = SubtestBDU()
        self.__fault = Bug(True)

        logging.basicConfig(filename="C:\Stend\project_class\log\TestBDU43.log",
                            filemode="w",
                            level=logging.DEBUG,
                            encoding="utf-8",
                            format='[%(asctime)s: %(name)s: %(levelname)s] %(message)s')
        logging.getLogger('mysql').setLevel('WARNING')
        self.logger = logging.getLogger(__name__)

    def st_test_1_bdu_4_3(self) -> bool:
        """
            Тест 1. Проверка исходного состояния блока:
        """
        if self.sub_test.subtest_bdu_inp_a1(test_num=1, subtest_num=1.0, err_code=47):
            self.__mysql_conn.mysql_ins_result("неисправен", '1')
            return True
        else:
            return False

    def st_test_20_bdu_4_3(self) -> bool:
        """
            Тест 2. Проверка включения выключения блока от кнопки «Пуск Стоп».
            2.1. Проверка исходного состояния блока
        """
        self.__ctrl_kl.ctrl_relay('KL2', True)
        if self.sub_test.subtest_bdu_inp_a1(test_num=2, subtest_num=2.0, err_code=13):
            return True
        else:
            return False

    def st_test_21_bdu_4_3(self) -> bool:
        """
            2.2. Включение блока от кнопки «Пуск»
            2.3. Проверка удержания блока во включенном состоянии при подключении Rш пульта управления:
        """
        if self.__subtest_22(2.2, 2):
            if self.__subtest_23(2.3, 2):
                return True
        return False

    def st_test_22_bdu_4_3(self) -> bool:
        """
            2.4. Выключение блока от кнопки «Стоп»
        """
        self.__mysql_conn.mysql_ins_result("идет тест 2.4", '2')
        self.__ctrl_kl.ctrl_relay('KL12', False)
        if self.sub_test.subtest_bdu_inp_a1(test_num=2, subtest_num=2.4, err_code=23):
            pass
        else:
            return False
        self.__mysql_conn.mysql_ins_result("неисправен", '2')
        self.__ctrl_kl.ctrl_relay('KL25', False)
        self.__ctrl_kl.ctrl_relay('KL1', False)
        return True

    def st_test_30_bdu_4_3(self) -> bool:
        """
            3. повторяем тесты 2.2 и 2.3
        """
        if self.__subtest_22(3.1, 3):
            if self.__subtest_23(3.2, 3):
                return True
        return False

    def st_test_31_bdu_4_3(self) -> bool:
        """
            3. Отключение исполнительного элемента при увеличении сопротивления цепи заземления
        """
        self.__resist.resist_0_to_63_ohm()
        if self.sub_test.subtest_bdu_inp_a1(test_num=3, subtest_num=3.3, err_code=24):
            pass
        else:
            return False
        self.__mysql_conn.mysql_ins_result("неисправен", '3')
        self.__ctrl_kl.ctrl_relay('KL12', False)
        self.__ctrl_kl.ctrl_relay('KL25', False)
        self.__ctrl_kl.ctrl_relay('KL1', False)
        return True

    def st_test_40_bdu_4_3(self) -> bool:
        """
            4. повторяем тесты 2.2 и 2.3
        """
        if self.__subtest_22(4.1, 4):
            if self.__subtest_23(4.2, 4):
                return True
        return False

    def st_test_41_bdu_4_3(self) -> bool:
        """
            Тест 4. Защита от потери управляемости при замыкании проводов ДУ
        """
        self.__ctrl_kl.ctrl_relay('KL11', True)
        if self.sub_test.subtest_bdu_inp_a1(test_num=4, subtest_num=4.3, err_code=3):
            pass
        else:
            return False
        self.__mysql_conn.mysql_ins_result("неисправен", '4')
        self.__ctrl_kl.ctrl_relay('KL12', False)
        self.__ctrl_kl.ctrl_relay('KL25', False)
        self.__ctrl_kl.ctrl_relay('KL1', False)
        self.__ctrl_kl.ctrl_relay('KL11', False)
        return True

    def st_test_50_bdu_4_3(self) -> bool:
        """
            5. повторяем тесты 2.2 и 2.3
        """
        if self.__subtest_22(5.1, 5):
            if self.__subtest_23(5.2, 5):
                return True
        return False

    def st_test_51_bdu_4_3(self) -> bool:
        """
            Тест 5. Защита от потери управляемости при обрыве проводов ДУ
        """
        self.__ctrl_kl.ctrl_relay('KL12', False)
        if self.sub_test.subtest_bdu_inp_a1(test_num=5, subtest_num=5.3, err_code=4):
            self.__mysql_conn.mysql_ins_result("неисправен", '5')
            return True
        else:
            return False

    def __subtest_22(self, subtest_2_num: float, test_2_num: int) -> bool:
        """
            2.2. Включение блока от кнопки «Пуск»
        """
        self.__mysql_conn.mysql_ins_result(f'идёт тест {subtest_2_num}', f'{test_2_num}')
        self.__resist.resist_ohm(0)
        self.__ctrl_kl.ctrl_relay('KL12', True)
        sleep(1)
        if self.sub_test.subtest_bdu_inp_a1(test_num=test_2_num, subtest_num=subtest_2_num, err_code=21, position=True):
            return True
        else:
            return False

    def __subtest_23(self, subtest_3_num: float, test_3_num: int) -> bool:
        """
            2.3. Проверка удержания блока во включенном состоянии при подключении Rш пульта управления:
        """
        self.__mysql_conn.mysql_ins_result(f'идёт тест {subtest_3_num}', f'{test_3_num}')
        self.__ctrl_kl.ctrl_relay('KL1', True)
        self.__ctrl_kl.ctrl_relay('KL25', True)
        sleep(1)
        if self.sub_test.subtest_bdu_inp_a1(test_num=test_3_num, subtest_num=subtest_3_num, err_code=22, position=True):
            return True
        else:
            return False

    def st_test_bdu_4_3(self) -> bool:
        """
            Главная функция которая собирает все остальные
        """
        if self.st_test_1_bdu_4_3():
            if self.st_test_20_bdu_4_3():
                if self.st_test_21_bdu_4_3():
                    if self.st_test_22_bdu_4_3():
                        if self.st_test_30_bdu_4_3():
                            if self.st_test_31_bdu_4_3():
                                if self.st_test_40_bdu_4_3():
                                    if self.st_test_41_bdu_4_3():
                                        if self.st_test_50_bdu_4_3():
                                            if self.st_test_51_bdu_4_3():
                                                return True
        return False


if __name__ == '__main__':
    test_bdu_4_3 = TestBDU43()
    reset_test_bdu_4_3 = ResetRelay()
    mysql_conn_test_bdu_4_3 = MySQLConnect()
    fault = Bug(True)
    try:
        if test_bdu_4_3.st_test_bdu_4_3():
            mysql_conn_test_bdu_4_3.mysql_block_good()
            my_msg('Блок исправен', 'green')
        else:
            mysql_conn_test_bdu_4_3.mysql_block_bad()
            my_msg('Блок неисправен', 'red')
    except OSError:
        my_msg("ошибка системы", 'red')
    except SystemError:
        my_msg("внутренняя ошибка", 'red')
    except ModbusConnectException as mce:
        fault.debug_msg(mce, 'red')
        my_msg(f'{mce}', 'red')
    finally:
        reset_test_bdu_4_3.reset_all()
        sys.exit()
