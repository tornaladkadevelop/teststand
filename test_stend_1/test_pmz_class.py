#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Алгоритм проверки

Тип блока	Производитель
ПМЗ	Нет производителя
ПМЗ	Углеприбор
ПМЗ-П	Нет производителя
ПМЗ-П	Пульсар

"""

__all__ = ["TestPMZ"]

from sys import exit
from time import sleep
from my_msgbox import *
from my_msgbox_2 import *
from gen_func_procedure import *
from gen_func_utils import *
from gen_mb_client import *
from gen_mysql_connect import *

proc = Procedure()
reset = ResetRelay()
resist = Resistor()
read_mb = ReadMB()
ctrl_kl = CtrlKL()
mysql_conn = MySQLConnect()
fault = Bug(True)

# Таблица уставок
# № уставки	1	2	3	4	5	6	7	8	9
# U2[i], В	75,4	92	114	125	141	156,4	172	182,4	196

list_ust_num = (1, 2, 3, 4, 5, 6, 7, 8, 9)
list_ust = (75.4, 92, 114, 125, 141, 156.4, 172, 182.4, 196)
list_delta_t = []
list_delta_percent = []
list_result = []


class TestPMZ(object):
    def __init__(self):
        pass

    def st_test_pmz(self):
        # reset.reset_all()
        msg_1 = "Убедитесь в отсутствии в панелях разъемов установленных блоков Подключите " \
                "блок ПМЗ в разъем Х14 на панели B"
        msg_2 = "Переключите тумблер режимов, расположенный на корпусе блока, в положение «Работа»"
        if my_msg(msg_1):
            if my_msg(msg_2):
                pass
            else:
                return False
        else:
            return False
        # Тест 1. Проверка исходного состояния блока:
        ctrl_kl.ctrl_relay('KL21', True)
        reset.sbros_zashit_kl30_1s5()
        fault.debug_msg("сброс защит", 3)
        in_a1, in_a2, in_a5 = self.__inputs_a()
        if in_a1 == False and in_a2 == False and in_a5 == True:
            pass
        else:
            mysql_conn.mysql_ins_result('неисправен', '1')
            fault.debug_msg("положение выходов блока не соответствует", 1)
            return False
        fault.debug_msg("положение выходов блока соответствует", 4)
        mysql_conn.mysql_ins_result('исправен', '1')
        ####################################################################################################################
        # Тест 2. Проверка работоспособности блока в режиме «Проверка»
        # Процедура 2.1. Проверка вероятности наличия короткого замыкания на входе измерительной цепи блока
        # 2.1.1. Проверка отсутствия вероятности возникновения межвиткового замыкания на стороне первичной обмотки TV1
        mysql_conn.mysql_ins_result('идет тест 2.1', '2')
        meas_volt_ust = proc.procedure_1_21_31()
        if meas_volt_ust != False:
            pass
        else:
            mysql_conn.mysql_ins_result("неисправен", "1")
            return False
        # 2.1.4. Проверка отсутствия короткого замыкания на входе измерительной части блока:
        fault.debug_msg("тест 2.1.4 начало\t", 3)
        mysql_conn.mysql_ins_result('идет тест 2.1.4', '2')
        ctrl_kl.ctrl_relay('KL63', True)
        sleep(1)
        min_volt = 0.4 * meas_volt_ust
        max_volt = 1.1 * meas_volt_ust
        meas_volt = read_mb.read_analog()
        fault.debug_msg(f'напряжение после включения KL63\t{meas_volt}\tдолжно быть от\t{min_volt}\tдо\t{max_volt}', 3)
        if min_volt <= meas_volt <= max_volt:
            pass
        else:
            mysql_conn.mysql_ins_result('неисправен', '2')
            mysql_conn.mysql_error(455)
            reset.sbros_kl63_proc_1_21_31()
            return False
        reset.sbros_kl63_proc_1_21_31()
        # Процедура 2.2. Процедура определения коэффициента отклонения фактического напряжения от номинального
        fault.debug_msg("тест 2.2 начало\t", 3)
        mysql_conn.mysql_ins_result('идет тест 2.2', '2')
        coef_volt = proc.procedure_1_22_32()
        if coef_volt != False:
            pass
        else:
            mysql_conn.mysql_ins_result('неисправен', '2')
            reset.stop_procedure_32()
            return False
        reset.stop_procedure_32()
        ##############################################################################
        # Сообщение	«Переключите тумблер на корпусе блока в положение «Проверка»     #
        ##############################################################################
        msg_3 = "Переключите тумблер на корпусе блока в положение «Проверка»"
        if my_msg(msg_3):
            pass
        else:
            return False
        # Процедура 2.3. Формирование нагрузочного сигнала U3:
        fault.debug_msg("тест 2.3 начало\t", 3)
        if proc.start_procedure_1():
            calc_volt = proc.start_procedure_212(coef_volt=coef_volt)
            if calc_volt != False:
                if proc.start_procedure_312(calc_volt=calc_volt):
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
        # 2.4.  Проверка срабатывания блока от сигнала нагрузки:
        ctrl_kl.ctrl_ai_code_v1(108)
        in_a1, in_a2, in_a5 = self.__inputs_a()
        if in_a1 == True and in_a2 == True and in_a5 == False:
            pass
        else:
            fault.debug_msg("положение выходов блока не соответствует", 1)
            reset.stop_procedure_3()
            mysql_conn.mysql_ins_result('неисправен', '2')
            return False
        fault.debug_msg("положение выходов блока соответствует", 4)
        reset.stop_procedure_3()
        # 2.4.2. Сброс защит после проверки
        reset.sbros_zashit_kl30_1s5()
        fault.debug_msg("сброс защит", 3)
        in_a1, in_a2, in_a5 = self.__inputs_a()
        if in_a1 == False and in_a2 == False and in_a5 == True:
            pass
        else:
            fault.debug_msg("положение выходов блока не соответствует", 1)
            mysql_conn.mysql_ins_result('неисправен', '2')
            return False
        fault.debug_msg("положение выходов блока соответствует", 4)
        mysql_conn.mysql_ins_result('исправен', '2')

        ##########################################################################################################
        # Тест 3. Проверка срабатывания блока по уставкам

        # Сообщение	«Переключите тумблер на корпусе блока в положение «Работа»
        msg_2 = "Переключите тумблер на корпусе блока в положение «Работа»"
        if my_msg(msg_2):
            pass
        else:
            return False
        k = 0
        for i in list_ust:
            msg_3 = (f'Установите регулятор уставок на блоке в положение\t{list_ust_num[k]}')
            msg_result = my_msg_2(msg_3)
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
                return False
            # Δ%= 0.0038*U42[i]+2.27* U4[i]
            meas_volt = read_mb.read_analog()
            calc_delta_percent = 0.0038 * meas_volt ** 2 + 2.27 * meas_volt
            list_delta_percent.append(calc_delta_percent)
            # 3.4.  Проверка срабатывания блока от сигнала нагрузки:
            calc_delta_t = ctrl_kl.ctrl_ai_code_v0(104)
            if calc_delta_t != 9999:
                pass
            else:
                mysql_conn.mysql_ins_result('неисправен', '3')
            fault.debug_msg(f'время срабатывания, мс\t{calc_delta_t}', 5)
            list_delta_t.append(calc_delta_t)
            mysql_conn.mysql_add_message(f'уставка {list_ust_num[k]} дельта t: {calc_delta_t:.0f}')
            mysql_conn.mysql_add_message(f'уставка {list_ust_num[k]} дельта %: {calc_delta_percent:.0f}')
            in_a1, in_a2, in_a5 = self.__inputs_a()
            if in_a1 == True and in_a2 == True and in_a5 == False:
                fault.debug_msg("положение выходов блока соответствует", 4)
                reset.stop_procedure_3()
                if self.__subtest_36():
                    k += 1
                    continue
                else:
                    return False
            else:
                fault.debug_msg("положение выходов блока не соответствует", 1)
                reset.stop_procedure_3()
                if self.__subtest_35(coef_volt=coef_volt, i=i, k=k):
                    if self.__subtest_36():
                        k += 1
                        continue
                    else:
                        mysql_conn.mysql_ins_result('неисправен', '3')
                        return False
                else:
                    mysql_conn.mysql_ins_result('неисправен', '3')
                    return False
        mysql_conn.mysql_ins_result('исправен', '3')
        return True

    def __subtest_35(self, coef_volt, i, k):
        # 3.5. Формирование нагрузочного сигнала 1,1*U3[i]:
        reset.sbros_zashit_kl30_1s5()
        fault.debug_msg("сброс защит", 3)
        in_a1, in_a2, in_a5 = self.__inputs_a()
        if in_a1 == False and in_a2 == False and in_a5 == True:
            pass
        else:
            fault.debug_msg("положение выходов блока не соответствует", 1)
            mysql_conn.mysql_ins_result('неисправен', '3')
            return False
        fault.debug_msg("положение выходов блока соответствует", 4)
        if proc.start_procedure_1():
            calc_volt = proc.start_procedure_25(coef_volt, i)
            if calc_volt != False:
                if proc.start_procedure_34(calc_volt=calc_volt, setpoint_volt=i):
                    pass
                else:
                    return False
            else:
                return False
        else:
            return False
        # Δ%= 0.0038*U42[i]+2.27* U4[i]
        meas_volt = read_mb.read_analog()
        calc_delta_percent = 0.0038 * meas_volt ** 2 + 2.27 * meas_volt
        list_delta_percent[-1] = calc_delta_percent
        calc_delta_t = ctrl_kl.ctrl_ai_code_v0(104)
        if calc_delta_t != 9999:
            pass
        else:
            mysql_conn.mysql_ins_result('неисправен', '3')
        fault.debug_msg(f'время срабатывания, мс\t{calc_delta_t}', 5)
        list_delta_t[-1] = calc_delta_t
        mysql_conn.mysql_add_message(f'уставка {list_ust_num[k]} дельта t: {calc_delta_t:.0f}')
        mysql_conn.mysql_add_message(f'уставка {list_ust_num[k]} дельта %: {calc_delta_percent:.0f}')
        in_a1, in_a2, in_a5 = self.__inputs_a()
        if in_a1 == True and in_a2 == True and in_a5 == False:
            pass
        else:
            fault.debug_msg("положение выходов блока не соответствует", 1)
            reset.stop_procedure_3()
            mysql_conn.mysql_ins_result('неисправен', '3')
            return False
        fault.debug_msg("положение выходов блока соответствует", 4)
        reset.stop_procedure_3()
        return True

    def __subtest_36(self):
        # 3.6. Сброс защит после проверки
        reset.sbros_zashit_kl30_1s5()
        fault.debug_msg("сброс защит", 3)
        in_a1, in_a2, in_a5 = self.__inputs_a()
        if in_a1 == False and in_a2 == False and in_a5 == True:
            pass
        else:
            fault.debug_msg("положение выходов блока не соответствует", 1)
            mysql_conn.mysql_ins_result('неисправен', '3')
            return False
        fault.debug_msg("положение выходов блока соответствует", 4)
        return True

    @staticmethod
    def __inputs_a():
        in_a1 = read_mb.read_discrete(1)
        in_a2 = read_mb.read_discrete(2)
        in_a5 = read_mb.read_discrete(5)
        return in_a1, in_a2, in_a5

    @staticmethod
    def __inputs_b():
        in_b0 = read_mb.read_discrete(8)
        return in_b0


if __name__ == '__main__':
    try:
        test_pmz = TestPMZ()
        if test_pmz.st_test_pmz():
            for t in range(9):
                list_result.append((list_ust[t], list_delta_percent[t], list_delta_t[t]))
            fault.debug_msg(list_result, 2)
            mysql_conn.mysql_pmz_result(list_result)
            mysql_conn.mysql_block_good()
            my_msg('Блок исправен')
        else:
            for t in range(len(list_delta_t)):
                list_result.append((list_ust[t], list_delta_percent[t], list_delta_t[t]))
            fault.debug_msg(list_result, 2)
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
