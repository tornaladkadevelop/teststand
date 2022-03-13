#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Алгоритм проверки

Тип блока           Производитель
МТЗ-5 вер.2-8/0.8-3	Завод Электромашина


"""

import sys

from time import sleep, time

from gen_func_utils import *
from my_msgbox import *
from my_msgbox_2 import *
from gen_func_procedure import *
from gen_mb_client import *
from gen_mysql_connect import *

__all__ = ["TestMTZ5V28"]

reset = ResetRelay()
proc = Procedure()
read_mb = ReadMB()
ctrl_kl = CtrlKL()
mysql_conn = MySQLConnect()
fault = Bug(True)

# Таблица уставок №1 (К=1,5) ТЗП
# № уставки	`0.8	`1	`2	`2.5	`3
# i	`1	`2	`3	`4	`5
# U2[i], В	`22.1	`27.6	`55.1	`68.9	`82.5
#
# Таблица уставок №2 (К=1) МТЗ
# № уставки	`2	`3	`4	`5	`6	`7	`8
# i	`1	`2	`3	`4	`5	`6	`7
# U2[i], В	`36.7	`55	`73.4	`91.7	`110	`128.4	`146.7

list_ust_tzp_num = (0.8, 1, 2, 2.5, 3)
list_ust_tzp = (22.1, 27.6, 55.1, 68.9, 82.5)
list_ust_mtz_num = (2, 3, 4, 5, 6, 7, 8)
list_ust_mtz = (36.7, 55.0, 73.4, 91.7, 110.0, 128.4, 146.7)
list_delta_t_mtz = []
list_delta_t_tzp = []
list_delta_percent_mtz = []
list_delta_percent_tzp = []
list_mtz_result = []
list_tzp_result = []
ust_mtz = 20.0


class TestMTZ5V28(object):
    def __init__(self):
        pass
    
    def st_test_mtz_5_v2_8(self):
        # reset.reset_all()
        # Сообщение	«Убедитесь в отсутствии других блоков в панелях разъемов
        # и вставьте блок в соответствующий разъем панели B»
        # 	«Переключите тумблер на корпусе блока в положение «Работа» и установите регуляторы уставок
        # 	в положение 2 (2-8) и в положение 0.8 (0.8-3)»
        msg_1 = "Убедитесь в отсутствии других блоков в панелях разъемов и вставьте блок в соответствующий разъем панели B"
        msg_2 = "«Переключите тумблер на корпусе блока в положение «Работа» и установите регуляторы уставок " \
                "в положение 2 (2-8) и в положение 0.8 (0.8-3)»"
        if my_msg(msg_1):
            if my_msg(msg_2):
                pass
            else:
                return False
        else:
            return False
        mysql_conn.mysql_ins_result('идёт тест 1', '1')
        ctrl_kl.ctrl_relay('KL1', True)
        sleep(0.5)
        ctrl_kl.ctrl_relay('KL2', True)
        sleep(1)
        self.__sbros_zashit()
        in_a1, in_a5 = self.__inputs_a()
        if in_a1 == True and in_a5 == False:
            pass
        else:
            fault.debug_msg("тест 1.1 положение выходов не соответствует", 1)
            mysql_conn.mysql_ins_result('неисправен', '1')
            return False
        fault.debug_msg("тест 1.1 положение выходов соответствует", 4)
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
        fault.debug_msg(f'напряжение после включения KL63\t{meas_volt}\tдолжно быть от\t{min_volt}\tдо\t{max_volt}', 3)
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
            reset.stop_procedure_32()
            return False
        reset.stop_procedure_32()
        mysql_conn.mysql_ins_result('исправен', '1')
        # Тест 2. Проверка работоспособности защиты МТЗ блока в режиме «Проверка»
        # Сообщение	«Переключите регулятор МТЗ, расположенный на корпусе блока в положение «Проверка».
        msg_3 = "Переключите регулятор МТЗ, расположенный на корпусе блока в положение «Проверка»"
        if my_msg(msg_3):
            pass
        else:
            return False
        if proc.procedure_1_24_34(setpoint_volt=ust_mtz, coef_volt=coef_volt):
            pass
        else:
             mysql_conn.mysql_ins_result("неисправен TV1", "2")
             return False
        fault.debug_msg("2.2.  Проверка срабатывания блока от сигнала нагрузки:", 3)
        # 2.2.  Проверка срабатывания блока от сигнала нагрузки:
        mysql_conn.mysql_ins_result('идёт тест 2.2', '2')
        ctrl_kl.ctrl_relay('KL63', True)
        sleep(0.5)
        ctrl_kl.ctrl_relay('KL63', False)
        sleep(0.2)
        in_a1, in_a5 = self.__inputs_a()
        if in_a1 == False and in_a5 == True:
            pass
        elif in_a1 == True:
            mysql_conn.mysql_ins_result('неисправен', '2')
            mysql_conn.mysql_error(444)
            return False
        elif in_a5 == False:
            mysql_conn.mysql_ins_result('неисправен', '2')
            mysql_conn.mysql_error(445)
            return False
        reset.stop_procedure_3()
        # 2.4.2. Сброс защит после проверки
        mysql_conn.mysql_ins_result('идёт тест 2.4', '2')
        fault.debug_msg("2.4.2. Сброс защит после проверки", 3)
        self.__sbros_zashit()
        in_a1, in_a5 = self.__inputs_a()
        if in_a1 == True and in_a5 == False:
            pass
        elif in_a1 == False:
            fault.debug_msg("положение выходов не соответствует", 1)
            mysql_conn.mysql_ins_result('неисправен', '2')
            mysql_conn.mysql_error(446)
            return False
        elif in_a5 == True:
            fault.debug_msg("положение выходов не соответствует", 1)
            mysql_conn.mysql_ins_result('неисправен', '2')
            mysql_conn.mysql_error(447)
            return False
        fault.debug_msg("положение выходов соответствует", 4)
        mysql_conn.mysql_ins_result('исправен', '2')
        # Тест 3. Проверка срабатывания защиты ПМЗ блока по уставкам
        #######################################################################################
        # Сообщение	«Переключите тумблер, расположенный на корпусе блока в положение «Работа» #
        #######################################################################################
        ######################################################################
        # Сообщение	Установите регулятор уставок на блоке в положение [i]	 #
        ######################################################################
        msg_test_3 = "Переключите тумблер, расположенный на корпусе блока в положение «Работа»"
        if my_msg(msg_test_3):
            pass
        else:
            return False
        mysql_conn.mysql_ins_result('идёт тест 3', '3')
        msg_5 = "Установите регулятор уставок на блоке в положение \t"
        k = 0
        for i in list_ust_mtz:
            msg_result_mtz = my_msg_2(f'{msg_5} {list_ust_mtz_num[k]}')
            if msg_result_mtz == 0:
                pass
            elif msg_result_mtz == 1:
                return False
            elif msg_result_mtz == 2:
                mysql_conn.mysql_add_message(f'уставка {list_ust_mtz_num[k]} пропущена')
                list_delta_percent_mtz.append('пропущена')
                list_delta_t_mtz.append('пропущена')
                k += 1
                continue
            if proc.procedure_1_24_34(setpoint_volt=i, coef_volt=coef_volt):
                pass
            else:
                mysql_conn.mysql_ins_result("неисправен TV1", "3")
                return False
            fault.debug_msg("3.1.  Проверка срабатывания блока от сигнала нагрузки:", 3)
            # 3.1.  Проверка срабатывания блока от сигнала нагрузки:
            mysql_conn.mysql_ins_result(f'уставка {list_ust_mtz_num[k]}', '3')
            # Δ%= 3.4364*(U4[i])/0.63
            meas_volt = read_mb.read_analog()
            calc_delta_percent_mtz = 3.4364 * meas_volt / 0.63
            fault.debug_msg(f'дельта %\t{calc_delta_percent_mtz}', 2)
            list_delta_percent_mtz.append(round(calc_delta_percent_mtz, 0))
            calc_delta_t_mtz = ctrl_kl.ctrl_ai_code_v0(110)
            if calc_delta_t_mtz != 9999:
                pass
            else:
                mysql_conn.mysql_ins_result('неисправен', '3')
            fault.debug_msg(f'дельта t\t{calc_delta_t_mtz}', 3)
            list_delta_t_mtz.append(round(calc_delta_t_mtz, 0))
            mysql_conn.mysql_add_message(f'уставка {list_ust_mtz_num[k]} дельта t: {calc_delta_t_mtz:.0f}')
            mysql_conn.mysql_add_message(f'уставка {list_ust_mtz_num[k]} дельта %: {calc_delta_percent_mtz:.0f}')
            in_a1, in_a5 = self.__inputs_a()
            if in_a1 == False and in_a5 == True:
                reset.stop_procedure_3()
                self.__subtest_35()
            else:
                reset.stop_procedure_3()
                mysql_conn.mysql_error(448)
                if self.__subtest_32(coef_volt, i, k):
                    if self.__subtest_35():
                        k += 1
                        continue
                    else:
                        mysql_conn.mysql_ins_result('неисправен', '3')
                        return False
                else:
                    if self.__subtest_33():
                        k += 1
                        continue
                    else:
                        mysql_conn.mysql_ins_result('неисправен', '3')
                        return False
        mysql_conn.mysql_ins_result('исправен', '3')
        # Тест 4. Проверка срабатывания защиты от перегрузки блока по уставкам
        # Сообщение	Установите регулятор времени перегруза на блоке в положение «15 сек»
        # 	Установите регулятор МТЗ, расположенный на блоке, в положение «8»
        # Сообщение	Установите регулятор уставок на блоке в положение [i]
        msg_6 = "Установите регулятор времени перегруза на блоке в положение «21 сек»"
        # msg_7 = "Установите регулятор МТЗ, расположенный на блоке, в положение «8»"
        msg_8 = "Установите регулятор уставок на блоке в положение\t"
        if my_msg(msg_6):
            pass
        else:
            return False
        mysql_conn.mysql_ins_result('идёт тест 4', '4')
        m = 0
        for n in list_ust_tzp:
            msg_result_tzp = my_msg_2(f'{msg_8} {list_ust_tzp_num[m]}')
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
            mysql_conn.mysql_ins_result(f'уставка {list_ust_tzp_num[m]}', '4')
            if proc.procedure_1_24_34(setpoint_volt=n, coef_volt=coef_volt):
                pass
            else:
                mysql_conn.mysql_ins_result("неисправен TV1", "4")
                return False
            # Δ%= 3.4364*U4[i]/0.63
            meas_volt = read_mb.read_analog()
            calc_delta_percent_tzp = 3.4364 * meas_volt / 0.63
            fault.debug_msg(f'дельта %\t {calc_delta_percent_tzp}', 2)
            list_delta_percent_tzp.append(round(calc_delta_percent_tzp, 0))
            # 4.4.  Проверка срабатывания блока от сигнала нагрузки:
            ctrl_kl.ctrl_relay('KL63', True)
            r = 0
            in_b1 = self.__inputs_b()
            while in_b1 == False and r <= 5:
                in_b1 = self.__inputs_b()
                r += 1
            start_timer_tzp = time()
            delta_t_tzp = 0
            in_a5 = self.__inputs_a5()
            while in_a5 == False and delta_t_tzp <= 15:
                delta_t_tzp = time() - start_timer_tzp
                in_a5 = self.__inputs_a5()
            stop_timer_tzp = time()
            ctrl_kl.ctrl_relay('KL63', False)
            calc_delta_t_tzp = stop_timer_tzp - start_timer_tzp
            fault.debug_msg(f'тест 3 delta t: {calc_delta_t_tzp}', 2)
            list_delta_t_tzp.append(round(calc_delta_t_tzp, 0))
            mysql_conn.mysql_add_message(f'уставка {list_ust_tzp_num[m]} дельта t: {calc_delta_t_tzp:.0f}')
            mysql_conn.mysql_add_message(f'уставка {list_ust_tzp_num[m]} дельта %: {calc_delta_percent_tzp:.0f}')
            in_a1, in_a5 = self.__inputs_a()
            if in_a1 == False and in_a5 == True and calc_delta_t_tzp <= 21:
                fault.debug_msg("положение выходов соответствует", 4)
                if self.__subtest_46():
                    m += 1
                    continue
                else:
                    return False
            else:
                fault.debug_msg("положение выходов не соответствует", 1)
                mysql_conn.mysql_error(448)
                if self.__subtest_45():
                    m += 1
                    continue
                else:
                    return False
        mysql_conn.mysql_ins_result('исправен', '4')
        return True
    
    def __subtest_32(self, coef_volt, i, k):
        # 3.2. Формирование нагрузочного сигнала 1,15*U3[i]:
        self.__sbros_zashit()
        in_a1, in_a5 = self.__inputs_a()
        if in_a1 == True and in_a5 == False:
            pass
        elif in_a1 == False:
            mysql_conn.mysql_error(446)
            mysql_conn.mysql_ins_result('неисправен', '3')
            return False
        elif in_a5 == True:
            mysql_conn.mysql_error(447)
            mysql_conn.mysql_ins_result('неисправен', '3')
            return False
        # Процедура 1. Проверка отсутствия вероятности возникновения межвиткового замыкания
        # на стороне первичной обмотки трансформатора TV1
        # Процедура 2: а=8. Проверка отсутствия вероятности возникновения межвиткового замыкания
        # на стороне вторичной обмотки TV1:
        # Процедура 3: а=5 Формирование нагрузочного сигнала U3:
        if proc.start_procedure_1():
            calc_vol = proc.start_procedure_28(coef_volt=coef_volt, setpoint_volt=i)
            if proc.start_procedure_35(calc_volt=calc_vol, setpoint_volt=i):
                pass
            else:
                mysql_conn.mysql_ins_result('неисправен', '3')
                return False
        else:
            mysql_conn.mysql_ins_result('неисправен', '3')
            return False
        # 3.2.2.  Проверка срабатывания блока от сигнала нагрузки:
        meas_volt = read_mb.read_analog()
        calc_delta_percent_mtz = 3.4364 * meas_volt / 0.63
        list_delta_percent_mtz[-1] = round(calc_delta_percent_mtz, 0)
        calc_delta_t_mtz = ctrl_kl.ctrl_ai_code_v0(110)
        if calc_delta_t_mtz != 9999:
            pass
        else:
            mysql_conn.mysql_ins_result('неисправен', '3')
        list_delta_t_mtz[-1] = round(calc_delta_t_mtz, 0)
        mysql_conn.mysql_add_message(f'уставка {list_ust_mtz_num[k]} дельта t: {calc_delta_t_mtz:.0f}')
        mysql_conn.mysql_add_message(f'уставка {list_ust_mtz_num[k]} дельта %: {calc_delta_percent_mtz:.0f}')
        in_a1, in_a5 = self.__inputs_a()
        if in_a1 == False and in_a5 == True:
            reset.stop_procedure_3()
            return True
        else:
            reset.stop_procedure_3()
            mysql_conn.mysql_error(448)
            return False
        # Если входа DI.A1, DI.A5 занимают состояние, указанное в таблице выше, то переходим к п.3.5.
        # Если входа DI.A1, DI.A5  не заняли состояние, указанное в таблице состояний DI,
        # расположенной выше, то выдаем сообщение, соответствующее коду ошибки и переходим к п.3.3.
    
    def __subtest_33(self):
        # 3.3. Сброс защит после проверки
        self.__sbros_zashit()
        in_a1, in_a5 = self.__inputs_a()
        if in_a1 == True and in_a5 == False:
            return True
        elif in_a1 == False:
            mysql_conn.mysql_error(446)
            mysql_conn.mysql_ins_result('неисправен', '3')
            return False
        elif in_a5 == True:
            mysql_conn.mysql_error(447)
            mysql_conn.mysql_ins_result('неисправен', '3')
            return False
    
    def __subtest_35(self):
        # 3.5. Расчет относительной нагрузки сигнала
        # Δ%= 3.4364*(U4[i])/0.63
        self.__sbros_zashit()
        in_a1, in_a5 = self.__inputs_a()
        if in_a1 == True and in_a5 == False:
            return True
        elif in_a1 == False:
            mysql_conn.mysql_error(446)
            mysql_conn.mysql_ins_result('неисправен', '3')
            return False
        elif in_a5 == True:
            mysql_conn.mysql_error(447)
            mysql_conn.mysql_ins_result('неисправен', '3')
            return False
    
    def __subtest_45(self):
        reset.stop_procedure_3()
        # 4.5.1. Сброс защит после проверки
        self.__sbros_zashit()
        in_a1, in_a5 = self.__inputs_a()
        if in_a1 == True and in_a5 == False:
            fault.debug_msg("тест 4.5 положение выходов соответствует", 4)
            return True
        elif in_a1 == False:
            mysql_conn.mysql_error(446)
            mysql_conn.mysql_ins_result('неисправен', '4')
            fault.debug_msg("тест 4.5 положение выходов не соответствует", 1)
            return False
        elif in_a5 == True:
            mysql_conn.mysql_error(447)
            mysql_conn.mysql_ins_result('неисправен', '4')
            fault.debug_msg("тест 4.5 положение выходов не соответствует", 1)
            return False
    
    def __subtest_46(self):
        reset.stop_procedure_3()
        # 4.6.1. Сброс защит после проверки
        # Определение кратности сигнала нагрузки: Δ%= 3.4364*U4[i]/0.63
        self.__sbros_zashit()
        in_a1, in_a5 = self.__inputs_a()
        if in_a1 == True and in_a5 == False:
            fault.debug_msg("тест 4.6 положение выходов соответствует", 4)
            return True
        elif in_a1 == False:
            mysql_conn.mysql_error(449)
            mysql_conn.mysql_ins_result('неисправен', '4')
            fault.debug_msg("тест 4.6 положение выходов не соответствует", 1)
            return False
        elif in_a5 == True:
            mysql_conn.mysql_error(450)
            mysql_conn.mysql_ins_result('неисправен', '4')
            fault.debug_msg("тест 4.6 положение выходов не соответствует", 1)
            return False
    
    @staticmethod
    def __inputs_a():
        in_a1 = read_mb.read_discrete(1)
        in_a5 = read_mb.read_discrete(5)
        return in_a1, in_a5
    
    @staticmethod
    def __inputs_a5():
        in_a5 = read_mb.read_discrete(5)
        return in_a5
    
    def __sbros_zashit(self):
        ctrl_kl.ctrl_relay('KL1', False)
        sleep(1.5)
        ctrl_kl.ctrl_relay('KL1', True)
        sleep(2)
    
    @staticmethod
    def __inputs_b():
        in_b1 = read_mb.read_discrete(9)
        return in_b1


if __name__ == '__main__':
    try:
        test_mtz_5_v2_8 = TestMTZ5V28()
        if test_mtz_5_v2_8.st_test_mtz_5_v2_8():
            g1, g2 = 0, 0
            for g1 in range(len(list_delta_percent_mtz)):
                list_mtz_result.append((list_ust_mtz_num[g1], list_delta_percent_mtz[g1], list_delta_t_mtz[g1]))
            mysql_conn.mysql_pmz_result(list_mtz_result)
            for g2 in range(len(list_delta_percent_tzp)):
                list_tzp_result.append((list_ust_tzp_num[g2], list_delta_percent_tzp[g2], list_delta_t_tzp[g2]))
            mysql_conn.mysql_tzp_result(list_tzp_result)
            mysql_conn.mysql_block_good()
            my_msg('Блок исправен', 'green')
        else:
            g1, g2 = 0, 0
            for g1 in range(len(list_delta_percent_mtz)):
                list_mtz_result.append((list_ust_mtz_num[g1], list_delta_percent_mtz[g1], list_delta_t_mtz[g1]))
            mysql_conn.mysql_pmz_result(list_mtz_result)
            for g2 in range(len(list_delta_percent_tzp)):
                list_tzp_result.append((list_ust_tzp_num[g2], list_delta_percent_tzp[g2], list_delta_t_tzp[g2]))
            mysql_conn.mysql_tzp_result(list_tzp_result)
            mysql_conn.mysql_block_bad()
            my_msg('Блок неисправен', 'red')
    except OSError:
        my_msg("ошибка системы", 'red')
    except SystemError:
        my_msg("внутренняя ошибка", 'red')
    finally:
        reset.reset_all()
        sys.exit()
