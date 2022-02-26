#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Алгоритм проверки

Тип блока	Производитель
БКЗ-ЗМК	    Без Производителя
БКЗ-ЗМК	    ДонЭнергоЗавод
БКЗ-ЗМК	    ИТЭП
БКЗ-Д	    Без Производителя
БКЗ-Д	    ДонЭнергоЗавод
БКЗ-З	    Без Производителя
БКЗ-З	    ДонЭнергоЗавод
БКЗ-З	    ИТЭП
"""

from sys import exit
from time import sleep, time
from my_msgbox import *
from my_msgbox_2 import *
from gen_func_procedure import *
from gen_func_utils import *
from gen_mb_client import *
from gen_mysql_connect import *

__all__ = ["TestBKZ3MK"]

proc = Procedure()
reset = ResetRelay()
resist = Resistor()
ctrl_kl = CtrlKL()
read_mb = ReadMB()
mysql_conn = MySQLConnect()
fault = Bug(True)

# Таблица уставок №1 (К=1.2)
# № уставки	0.3	0.4	0.5	0.6	0.7	0.8	0.9	1.0	1.1
# i	       1   2   3   4   5    6  7    8    9
# U2[i], В 4.7 6.2 7.7 9.2 10.6 12 13.4 14.7 16.6
#
# Таблица уставок №2 (К=1)
# № уставки	1	2	3	4	5	6	7	8	9	10	11
# i	1	2	3	4	5	6	7	8	9	10	11
# U2[i], В	21.8	27.2	32.7	38.1	43.6	49.0	54.4	59.9	65.3	70.8	76.2

# Тест 5. Проверка срабатывания защиты ТЗП блока по уставкам
# медленные
list_ust_tzp_num = (0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 1.1)
list_ust_tzp = (4.7, 6.2, 7.7, 9.2, 10.6, 12.0, 13.4, 14.7, 16.6)
list_delta_t_tzp = []
list_delta_percent_tzp = []
list_result_tzp = []
# Тест 4. Проверка срабатывания защиты МТЗ блока по уставкам
# быстрые
list_ust_mtz_num = (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11)
list_ust_mtz = (21.8, 27.2, 32.7, 38.1, 43.6, 49.0, 54.4, 59.9, 65.3, 70.8, 76.2)
list_delta_t_mtz = []
list_delta_percent_mtz = []
list_result_mtz = []

list_result_mtz_num = ('6', '7', '8', '9', '10', '11', '12', '13', '14', '15', '16')
list_result_tzp_num = ('17', '18', '19', '20', '21', '22', '23', '24', '25')


class TestBKZ3MK(object):
    def __init__(self):
        pass
    
    def st_test_bkz_3mk(self):
        # reset.reset_all()
        # Сообщение: «Убедитесь в отсутствии других блоков в панелях разъемов и вставьте блок
        #            в соответствующий разъем панели С» «Подключите к клемме «С», расположенной
        #            на корпусе блока, провод с литерой «С» «Переключите регулятор МТЗ на корпусе
        #            блока в положение «1», регулятор ТЗП в положение «1.1» «Переключите тумблера, \
        #            расположенные на корпусе блока в положение «Работа» и «660В»
        msg_1 = "Убедитесь в отсутствии других блоков в панелях разъемов и вставьте " \
                "блок в соответствующий разъем панели С»"
        msg_2 = "«Переключите регулятор МТЗ на корпусе блока в положение «1», регулятор ТЗП в положение " \
                "«1.1» «Переключите тумблеры в положение «Работа» и «660В»"
        if my_msg(msg_1):
            if my_msg(msg_2):
                pass
            else:
                return False
        else:
            return False
        # Тест 1. Проверка исходного состояния блока:
        mysql_conn.mysql_ins_result('идет тест 1', '1')
        fault.debug_msg("Тест 1. Проверка исходного состояния блока", 4)
        ctrl_kl.ctrl_relay('KL21', True)
        sleep(2)
        reset.sbros_zashit_kl30_1s5()
        sleep(1)
        in_a5, in_a6 = self.__inputs_a()
        if in_a5 == True and in_a6 == True:
            fault.debug_msg("состояние выходов соответствует", 3)
            pass
        else:
            mysql_conn.mysql_ins_result('неисправен', '1')
            if in_a5 == False:
                fault.debug_msg("вход 5 не соответствует", 1)
                mysql_conn.mysql_error(317)
            elif in_a6 == False:
                fault.debug_msg("вход 6 не соответствует", 1)
                mysql_conn.mysql_error(318)
            return False
        meas_volt_ust = proc.procedure_1_21_31()
        if meas_volt_ust != False:
            pass
        else:
            mysql_conn.mysql_ins_result('неисправен', '1')
            return False
        # 1.1.2. Проверка отсутствия короткого замыкания на входе измерительной части блока:
        # Включение вторичного главного контакта	KL63 – ВКЛ
        mysql_conn.mysql_ins_result('идет тест 1.1.2', '1')
        ctrl_kl.ctrl_relay('KL63', True)
        meas_volt = read_mb.read_analog()
        if 0.8 * meas_volt_ust <= meas_volt <= 1.1 * meas_volt_ust:
            pass
        else:
            fault.debug_msg("напряжение не соответствует", 1)
            mysql_conn.mysql_ins_result('неисправен', '1')
            mysql_conn.mysql_error(32)
            reset.sbros_kl63_proc_1_21_31()
            return False
        fault.debug_msg("напряжение соответствует", 3)
        # 1.1.3. Финишные операции отсутствия короткого замыкания на входе измерительной части блока::
        reset.sbros_kl63_proc_1_21_31()
        # 1.2. Определение коэффициента Кс отклонения фактического напряжения от номинального
        mysql_conn.mysql_ins_result('идет тест 1.2', '1')
        coef_volt = proc.procedure_1_22_32()
        if coef_volt != False:
            pass
        else:
            mysql_conn.mysql_ins_result('неисправен', '1')
            return False
        # 1.2.1. Определение поправочного коэффициента сети Кс:
        mysql_conn.mysql_ins_result('идет тест 1.2.1', '1')
        fault.debug_msg(f'коэффициент сети\t {coef_volt}', 2)
        reset.stop_procedure_32()
        mysql_conn.mysql_ins_result('исправен', '1')
        fault.debug_msg("тест 1 пройден", 3)
    
        ####################################################################################################################
        # Тест 2. Проверка работы блока при нормальном сопротивлении изоляции контролируемого присоединения
        mysql_conn.mysql_ins_result('идет тест 2', '2')
        resist.resist_kohm(200)
        sleep(1)
        in_a5, in_a6 = self.__inputs_a()
        if in_a5 == True and in_a6 == True:
            pass
        else:
            mysql_conn.mysql_ins_result('неисправен', '2')
            if in_a5 == False:
                fault.debug_msg("вход 5 не соответствует", 1)
                mysql_conn.mysql_error(319)
            elif in_a6 == False:
                fault.debug_msg("вход 6 не соответствует", 1)
                mysql_conn.mysql_error(320)
            return False
        fault.debug_msg("состояние выходов соответствует", 3)
        mysql_conn.mysql_ins_result('исправен', '2')
        fault.debug_msg("тест 2 пройден", 3)
    
        ####################################################################################################################
        # Тест 3. Проверка работы блока при снижении уровня сопротивлении изоляции ниже аварийной уставки
        mysql_conn.mysql_ins_result('идет тест 3', '3')
        ctrl_kl.ctrl_relay('KL22', True)
        in_a5, in_a6 = self.__inputs_a()
        if in_a5 == True and in_a6 == False:
            pass
        else:
            mysql_conn.mysql_ins_result('неисправен', '3')
            if in_a5 == False:
                fault.debug_msg("вход 5 не соответствует", 1)
                mysql_conn.mysql_error(321)
            elif in_a6 == True:
                fault.debug_msg("вход 6 не соответствует", 1)
                mysql_conn.mysql_error(322)
            return False
        fault.debug_msg("состояние выходов блока соответствует", 3)
        mysql_conn.mysql_ins_result('исправен', '3')
        resist.resist_kohm(590)
        ctrl_kl.ctrl_relay('KL22', False)
        sleep(2)
        reset.sbros_zashit_kl30_1s5()
        in_a5, in_a6 = self.__inputs_a()
        fault.debug_msg(f'положение входов \t {in_a5=} {in_a6=}', 5)
        if in_a5 == True and in_a6 == True:
            pass
        else:
            return False
        fault.debug_msg("тест 3 пройден", 3)
    
        ####################################################################################################################
        # Тест 4. Проверка срабатывания защиты МТЗ блока по уставкам
    
        # Сообщение	Установите регулятор МТЗ (1-11), расположенный на корпусе блока, в положение [i]
    
        mysql_conn.mysql_ins_result('идет тест 4', '4')
        msg_3 = "Установите регулятор МТЗ (1-11), расположенный на корпусе блока, в положение"
        k = 0
        for i in list_ust_mtz:
            # k += 1
            msg_result_mtz = my_msg_2(f'{msg_3} {list_ust_mtz_num[k]}')
            if msg_result_mtz == 0:
                pass
            elif msg_result_mtz == 1:
                return False
            elif msg_result_mtz == 2:
                mysql_conn.mysql_add_message(f'уставка МТЗ {list_ust_mtz_num[k]} пропущена')
                list_delta_percent_mtz.append('пропущена')
                list_delta_t_mtz.append('пропущена')
                k += 1
                continue
            if proc.procedure_1_24_34(coef_volt=coef_volt, setpoint_volt=i):
                pass
            else:
                mysql_conn.mysql_ins_result('неисправен', '4')
                return False
            # 4.1.  Проверка срабатывания блока от сигнала нагрузки:
            # Δ% = 9,19125*U4
            meas_volt_test4 = read_mb.read_analog()
            fault.debug_msg(f'напряжение \t {meas_volt_test4}', 2)
            calc_delta_percent_mtz = meas_volt_test4 * 9.19125
            fault.debug_msg(f'дельта % \t {calc_delta_percent_mtz}', 2)
            list_delta_percent_mtz.append(round(calc_delta_percent_mtz, 0))
            mysql_conn.mysql_ins_result('идет тест 4.1', '4')
            calc_delta_t_mtz = ctrl_kl.ctrl_ai_code_v0(code=105)
            if calc_delta_t_mtz != 9999:
                pass
            else:
                mysql_conn.mysql_ins_result('неисправен', '4')
            fault.debug_msg(f'дельта t \t {calc_delta_t_mtz}', 2)
            list_delta_t_mtz.append(round(calc_delta_t_mtz, 0))
            mysql_conn.mysql_add_message(f'уставка МТЗ {list_ust_mtz_num[k]}  дельта t: {calc_delta_t_mtz}')
            in_a5, in_a6 = self.__inputs_a()
            fault.debug_msg(f'положение входов \t {in_a5=} {in_a6=}', 5)
            if in_a5 == False and in_a6 == True:
                reset.stop_procedure_3()
                if self.__subtest_45():
                    fault.debug_msg("подтест 4.5 пройден", 3)
                    k += 1
                    continue
                else:
                    fault.debug_msg("подтест 4.5 не пройден", 1)
                    mysql_conn.mysql_ins_result('неисправен', '4')
                    return False
            else:
                if self.__subtest_42(coef_volt, i, k):
                    fault.debug_msg("подтест 4.2 пройден", 3)
                    k += 1
                    continue
                else:
                    fault.debug_msg("подтест 4.2 не пройден", 1)
                    mysql_conn.mysql_ins_result('неисправен', '4')
                    return False
        mysql_conn.mysql_ins_result('исправен', '4')
        fault.debug_msg(list_result_mtz, 2)
        fault.debug_msg("тест 4 пройден", 3)
    
        ####################################################################################################################
        # Тест 5. Проверка срабатывания защиты ТЗП блока по уставкам
    
        #######################################################################################
        # Сообщение	Установите регулятор МТЗ (1-11), расположенный на блоке, в положение «11» #
        #######################################################################################
    
        msg_4 = "Установите регулятор МТЗ (1-11), расположенный на блоке, в положение «11»"
        if my_msg(msg_4):
            pass
        else:
            return False
        mysql_conn.mysql_ins_result('идет тест 5', '5')
        # Цикл i=1…9 Таблица уставок №1
        m = 0
        for n in list_ust_tzp:
            ########################################################################################
            # Сообщение	Установите регулятор ТЗП (0.3-1.1), расположенный на блоке в положение [i] #
            ########################################################################################
            msg_5 = "Установите регулятор ТЗП (0.3-1.1), расположенный на блоке в положение"
            msg_result_tzp = my_msg(f'{msg_5} {list_ust_tzp_num[m]}')
            if msg_result_tzp == 0:
                pass
            elif msg_result_tzp == 1:
                return False
            elif msg_result_tzp == 2:
                mysql_conn.mysql_add_message('уставка ТЗП ' + str(list_ust_tzp_num[m]) + ' пропущена')
                list_delta_percent_tzp.append('пропущена')
                list_delta_t_tzp.append('пропущена')
                m += 1
                continue
            if proc.procedure_1_24_34(coef_volt=coef_volt, setpoint_volt=n):
                pass
            else:
                mysql_conn.mysql_ins_result('неисправен', '5')
                return False
            # Δ%= 0.06075*(U4)2 + 8.887875*U4
            meas_volt_test5 = read_mb.read_analog()
            fault.debug_msg(f'напряжение \t {meas_volt_test5}', 2)
            calc_delta_percent_tzp = 0.06075 * meas_volt_test5 ** 2 + 8.887875 * meas_volt_test5
            list_delta_percent_tzp.append(round(calc_delta_percent_tzp, 0))
            fault.debug_msg(f'дельта % \t {calc_delta_percent_tzp}', 2)
            # 5.4.  Проверка срабатывания блока от сигнала нагрузки:
            mysql_conn.mysql_ins_result('идет тест 5.4', '5')
            calc_delta_t_tzp = self.__delta_t_tzp()
            fault.debug_msg(f'дельта t \t {calc_delta_t_tzp}', 2)
            list_delta_t_tzp.append(round(calc_delta_t_tzp, 0))
            mysql_conn.mysql_add_message(f'уставка ТЗП {list_ust_tzp_num[m]} дельта t: {calc_delta_t_tzp}')
            reset.sbros_kl63_proc_all()
            if calc_delta_t_tzp != 0:
                in_a5, in_a6 = self.__inputs_a()
                if calc_delta_t_tzp <= 360 and in_a5 == True and in_a6 == False:
                    if self.__subtest_56():
                        m += 1
                        continue
                    else:
                        mysql_conn.mysql_ins_result('неисправен', '5')
                        return False
                elif calc_delta_t_tzp > 360 and in_a5 == False:
                    mysql_conn.mysql_error(327)
                    if self.__subtest_55():
                        m += 1
                        continue
                    else:
                        mysql_conn.mysql_ins_result('неисправен', '5')
                        return False
                elif calc_delta_t_tzp > 360 and in_a6 == True:
                    mysql_conn.mysql_error(328)
                    if self.__subtest_55():
                        m += 1
                        continue
                    else:
                        mysql_conn.mysql_ins_result('неисправен', '5')
                        return False
                elif calc_delta_t_tzp < 360 and in_a5 == True and in_a6 == True:
                    mysql_conn.mysql_error(328)
                    if self.__subtest_55():
                        m += 1
                        continue
                    else:
                        mysql_conn.mysql_ins_result('неисправен', '5')
                        return False
            else:
                mysql_conn.mysql_ins_result('неисправен', '5')
                return False
        mysql_conn.mysql_ins_result('исправен', '5')
        return True
    
    def __subtest_42(self, coef_volt, i, k):
        mysql_conn.mysql_ins_result('идет тест 4.2', '4')
        # 3.2. Формирование нагрузочного сигнала 1,1*calc_volt[i]:
        # 3.2.1. Сброс защит после проверки
        reset.sbros_zashit_kl30_1s5()
        in_a5, in_a6 = self.__inputs_a()
        fault.debug_msg(f'положение входов \t {in_a5=} {in_a6=}', 5)
        if in_a5 == True and in_a6 == True:
            pass
        else:
            if in_a5 == False:
                mysql_conn.mysql_error(325)
            elif in_a5 == False:
                mysql_conn.mysql_error(326)
            return False
        if proc.start_procedure_1():
            calc_volt = proc.start_procedure_25(coef_volt, i)
            if calc_volt != False:
                if proc.start_procedure_35(calc_volt=calc_volt, setpoint_volt=i):
                    pass
                else:
                    return False
            else:
                return False
        else:
            return False
        meas_volt_test4 = read_mb.read_analog()
        calc_delta_percent_mtz = meas_volt_test4 * 9.19125
        fault.debug_msg(calc_delta_percent_mtz, 2)
        list_delta_percent_mtz[-1] = round(calc_delta_percent_mtz, 0)
        # 3.2.2.  Проверка срабатывания блока от сигнала нагрузки:
        mysql_conn.mysql_ins_result('идет тест 4.2.2', '4')
        calc_delta_t_mtz = ctrl_kl.ctrl_ai_code_v0(code=105)
        if calc_delta_t_mtz != 9999:
            pass
        else:
            mysql_conn.mysql_ins_result('неисправен', '4')
        fault.debug_msg(f'дельта t \t {calc_delta_t_mtz}', 2)
        list_delta_t_mtz[-1] = round(calc_delta_t_mtz, 0)
        mysql_conn.mysql_add_message(f'уставка МТЗ {list_ust_mtz_num[k]} дельта t: {calc_delta_t_mtz}')
        in_a5, in_a6 = self.__inputs_a()
        fault.debug_msg(f'положение входов \t {in_a5=} {in_a6=}', 5)
        if in_a5 == False and in_a6 == True:
            reset.stop_procedure_3()
            if self.__subtest_45():
                return True
            else:
                return False
        elif in_a5 == True:
            mysql_conn.mysql_error(323)
            if self.__subtest_43():
                return True
            else:
                return False
        elif in_a6 == False:
            mysql_conn.mysql_error(324)
            if self.__subtest_43():
                return True
            else:
                return False
    
    def __subtest_43(self):
        mysql_conn.mysql_ins_result('идет тест 4.3', '4')
        reset.sbros_zashit_kl30_1s5()
        in_a5, in_a6 = self.__inputs_a()
        fault.debug_msg(f'положение входов \t {in_a5=} {in_a6=}', 5)
        if in_a5 == True and in_a6 == True:
            pass
        else:
            if in_a5 == False:
                mysql_conn.mysql_error(325)
            elif in_a6 == False:
                mysql_conn.mysql_error(326)
            return False
        return True
    
    def __subtest_45(self):
        mysql_conn.mysql_ins_result('идет тест 4.5', '4')
        # 4.5. Расчет времени и кратности срабатывания
        reset.sbros_zashit_kl30_1s5()
        in_a5, in_a6 = self.__inputs_a()
        fault.debug_msg(f'положение входов \t {in_a5=} {in_a6=}', 5)
        if in_a5 == True and in_a6 == True:
            fault.debug_msg("положение входов соответствует", 4)
            return True
        elif in_a5 == False:
            mysql_conn.mysql_error(325)
            return False
        elif in_a6 == False:
            mysql_conn.mysql_error(326)
            return False
    
    def __subtest_55(self):
        mysql_conn.mysql_ins_result('идет тест 5.5', '5')
        fault.debug_msg('идет тест 5.5', 3)
        reset.sbros_zashit_kl30_1s5()
        in_a5, in_a6 = self.__inputs_a()
        fault.debug_msg(f'положение входов \t {in_a5=} {in_a6=}', 5)
        if in_a5 == True and in_a6 == True:
            return True
        elif in_a5 == False:
            mysql_conn.mysql_error(329)
            return False
        elif in_a6 == False:
            mysql_conn.mysql_error(330)
            return False
    
    def __subtest_56(self):
        mysql_conn.mysql_ins_result('идет тест 5.6', '5')
        fault.debug_msg('идет тест 5.6', 3)
        reset.sbros_zashit_kl30_1s5()
        in_a5, in_a6 = self.__inputs_a()
        fault.debug_msg(f'положение входов \t {in_a5=} {in_a6=}', 5)
        if in_a5 == True and in_a6 == True:
            return True
        elif in_a5 == False:
            mysql_conn.mysql_error(329)
            return False
        elif in_a6 == False:
            mysql_conn.mysql_error(330)
            return False
    
    @staticmethod
    def __inputs_a():
        in_a5 = read_mb.read_discrete(5)
        in_a6 = read_mb.read_discrete(6)
        return in_a5, in_a6
    
    @staticmethod
    def __inputs_b():
        in_b0 = read_mb.read_discrete(8)
        in_b1 = read_mb.read_discrete(9)
        return in_b0, in_b1
    
    def __inputs_b1(self):
        in_b1 = read_mb.read_discrete(9)
        return in_b1
    
    @staticmethod
    def __inputs_a6():
        in_a6 = read_mb.read_discrete(6)
        return in_a6
    
    def __delta_t_tzp(self):
        ctrl_kl.ctrl_relay('KL63', True)
        in_b1 = self.__inputs_b1()
        i = 0
        while in_b1 == False and i <= 20:
            in_b1 = self.__inputs_b1()
            i += 1
        if in_b1 == True:
            start_timer = time()
            meas_time = 0
            in_a6 = self.__inputs_a6()
            while in_a6 == True and meas_time <= 370:
                in_a6 = self.__inputs_a6()
                meas_time = time() - start_timer
                #mt = round(meas_time, 2)
                #print("\r {}".format(mt), end="")
            if in_a6 == False:
                stop_timer = time()
                delta_t_calc = stop_timer - start_timer
                return delta_t_calc
            else:
                return 0
        else:
            return 0


if __name__ == '__main__':
    try:
        test_bkz_3mk = TestBKZ3MK()
        if test_bkz_3mk.st_test_bkz_3mk():
            for g1 in range(len(list_delta_percent_mtz)):
                list_result_mtz.append((list_ust_mtz_num[g1], list_delta_percent_mtz[g1], list_delta_t_mtz[g1]))
            mysql_conn.mysql_pmz_result(list_result_mtz)
            for g2 in range(len(list_delta_percent_tzp)):
                list_result_tzp.append((list_ust_tzp_num[g2], list_delta_percent_tzp[g2], list_delta_t_tzp[g2]))
            mysql_conn.mysql_tzp_result(list_result_tzp)
            mysql_conn.mysql_block_good()
            my_msg('Блок исправен')
        else:
            for g1 in range(len(list_delta_percent_mtz)):
                list_result_mtz.append((list_ust_mtz_num[g1], list_delta_percent_mtz[g1], list_delta_t_mtz[g1]))
            mysql_conn.mysql_pmz_result(list_result_mtz)
            for g2 in range(len(list_delta_percent_tzp)):
                list_result_tzp.append((list_ust_tzp_num[g2], list_delta_percent_tzp[g2], list_delta_t_tzp[g2]))
            mysql_conn.mysql_tzp_result(list_result_tzp)
            mysql_conn.mysql_block_bad()
            my_msg('Блок неисправен')
    except OSError:
        my_msg("ошибка системы")
    except SystemError:
        my_msg("внутренняя ошибка")
    finally:
        reset.reset_all()
        exit()
