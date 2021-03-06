#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Тип блока Производитель
БУ АПШ.М    Без Производителя
БУ АПШ.М    Горэкс-Светотехника 
"""

import sys

from time import sleep

from gen_func_utils import *
from my_msgbox import *
from gen_mb_client import *
from gen_mysql_connect import *

__all__ = ["TestBUAPSHM"]


class TestBUAPSHM(object):

    __resist = Resistor()
    __read_mb = ReadMB()
    __ctrl_kl = CtrlKL()
    __mysql_conn = MySQLConnect()
    __fault = Bug(None)

    def __init__(self):
        pass

    def st_test_10_bu_apsh_m(self) -> bool:
        """
        Тест 1. Проверка исходного состояния контактов блока:
        """
        in_a1, in_a2 = self.__inputs_a()
        if in_a1 is False and in_a2 is False:
            pass
        else:
            self.__mysql_conn.mysql_ins_result('неисправен', '1')
            if in_a1 is True:
                self.__mysql_conn.mysql_error(99)
            elif in_a2 is True:
                self.__mysql_conn.mysql_error(100)
            return False
        return True

    def st_test_11_bu_apsh_m(self) -> bool:
        """
        1.1. Проверка состояния контактов блока при подаче напряжения питания
        """
        self.__ctrl_kl.ctrl_relay('KL21', True)
        sleep(1)
        in_a1, in_a2 = self.__inputs_a()
        if in_a1 is False and in_a2 is False:
            pass
        else:
            self.__mysql_conn.mysql_ins_result('неисправен', '1')
            if in_a1 is True:
                self.__mysql_conn.mysql_error(101)
            elif in_a2 is True:
                self.__mysql_conn.mysql_error(102)
            return False
        self.__mysql_conn.mysql_ins_result('исправен', '1')
        return True

    def st_test_20_bu_apsh_m(self) -> bool:
        """
        2. Проверка включения / выключения 1 канала блока от кнопки «Пуск / Стоп».
        """
        if self.__subtest_20():
            pass
        else:
            self.__mysql_conn.mysql_ins_result('неисправен', '2')
            return False
        # 2.1. Выключение 1 канала блока от кнопки «Пуск» при сопротивлении 10 Ом
        self.__ctrl_kl.ctrl_relay('KL12', False)
        in_a1, in_a2 = self.__inputs_a()
        if in_a1 is False and in_a2 is False:
            pass
        else:
            self.__mysql_conn.mysql_ins_result('неисправен', '2')
            if in_a1 is True:
                self.__mysql_conn.mysql_error(105)
            elif in_a2 is True:
                self.__mysql_conn.mysql_error(106)
            return False
        self.__mysql_conn.mysql_ins_result('исправен', '2')
        return True

    def st_test_30_bu_apsh_m(self) -> bool:
        """
        3. Отключение 1 канала блока при увеличении сопротивления
        цепи заземления на величину более 100 Ом
        """
        if self.__subtest_20():
            pass
        else:
            self.__mysql_conn.mysql_ins_result('неисправен', '3')
        self.__resist.resist_10_to_110_ohm()
        in_a1, in_a2 = self.__inputs_a()
        if in_a1 is False and in_a2 is False:
            pass
        else:
            self.__mysql_conn.mysql_ins_result('неисправен', '3')
            if in_a1 is True:
                self.__mysql_conn.mysql_error(107)
            elif in_a2 is True:
                self.__mysql_conn.mysql_error(108)
            return False
        self.__mysql_conn.mysql_ins_result('исправен', '3')
        self.__ctrl_kl.ctrl_relay('KL12', False)
        return True

    def st_test_40_bu_apsh_m(self) -> bool:
        """
        4. Защита от потери управляемости 1 канала блока при замыкании проводов ДУ
        """
        if self.__subtest_20():
            pass
        else:
            self.__mysql_conn.mysql_ins_result('неисправен', '4')
            return False
        self.__ctrl_kl.ctrl_relay('KL11', True)
        sleep(2)
        in_a1, in_a2 = self.__inputs_a()
        if in_a1 is False and in_a2 is False:
            pass
        else:
            self.__mysql_conn.mysql_ins_result('неисправен', '4')
            if in_a1 is True:
                self.__mysql_conn.mysql_error(109)
            elif in_a2 is True:
                self.__mysql_conn.mysql_error(110)
            return False
        self.__mysql_conn.mysql_ins_result('исправен', '4')
        self.__ctrl_kl.ctrl_relay('KL12', False)
        self.__ctrl_kl.ctrl_relay('KL11', False)
        sleep(2)
        return True

    def st_test_50_bu_apsh_m(self) -> bool:
        """
        Тест 5. Защита от потери управляемости 1 канала блока при обрыве проводов ДУ
        """
        if self.__subtest_20():
            pass
        else:
            self.__mysql_conn.mysql_ins_result('неисправен', '5')
            return False
        self.__ctrl_kl.ctrl_relay('KL12', False)
        sleep(2)
        in_a1, in_a2 = self.__inputs_a()
        if in_a1 is False and in_a2 is False:
            pass
        else:
            self.__mysql_conn.mysql_ins_result('неисправен', '5')
            if in_a1 is True:
                self.__mysql_conn.mysql_error(111)
            elif in_a2 is True:
                self.__mysql_conn.mysql_error(112)
            return False
        self.__mysql_conn.mysql_ins_result('исправен', '5')
        return True

    def st_test_60_bu_apsh_m(self) -> bool:
        """
        6. Проверка включения / выключения 2 канала блока от кнопки «Пуск / Стоп».
        6.1. Включение 1 канала блока от кнопки «Пуск» при сопротивлении 10 Ом.
        """
        self.__ctrl_kl.ctrl_relay('KL26', True)
        sleep(2)
        if self.__subtest_61():
            pass
        else:
            self.__mysql_conn.mysql_ins_result('неисправен', '6')
            return False
        # 6.2. Выключение 2 канала блока от кнопки «Пуск» при сопротивлении 10 Ом
        self.__ctrl_kl.ctrl_relay('KL12', False)
        sleep(2)
        in_a1, in_a2 = self.__inputs_a()
        if in_a1 is False and in_a2 is False:
            pass
        else:
            self.__mysql_conn.mysql_ins_result('неисправен', '6')
            if in_a1 is True:
                self.__mysql_conn.mysql_error(115)
            elif in_a2 is True:
                self.__mysql_conn.mysql_error(116)
            return False
        self.__mysql_conn.mysql_ins_result('исправен', '6')
        return True

    def st_test_70_bu_apsh_m(self) -> bool:
        """
        7. Отключение 2 канала блока при увеличении сопротивления цепи заземления
        на величину более 100 Ом
        """
        sleep(2)
        if self.__subtest_61():
            pass
        else:
            self.__mysql_conn.mysql_ins_result('неисправен', '7')
            return False
        self.__resist.resist_10_to_110_ohm()
        in_a1, in_a2 = self.__inputs_a()
        if in_a1 is False and in_a2 is False:
            pass
        else:
            self.__mysql_conn.mysql_ins_result('неисправен', '7')
            if in_a1 is True:
                self.__mysql_conn.mysql_error(117)
            elif in_a2 is True:
                self.__mysql_conn.mysql_error(118)
            return False
        self.__mysql_conn.mysql_ins_result('исправен', '7')
        self.__ctrl_kl.ctrl_relay('KL12', False)
        return True

    def st_test_80_bu_apsh_m(self) -> bool:
        """
        8. Защита от потери управляемости 2 канала блока при замыкании проводов ДУ
        """
        sleep(2)
        if self.__subtest_61():
            pass
        else:
            self.__mysql_conn.mysql_ins_result('неисправен', '8')
        self.__ctrl_kl.ctrl_relay('KL11', True)
        sleep(2)
        in_a1, in_a2 = self.__inputs_a()
        if in_a1 is False and in_a2 is False:
            pass
        else:
            self.__mysql_conn.mysql_ins_result('неисправен', '8')
            if in_a1 is True:
                self.__mysql_conn.mysql_error(119)
            elif in_a2 is True:
                self.__mysql_conn.mysql_error(120)
            return False
        self.__mysql_conn.mysql_ins_result('исправен', '8')
        self.__ctrl_kl.ctrl_relay('KL12', False)
        self.__ctrl_kl.ctrl_relay('KL11', False)
        return True

    def st_test_90_bu_apsh_m(self) -> bool:
        """
        Тест 9. Защита от потери управляемости 2 канала блока при обрыве проводов ДУ
        """
        if self.__subtest_61():
            pass
        else:
            self.__mysql_conn.mysql_ins_result('неисправен', '9')
        self.__ctrl_kl.ctrl_relay('KL12', False)
        sleep(2)
        in_a1, in_a2 = self.__inputs_a()
        if in_a1 is False and in_a2 is False:
            pass
        else:
            self.__mysql_conn.mysql_ins_result('неисправен', '9')
            if in_a1 is True:
                self.__mysql_conn.mysql_error(121)
            elif in_a2 is True:
                self.__mysql_conn.mysql_error(122)
            return False
        self.__mysql_conn.mysql_ins_result('исправен', '9')
        return True

    def __subtest_20(self):
        self.__resist.resist_ohm(10)
        sleep(2)
        self.__ctrl_kl.ctrl_relay('KL12', True)
        sleep(2)
        in_a1, in_a2 = self.__inputs_a()
        sleep(1)
        if in_a1 is True and in_a2 is False:
            pass
        else:
            if in_a1 is False:
                self.__mysql_conn.mysql_error(103)
            elif in_a2 is True:
                self.__mysql_conn.mysql_error(104)
            return False
        return True

    def __subtest_61(self):
        self.__resist.resist_ohm(10)
        sleep(2)
        self.__ctrl_kl.ctrl_relay('KL12', True)
        sleep(2)
        in_a1, in_a2 = self.__inputs_a()
        sleep(1)
        if in_a1 is False and in_a2 is True:
            pass
        else:
            if in_a1 is True:
                self.__mysql_conn.mysql_error(113)
            elif in_a2 is False:
                self.__mysql_conn.mysql_error(114)
            return False
        return True

    def __inputs_a(self):
        in_a1 = self.__read_mb.read_discrete(1)
        in_a2 = self.__read_mb.read_discrete(2)
        if in_a1 is None or in_a2 is None:
            raise ModbusConnectException(f'нет связи с контроллером')
        return in_a1, in_a2

    def st_test_bu_apsh_m(self) -> bool:
        if self.st_test_10_bu_apsh_m():
            if self.st_test_11_bu_apsh_m():
                if self.st_test_20_bu_apsh_m():
                    if self.st_test_30_bu_apsh_m():
                        if self.st_test_40_bu_apsh_m():
                            if self.st_test_50_bu_apsh_m():
                                if self.st_test_60_bu_apsh_m():
                                    if self.st_test_70_bu_apsh_m():
                                        if self.st_test_80_bu_apsh_m():
                                            if self.st_test_90_bu_apsh_m():
                                                return True
        return False


if __name__ == '__main__':
    test_bu_apsh_m = TestBUAPSHM()
    reset_test_bu_apsh_m = ResetRelay()
    mysql_conn_bu_apsh_m = MySQLConnect()
    fault = Bug(True)
    try:
        if test_bu_apsh_m.st_test_bu_apsh_m():
            mysql_conn_bu_apsh_m.mysql_block_good()
            my_msg('Блок исправен', '#1E8C1E')
        else:
            mysql_conn_bu_apsh_m.mysql_block_bad()
            my_msg('Блок неисправен', '#A61E1E')
    except OSError:
        my_msg("ошибка системы", '#A61E1E')
    except SystemError:
        my_msg("внутренняя ошибка", '#A61E1E')
    except ModbusConnectException as mce:
        fault.debug_msg(mce, 1)
        my_msg(str(mce), '#A61E1E')
    finally:
        reset_test_bu_apsh_m.reset_all()
        sys.exit()
