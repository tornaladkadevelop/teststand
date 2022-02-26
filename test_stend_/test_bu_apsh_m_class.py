#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тип блока Производитель
БУ АПШ.М    Без Производителя
БУ АПШ.М    Горэкс-Светотехника 
"""

from sys import exit
from time import sleep
from gen_func_utils import *
from my_msgbox import *
from gen_mb_client import *
from gen_mysql_connect import *

__all__ = ["TestBUAPSHM"]

reset = ResetRelay()
resist = Resistor()
read_mb = ReadMB()
ctrl_kl = CtrlKL()
mysql_conn = MySQLConnect()
fault = Bug(None)


class TestBUAPSHM(object):
    def __init__(self):
        pass
    
    def st_test_bu_apsh_m(self):
        # reset.reset_all()
        # Тест 1. Проверка исходного состояния контактов блока:
        in_a1, in_a2 = self.__inputs_a()
        if in_a1 == False and in_a2 == False:
            pass
        else:
            mysql_conn.mysql_ins_result('неисправен', '1')
            if in_a1 == True:
                mysql_conn.mysql_error(99)
            elif in_a2 == True:
                mysql_conn.mysql_error(100)
            return False
        # 1.1. Проверка состояния контактов блока при подаче напряжения питания
        ctrl_kl.ctrl_relay('KL21', True)
        sleep(1)
        in_a1, in_a2 = self.__inputs_a()
        if in_a1 == False and in_a2 == False:
            pass
        else:
            mysql_conn.mysql_ins_result('неисправен', '1')
            if in_a1 == True:
                mysql_conn.mysql_error(101)
            elif in_a2 == True:
                mysql_conn.mysql_error(102)
            return False
        mysql_conn.mysql_ins_result('исправен', '1')
        # 2. Проверка включения / выключения 1 канала блока от кнопки «Пуск / Стоп».
        if self.__subtest_20():
            pass
        else:
            mysql_conn.mysql_ins_result('неисправен', '2')
            return False
        # 2.1. Выключение 1 канала блока от кнопки «Пуск» при сопротивлении 10 Ом
        ctrl_kl.ctrl_relay('KL12', False)
        in_a1, in_a2 = self.__inputs_a()
        if in_a1 == False and in_a2 == False:
            pass
        else:
            mysql_conn.mysql_ins_result('неисправен', '2')
            if in_a1 == True:
                mysql_conn.mysql_error(105)
            elif in_a2 == True:
                mysql_conn.mysql_error(106)
            return False
        mysql_conn.mysql_ins_result('исправен', '2')
        # 3. Отключение 1 канала блока при увеличении сопротивления
        # цепи заземления на величину более 100 Ом
        if self.__subtest_20():
            pass
        else:
            mysql_conn.mysql_ins_result('неисправен', '3')
        resist.resist_10_to_110_ohm()
        in_a1, in_a2 = self.__inputs_a()
        if in_a1 == False and in_a2 == False:
            pass
        else:
            mysql_conn.mysql_ins_result('неисправен', '3')
            if in_a1 == True:
                mysql_conn.mysql_error(107)
            elif in_a2 == True:
                mysql_conn.mysql_error(108)
            return False
        mysql_conn.mysql_ins_result('исправен', '3')
        ctrl_kl.ctrl_relay('KL12', False)
        # 4. Защита от потери управляемости 1 канала блока при замыкании проводов ДУ
        # Повторить пп.2.0
        if self.__subtest_20():
            pass
        else:
            mysql_conn.mysql_ins_result('неисправен', '4')
            return False
        ctrl_kl.ctrl_relay('KL11', True)
        sleep(2)
        in_a1, in_a2 = self.__inputs_a()
        if in_a1 == False and in_a2 == False:
            pass
        else:
            mysql_conn.mysql_ins_result('неисправен', '4')
            if in_a1 == True:
                mysql_conn.mysql_error(109)
            elif in_a2 == True:
                mysql_conn.mysql_error(110)
            return False
        mysql_conn.mysql_ins_result('исправен', '4')
        ctrl_kl.ctrl_relay('KL12', False)
        ctrl_kl.ctrl_relay('KL11', False)
        sleep(2)
        # Тест 5. Защита от потери управляемости 1 канала блока при обрыве проводов ДУ
        # Повторить пп.2.0
        # 2.0.Включение 1 канала блока от кнопки «Пуск» при сопротивлении 10 Ом
        if self.__subtest_20():
            pass
        else:
            mysql_conn.mysql_ins_result('неисправен', '5')
            return False
        ctrl_kl.ctrl_relay('KL12', False)
        sleep(2)
        in_a1, in_a2 = self.__inputs_a()
        if in_a1 == False and in_a2 == False:
            pass
        else:
            mysql_conn.mysql_ins_result('неисправен', '5')
            if in_a1 == True:
                mysql_conn.mysql_error(111)
            elif in_a2 == True:
                mysql_conn.mysql_error(112)
            return False
        mysql_conn.mysql_ins_result('исправен', '5')
        # 6. Проверка включения / выключения 2 канала блока от кнопки «Пуск / Стоп».
        # 6.1. Включение 1 канала блока от кнопки «Пуск» при сопротивлении 10 Ом.
        ctrl_kl.ctrl_relay('KL26', True)
        sleep(2)
        if self.__subtest_61():
            pass
        else:
            mysql_conn.mysql_ins_result('неисправен', '6')
            return False
        # 6.2. Выключение 2 канала блока от кнопки «Пуск» при сопротивлении 10 Ом
        ctrl_kl.ctrl_relay('KL12', False)
        sleep(2)
        in_a1, in_a2 = self.__inputs_a()
        if in_a1 == False and in_a2 == False:
            pass
        else:
            mysql_conn.mysql_ins_result('неисправен', '6')
            if in_a1 == True:
                mysql_conn.mysql_error(115)
            elif in_a2 == True:
                mysql_conn.mysql_error(116)
            return False
        mysql_conn.mysql_ins_result('исправен', '6')
        # 7. Отключение 2 канала блока при увеличении сопротивления цепи заземления
        # на величину более 100 Ом
        # Повторить пп.6.1.
        sleep(2)
        if self.__subtest_61():
            pass
        else:
            mysql_conn.mysql_ins_result('неисправен', '7')
            return False
        resist.resist_10_to_110_ohm()
        in_a1, in_a2 = self.__inputs_a()
        if in_a1 == False and in_a2 == False:
            pass
        else:
            mysql_conn.mysql_ins_result('неисправен', '7')
            if in_a1 == True:
                mysql_conn.mysql_error(117)
            elif in_a2 == True:
                mysql_conn.mysql_error(118)
            return False
        mysql_conn.mysql_ins_result('исправен', '7')
        ctrl_kl.ctrl_relay('KL12', False)
        # 8. Защита от потери управляемости 2 канала блока при замыкании проводов ДУ
        # Повторить пп.6.1 * )
        sleep(2)
        if self.__subtest_61():
            pass
        else:
            mysql_conn.mysql_ins_result('неисправен', '8')
        ctrl_kl.ctrl_relay('KL11', True)
        sleep(2)
        in_a1, in_a2 = self.__inputs_a()
        if in_a1 == False and in_a2 == False:
            pass
        else:
            mysql_conn.mysql_ins_result('неисправен', '8')
            if in_a1 == True:
                mysql_conn.mysql_error(119)
            elif in_a2 == True:
                mysql_conn.mysql_error(120)
            return False
        mysql_conn.mysql_ins_result('исправен', '8')
        ctrl_kl.ctrl_relay('KL12', False)
        ctrl_kl.ctrl_relay('KL11', False)
        # Тест 9. Защита от потери управляемости 2 канала блока при обрыве проводов ДУ
        # Повторить пп.6.1 * )
        if self.__subtest_61():
            pass
        else:
            mysql_conn.mysql_ins_result('неисправен', '9')
        ctrl_kl.ctrl_relay('KL12', False)
        sleep(2)
        in_a1, in_a2 = self.__inputs_a()
        if in_a1 == False and in_a2 == False:
            pass
        else:
            mysql_conn.mysql_ins_result('неисправен', '9')
            if in_a1 == True:
                mysql_conn.mysql_error(121)
            elif in_a2 == True:
                mysql_conn.mysql_error(122)
            return False
        mysql_conn.mysql_ins_result('исправен', '9')
        return True
    
    def __subtest_20(self):
        resist.resist_ohm(10)
        sleep(2)
        ctrl_kl.ctrl_relay('KL12', True)
        sleep(2)
        in_a1, in_a2 = self.__inputs_a()
        sleep(1)
        if in_a1 == True and in_a2 == False:
            pass
        else:
            if in_a1 == False:
                mysql_conn.mysql_error(103)
            elif in_a2 == True:
                mysql_conn.mysql_error(104)
            return False
        return True
    
    def __subtest_61(self):
        resist.resist_ohm(10)
        sleep(2)
        ctrl_kl.ctrl_relay('KL12', True)
        sleep(2)
        in_a1, in_a2 = self.__inputs_a()
        sleep(1)
        if in_a1 == False and in_a2 == True:
            pass
        else:
            if in_a1 == True:
                mysql_conn.mysql_error(113)
            elif in_a2 == False:
                mysql_conn.mysql_error(114)
            return False
        return True
    
    @staticmethod
    def __inputs_a():
        in_a1 = read_mb.read_discrete(1)
        in_a2 = read_mb.read_discrete(2)
        return in_a1, in_a2


if __name__ == '__main__':
    try:
        test_bu_apsh_m = TestBUAPSHM()
        if test_bu_apsh_m.st_test_bu_apsh_m():
            mysql_conn.mysql_block_good()
            my_msg('Блок исправен')
        else:
            mysql_conn.mysql_block_bad()
            my_msg('Блок неисправен')
    except OSError:
        my_msg("ошибка системы")
    except SystemError:
        my_msg("внутренняя ошибка")
    finally:
        reset.reset_all()
        exit()
