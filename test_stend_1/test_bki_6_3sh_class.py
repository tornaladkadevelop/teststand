#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Алгоритм проверки
Тип блока Производитель
БКИ-6-3Ш

"""

from sys import exit
from time import sleep
from gen_func_utils import *
from my_msgbox import *
from gen_mb_client import *
from gen_mysql_connect import *

__all__ = ["TestBKI6"]

reset = ResetRelay()
resist = Resistor()
result = Result()
ctrl_kl = CtrlKL()
read_mb = ReadMB()
mysql_conn = MySQLConnect()
fault = Bug(True)


class TestBKI6(object):
    def __init__(self):
        pass
    
    def st_test_bki_6_3sh(self):
        # reset.reset_all()
        # Тест 1. Проверка исходного состояния контактов блока при отсутствии напряжения питания
    
        #############################################################################################################
        # Сообщение	Убедитесь в отсутствии других блоков или соединительных кабелей в панели разъемов А
        # Подключите в разъем, расположенный на панели разъемов А соединительный кабель для проверки блока БКИ-6-3Ш
        #############################################################################################################
    
        msg_1 = 'Убедитесь в отсутствии других блоков или соединительных кабелей в панели разъемов А'
        msg_2 = 'Подключите в разъем, расположенный на панели разъемов А ' \
                'соединительный кабель для проверки блока БКИ-6-3Ш'
        if my_msg(msg_1):
            if my_msg(msg_2):
                pass
            else:
                exit()
        else:
            exit()
        ctrl_kl.ctrl_relay('KL22', True)
        sleep(3)
        in_a1, in_a4, in_a5, in_a6, in_a7 = self.__inputs_a()
        if in_a1 == False and in_a7 == True and in_a6 == True and in_a4 == False and in_a5 == True:
            pass
        else:
            fault.debug_msg('тест 1 положение выходов не соответствует', 1)
            mysql_conn.mysql_ins_result('неисправен', '1')
            if in_a1 == True or in_a7 == False:
                mysql_conn.mysql_error(123)
            elif in_a6 == False:
                mysql_conn.mysql_error(124)
            elif in_a4 == True and in_a5 == False:
                mysql_conn.mysql_error(125)
            return False
        fault.debug_msg('тест 1 положение выходов соответствует', 4)
        mysql_conn.mysql_ins_result('исправен', '1')
        # Тест 2. Проверка работы контактов блока при подаче питания на блок и отсутствии утечки
        ctrl_kl.ctrl_relay('KL21', True)
        k1 = 0
        in_a1, in_a7 = self.__inputs_a1_a7()
        while in_a1 == False and in_a7 == True and k1 <= 20:
            sleep(0.2)
            in_a1, in_a7 = self.__inputs_a1_a7()
            k1 += 1
        if in_a1 == True and in_a7 == False:
            pass
        else:
            mysql_conn.mysql_ins_result("неисправен", "2")
            fault.debug_msg('тест 2.0 положение выходов не соответствует', 1)
            return False
        k2 = 0
        in_a1, in_a7 = self.__inputs_a1_a7()
        while in_a1 == True and in_a7 == False and k2 <= 20:
            sleep(0.2)
            in_a1, in_a7 = self.__inputs_a1_a7()
            k1 += 1
        if in_a1 == False and in_a7 == True:
            pass
        else:
            mysql_conn.mysql_ins_result("неисправен", "2")
            fault.debug_msg('тест 2.0 положение выходов не соответствует', 1)
            return False
        fault.debug_msg('тест 2.0 положение выходов соответствует', 4)
        # 2.1. Проверка установившегося состояния контактов по истечению 20 сек
        in_a1, in_a4, in_a5, in_a6, in_a7 = self.__inputs_a()
        if in_a1 == False and in_a7 == True and in_a6 == True and in_a4 == False and in_a5 == True:
            pass
        else:
            fault.debug_msg('тест 2.1 положение выходов не соответствует', 1)
            mysql_conn.mysql_ins_result('неисправен', '2')
            if in_a1 == True or in_a7 == False:
                mysql_conn.mysql_error(126)
            elif in_a6 == False:
                mysql_conn.mysql_error(127)
            elif in_a4 == True and in_a5 == False:
                mysql_conn.mysql_error(128)
            return False
        fault.debug_msg('тест 2.1 положение выходов соответствует', 4)
        mysql_conn.mysql_ins_result('исправен', '2')
        # Тест 3. Проверка работы контактов реле К4 «Блокировка ВКЛ».
        ctrl_kl.ctrl_relay('KL36', True)
        sleep(1)
        in_a1, in_a4, in_a5, in_a6, in_a7 = self.__inputs_a()
        if in_a1 == False and in_a7 == True and in_a6 == True and in_a4 == False and in_a5 == True:
            pass
        else:
            fault.debug_msg('тест 3.1 положение выходов не соответствует', 1)
            mysql_conn.mysql_ins_result('неисправен', '3')
            if in_a1 == True or in_a7 == False:
                mysql_conn.mysql_error(129)
            elif in_a6 == False:
                mysql_conn.mysql_error(130)
            elif in_a4 == True and in_a5 == False:
                mysql_conn.mysql_error(131)
            return False
        fault.debug_msg('тест 3.1 положение выходов соответствует', 4)
        ctrl_kl.ctrl_relay('KL36', False)
        k3 = 0
        in_a1, in_a7 = self.__inputs_a1_a7()
        while in_a1 == False and in_a7 == True and k3 <= 40:
            sleep(0.2)
            in_a1, in_a7 = self.__inputs_a1_a7()
            k3 += 1
        if in_a1 == True and in_a7 == False:
            pass
        else:
            mysql_conn.mysql_ins_result("неисправен", "3")
            fault.debug_msg('тест 3.2 положение выходов не соответствует', 1)
            return False
        k4 = 0
        in_a1, in_a7 = self.__inputs_a1_a7()
        while in_a1 == True and in_a7 == False and k4 <= 40:
            sleep(0.2)
            in_a1, in_a7 = self.__inputs_a1_a7()
            k4 += 1
        if in_a1 == False and in_a7 == True:
            pass
        else:
            mysql_conn.mysql_ins_result("неисправен", "3")
            fault.debug_msg('тест 3.2 положение выходов не соответствует', 1)
            return False
        fault.debug_msg('тест 3.2 положение выходов соответствует', 4)
        in_a1, in_a4, in_a5, in_a6, in_a7 = self.__inputs_a()
        if in_a1 == False and in_a7 == True and in_a6 == True and in_a4 == False and in_a5 == True:
            pass
        else:
            fault.debug_msg('тест 3.3 положение выходов не соответствует', 1)
            mysql_conn.mysql_ins_result('неисправен', '3')
            if in_a1 == True or in_a7 == False:
                mysql_conn.mysql_error(132)
            elif in_a6 == False:
                mysql_conn.mysql_error(133)
            elif in_a4 == True and in_a5 == False:
                mysql_conn.mysql_error(134)
            return False
        fault.debug_msg('тест 3.3 положение выходов соответствует', 4)
        mysql_conn.mysql_ins_result('исправен', '3')
        # Тест 4. Проверка работы контактов реле К6 «Срабатывание БКИ»
        ctrl_kl.ctrl_relay('KL22', False)
        resist.resist_kohm(30)
        sleep(10)
        in_a1, in_a4, in_a5, in_a6, in_a7 = self.__inputs_a()
        if in_a1 == False and in_a7 == True and in_a6 == False and in_a4 == True and in_a5 == False:
            pass
        else:
            fault.debug_msg('тест 4.1 положение выходов не соответствует', 1)
            mysql_conn.mysql_ins_result('неисправен', '4')
            if in_a1 == True or in_a7 == False:
                mysql_conn.mysql_error(135)
            elif in_a6 == True:
                mysql_conn.mysql_error(136)
            elif in_a4 == False and in_a5 == True:
                mysql_conn.mysql_error(137)
            return False
        fault.debug_msg('тест 4.1 положение выходов соответствует', 4)
        # 4.2. Отключение 30 кОм
        resist.resist_kohm(590)
        sleep(2)
        in_a1, in_a4, in_a5, in_a6, in_a7 = self.__inputs_a()
        if in_a1 == False and in_a7 == True and in_a6 == False and in_a4 == False and in_a5 == True:
            pass
        else:
            fault.debug_msg('тест 4.2 положение выходов не соответствует', 1)
            mysql_conn.mysql_ins_result('неисправен', '4')
            if in_a1 == True or in_a7 == False:
                mysql_conn.mysql_error(138)
            elif in_a6 == True:
                mysql_conn.mysql_error(139)
            elif in_a4 == True and in_a5 == False:
                mysql_conn.mysql_error(140)
            return False
        fault.debug_msg('тест 4.2 положение выходов соответствует', 4)
        mysql_conn.mysql_ins_result('исправен', '4')
        # Тест 5. Проверка исправности контактов реле К5 «Срабатывание БКИ на сигнал
        ctrl_kl.ctrl_relay('KL22', True)
        sleep(2)
        in_a1, in_a4, in_a5, in_a6, in_a7 = self.__inputs_a()
        if in_a1 == False and in_a7 == True and in_a6 == True and in_a4 == False and in_a5 == True:
            pass
        else:
            fault.debug_msg('тест 5.1 положение выходов не соответствует', 1)
            mysql_conn.mysql_ins_result('неисправен', '5')
            if in_a1 == True or in_a7 == False:
                mysql_conn.mysql_error(141)
            elif in_a6 == False:
                mysql_conn.mysql_error(142)
            elif in_a4 == True and in_a5 == False:
                mysql_conn.mysql_error(143)
            return False
        fault.debug_msg('тест 5.1 положение выходов соответствует', 4)
        ctrl_kl.ctrl_relay('KL22', False)
        sleep(5)
        in_a1, in_a4, in_a5, in_a6, in_a7 = self.__inputs_a()
        if in_a1 == False and in_a7 == True and in_a6 == False and in_a4 == False and in_a5 == True:
            pass
        else:
            fault.debug_msg('тест 5.2 положение выходов не соответствует', 1)
            mysql_conn.mysql_ins_result('неисправен', '5')
            if in_a1 == True or in_a7 == False:
                mysql_conn.mysql_error(144)
            elif in_a6 == True:
                mysql_conn.mysql_error(145)
            elif in_a4 == True and in_a5 == False:
                mysql_conn.mysql_error(146)
            return False
        fault.debug_msg('тест 5.2 положение выходов соответствует', 4)
        mysql_conn.mysql_ins_result('исправен', '5')
        return True
    
    @staticmethod
    def __inputs_a():
        in_a1 = read_mb.read_discrete(1)
        in_a4 = read_mb.read_discrete(4)
        in_a5 = read_mb.read_discrete(5)
        in_a6 = read_mb.read_discrete(6)
        in_a7 = read_mb.read_discrete(7)
        return in_a1, in_a4, in_a5, in_a6, in_a7
    
    @staticmethod
    def __inputs_a1_a7():
        in_a1 = read_mb.read_discrete(1)
        in_a7 = read_mb.read_discrete(7)
        return in_a1, in_a7


if __name__ == '__main__':
    try:
        test_bki_6_3sh = TestBKI6()
        if test_bki_6_3sh.st_test_bki_6_3sh():
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
