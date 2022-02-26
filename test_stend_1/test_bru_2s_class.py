#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Алгоритм проверки

Тип блока	Производитель	    Уникальный номер
БРУ-2С	Нет производителя

"""

from sys import exit
from my_msgbox import *
from gen_func_procedure import *
from gen_func_utils import *
from gen_mb_client import *
from gen_mysql_connect import *

__all__ = ["TestBRU2S"]

reset = ResetRelay()
proc = Procedure()
resist = Resistor()
read_mb = ReadMB()
ctrl_kl = CtrlKL()
mysql_conn = MySQLConnect()


class TestBRU2S(object):
    def __init__(self):
        pass

    def st_test_bru_2s(self):
        # reset.reset_all()
        # Тест 1. Проверка исходного состояния блока:
        in_a1 = self.__inputs_a()
        if in_a1 == False:
            pass
        else:
            mysql_conn.mysql_ins_result('неисправен', '1')
            mysql_conn.mysql_error(47)
            return False
        mysql_conn.mysql_ins_result('исправен', '1')
        # Тест 2. Проверка включения/выключения блока от кнопки «Пуск/Стоп»
        ctrl_kl.ctrl_relay('KL21', True)
        in_a1 = self.__inputs_a()
        if in_a1 == False:
            pass
        else:
            mysql_conn.mysql_ins_result('неисправен', '2')
            mysql_conn.mysql_error(48)
            return False
        # 2.2. Включение блока от кнопки «Пуск»
        # 2.3. Проверка удержания блока во включенном состоянии при подключении Rш пульта управления:
        if self.__subtest_22_23():
            pass
        else:
            mysql_conn.mysql_ins_result('неисправен', '2')
            return False
        # 2.4. Выключение блока от кнопки «Стоп»
        ctrl_kl.ctrl_relay('KL12', False)
        in_a1 = self.__inputs_a()
        if in_a1 == False:
            pass
        else:
            mysql_conn.mysql_ins_result('неисправен', '2')
            mysql_conn.mysql_error(51)
            return False
        ctrl_kl.ctrl_relay('KL25', False)
        mysql_conn.mysql_ins_result('исправен', '2')
        # 3. Отключение выходного контакта блока при увеличении сопротивления цепи заземления
        if self.__subtest_22_23():
            pass
        else:
            mysql_conn.mysql_ins_result('неисправен', '3')
            return False
        resist.resist_ohm(150)
        in_a1 = self.__inputs_a()
        if in_a1 == False:
            pass
        else:
            mysql_conn.mysql_ins_result('неисправен', '3')
            mysql_conn.mysql_error(52)
            return False
        ctrl_kl.ctrl_relay('KL12', False)
        ctrl_kl.ctrl_relay('KL25', False)
        mysql_conn.mysql_ins_result('исправен', '3')
        # 4. Защита от потери управляемости при замыкании проводов ДУ
        if self.__subtest_22_23():
            pass
        else:
            mysql_conn.mysql_ins_result('неисправен', '4')
            return False
        ctrl_kl.ctrl_relay('KL11', True)
        in_a1 = self.__inputs_a()
        if in_a1 == False:
            pass
        else:
            mysql_conn.mysql_error(53)
            mysql_conn.mysql_ins_result('неисправен', '4')
            return False
        ctrl_kl.ctrl_relay('KL12', False)
        ctrl_kl.ctrl_relay('KL25', False)
        ctrl_kl.ctrl_relay('KL11', False)
        mysql_conn.mysql_ins_result('исправен', '4')
        # Тест 5. Защита от потери управляемости блока при обрыве проводов ДУ
        if self.__subtest_22_23():
            pass
        else:
            mysql_conn.mysql_ins_result('неисправен', '5')
            return False
        ctrl_kl.ctrl_relay('KL12', False)
        in_a1 = self.__inputs_a()
        if in_a1 == False:
            pass
        else:
            mysql_conn.mysql_error(54)
            mysql_conn.mysql_ins_result('неисправен', '5')
            return False
        ctrl_kl.ctrl_relay('KL25', False)
        mysql_conn.mysql_ins_result('исправен', '5')
        #########################################################################################
        # Сообщение	Переведите тумблер «П/А» на блоке в положение «П» и нажмите кнопку «ОК».    #
        #Если на блоке нет тумблера «П/А» нажмите кнопку «Нет тумблера»                         #
        #########################################################################################
        msg_1 = "Переведите тумблер «П/А» на блоке в положение «П» и нажмите кнопку «ОК» " \
                "Если на блоке нет тумблера «П/А» нажмите кнопку «Отмена»"
        if my_msg(msg_1):
            if self.__subtest_6():
                mysql_conn.mysql_ins_result('исправен', '6')
                if self.__subtest_7():
                    mysql_conn.mysql_ins_result('исправен', '7')
                else:
                    mysql_conn.mysql_ins_result('неисправен', '7')
                    return False
            else:
                mysql_conn.mysql_ins_result('неисправен', '6')
                return False
        else:
            if self.__subtest_7():
                mysql_conn.mysql_ins_result('пропущен', '6')
                mysql_conn.mysql_ins_result('исправен', '7')
            else:
                mysql_conn.mysql_ins_result('пропущен', '6')
                mysql_conn.mysql_ins_result('неисправен', '7')
                return False
        return True
    
    def __subtest_22_23(self):
        # 2.2. Включение блока от кнопки «Пуск»
        # 2.3. Проверка удержания блока во включенном состоянии при подключении Rш пульта управления:
        resist.resist_ohm(0)
        ctrl_kl.ctrl_relay('KL12', True)
        in_a1 = self.__inputs_a()
        if in_a1 == True:
            pass
        else:
            mysql_conn.mysql_error(49)
            return False
        ctrl_kl.ctrl_relay('KL25', True)
        in_a1 = self.__inputs_a()
        if in_a1 == True:
            return True
        else:
            mysql_conn.mysql_error(50)
            return False
    
    def __subtest_6(self):
        # Тест 6. Блокировка включения блока при снижении сопротивления изоляции
        # контролируемого присоединения до уровня предупредительной уставки
        resist.resist_kohm(200)
        ctrl_kl.ctrl_relay('KL12', True)
        in_a1 = self.__inputs_a()
        if in_a1 == False:
            ctrl_kl.ctrl_relay('KL12', False)
            return True
        else:
            mysql_conn.mysql_error(55)
            return False
    
    def __subtest_7(self):
        # Тест 7. Блокировка включения блока при снижении сопротивления изоляции
        # контролируемого присоединения до уровня аварийной уставки
        resist.resist_kohm(30)
        ctrl_kl.ctrl_relay('KL12', True)
        in_a1 = self.__inputs_a()
        if in_a1 == False:
            ctrl_kl.ctrl_relay('KL12', False)
            return True
        else:
            mysql_conn.mysql_error(56)
            return False
    
    @staticmethod
    def __inputs_a():
        in_a1 = read_mb.read_discrete(1)
        return in_a1


if __name__ == '__main__':
    try:
        test_bru_2s = TestBRU2S()
        if test_bru_2s.st_test_bru_2s():
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
