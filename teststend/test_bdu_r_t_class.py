#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Тип блока  Производитель
БДУ-Р-Т	   Нет производителя
БДУ-Р-Т	   ТЭТЗ-Инвест
БДУ-Р-Т	   Стройэнергомаш

"""

import sys
import logging

from time import sleep

from gen_func_utils import *
from my_msgbox import *
from gen_mb_client import *
from gen_mysql_connect import *
from gen_subtest import SubtestA1A2

__all__ = ["TestBDURT"]


class TestBDURT(object):

    def __init__(self):
        self.__resist = Resistor()
        self.__ctrl_kl = CtrlKL()
        self.__read_mb = ReadMB()
        self.__mysql_conn = MySQLConnect()
        # self.__fault = Bug(None)
        self.subtest = SubtestA1A2()

        logging.basicConfig(filename="C:\Stend\project_class\log\TestBDURT.log",
                            filemode="w",
                            level=logging.DEBUG,
                            encoding="utf-8",
                            format='[%(asctime)s: %(name)s: %(levelname)s] %(message)s')
        logging.getLogger('mysql').setLevel('DEBUG')
        self.logger = logging.getLogger(__name__)

    def st_test_1(self) -> bool:
        if self.subtest.subtest_inp_a1a2(test_num=1, subtest_num=1.0, err_code_a1=288, err_code_a2=288,
                                         position_a1=False, position_a2=False):
            return True
        return False

    def st_test_20(self) -> bool:
        """
        Тест 2. Проверка включения/выключения блока от кнопки «Пуск/Стоп» в режиме «Вперед».
        """
        self.logger.debug("старт теста 2.0")
        self.__ctrl_kl.ctrl_relay('KL2', True)
        self.logger.debug("включен KL2")
        sleep(1)
        if self.subtest.subtest_inp_a1a2(test_num=2, subtest_num=2.0, err_code_a1=290, err_code_a2=291,
                                         position_a1=False, position_a2=False):
            return True
        return False

    def st_test_21(self) -> bool:
        """
        2.2. Включение блока от кнопки «Пуск» в режиме «Вперёд»
        2.3. Проверка удержания блока во включенном состоянии при подключении Rш пульта управления:
        """
        if self.subtest.subtest_a_bdu(test_num=2, subtest_num=2.1, err_code_a1=292, err_code_a2=293,
                                      position_a1=True, position_a2=False):
            if self.subtest.subtest_b_bdu(test_num=2, subtest_num=2.2, err_code_a1=294, err_code_a2=295,
                                          position_a1=True, position_a2=False):
                return True
        return False

    def st_test_23(self) -> bool:
        """
        2.4. Выключение блока в режиме «Вперед» от кнопки «Стоп»
        """
        self.logger.debug("старт теста 2.3")
        self.__ctrl_kl.ctrl_relay('KL12', False)
        self.logger.debug(' включен KL12')
        sleep(1)
        if self.subtest.subtest_inp_a1a2(test_num=2, subtest_num=2.3, err_code_a1=296, err_code_a2=297,
                                         position_a1=False, position_a2=False):
            self.__ctrl_kl.ctrl_relay('KL25', False)
            self.__ctrl_kl.ctrl_relay('KL1', False)
            self.logger.debug(' отключены KL25, KL1')
            return True
        return False

    def st_test_30(self) -> bool:
        """
        Тест 3. Проверка включения/выключения блока от кнопки «Пуск/Стоп» в режиме «Назад»
        3.1. Включение блока от кнопки «Пуск» в режиме «Назад»
        """
        self.logger.debug("старт теста 3.0")
        self.__ctrl_kl.ctrl_relay('KL26', True)
        self.logger.debug(' включен KL26')
        self.__resist.resist_ohm(10)
        self.__ctrl_kl.ctrl_relay('KL12', True)
        self.logger.debug(' включен KL12')
        sleep(1)
        if self.subtest.subtest_inp_a1a2(test_num=3, subtest_num=3.0, err_code_a1=298, err_code_a2=299,
                                         position_a1=False, position_a2=True):
            return True
        return False

    def st_test_31(self) -> bool:
        """
        3.2. Проверка удержания контактов К5.2 режима «Назад» блока во включенном состоянии
        при подключении Rш пульта управления:
        """
        self.logger.debug("старт теста 3.1")
        self.__ctrl_kl.ctrl_relay('KL27', True)
        self.__ctrl_kl.ctrl_relay('KL1', True)
        self.__ctrl_kl.ctrl_relay('KL25', True)
        self.logger.debug(' включены KL27, KL25, KL1')
        sleep(1)
        if self.subtest.subtest_inp_a1a2(test_num=3, subtest_num=3.1, err_code_a1=300, err_code_a2=301,
                                         position_a1=True, position_a2=False):
            return True
        return False

    def st_test_32(self) -> bool:
        """
        3.3. Выключение блока в режиме «Вперед» от кнопки «Стоп»
        """
        self.logger.debug("старт теста 3.2")
        self.__ctrl_kl.ctrl_relay('KL12', False)
        self.logger.debug(' отключен KL12')
        sleep(1)
        if self.subtest.subtest_inp_a1a2(test_num=3, subtest_num=3.2, err_code_a1=302, err_code_a2=303,
                                         position_a1=False, position_a2=False):
            self.__ctrl_kl.ctrl_relay('KL26', False)
            self.__ctrl_kl.ctrl_relay('KL27', False)
            self.__ctrl_kl.ctrl_relay('KL1', False)
            self.__ctrl_kl.ctrl_relay('KL25', False)
            self.logger.debug(' отключены KL26, KL27, KL1, KL25')
            return True
        return False

    def st_test_40(self) -> bool:
        """
        Повторяем тест 2.2. Включение блока от кнопки «Пуск» в режиме «Вперёд»
        Повторяем тест 2.3. Проверка удержания блока во включенном состоянии при подключении Rш пульта управления:
        """
        if self.subtest.subtest_a_bdu(test_num=4, subtest_num=4.0, err_code_a1=292, err_code_a2=293,
                                      position_a1=True, position_a2=False):
            if self.subtest.subtest_b_bdu(test_num=4, subtest_num=4.1, err_code_a1=294, err_code_a2=295,
                                          position_a1=True, position_a2=False):
                return True
        return False

    def st_test_42(self) -> bool:
        """
        # 4. Отключение исполнительного элемента при увеличении сопротивления цепи заземления на величину свыше 50 Ом
        """
        self.logger.debug("старт теста 4.2")
        self.__resist.resist_10_to_50_ohm()
        sleep(1)
        if self.subtest.subtest_inp_a1a2(test_num=4, subtest_num=4.2, err_code_a1=304, err_code_a2=305,
                                         position_a1=False, position_a2=False):
            self.__ctrl_kl.ctrl_relay('KL12', False)
            self.__ctrl_kl.ctrl_relay('KL25', False)
            self.__ctrl_kl.ctrl_relay('KL1', False)
            self.logger.debug(' отключены KL12, KL25, KL1')
            return True
        return False

    def st_test_50(self) -> bool:
        """
        Повторяем тест 2.2. Включение блока от кнопки «Пуск» в режиме «Вперёд»
        Повторяем тест 2.3. Проверка удержания блока во включенном состоянии при подключении Rш пульта управления:
        """
        if self.subtest.subtest_a_bdu(test_num=5, subtest_num=5.0, err_code_a1=292, err_code_a2=293,
                                      position_a1=True, position_a2=False):
            if self.subtest.subtest_b_bdu(test_num=5, subtest_num=5.1, err_code_a1=294, err_code_a2=295,
                                          position_a1=True, position_a2=False):
                return True
        return False

    def st_test_52(self) -> bool:
        """
        # 5. Защита от потери управляемости при замыкании проводов ДУ
        """
        self.logger.debug("старт теста 5.2")
        self.__ctrl_kl.ctrl_relay('KL11', True)
        self.logger.debug(' включен KL11')
        sleep(1)
        if self.subtest.subtest_inp_a1a2(test_num=5, subtest_num=5.2, err_code_a1=306, err_code_a2=307,
                                         position_a1=False, position_a2=False):
            self.__ctrl_kl.ctrl_relay('KL12', False)
            self.__ctrl_kl.ctrl_relay('KL1', False)
            self.__ctrl_kl.ctrl_relay('KL25', False)
            self.__ctrl_kl.ctrl_relay('KL11', False)
            self.logger.debug(' отключены KL12, KL1, KL25, KL11')
            return True
        return False

    def st_test_60(self) -> bool:
        """
        Повторяем тест 2.2. Включение блока от кнопки «Пуск» в режиме «Вперёд»
        Повторяем тест 2.3. Проверка удержания блока во включенном состоянии при подключении Rш пульта управления:
        """
        if self.subtest.subtest_a_bdu(test_num=6, subtest_num=6.0, err_code_a1=292, err_code_a2=293,
                                      position_a1=True, position_a2=False):
            if self.subtest.subtest_b_bdu(test_num=6, subtest_num=6.1, err_code_a1=294, err_code_a2=295,
                                          position_a1=True, position_a2=False):
                return True
        return False

    def st_test_62(self) -> bool:
        """
        # Тест 6. Защита от потери управляемости при обрыве проводов ДУ
        """
        self.logger.debug("старт теста 6.2")
        self.__ctrl_kl.ctrl_relay('KL12', False)
        self.logger.debug(' отключен KL12')
        sleep(1)
        if self.subtest.subtest_inp_a1a2(test_num=6, subtest_num=6.2, err_code_a1=308, err_code_a2=309,
                                         position_a1=False, position_a2=False):
            return True
        return False

    def st_test_70(self) -> bool:
        """
        # Тест 7. Проверка работоспособности функции "Проверка" блока
        """
        self.logger.debug("старт теста 7.0")
        self.__ctrl_kl.ctrl_relay('KL24', True)
        self.logger.debug(' включен KL24')
        sleep(1)
        if self.subtest.subtest_inp_a1a2(test_num=7, subtest_num=7.0, err_code_a1=310, err_code_a2=311,
                                         position_a1=False, position_a2=True):
            return True
        return False

    def st_test_bdu_r_t(self) -> bool:
        """
        Главная функция которая собирает все остальные
        """
        if self.st_test_1():
            if self.st_test_20():
                if self.st_test_21():
                    if self.st_test_23():
                        if self.st_test_30():
                            if self.st_test_31():
                                if self.st_test_32():
                                    if self.st_test_40():
                                        if self.st_test_42():
                                            if self.st_test_50():
                                                if self.st_test_52():
                                                    if self.st_test_60():
                                                        if self.st_test_62():
                                                            if self.st_test_70():
                                                                return True
        return False


if __name__ == '__main__':
    test_bdu_r_t = TestBDURT()
    reset_test_bdu_r_t = ResetRelay()
    mysql_conn_bdu_r_t = MySQLConnect()
    fault = Bug(True)
    try:
        if test_bdu_r_t.st_test_bdu_r_t():
            mysql_conn_bdu_r_t.mysql_block_good()
            my_msg('Блок исправен', 'green')
        else:
            mysql_conn_bdu_r_t.mysql_block_bad()
            my_msg('Блок неисправен', 'red')
    except OSError:
        my_msg("ошибка системы", 'red')
    except SystemError:
        my_msg("внутренняя ошибка", 'red')
    except ModbusConnectException as mce:
        fault.debug_msg(mce, 'red')
        my_msg(f'{mce}', 'red')
    finally:
        reset_test_bdu_r_t.reset_all()
        sys.exit()
