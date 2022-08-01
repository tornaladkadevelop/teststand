#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Алгоритм проверки
Тип блока Производитель
БДУ-Д4-2	Нет производителя
БДУ-Д4-2	ДонЭнергоЗавод
БДУ-Д.01	Без Производителя

"""

import sys
import logging

from time import sleep

from general_func.exception import *
from general_func.subtest import *
from general_func.utils import *
from general_func.database import *
from general_func.modbus import *
from general_func.resistance import Resistor
from general_func.reset import ResetRelay
from gui.msgbox_1 import *

__all__ = ["TestBDUD42"]


class TestBDUD42:

    def __init__(self):
        self.resist = Resistor()
        self.ctrl_kl = CtrlKL()
        self.read_mb = ReadMB()
        self.mysql_conn = MySQLConnect()
        # self.fault = Bug(True)
        self.subtest = Subtest2in()

        logging.basicConfig(filename="C:\Stend\project_class\log\TestBDUD42.log",
                            filemode="w",
                            level=logging.DEBUG,
                            encoding="utf-8",
                            format='[%(asctime)s: %(name)s: %(levelname)s] %(message)s')
        logging.getLogger('mysql').setLevel('DEBUG')
        self.logger = logging.getLogger(__name__)

    def st_test_1(self) -> bool:
        """
        Тест 1. Проверка исходного состояния блока:
        """
        if self.subtest.subtest_2di(test_num=1, subtest_num=1.0, err_code_a1=5, err_code_a2=6, position_a1=False,
                                    position_a2=False):
            return True
        return False

    def st_test_20(self) -> bool:
        """
        Тест 2. Проверка включения выключения блока от кнопки «Пуск Стоп».
        2.1. Проверка исходного состояния блока
        """
        self.logger.debug("старт теста 2.0")
        self.ctrl_kl.ctrl_relay('KL2', True)
        self.logger.debug("включен KL2")
        sleep(1)
        if self.subtest.subtest_2di(test_num=2, subtest_num=2.0, err_code_a1=13, err_code_a2=14, position_a1=False,
                                    position_a2=False):
            return True
        return False

    def st_test_21(self) -> bool:
        """
        2.2. Включение блока от кнопки «Пуск»
        2.3. Проверка удержания блока во включенном состоянии при подключении Rш пульта управления:
        """
        if self.subtest.subtest_a_bdu(test_num=2, subtest_num=2.1, err_code_a1=15, err_code_a2=16,
                                      position_a1=True, position_a2=True):
            if self.subtest.subtest_b_bdu(test_num=2, subtest_num=2.2, err_code_a1=7, err_code_a2=8,
                                          position_a1=True, position_a2=True):
                return True
        return False

    def st_test_23(self) -> bool:
        """
        2.4. Выключение блока от кнопки «Стоп»
        """
        self.logger.debug("старт теста 2.3")
        self.ctrl_kl.ctrl_relay('KL12', False)
        self.logger.debug("отключен KL12")
        sleep(2)
        if self.subtest.subtest_2di(test_num=2, subtest_num=2.3, err_code_a1=17, err_code_a2=18, position_a1=False,
                                    position_a2=False):
            self.ctrl_kl.ctrl_relay('KL1', False)
            self.ctrl_kl.ctrl_relay('KL25', False)
            self.logger.debug("отключены KL25, KL1")
            return True
        return False

    def st_test_30(self) -> bool:
        """
        Повторяем тест 2.2. Включение блока от кнопки «Пуск»
        Повторяем тест 2.3. Проверка удержания блока во включенном состоянии при подключении Rш пульта управления:
        """
        if self.subtest.subtest_a_bdu(test_num=3, subtest_num=3.0, err_code_a1=15, err_code_a2=16,
                                      position_a1=True, position_a2=True):
            if self.subtest.subtest_b_bdu(test_num=3, subtest_num=3.1, err_code_a1=7, err_code_a2=8,
                                          position_a1=True, position_a2=True):
                return True
        return False

    def st_test_32(self) -> bool:
        """
        3. Отключение исполнительного элемента при увеличении сопротивления цепи заземления
        """
        self.logger.debug("старт теста 3.2")
        self.resist.resist_10_to_110_ohm()
        sleep(3)
        if self.subtest.subtest_2di(test_num=3, subtest_num=3.2, err_code_a1=19, err_code_a2=20, position_a1=False,
                                    position_a2=False):
            self.ctrl_kl.ctrl_relay('KL12', False)
            self.ctrl_kl.ctrl_relay('KL25', False)
            self.ctrl_kl.ctrl_relay('KL1', False)
            self.logger.debug("отключены KL12, KL25, KL1")
            return True
        return False

    def st_test_40(self) -> bool:
        """
        Повторяем тест 2.2. Включение блока от кнопки «Пуск»
        Повторяем тест 2.3. Проверка удержания блока во включенном состоянии при подключении Rш пульта управления:
        """
        if self.subtest.subtest_a_bdu(test_num=4, subtest_num=4.0, err_code_a1=15, err_code_a2=16,
                                      position_a1=True, position_a2=True):
            if self.subtest.subtest_b_bdu(test_num=4, subtest_num=4.1, err_code_a1=7, err_code_a2=8,
                                          position_a1=True, position_a2=True):
                return True
        return False

    def st_test_42(self) -> bool:
        """
        Тест 4. Защита от потери управляемости при замыкании проводов ДУ
        """
        self.logger.debug("старт теста 4.2")
        self.ctrl_kl.ctrl_relay('KL11', True)
        self.logger.debug("включен KL11")
        sleep(1)
        if self.subtest.subtest_2di(test_num=4, subtest_num=4.2, err_code_a1=9, err_code_a2=10, position_a1=False,
                                    position_a2=False):
            self.ctrl_kl.ctrl_relay('KL12', False)
            self.ctrl_kl.ctrl_relay('KL25', False)
            self.ctrl_kl.ctrl_relay('KL1', False)
            self.ctrl_kl.ctrl_relay('KL11', False)
            self.logger.debug("отключены KL12, KL25, KL1, KL11")
            return True
        return False

    def st_test_50(self) -> bool:
        """
        Повторяем тест 2.2. Включение блока от кнопки «Пуск»
        Повторяем тест 2.3. Проверка удержания блока во включенном состоянии при подключении Rш пульта управления:
        """
        if self.subtest.subtest_a_bdu(test_num=5, subtest_num=5.0, err_code_a1=15, err_code_a2=16,
                                      position_a1=True, position_a2=True):
            if self.subtest.subtest_b_bdu(test_num=5, subtest_num=5.1, err_code_a1=7, err_code_a2=8,
                                          position_a1=True, position_a2=True):
                return True
        return False

    def st_test_52(self) -> bool:
        """
        Тест 5. Защита от потери управляемости при обрыве проводов ДУ
        """
        self.logger.debug("старт теста 5.2")
        self.ctrl_kl.ctrl_relay('KL12', False)
        self.logger.debug("отключен KL12")
        sleep(1)
        if self.subtest.subtest_2di(test_num=5, subtest_num=5.2, err_code_a1=11, err_code_a2=12, position_a1=False,
                                    position_a2=False):
            return True
        return False

    def st_test_bdu_d4_2(self) -> bool:
        """
            Главная функция которая собирает все остальные.
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
    test_bdu_d4_2 = TestBDUD42()
    reset_test_bdu_d4_2 = ResetRelay()
    mysql_conn_test_bdu_d4_2 = MySQLConnect()
    fault = Bug(None)
    try:
        if test_bdu_d4_2.st_test_bdu_d4_2():
            mysql_conn_test_bdu_d4_2.mysql_block_good()
            my_msg('Блок исправен', 'green')
        else:
            mysql_conn_test_bdu_d4_2.mysql_block_bad()
            my_msg('Блок неисправен', 'red')
    except OSError:
        my_msg("ошибка системы", 'red')
    except SystemError:
        my_msg("внутренняя ошибка", 'red')
    except ModbusConnectException as mce:
        fault.debug_msg(mce, 'red')
        my_msg(f'{mce}', 'red')
    finally:
        reset_test_bdu_d4_2.reset_all()
        sys.exit()
