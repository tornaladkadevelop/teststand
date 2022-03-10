#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Тип блока     Производитель
БДУ             Без Производителя
БДУ             Углеприбор
БДУ-1           Без Производителя
БДУ-1           Углеприбор
БДУ-4           Без Производителя
БДУ-4           Углеприбор
БДУ-Т           Без Производителя
БДУ-Т           Углеприбор
БДУ-Т           ТЭТЗ-Инвест
БДУ-Т           Строй-ЭнергоМаш
БДУ-П Х5-01     Пульсар
БДУ-П УХЛ 01    Пульсар
БДУ-П УХЛ5-03   Пульсар
"""

from sys import exit
from time import sleep
from gen_func_utils import *
from my_msgbox import *
from gen_mb_client import *
from gen_mysql_connect import *

__all__ = ["TestBDU014TP"]


class TestBDU014TP(object):
    __resist = Resistor()
    __ctrl_kl = CtrlKL()
    __read_mb = ReadMB()
    __mysql_conn = MySQLConnect()
    __fault = Bug(True)

    def __init__(self):
        pass

    def st_test_1_bdu_014tp(self) -> bool:
        """
        Тест 1. Проверка исходного состояния блока:
        :return:
        """
        self.__fault.debug_msg(f'тест 1', 4)
        self.__mysql_conn.mysql_ins_result("идет тест 1", "1")
        in_a0, in_a1 = self.__inputs_a()
        if in_a1 is False:
            pass
        else:
            self.__mysql_conn.mysql_ins_result("неисправен", "1")
            self.__mysql_conn.mysql_error(476)
            return False
        self.__mysql_conn.mysql_ins_result("исправен", "1")
        return True

    def st_test_20_bdu_014tp(self) -> bool:
        """
        Тест 2. Проверка включения / выключения блока от кнопки «Пуск / Стоп».
        2.1. Проверка исходного состояния блока
        """
        self.__fault.debug_msg(f'тест 2.0', 4)
        self.__mysql_conn.mysql_ins_result("идет тест 2.1", "2")
        self.__ctrl_kl.ctrl_relay('KL2', True)
        in_a0, in_a1 = self.__inputs_a()
        sleep(1)
        if in_a1 is False:
            return True
        else:
            self.__mysql_conn.mysql_ins_result("неисправен", "2")
            return False

    def st_test_21_bdu_014tp(self) -> bool:
        """
        2.2. Включение канала блока от кнопки «Пуск» при сопротивлении 10 Ом
        """
        self.__fault.debug_msg(f'тест 2.1', 4)
        if self.subtest_22(2.2, 2):
            return True
        return False

    def st_test_22_bdu_014tp(self) -> bool:
        """
        2.3. Выключение канала блока от кнопки «Пуск» при сопротивлении 10 Ом
        """
        self.__fault.debug_msg(f'тест 2.2', 4)
        self.__mysql_conn.mysql_ins_result("идет тест 2.3", "2")
        self.__ctrl_kl.ctrl_relay('KL12', False)
        sleep(1)
        in_a0, in_a1 = self.__inputs_a()
        if in_a1 is False:
            pass
        else:
            self.__mysql_conn.mysql_ins_result("неисправен", "2")
            self.__mysql_conn.mysql_error(27)
            return False
        self.__mysql_conn.mysql_ins_result("исправен", "2")
        return True

    def st_test_30_bdu_014tp(self) -> bool:
        """
        повтор теста 2.2
        """
        self.__fault.debug_msg(f'тест 3.0', 4)
        if self.subtest_22(3.1, 3):
            return True
        return False

    def st_test_31_bdu_014tp(self) -> bool:
        """
        3. Удержание исполнительного элемента при сопротивлении цепи заземления до 35 Ом
        """
        self.__fault.debug_msg(f'тест 3.1', 4)
        self.__resist.resist_10_to_35_ohm()
        sleep(1)
        in_a0, in_a1 = self.__inputs_a()
        if in_a1 is True:
            pass
        else:
            self.__mysql_conn.mysql_ins_result("неисправен", "3")
            self.__mysql_conn.mysql_error(28)
            return False
        self.__mysql_conn.mysql_ins_result("исправен", "3")
        return True

    def st_test_40_bdu_014tp(self) -> bool:
        """
        4. Отключение исполнительного элемента при сопротивлении цепи заземления свыше 50 Ом
        """
        self.__fault.debug_msg(f'тест 4.0', 4)
        self.__mysql_conn.mysql_ins_result("идет тест 4", "4")
        self.__resist.resist_35_to_110_ohm()
        sleep(1)
        in_a0, in_a1 = self.__inputs_a()
        if in_a1 is False:
            pass
        else:
            self.__mysql_conn.mysql_ins_result("неисправен", "4")
            self.__mysql_conn.mysql_error(29)
            return False
        self.__ctrl_kl.ctrl_relay('KL12', False)
        self.__ctrl_kl.ctrl_relay('KL1', False)
        self.__mysql_conn.mysql_ins_result("исправен", "4")
        return True

    def st_test_50_bdu_014tp(self) -> bool:
        """
        повтор теста 2.2
        """
        self.__fault.debug_msg(f'тест 5.0', 4)
        if self.subtest_22(5.1, 5):
            return True
        return False

    def st_test_51_bdu_014tp(self) -> bool:
        """
        5. Защита от потери управляемости при замыкании проводов ДУ
        """
        self.__fault.debug_msg(f'тест 5.1', 4)
        self.__ctrl_kl.ctrl_relay('KL11', True)
        sleep(2)
        in_a0, in_a1 = self.__inputs_a()
        if in_a1 is False:
            pass
        else:
            self.__mysql_conn.mysql_ins_result("неисправен", "5")
            self.__mysql_conn.mysql_error(3)
            return False
        self.__ctrl_kl.ctrl_relay('KL12', False)
        self.__ctrl_kl.ctrl_relay('KL1', False)
        self.__ctrl_kl.ctrl_relay('KL11', False)
        self.__mysql_conn.mysql_ins_result("исправен", "5")
        return True

    def st_test_60_bdu_014tp(self) -> bool:
        """
        повтор теста 2.2
        """
        self.__fault.debug_msg(f'тест 6.0', 4)
        if self.subtest_22(6.1, 6):
            return True
        return False

    def st_test_61_bdu_014tp(self) -> bool:
        """
        Тест 6. Защита от потери управляемости при обрыве проводов ДУ
        """
        self.__fault.debug_msg(f'тест 6.1', 4)
        self.__ctrl_kl.ctrl_relay('KL12', False)
        sleep(1)
        in_a0, in_a1 = self.__inputs_a()
        if in_a1 is False:
            pass
        else:
            self.__mysql_conn.mysql_ins_result("неисправен", "6")
            self.__mysql_conn.mysql_error(4)
            return False
        self.__mysql_conn.mysql_ins_result("исправен", "6")
        return True

    def subtest_22(self, subtest_2_num: float, test_2_num: int) -> bool:
        self.__mysql_conn.mysql_ins_result(f'идёт тест {subtest_2_num}', f'{test_2_num}')
        self.__resist.resist_ohm(255)
        # sleep(1)
        self.__resist.resist_ohm(10)
        # sleep(2)
        self.__ctrl_kl.ctrl_relay('KL1', True)
        sleep(1)
        self.__ctrl_kl.ctrl_relay('KL12', True)
        sleep(1)
        in_a0, in_a1 = self.__inputs_a()
        if in_a1 is True:
            pass
        else:
            self.__mysql_conn.mysql_ins_result("неисправен", f'{test_2_num}')
            self.__fault.debug_msg(f'тест {subtest_2_num} положение выходов не соответствует', 1)
            self.__mysql_conn.mysql_error(26)
            return False
        self.__fault.debug_msg(f'тест {subtest_2_num} положение выходов соответствует', 3)
        return True

    def __inputs_a(self):
        in_a0 = self.__read_mb.read_discrete(0)
        in_a1 = self.__read_mb.read_discrete(1)
        self.__fault.debug_msg(f'{in_a0 = }  {in_a1 = }', 4)
        if in_a1 is None or in_a0 is None:
            self.__fault.debug_msg(f'нет связи с контроллером', 1)
        return in_a0, in_a1

    def st_test_bdu_014tp(self) -> bool:
        """
            Главная функция которая собирает все остальные
        """
        if self.st_test_1_bdu_014tp():
            if self.st_test_20_bdu_014tp():
                if self.st_test_21_bdu_014tp():
                    if self.st_test_22_bdu_014tp():
                        if self.st_test_30_bdu_014tp():
                            if self.st_test_31_bdu_014tp():
                                if self.st_test_40_bdu_014tp():
                                    if self.st_test_50_bdu_014tp():
                                        if self.st_test_51_bdu_014tp():
                                            if self.st_test_60_bdu_014tp():
                                                if self.st_test_61_bdu_014tp():
                                                    return True
        return False


if __name__ == '__main__':
    test_bdu_014tp = TestBDU014TP()
    reset_test_bdu_014tp = ResetRelay()
    mysql_conn_test_bdu_014tp = MySQLConnect()
    fault = Bug(True)
    try:
        if test_bdu_014tp.st_test_bdu_014tp():
            mysql_conn_test_bdu_014tp.mysql_block_good()
            my_msg('Блок исправен', '#1E8C1E')
        else:
            mysql_conn_test_bdu_014tp.mysql_block_bad()
            my_msg('Блок неисправен', '#A61E1E')
    except OSError:
        my_msg("ошибка системы", '#A61E1E')
    except SystemError:
        my_msg("внутренняя ошибка", '#A61E1E')
    except ModbusConnectException as mce:
        fault.debug_msg(mce, 1)
        my_msg(str(mce), '#A61E1E')
    finally:
        reset_test_bdu_014tp.reset_all()
        exit()
