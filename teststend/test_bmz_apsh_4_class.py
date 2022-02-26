#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Алгоритм проверки

Тип блока	Производитель
БМЗ АПШ 4.0	Нет производителя
БМЗ АПШ 4.0	Горэкс-Светотехника

"""

from time import sleep
from sys import exit
from gen_func_procedure import *
from gen_func_utils import *
from my_msgbox import *
from my_msgbox_2 import *
from gen_mb_client import *
from gen_mysql_connect import *

__all__ = ["TestBMZAPSH4"]

proc = Procedure()
reset = ResetRelay()
ctrl_kl = CtrlKL()
read_mb = ReadMB()
mysql_conn = MySQLConnect()
fault = Bug(True)

# Таблица уставок
#
# № уставки	1	2	3	4	5
# i	1	2	3	4	5
# U2[i], В	9.84	16.08	23.28	34.44	50.04

# ust = (9.84, 16.08, 23.28, 34.44, 50.04)

# with open('config.json', 'r') as rf:
#     config = rf.read()
#
# set_point = json.loads(config)
# set_point_bmz_apsh_4 = set_point.get('set_point_bmz_apsh_4')
# list_ust = set_point_bmz_apsh_4.get('list_ust')
# list_ust_num = set_point_bmz_apsh_4.get('list_ust_num')
list_ust_num = (1, 2, 3, 4, 5)
list_ust = (9.84, 16.08, 23.28, 34.44, 50.04)

list_delta_t = []
list_result = []


class TestBMZAPSH4(object):
    def __init__(self):
        pass
    
    def st_test_bmz_apsh_4(self):
        # reset.reset_all()
        # Тест 1. Проверка исходного состояния блока:
        # Сообщение	«Установите переключатель уставок на блоке в положение 1
        msg_1 = "Установите переключатель уставок на блоке в положение 1"
        if my_msg(msg_1):
            pass
        else:
            return False
        mysql_conn.mysql_ins_result('идёт тест 1.1', '1')
        ctrl_kl.ctrl_relay('KL66', True)
        reset.sbros_zashit_kl1()
        in_a1 = self.__inputs_a()
        if in_a1 == False:
            fault.debug_msg("вход 1 соответствует", 4)
            pass
        else:
            fault.debug_msg("вход 1 не соответствует", 1)
            mysql_conn.mysql_ins_result('неисправен', '1')
            mysql_conn.mysql_error(342)
            return False
        mysql_conn.mysql_ins_result('идёт тест 1.2', '1')
        meas_volt_ust = proc.procedure_1_21_31()
        if meas_volt_ust != False:
            pass
        else:
            mysql_conn.mysql_ins_result('неисправен TV1', '1')
        ctrl_kl.ctrl_relay('KL63', True)
        meas_volt = read_mb.read_analog()
        if 0.9 * meas_volt_ust <= meas_volt <= 1.1 * meas_volt_ust:
            pass
        else:
            fault.debug_msg("напряжение не соответствует", 1)
            mysql_conn.mysql_ins_result('неисправен', '1')
            mysql_conn.mysql_error(343)
            reset.sbros_kl63_proc_1_21_31()
        fault.debug_msg(f'напряжение соответствует заданному \t {meas_volt}', 2)
        reset.sbros_kl63_proc_1_21_31()
        mysql_conn.mysql_ins_result('идёт тест 1.3', '1')
        coef_volt = proc.procedure_1_22_32()
        fault.debug_msg(f'коэф. сети \t {coef_volt}', 2)
        if coef_volt != False:
            pass
        else:
            reset.stop_procedure_32()
            mysql_conn.mysql_ins_result('неисправен TV1', '1')
            return False
        mysql_conn.mysql_ins_result('тест 1 исправен', '1')
        reset.stop_procedure_32()
        # Тест 2. Проверка срабатывания защиты блока по уставкам
        # Сообщение	Установите регулятор уставок на блоке в положение [i]
        fault.debug_msg("запуск теста 2", 3)
        mysql_conn.mysql_ins_result('идёт тест 2', '1')
        k = 0
        for i in list_ust:
            msg_4 = (f'Установите регулятор уставок на блоке в положение: {list_ust_num[k]}')
            msg_result = my_msg_2(msg_4)
            if msg_result == 0:
                pass
            elif msg_result == 1:
                return False
            elif msg_result == 2:
                mysql_conn.mysql_add_message(f'уставка {list_ust_num[k]} пропущена')
                list_delta_t.append('пропущена')
                k += 1
                continue
            mysql_conn.mysql_ins_result(f'уставка {list_ust_num[k]}', '4')
            if proc.procedure_1_24_34(coef_volt=coef_volt, setpoint_volt=i):
                pass
            else:
                mysql_conn.mysql_ins_result('неисправен TV1', '1')
            # 2.1.  Проверка срабатывания блока от сигнала нагрузки:
            calc_delta_t = ctrl_kl.ctrl_ai_code_v0(111)
            fault.debug_msg(f'delta t:\t {calc_delta_t}', 2)
            list_delta_t.append(round(calc_delta_t, 0))
            mysql_conn.mysql_add_message(f'уставка {list_ust_num[k]} дельта t: {calc_delta_t:.1f}')
            in_a1 = self.__inputs_a()
            if in_a1 == True:
                fault.debug_msg("вход 1 соответствует", 4)
                reset.stop_procedure_3()
                if self.__sbros_zashit():
                    k += 1
                    continue
                else:
                    return False
            else:
                fault.debug_msg("вход 1 не соответствует", 1)
                mysql_conn.mysql_ins_result('неисправен', '1')
                mysql_conn.mysql_error(344)
                reset.stop_procedure_3()
                if self.__subtest_2_2(coef_volt=coef_volt, i=i, k=k):
                    if self.__sbros_zashit():
                        k += 1
                        continue
                    else:
                        return False
                else:
                    return False
        mysql_conn.mysql_ins_result('исправен', '1')
        fault.debug_msg("тест 2 пройден", 3)
        fault.debug_msg("сбрасываем все и завершаем проверку", 3)
        return True
    
    def __subtest_2_2(self, coef_volt, i, k):
        if self.__sbros_zashit():
            pass
        else:
            return False
        if proc.procedure_1_25_35(coef_volt=coef_volt, setpoint_volt=i):
            pass
        else:
            return False
        calc_delta_t = ctrl_kl.ctrl_ai_code_v0(111)
        fault.debug_msg('delta t\t' + str(calc_delta_t), 2)
        list_delta_t[-1] = round(calc_delta_t, 0)
        mysql_conn.mysql_add_message(f'уставка {list_ust_num[k]} дельта t: {calc_delta_t:.1f}')
        in_a1 = self.__inputs_a()
        if in_a1 == True:
            pass
        else:
            fault.debug_msg("вход 1 не соответствует", 1)
            mysql_conn.mysql_ins_result('неисправен', '1')
            mysql_conn.mysql_error(346)
            return False
        reset.stop_procedure_3()
        return True
    
    def __sbros_zashit(self):
        ctrl_kl.ctrl_relay('KL1', True)
        sleep(1.5)
        ctrl_kl.ctrl_relay('KL1', False)
        sleep(2)
        in_a1 = self.__inputs_a()
        if in_a1 == False:
            pass
        else:
            fault.debug_msg("вход 1 не соответствует", 1)
            mysql_conn.mysql_ins_result('неисправен', '1')
            mysql_conn.mysql_error(344)
            return False
        fault.debug_msg("вход 1 соответствует", 4)
        return True
    
    @staticmethod
    def __inputs_a():
        in_a1 = read_mb.read_discrete(1)
        return in_a1
    
    @staticmethod
    def __inputs_b():
        in_b0 = read_mb.read_discrete(8)
        in_b1 = read_mb.read_discrete(9)
        return in_b0, in_b1


if __name__ == '__main__':
    try:
        test_bmz_apsh_4 = TestBMZAPSH4()
        if test_bmz_apsh_4.st_test_bmz_apsh_4():
            for t1 in range(len(list_delta_t)):
                list_result.append((list_ust_num[t1], list_delta_t[t1]))
            mysql_conn.mysql_ubtz_btz_result(list_result)
            mysql_conn.mysql_block_good()
            my_msg('Блок исправен')
        else:
            for t1 in range(len(list_delta_t)):
                list_result.append((list_ust_num[t1], list_delta_t[t1]))
            mysql_conn.mysql_ubtz_btz_result(list_result)
            mysql_conn.mysql_block_bad()
            my_msg('Блок неисправен')
    except OSError:
        my_msg("ошибка системы")
    except SystemError:
        my_msg("внутренняя ошибка")
    finally:
        reset.reset_all()
        exit()
