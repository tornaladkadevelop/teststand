#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Тип блока     Производитель
БЗМП-П1	Пульсар
"""

from sys import exit
from time import sleep, time
from my_msgbox import *
from gen_func_procedure import *
from gen_func_utils import *
from gen_mb_client import *
from gen_mysql_connect import *

__all__ = ["TestBZMPP1"]

proc = Procedure()
reset = ResetRelay()
resist = Resistor()
read_mb = ReadMB()
mb_ctrl = CtrlKL()
mysql_conn = MySQLConnect()
fault = Bug(True)
ust = 14.64


class TestBZMPP1(object):
    def __init__(self):
        pass
    
    def st_test_bzmp_p1(self):
        # reset.reset_all()
        # Тест 1. Проверка исходного состояния блока:
        # Сообщение	«Убедитесь в отсутствии других блоков и вставьте блок БЗМП-П1 в соответствующий разъем»
        msg_1 = "Убедитесь в отсутствии других блоков и вставьте блок БЗМП-П1 в соответствующий разъем"
        if my_msg(msg_1):
            pass
        else:
            return False
        # 1.1.	Проверка вероятности наличия короткого замыкания на входе измерительной цепи блока
        meas_volt_ust = proc.procedure_1_21_31()
        if meas_volt_ust != False:
            pass
        else:
            mysql_conn.mysql_ins_result("неисправен TV1", "1")
            return False
        mb_ctrl.ctrl_relay('KL73', True)
        sleep(5)
        mb_ctrl.ctrl_relay('KL90', True)
        sleep(5)
        mb_ctrl.ctrl_relay('KL63', True)
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
        # 1.2. Определение коэффициента Кс отклонения фактического напряжения от номинального
        coef_volt = proc.procedure_1_22_32()
        if coef_volt != False:
            pass
        else:
            mysql_conn.mysql_ins_result("неисправен TV1", "1")
            return False
        reset.stop_procedure_32()
        # Подача напряжения питания ~50В	KL67 - ВКЛ
        # 	DQ3:5А - ВКЛ
        # 	Пауза 1000 мс
        mb_ctrl.ctrl_relay('KL67', True)
        # sleep(120)
        timer_test_1 = 0
        start_timer_test_1 = time()
        # in_a1, in_a6 = self.__inputs_a()
        while timer_test_1 <= 120:
            # in_a1 == False and in_a6 == True and
            sleep(0.2)
            timer_test_1 = time() - start_timer_test_1
            in_a1, in_a6 = self.__inputs_a()
            fault.debug_msg(f'времени прошло\t{timer_test_1}', 2)
            if in_a1 == True and in_a6 == False:
                break
            else:
                # fault.debug_msg("положение выходов не соответствует", 1)
                # return False
                continue
        in_a1, in_a6 = self.__inputs_a()
        if in_a1 == True and in_a6 == False:
            pass
        else:
            mysql_conn.mysql_ins_result("неисправен", "1")
            return False
        mysql_conn.mysql_ins_result("исправен", "1")
        # Тест 2. Проверка защиты ПМЗ
        # Сообщение	«С помощью кнопок SB1…SB3, расположенных на панели разъемов, установите следующие параметры блока:
        # - Iном=200А; Iпер=1.2; Iпуск=7.5»
        # Сообщение	«С помощью кнопок SB1…SB3 перейдите к окну на дисплее блока с надписью «Токи фаз»
        msg_2 = "С помощью кнопок SB1…SB3, расположенных на панели разъемов, " \
                "установите следующие параметры блока: - Iном=200А; Iпер=1.2; Iпуск=7.5»"
        msg_3 = "С помощью кнопок SB1…SB3 перейдите к окну на дисплее блока с надписью «Токи фаз»"
        if my_msg(msg_2):
            if my_msg(msg_3):
                pass
            else:
                return False
        else:
            return False
        if proc.start_procedure_1():
            calc_volt = proc.start_procedure_29(coef_volt=coef_volt)
            if calc_volt != False:
                if proc.start_procedure_38(calc_volt=calc_volt):
                    pass
                else:
                    mysql_conn.mysql_ins_result("неисправен TV1", "2")
                    return False
            else:
                mysql_conn.mysql_ins_result("неисправен TV1", "2")
                return False
        else:
            mysql_conn.mysql_ins_result("неисправен TV1", "2")
            return False
        mb_ctrl.ctrl_relay('KL63', True)
        sleep(0.5)
        mb_ctrl.ctrl_relay('KL63', False)
        sleep(1)
        in_a1, in_a6 = self.__inputs_a()
        if in_a1 == False and in_a6 == True:
            pass
        else:
            fault.debug_msg("положение выходов не соответствует", 1)
            mysql_conn.mysql_ins_result("неисправен", "2")
            reset.stop_procedure_3()
            return False
        reset.stop_procedure_3()
        # 2.4.2. Сброс защит после проверки
        self.__sbros_zashit()
        in_a1, in_a6 = self.__inputs_a()
        if in_a1 == True and in_a6 == False:
            pass
        else:
            fault.debug_msg("положение выходов не соответствует", 1)
            mysql_conn.mysql_ins_result("неисправен", "2")
            return False
        mysql_conn.mysql_ins_result("исправен", "2")
        # Тест 3. Проверка защиты от несимметрии фаз
        # Сообщение	«С помощью кнопок SB1…SB3 перейдите к окну на дисплее блока с надписью «Токи фаз»
        msg_4 = "С помощью кнопок SB1…SB3 перейдите к окну на дисплее блока с надписью «Токи фаз»"
        if my_msg(msg_4):
            pass
        else:
            return False
        if proc.start_procedure_1():
            calc_volt = proc.start_procedure_210(coef_volt=coef_volt)
            if calc_volt != False:
                if proc.start_procedure_39(calc_volt=calc_volt):
                    pass
                else:
                    mysql_conn.mysql_ins_result("неисправен TV1", "3")
                    return False
            else:
                mysql_conn.mysql_ins_result("неисправен TV1", "3")
                return False
        else:
            mysql_conn.mysql_ins_result("неисправен TV1", "3")
            return False
        mb_ctrl.ctrl_relay('KL81', True)
        sleep(0.1)
        mb_ctrl.ctrl_relay('KL63', True)
        in_b1 = self.__inputs_b()
        i = 0
        while in_b1 == False and i <= 10:
            in_b1 = self.__inputs_b()
            i += 1
        start_timer = time()
        in_a6 = self.__inputs_a6()
        stop_timer = 0
        while in_a6 == False and stop_timer <= 12:
            in_a6 = self.__inputs_a6()
            stop_timer = time() - start_timer
        timer_test_5_2 = stop_timer
        fault.debug_msg(f'таймер тест 3: {timer_test_5_2}', 2)
        in_a1, in_a6 = self.__inputs_a()
        if in_a1 == False and in_a6 == True and timer_test_5_2 <= 12:
            pass
        else:
            fault.debug_msg("положение выходов не соответствует", 1)
            mysql_conn.mysql_ins_result("неисправен", "3")
            reset.sbros_kl63_proc_all()
            mb_ctrl.ctrl_relay('KL81', False)
            return False
        reset.sbros_kl63_proc_all()
        mb_ctrl.ctrl_relay('KL81', False)
        # 3.5. Сброс защит после проверки
        mb_ctrl.ctrl_relay('KL24', True)
        sleep(4)
        mb_ctrl.ctrl_relay('KL24', False)
        sleep(0.7)
        in_a1, in_a6 = self.__inputs_a()
        if in_a1 == True and in_a6 == False:
            pass
        else:
            fault.debug_msg("положение выходов не соответствует", 1)
            mysql_conn.mysql_ins_result("неисправен", "5")
            return False
        mysql_conn.mysql_ins_result(f'исправен, {timer_test_5_2:.1f} сек', "3")
        # Тест 4. Проверка защиты от перегрузки
        # Сообщение	«С помощью кнопок SB1…SB3 перейдите к окну на дисплее блока с надписью «Токи фаз»
        msg_5 = "С помощью кнопок SB1…SB3 перейдите к окну на дисплее блока с надписью «Токи фаз»"
        if my_msg(msg_5):
            pass
        else:
            return False
        if proc.start_procedure_1():
            calc_volt = proc.start_procedure_24(coef_volt=coef_volt, setpoint_volt=ust)
            if calc_volt != False:
                if proc.start_procedure_34(calc_volt=calc_volt, setpoint_volt=ust):
                    pass
                else:
                    mysql_conn.mysql_ins_result("неисправен TV1", "4")
                    return False
            else:
                mysql_conn.mysql_ins_result("неисправен TV1", "4")
                return False
        else:
            mysql_conn.mysql_ins_result("неисправен TV1", "4")
            return False
        # 6.2.  Проверка срабатывания блока от сигнала нагрузки:
        mb_ctrl.ctrl_relay('KL63', True)
        in_b1 = self.__inputs_b()
        k = 0
        while in_b1 == False and k <= 10:
            in_b1 = self.__inputs_b()
            k += 1
        start_timer = time()
        in_a6 = self.__inputs_a6()
        stop_timer = 0
        while in_a6 == False and stop_timer <= 360:
            in_a6 = self.__inputs_a6()
            stop_timer = time() - start_timer
            fault.debug_msg(f'таймер тест 4: {stop_timer}', 2)
        timer_test_6_2 = stop_timer
        fault.debug_msg(f'таймер тест 4: {timer_test_6_2}', 2)
        in_a1, in_a6 = self.__inputs_a()
        if in_a1 == False and in_a6 == True and timer_test_6_2 <= 360:
            pass
        else:
            fault.debug_msg("положение выходов не соответствует", 1)
            mysql_conn.mysql_ins_result("неисправен", "4")
            reset.sbros_kl63_proc_all()
            return False
        reset.sbros_kl63_proc_all()
        # Выдаем сообщение: «Сработала защита от перегрузки»
        # 6.6. Сброс защит после проверки
        self.__sbros_zashit()
        in_a1, in_a6 = self.__inputs_a()
        if in_a1 == True and in_a6 == False:
            pass
        else:
            fault.debug_msg("положение выходов не соответствует", 1)
            mysql_conn.mysql_ins_result("неисправен", "4")
            return False
        mysql_conn.mysql_ins_result(f'исправен, {timer_test_6_2:.1f} сек', "4")
        return True
    
    def __sbros_zashit(self):
        mb_ctrl.ctrl_relay('KL24', True)
        sleep(3)
        mb_ctrl.ctrl_relay('KL24', False)
        sleep(0.7)
    
    @staticmethod
    def __inputs_a():
        in_a1 = read_mb.read_discrete(1)
        in_a6 = read_mb.read_discrete(6)
        return in_a1, in_a6
    
    @staticmethod
    def __inputs_a5():
        in_a5 = read_mb.read_discrete(5)
        return in_a5
    
    @staticmethod
    def __inputs_a6():
        in_a6 = read_mb.read_discrete(6)
        return in_a6
    
    @staticmethod
    def __inputs_b():
        in_a9 = read_mb.read_discrete(9)
        return in_a9


if __name__ == '__main__':
    try:
        test_bzmp_p1 = TestBZMPP1()
        if test_bzmp_p1.st_test_bzmp_p1():
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
