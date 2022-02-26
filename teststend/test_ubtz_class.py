#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Алгоритм проверки

Тип блока	Производитель
УБТЗ	Нет производителя
УБТЗ	Горэкс-Светотехника

"""

# import json
from sys import exit
from time import sleep, time
from gen_func_procedure import *
from gen_func_utils import *
from my_msgbox import *
from my_msgbox_2 import *
from gen_mb_client import *
from gen_mysql_connect import *

__all__ = ["TestUBTZ"]

reset = ResetRelay()
proc = Procedure()
fault = Bug(True)
read_mb = ReadMB()
ctrl_kl = CtrlKL()
mysql_conn = MySQLConnect()

# Таблица уставок №1 (К=1.0) ТЗП
# № уставки	1	2	3	4	5	6	7
# i	1	2	3	4	5	6	7
# U2[i], В	11.2	15	18.7	22.4	26.2	29.9	33.6
#
# Таблица уставок №2 (К=1.1) БМЗ
# № уставки	1	2	3	4	5	6	7
# i	1	2	3	4	5	6	7
# U2[i], В	6.9	13.8	27.4	41.1	54.8	68.5	82.2

# with open('config.json', 'r') as rf:
#     config = rf.read()
#
# set_point = json.loads(config)
# set_point_ubtz = set_point.get('set_point_ubtz')
# list_ust_tzp = set_point_ubtz.get('list_ust_tzp')
# list_ust_bmz = set_point_ubtz.get('list_ust_bmz')
# list_ust_bmz_num = set_point_ubtz.get('list_ust_bmz_num')
# list_ust_tzp_num = set_point_ubtz.get('list_ust_tzp_num')

list_ust_bmz_num = (1, 2, 3, 4, 5, 6, 7)
list_ust_tzp_num = (1, 2, 3, 4, 5, 6, 7)
list_ust_bmz = (6.9, 13.8, 27.4, 41.1, 54.8, 68.5, 82.2)
list_ust_tzp = (11.2, 15.0, 18.7, 22.4, 26.2, 29.9, 33.6)

list_delta_t_tzp = []
list_delta_t_bmz = []
list_bmz_result = []
list_tzp_result = []


class TestUBTZ(object):
    def __init__(self):
        pass
    
    def st_test_ubtz(self):
        # reset.reset_all()
        # Сообщение	«Убедитесь в отсутствии других блоков в панелях разъемов и вставьте
        # блок в соответствующий разъем панели С»
        # «Переключите регулятор БМЗ на корпусе блока в положение «1», регулятор ТЗП в положение «0»
        msg_1 = "Убедитесь в отсутствии других блоков в панелях разъемов и вставьте " \
                "блок в соответствующий разъем панели С"
        msg_2 = "Переключите регулятор БМЗ на корпусе блока в положение «1», регулятор ТЗП в положение «0»"
        if my_msg(msg_1):
            if my_msg(msg_2):
                pass
            else:
                return False
        else:
            return False
        mysql_conn.mysql_ins_result("идёт тест 1.1", '1')
        ctrl_kl.ctrl_relay('KL22', True)
        ctrl_kl.ctrl_relay('KL66', True)
        self.__sbros_zashit()
        in_a1, in_a2, in_a5, in_a6 = self.__inputs_a()
        if in_a1 == False and in_a5 == True and in_a2 == False and in_a6 == True:
            pass
        else:
            fault.debug_msg('тест 1 положение выходов не соответствует', 1)
            mysql_conn.mysql_ins_result("неисправен", '1')
            if in_a1 == True:
                mysql_conn.mysql_error(451)
            elif in_a5 == True:
                mysql_conn.mysql_error(452)
            elif in_a2 == True:
                mysql_conn.mysql_error(453)
            elif in_a6 == True:
                mysql_conn.mysql_error(454)
            return False
        fault.debug_msg('тест 1 положение выходов соответствует', 4)
        # 1.1. Проверка вероятности наличия короткого замыкания на входе измерительной цепи блока
        fault.debug_msg('тест 1.1', 3)
        mysql_conn.mysql_ins_result("идёт тест 1.2", '1')
        meas_volt_ust = proc.procedure_1_21_31()
        if meas_volt_ust != False:
            pass
        else:
            return False
        # 1.1.2. Проверка отсутствия короткого замыкания на входе измерительной части блока:
        fault.debug_msg('тест 1.2', 3)
        mysql_conn.mysql_ins_result("идёт тест 1.3", '1')
        ctrl_kl.ctrl_relay('KL63', True)
        sleep(1)
        min_volt = 0.6 * meas_volt_ust
        max_volt = 1.1 * meas_volt_ust
        meas_volt = read_mb.read_analog()
        if min_volt <= meas_volt <= max_volt:
            pass
        else:
            mysql_conn.mysql_ins_result('неисправен', '1')
            mysql_conn.mysql_error(455)
            reset.sbros_kl63_proc_1_21_31()
            return False
        reset.sbros_kl63_proc_1_21_31()
        # 1.2. Определение коэффициента Кс отклонения фактического напряжения от номинального
        fault.debug_msg('тест 1.3', 3)
        mysql_conn.mysql_ins_result("идёт тест 1.4", '1')
        coef_volt = proc.procedure_1_22_32()
        if coef_volt != False:
            pass
        else:
            mysql_conn.mysql_ins_result('неисправен', '1')
            reset.stop_procedure_32()
            return False
        reset.stop_procedure_32()
        mysql_conn.mysql_ins_result('исправен', '1')
        fault.debug_msg('тест 1 завершён', 3)
        # Тест 2. Проверка срабатывания защиты БМЗ блока по уставкам
        # Цикл i=1…7 (Таблица уставок 2 (БМЗ)
        ########################################################################################
        # Сообщение	Установите регулятор БМЗ, расположенный на корпусе блока, в положение [i]  #
        ########################################################################################
        msg_1 = "Установите регулятор БМЗ, расположенный на корпусе блока, в положение\t"
        k = 0
        for i in list_ust_bmz:
            msg_result_bmz = my_msg_2(f'{msg_1} {list_ust_bmz_num[k]}')
            if msg_result_bmz == 0:
                pass
            elif msg_result_bmz == 1:
                return False
            elif msg_result_bmz == 2:
                mysql_conn.mysql_add_message(f'уставка {list_ust_bmz_num[k]} пропущена')
                list_delta_t_bmz.append('пропущена')
                k += 1
                continue
            mysql_conn.mysql_ins_result(f'уставка БМЗ {list_ust_bmz_num[k]}', '1')
            if proc.procedure_1_24_34(coef_volt=coef_volt, setpoint_volt=i):
                pass
            else:
                mysql_conn.mysql_ins_result('неисправен TV1', '1')
                return False
            # 3.1.  Проверка срабатывания блока от сигнала нагрузки:
            calc_delta_t_bmz = ctrl_kl.ctrl_ai_code_v0(109)
            fault.debug_msg(f'тест 2, дельта t\t{calc_delta_t_bmz}', 2)
            list_delta_t_bmz.append(calc_delta_t_bmz)
            mysql_conn.mysql_add_message(f'уставка {list_ust_bmz_num[k]} дельта t: {calc_delta_t_bmz}')
            in_a1, in_a2, in_a5, in_a6 = self.__inputs_a()
            if in_a1 == True and in_a5 == False and in_a2 == False and in_a6 == True:
                fault.debug_msg('тест 2 положение выходов соответствует', 4)
                reset.stop_procedure_3()
                if self.__subtest_35():
                    k += 1
                    continue
                else:
                    mysql_conn.mysql_ins_result("тест 2 неисправен", '1')
                    return False
            else:
                fault.debug_msg('тест 2 положение выходов не соответствует', 1)
                if in_a1 == False:
                    mysql_conn.mysql_error(456)
                elif in_a5 == True:
                    mysql_conn.mysql_error(457)
                elif in_a2 == True:
                    mysql_conn.mysql_error(458)
                elif in_a6 == False:
                    mysql_conn.mysql_error(459)
                reset.stop_procedure_3()
                if self.__subtest_32(coef_volt=coef_volt, i=i, k=k):
                    if self.__subtest_35():
                        k += 1
                        continue
                    else:
                        mysql_conn.mysql_ins_result("тест 2 неисправен", '1')
                        return False
                else:
                    if self.__subtest_33():
                        k += 1
                        continue
                    else:
                        mysql_conn.mysql_ins_result("тест 2 неисправен", '1')
                        return False
        mysql_conn.mysql_ins_result("тест 2 исправен", '1')
        # Тест 3. Проверка срабатывания защиты ТЗП блока по уставкам
        # Сообщение:	Установите регулятор БМЗ, расположенный на блоке, в положение «0»
        msg_2 = "Установите регулятор БМЗ, расположенный на блоке, в положение «0»"
        if my_msg(msg_2):
            pass
        else:
            return False
        # Цикл i=1…7 Таблица уставок №1
        ###############################################################################
        # Сообщение	Установите регулятор ТЗП, расположенный на блоке в положение [i]  #
        ###############################################################################
        msg_3 = "Установите регулятор ТЗП, расположенный на блоке в положение\t"
        m = 0
        for n in list_ust_tzp:
            msg_result_tzp = my_msg_2(f'{msg_3} {list_ust_tzp_num[m]}')
            if msg_result_tzp == 0:
                pass
            elif msg_result_tzp == 1:
                return False
            elif msg_result_tzp == 2:
                mysql_conn.mysql_add_message(f'уставка {list_ust_tzp_num[m]} пропущена')
                list_delta_t_tzp.append('пропущена')
                k += 1
                continue
            mysql_conn.mysql_ins_result(f'уставка ТЗП {list_ust_tzp_num[m]}', '1')
            if proc.procedure_1_24_34(coef_volt=coef_volt, setpoint_volt=n):
                pass
            else:
                mysql_conn.mysql_ins_result("тест 3 неисправен TV1", '1')
                return False
            # 4.4.  Проверка срабатывания блока от сигнала нагрузки:
            ctrl_kl.ctrl_relay('KL63', True)
            in_b1 = self.__inputs_b1()
            while in_b1 == False:
                in_b1 = self.__inputs_b1()
            start_timer = time()
            sub_timer = 0
            in_a6 = self.__inputs_a6()
            while in_a6 == True and sub_timer <= 370:
                sub_timer = time() - start_timer
                # fault.debug_msg("времени прошло\t" + str(sub_timer), 2)
                sleep(0.2)
                in_a6 = self.__inputs_a6()
            stop_timer = time()
            reset.stop_procedure_3()
            calc_delta_t_tzp = stop_timer - start_timer
            fault.debug_msg(f'тест 3 delta t:\t{calc_delta_t_tzp}', 2)
            list_delta_t_tzp.append(calc_delta_t_tzp)
            mysql_conn.mysql_add_message(f'уставка {list_ust_tzp_num[k]} дельта t: {calc_delta_t_tzp:.0f}')
            in_a1, in_a2, in_a5, in_a6 = self.__inputs_a()
            if in_a1 == False and in_a5 == True and in_a2 == False and in_a6 == True and calc_delta_t_tzp <= 360:
                if self.__subtest_46():
                    m += 1
                    continue
                else:
                    return False
            else:
                if in_a1 == True:
                    mysql_conn.mysql_error(451)
                elif in_a5 == True:
                    mysql_conn.mysql_error(452)
                elif in_a2 == True:
                    mysql_conn.mysql_error(453)
                elif in_a6 == True:
                    mysql_conn.mysql_error(454)
                mysql_conn.mysql_ins_result("тест 3 неисправен", '1')
                if self.__subtest_46():
                    m += 1
                    continue
                else:
                    return False
        mysql_conn.mysql_ins_result("исправен", '1')
        return True
    
    def __subtest_32(self, coef_volt, i, k):
        """
        3.2. Формирование нагрузочного сигнала 1,1*U3[i]:
        :return:
        """
        # 3.2.1. Сброс защит после проверки
        self.__sbros_zashit()
        in_a1, in_a2, in_a5, in_a6 = self.__inputs_a()
        if in_a1 == False and in_a5 == True and in_a2 == False and in_a6 == True:
            pass
        else:
            fault.debug_msg("тест 3.1 положение выходов не соответствует", 1)
            mysql_conn.mysql_ins_result("тест 2 неисправен", '1')
            if in_a1 == True:
                mysql_conn.mysql_error(460)
            elif in_a5 == True:
                mysql_conn.mysql_error(461)
            elif in_a2 == True:
                mysql_conn.mysql_error(462)
            elif in_a6 == True:
                mysql_conn.mysql_error(463)
            return False
        fault.debug_msg("тест 3.1 положение выходов соответствует", 4)
        if proc.procedure_1_25_35(coef_volt=coef_volt, setpoint_volt=i):
            pass
        else:
            mysql_conn.mysql_ins_result("неисправен TV1", '1')
            return False
        # 3.2.2.  Проверка срабатывания блока от сигнала нагрузки:
        calc_delta_t_bmz = ctrl_kl.ctrl_ai_code_v0(109)
        fault.debug_msg(f'тест 3 delta t:\t{calc_delta_t_bmz}', 2)
        list_delta_t_bmz[-1] = calc_delta_t_bmz
        mysql_conn.mysql_add_message(f'уставка {list_ust_bmz_num[k]} дельта t: {calc_delta_t_bmz:.0f}')
        in_a1, in_a2, in_a5, in_a6 = self.__inputs_a()
        if in_a1 == True and in_a5 == False and in_a2 == False and in_a6 == True:
            pass
        else:
            fault.debug_msg("тест 3.2 положение выходов не соответствует", 1)
            reset.stop_procedure_3()
            if in_a1 == True:
                mysql_conn.mysql_error(464)
            elif in_a5 == True:
                mysql_conn.mysql_error(465)
            elif in_a2 == True:
                mysql_conn.mysql_error(466)
            elif in_a6 == True:
                mysql_conn.mysql_error(467)
            return False
        fault.debug_msg("тест 3.2 положение выходов соответствует", 4)
        reset.stop_procedure_3()
        return True
    
    def __subtest_33(self):
        """
        3.3. Сброс защит после проверки
        :return:
        """
        self.__sbros_zashit()
        in_a1, in_a2, in_a5, in_a6 = self.__inputs_a()
        if in_a1 == False and in_a5 == True and in_a2 == False and in_a6 == True:
            return True
        elif in_a1 == True:
            mysql_conn.mysql_error(460)
            mysql_conn.mysql_ins_result("тест 2 неисправен", '1')
            return False
        elif in_a5 == True:
            mysql_conn.mysql_error(461)
            mysql_conn.mysql_ins_result("тест 2 неисправен", '1')
            return False
        elif in_a2 == True:
            mysql_conn.mysql_error(462)
            mysql_conn.mysql_ins_result("тест 2 неисправен", '1')
            return False
        elif in_a6 == True:
            mysql_conn.mysql_error(463)
            mysql_conn.mysql_ins_result("тест 2 неисправен", '1')
            return False
    
    def __subtest_35(self):
        """
        3.5. Расчет времени срабатывания
        ΔT= T1[i] - T0[i], мс
        3.6. Сброс защит после проверки
    
        :return:
        """
        self.__sbros_zashit()
        in_a1, in_a2, in_a5, in_a6 = self.__inputs_a()
        if in_a1 == False and in_a5 == True and in_a2 == False and in_a6 == True:
            return True
        elif in_a1 == True:
            mysql_conn.mysql_error(460)
            mysql_conn.mysql_ins_result("тест 2 неисправен", '1')
            return False
        elif in_a5 == True:
            mysql_conn.mysql_error(461)
            mysql_conn.mysql_ins_result("тест 2 неисправен", '1')
            return False
        elif in_a2 == True:
            mysql_conn.mysql_error(462)
            mysql_conn.mysql_ins_result("тест 2 неисправен", '1')
            return False
        elif in_a6 == True:
            mysql_conn.mysql_error(463)
            mysql_conn.mysql_ins_result("тест 2 неисправен", '1')
            return False
    
    def __subtest_46(self):
        self.__sbros_zashit()
        in_a1, in_a2, in_a5, in_a6 = self.__inputs_a()
        if in_a1 == False and in_a5 == True and in_a2 == False and in_a6 == True:
            return True
        elif in_a1 == True:
            mysql_conn.mysql_error(460)
            mysql_conn.mysql_ins_result("тест 3 неисправен", '1')
            return False
        elif in_a5 == True:
            mysql_conn.mysql_error(461)
            mysql_conn.mysql_ins_result("тест 3 неисправен", '1')
            return False
        elif in_a2 == True:
            mysql_conn.mysql_error(462)
            mysql_conn.mysql_ins_result("тест 3 неисправен", '1')
            return False
        elif in_a6 == True:
            mysql_conn.mysql_error(463)
            mysql_conn.mysql_ins_result("тест 3 неисправен", '1')
            return False
    
    def __sbros_zashit(self):
        ctrl_kl.ctrl_relay('KL1', True)
        ctrl_kl.ctrl_relay('KL31', True)
        sleep(1.5)
        ctrl_kl.ctrl_relay('KL1', False)
        ctrl_kl.ctrl_relay('KL31', False)
        sleep(2)
    
    @staticmethod
    def __inputs_a():
        in_a1 = read_mb.read_discrete(1)
        in_a2 = read_mb.read_discrete(2)
        in_a5 = read_mb.read_discrete(5)
        in_a6 = read_mb.read_discrete(6)
        return in_a1, in_a2, in_a5, in_a6
    
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
    def __inputs_a6():
        in_a6 = read_mb.read_discrete(6)
        return in_a6


if __name__ == '__main__':
    try:
        test_ubtz = TestUBTZ()
        if test_ubtz.st_test_ubtz():
            for t1 in range(len(list_delta_t_bmz)):
                list_bmz_result.append((list_ust_bmz_num[t1], list_delta_t_bmz[t1]))
            for t2 in range(len(list_delta_t_tzp)):
                list_tzp_result.append((list_ust_tzp_num[t2], list_delta_t_tzp[t2]))
            mysql_conn.mysql_ubtz_btz_result(list_bmz_result)
            mysql_conn.mysql_ubtz_tzp_result(list_tzp_result)
            mysql_conn.mysql_block_good()
            my_msg('Блок исправен')
        else:
            for t1 in range(len(list_delta_t_bmz)):
                list_bmz_result.append((list_ust_bmz_num[t1], list_delta_t_bmz[t1]))
            for t2 in range(len(list_delta_t_tzp)):
                list_tzp_result.append((list_ust_tzp_num[t2], list_delta_t_tzp[t2]))
            mysql_conn.mysql_ubtz_btz_result(list_bmz_result)
            mysql_conn.mysql_ubtz_tzp_result(list_tzp_result)
            mysql_conn.mysql_block_bad()
            my_msg('Блок неисправен')
    except OSError:
        my_msg("ошибка системы")
    except SystemError:
        my_msg("внутренняя ошибка")
    finally:
        reset.reset_all()
        exit()
