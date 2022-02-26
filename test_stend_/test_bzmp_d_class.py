#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Алгоритм проверки

Тип блока	Производитель
БЗМП-Д	ДИГ, ООО

"""

__all__ = ["TestBZMPD"]

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

# U2 =22.6В.
ust_1 = 22.6
# U2 =15В.
ust_2 = 15.0


class TestBZMPD(object):
    def __init__(self):
        pass
    
    def st_test_bzmp_d(self):
        # reset.reset_all()
        mysql_conn.mysql_ins_result('идёт тест 1.1', '1')
        mysql_conn.mysql_ins_result('---', '2')
        mysql_conn.mysql_ins_result('---', '3')
        mysql_conn.mysql_ins_result('---', '4')
        mysql_conn.mysql_ins_result('---', '5')
        # Тест 1. Проверка исходного состояния блока:
        # Сообщение	«Убедитесь в отсутствии других блоков и подключите блок БЗМП-Д к испытательной панели»
        msg_1 = "Убедитесь в отсутствии других блоков и подключите блок БЗМП-Д к испытательной панели"
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
        mysql_conn.mysql_ins_result('идёт тест 1.2', '1')
        coef_volt = proc.procedure_1_22_32()
        if coef_volt != False:
            pass
        else:
            mysql_conn.mysql_ins_result("неисправен TV1", "1")
            return False
        reset.stop_procedure_32()
        # Подача напряжения питания ~50В
        mysql_conn.mysql_ins_result('идёт тест 1.3', '1')
        mb_ctrl.ctrl_relay('KL67', True)
        timer_test_1 = 0
        start_timer_test_1 = time()
        while timer_test_1 <= 120:
            mb_ctrl.ctrl_relay('KL24', True)
            # in_a1 == False and in_a5 == False and in_a6 == True and
            sleep(0.2)
            mb_ctrl.ctrl_relay('KL24', False)
            timer_test_1 = time() - start_timer_test_1
            in_a1, in_a5, in_a6 = self.__inputs_a()
            fault.debug_msg(f'времени прошло\t{timer_test_1:.2f}', 2)
            if in_a1 == True and in_a5 == True and in_a6 == False:
                break
            else:
                # fault.debug_msg("положение выходов не соответствует", 1)
                # return False
                continue
        in_a1, in_a5, in_a6 = self.__inputs_a()
        if in_a1 == True and in_a5 == True and in_a6 == False:
            pass
        else:
            fault.debug_msg("тест 1.2 положение выходов не соответствует", 1)
            mysql_conn.mysql_ins_result("неисправен", "1")
            return False
        fault.debug_msg("тест 1.2 положение выходов соответствует", 4)
        mysql_conn.mysql_ins_result("исправен", "1")
        # Тест 2. Проверка срабатывания блока при снижении изоляции цепей 36В
        # Сообщение	«С помощью кнопок SB1…SB3, расположенных на панели разъемов, установите следующие
        # параметры блока, при их наличии в зависимости от исполнения блока:
        # - Номинальный ток: 160А (все исполнения);
        # - Кратность пускового тока: 7.5 (все исполнения);
        # - Номинальное рабочее напряжение: 1140В (все исполнения);
        # - Перекос фаз по току: 0% (все исполнения);
        # - Датчик тока: ДТК-1 (некоторые исполнения);
        # - Режим работы:
        # пускатель (некоторые исполнения) или
        # БРУ ВКЛ, БКИ ВКЛ (некоторые исполнения)
        #
        #
        # Сообщение	«С помощью кнопки SB3 перейдите в главное окно меню блока»
        msg_2 = "С помощью кнопок SB1…SB3, расположенных на панели разъемов, установите следующие параметры блока, " \
                "при их наличии в зависимости от исполнения блока:\n" \
                "- Номинальный ток: 160А (все исполнения);- Кратность пускового тока: 7.5 (все исполнения);\n" \
                "- Номинальное рабочее напряжение: 1140В (все исполнения);\n" \
                "- Перекос фаз по току: 0% (все исполнения); - Датчик тока: ДТК-1 (некоторые исполнения);\n" \
                "- Режим работы: пускатель (некоторые исполнения) или БРУ ВКЛ, БКИ ВКЛ (некоторые исполнения)"
        msg_3 = "С помощью кнопки SB3 перейдите в главное окно меню блока"
        if my_msg(msg_2):
            if my_msg(msg_3):
                pass
            else:
                return False
        else:
            return False
        mysql_conn.mysql_ins_result('идёт тест 2.1', '2')
        mb_ctrl.ctrl_relay('KL21', True)
        sleep(1)
        mb_ctrl.ctrl_relay('KL84', True)
        sleep(5)
        mb_ctrl.ctrl_relay('KL84', False)
        sleep(0.2)
        in_a6 = self.__inputs_a6()
        if in_a6 == True:
            pass
        else:
            fault.debug_msg("тест 2.1 положение выходов не соответствует", 1)
            mysql_conn.mysql_ins_result("неисправен", "2")
            return False
        fault.debug_msg("тест 2.1 положение выходов соответствует", 4)
        # 2.2. Сброс защит после проверки
        mysql_conn.mysql_ins_result('идёт тест 2.2', '2')
        mb_ctrl.ctrl_relay('KL24', True)
        sleep(0.3)
        mb_ctrl.ctrl_relay('KL24', False)
        sleep(0.7)
        in_a1, in_a5, in_a6 = self.__inputs_a()
        if in_a1 == True and in_a5 == True and in_a6 == False:
            pass
        else:
            fault.debug_msg("тест 2.2 положение выходов не соответствует", 1)
            mysql_conn.mysql_ins_result("неисправен", "2")
            return False
        mysql_conn.mysql_ins_result("исправен", "2")
        fault.debug_msg("тест 2.2 положение выходов соответствует", 4)
        # Тест 3. Проверка срабатывания блока при снижении силовой изоляции
        # Сообщение	«С помощью кнопки SB3 перейдите в главное окно меню блока»
        msg_4 = "С помощью кнопки SB3 перейдите в главное окно меню блока"
        if my_msg(msg_4):
            pass
        else:
            return False
        mysql_conn.mysql_ins_result('идёт тест 3.1', '3')
        resist.resist_kohm(61)
        sleep(2)
        in_a1, in_a5, in_a6 = self.__inputs_a()
        if in_a1 == False and in_a5 == False and in_a6 == True:
            pass
        else:
            fault.debug_msg("тест 3 положение выходов не соответствует", 1)
            mysql_conn.mysql_ins_result("неисправен", "3")
            return False
        fault.debug_msg("тест 3 положение выходов соответствует", 4)
        resist.resist_kohm(590)
        sleep(2)
        mysql_conn.mysql_ins_result('идёт тест 3.2', '3')
        mb_ctrl.ctrl_relay('KL24', True)
        sleep(0.3)
        mb_ctrl.ctrl_relay('KL24', False)
        sleep(0.7)
        in_a1, in_a5, in_a6 = self.__inputs_a()
        if in_a1 == True and in_a5 == True and in_a6 == False:
            pass
        else:
            fault.debug_msg("положение выходов не соответствует", 1)
            mysql_conn.mysql_ins_result("неисправен", "3")
            return False
        fault.debug_msg("тест 3 положение выходов соответствует", 4)
        mysql_conn.mysql_ins_result("исправен", "3")
        # Тест 4. Проверка защиты ПМЗ
        # Сообщение	«С помощью кнопки SB3 перейдите в главное окно меню блока»
        msg_5 = "С помощью кнопки SB3 перейдите в главное окно меню блока"
        if my_msg(msg_5):
            pass
        else:
            return False
        mysql_conn.mysql_ins_result('идёт тест 4.1', '4')
        if proc.start_procedure_1():
            calc_volt = proc.start_procedure_24(coef_volt=coef_volt, setpoint_volt=ust_1)
            if calc_volt != False:
                if proc.start_procedure_34(calc_volt=calc_volt, setpoint_volt=ust_1):
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
        mysql_conn.mysql_ins_result('идёт тест 4.2', '4')
        mb_ctrl.ctrl_relay('KL63', True)
        sleep(0.5)
        mb_ctrl.ctrl_relay('KL63', False)
        in_a1, in_a5, in_a6 = self.__inputs_a()
        if in_a1 == False and in_a5 == False and in_a6 == True:
            pass
        else:
            fault.debug_msg("положение выходов не соответствует", 1)
            mysql_conn.mysql_ins_result("неисправен", "4")
            reset.stop_procedure_3()
            return False
        fault.debug_msg("положение выходов соответствует", 4)
        reset.stop_procedure_3()
        mysql_conn.mysql_ins_result('идёт тест 4.3', '4')
        mb_ctrl.ctrl_relay('KL24', True)
        sleep(0.3)
        mb_ctrl.ctrl_relay('KL24', False)
        sleep(0.7)
        in_a1, in_a5, in_a6 = self.__inputs_a()
        if in_a1 == True and in_a5 == True and in_a6 == False:
            pass
        else:
            fault.debug_msg("положение выходов не соответствует", 1)
            mysql_conn.mysql_ins_result("неисправен", "4")
            return False
        fault.debug_msg("положение выходов соответствует", 4)
        mysql_conn.mysql_ins_result("исправен", "4")
        # Тест 5. Проверка защиты от перегрузки
        # Сообщение	«С помощью кнопки SB3 перейдите в главное окно меню блока»
        mysql_conn.mysql_ins_result('идёт тест 5.1', '5')
        if proc.start_procedure_1():
            calc_volt = proc.start_procedure_24(coef_volt=coef_volt, setpoint_volt=ust_2)
            if calc_volt != False:
                if proc.start_procedure_34(calc_volt=calc_volt, setpoint_volt=ust_2):
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
        # 5.2.  Проверка срабатывания блока от сигнала нагрузки:
        mysql_conn.mysql_ins_result('идёт тест 5.2', '5')
        mb_ctrl.ctrl_relay('KL63', True)
        in_b1 = self.__inputs_b()
        k = 0
        while in_b1 == False and k <= 10:
            in_b1 = self.__inputs_b()
            k += 1
        start_timer_test_5 = time()
        in_a5 = self.__inputs_a5()
        stop_timer = 0
        while in_a5 == True and stop_timer <= 360:
            in_a5 = self.__inputs_a5()
            sleep(0.2)
            stop_timer_test_5 = time() - start_timer_test_5
            fault.debug_msg(f'таймер тест 5: {stop_timer_test_5}', 2)
        stop_timer_test_5 = time()
        timer_test_5 = stop_timer_test_5 - start_timer_test_5
        fault.debug_msg(f'таймер тест 5: {timer_test_5}', 2)
        sleep(2)
        mysql_conn.mysql_ins_result('идёт тест 5.2', '5')
        in_a1, in_a5, in_a6 = self.__inputs_a()
        if in_a1 == False and in_a5 == False and in_a6 == True and timer_test_5 <= 360:
            pass
        else:
            fault.debug_msg("положение выходов не соответствует", 1)
            mysql_conn.mysql_ins_result("неисправен", "5")
            reset.sbros_kl63_proc_all()
            return False
        fault.debug_msg("положение выходов соответствует", 4)
        reset.sbros_kl63_proc_all()
        mysql_conn.mysql_ins_result('идёт тест 5.3', '5')
        self.__sbros_zashit()
        in_a1, in_a5, in_a6 = self.__inputs_a()
        if in_a1 == True and in_a5 == True and in_a6 == False:
            pass
        else:
            fault.debug_msg("положение выходов не соответствует", 1)
            mysql_conn.mysql_ins_result("неисправен", "5")
            return False
        fault.debug_msg("положение выходов соответствует", 4)
        mysql_conn.mysql_ins_result(f'исправен, {timer_test_5:.1f} сек', "5")
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
        test_bzmp_d = TestBZMPD()
        if test_bzmp_d.st_test_bzmp_d():
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
