#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Алгоритм проверки

Тип блока	Производитель
ММТЗ-Д	Нет производителя
ММТЗ-Д	ДонЭнергоЗавод

"""

from sys import exit
from time import sleep
from gen_func_procedure import *
from gen_func_utils import *
from my_msgbox import *
from my_msgbox_2 import *
from gen_mb_client import *
from gen_mysql_connect import *

__all__ = ["TestMMTZD"]

reset = ResetRelay()
proc = Procedure()
read_mb = ReadMB()
ctrl_kl = CtrlKL()
mysql_conn = MySQLConnect()
fault = Bug(True)

# Таблица уставок №1
#
# № уставки	10	20	30	40	50
# i	1	2	3	4	5
# U2[i], В	7.7	16.5	25.4	31.9	39.4

list_ust_num = (10, 20, 30, 40, 50)
# ust = (7.7, 16.5, 25.4, 31.9, 39.4)
list_ust = (8.0, 16.5, 25.4, 31.9, 39.4)
list_num_yach_test_2 = ("3", "4", "5", "6", "7")
list_num_yach_test_3 = ("9", "10", "11", "12", "13")
list_ust_str = ('10', '20', '30', '40', '50')


class TestMMTZD(object):
    def __init__(self):
        pass
    
    def st_test_mmtz_d(self):
        # reset.reset_all()
        # Тест 1. Проверка исходного состояния блока:
    
        ############################################################################
        # Сообщение	Убедитесь в отсутствии в панелях разъемов установленных блоков.#
        # Подключите блок в разъем Х21 на панели С                                 #
        ############################################################################
    
        ################################################################################################
        # Сообщение	«Переключите тумблер режимов, расположенный на корпусе блока, в положение «Работа» #
        ################################################################################################
    
        msg_1 = "Убедитесь в отсутствии в панелях разъемов установленных блоков. " \
                "Подключите блок в разъем Х21 на панели С"
        msg_2 = "Переключите тумблер режимов, расположенный на корпусе блока, в положение «Работа»"
        if my_msg(msg_1):
            if my_msg(msg_2):
                pass
            else:
                return False
        else:
            return False
        ctrl_kl.ctrl_relay('KL33', True)
        reset.sbros_zashit_kl1()
        in_a1, in_a5 = self.__inputs_a()
        if in_a1 == True and in_a5 == True:
            fault.debug_msg("положение выходов блока соответствует", 3)
            pass
        elif in_a1 == False:
            fault.debug_msg("положение входа 1 не соответствует", 1)
            mysql_conn.mysql_error(412)
            mysql_conn.mysql_ins_result("неисправен", "1")
            return False
        elif in_a5 == False:
            fault.debug_msg("положение входа 5 не соответствует", 1)
            mysql_conn.mysql_error(413)
            mysql_conn.mysql_ins_result("неисправен", "1")
            return False
        # 1.1. Проверка вероятности наличия короткого замыкания на входе измерительной цепи блока
        meas_volt_ust = proc.procedure_1_21_31()
        if meas_volt_ust != False:
            pass
        else:
            mysql_conn.mysql_ins_result("неисправен", "1")
            return False
        # 1.1.2. Проверка отсутствия короткого замыкания на входе измерительной части блока:
        fault.debug_msg("тест 1.1.2 начало\t", 3)
        ctrl_kl.ctrl_relay('KL63', True)
        min_volt = 0.4 * meas_volt_ust
        max_volt = 1.1 * meas_volt_ust
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
        # 1.2. Определение коэффициента Кс отклонения фактического напряжения от номинального
        coef_volt = proc.procedure_1_22_32()
        fault.debug_msg(f'коэф. сети равен: {coef_volt}', 4)
        if coef_volt != False:
            pass
        else:
            mysql_conn.mysql_ins_result('неисправен', '1')
            return False
        mysql_conn.mysql_ins_result('исправен', '1')
        reset.stop_procedure_32()
        # Тест 2. Проверка срабатывания защиты II канала по уставкам
    
        ###############################################################################################
        # Сообщение	Установите регулятор уставок III канала, расположенного на блоке в положение «50» #
        ###############################################################################################
    
        ###############################################################################################
        # Сообщение	Установите регулятор уставок II канала, расположенного на блоке в положение [i]   #
        ###############################################################################################
    
        msg_3 = "Установите регулятор уставок III канала, расположенного на блоке в положение «50»"
        msg_4 = "Установите регулятор уставок II канала, расположенного на блоке в положение\t"
        if my_msg(msg_3):
            pass
        else:
            return False
        k = 0
        for i in list_ust:
            msg_result = my_msg_2(f'{msg_4} {list_ust_num[k]}')
            if msg_result == 0:
                pass
            elif msg_result == 1:
                return False
            elif msg_result == 2:
                mysql_conn.mysql_add_message(f'уставка {list_ust_num[k]} пропущена')
                k += 1
                continue
            if proc.start_procedure_1():
                calc_volt = proc.start_procedure_24(coef_volt, i)
                if calc_volt != False:
                    if proc.start_procedure_34(calc_volt=calc_volt, setpoint_volt=i):
                        pass
                    else:
                        mysql_conn.mysql_ins_result('неисправен TV1', '2')
                        return False
                else:
                    mysql_conn.mysql_ins_result('неисправен TV1', '2')
                    return False
            else:
                mysql_conn.mysql_ins_result('неисправен TV1', '2')
                return False
            # 2.1.  Проверка срабатывания блока от сигнала нагрузки:
            ctrl_kl.ctrl_ai_code_v1(106)
            sleep(3)
            in_a1, in_a5 = self.__inputs_a()
            if in_a1 == False and in_a5 == False:
                fault.debug_msg("положение выходов блока соответствует", 3)
                reset.stop_procedure_3()
                if self.__subtest_25():
                    mysql_conn.mysql_ins_result('исправен', list_num_yach_test_2[k])
                else:
                    mysql_conn.mysql_ins_result('неисправен', list_num_yach_test_2[k])
                    return False
            elif in_a1 == True:
                if self.__subtest_22(coef_volt, i):
                    mysql_conn.mysql_ins_result('исправен', list_num_yach_test_2[k])
                else:
                    mysql_conn.mysql_ins_result('неисправен', '2')
                    mysql_conn.mysql_error(415)
                    mysql_conn.mysql_ins_result('неисправен', list_num_yach_test_2[k])
                    return False
            elif in_a5 == True:
                if self.__subtest_22(coef_volt, i):
                    mysql_conn.mysql_ins_result('исправен', list_num_yach_test_2[k])
                else:
                    mysql_conn.mysql_ins_result('неисправен', '2')
                    mysql_conn.mysql_error(416)
                    mysql_conn.mysql_ins_result('неисправен', list_num_yach_test_2[k])
                    return False
            k += 1
        mysql_conn.mysql_ins_result('исправен', '2')
        # Тест 3. Проверка срабатывания защиты III канала по уставкам
        ctrl_kl.ctrl_relay('KL73', True)
        sleep(5)
        ####################################################################################
        # Установите регулятор уставок II канала, расположенного на блоке в положение «50» #
        ####################################################################################
    
        ####################################################################################
        # Установите регулятор уставок III канала, расположенного на блоке в положение [i] #
        ####################################################################################
    
        msg_5 = "Установите регулятор уставок II канала, расположенного на блоке в положение «50»"
        msg_6 = "Установите регулятор уставок III канала, расположенного на блоке в положение\t"
        if my_msg(msg_5):
            pass
        else:
            return False
        x = 0
        for y in list_ust:
            msg_result = my_msg_2(f'{msg_6} {list_ust_num[x]}')
            if msg_result == 0:
                pass
            elif msg_result == 1:
                return False
            elif msg_result == 2:
                mysql_conn.mysql_add_message(f'уставка {list_ust_num[x]} пропущена')
                x += 1
                continue
            if proc.start_procedure_1():
                calc_volt = proc.start_procedure_24(coef_volt, y)
                if proc.start_procedure_34(calc_volt=calc_volt, setpoint_volt=y):
                    pass
                else:
                    mysql_conn.mysql_ins_result('неисправен', '3')
                    return False
            else:
                mysql_conn.mysql_ins_result('неисправен', '3')
            # opc['Устройство.tg.in_vtor_gl_kont_KL63'] = True
            # sleep(0.08)
            # opc['Устройство.tg.in_vtor_gl_kont_KL63'] = False
            ctrl_kl.ctrl_ai_code_v1(106)
            sleep(3)
            in_a1, in_a5 = self.__inputs_a()
            if in_a1 == False and in_a5 == False:
                reset.stop_procedure_3()
                if self.__subtest_35():
                    mysql_conn.mysql_ins_result('исправен', list_num_yach_test_3[x])
                else:
                    mysql_conn.mysql_ins_result('неисправен', list_num_yach_test_3[x])
                    return False
            elif in_a1 == True:
                if self.__subtest_32(coef_volt, y):
                    mysql_conn.mysql_ins_result('исправен', list_num_yach_test_3[x])
                else:
                    mysql_conn.mysql_ins_result('неисправен', '3')
                    mysql_conn.mysql_error(419)
                    mysql_conn.mysql_ins_result('неисправен', list_num_yach_test_3[x])
                    return False
            elif in_a5 == True:
                if self.__subtest_32(coef_volt, y):
                    mysql_conn.mysql_ins_result('исправен', list_num_yach_test_3[x])
                else:
                    mysql_conn.mysql_ins_result('неисправен', '3')
                    mysql_conn.mysql_error(420)
                    mysql_conn.mysql_ins_result('неисправен', list_num_yach_test_3[x])
                    return False
            x += 1
        mysql_conn.mysql_ins_result('исправен', '8')
        return True
    
    def __subtest_22(self, coef_volt, i):
        # 2.2. Формирование нагрузочного сигнала 1,1*calc_volt[i]:
        reset.sbros_zashit_kl1()
        in_a1, in_a5 = self.__inputs_a()
        if in_a1 == True and in_a5 == True:
            pass
        elif in_a1 == False:
            mysql_conn.mysql_ins_result('неисправен', '2')
            mysql_conn.mysql_error(417)
            return False
        elif in_a5 == False:
            mysql_conn.mysql_ins_result('неисправен', '2')
            mysql_conn.mysql_error(418)
            return False
        if proc.start_procedure_1():
            calc_volt = proc.start_procedure_25(coef_volt, i)
            if calc_volt != False:
                if proc.start_procedure_35(calc_volt=calc_volt, setpoint_volt=i):
                    pass
                else:
                    mysql_conn.mysql_ins_result('неисправен', '2')
            else:
                mysql_conn.mysql_ins_result('неисправен', '2')
        else:
            mysql_conn.mysql_ins_result('неисправен', '2')
        # 2.2.2.  Проверка срабатывания блока от сигнала нагрузки:
        ctrl_kl.ctrl_ai_code_v1(107)
        sleep(3)
        in_a1, in_a5 = self.__inputs_a()
        if in_a1 == False and in_a5 == False:
            reset.stop_procedure_3()
            if self.__subtest_25():
                return True
            else:
                return False
        elif in_a1 == True:
            mysql_conn.mysql_ins_result('неисправен', '2')
            mysql_conn.mysql_error(415)
            if self.__subtest_23():
                return True
            else:
                return False
        elif in_a5 == True:
            mysql_conn.mysql_ins_result('неисправен', '2')
            mysql_conn.mysql_error(416)
            if self.__subtest_23():
                return True
            else:
                return False
    
    def __subtest_23(self):
        # 2.3. Сброс защит после проверки
        reset.sbros_zashit_kl1()
        in_a1, in_a5 = self.__inputs_a()
        if in_a1 == True and in_a5 == True:
            return True
        elif in_a1 == False:
            mysql_conn.mysql_ins_result('неисправен', '2')
            mysql_conn.mysql_error(417)
            return False
        elif in_a5 == False:
            mysql_conn.mysql_ins_result('неисправен', '2')
            mysql_conn.mysql_error(418)
            return False
    
    def __subtest_25(self):
        # 2.5. Сброс защит после проверки
        reset.sbros_zashit_kl1()
        in_a1, in_a5 = self.__inputs_a()
        if in_a1 == True and in_a5 == True:
            return True
        elif in_a1 == False:
            mysql_conn.mysql_ins_result('неисправен', '2')
            mysql_conn.mysql_error(417)
            return False
        elif in_a5 == False:
            mysql_conn.mysql_ins_result('неисправен', '2')
            mysql_conn.mysql_error(418)
            return False
    
    def __subtest_32(self, coef_volt, y):
        # 3.2. Формирование нагрузочного сигнала 1,1*calc_volt[i]:
        reset.sbros_zashit_kl1()
        in_a1, in_a5 = self.__inputs_a()
        if in_a1 == True and in_a5 == True:
            pass
        elif in_a1 == False:
            mysql_conn.mysql_ins_result('неисправен', '3')
            mysql_conn.mysql_error(417)
            return False
        elif in_a5 == False:
            mysql_conn.mysql_ins_result('неисправен', '3')
            mysql_conn.mysql_error(418)
            return False
        if proc.start_procedure_1():
            calc_volt = proc.start_procedure_25(coef_volt, y)
            if proc.start_procedure_35(calc_volt=calc_volt, setpoint_volt=y):
                pass
            else:
                mysql_conn.mysql_ins_result('неисправен', '3')
                return False
        else:
            mysql_conn.mysql_ins_result('неисправен', '3')
            return False
        # 2.2.2.  Проверка срабатывания блока от сигнала нагрузки:
        ctrl_kl.ctrl_ai_code_v1(107)
        sleep(3)
        in_a1, in_a5 = self.__inputs_a()
        if in_a1 == False and in_a5 == False:
            reset.stop_procedure_3()
            if self.__subtest_35():
                return True
            else:
                return False
        elif in_a1 == True:
            mysql_conn.mysql_ins_result('неисправен', '3')
            mysql_conn.mysql_error(419)
            if self.__subtest_33():
                return True
            else:
                return False
        elif in_a5 == True:
            mysql_conn.mysql_ins_result('неисправен', '3')
            mysql_conn.mysql_error(420)
            if self.__subtest_33():
                return True
            else:
                return False
    
    def __subtest_33(self):
        # 2.3. Сброс защит после проверки
        reset.sbros_zashit_kl1()
        in_a1, in_a5 = self.__inputs_a()
        if in_a1 == True and in_a5 == True:
            return True
        elif in_a1 == False:
            mysql_conn.mysql_ins_result('неисправен', '3')
            mysql_conn.mysql_error(417)
            return False
        elif in_a5 == False:
            mysql_conn.mysql_ins_result('неисправен', '3')
            mysql_conn.mysql_error(418)
            return False
    
    def __subtest_35(self):
        # 2.5. Сброс защит после проверки
        reset.sbros_zashit_kl1()
        in_a1, in_a5 = self.__inputs_a()
        if in_a1 == True and in_a5 == True:
            return True
        elif in_a1 == False:
            mysql_conn.mysql_ins_result('неисправен', '3')
            mysql_conn.mysql_error(417)
            return False
        elif in_a5 == False:
            mysql_conn.mysql_ins_result('неисправен', '3')
            mysql_conn.mysql_error(418)
            return False
    
    @staticmethod
    def __inputs_a():
        in_a1 = read_mb.read_discrete(1)
        in_a5 = read_mb.read_discrete(5)
        return in_a1, in_a5
    

if __name__ == '__main__':
    try:
        test_mmtz_d = TestMMTZD()
        if test_mmtz_d.st_test_mmtz_d():
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
