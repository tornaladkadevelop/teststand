#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Алгоритм проверки
Тип блока Производитель
БУ ПМВИР (пускатель)	Без Производителя

"""

from sys import exit
from time import sleep
from gen_func_utils import *
from my_msgbox import *
from gen_mb_client import *
from gen_mysql_connect import *

__all__ = ["TestBUPMVIR"]

reset = ResetRelay()
resist = Resistor()
read_mb = ReadMB()
ctrl_kl = CtrlKL()
mysql_conn = MySQLConnect()
fault = Bug(None)


class TestBUPMVIR(object):
    def __init__(self):
        pass
    
    def st_test_bu_pmvir(self):
        # reset.reset_all()
        # Тест 1. Проверка исходного состояния блока:
        in_a1 = self.__inputs_a()
        if in_a1 == False:
            pass
        else:
            mysql_conn.mysql_error(89)
            mysql_conn.mysql_ins_result("неисправен", '1')
        # 1.1. Проверка состояния контактов блока при подаче напряжения питания
        # opc['Устройство.tg.in_cont_ser_KT_KL27'] = True
        ctrl_kl.ctrl_relay('KL21', True)
        in_a1 = self.__inputs_a()
        if in_a1 == False:
            pass
        else:
            mysql_conn.mysql_error(90)
            mysql_conn.mysql_ins_result("неисправен", '1')
            return False
        mysql_conn.mysql_ins_result("исправен", '1')
        # 2. Проверка включения/выключения блока от кнопки «Пуск/Стоп».
        # 2.1. Проверка исходного состояния блока
        if self.__subtest_21():
            pass
        else:
            mysql_conn.mysql_ins_result("неисправен", '2')
            return False
        # 2.2. Выключение блока от кнопки «Стоп» при сопротивлении 10 Ом
        ctrl_kl.ctrl_relay('KL12', False)
        in_a1 = self.__inputs_a()
        if in_a1 == False:
            pass
        else:
            mysql_conn.mysql_error(92)
            mysql_conn.mysql_ins_result("неисправен", '2')
            return False
        mysql_conn.mysql_ins_result("исправен", '2')
        # 3. Проверка блокировки включения блока при снижении сопротивления изоляции контролируемого присоединения:
        ctrl_kl.ctrl_relay('KL22', True)
        resist.resist_ohm(10)
        ctrl_kl.ctrl_relay('KL12', True)
        in_a1 = self.__inputs_a()
        if in_a1 == False:
            pass
        else:
            mysql_conn.mysql_error(93)
            mysql_conn.mysql_ins_result("неисправен", '3')
            return False
        ctrl_kl.ctrl_relay('KL22', False)
        ctrl_kl.ctrl_relay('KL12', False)
        mysql_conn.mysql_ins_result("исправен", '3')
        # 4.  Отключение блока при увеличении сопротивления цепи заземления на величину более 100 Ом
        if self.__subtest_21():
            pass
        else:
            mysql_conn.mysql_ins_result("неисправен", '4')
            return False
        resist.resist_10_to_137_ohm()
        sleep(1)
        in_a1 = self.__inputs_a()
        if in_a1 == False:
            pass
        else:
            mysql_conn.mysql_error(94)
            mysql_conn.mysql_ins_result("неисправен", '4')
            return False
        ctrl_kl.ctrl_relay('KL12', False)
        mysql_conn.mysql_ins_result("исправен", '4')
        # Тест 5. Защита от потери управляемости блока при замыкании проводов ДУ
        if self.__subtest_21():
            pass
        else:
            mysql_conn.mysql_ins_result("неисправен", '5')
            return False
        ctrl_kl.ctrl_relay('KL11', True)
        in_a1 = self.__inputs_a()
        if in_a1 == False:
            pass
        else:
            mysql_conn.mysql_error(95)
            mysql_conn.mysql_ins_result("неисправен", '5')
            return False
        ctrl_kl.ctrl_relay('KL12', False)
        ctrl_kl.ctrl_relay('KL11', False)
        mysql_conn.mysql_ins_result("исправен", '5')
        # Тест 6. Защита от потери управляемости блока при обрыве проводов ДУ
        if self.__subtest_21():
            pass
        else:
            mysql_conn.mysql_ins_result("неисправен", '6')
            return False
        ctrl_kl.ctrl_relay('KL12', False)
        in_a1 = self.__inputs_a()
        if in_a1 == False:
            pass
        else:
            mysql_conn.mysql_error(96)
            mysql_conn.mysql_ins_result("неисправен", '6')
            return False
        mysql_conn.mysql_ins_result("исправен", '6')
        # 7. Проверка отключения блока от срабатывания защиты УМЗ.
        if self.__subtest_21():
            pass
        else:
            mysql_conn.mysql_ins_result("неисправен", '7')
            return False
        ctrl_kl.ctrl_relay('KL27', False)
        ctrl_kl.ctrl_relay('KL30', True)
        sleep(2)
        ctrl_kl.ctrl_relay('KL27', True)
        sleep(6)
        in_a1 = self.__inputs_a()
        if in_a1 == False:
            pass
        else:
            mysql_conn.mysql_error(97)
            mysql_conn.mysql_ins_result("неисправен", '7')
            return False
        ctrl_kl.ctrl_relay('KL30', False)
        sleep(6)
        in_a1 = self.__inputs_a()
        if in_a1 == True:
            pass
        else:
            mysql_conn.mysql_error(98)
            mysql_conn.mysql_ins_result("неисправен", '7')
            return False
        mysql_conn.mysql_ins_result("исправен", '7')
        return True
    
    def __subtest_21(self):
        # 2.1. Включение блока от кнопки «Пуск» при сопротивлении 10 Ом
        resist.resist_ohm(10)
        ctrl_kl.ctrl_relay('KL12', True)
        sleep(1)
        in_a1 = self.__inputs_a()
        if in_a1 == True:
            return True
        else:
            mysql_conn.mysql_error(91)
            return False
    
    @staticmethod
    def __inputs_a():
        in_a1 = read_mb.read_discrete(1)
        return in_a1


if __name__ == '__main__':
    try:
        test_bu_pmvir = TestBUPMVIR()
        if test_bu_pmvir.st_test_bu_pmvir():
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
