#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Алгоритм проверки
Тип блока Производитель
БДУ-Д	Без Производителя
БДУ-Д	Углеприбор

"""

import sys
import logging

from time import sleep

from gen_func_utils import *
from my_msgbox import *
from gen_mb_client import *
from gen_mysql_connect import *
from gen_subtest import SubtestBDU

__all__ = ["TestBDUD"]


class TestBDUD(object):

    def __init__(self):
        self.__resist = Resistor()
        self.__read_mb = ReadMB()
        self.__ctrl_kl = CtrlKL()
        self.__mysql_conn = MySQLConnect()
        self.sub_test = SubtestBDU()
        self.__fault = Bug(True)

        logging.basicConfig(filename="C:\Stend\project_class\log\TestBDUD.log",
                            filemode="w",
                            level=logging.DEBUG,
                            encoding="utf-8",
                            format='[%(asctime)s: %(name)s: %(levelname)s] %(message)s')
        logging.getLogger('mysql').setLevel('DEBUG')
        self.logger = logging.getLogger(__name__)

    def st_test_10(self) -> bool:
        """
        Тест 1. Проверка исходного состояния блока:
        """
        if self.sub_test.subtest_bdu_inp_a1(test_num=1, subtest_num=1.0, err_code=47):
            return True
        return False

    def st_test_20(self) -> bool:
        """
        Тест 2. Проверка включения выключения блока от кнопки «Пуск Стоп».
        2.1. Проверка исходного состояния блока
        """
        self.logger.debug(f"старт теста: 2, подтест: 0")
        self.__ctrl_kl.ctrl_relay('KL2', True)
        self.logger.debug(f'включение KL2')
        if self.sub_test.subtest_bdu_inp_a1(test_num=2, subtest_num=2.0, err_code=13, position=False):
            return True
        return False

    def st_test_21(self) -> bool:
        """
        2.2. Включение блока от кнопки «Пуск»
        2.3. Проверка удержания блока во включенном состоянии при подключении Rш пульта управления:
        """
        if self.sub_test.subtest_a_bdud(test_num=2, subtest_num=2.1):
            if self.sub_test.subtest_b_bdu43_d(test_num=2, subtest_num=2.2):
                return True
        return False

    def st_test_23(self) -> bool:
        """
        2.4. Выключение блока от кнопки «Стоп»
        """
        self.logger.debug(f"старт теста: 2, подтест: 3")
        self.__ctrl_kl.ctrl_relay('KL12', False)
        self.logger.debug(f'отключение KL12')
        sleep(3)
        if self.sub_test.subtest_bdu_inp_a1(test_num=2, subtest_num=2.3, err_code=23, position=False):
            self.__ctrl_kl.ctrl_relay('KL25', False)
            self.__ctrl_kl.ctrl_relay('KL1', False)
            self.logger.debug(f'отключение KL25, KL1')
            return True
        return False

    def st_test_30(self) -> bool:
        """
        Повторяем тест 2.2. Включение блока от кнопки «Пуск»
        Повторяем тест 2.3. Проверка удержания блока во включенном состоянии при подключении Rш пульта управления:
        """
        if self.sub_test.subtest_a_bdud(test_num=3, subtest_num=3.0):
            if self.sub_test.subtest_b_bdu43_d(test_num=3, subtest_num=3.1):
                return True
        return False

    def st_test_32(self) -> bool:
        """
        3. Отключение исполнительного элемента при увеличении сопротивления цепи заземления
        """
        self.logger.debug(f"старт теста: 3, подтест: 2")
        self.__resist.resist_0_to_63_ohm()
        sleep(3)
        if self.sub_test.subtest_bdu_inp_a1(test_num=3, subtest_num=3.2, err_code=24, position=False):
            self.__ctrl_kl.ctrl_relay('KL12', False)
            self.__ctrl_kl.ctrl_relay('KL25', False)
            self.__ctrl_kl.ctrl_relay('KL1', False)
            self.logger.debug(f'отключение KL12, KL25, KL1')
            return True
        return False

    def st_test_40(self) -> bool:
        """
        Повторяем тест 2.2. Включение блока от кнопки «Пуск»
        Повторяем тест 2.3. Проверка удержания блока во включенном состоянии при подключении Rш пульта управления:
        """
        if self.sub_test.subtest_a_bdud(test_num=4, subtest_num=4.0):
            if self.sub_test.subtest_b_bdu43_d(test_num=4, subtest_num=4.1):
                return True
        return False

    def st_test_42(self) -> bool:
        """
        Тест 4. Защита от потери управляемости при замыкании проводов ДУ
        """
        self.logger.debug(f"старт теста: 4, подтест: 2")
        self.__ctrl_kl.ctrl_relay('KL11', True)
        self.logger.debug(f'включение KL11')
        sleep(3)
        if self.sub_test.subtest_bdu_inp_a1(test_num=4, subtest_num=4.2, err_code=3, position=False):
            self.__ctrl_kl.ctrl_relay('KL12', False)
            self.__ctrl_kl.ctrl_relay('KL25', False)
            self.__ctrl_kl.ctrl_relay('KL1', False)
            self.__ctrl_kl.ctrl_relay('KL11', False)
            self.logger.debug(f'отключение KL12, KL25, KL1, KL11')
            return True
        return False

    def st_test_50(self) -> bool:
        """
        Повторяем тест 2.2. Включение блока от кнопки «Пуск»
        Повторяем тест 2.3. Проверка удержания блока во включенном состоянии при подключении Rш пульта управления:
        """
        if self.sub_test.subtest_a_bdud(test_num=5, subtest_num=5.0):
            if self.sub_test.subtest_b_bdu43_d(test_num=5, subtest_num=5.1):
                return True
        return False

    def st_test_52(self) -> bool:
        """
        Тест 5. Защита от потери управляемости при обрыве проводов ДУ
        """
        self.logger.debug(f"старт теста: 5, подтест: 2")
        self.__ctrl_kl.ctrl_relay('KL12', False)
        self.logger.debug(f'отключение KL12')
        sleep(3)
        if self.sub_test.subtest_bdu_inp_a1(test_num=5, subtest_num=5.2, err_code=4, position=False):
            return True
        return False

    def st_test_bdu_d(self) -> bool:
        """
            Главная функция которая собирает все остальные
        """
        if self.st_test_10():
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
    test_bdu_d = TestBDUD()
    reset_test_bdu_d = ResetRelay()
    mysql_conn_test_bdu_d = MySQLConnect()
    fault = Bug(True)
    try:
        if test_bdu_d.st_test_bdu_d():
            mysql_conn_test_bdu_d.mysql_block_good()
            my_msg('Блок исправен', 'green')
        else:
            mysql_conn_test_bdu_d.mysql_block_bad()
            my_msg('Блок неисправен', 'red')
    except OSError:
        my_msg("ошибка системы", 'red')
    except SystemError:
        my_msg("внутренняя ошибка", 'red')
    except ModbusConnectException as mce:
        fault.debug_msg(mce, 'red')
        my_msg(f'{mce}', 'red')
    finally:
        reset_test_bdu_d.reset_all()
        sys.exit()
