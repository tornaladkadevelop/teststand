#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Алгоритм проверки
Тип блока Производитель
БДУ	Без Производителя
БДУ	Углеприбор

"""

import sys
import logging

from time import sleep

from gen_func_utils import *
from my_msgbox import *
from gen_mb_client import *
from gen_mysql_connect import *
from gen_subtest import SubtestBDU

__all__ = ["TestBDU"]


class TestBDU(object):

    def __init__(self):
        self.__resist = Resistor()
        self.__ctrl_kl = CtrlKL()
        self.__read_mb = ReadMB()
        self.__mysql_conn = MySQLConnect()
        self.sub_test = SubtestBDU()
        self.__fault = Bug(True)

        logging.basicConfig(filename="C:\Stend\project_class\log\TestBDU.log",
                            filemode="w",
                            level=logging.DEBUG,
                            encoding="utf-8",
                            format='[%(asctime)s: %(name)s: %(levelname)s] %(message)s')
        logging.getLogger('mysql').setLevel('DEBUG')
        self.logger = logging.getLogger(__name__)

    def st_test_10(self) -> bool:
        """
        Тест 1. проверка исходного состояния блока
        """
        if self.sub_test.subtest_bdu_inp_a1(test_num=1, subtest_num=1.0, err_code=47):
            return True
        return False

    def st_test_20(self) -> bool:
        """
        Тест-2 Проверка включения/отключения блока от кнопки пуск
        """
        self.logger.debug(f"старт теста: 2, подтест: 0")
        self.__ctrl_kl.ctrl_relay('KL2', True)
        self.logger.debug(f'включение KL2')
        sleep(3)
        if self.sub_test.subtest_bdu_inp_a1(test_num=2, subtest_num=2.0, err_code=21, position=False):
            return True
        return False

    def st_test_21(self) -> bool:
        """
        Тест-2.2 Проверка канала блока от кнопки "Пуск"
        """
        self.logger.debug(f"старт теста: 2, подтест: 1")
        self.__resist.resist_ohm(10)
        sleep(3)
        self.__ctrl_kl.ctrl_relay('KL12', True)
        self.logger.debug(f'включение KL12')
        sleep(3)
        if self.sub_test.subtest_bdu_inp_a1(test_num=2, subtest_num=2.1, err_code=21, position=True):
            return True
        return False

    def st_test_22(self) -> bool:
        """
        Тест 2.3 Выключение канала блока от кнопки «Пуск» при сопротивлении 10 Ом
        """
        self.logger.debug(f"старт теста: 2, подтест: 2")
        sleep(3)
        self.__ctrl_kl.ctrl_relay('KL12', False)
        self.logger.debug(f'отключение KL12')
        sleep(3)
        if self.sub_test.subtest_bdu_inp_a1(test_num=2, subtest_num=2.2, err_code=21, position=False):
            return True
        return False

    def st_test_30(self) -> bool:
        """
        Тест-3. Удержание исполнительного элемента при сопротивлении цепи заземления до 35 Ом
        """
        self.logger.debug(f"старт теста: 3, подтест: 0")
        sleep(3)
        self.__ctrl_kl.ctrl_relay('KL12', True)
        self.logger.debug(f'включение KL12')
        sleep(0.5)
        # Отключаем KL5, KL8 для формирования 35 Ом
        self.__ctrl_kl.ctrl_relay('KL5', False)
        self.__ctrl_kl.ctrl_relay('KL8', False)
        self.logger.debug(f'отключение KL5, KL8')
        sleep(1)
        if self.sub_test.subtest_bdu_inp_a1(test_num=3, subtest_num=3.0, err_code=28, position=False):
            return True
        return False

    def st_test_40(self) -> bool:
        """
        Тест 4. Отключение исполнительного элемента при сопротивлении цепи заземления свыше 50 Ом
        """
        self.logger.debug(f"старт теста: 4, подтест: 0")
        self.__ctrl_kl.ctrl_relay('KL7', False)
        self.__ctrl_kl.ctrl_relay('KL9', False)
        self.__ctrl_kl.ctrl_relay('KL4', True)
        self.__ctrl_kl.ctrl_relay('KL6', True)
        self.__ctrl_kl.ctrl_relay('KL10', True)
        self.logger.debug(f'включение KL4, KL6, KL10, отключение KL7, KL9')
        if self.sub_test.subtest_bdu_inp_a1(test_num=4, subtest_num=4.0, err_code=29, position=False):
            sleep(0.5)
            self.__ctrl_kl.ctrl_relay('KL12', False)
            self.logger.debug(f'отключение KL12')
            return True
        return False

    def st_test_50(self) -> bool:
        """
        Тест 5. Защита от потери управляемости при замыкании проводов ДУ
        """
        self.logger.debug(f"старт теста: 5, подтест: 0")
        self.__resist.resist_ohm(10)
        sleep(1)
        self.__ctrl_kl.ctrl_relay('KL12', True)
        self.logger.debug(f'включение KL12')
        sleep(0.5)
        self.__ctrl_kl.ctrl_relay('KL11', True)
        self.logger.debug(f'включение KL11')
        sleep(1)
        if self.sub_test.subtest_bdu_inp_a1(test_num=5, subtest_num=5.0, err_code=3, position=False):
            self.__ctrl_kl.ctrl_relay('KL12', False)
            self.__ctrl_kl.ctrl_relay('KL11', False)
            self.__ctrl_kl.ctrl_relay('KL1', False)
            self.logger.debug(f'отключение KL12, KL11, KL1')
            return True
        return False

    def st_test_60(self) -> bool:
        """
        Тест 6. Защита от потери управляемости при обрыве проводов ДУ
        """
        self.logger.debug(f"старт теста: 6, подтест: 0")
        self.__resist.resist_ohm(10)
        sleep(1)
        self.__ctrl_kl.ctrl_relay('KL12', True)
        self.logger.debug(f'включение KL12')
        sleep(1)
        self.__ctrl_kl.ctrl_relay('KL12', False)
        self.logger.debug(f'отключение KL12')
        sleep(1)
        if self.sub_test.subtest_bdu_inp_a1(test_num=6, subtest_num=6.0, err_code=4, position=False):
            return True
        return False

    def st_test_bdu(self) -> bool:
        """
            Главная функция которая собирает все остальные
        """
        if self.st_test_10():
            if self.st_test_20():
                if self.st_test_21():
                    if self.st_test_22():
                        if self.st_test_30():
                            if self.st_test_40():
                                if self.st_test_50():
                                    if self.st_test_60():
                                        return True
        return False


if __name__ == '__main__':
    test_bdu = TestBDU()
    reset_test_bdu = ResetRelay()
    mysql_conn_test_bdu = MySQLConnect()
    fault = Bug(True)
    try:
        if test_bdu.st_test_bdu():
            mysql_conn_test_bdu.mysql_block_good()
            my_msg('Блок исправен', 'green')
        else:
            mysql_conn_test_bdu.mysql_block_bad()
            my_msg('Блок неисправен', 'red')
    except OSError:
        my_msg("ошибка системы", 'red')
    except SystemError:
        my_msg("внутренняя ошибка", 'red')
    except ModbusConnectException as mce:
        fault.debug_msg(mce, 'red')
        my_msg(f'{mce}', 'red')
    finally:
        reset_test_bdu.reset_all()
        sys.exit()
