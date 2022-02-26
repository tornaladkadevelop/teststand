#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Алгоритм проверки

Тип блока	Производитель	    Уникальный номер
БМЗ-2	    Нет производителя	        77
БМЗ-2	    ТЭТЗ-Инвест	                78
БМЗ-2	    Строй-энергомаш	            79

"""

from sys import exit
from time import sleep
from my_msgbox import *
from my_msgbox_2 import *
from gen_func_procedure import *
from gen_func_utils import *
from gen_mb_client import *
from gen_mysql_connect import *

__all__ = ['TestBMZ2']

reset = ResetRelay()
proc = Procedure()
ctrl_kl = CtrlKL()
read_mb = ReadMB()
mysql_conn = MySQLConnect()
fault = Bug(True)

# Таблица уставок №1
#
# № уставки	1	2	3	4	5	6	7	8	9	10	11
# i	1	2	3	4	5	6	7	8	9	10	11
# U2[i], В	32.2	40.2	48.2	56.3	64.3	72.3	80.4	88.4	96.5	104.5	112.5
list_ust_num = (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11)
# ust = (32.2, 40.2, 48.2, 56.3, 64.3, 72.3, 80.4, 88.4, 96.5, 104.5, 112.5)
list_ust = (32.2, 40.2, 48.2, 56.3, 64.3, 72.3, 80.4, 88.4, 98.5, 106.5, 114.5)
list_delta_t = []
list_delta_percent = []
list_result = []


class TestBMZ2(object):
    def __init__(self):
        pass
    
    def st_test_bmz_2(self):
        # reset.reset_all()
        # Тест 1. Проверка исходного состояния блока:
    
        ###############################################################
        # Сообщение	«Переключите тумблер на корпусе блока в положение #
        # «Работа» и установите регулятор уставок в положение 1       #
        ###############################################################
    
        msg_1 = "Переключите тумблер на корпусе блока в положение " \
                "«Работа» и установите регулятор уставок в положение 1"
        if my_msg(msg_1):
            pass
        else:
            return False
        mysql_conn.mysql_ins_result('идет тест 1', '1')
        ctrl_kl.ctrl_relay('KL21', True)
        fault.debug_msg("KL21 включен", 4)
        reset.sbros_zashit_kl30()
        fault.debug_msg("тест 1 сброс защит", 4)
        in_a1, in_a2, in_a5 = self.__inputs_a()
        if in_a1 == False and in_a5 == True and in_a2 == False:
            fault.debug_msg("верное состояние выходов блока", 3)
            pass
        else:
            mysql_conn.mysql_ins_result('неисправен', '1')
            if in_a1 == True:
                fault.debug_msg("неверное состояние", 1)
                mysql_conn.mysql_error(331)
            elif in_a5 == False:
                fault.debug_msg("неверное состояние", 1)
                mysql_conn.mysql_error(332)
            elif in_a2 == True:
                fault.debug_msg("неверное состояние", 1)
                mysql_conn.mysql_error(333)
            return False
        # 1.1. Проверка вероятности наличия короткого замыкания на входе измерительной цепи блока
        mysql_conn.mysql_ins_result('идет тест 1.1', '1')
        meas_volt_ust = proc.procedure_1_21_31()
        fault.debug_msg(f'напряжение в процедуре 1 {meas_volt_ust}', 2)
        if meas_volt_ust != False:
            pass
        else:
            mysql_conn.mysql_ins_result('неисправен', '1')
        ctrl_kl.ctrl_relay('KL63', True)
        meas_volt = read_mb.read_analog()
        fault.debug_msg(f'напряжение после подключения KL63 {meas_volt}', 2)
        if 0.6 * meas_volt_ust <= meas_volt <= 1.1 * meas_volt_ust:
            pass
        else:
            fault.debug_msg("напряжение не соответствует", 1)
            mysql_conn.mysql_ins_result('неисправен', '1')
            mysql_conn.mysql_error(394)
            reset.sbros_kl63_proc_1_21_31()
            return False
        fault.debug_msg("напряжение соответствует", 4)
        reset.sbros_kl63_proc_1_21_31()
        # 1.2. Определение коэффициента Кс отклонения фактического напряжения от номинального
        mysql_conn.mysql_ins_result('идет тест 1.2', '1')
        coef_volt = proc.procedure_1_22_32()
        if coef_volt != False:
            pass
        else:
            mysql_conn.mysql_ins_result('неисправен', '1')
            return False
        mysql_conn.mysql_ins_result('исправен', '1')
        reset.stop_procedure_3()
        fault.debug_msg("тест 1 пройден", 2)
    
        ####################################################################################################################
        # Тест 2. Проверка работоспособности защиты блока в режиме «Проверка»
    
        ###########################################################################
        # Сообщение	«Переключите тумблер на корпусе блока в положение «Проверка». #
        ###########################################################################
        msg_2 = "Переключите тумблер на корпусе блока в положение «Проверка»."
        if my_msg(msg_2):
            pass
        else:
            return False
        mysql_conn.mysql_ins_result('идет тест 2', '2')
        fault.debug_msg("начало теста 2, сброс всех реле", 4)
        if proc.start_procedure_1():
            calc_volt = proc.start_procedure_23(coef_volt)
            if calc_volt != False:
                if proc.start_procedure_37(calc_volt):
                    pass
                else:
                    mysql_conn.mysql_ins_result('неисправен', '2')
                    return False
            else:
                mysql_conn.mysql_ins_result('неисправен', '2')
                return False
        else:
            mysql_conn.mysql_ins_result('неисправен', '2')
            return False
        ctrl_kl.ctrl_relay('KL63', True)
        sleep(2)
        ctrl_kl.ctrl_relay('KL63', False)
        sleep(1)
        in_a1, in_a2, in_a5 = self.__inputs_a()
        if in_a1 == True and in_a5 == False and in_a2 == True:
            fault.debug_msg("состояние выходов блока соответствуют", 3)
            pass
        else:
            mysql_conn.mysql_ins_result('неисправен', '2')
            if in_a1 == False:
                fault.debug_msg("состояние входа 1 не соответствует", 1)
                mysql_conn.mysql_error(335)
            elif in_a5 == True:
                fault.debug_msg("состояние входа 5 не соответствует", 1)
                mysql_conn.mysql_error(336)
            elif in_a2 == False:
                fault.debug_msg("состояние входа 2 не соответствует",1)
                mysql_conn.mysql_error(337)
            return False
        reset.stop_procedure_3()
        # 2.4.2. Сброс защит после проверки
        mysql_conn.mysql_ins_result('идет тест 2.4', '2')
        reset.sbros_zashit_kl30()
        in_a1, in_a2, in_a5 = self.__inputs_a()
        if in_a1 == False and in_a5 == True and in_a2 == False:
            fault.debug_msg("состояние выходов соответствует", 3)
            pass
        else:
            mysql_conn.mysql_ins_result('неисправен', '2')
            if in_a1 == True:
                fault.debug_msg("вход 1 не соответствует", 1)
                mysql_conn.mysql_error(338)
            elif in_a5 == False:
                fault.debug_msg("вход 5 не соответствует", 1)
                mysql_conn.mysql_error(339)
            elif in_a2 == True:
                fault.debug_msg("вход 2 не соответствует", 1)
                mysql_conn.mysql_error(340)
            return False
        mysql_conn.mysql_ins_result('исправен', '2')
        fault.debug_msg("тест 2 пройден", 2)
    
        ####################################################################################################################
        # Тест 3. Проверка срабатывания защиты блока по уставкам
    
        #########################################################################
        # Сообщение	«Переключите тумблер на корпусе блока в положение «Работа» #
        #########################################################################
        msg_3 = "Переключите тумблер на корпусе блока в положение «Работа»"
        if my_msg(msg_3):
            pass
        else:
            return False
        mysql_conn.mysql_ins_result('идет тест 3', '3')
        # Цикл i=1…11 (Таблица уставок 1)
    
        ###################################################################
        # Сообщение	Установите регулятор уставок на блоке в положение [i] #
        ###################################################################
        k = 0
        for i in list_ust:
            msg_4 = (f'Установите регулятор уставок на блоке в положение {list_ust_num[k]}')
            msg_result = my_msg_2(msg_4)
            if msg_result == 0:
                pass
            elif msg_result == 1:
                return False
            elif msg_result == 2:
                mysql_conn.mysql_add_message(f'уставка {list_ust_num[k]} пропущена')
                list_delta_percent.append('пропущена')
                list_delta_t.append('пропущена')
                k += 1
                continue
            mysql_conn.mysql_ins_result('идет тест 3.1', '3')
            if proc.procedure_1_24_34(coef_volt=coef_volt, setpoint_volt=i):
                pass
            else:
                mysql_conn.mysql_ins_result('неисправен', '3')
                return False
            calc_delta_t = ctrl_kl.ctrl_ai_code_v0(code=104)
            if calc_delta_t != 9999:
                pass
            else:
                mysql_conn.mysql_ins_result('неисправен', '3')
            fault.debug_msg(f'дельта t \t {calc_delta_t}', 2)
            list_delta_t.append(round(calc_delta_t, 0))
            # Δ%= 6,1085*U4
            meas_volt = read_mb.read_analog()
            calc_delta_percent = meas_volt * 6.1085
            fault.debug_msg(f'дельта % \t {calc_delta_percent}', 2)
            list_delta_percent.append(round(calc_delta_percent, 0))
            reset.stop_procedure_3()
            mysql_conn.mysql_add_message(f'уставка {list_ust_num[k]} дельта t: {calc_delta_t}')
            mysql_conn.mysql_add_message(f'уставка {list_ust_num[k]} дельта %: {calc_delta_percent}')
            in_a1, in_a2, in_a5 = self.__inputs_a()
            if in_a1 == True and in_a5 == False and in_a2 == True:
                fault.debug_msg("соответствие выходов блока, сбрасываем и переходим к тесту 3.5", 3)
                if self.__subtest_35():
                    k += 1
                    continue
                else:
                    mysql_conn.mysql_ins_result('неисправен', '3')
                    return False
            else:
                fault.debug_msg("не соответствие выходов блока, переходим к тесту 3.2", 2)
                mysql_conn.mysql_ins_result('неисправен', '3')
                mysql_conn.mysql_error(341)
                if self.__subtest_32(coef_volt, i, k):
                    if self.__subtest_35():
                        k += 1
                        continue
                    else:
                        mysql_conn.mysql_ins_result('неисправен', '3')
                        return False
                else:
                    if self.__subtest_35():
                        k += 1
                        continue
                    else:
                        mysql_conn.mysql_ins_result('неисправен', '3')
                        return False
        mysql_conn.mysql_ins_result('исправен', '3')
        return True
    
    def __subtest_32(self, coef_volt, i, k):
        # 3.2. Формирование нагрузочного сигнала 1,1*calc_volt[i]:
        # 3.2.1. Сброс защит после проверки
        mysql_conn.mysql_ins_result('идет тест 3.2', '3')
        fault.debug_msg("старт теста 3.2", 3)
        reset.sbros_zashit_kl30()
        in_a1, in_a2, in_a5 = self.__inputs_a()
        if in_a1 == False and in_a5 == True and in_a2 == False:
            fault.debug_msg("состояние выходов блока соответствуют", 3)
            pass
        else:
            mysql_conn.mysql_ins_result('неисправен', '3')
            if in_a1 == True:
                fault.debug_msg("состояние входа 1 не соответствуют", 1)
                mysql_conn.mysql_error(338)
            elif in_a5 == False:
                fault.debug_msg("состояние входа 5 не соответствует", 1)
                mysql_conn.mysql_error(339)
            elif in_a2 == True:
                fault.debug_msg("состояние входа 2 не соответствует", 1)
                mysql_conn.mysql_error(340)
            return False
        mysql_conn.mysql_ins_result('идет тест 3.3', '3')
        if proc.start_procedure_1():
            calc_volt = proc.start_procedure_25(coef_volt, i)
            if calc_volt != False:
                if proc.start_procedure_35(i, calc_volt):
                    pass
                else:
                    return False
            else:
                return False
        else:
            return False
        # Δ%= 6,1085*U4
        meas_volt = read_mb.read_analog()
        calc_delta_percent = meas_volt * 6.1085
        fault.debug_msg(f'дельта % \t {calc_delta_percent}', 2)
        list_delta_percent[-1] = round(calc_delta_percent, 0)
        mysql_conn.mysql_ins_result('идет тест 3.4', '3')
        calc_delta_t = ctrl_kl.ctrl_ai_code_v0(code=104)
        if calc_delta_t != 9999:
            pass
        else:
            mysql_conn.mysql_ins_result('неисправен', '3')
        fault.debug_msg(f'дельта t \t {calc_delta_t}', 2)
        list_delta_t[-1] = round(calc_delta_t, 0)
        mysql_conn.mysql_add_message(f'уставка {list_ust_num[k]} дельта t: {calc_delta_t}')
        mysql_conn.mysql_add_message(f'уставка {list_ust_num[k]} дельта %: {calc_delta_percent}')
        in_a1, in_a2, in_a5 = self.__inputs_a()
        if in_a1 == True and in_a5 == False and in_a2 == True:
            fault.debug_msg("выходы блока соответствуют", 3)
            reset.stop_procedure_3()
            fault.debug_msg("сброс реле и старт теста 3.5", 2)
            return True
        else:
            fault.debug_msg("выходы блока не соответствуют", 1)
            mysql_conn.mysql_ins_result('неисправен', '3')
            mysql_conn.mysql_error(341)
            return False
    
    def __subtest_35(self):
        # 3.5. Расчет относительной нагрузки сигнала
        mysql_conn.mysql_ins_result('идет тест 3.5', '3')
        fault.debug_msg("старт теста 3.5", 2)
        reset.sbros_zashit_kl30()
        in_a1, in_a2, in_a5 = self.__inputs_a()
        if in_a1 is False and in_a5 and in_a2 is False:
            fault.debug_msg("состояние выходов блока соответствует", 3)
            fault.debug_msg("тест 3.5 завершен", 2)
            return True
        else:
            mysql_conn.mysql_ins_result('неисправен', '3')
            if in_a1 == True:
                fault.debug_msg("вход 1 не соответствует", 1)
                mysql_conn.mysql_error(338)
            elif in_a5 == False:
                fault.debug_msg("вход 5 не соответствует", 1)
                mysql_conn.mysql_error(339)
            elif in_a2 == True:
                fault.debug_msg("вход 2 не соответствует", 1)
                mysql_conn.mysql_error(340)
            return False
    
    @staticmethod
    def __inputs_a():
        in_a1 = read_mb.read_discrete(1)
        in_a2 = read_mb.read_discrete(2)
        in_a5 = read_mb.read_discrete(5)
        return in_a1, in_a2, in_a5
    
    @staticmethod
    def __inputs_b():
        in_b0 = read_mb.read_discrete(8)
        in_b1 = read_mb.read_discrete(9)
        return in_b0, in_b1


if __name__ == '__main__':
    try:
        test_bmz_2 = TestBMZ2()
        if test_bmz_2.st_test_bmz_2():
            for g1 in range(len(list_delta_percent)):
                list_result.append((list_ust_num[g1], list_delta_percent[g1], list_delta_t[g1]))
            mysql_conn.mysql_pmz_result(list_result)
            mysql_conn.mysql_block_good()
            my_msg('Блок исправен')
        else:
            for g1 in range(len(list_delta_percent)):
                list_result.append((list_ust_num[g1], list_delta_percent[g1], list_delta_t[g1]))
            mysql_conn.mysql_pmz_result(list_result)
            mysql_conn.mysql_block_bad()
            my_msg('Блок неисправен')
    except OSError:
        my_msg("ошибка системы")
    except SystemError:
        my_msg("внутренняя ошибка")
    finally:
        reset.reset_all()
        exit()
