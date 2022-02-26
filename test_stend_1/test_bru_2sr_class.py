#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Алгоритм проверки

Тип блока	Производитель	    Уникальный номер
БРУ-2СР	Нет производителя

"""

from time import sleep
from sys import exit
from my_msgbox import *
from gen_func_utils import *
from gen_mb_client import *
from gen_mysql_connect import *

__all__ = ["TestBRU2SR"]

reset = ResetRelay()
resist = Resistor()
read_mb = ReadMB()
ctrl_kl = CtrlKL()
mysql_conn = MySQLConnect()
fault = Bug(None)


class TestBRU2SR(object):
    def __init__(self):
        pass
    
    def st_test_bru_2sr(self):
        # reset.reset_all()
        # Тест 1. Проверка исходного состояния блока:
        in_a1, in_a2 = self.__inputs_a()
        if in_a1 == False and in_a2 == False:
            pass
        else:
            mysql_conn.mysql_ins_result('неисправен', '1')
            if in_a1 == True:
                mysql_conn.mysql_error(57)
            elif in_a2 == True:
                mysql_conn.mysql_error(58)
            return False
        mysql_conn.mysql_ins_result('исправен', '1')
        # Тест 2. Проверка включения/выключения блока от кнопки «Пуск/Стоп» в режиме «Вперёд».
        ctrl_kl.ctrl_relay('KL21', True)
        in_a1, in_a2 = self.__inputs_a()
        if in_a1 == False and in_a2 == False:
            pass
        else:
            mysql_conn.mysql_ins_result('неисправен', '2')
            if in_a1 == True:
                mysql_conn.mysql_error(59)
            elif in_a2 == True:
                mysql_conn.mysql_error(60)
            return False
        # 2.2. Включение блока от кнопки «Пуск»
        # 2.3. Проверка удержания блока во включенном состоянии при подключении Rш пульта управления:
        if self.__subtest_22_23():
            pass
        else:
            mysql_conn.mysql_ins_result('неисправен', '2')
        # 2.4. Выключение блока от кнопки «Стоп»
        ctrl_kl.ctrl_relay('KL12', False)
        in_a1, in_a2 = self.__inputs_a()
        if in_a1 == False and in_a2 == False:
            pass
        else:
            mysql_conn.mysql_ins_result('неисправен', '2')
            if in_a1 == True:
                mysql_conn.mysql_error(65)
            elif in_a2 == True:
                mysql_conn.mysql_error(66)
            return False
        ctrl_kl.ctrl_relay('KL25', False)
        mysql_conn.mysql_ins_result('исправен', '2')
        # 3. Отключение контакта «Вперёд» при увеличении сопротивления цепи заземления
        if self.__subtest_22_23():
            pass
        else:
            mysql_conn.mysql_ins_result('неисправен', '3')
            return False
        resist.resist_ohm(150)
        sleep(1)
        in_a1, in_a2 = self.__inputs_a()
        if in_a1 == False and in_a2 == False:
            pass
        else:
            mysql_conn.mysql_ins_result('неисправен', '3')
            if in_a1 == True:
                mysql_conn.mysql_error(67)
            elif in_a2 == True:
                mysql_conn.mysql_error(68)
            return False
        ctrl_kl.ctrl_relay('KL12', False)
        ctrl_kl.ctrl_relay('KL25', False)
        mysql_conn.mysql_ins_result('исправен', '3')
        # 4. Защита от потери управляемости канала «Вперёд» при замыкании проводов ДУ
        if self.__subtest_22_23():
            pass
        else:
            mysql_conn.mysql_ins_result('неисправен', '4')
            return False
        ctrl_kl.ctrl_relay('KL11', True)
        in_a1, in_a2 = self.__inputs_a()
        if in_a1 == False and in_a2 == False:
            pass
        else:
            mysql_conn.mysql_ins_result('неисправен', '4')
            if in_a1 == True:
                mysql_conn.mysql_error(69)
            elif in_a2 == True:
                mysql_conn.mysql_error(70)
            return False
        ctrl_kl.ctrl_relay('KL12', False)
        ctrl_kl.ctrl_relay('KL25', False)
        ctrl_kl.ctrl_relay('KL11', False)
        mysql_conn.mysql_ins_result('исправен', '4')
        # Тест 5. Защита от потери управляемости канала «Вперёд» при обрыве проводов ДУ
        if self.__subtest_22_23():
            pass
        else:
            mysql_conn.mysql_ins_result('неисправен', '5')
            return False
        ctrl_kl.ctrl_relay('KL12', False)
        in_a1, in_a2 = self.__inputs_a()
        if in_a1 == False and in_a2 == False:
            pass
        else:
            mysql_conn.mysql_ins_result('неисправен', '5')
            if in_a1 == True:
                mysql_conn.mysql_error(71)
            elif in_a2 == True:
                mysql_conn.mysql_error(72)
            return False
        ctrl_kl.ctrl_relay('KL25', False)
        mysql_conn.mysql_ins_result('исправен', '5')
        # Тест 6. Проверка включения/выключения блока от кнопки «Пуск/Стоп» в режиме «Назад».
        ctrl_kl.ctrl_relay('KL26', True)
        in_a1, in_a2 = self.__inputs_a()
        if in_a1 == False and in_a2 == False:
            pass
        else:
            mysql_conn.mysql_ins_result('неисправен', '6')
            if in_a1 == True:
                mysql_conn.mysql_error(59)
            elif in_a2 == True:
                mysql_conn.mysql_error(60)
            return False
        # 6.2. Включение блока от кнопки «Пуск» режима «Назад»
        # 6.3. Проверка удержания блока во включенном состоянии
        # при подключении Rш пульта управления режима «Назад»:
        if self.__subtest_62_63():
            pass
        else:
            mysql_conn.mysql_ins_result('неисправен', '6')
            return False
        # 6.4. Выключение блока от кнопки «Стоп» режима «Назад»
        ctrl_kl.ctrl_relay('KL12', False)
        in_a1, in_a2 = self.__inputs_a()
        if in_a1 == False and in_a2 == False:
            pass
        else:
            mysql_conn.mysql_ins_result('неисправен', '6')
            if in_a1 == True:
                mysql_conn.mysql_error(77)
            elif in_a2 == True:
                mysql_conn.mysql_error(78)
            return False
        ctrl_kl.ctrl_relay('KL25', False)
        mysql_conn.mysql_ins_result('исправен', '6')
        # 7. Отключение контакта «Назад» при увеличении сопротивления цепи заземления
        if self.__subtest_62_63():
            pass
        else:
            mysql_conn.mysql_ins_result('неисправен', '7')
            return False
        resist.resist_ohm(150)
        in_a1, in_a2 = self.__inputs_a()
        if in_a1 == False and in_a2 == False:
            pass
        else:
            mysql_conn.mysql_ins_result('неисправен', '7')
            if in_a1 == True:
                mysql_conn.mysql_error(79)
            elif in_a2 == True:
                mysql_conn.mysql_error(80)
            return False
        ctrl_kl.ctrl_relay('KL12', False)
        ctrl_kl.ctrl_relay('KL25', False)
        mysql_conn.mysql_ins_result('исправен', '7')
        # 8. Защита от потери управляемости канала «Назад» при замыкании проводов ДУ
        if self.__subtest_62_63():
            pass
        else:
            mysql_conn.mysql_ins_result('неисправен', '8')
            return False
        ctrl_kl.ctrl_relay('KL11', True)
        in_a1, in_a2 = self.__inputs_a()
        if in_a1 == False and in_a2 == False:
            pass
        else:
            mysql_conn.mysql_ins_result('неисправен', '8')
            if in_a1 == True:
                mysql_conn.mysql_error(81)
            elif in_a2 == True:
                mysql_conn.mysql_error(82)
            return False
        ctrl_kl.ctrl_relay('KL12', False)
        ctrl_kl.ctrl_relay('KL25', False)
        ctrl_kl.ctrl_relay('KL11', False)
        mysql_conn.mysql_ins_result('исправен', '8')
        # Тест 9. Защита от потери управляемости канала «Назад» при обрыве проводов ДУ
        if self.__subtest_62_63():
            pass
        else:
            mysql_conn.mysql_ins_result('неисправен', '9')
            return False
        ctrl_kl.ctrl_relay('KL12', False)
        in_a1, in_a2 = self.__inputs_a()
        if in_a1 == False and in_a2 == False:
            pass
        else:
            mysql_conn.mysql_ins_result('неисправен', '9')
            if in_a1 == True:
                mysql_conn.mysql_error(83)
            elif in_a2 == True:
                mysql_conn.mysql_error(84)
            return False
        ctrl_kl.ctrl_relay('KL25', False)
        mysql_conn.mysql_ins_result('исправен', '9')
        #########################################################################################
        # Сообщение	Переведите тумблер «П/А» на блоке в положение «П» и нажмите кнопку «ОК».    #
        #Если на блоке нет тумблера «П/А» нажмите кнопку «Нет тумблера»                         #
        #########################################################################################
        msg_1 = "Переведите тумблер «П/А» на блоке в положение «П» и нажмите кнопку «ОК» " \
                "Если на блоке нет тумблера «П/А» нажмите кнопку «Отмена»"
        if my_msg(msg_1):
            if self.__subtest_10():
                mysql_conn.mysql_ins_result('исправен', '10')
                if self.__subtest_11():
                    mysql_conn.mysql_ins_result('исправен', '11')
                else:
                    mysql_conn.mysql_ins_result('неисправен', '11')
                    return False
            else:
                mysql_conn.mysql_ins_result('неисправен', '10')
                return False
        else:
            if self.__subtest_11():
                mysql_conn.mysql_ins_result('пропущен', '10')
                mysql_conn.mysql_ins_result('исправен', '11')
            else:
                mysql_conn.mysql_ins_result('пропущен', '10')
                mysql_conn.mysql_ins_result('неисправен', '11')
                return False
        return True
    
    def __subtest_22_23(self):
        # 2.2. Включение блока от кнопки «Пуск» режима «Вперёд»
        # 2.3. Проверка удержания блока во включенном состоянии при
        # подключении Rш пульта управления режима «Вперёд»:
        resist.resist_ohm(0)
        ctrl_kl.ctrl_relay('KL12', True)
        in_a1, in_a2 = self.__inputs_a()
        if in_a1 == True and in_a2 == False:
            pass
        else:
            if in_a1 == False:
                mysql_conn.mysql_error(61)
            elif in_a2 == True:
                mysql_conn.mysql_error(62)
            return False
        ctrl_kl.ctrl_relay('KL25', True)
        in_a1, in_a2 = self.__inputs_a()
        if in_a1 == True and in_a2 == False:
            pass
        else:
            if in_a1 == False:
                mysql_conn.mysql_error(63)
            elif in_a2 == True:
                mysql_conn.mysql_error(64)
            return False
        return True
    
    def __subtest_62_63(self):
        # 6.2. Включение блока от кнопки «Пуск» режима «Назад»
        # 6.3. Проверка удержания блока во включенном состоянии
        # при подключении Rш пульта управления режима «Назад»:
        resist.resist_ohm(0)
        ctrl_kl.ctrl_relay('KL12', True)
        in_a1, in_a2 = self.__inputs_a()
        if in_a1 == False and in_a2 == True:
            pass
        else:
            if in_a1 == True:
                mysql_conn.mysql_error(73)
            elif in_a2 == False:
                mysql_conn.mysql_error(74)
            return False
        ctrl_kl.ctrl_relay('KL25', True)
        in_a1, in_a2 = self.__inputs_a()
        if in_a1 == False and in_a2 == True:
            pass
        else:
            if in_a1 == True:
                mysql_conn.mysql_error(75)
            elif in_a2 == False:
                mysql_conn.mysql_error(76)
            return False
        return True
    
    def __subtest_10(self):
        # Тест 10. Блокировка включения блока при снижении сопротивления изоляции
        # контролируемого присоединения до уровня предупредительной уставки
        resist.resist_kohm(200)
        ctrl_kl.ctrl_relay('KL12', True)
        in_a1, in_a2 = self.__inputs_a()
        if in_a1 == False and in_a2 == False:
            pass
        else:
            if in_a1 == True:
                mysql_conn.mysql_error(85)
            elif in_a2 == True:
                mysql_conn.mysql_error(86)
            return False
        ctrl_kl.ctrl_relay('KL12', False)
        return True
    
    def __subtest_11(self):
        # Тест 11. Блокировка включения блока при снижении сопротивления
        # изоляции контролируемого присоединения до уровня аварийной уставки
        resist.resist_kohm(30)
        ctrl_kl.ctrl_relay('KL12', True)
        in_a1, in_a2 = self.__inputs_a()
        if in_a1 == False and in_a2 == False:
            pass
        else:
            if in_a1 == True:
                mysql_conn.mysql_error(87)
            elif in_a2 == True:
                mysql_conn.mysql_error(88)
            return False
        ctrl_kl.ctrl_relay('KL12', False)
        return True
    
    @staticmethod
    def __inputs_a():
        in_a1 = read_mb.read_discrete(1)
        in_a2 = read_mb.read_discrete(2)
        return in_a1, in_a2


if __name__ == '__main__':
    try:
        test_bru_2sr = TestBRU2SR()
        if test_bru_2sr.st_test_bru_2sr():
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
