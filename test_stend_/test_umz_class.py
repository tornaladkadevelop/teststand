#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Алгоритм проверки

Тип блока	Производитель
УМЗ	        Нет производителя

"""

from sys import exit
from time import sleep
from gen_func_procedure import *
from gen_func_utils import *
from my_msgbox import *
from my_msgbox_2 import *
from gen_mb_client import *
from gen_mysql_connect import *

__all__ = ["TestUMZ"]

reset = ResetRelay()
proc = Procedure()
read_mb = ReadMB()
ctrl_kl = CtrlKL()
mysql_conn = MySQLConnect()
fault = Bug(True)

# Таблица уставок №1
# № уставки	1	2	3	4	5	6	7	8	9	10	11
# i	1	2	3	4	5	6	7	8	9	10	11
# U2[i], В	22.6	27.1	31.9	36.5	41.3	46.4	50.2	54.7	59.3	63.8	68.4

list_ust = (22.6, 27.1, 31.9, 36.5, 41.3, 46.4, 50.2, 54.7, 59.3, 63.8, 68.4)
list_ust_num = (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11)
list_delta_t_ab = []
list_delta_t_vg = []
list_delta_percent_ab = []
list_delta_percent_vg = []
list_result = []
meas_volt_ab = 0
meas_volt_vg = 0
test_setpoint_ab = False
test_setpoint_vg = False

msg_4 = "Произведите взвод защит, нажав на корпусе блока на кнопку «Взвод»"


class TestUMZ(object):
    def __init__(self):
        pass
    
    def st_test_umz(self):
        # reset.reset_all()
        # Тест 1. Проверка исходного состояния блока:
    
        #################################################################################################
        # Сообщение	Убедитесь в отсутствии в панелях разъемов установленных блоков                      #
        # Подключите блок УМЗ в разъем Х8 на панели B с помощью соответствующей кабельной сборки        #
        #################################################################################################
    
        #################################################################################################
        # Сообщение	«Переключите тумблер режимов, расположенный на корпусе блока, в положение «Работа»  #
        # «Переведите оба регулятора уставок на корпусе блока в положение «1».                          #
        # Произведите взвод защит, нажав на корпусе блока на кнопку «Взвод»                             #
        #################################################################################################
    
        msg_1 = "Убедитесь в отсутствии в панелях разъемов установленных блоков Подключите " \
                "блок УМЗ в разъем Х8 на панели B с помощью соответствующей кабельной сборки"
        msg_2 = "Переключите тумблер режимов, расположенный на корпусе блока, в положение «Работа»"
        msg_3 = "Переведите оба регулятора уставок на корпусе блока в положение «1»"
    
        if my_msg(msg_1):
            if my_msg(msg_2):
                if my_msg(msg_3):
                    if my_msg(msg_4):
                        pass
                    else:
                        return False
                else:
                    return False
            else:
                return False
        else:
            return False
        mysql_conn.mysql_ins_result("идет тест 1.0", "1")
        in_a1, in_a5 = self.__inputs_a()
        if in_a1 == False and in_a5 == True:
            pass
        elif in_a1 == True:
            mysql_conn.mysql_error(476)
            mysql_conn.mysql_ins_result("неисправен", "1")
            return False
        elif in_a5 == False:
            mysql_conn.mysql_error(477)
            mysql_conn.mysql_ins_result("неисправен", "1")
            return False
        # 1.1. Проверка вероятности наличия короткого замыкания на входе измерительной цепи блока
        mysql_conn.mysql_ins_result("идет тест 1.1", "1")
        meas_volt_ust = proc.procedure_1_21_31()
        if meas_volt_ust != False:
            pass
        else:
            mysql_conn.mysql_ins_result("неисправен", "1")
            return False
        # 1.1.2. Проверка отсутствия короткого замыкания на входе измерительной части блока:
        mysql_conn.mysql_ins_result("идет тест 1.1.2", "1")
        ctrl_kl.ctrl_relay('KL63', True)
        sleep(1)
        min_volt = 0.4 * meas_volt_ust
        max_volt = 1.1 * meas_volt_ust
        meas_volt = read_mb.read_analog()
        fault.debug_msg(f'напряжение после включения KL63 \t{meas_volt}', 2)
        if min_volt <= meas_volt <= max_volt:
            pass
        else:
            fault.debug_msg("измеренное напряжение не соответствует заданному", 1)
            mysql_conn.mysql_ins_result('неисправен', '1')
            mysql_conn.mysql_error(478)
            reset.sbros_kl63_proc_1_21_31()
            return False
        fault.debug_msg("измеренное напряжение соответствует заданному", 3)
        reset.sbros_kl63_proc_1_21_31()
        # 1.2. Определение коэффициента Кс отклонения фактического напряжения от номинального
        mysql_conn.mysql_ins_result("идет тест 1.2", "1")
        coef_volt = proc.procedure_1_22_32()
        if coef_volt != False:
            pass
        else:
            mysql_conn.mysql_ins_result('неисправен', '1')
            mysql_conn.mysql_error(150)
            return False
        fault.debug_msg(f'коэф. сети\t {coef_volt}', 2)
        mysql_conn.mysql_ins_result('исправен', '1')
        reset.stop_procedure_32()
    
        ####################################################################################################################
        # Тест 2. Проверка срабатывания защиты канала АБ по уставкам
    
        #########################################################################
        # Сообщение	Установите оба регулятора уставок на блоке в положение [i]  #
        #########################################################################
        if my_msg(msg_4):
            pass
        else:
            return False
        k = 0
        for i in list_ust:
            mysql_conn.mysql_ins_result("идет тест", "2")
            msg_5 = (f'Установите оба регулятора уставок на блоке в положение \t{list_ust_num[k]}')
            msg_result = my_msg_2(msg_5)
            if msg_result == 0:
                pass
            elif msg_result == 1:
                return False
            elif msg_result == 2:
                mysql_conn.mysql_add_message(f'уставка {list_ust_num[k]} пропущена')
                list_delta_percent_ab.append('пропущена')
                list_delta_t_ab.append('пропущена')
                list_delta_percent_vg.append('пропущена')
                list_delta_t_vg.append('пропущена')
                k += 1
                continue
            progress_msg = (f'формируем U уставки {k}')
            mysql_conn.mysql_ins_result(progress_msg, '2')
            if proc.procedure_1_24_34(coef_volt=coef_volt, setpoint_volt=i):
                pass
            else:
                mysql_conn.mysql_ins_result('неисправен', '2')
                return False
            progress_msg = (f'канал АБ дельта t {k}')
            mysql_conn.mysql_ins_result(progress_msg, '2')
            calc_delta_t_ab = ctrl_kl.ctrl_ai_code_v0(109)
            if calc_delta_t_ab != 9999:
                pass
            else:
                return False
            list_delta_t_ab.append(calc_delta_t_ab)
            in_a1, in_a5 = self.__inputs_a()
            if in_a1 == True and in_a5 == False:
                # Δ%= 0,00004762*(U4)2+9,5648* U4
                progress_msg = (f'канал АБ дельта % {k}')
                mysql_conn.mysql_ins_result(progress_msg, '2')
                meas_volt_ab = read_mb.read_analog()
                calc_delta_percent_ab = 0.00004762 * meas_volt_ab ** 2 + 9.5648 * meas_volt_ab
                list_delta_percent_ab.append(calc_delta_percent_ab)
                test_setpoint_ab = True
                mysql_conn.mysql_add_message(f'уставка {list_ust_num[k]} дельта t: {calc_delta_t_ab:.0f}')
                mysql_conn.mysql_add_message(f'уставка {list_ust_num[k]} дельта %: {calc_delta_percent_ab:.0f}')
            else:
                test_setpoint_ab = False
            ctrl_kl.ctrl_relay('KL73', True)
            if my_msg(msg_4):
                pass
            else:
                return False
            progress_msg = (f'канал ВГ дельта t {k}')
            mysql_conn.mysql_ins_result(progress_msg, '2')
            calc_delta_t_vg = ctrl_kl.ctrl_ai_code_v0(109)
            if calc_delta_t_ab != 9999:
                pass
            else:
                return False
            list_delta_t_vg.append(calc_delta_t_vg)
            in_a1, in_a5 = self.__inputs_a()
            if in_a1 == True and in_a5 == False:
                # Δ%= 0,00004762*(U4)2+9,5648* U4
                progress_msg = (f'канал ВГ дельта % {k}')
                mysql_conn.mysql_ins_result(progress_msg, '2')
                meas_volt_vg = read_mb.read_analog()
                calc_delta_percent_vg = 0.00004762 * meas_volt_vg ** 2 + 9.5648 * meas_volt_vg
                list_delta_percent_vg.append(calc_delta_percent_vg)
                test_setpoint_vg = True
                mysql_conn.mysql_add_message(f'уставка {list_ust_num[k]} дельта t: {calc_delta_t_vg:.0f}')
                mysql_conn.mysql_add_message(f'уставка {list_ust_num[k]} дельта %: {calc_delta_percent_vg:.0f}')
            else:
                test_setpoint_vg = False
            ctrl_kl.ctrl_relay('KL73', False)
            if my_msg(msg_4):
                pass
            else:
                return False
            reset.stop_procedure_3()
            if test_setpoint_ab == True and test_setpoint_vg == True:
                k += 1
                continue
            elif test_setpoint_ab == False and test_setpoint_vg == False:
                progress_msg = (f'повышаем U уставки {k}')
                mysql_conn.mysql_ins_result(progress_msg, '2')
                if proc.procedure_1_25_35(coef_volt=coef_volt, setpoint_volt=i):
                    pass
                else:
                    mysql_conn.mysql_ins_result('неисправен', '2')
                    return False
                calc_delta_t_ab = ctrl_kl.ctrl_ai_code_v0(109)
                if calc_delta_t_ab != 9999:
                    pass
                else:
                    return False
                list_delta_t_ab[-1] = calc_delta_t_ab
                in_a1, in_a5 = self.__inputs_a()
                if in_a1 == True and in_a5 == False:
                    # Δ%= 0,00004762*(U4)2+9,5648* U4
                    meas_volt_ab = read_mb.read_analog()
                    calc_delta_percent_ab = 0.00004762 * meas_volt_ab ** 2 + 9.5648 * meas_volt_ab
                    list_delta_percent_ab[-1] = calc_delta_percent_ab
                    test_setpoint_ab = True
                    mysql_conn.mysql_add_message(f'уставка {list_ust_num[k]} дельта t: {calc_delta_t_ab:.0f}')
                else:
                    test_setpoint_ab = False
                ctrl_kl.ctrl_relay('KL73', True)
                if my_msg(msg_4):
                    pass
                else:
                    return False
                calc_delta_t_vg = ctrl_kl.ctrl_ai_code_v0(109)
                if calc_delta_t_ab != 9999:
                    pass
                else:
                    return False
                list_delta_t_vg[-1] = calc_delta_t_vg
                in_a1, in_a5 = self.__inputs_a()
                if in_a1 == True and in_a5 == False:
                    # Δ%= 0,00004762*(U4)2+9,5648* U4
                    meas_volt_vg = read_mb.read_analog()
                    calc_delta_percent_vg = 0.00004762 * meas_volt_vg ** 2 + 9.5648 * meas_volt_vg
                    list_delta_percent_vg[-1] = calc_delta_percent_vg
                    test_setpoint_vg = True
                    mysql_conn.mysql_add_message(f'уставка {list_ust_num[k]} дельта t: {calc_delta_t_vg:.0f}')
                    mysql_conn.mysql_add_message(f'уставка {list_ust_num[k]} дельта %: {calc_delta_percent_vg:.0f}')
                else:
                    test_setpoint_vg = False
                ctrl_kl.ctrl_relay('KL73', False)
                if my_msg(msg_4):
                    pass
                else:
                    return False
                reset.stop_procedure_3()
                if test_setpoint_ab == True and test_setpoint_vg == True:
                    k += 1
                    continue
                else:
                    return False
            elif test_setpoint_ab == False and test_setpoint_vg == True:
                if proc.procedure_1_25_35(coef_volt=coef_volt, setpoint_volt=i):
                    pass
                else:
                    mysql_conn.mysql_ins_result('неисправен', '2')
                    return False
                if my_msg(msg_4):
                    pass
                else:
                    return False
                calc_delta_t_ab = ctrl_kl.ctrl_ai_code_v0(109)
                if calc_delta_t_ab != 9999:
                    pass
                else:
                    return False
                list_delta_t_ab[-1] = calc_delta_t_ab
                in_a1, in_a5 = self.__inputs_a()
                if in_a1 == True and in_a5 == False:
                    # Δ%= 0,00004762*(U4)2+9,5648* U4
                    meas_volt_ab = read_mb.read_analog()
                    calc_delta_percent_ab = 0.00004762 * meas_volt_ab ** 2 + 9.5648 * meas_volt_ab
                    list_delta_percent_ab[-1] = calc_delta_percent_ab
                    test_setpoint_ab = True
                    mysql_conn.mysql_add_message(f'уставка {list_ust_num[k]} дельта t: {calc_delta_t_ab:.0f}')
                    mysql_conn.mysql_add_message(f'уставка {list_ust_num[k]} дельта %: {calc_delta_percent_ab:.0f}')
                else:
                    test_setpoint_ab = False
                reset.stop_procedure_3()
                if my_msg(msg_4):
                    pass
                else:
                    return False
                if test_setpoint_ab == True:
                    k += 1
                    continue
                else:
                    return False
            elif test_setpoint_ab == True and test_setpoint_vg == False:
                if proc.procedure_1_25_35(coef_volt=coef_volt, setpoint_volt=i):
                    pass
                else:
                    mysql_conn.mysql_ins_result('неисправен', '2')
                    return False
                ctrl_kl.ctrl_relay('KL73', True)
                if my_msg(msg_4):
                    pass
                else:
                    return False
                calc_delta_t_vg = ctrl_kl.ctrl_ai_code_v0(109)
                if calc_delta_t_ab != 9999:
                    pass
                else:
                    return False
                list_delta_t_vg[-1] = calc_delta_t_vg
                in_a1, in_a5 = self.__inputs_a()
                if in_a1 == True and in_a5 == False:
                    # Δ%= 0,00004762*(U4)2+9,5648* U4
                    meas_volt_vg = read_mb.read_analog()
                    calc_delta_percent_vg = 0.00004762 * meas_volt_vg ** 2 + 9.5648 * meas_volt_vg
                    list_delta_percent_vg[-1] = calc_delta_percent_vg
                    test_setpoint_vg = True
                    mysql_conn.mysql_add_message(f'уставка {list_ust_num[k]} дельта t: {calc_delta_t_vg:.0f}')
                    mysql_conn.mysql_add_message(f'уставка {list_ust_num[k]} дельта %: {calc_delta_percent_vg:.0f}')
                else:
                    test_setpoint_vg = False
                ctrl_kl.ctrl_relay('KL73', False)
                if my_msg(msg_4):
                    pass
                else:
                    return False
                reset.stop_procedure_3()
                if test_setpoint_vg == True:
                    k += 1
                    continue
                else:
                    return False
        mysql_conn.mysql_ins_result('исправен', '2')
        if my_msg(msg_4):
            pass
        else:
            return False
        in_a1, in_a5 = self.__inputs_a()
        if in_a1 == False and in_a5 == True:
            return True
        elif in_a1 == True:
            mysql_conn.mysql_error(480)
            return False
        elif in_a5 == False:
            mysql_conn.mysql_error(481)
            return False
    
    @staticmethod
    def __inputs_a():
        in_a1 = read_mb.read_discrete(1)
        in_a5 = read_mb.read_discrete(5)
        return in_a1, in_a5


if __name__ == '__main__':
    try:
        test_umz = TestUMZ()
        if test_umz.st_test_umz():
            for t in range(11):
                list_result.append((list_ust_num[t], list_delta_percent_ab[t], list_delta_t_ab[t],
                                    list_ust_num[t], list_delta_percent_vg[t], list_delta_t_vg[t]))
            mysql_conn.mysql_umz_result(list_result)
            mysql_conn.mysql_block_good()
            my_msg('Блок исправен')
        else:
            for t in range(len(list_delta_t_ab)):
                list_result.append((list_ust_num[t], list_delta_percent_ab[t], list_delta_t_ab[t],
                                    list_ust_num[t], list_delta_percent_vg[t], list_delta_t_vg[t]))
            mysql_conn.mysql_umz_result(list_result)
            mysql_conn.mysql_block_bad()
            my_msg('Блок неисправен')
    except OSError:
        my_msg("ошибка системы")
    except SystemError:
        my_msg("внутренняя ошибка")
    finally:
        reset.reset_all()
        exit()
