#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Алгоритм проверки

Тип блока	Производитель
БТЗ-Т	    Нет производителя
БТЗ-Т	    ТЭТЗ-Инвест
БТЗ-Т	    Строй-энергомаш
БТЗ-Т	    Углеприбор
"""

from sys import exit
from time import time, sleep
from gen_func_procedure import *
from gen_func_utils import *
from my_msgbox import *
from my_msgbox_2 import *
from gen_mb_client import *
from gen_mysql_connect import *

__all__ = ["TestBTZT"]

# Таблица уставок №1
# № уставки	0.5	0.6	0.7	0.8	0.9	1.0
# i	1	2	3	4	5	6
# U2[i], В	23.7	28.6	35.56	37.4	42.6	47.3
#
# Таблица уставок №2
# № уставки	1	2	3	4	5	6	7	8	9	10	11
# i	1	2	3	4	5	6	7	8	9	10	11
# U2[i], В	67.9	86.4	100.1	117.2	140.7	146.4	156.6	164.2	175.7	183.7	192.1

reset = ResetRelay()
proc = Procedure()
read_mb = ReadMB()
ctrl_kl = CtrlKL()
mysql_conn = MySQLConnect()
fault = Bug(True)
# None - отключен, True - включен

# ust_1 = (23.7, 28.6, 35.56, 37.4, 42.6, 47.3)
list_ust_tzp = (25.7, 30.6, 37.56, 39.4, 44.6, 49.3)
list_ust_pmz = (67.9, 86.4, 100.1, 117.2, 140.7, 146.4, 156.6, 164.2, 175.7, 183.7, 192.1)
list_delta_t_pmz = []
list_delta_t_tzp = []
list_delta_percent_pmz = []
list_delta_percent_tzp = []
list_ust_tzp_num = (0.5, 0.6, 0.7, 0.8, 0.9, 1.0)
list_ust_pmz_num = (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11)
list_result_pmz = []
list_result_tzp = []


class TestBTZT(object):
    def __init__(self):
        pass
    
    def st_test_btz_t(self):
        # reset.reset_all()
        # Тест 1. Проверка исходного состояния блока:
    
        ###############################################################################
        # Сообщение	«Переключите оба тумблера на корпусе блока в положение «Работа»   #
        # и установите регуляторы уставок в положение 1 (1-11) и положение 1 (0.5-1)  #
        ###############################################################################
    
        msg_1 = "Переключите оба тумблера на корпусе блока в положение «Работа» и установите " \
                "регуляторы уставок в положение 1 (1-11) и положение 1.0 (0.5-1.0)"
        if my_msg(msg_1):
            pass
        else:
            return False
        fault.debug_msg("тест 1", 3)
        mysql_conn.mysql_ins_result('идет тест 1', '1')
        ctrl_kl.ctrl_relay('KL21', True)
        reset.sbros_zashit_kl30()
        in_a1, in_a2, in_a5, in_a6 = self.__inputs_a()
        if in_a1 == False and in_a5 == True and in_a2 == False and in_a6 == True:
            fault.debug_msg("положение выходов блока соответствует", 4)
            pass
        else:
            mysql_conn.mysql_ins_result('неисправен', '1')
            if in_a1 == True:
                fault.debug_msg("положение входа 1 не соответствует", 1)
                mysql_conn.mysql_error(390)
            elif in_a5 == False:
                fault.debug_msg("положение входа 5 не соответствует", 1)
                mysql_conn.mysql_error(391)
            elif in_a2 == True:
                fault.debug_msg("положение входа 2 не соответствует", 1)
                mysql_conn.mysql_error(392)
            elif in_a6 == False:
                fault.debug_msg("положение входа 6 не соответствует", 1)
                mysql_conn.mysql_error(393)
            return False
    
        # 1.1. Проверка вероятности наличия короткого замыкания
        # на входе измерительной цепи блока
        fault.debug_msg("тест 1.1", 3)
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
        fault.debug_msg("тест 1.2", 3)
        mysql_conn.mysql_ins_result('идет тест 1.2', '1')
        coef_volt = proc.procedure_1_22_32()
        if coef_volt != False:
            pass
        else:
            mysql_conn.mysql_ins_result('неисправен', '1')
            return False
        fault.debug_msg(f'коэффициент {coef_volt}', 2)
        mysql_conn.mysql_ins_result('исправен', '1')
        reset.stop_procedure_32()
        fault.debug_msg("тест 1 завершен", 3)
        # Тест 2. Проверка работоспособности защиты ПМЗ блока в режиме «Проверка»
    
        #########################################################################################
        # Сообщение	«Переключите тумблер ПМЗ (1-11)  на корпусе блока в положение «Проверка».   #
        #########################################################################################
    
        msg_2 = "Переключите тумблер ПМЗ (1-11) на корпусе блока в положение «Проверка»"
        if my_msg(msg_2):
            pass
        else:
            return False
        fault.debug_msg("тест 2", 3)
        mysql_conn.mysql_ins_result('идет тест 2.1', '2')
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
    
        # 2.2.  Проверка срабатывания блока от сигнала нагрузки:
        fault.debug_msg("тест 2.2", 3)
        mysql_conn.mysql_ins_result('идет тест 2.2', '2')
        ctrl_kl.ctrl_relay('KL63', True)
        sleep(2)
        ctrl_kl.ctrl_relay('KL63', False)
        in_a1, in_a2, in_a5, in_a6 = self.__inputs_a()
        if in_a1 == False and in_a5 == True and in_a2 == True and in_a6 == False:
            fault.debug_msg("положение выходов блока соответствует", 4)
            pass
        else:
            mysql_conn.mysql_ins_result('неисправен', '2')
            if in_a1 == True:
                fault.debug_msg("положение входа 1 не соответствует", 1)
                mysql_conn.mysql_error(395)
            elif in_a5 == False:
                fault.debug_msg("положение входа 5 не соответствует", 1)
                mysql_conn.mysql_error(396)
            elif in_a2 == False:
                fault.debug_msg("положение входа 2 не соответствует", 1)
                mysql_conn.mysql_error(397)
            elif in_a6 == True:
                fault.debug_msg("положение входа 6 не соответствует", 1)
                mysql_conn.mysql_error(398)
            return False
        reset.stop_procedure_3()
        # 2.4.2. Сброс защит после проверки
        fault.debug_msg("тест 2.4", 3)
        mysql_conn.mysql_ins_result('идет тест 2.4', '2')
        reset.sbros_zashit_kl30()
        in_a1, in_a2, in_a5, in_a6 = self.__inputs_a()
        if in_a1 == False and in_a5 == True and in_a2 == False and in_a6 == True:
            fault.debug_msg("положение выходов блока соответствует", 4)
            pass
        else:
            mysql_conn.mysql_ins_result('неисправен', '2')
            if in_a1 == True:
                fault.debug_msg("положение входа 1 не соответствует", 1)
                mysql_conn.mysql_error(399)
            elif in_a5 == False:
                fault.debug_msg("положение входа 5 не соответствует", 1)
                mysql_conn.mysql_error(400)
            elif in_a2 == True:
                fault.debug_msg("положение входа 2 не соответствует", 1)
                mysql_conn.mysql_error(401)
            elif in_a6 == False:
                fault.debug_msg("положение входа 6 не соответствует", 1)
                mysql_conn.mysql_error(402)
            return False
        mysql_conn.mysql_ins_result('исправен', '2')
        fault.debug_msg("тест 2 завершен", 3)
        msg_9 = "Переключите тумблер ПМЗ (1-11) в положение «Работа»"
        if my_msg(msg_9):
            pass
        else:
            return False
    
        # Тест 3. Проверка работоспособности защиты ТЗП блока в режиме «Проверка»
    
        ###################################################################
        # Сообщение	«Переключите тумблер ПМЗ (1-11) в положение «Работа». #
        # «Переключите тумблер ТЗП (0.5-1) в положение «Проверка».        #
        ###################################################################
        msg_3 = "«Переключите тумблер ТЗП (0.5-1.0) в положение «Проверка»"
        if my_msg(msg_3):
            pass
        else:
            return False
        fault.debug_msg("тест 3", 3)
        mysql_conn.mysql_ins_result('идет тест 3.1', '3')
        in_a1, in_a2, in_a5, in_a6 = self.__inputs_a()
        if in_a1 == True and in_a5 == False and in_a2 == False and in_a6 == True:
            fault.debug_msg("положение выходов блока соответствует", 4)
            pass
        else:
            mysql_conn.mysql_ins_result('неисправен', '3')
            if in_a1 == False:
                fault.debug_msg("положение входа 1 не соответствует", 1)
                mysql_conn.mysql_error(403)
            elif in_a5 == True:
                fault.debug_msg("положение входа 5 не соответствует", 1)
                mysql_conn.mysql_error(404)
            elif in_a2 == True:
                fault.debug_msg("положение входа 2 не соответствует", 1)
                mysql_conn.mysql_error(405)
            elif in_a6 == False:
                fault.debug_msg("положение входа 6 не соответствует", 1)
                mysql_conn.mysql_error(406)
            return False
    
        # 3.2. Сброс защит после проверки
    
        ###############################################
        # Сообщение	«Переключите тумблер ТЗП (0.5…1)  #
        # на корпусе блока в положение «Работа»       #
        ###############################################
    
        fault.debug_msg("тест 3.2", 3)
        mysql_conn.mysql_ins_result('идет тест 3.2', '3')
        msg_8 = "Переключите тумблер ТЗП (0.5…1.0) на корпусе блока в положение «Работа»"
        if my_msg(msg_8):
            pass
        else:
            return False
        reset.sbros_zashit_kl30()
        in_a1, in_a2, in_a5, in_a6 = self.__inputs_a()
        if in_a1 == False and in_a5 == True and in_a2 == False and in_a6 == True:
            fault.debug_msg("положение выходов блока соответствует", 4)
            pass
        else:
            mysql_conn.mysql_ins_result('неисправен', '3')
            if in_a1 == True:
                fault.debug_msg("положение входа 1 не соответствует", 1)
                mysql_conn.mysql_error(407)
            elif in_a5 == False:
                fault.debug_msg("положение входа 5 не соответствует", 1)
                mysql_conn.mysql_error(408)
            elif in_a2 == True:
                fault.debug_msg("положение входа 2 не соответствует", 1)
                mysql_conn.mysql_error(409)
            elif in_a6 == False:
                fault.debug_msg("положение входа 6 не соответствует", 1)
                mysql_conn.mysql_error(410)
            return False
        mysql_conn.mysql_ins_result('исправен', '3')
        fault.debug_msg("тест 3 завершен", 3)
    
        ###############################################################################
        # Тест 4. Проверка срабатывания защиты ПМЗ блока по уставкам
        ###############################################################################
        fault.debug_msg("тест 4", 3)
        mysql_conn.mysql_ins_result('идет тест 4', '4')
        # Цикл i=1…11 ( Таблица уставок 2)
        k = 0
        for i in list_ust_pmz:
            ###################################################################
            # Сообщение	Установите регулятор уставок на блоке в положение [i] #
            ###################################################################
            msg_5 = (f'Установите регулятор уставок ПМЗ (1-11) на блоке в положение {list_ust_pmz_num[k]}')
            msg_result = my_msg_2(msg_5)
            if msg_result == 0:
                pass
            elif msg_result == 1:
                return False
            elif msg_result == 2:
                mysql_conn.mysql_add_message(f'уставка {list_ust_pmz_num[k]} пропущена')
                list_delta_percent_pmz.append('пропущена')
                list_delta_t_pmz.append('пропущена')
                k += 1
                continue
            mysql_conn.mysql_ins_result('идет тест 4.1', '4')
            if proc.procedure_1_24_34(coef_volt=coef_volt, setpoint_volt=i):
                pass
            else:
                mysql_conn.mysql_ins_result('неисправен', '4')
                return False
            meas_volt_pmz = read_mb.read_analog()
            # Δ%= 2.7938*U4
            calc_delta_percent_pmz = 2.7938 * meas_volt_pmz
            list_delta_percent_pmz.append(round(calc_delta_percent_pmz, 0))
            # 4.1.  Проверка срабатывания блока от сигнала нагрузки:
            fault.debug_msg("тест 4.1", 3)
            mysql_conn.mysql_ins_result('идет тест 4.2', '4')
            calc_delta_t_pmz = ctrl_kl.ctrl_ai_code_v0(103)
            if calc_delta_t_pmz != 9999:
                pass
            else:
                mysql_conn.mysql_ins_result('неисправен', '4')
            fault.debug_msg(f'дельта t: {calc_delta_t_pmz}', 2)
            list_delta_t_pmz.append(round(calc_delta_t_pmz, 0))
            mysql_conn.mysql_add_message(f'уставка {list_ust_pmz_num[k]} дельта t: {calc_delta_t_pmz:.0f}')
            mysql_conn.mysql_add_message(f'уставка {list_ust_pmz_num[k]} дельта %: {calc_delta_percent_pmz:.0f}')
            in_a1, in_a2, in_a5, in_a6 = self.__inputs_a()
            if in_a1 == False and in_a5 == True and in_a2 == True and in_a6 == False:
                fault.debug_msg("положение выходов блока соответствует", 4)
                reset.stop_procedure_3()
                if self.__subtest_45():
                    k += 1
                    continue
                else:
                    mysql_conn.mysql_ins_result('неисправен', '4')
                    return False
            else:
                fault.debug_msg("положение выходов блока не соответствует", 1)
                mysql_conn.mysql_ins_result('неисправен', '4')
                mysql_conn.mysql_error(389)
                if self.__subtest_42(coef_volt, i, k):
                    if self.__subtest_45():
                        k += 1
                        continue
                    else:
                        mysql_conn.mysql_ins_result('неисправен', '4')
                else:
                    if self.__subtest_43():
                        k += 1
                        continue
                    else:
                        mysql_conn.mysql_ins_result('неисправен', '4')
        for t in range(len(list_delta_percent_pmz)):
            list_result_pmz.append((list_ust_pmz_num[t], list_delta_percent_pmz[t], list_delta_t_pmz[t]))
        mysql_conn.mysql_pmz_result(list_result_pmz)
        mysql_conn.mysql_ins_result('исправен', '4')
        fault.debug_msg("тест 4 завершен", 3)
    
        # Тест 5. Проверка срабатывания защиты ТЗП блока по уставкам
        ########################################################################
        # Сообщение	«Переключите тумблер на корпусе блока в положение «Работа» #
        ########################################################################
    
        fault.debug_msg("тест 5", 3)
        mysql_conn.mysql_ins_result('идет тест 5', '5')
        # Цикл i=1…6 (уставки 0.5-0.6-0.7-0.8-0.9-.) Таблица уставок №1
        m = 0
        for n in list_ust_tzp:
            ###################################################################
            # Сообщение	Установите регулятор уставок на блоке в положение [i] #
            ###################################################################
            msg_7 = (f'Установите регулятор уставок ТЗП (0.5…1.0) на блоке в положение\t{list_ust_tzp_num[m]}')
            msg_result = my_msg_2(msg_7)
            if msg_result == 0:
                pass
            elif msg_result == 1:
                return False
            elif msg_result == 2:
                mysql_conn.mysql_add_message(f'уставка {list_ust_tzp_num[m]} пропущена')
                list_delta_percent_tzp.append('пропущена')
                list_delta_t_tzp.append('пропущена')
                m += 1
                continue
            mysql_conn.mysql_ins_result('идет тест 5.1', '5')
            if proc.procedure_1_24_34(coef_volt=coef_volt, setpoint_volt=n):
                pass
            else:
                mysql_conn.mysql_ins_result('неисправен', '5')
                return False
            meas_volt_tzp = read_mb.read_analog()
            # Δ%= 0.0044*U42[i]+2.274* U4[i]
            calc_delta_percent_tzp = 0.0044 * meas_volt_tzp ** 2 + 2.274 * meas_volt_tzp
            list_delta_percent_tzp.append(round(calc_delta_percent_tzp, 0))
            # 5.4.  Проверка срабатывания блока от сигнала нагрузки:
            fault.debug_msg("тест 5.4", 3)
            mysql_conn.mysql_ins_result('идет тест 5.4', '5')
            ctrl_kl.ctrl_relay('KL63', True)
            in_b0, in_b1 = self.__inputs_b()
            while in_b1 == False:
                in_b0, in_b1 = self.__inputs_b()
            start_timer_2 = time()
            in_a5 = self.__read_in_a5()
            sub_timer = 0
            while in_a5 == True and sub_timer <= 360:
                sleep(0.2)
                sub_timer = time() - start_timer_2
                fault.debug_msg(f'времени прошло {sub_timer}', 2)
                fault.debug_msg(f'{in_a5=}', 3)
                in_a5 = self.__read_in_a5()
            stop_timer_2 = time()
            calc_delta_t_tzp = stop_timer_2 - start_timer_2
            fault.debug_msg(f'дельта t: {calc_delta_t_tzp}', 2)
            ctrl_kl.ctrl_relay('KL63', False)
            list_delta_t_tzp.append(round(calc_delta_t_tzp, 0))
            mysql_conn.mysql_add_message(f'уставка {list_ust_tzp_num[m]} дельта t: {calc_delta_t_tzp:.1f}')
            mysql_conn.mysql_add_message(f'уставка {list_ust_tzp_num[m]} дельта %: {calc_delta_percent_tzp:.1f}')
            in_a1, in_a2, in_a5, in_a6 = self.__inputs_a()
            if in_a1 == True and in_a5 == False and in_a2 == False and in_a6 == True and calc_delta_t_tzp <= 360:
                fault.debug_msg("входа соответствуют ", 4)
                if self.__subtest_56():
                    m += 1
                    continue
                else:
    
                    mysql_conn.mysql_ins_result('неисправен', '5')
                    return False
            else:
                fault.debug_msg("входа не соответствуют ", 1)
                mysql_conn.mysql_ins_result('неисправен', '5')
                mysql_conn.mysql_error(411)
                if self.__subtest_55():
                    m += 1
                    continue
                else:
                    mysql_conn.mysql_ins_result('неисправен', '5')
                    return False
        mysql_conn.mysql_ins_result('исправен', '5')
        for y in range(len(list_delta_percent_tzp)):
            list_result_tzp.append((list_ust_tzp_num[y], list_delta_percent_tzp[y], list_delta_t_tzp[y]))
        mysql_conn.mysql_tzp_result(list_result_tzp)
        return True
    
    def __subtest_42(self, coef_volt, i, k):
        """
        4.2. Формирование нагрузочного сигнала 1,1*calc_volt[i]:
        :return:
        """
        fault.debug_msg("тест 4.2", 3)
        mysql_conn.mysql_ins_result('идет тест 4.2', '4')
        reset.sbros_zashit_kl30()
        in_a1, in_a2, in_a5, in_a6 = self.__inputs_a()
        if in_a1 == False and in_a5 == True and in_a2 == False and in_a6 == True:
            pass
        else:
            mysql_conn.mysql_ins_result('неисправен', '4')
            if in_a1 == True:
                mysql_conn.mysql_error(399)
            elif in_a5 == False:
                mysql_conn.mysql_error(400)
            elif in_a2 == True:
                mysql_conn.mysql_error(401)
            elif in_a6 == False:
                mysql_conn.mysql_error(402)
            return False
        if proc.start_procedure_1():
            calc_volt = proc.start_procedure_25(coef_volt, i)
            if calc_volt != False:
                if proc.start_procedure_35(calc_volt, i):
                    pass
                else:
                    mysql_conn.mysql_ins_result('неисправен', '4')
            else:
                mysql_conn.mysql_ins_result('неисправен', '4')
        else:
            mysql_conn.mysql_ins_result('неисправен', '4')
        meas_volt_pmz = read_mb.read_analog()
        # Δ%= 2.7938*U4
        calc_delta_percent_pmz = 2.7938 * meas_volt_pmz
        list_delta_percent_pmz[-1] = round(calc_delta_percent_pmz, 0)
        # 4.2.2.  Проверка срабатывания блока от сигнала нагрузки:
        fault.debug_msg("тест 4.2.2", 3)
        mysql_conn.mysql_ins_result('идет тест 4.2.2', '4')
        calc_delta_t_pmz = ctrl_kl.ctrl_ai_code_v0(103)
        if calc_delta_t_pmz != 9999:
            pass
        else:
            mysql_conn.mysql_ins_result('неисправен', '4')
        fault.debug_msg(f'дельта t: {calc_delta_t_pmz}', 2)
        list_delta_t_pmz[-1] = round(calc_delta_t_pmz, 0)
        mysql_conn.mysql_add_message(f'уставка {list_ust_pmz_num[k]} дельта t: {calc_delta_t_pmz:.0f}')
        mysql_conn.mysql_add_message(f'уставка {list_ust_pmz_num[k]} дельта %: {calc_delta_percent_pmz:.0f}')
        in_a1, in_a2, in_a5, in_a6 = self.__inputs_a()
        if in_a1 == False and in_a5 == True and in_a2 == True and in_a6 == False:
            pass
        else:
            return False
        reset.stop_procedure_3()
        return True
    
    def __subtest_43(self):
        fault.debug_msg("тест 4.3", 3)
        mysql_conn.mysql_ins_result('идет тест 4.3', '4')
        reset.sbros_zashit_kl30()
        in_a1, in_a2, in_a5, in_a6 = self.__inputs_a()
        if in_a1 == False and in_a5 == True and in_a2 == False and in_a6 == True:
            pass
        else:
            mysql_conn.mysql_ins_result('неисправен', '4')
            if in_a1 == True:
                mysql_conn.mysql_error(399)
            elif in_a5 == False:
                mysql_conn.mysql_error(400)
            elif in_a2 == True:
                mysql_conn.mysql_error(401)
            elif in_a6 == False:
                mysql_conn.mysql_error(402)
            return False
        return True
    
    def __subtest_45(self):
        fault.debug_msg("тест 4.5", 3)
        mysql_conn.mysql_ins_result('идет тест 4.5', '4')
        reset.sbros_zashit_kl30()
        in_a1, in_a2, in_a5, in_a6 = self.__inputs_a()
        if in_a1 == False and in_a5 == True and in_a2 == False and in_a6 == True:
            pass
        else:
            mysql_conn.mysql_ins_result('неисправен', '4')
            if in_a1 == True:
                mysql_conn.mysql_error(399)
            elif in_a5 == False:
                mysql_conn.mysql_error(400)
            elif in_a2 == True:
                mysql_conn.mysql_error(401)
            elif in_a6 == False:
                mysql_conn.mysql_error(402)
            return False
        return True
    
    def __subtest_55(self):
        fault.debug_msg("тест 5.5", 3)
        mysql_conn.mysql_ins_result('идет тест 5.5', '5')
        reset.stop_procedure_3()
        reset.sbros_zashit_kl30()
        in_a1, in_a2, in_a5, in_a6 = self.__inputs_a()
        if in_a1 == False and in_a5 == True and in_a2 == False and in_a6 == True:
            pass
        else:
            mysql_conn.mysql_ins_result('неисправен', '5')
            if in_a1 == True:
                mysql_conn.mysql_error(399)
            elif in_a5 == False:
                mysql_conn.mysql_error(400)
            elif in_a2 == True:
                mysql_conn.mysql_error(401)
            elif in_a6 == False:
                mysql_conn.mysql_error(402)
            return False
        return True
    
    def __subtest_56(self):
        fault.debug_msg("тест 5.6", 3)
        mysql_conn.mysql_ins_result('идет тест 5.6', '5')
        reset.stop_procedure_3()
        # Определение кратности сигнала нагрузки: Δ%= 0.0044*U42[i]+2.274* U4[i]
        # 5.6.1. Сброс защит после проверки
        reset.sbros_zashit_kl30()
        in_a1, in_a2, in_a5, in_a6 = self.__inputs_a()
        if in_a1 == False and in_a5 == True and in_a2 == False and in_a6 == True:
            pass
        else:
            mysql_conn.mysql_ins_result('неисправен', '5')
            if in_a1 == True:
                mysql_conn.mysql_error(399)
            elif in_a5 == False:
                mysql_conn.mysql_error(400)
            elif in_a2 == True:
                mysql_conn.mysql_error(401)
            elif in_a6 == False:
                mysql_conn.mysql_error(402)
            return False
        return True
    
    @staticmethod
    def __inputs_a():
        in_a1 = read_mb.read_discrete(1)
        in_a2 = read_mb.read_discrete(2)
        in_a5 = read_mb.read_discrete(5)
        in_a6 = read_mb.read_discrete(6)
        return in_a1, in_a2, in_a5, in_a6
    
    @staticmethod
    def __read_in_a5():
        in_a5 = read_mb.read_discrete(5)
        return in_a5
    
    @staticmethod
    def __inputs_b():
        in_b0 = read_mb.read_discrete(8)
        in_b1 = read_mb.read_discrete(9)
        return in_b0, in_b1


if __name__ == '__main__':
    try:
        test_btz_t = TestBTZT()
        if test_btz_t.st_test_btz_t():
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
