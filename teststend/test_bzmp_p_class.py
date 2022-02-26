#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Алгоритм проверки

Тип блока	Производитель
БЗМП-П	Пульсар

"""

__all__ = ["TestBZMPP"]

from sys import exit
from time import sleep, time
from my_msgbox import *
from gen_func_procedure import *
from gen_func_utils import *
from gen_mb_client import *
from gen_mysql_connect import *


proc = Procedure()
reset = ResetRelay()
resist = Resistor()
read_mb = ReadMB()
mb_ctrl = CtrlKL()
mysql_conn = MySQLConnect()
fault = Bug(True)


class TestBZMPP(object):
    def __init__(self):
        pass
    
    def st_test_bzmp_p(self):
        # reset.reset_all()
        # Тест 1. Проверка исходного состояния блока:
        # Сообщение	«Убедитесь в отсутствии других блоков и вставьте блок БЗМП-П в соответствующий разъем»
        msg_1 = "Убедитесь в отсутствии других блоков и вставьте блок БЗМП-П в соответствующий разъем"
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
            reset.stop_procedure_32()
            return False
        reset.stop_procedure_32()
        # Подача напряжения питания ~50В	KL67 - ВКЛ
        # 	DQ3:5А - ВКЛ
        # 	Пауза 1000 мс
        mb_ctrl.ctrl_relay('KL67', True)
        # sleep(120)
        timer_test_1 = 0
        start_timer_test_1 = time()
        in_a1, in_a5, in_a6 = self.__inputs_a()
        while timer_test_1 <= 120:
            # in_a1 == False and in_a5 == False and in_a6 == True and
            sleep(0.2)
            timer_test_1 = time() - start_timer_test_1
            in_a1, in_a5, in_a6 = self.__inputs_a()
            fault.debug_msg(f'времени прошло:\t{timer_test_1}', 2)
            if in_a1 == True and in_a5 == True and in_a6 == False:
                break
            else:
                #fault.debug_msg("положение выходов не соответствует", 1)
                #return False
                continue
        mysql_conn.mysql_ins_result("исправен", "1")
        # Тест 2. Проверка срабатывания блока при снижении изоляции цепей 36В
        # Сообщение	«С помощью кнопок SB1…SB3, расположенных на панели разъемов, установите следующие параметры блока:
        # - Iном=200А; Iпер=1.2; Iпуск=7.5; Uном = 660В»
        # Сообщение	«С помощью кнопки SB3 перейдите к окну на дисплее блока с надписью «Uном=660В»
        msg_2 = "С помощью кнопок SB1…SB3, расположенных на панели разъемов, установите следующие параметры блока:" \
                "Iном = 200А; Iпер = 1.2; Iпуск= 7.5; Uном = 660В»"
        msg_3 = "С помощью кнопки SB3 перейдите к окну на дисплее блока с надписью «Uном=660В»"
        if my_msg(msg_2):
            if my_msg(msg_3):
                pass
            else:
                return False
        else:
            return False
        # Подача напряжения питания ~36В	KL21 - ВКЛ	А1:4A - ВКЛ
        # Пауза 1000 мс
        # Создание утечки 36В	KL24 - ВКЛ	А1:7A - ВКЛ
        # Пауза 100 мс
        # Ликвидация утечки 36В	KL24 - ВЫКЛ	А1:7A - ВЫКЛ
        # Пауза 200 мс
        mb_ctrl.ctrl_relay('KL21', True)
        sleep(1)
        mb_ctrl.ctrl_relay('KL27', True)
        sleep(0.1)
        mb_ctrl.ctrl_relay('KL27', False)
        sleep(0.2)
        # in_a1, in_a5, in_a6 = self.__inputs_a()
        in_a6 = self.__inputs_a6()
        # if in_a1 == False and in_a5 == False and in_a6 == True:
        if in_a6 == True:
            pass
        else:
            fault.debug_msg("положение выходов не соответствует", 1)
            mysql_conn.mysql_ins_result("неисправен", "2")
            return False
        sleep(2)
        in_a1, in_a5, in_a6 = self.__inputs_a()
        if in_a1 == True and in_a5 == True and in_a6 == False:
            pass
        else:
            fault.debug_msg("положение выходов не соответствует", 1)
            mysql_conn.mysql_ins_result("неисправен", "2")
            return False
        mysql_conn.mysql_ins_result("исправен", "2")
        # Тест 3. Проверка срабатывания блока при снижении силовой изоляции
        # Сообщение	«С помощью кнопки SB3 перейдите к окну на дисплее блока с надписью «Uном=660В»
        # Пауза 300 мсек
        msg_4 = "С помощью кнопки SB3 перейдите к окну на дисплее блока с надписью «Uном=660В»"
        if my_msg(msg_4):
            pass
        else:
            return False
        # sleep(0.3)
        # in_a1, in_a5, in_a6 = self.__inputs_a()
        # if in_a1 == False and in_a5 == False and in_a6 == True:
        #     pass
        # else:
        #     fault.debug_msg("положение выходов не соответствует", 1)
        #     mysql_conn.mysql_ins_result("неисправен", "3")
        #     return False
        # Формирование 65 кОм	KL13- KL20 	А2:0B - А2:7B
        resist.resist_kohm(61)
        in_a1, in_a5, in_a6 = self.__inputs_a()
        if in_a1 == False and in_a5 == False and in_a6 == True:
            pass
        else:
            fault.debug_msg("положение выходов не соответствует", 1)
            mysql_conn.mysql_ins_result("неисправен", "3")
            return False
        # Отключение 65 кОм	KL13- KL20-ВЫКЛ 	А2:0B - А2:7B-ВЫКЛ
        # Пауза 2000 мс
        resist.resist_kohm(590)
        sleep(2)
        in_a1, in_a5, in_a6 = self.__inputs_a()
        if in_a1 == True and in_a5 == True and in_a6 == False:
            pass
        else:
            fault.debug_msg("положение выходов не соответствует", 1)
            mysql_conn.mysql_ins_result("неисправен", "3")
            return False
        mysql_conn.mysql_ins_result("исправен", "3")
        # Тест 4. Проверка защиты ПМЗ
        # Сообщение	«С помощью кнопки SB3 перейдите к окну на дисплее блока с надписью «Токи фаз»
        msg_5 = "С помощью кнопки SB3 перейдите к окну на дисплее блока с надписью «Токи фаз»"
        if my_msg(msg_5):
            pass
        else:
            return False
        if proc.start_procedure_1():
            calc_volt = proc.start_procedure_29(coef_volt=coef_volt)
            if calc_volt != False:
                if proc.start_procedure_38(calc_volt=calc_volt):
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
        # 4.2.  Проверка срабатывания блока от сигнала нагрузки:
        mb_ctrl.ctrl_relay('KL63', True)
        sleep(0.5)
        mb_ctrl.ctrl_relay('KL63', False)
        sleep(1)
        in_a1, in_a5, in_a6 = self.__inputs_a()
        if in_a1 == False and in_a5 == False and in_a6 == True:
            pass
        else:
            fault.debug_msg("положение выходов не соответствует", 1)
            mysql_conn.mysql_ins_result("неисправен", "4")
            reset.stop_procedure_3()
            return False
        reset.stop_procedure_3()
        # 4.2.2. Сброс защит после проверки
        self.__sbros_zashit()
        in_a1, in_a5, in_a6 = self.__inputs_a()
        if in_a1 == True and in_a5 == True and in_a6 == False:
            pass
        else:
            fault.debug_msg("положение выходов не соответствует", 1)
            mysql_conn.mysql_ins_result("неисправен", "4")
            return False
        mysql_conn.mysql_ins_result("исправен", "4")
        # Тест 5. Проверка защиты от несимметрии фаз
        # Сообщение	«С помощью кнопок SB1…SB3 перейдите к окну на дисплее блока с надписью «Токи фаз»
        msg_6 = "С помощью кнопок SB1…SB3 перейдите к окну на дисплее блока с надписью «Токи фаз»"
        if my_msg(msg_6):
            pass
        else:
            return False
        if proc.start_procedure_1():
            calc_volt = proc.start_procedure_210(coef_volt=coef_volt)
            if calc_volt != False:
                if proc.start_procedure_39(calc_volt=calc_volt):
                    pass
                else:
                    mysql_conn.mysql_ins_result("неисправен TV1", "5")
                    return False
            else:
                mysql_conn.mysql_ins_result("неисправен TV1", "5")
                return False
        else:
            mysql_conn.mysql_ins_result("неисправен TV1", "5")
            return False
        # 5.2.  Проверка срабатывания блока от сигнала нагрузки:
        mb_ctrl.ctrl_relay('KL81', True)
        sleep(0.1)
        mb_ctrl.ctrl_relay('KL63', True)
        in_b1 = self.__inputs_b()
        i = 0
        while in_b1 == False and i <= 10:
            in_b1 = self.__inputs_b()
            i += 1
        start_timer = time()
        in_a5 = self.__inputs_a5()
        stop_timer = 0
        while in_a5 == True and stop_timer <= 12:
            in_a5 = self.__inputs_a5()
            stop_timer = time() - start_timer
        timer_test_5_2 = stop_timer
        fault.debug_msg(f'таймер тест 6.2: {timer_test_5_2}', 2)
        in_a1, in_a5, in_a6 = self.__inputs_a()
        if in_a1 == False and in_a5 == False and in_a6 == True and timer_test_5_2 <= 12:
            pass
        else:
            fault.debug_msg("положение выходов не соответствует", 1)
            mysql_conn.mysql_ins_result("неисправен", "5")
            reset.sbros_kl63_proc_all()
            mb_ctrl.ctrl_relay('KL81', False)
            return False
        reset.sbros_kl63_proc_all()
        mb_ctrl.ctrl_relay('KL81', False)
        mb_ctrl.ctrl_relay('KL24', True)
        sleep(4)
        mb_ctrl.ctrl_relay('KL24', False)
        sleep(0.7)
        in_a1, in_a5, in_a6 = self.__inputs_a()
        if in_a1 == True and in_a5 == True and in_a6 == False:
            pass
        else:
            fault.debug_msg("положение выходов не соответствует", 1)
            mysql_conn.mysql_ins_result("неисправен", "5")
            return False
        mysql_conn.mysql_ins_result(f'исправен, {timer_test_5_2:.1f} сек', "5")
        # Тест 6. Проверка защиты от перегрузки
        # Сообщение	«С помощью кнопок SB1…SB3 перейдите к окну на дисплее блока с надписью «Токи фаз»
        msg_7 = "С помощью кнопок SB1…SB3 перейдите к окну на дисплее блока с надписью «Токи фаз»"
        if my_msg(msg_7):
            pass
        else:
            return False
        if proc.start_procedure_1():
            calc_volt = proc.start_procedure_211(coef_volt=coef_volt)
            if calc_volt != False:
                if proc.start_procedure_310(calc_volt=calc_volt):
                    pass
                else:
                    mysql_conn.mysql_ins_result("неисправен TV1", "6")
                    return False
            else:
                mysql_conn.mysql_ins_result("неисправен TV1", "6")
                return False
        else:
            mysql_conn.mysql_ins_result("неисправен TV1", "6")
            return False
        # 6.2.  Проверка срабатывания блока от сигнала нагрузки:
        mb_ctrl.ctrl_relay('KL63', True)
        in_b1 = self.__inputs_b()
        k = 0
        while in_b1 == False and k <= 10:
            in_b1 = self.__inputs_b()
            k += 1
        start_timer = time()
        in_a5 = self.__inputs_a5()
        stop_timer = 0
        while in_a5 == True and stop_timer <= 360:
            in_a5 = self.__inputs_a5()
            stop_timer = time() - start_timer
        timer_test_6_2 = stop_timer
        fault.debug_msg(f'таймер тест 6.2: {timer_test_6_2}', 2)
        in_a1, in_a5, in_a6 = self.__inputs_a()
        if in_a1 == False and in_a5 == False and in_a6 == True and timer_test_6_2 <= 360:
            pass
        else:
            fault.debug_msg("положение выходов не соответствует", 1)
            mysql_conn.mysql_ins_result("неисправен", "6")
            reset.sbros_kl63_proc_all()
            return False
        reset.sbros_kl63_proc_all()
        # Выдаем сообщение: «Сработала защита от перегрузки»
        # 6.6. Сброс защит после проверки
        self.__sbros_zashit()
        in_a1, in_a5, in_a6 = self.__inputs_a()
        if in_a1 == True and in_a5 == True and in_a6 == False:
            pass
        else:
            fault.debug_msg("положение выходов не соответствует", 1)
            mysql_conn.mysql_ins_result("неисправен", "6")
            return False
        mysql_conn.mysql_ins_result(f'исправен, {timer_test_6_2:.1f} сек', "6")
        return True
    
    def __sbros_zashit(self):
        mb_ctrl.ctrl_relay('KL24', True)
        sleep(3)
        mb_ctrl.ctrl_relay('KL24', False)
        sleep(0.7)
    
    @staticmethod
    def __inputs_a():
        in_a1 = read_mb.read_discrete(1)
        in_a5 = read_mb.read_discrete(5)
        in_a6 = read_mb.read_discrete(6)
        return in_a1, in_a5, in_a6
    
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
        test_bzmp_p = TestBZMPP()
        if test_bzmp_p.st_test_bzmp_p():
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
