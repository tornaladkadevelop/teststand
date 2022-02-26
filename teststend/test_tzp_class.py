#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Алгоритм проверки

Тип блока	Производитель	    Уникальный номер
ТЗП	        Нет производителя	    61
ТЗП	        Углеприбор	            62
ТЗП-П	    Нет производителя	    63
ТЗП-П	    Пульсар	                64

"""

from sys import exit
from time import time, sleep
from gen_func_procedure import *
from gen_func_utils import *
from gen_func_tv1 import *
from my_msgbox import *
from my_msgbox_2 import *
from gen_mb_client import *
from gen_mysql_connect import *

__all__ = ["TestTZP"]

# Таблица уставок
# № уставки	0.5	0.6	0.7	0.8	0.9	1.0
# U2[i], В	25.7	29.8	34.3	39.1	43.7	48.5

reset = ResetRelay()
proc = Procedure()
perv_obm = PervObmTV1()
vtor_obm = VtorObmTV1()
read_mb = ReadMB()
ctrl_kl = CtrlKL()
mysql_conn = MySQLConnect()
fault = Bug(True)

list_ust_num = (0.5,	0.6, 0.7, 0.8, 0.9, 1.0)
list_ust = (25.7, 29.8, 34.3, 39.1, 43.7, 48.5)
list_delta_t = []
list_delta_percent = []
list_tzp_result = []
coef_volt = 0.0


class TestTZP(object):
    def __init__(self):
        pass
    
    def st_test_tzp(self):
        # reset.reset_all()
        mysql_conn.mysql_ins_result('идет тест 1', '1')
        # Тест 1. Проверка исходного состояния блока:
        ctrl_kl.ctrl_relay('KL21', True)
        reset.sbros_zashit_kl30_1s5()
        in_a1, in_a5 = self.__inputs_a()
        if in_a1 == False and in_a5 == True:
            fault.debug_msg("состояние выходов блока соответствует", 3)
            pass
        elif in_a1 == True:
            fault.debug_msg("вход 1 не соответствует", 1)
            mysql_conn.mysql_ins_result('неисправен', '1')
            mysql_conn.mysql_error(277)
            return False
        elif in_a5 == False:
            fault.debug_msg("вход 5 не соответствует", 1)
            mysql_conn.mysql_ins_result('неисправен', '1')
            mysql_conn.mysql_error(278)
            return False
        # 1.1. Проверка вероятности наличия короткого замыкания на входе измерительной цепи блока
        mysql_conn.mysql_ins_result('идет тест 1.1', '1')
        meas_volt_ust = proc.procedure_1_21_31()
        if meas_volt_ust != False:
            pass
        else:
            mysql_conn.mysql_ins_result('неисправен', '1')
            return False
        # 1.1.3. Проверка отсутствия короткого замыкания на входе измерительной части блока:
        mysql_conn.mysql_ins_result('идет тест 1.2', '1')
        ctrl_kl.ctrl_relay('KL63', True)
        sleep(1)
        min_volt = 0.6 * meas_volt_ust
        max_volt = 1.1 * meas_volt_ust
        meas_volt = read_mb.read_analog()
        fault.debug_msg(f'напряжение \t{meas_volt}', 3)
        if min_volt <= meas_volt <= max_volt:
            fault.debug_msg("напряжение соответствует", 3)
            pass
        else:
            fault.debug_msg("напряжение не соответствует", 1)
            mysql_conn.mysql_ins_result('неисправен', '1')
            mysql_conn.mysql_error(281)
            reset.sbros_kl63_proc_1_21_31()
            return False
        # 1.1.4. Финишные операции отсутствия короткого замыкания на входе измерительной части блока::
        reset.sbros_kl63_proc_1_21_31()
        # 1.2. Определение коэффициента отклонения фактического напряжения от номинального
        mysql_conn.mysql_ins_result('идет тест 1.3', '1')
        coef_volt = proc.procedure_1_22_32()
        if coef_volt != False:
            pass
        else:
            mysql_conn.mysql_ins_result('неисправен', '1')
            return False
        # 1.2.3. Определение поправочного коэффициента сети Кс:
        reset.stop_procedure_32()
        fault.debug_msg("тест 1 пройден", 3)
        mysql_conn.mysql_ins_result('исправен', '1')
        # Тест 2. Проверка работоспособности блока в режиме «Проверка»
    
        ###########################################################################
        # Сообщение	«Переключите тумблер на корпусе блока в положение «Проверка»  #
        ###########################################################################
    
        msg_1 = "Переключите тумблер на корпусе блока в положение «Проверка» "
        if my_msg(msg_1):
            pass
        else:
            return False
        fault.debug_msg("тест 2.1", 4)
        mysql_conn.mysql_ins_result('идет тест 2', '2')
        in_a1, in_a5 = self.__inputs_a()
        if in_a1 == True and in_a5 == False:
            fault.debug_msg("положение выходов блока соответствует", 3)
            pass
        elif in_a1 == False:
            fault.debug_msg("положение входа 1 не соответствует", 1)
            mysql_conn.mysql_ins_result('неисправен', '2')
            mysql_conn.mysql_error(282)
            return False
        elif in_a5 == True:
            fault.debug_msg("положение входа 5 не соответствует", 1)
            mysql_conn.mysql_ins_result('неисправен', '2')
            mysql_conn.mysql_error(283)
            return False
        msg_3 = "Переключите тумблер на корпусе блока в положение «Работа» "
        if my_msg(msg_3):
            pass
        else:
            return False
        # 2.2. Сброс защит после проверки
        fault.debug_msg("тест 2.2", 4)
        mysql_conn.mysql_ins_result('идет тест 2.1', '2')
        reset.sbros_zashit_kl30_1s5()
        in_a1, in_a5 = self.__inputs_a()
        if in_a1 == False and in_a5 == True:
            pass
        elif in_a1 == True:
            fault.debug_msg("положение входа 1 не соответствует", 1)
            mysql_conn.mysql_ins_result('неисправен', '2')
            mysql_conn.mysql_error(284)
            return False
        elif in_a5 == False:
            fault.debug_msg("положение входа 5 не соответствует", 1)
            mysql_conn.mysql_ins_result('неисправен', '2')
            mysql_conn.mysql_error(285)
            return False
        fault.debug_msg("положение выходов блока соответствует", 3)
        mysql_conn.mysql_ins_result('исправен', '2')
        fault.debug_msg("тест 2 пройден", 3)
    
        ####################################################################################################################
        # Тест 3. Проверка срабатывания блока по уставкам
        ####################################################################################################################
    
        fault.debug_msg("тест 3", 4)
        mysql_conn.mysql_ins_result('идет тест 3', '3')
        k = 0
        for i in list_ust:
            mysql_conn.mysql_ins_result(f'проверка уставки {list_ust_num[k]}', '3')
            msg_5 = (f'Установите регулятор уставок на блоке в положение \t{list_ust_num[k]}')
            msg_result = my_msg_2(msg_5)
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
            if proc.procedure_1_24_34(coef_volt=coef_volt, setpoint_volt=i):
                pass
            else:
                mysql_conn.mysql_ins_result('неисправен', '4')
                return False
            meas_volt = read_mb.read_analog()
            # Определение кратности сигнала нагрузки: Δ%= 0.0044*U42[i]+2.274* U4[i]
            calc_delta_percent = 0.0044 * meas_volt ** 2 + 2.274 * meas_volt
            list_delta_percent.append(calc_delta_percent)
            if 0.9 * i / coef_volt <= meas_volt <= 1.1 * i / coef_volt:
                # Включение вторичного главного контакта	KL63 - ВКЛ	DQ5:1B - ВКЛ
                # Запуск таймера происходит по условию замыкания DI.b0 (контакт реле KL63)
                # Остановка таймера происходит по условию размыкания DI.a5 T1[i]
                fault.debug_msg(f'напряжение соответствует {meas_volt}', 3)
                ctrl_kl.ctrl_relay('KL63', True)
                in_b0, in_b1 = self.__inputs_b()
                while in_b0 == False:
                    in_b0, in_b1 = self.__inputs_b()
                start_timer = time()
                sub_timer = 0
                in_a1, in_a5 = self.__inputs_a()
                while in_a5 == True and sub_timer <= 370:
                    sleep(0.2)
                    sub_timer = time() - start_timer
                    fault.debug_msg(f'времени прошло {sub_timer}', 2)
                    in_a1, in_a5 = self.__inputs_a()
                stop_timer = time()
                ctrl_kl.ctrl_relay('KL63', False)
                calc_delta_t = stop_timer - start_timer
                reset.stop_procedure_3()
                fault.debug_msg(f'тест 3 delta t: {calc_delta_t}', 4)
                list_delta_t.append(calc_delta_t)
                mysql_conn.mysql_add_message(f'уставка {list_ust_num[k]} дельта t: {calc_delta_t:.0f}')
                mysql_conn.mysql_add_message(f'уставка {list_ust_num[k]} дельта %: {calc_delta_percent:.0f}')
                in_a1, in_a5 = self.__inputs_a()
                if calc_delta_t <= 360 and in_a1 == True and in_a5 == False:
                    # Если в период времени до 6 минут входа DI.A1, DI.A5 занимают
                    # состояние, указанное в таблице выше, то переходим к п.3.6.
                    fault.debug_msg("время переключения соответствует", 3)
                    self.__subtest_36(meas_volt)
                    k += 1
                    continue
                else:
                    # Если в период времени до 6 минут входа DI.A1, DI.A5 не занимают
                    # состояние, указанное в таблице выше, то переходим к п.3.5.
                    fault.debug_msg("время переключения не соответствует", 1)
                    mysql_conn.mysql_error(287)
                    self.__subtest_35()
                    k += 1
                    continue
            else:
                fault.debug_msg("напряжение U4 не соответствует", 1)
                mysql_conn.mysql_error(286)
                reset.stop_procedure_3()
        mysql_conn.mysql_ins_result('исправен', '3')
        for t in range(len(list_delta_percent)):
            list_tzp_result.append((list_ust_num[t], list_delta_percent[t], list_delta_t[t]))
        mysql_conn.mysql_tzp_result(list_tzp_result)
        return True
    
    def __subtest_35(self):
        mysql_conn.mysql_ins_result('идет тест 3.5', '3')
        reset.sbros_zashit_kl30_1s5()
        in_a1, in_a5 = self.__inputs_a()
        if in_a1 == False and in_a5 == True:
            fault.debug_msg("положение выходов блока соответствует", 3)
            return True
        elif in_a1 == True:
            fault.debug_msg("положение входа 1 не соответствует", 1)
            mysql_conn.mysql_ins_result('неисправен', '3')
            mysql_conn.mysql_error(284)
            return False
        elif in_a5 == False:
            fault.debug_msg("положение входа 5 не соответствует", 1)
            mysql_conn.mysql_ins_result('неисправен', '3')
            mysql_conn.mysql_error(285)
            return False
    
    def __subtest_36(self, meas_volt):
        mysql_conn.mysql_ins_result('идет тест 3.6', '3')
        reset.sbros_zashit_kl30_1s5()
        in_a1, in_a5 = self.__inputs_a()
        if in_a1 == False and in_a5 == True:
            fault.debug_msg("положение выходов блока соответствует", 3)
            return True
        elif in_a1 == True:
            fault.debug_msg("положение входа 1 не соответствует", 1)
            mysql_conn.mysql_ins_result('неисправен', '3')
            mysql_conn.mysql_error(284)
            return False
        elif in_a5 == False:
            fault.debug_msg("положение входа 5 не соответствует", 1)
            mysql_conn.mysql_ins_result('неисправен', '3')
            mysql_conn.mysql_error(285)
            return False
    
    @staticmethod
    def __inputs_a():
        in_a1 = read_mb.read_discrete(1)
        in_a5 = read_mb.read_discrete(5)
        return in_a1, in_a5
    
    @staticmethod
    def __inputs_b():
        in_b0 = read_mb.read_discrete(8)
        in_b1 = read_mb.read_discrete(9)
        return in_b0, in_b1


if __name__ == '__main__':
    try:
        test_tzp = TestTZP()
        if test_tzp.st_test_tzp():
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
