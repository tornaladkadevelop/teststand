#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Алгоритм проверки

Тип блока	Производитель
БТЗ-3	    Нет производителя
БТЗ-3	    ТЭТЗ-Инвест
БТЗ-3	    Строй-энергомаш
БТЗ-3	    Углеприбор

"""

from sys import exit
from time import sleep, time
from gen_func_utils import *
from my_msgbox import *
from my_msgbox_2 import *
from gen_func_procedure import *
from gen_mb_client import *
from gen_mysql_connect import *

__all__ = ["TestBTZ3"]

reset = ResetRelay()
proc = Procedure()
ctrl_kl = CtrlKL()
read_mb = ReadMB()
mysql_conn = MySQLConnect()
fault = Bug(True)

# Таблица уставок №1 ТЗП
# № уставки	0.5	0.6	0.7	0.8	0.9	1.0
# i	1	2	3	4	5	6
# U2[i], В	23.7	28.6	35.56	37.4	42.6	47.3
#
# Таблица уставок №2 ПМЗ
# № уставки	1	2	3	4	5	6	7	8	9	10	11
# i	1	2	3	4	5	6	7	8	9	10	11
# U2[i], В	67.9	86.4	100.1	117.2	140.7	146.4	156.6	164.2	175.7	183.7	192.1


list_ust_tzp_num = (0.5, 0.6, 0.7, 0.8, 0.9, 1.0)
list_ust_tzp = (23.7, 28.6, 35.56, 37.4, 42.6, 47.3)
list_ust_pmz_num = (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11)
list_ust_pmz = (67.9, 86.4, 100.1, 117.2, 140.7, 146.4, 156.6, 164.2, 175.7, 183.7, 192.1)
ust_prov = 80.0
list_delta_t_tzp = []
list_delta_t_pmz = []
list_delta_percent_tzp = []
list_delta_percent_pmz = []
list_result_tzp = []
list_result_pmz = []


class TestBTZ3(object):
    def __init__(self):
        pass
    
    def st_test_btz_3(self):
        # reset.reset_all()
        # Тест 1. Проверка исходного состояния блока:
        ##############################################################################
        # Сообщение	«Переключите оба тумблера на корпусе блока в положение «Работа»  #
        # и установите регуляторы уставок в положение 1 (1-11) и положение 1 (0.5-1) #
        ##############################################################################
        msg_1 = "Переключите оба тумблера на корпусе блока в положение «Работа» и установите " \
                "регуляторы уставок в положение 1 (1-11) и положение 1 (0.5-1)"
        if my_msg(msg_1):
            pass
        else:
            return False
        mysql_conn.mysql_ins_result('идёт тест 1', '1')
        ctrl_kl.ctrl_relay('KL21', True)
        self.__sbros_zashit_kl30()
        in_a1, in_a2, in_a5, in_a6 = self.__inputs_a()
        if in_a1 == False and in_a5 == True and in_a2 == False and in_a6 == True:
            pass
        else:
            mysql_conn.mysql_ins_result('неисправен', '1')
            if in_a1 == True:
                mysql_conn.mysql_error(368)
            elif in_a5 == False:
                mysql_conn.mysql_error(369)
            elif in_a2 == True:
                mysql_conn.mysql_error(370)
            elif in_a6 == False:
                mysql_conn.mysql_error(371)
            return False
        # 1.1. Проверка вероятности наличия короткого замыкания на входе измерительной цепи блока
        mysql_conn.mysql_ins_result('идёт тест 1.1', '1')
        meas_volt_ust = proc.procedure_1_21_31()
        if meas_volt_ust != False:
            pass
        else:
            mysql_conn.mysql_error(433)
            mysql_conn.mysql_ins_result('неисправен', '1')
            return False
        ctrl_kl.ctrl_relay('KL63', True)
        min_volt = 0.6 * meas_volt_ust
        max_volt = 1.0 * meas_volt_ust
        meas_volt = read_mb.read_analog()
        fault.debug_msg(f'напряжение после включения KL63:\t{meas_volt:.12}'
                        f'\tдолжно быть от\t{min_volt}\tдо\t{max_volt}', 3)
        if min_volt <= meas_volt <= max_volt:
            pass
        else:
            mysql_conn.mysql_ins_result('неисправен', '1')
            mysql_conn.mysql_error(455)
            reset.sbros_kl63_proc_1_21_31()
            return False
        reset.sbros_kl63_proc_1_21_31()
        # 1.1.3. Финишные операции отсутствия короткого замыкания на входе измерительной части блока::
        # 1.2. Определение коэффициента Кс отклонения фактического напряжения от номинального
        mysql_conn.mysql_ins_result('идёт тест 1.2', '1')
        fault.debug_msg("1.2. Определение коэффициента Кс отклонения фактического напряжения от номинального", 3)
        coef_volt = proc.procedure_1_22_32()
        if coef_volt != False:
            pass
        else:
            mysql_conn.mysql_ins_result("неисправен TV1", "1")
            return False
        reset.stop_procedure_32()
        mysql_conn.mysql_ins_result('исправен', '1')
        # Тест 2. Проверка работоспособности защиты ПМЗ блока в режиме «Проверка»
        ######################################################################################
        # Сообщение	«Переключите тумблер ПМЗ (1-11) на корпусе блока в положение «Проверка». #
        ######################################################################################
    
        msg_2 = "Переключите тумблер ПМЗ (1-11) на корпусе блока в положение «Проверка»"
        if my_msg(msg_2):
            pass
        else:
            return False
        fault.debug_msg("тест 2.1", 3)
        mysql_conn.mysql_ins_result('идёт тест 2', '2')
        if proc.procedure_1_24_34(setpoint_volt=ust_prov, coef_volt=coef_volt):
            pass
        else:
            mysql_conn.mysql_ins_result("неисправен TV1", "2")
            return False
        # 2.2.  Проверка срабатывания блока от сигнала нагрузки:
        fault.debug_msg("тест 2.2", 3)
        mysql_conn.mysql_ins_result('идёт тест 2.2', '2')
        ctrl_kl.ctrl_relay('KL63', True)
        sleep(2)
        ctrl_kl.ctrl_relay('KL63', False)
        in_a1, in_a2, in_a5, in_a6 = self.__inputs_a()
        if in_a1 == False and in_a5 == True and in_a2 == True and in_a6 == False:
            pass
        else:
            fault.debug_msg("тест 2.2 положение выходов не соответствует", 1)
            mysql_conn.mysql_ins_result('неисправен', '2')
            if in_a1 == True:
                mysql_conn.mysql_error(373)
            elif in_a5 == False:
                mysql_conn.mysql_error(374)
            elif in_a2 == False:
                mysql_conn.mysql_error(375)
            elif in_a6 == True:
                mysql_conn.mysql_error(376)
            return False
        fault.debug_msg("тест 2.2 положение выходов соответствует", 4)
        reset.stop_procedure_3()
        fault.debug_msg("тест 2.3", 3)
        self.__sbros_zashit_kl30()
        in_a1, in_a2, in_a5, in_a6 = self.__inputs_a()
        if in_a1 == False and in_a5 == True and in_a2 == False and in_a6 == True:
            pass
        else:
            fault.debug_msg("тест 2.3 положение выходов не соответствует", 1)
            mysql_conn.mysql_ins_result('неисправен', '2')
            if in_a1 == True:
                mysql_conn.mysql_error(377)
            elif in_a5 == False:
                mysql_conn.mysql_error(378)
            elif in_a2 == True:
                mysql_conn.mysql_error(379)
            elif in_a6 == False:
                mysql_conn.mysql_error(380)
            return False
        fault.debug_msg("тест 2.3 положение выходов соответствует", 4)
        mysql_conn.mysql_ins_result('исправен', '2')
        # Тест 3. Проверка работоспособности защиты ТЗП блока в режиме «Проверка»
    
        #####################################################################
        # Сообщение	«Переключите тумблер ПМЗ (1-11) в положение «Работа».   #
        # «Переключите тумблер ТЗП (0.5-1) в положение «Проверка».          #
        #####################################################################
    
        msg_3 = "Переключите тумблер ПМЗ (1-11) в положение «Работа» " \
                "«Переключите тумблер ТЗП (0.5-1) в положение «Проверка»"
        if my_msg(msg_3):
            pass
        else:
            return False
        fault.debug_msg("тест 3.1", 3)
        in_a1, in_a2, in_a5, in_a6 = self.__inputs_a()
        if in_a1 == True and in_a5 == False and in_a2 == False and in_a6 == True:
            pass
        else:
            fault.debug_msg("тест 3.1 положение выходов не соответствует", 1)
            mysql_conn.mysql_ins_result('неисправен', '3')
            if in_a1 == False:
                mysql_conn.mysql_error(381)
            elif in_a5 == True:
                mysql_conn.mysql_error(382)
            elif in_a2 == True:
                mysql_conn.mysql_error(383)
            elif in_a6 == False:
                mysql_conn.mysql_error(384)
            return False
        fault.debug_msg("тест 3.1 положение выходов соответствует", 4)
        # 3.2. Сброс защит после проверки
        msg_4 = "Переключите тумблер ТЗП (0.5…1) на корпусе блока в положение \"Работа\""
        if my_msg(msg_4):
            pass
        else:
            return False
        fault.debug_msg("тест 3.2", 3)
        self.__sbros_zashit_kl30()
        in_a1, in_a2, in_a5, in_a6 = self.__inputs_a()
        if in_a1 == False and in_a5 == True and in_a2 == False and in_a6 == True:
            pass
        else:
            fault.debug_msg("тест 3.2 положение выходов не соответствует", 1)
            mysql_conn.mysql_ins_result('неисправен', '3')
            if in_a1 == True:
                mysql_conn.mysql_error(385)
            elif in_a5 == False:
                mysql_conn.mysql_error(386)
            elif in_a2 == True:
                mysql_conn.mysql_error(387)
            elif in_a6 == False:
                mysql_conn.mysql_error(388)
            return False
        fault.debug_msg("тест 3.2 положение выходов соответствует", 4)
        mysql_conn.mysql_ins_result('исправен', '3')
        # Тест 4. Проверка срабатывания защиты ПМЗ блока по уставкам
        ###############################################
        # Сообщение	«Переключите тумблер ТЗП (0.5…1)  #
        # на корпусе блока в положение «Работа»       #
        ###############################################
        msg_4_1 = "Установите регулятор уставок ТЗП на блоке в положение 1.0"
        if my_msg(msg_4_1):
            pass
        else:
            return False
        k = 0
        for i in list_ust_pmz:
            fault.debug_msg(f'тест 4 уставка {list_ust_pmz_num[k]}', 4)
            ###################################################################
            # Сообщение	Установите регулятор уставок на блоке в положение [i] #
            ###################################################################
            msg_5 = (f'Установите регулятор уставок ПМЗ на блоке в положение {list_ust_pmz_num[k]}')
            msg_result_pmz = my_msg_2(msg_5)
            if msg_result_pmz == 0:
                pass
            elif msg_result_pmz == 1:
                return False
            elif msg_result_pmz == 2:
                mysql_conn.mysql_add_message(f'уставка {list_ust_pmz_num[k]} пропущена')
                list_delta_percent_pmz.append('пропущена')
                list_delta_t_pmz.append('пропущена')
                k += 1
                continue
            mysql_conn.mysql_ins_result(f'уставка {list_ust_pmz_num[k]}', "4")
            if proc.procedure_1_24_34(setpoint_volt=i, coef_volt=coef_volt):
                pass
            else:
                mysql_conn.mysql_ins_result("неисправен TV1", "4")
                return False
            # 4.1.  Проверка срабатывания блока от сигнала нагрузки:
            meas_volt = read_mb.read_analog()
            # Δ%= 0.0062*U42+1.992* U4
            calc_delta_percent_pmz = 0.0062 * meas_volt ** 2 + 1.992 * meas_volt
            list_delta_percent_pmz.append(calc_delta_percent_pmz)
            calc_delta_t_pmz = ctrl_kl.ctrl_ai_code_v0(103)
            if calc_delta_t_pmz != 9999:
                pass
            else:
                mysql_conn.mysql_ins_result('неисправен', '4')
            fault.debug_msg(f'тест 4.1 дельта t:\t{calc_delta_t_pmz}\tуставка\t{list_ust_pmz_num[k]}', 2)
            list_delta_t_pmz.append(round(calc_delta_t_pmz, 0))
            mysql_conn.mysql_add_message(f'уставка {list_ust_pmz_num[k]} дельта t: {calc_delta_t_pmz:.1f}')
            mysql_conn.mysql_add_message(f'уставка {list_ust_pmz_num[k]} дельта %: {calc_delta_percent_pmz:.1f}')
            in_a1, in_a2, in_a5, in_a6 = self.__inputs_a()
            if in_a1 == False and in_a5 == True and in_a2 == True and in_a6 == False:
                fault.debug_msg("тест 4.1 положение выходов соответствует", 4)
                reset.stop_procedure_3()
                if self.__subtest_45():
                    k += 1
                    continue
                else:
                    return False
            else:
                fault.debug_msg("тест 4.1 положение выходов не соответствует", 1)
                mysql_conn.mysql_ins_result('неисправен', '4')
                mysql_conn.mysql_error(389)
                if self.__subtest_42(coef_volt, i, k):
                    k += 1
                    continue
                else:
                    return False
        mysql_conn.mysql_ins_result('исправен', '4')
        # Тест 5. Проверка срабатывания защиты ТЗП блока по уставкам
    
        ####################################################################
        # Сообщение	Установите регулятор уставок на блоке в положение [i]  #
        ####################################################################
    
        m = 0
        for n in list_ust_tzp:
            msg_7 = (f'Установите регулятор уставок на блоке в положение {list_ust_tzp_num[m]}')
            msg_result_tzp = my_msg_2(msg_7)
            if msg_result_tzp == 0:
                pass
            elif msg_result_tzp == 1:
                return False
            elif msg_result_tzp == 2:
                mysql_conn.mysql_add_message(f'уставка {list_ust_tzp_num[m]} пропущена')
                list_delta_percent_tzp.append('пропущена')
                list_delta_t_tzp.append('пропущена')
                m += 1
                continue
            mysql_conn.mysql_ins_result(f'уставка {list_ust_tzp_num[m]}', "5")
            if proc.procedure_1_24_34(setpoint_volt=n, coef_volt=coef_volt):
                pass
            else:
                mysql_conn.mysql_ins_result("неисправен TV1", "5")
                return False
            meas_volt = read_mb.read_analog()
            # Δ%= 0.003*U42[i]+2.404* U4[i]
            calc_delta_percent_tzp = 0.003 * meas_volt ** 2 + 2.404 * meas_volt
            list_delta_percent_tzp.append(calc_delta_percent_tzp)
            # 5.4.  Проверка срабатывания блока от сигнала нагрузки:
            ctrl_kl.ctrl_relay('KL63', True)
            in_b1 = self.__inputs_b1()
            i1 = 0
            while in_b1 == False and i1 <= 4:
                in_b0, in_b1 = self.__inputs_b()
                i1 += 1
            start_timer_tzp = time()
            calc_delta_t_tzp = 0
            in_a5 = self.__inputs_a5()
            while in_a5 == True and calc_delta_t_tzp <= 370:
                in_a5 = self.__inputs_a5()
                stop_timer_tzp = time()
                calc_delta_t_tzp = stop_timer_tzp - start_timer_tzp
            ctrl_kl.ctrl_relay('KL63', False)
            fault.debug_msg(f'тест 5 delta t:\t{calc_delta_t_tzp}\tуставка\t{list_ust_tzp_num[m]}', 2)
            list_delta_t_tzp.append(calc_delta_t_tzp)
            mysql_conn.mysql_add_message(f'уставка ТЗП {list_ust_tzp_num[m]} дельта t: {calc_delta_t_tzp:.0f}')
            mysql_conn.mysql_add_message(f'уставка ТЗП {list_ust_tzp_num[m]} дельта %: {calc_delta_percent_tzp:.0f}')
            in_a1, in_a2, in_a5, in_a6 = self.__inputs_a()
            if in_a1 == False and in_a5 == True and in_a2 == True and in_a6 == False and calc_delta_t_tzp <= 360:
                if self.__subtest_56():
                    m += 1
                    continue
                else:
                    return False
            else:
                if self.__subtest_55():
                    m += 1
                    continue
                else:
                    return False
        mysql_conn.mysql_ins_result('исправен', '5')
        return True
    
    def __subtest_55(self):
        reset.stop_procedure_3()
        self.__sbros_zashit_kl30()
        in_a1, in_a2, in_a5, in_a6 = self.__inputs_a()
        if in_a1 == False and in_a5 == True and in_a2 == False and in_a6 == True:
            pass
        else:
            mysql_conn.mysql_ins_result('неисправен', '5')
            if in_a1 == True:
                mysql_conn.mysql_error(377)
            elif in_a5 == False:
                mysql_conn.mysql_error(378)
            elif in_a2 == True:
                mysql_conn.mysql_error(379)
            elif in_a6 == False:
                mysql_conn.mysql_error(380)
            return False
        return True
    
    def __subtest_56(self):
        reset.stop_procedure_3()
        # 5.6.1. Сброс защит после проверки
        self.__sbros_zashit_kl30()
        in_a1, in_a2, in_a5, in_a6 = self.__inputs_a()
        if in_a1 == False and in_a5 == True and in_a2 == False and in_a6 == True:
            pass
        else:
            mysql_conn.mysql_ins_result('неисправен', '5')
            if in_a1 == True:
                mysql_conn.mysql_error(377)
            elif in_a5 == False:
                mysql_conn.mysql_error(378)
            elif in_a2 == True:
                mysql_conn.mysql_error(379)
            elif in_a6 == False:
                mysql_conn.mysql_error(380)
            return False
        return True
    
    def __subtest_42(self, coef_volt, i, k):
        # 4.2. Формирование нагрузочного сигнала 1,1*U3[i]:
        # 4.2.1. Сброс защит после проверки
        self.__sbros_zashit_kl30()
        in_a1, in_a2, in_a5, in_a6 = self.__inputs_a()
        if in_a1 == False and in_a5 == True and in_a2 == False and in_a6 == True:
            pass
        else:
            mysql_conn.mysql_ins_result('неисправен', '4')
            if in_a1 == True:
                mysql_conn.mysql_error(377)
            elif in_a5 == False:
                mysql_conn.mysql_error(378)
            elif in_a2 == True:
                mysql_conn.mysql_error(379)
            elif in_a6 == False:
                mysql_conn.mysql_error(380)
            return False
        if proc.procedure_1_25_35(setpoint_volt=i, coef_volt=coef_volt):
            pass
        else:
            mysql_conn.mysql_ins_result("неисправен TV1", "4")
            return False
        # 4.2.2.  Проверка срабатывания блока от сигнала нагрузки:
        meas_volt = read_mb.read_analog()
        # Δ%= 0.0062*U42+1.992* U4
        calc_delta_percent_pmz = 0.0062 * meas_volt ** 2 + 1.992 * meas_volt
        list_delta_percent_pmz[-1] = round(calc_delta_percent_pmz, 0)
        calc_delta_t_pmz = ctrl_kl.ctrl_ai_code_v0(103)
        if calc_delta_t_pmz != 9999:
            pass
        else:
            mysql_conn.mysql_ins_result('неисправен', '4')
        list_delta_t_pmz[-1] = round(calc_delta_t_pmz, 0)
        mysql_conn.mysql_add_message(f'уставка ПМЗ {list_ust_pmz_num[k]} дельта t: {calc_delta_t_pmz:.0f}')
        mysql_conn.mysql_add_message(f'уставка ПМЗ {list_ust_pmz_num[k]} дельта %: {calc_delta_percent_pmz:.0f}')
        in_a1, in_a2, in_a5, in_a6 = self.__inputs_a()
        if in_a1 == False and in_a5 == True and in_a2 == True and in_a6 == False:
            if self.__subtest_45():
                pass
            else:
                mysql_conn.mysql_ins_result('неисправен', '4')
        else:
            mysql_conn.mysql_error(389)
            reset.stop_procedure_3()
            # 4.3. Сброс защит после проверки
            self.__sbros_zashit_kl30()
            in_a1, in_a2, in_a5, in_a6 = self.__inputs_a()
            if in_a1 == False and in_a5 == True and in_a2 == False and in_a6 == True:
                pass
            else:
                mysql_conn.mysql_ins_result('неисправен', '4')
                if in_a1 == True:
                    mysql_conn.mysql_error(377)
                elif in_a5 == False:
                    mysql_conn.mysql_error(378)
                elif in_a2 == True:
                    mysql_conn.mysql_error(379)
                elif in_a6 == False:
                    mysql_conn.mysql_error(380)
                return False
        return True
    
    def __subtest_45(self):
        # 4.5. Расчет относительной нагрузки сигнала
    
        # 4.6. Сброс защит после проверки
        self.__sbros_zashit_kl30()
        in_a1, in_a2, in_a5, in_a6 = self.__inputs_a()
        if in_a1 == False and in_a5 == True and in_a2 == False and in_a6 == True:
            pass
        else:
            mysql_conn.mysql_ins_result('неисправен', '4')
            if in_a1 == True:
                mysql_conn.mysql_error(377)
            elif in_a5 == False:
                mysql_conn.mysql_error(378)
            elif in_a2 == True:
                mysql_conn.mysql_error(379)
            elif in_a6 == False:
                mysql_conn.mysql_error(380)
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
    def __inputs_a5():
        in_a5 = read_mb.read_discrete(5)
        return in_a5
    
    @staticmethod
    def __inputs_b():
        in_b0 = read_mb.read_discrete(8)
        in_b1 = read_mb.read_discrete(9)
        return in_b0, in_b1
    
    @staticmethod
    def __inputs_b1():
        in_b1 = read_mb.read_discrete(9)
        return in_b1
    
    @staticmethod
    def __sbros_zashit_kl30():
        ctrl_kl.ctrl_relay('KL30', True)
        sleep(1.5)
        ctrl_kl.ctrl_relay('KL30', False)
        sleep(3)


if __name__ == '__main__':
    try:
        test_btz_3 = TestBTZ3()
        if test_btz_3.st_test_btz_3():
            g1, g2 = 0, 0
            for g1 in range(len(list_delta_percent_pmz)):
                list_result_pmz.append((list_ust_pmz_num[g1], list_delta_percent_pmz[g1], list_delta_t_pmz[g1]))
            mysql_conn.mysql_pmz_result(list_result_pmz)
            for g2 in range(len(list_delta_percent_tzp)):
                list_result_tzp.append((list_ust_tzp_num[g2], list_delta_percent_tzp[g2], list_delta_t_tzp[g2]))
            mysql_conn.mysql_tzp_result(list_result_tzp)
            mysql_conn.mysql_block_good()
            my_msg('Блок исправен')
        else:
            g1, g2 = 0, 0
            for g1 in range(len(list_delta_percent_pmz)):
                list_result_pmz.append((list_ust_pmz_num[g1], list_delta_percent_pmz[g1], list_delta_t_pmz[g1]))
            mysql_conn.mysql_pmz_result(list_result_pmz)
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
