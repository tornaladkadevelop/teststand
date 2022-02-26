#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Алгоритм проверки
Тип блока	Производитель
БКИ	нет производителя
БКИ	Углеприбор
БКИ-П	Пульсар

"""

from sys import exit
from time import sleep
from gen_func_utils import *
from my_msgbox import *
from gen_mb_client import *
from gen_mysql_connect import *

__all__ = ["TestBKIP"]

reset = ResetRelay()
resist = Resistor()
ctrl_kl = CtrlKL()
read_mb = ReadMB()
mysql_conn = MySQLConnect()
fault = Bug(None)


class TestBKIP(object):
    def __init__(self):
        pass
    
    def st_test_bki_p(self):
        # reset.reset_all()
        in_0, in_1 = self.__inputs_a()
        if in_0 == True and in_1 == False: 
            pass
        elif in_0 == False or in_1 == True:
            mysql_conn.mysql_ins_result("неисправен", "1")
            mysql_conn.mysql_error(30)
            return False
        mysql_conn.mysql_ins_result("исправен", "1")
        # Тест 2. Проверка работы блока при нормальном сопротивлении изоляции
        # Сообщение	Переведите тумблер на блоке в режим «Предупредительный»
        msg_1 = 'Переведите тумблер на блоке в режим «Предупредительный»'
        if my_msg(msg_1):
            pass
        else:
            return False
        ctrl_kl.ctrl_relay('KL21', True)
        sleep(2)
        resist.resist_kohm(220)
        sleep(2)
        in_0, in_1 = self.__inputs_a()
        if in_0 == True and in_1 == False:
            pass
        elif in_0 == False or in_1 == True:
            mysql_conn.mysql_ins_result("неисправен", "2")
            mysql_conn.mysql_error(31)
            return False
        mysql_conn.mysql_ins_result("исправен", "2")
        # Тест 3. Проверка работы блока в режиме «Предупредительный» при снижении
        # уровня сопротивлении изоляции до 100 кОм
        resist.resist_220_to_100_kohm()
        b = ctrl_kl.ctrl_ai_code_100()
        i = 0
        while b == 2 or i <= 10:
            sleep(0.2)
            i += 1
            b = ctrl_kl.ctrl_ai_code_100()
            if b == 0:
                break
            elif b == 1:
                mysql_conn.mysql_error(32)
                return False
        mysql_conn.mysql_ins_result("исправен", "3")
        # Тест 4. Проверка работы блока в режиме «Аварийный» при сопротивлении изоляции 100 кОм
        # Сообщение	Переведите тумблер на блоке в режим «Аварийный»
        msg_2 = 'Переведите тумблер на блоке в режим «Аварийный»'
        if my_msg(msg_2):
            pass
        else:
            return False
        sleep(2)
        in_a0, in_a1 = self.__inputs_a()
        if in_a0 == True and in_a1 == False:
            pass
        else:
            mysql_conn.mysql_ins_result("неисправен", "4")
            mysql_conn.mysql_error(33)
            ctrl_kl.ctrl_relay('KL21', False)
            return False
        mysql_conn.mysql_ins_result("исправен", "4")
        # Тест 5. Работа блока в режиме «Аварийный» при сопротивлении изоляции
        # ниже 30 кОм (Подключение на внутреннее сопротивление)
        # resist.resist_kohm(220)
        ctrl_kl.ctrl_relay('KL22', True)
        in_a0, in_a1 = self.__inputs_a()
        if in_a0 == False and in_a1 == True:
            pass
        else:
            mysql_conn.mysql_ins_result("неисправен", "5")
            mysql_conn.mysql_error(34)
    
            return False
        ctrl_kl.ctrl_relay('KL21', False)
        mysql_conn.mysql_ins_result("исправен", "5")
        return True
    
    @staticmethod
    def __inputs_a():
        in_0 = read_mb.read_discrete(0)
        in_1 = read_mb.read_discrete(1)
        return in_0, in_1


if __name__ == '__main__':
    try:
        test_bki_p = TestBKIP()
        if test_bki_p.st_test_bki_p():
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
