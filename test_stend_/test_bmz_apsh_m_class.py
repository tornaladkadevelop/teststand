#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Алгоритм проверки

Тип блока	Производитель
БМЗ АПШ.М	Нет производителя
БМЗ АПШ.М	Электроаппарат-Развитие

"""

from sys import exit
from time import sleep
from gen_func_procedure import *
from gen_func_utils import *
from my_msgbox import *
from gen_mb_client import *
from gen_mysql_connect import *

__all__ = ["TestBMZAPSHM"]

proc = Procedure()
reset = ResetRelay()
ctrl_kl = CtrlKL()
read_mb = ReadMB()
mysql_conn = MySQLConnect()
fault = Bug(True)


class TestBMZAPSHM(object):
    def __init__(self):
        pass
    
    def st_test_bmz_apsh_m(self):
        # reset.reset_all()
        # Тест 1. Проверка исходного состояния блока:
        # Сообщение	«Убедитесь в отсутствии блоков во всех испытательных разъемах.
        # Вставьте блок в соответствующий испытательный разъем»
        msg_1 = "Убедитесь в отсутствии блоков во всех испытательных разъемах. " \
                "Вставьте блок в соответствующий испытательный разъем»"
        if my_msg(msg_1):
            pass
        else:
            return False
        fault.debug_msg("тест 1", 4)
        ctrl_kl.ctrl_relay('KL21', True)
        reset.sbros_zashit_kl30()
        in_a1, in_a2, in_a5, in_a6 = self.__inputs_a()
        if in_a1 == False and in_a5 == True and in_a2 == False and in_a6 == True:
            fault.debug_msg("состояние выходов соответствует", 3)
            pass
        else:
            mysql_conn.mysql_ins_result('неисправен', '1')
            if in_a1 == True:
                fault.debug_msg("вход 1 не соответствует", 1)
                mysql_conn.mysql_error(347)
            elif in_a5 == False:
                fault.debug_msg("вход 5 не соответствует", 1)
                mysql_conn.mysql_error(348)
            elif in_a2 == True:
                fault.debug_msg("вход 2 не соответствует", 1)
                mysql_conn.mysql_error(349)
            elif in_a6 == False:
                fault.debug_msg("вход 6 не соответствует", 1)
                mysql_conn.mysql_error(350)
            return False
        fault.debug_msg("тест 1.1", 4)
        # 1.1. Проверка вероятности наличия короткого замыкания на входе измерительной цепи блока
        meas_volt_ust = proc.procedure_1_21_31()
        if meas_volt_ust != False:
            pass
        else:
            mysql_conn.mysql_ins_result('неисправен', '1')
            return False
        fault.debug_msg("тест 1.1.2", 4)
        # 1.1.2. Проверка отсутствия короткого замыкания на входе измерительной части блока:
        ctrl_kl.ctrl_relay('KL63', True)
        meas_volt = read_mb.read_analog()
        fault.debug_msg(f'измеряем напряжение:\t {meas_volt}', 4)
        if 0.9 * meas_volt_ust <= meas_volt <= 1.1 * meas_volt_ust:
            fault.debug_msg("напряжение соответствует", 3)
            pass
        else:
            fault.debug_msg("напряжение не соответствует", 1)
            mysql_conn.mysql_ins_result('неисправен', '1')
            reset.sbros_kl63_proc_1_21_31()
            return False
        fault.debug_msg("тест 1.1.3", 4)
        # 1.1.3. Финишные операции отсутствия короткого замыкания на входе измерительной части блока::
        reset.sbros_kl63_proc_1_21_31()
        fault.debug_msg("тест 1.2", 4)
        # 1.2. Определение коэффициента Кс отклонения фактического напряжения от номинального
        coef_volt = proc.procedure_1_22_32()
        if coef_volt != False:
            pass
        else:
            mysql_conn.mysql_ins_result('неисправен', '1')
            return False
        fault.debug_msg(f'вычисляем коэффициент сети:\t {coef_volt}', 4)
        reset.stop_procedure_32()
        mysql_conn.mysql_ins_result('исправен', '1')
        fault.debug_msg("тест 1 завершен", 3)
        fault.debug_msg("тест 2", 4)
        # Тест 2. Проверка работы 1 канала блока
        if proc.start_procedure_1():
            calc_volt = proc.start_procedure_26(coef_volt)
            if calc_volt != False:
                if proc.start_procedure_33(calc_volt):
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
        fault.debug_msg("тест 2.1", 4)
        # 2.1.  Проверка срабатывания блока от сигнала нагрузки:
        ctrl_kl.ctrl_relay('KL63', True)
        sleep(3)
        ctrl_kl.ctrl_relay('KL63', False)
        sleep(1)
        in_a1, in_a2, in_a5, in_a6 = self.__inputs_a()
        if in_a1 == True and in_a5 == False and in_a2 == False and in_a6 == True:
            fault.debug_msg("выходы блока соответствуют", 3)
            pass
        else:
            mysql_conn.mysql_ins_result('неисправен', '2')
            if in_a1 == False:
                fault.debug_msg("вход 1 не соответствует", 1)
                mysql_conn.mysql_error(352)
            elif in_a5 == True:
                fault.debug_msg("вход 5 не соответствует", 1)
                mysql_conn.mysql_error(353)
            elif in_a2 == True:
                fault.debug_msg("вход 2 не соответствует", 1)
                mysql_conn.mysql_error(354)
            elif in_a6 == False:
                fault.debug_msg("вход 6 не соответствует", 1)
                mysql_conn.mysql_error(355)
            return False
        reset.stop_procedure_3()
        fault.debug_msg("тест 2.2", 4)
        # 2.2. Сброс защит после проверки
        reset.sbros_zashit_kl30()
        in_a1, in_a2, in_a5, in_a6 = self.__inputs_a()
        if in_a1 == False and in_a5 == True and in_a2 == False and in_a6 == True:
            fault.debug_msg("выхода блока соответствуют", 3)
            mysql_conn.mysql_ins_result('исправен', '2')
        else:
            mysql_conn.mysql_ins_result('неисправен', '2')
            if in_a1 == True:
                fault.debug_msg("вход 1 не соответствует", 1)
                mysql_conn.mysql_error(356)
            elif in_a5 == False:
                fault.debug_msg("вход 5 не соответствует", 1)
                mysql_conn.mysql_error(357)
            elif in_a2 == True:
                fault.debug_msg("вход 2 не соответствует", 1)
                mysql_conn.mysql_error(358)
            elif in_a6 == False:
                fault.debug_msg("вход 6 не соответствует", 1)
                mysql_conn.mysql_error(359)
            return False
        fault.debug_msg("тест 2 пройден", 3)
        fault.debug_msg("тест 3", 4)
        # Тест 4. Проверка работы 2 канала блока
        ctrl_kl.ctrl_relay('KL73', True)
        if proc.start_procedure_1():
            calc_volt = proc.start_procedure_26(coef_volt)
            if calc_volt != False:
                if proc.start_procedure_33(calc_volt):
                    pass
                else:
                    mysql_conn.mysql_ins_result('неисправен', '3')
                    return False
            else:
                mysql_conn.mysql_ins_result('неисправен', '3')
                return False
        else:
            mysql_conn.mysql_ins_result('неисправен', '3')
            return False
        ctrl_kl.ctrl_relay('KL63', True)
        sleep(3)
        ctrl_kl.ctrl_relay('KL63', False)
        sleep(1)
        in_a1, in_a2, in_a5, in_a6 = self.__inputs_a()
        if in_a1 == False and in_a5 == True and in_a2 == True and in_a6 == False:
            fault.debug_msg("состояние выходов соответствует", 3)
            pass
        else:
            mysql_conn.mysql_ins_result('неисправен', '3')
            if in_a1 == True:
                fault.debug_msg("вход 1 не соответствует", 1)
                mysql_conn.mysql_error(360)
            elif in_a5 == False:
                fault.debug_msg("вход 5 не соответствует", 1)
                mysql_conn.mysql_error(361)
            elif in_a2 == False:
                fault.debug_msg("вход 2 не соответствует", 1)
                mysql_conn.mysql_error(362)
            elif in_a6 == True:
                fault.debug_msg("вход 6 не соответствует", 1)
                mysql_conn.mysql_error(363)
            return False
        reset.stop_procedure_3()
        fault.debug_msg("тест 3.2", 4)
        # 3.2. Сброс защит после проверки
        reset.sbros_zashit_kl30()
        sleep(1)
        in_a1, in_a2, in_a5, in_a6 = self.__inputs_a()
        if in_a1 == False and in_a5 == True and in_a2 == False and in_a6 == True:
            fault.debug_msg("состояние выходов блока соответсвует", 3)
        else:
            mysql_conn.mysql_ins_result('неисправен', '3')
            if in_a1 == True:
                fault.debug_msg("вход 1 не соответствует", 1)
                mysql_conn.mysql_error(364)
            elif in_a5 == False:
                fault.debug_msg("вход 5 не соответствует", 1)
                mysql_conn.mysql_error(365)
            elif in_a2 == False:
                fault.debug_msg("вход 2 не соответствует", 1)
                mysql_conn.mysql_error(366)
            elif in_a6 == True:
                fault.debug_msg("вход 6 не соответствует", 1)
                mysql_conn.mysql_error(367)
            return False
        mysql_conn.mysql_ins_result('исправен', '3')
        return True
    
    @staticmethod
    def __inputs_a():
        in_a1 = read_mb.read_discrete(1)
        in_a2 = read_mb.read_discrete(2)
        in_a5 = read_mb.read_discrete(5)
        in_a6 = read_mb.read_discrete(6)
        return in_a1, in_a2, in_a5, in_a6


if __name__ == '__main__':
    try:
        test_bmz_apsh_m = TestBMZAPSHM()
        if test_bmz_apsh_m.st_test_bmz_apsh_m():
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
