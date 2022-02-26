#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Алгоритм проверки

Тип блока	Производитель
БУЗ-2	Строй-энергомаш
БУЗ-2	ТЭТЗ-Инвест
БУЗ-2	нет производителя

"""

__all__ = ["TestBUZ2"]

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

ust_1 = 75.8
ust_2 = 20.3


class TestBUZ2(object):
    def __init__(self):
        pass
    
    def st_test_buz_2(self):
        # reset.reset_all()
        # Тест 1. Включение/выключение блока в нормальном режиме:
        # Сообщение	Убедитесь в отсутствии блоков в панелях разъемов.
        # Вставьте испытуемый блок БУЗ-2 в разъем Х17 на панели B.
        # Вставьте заведомо исправные блок БИ в разъем Х26  и блок БДЗ в разъем Х16, расположенные на панели B.
        msg_1 = "Убедитесь в отсутствии блоков в панелях разъемов. " \
                "Вставьте испытуемый блок БУЗ-2 в разъем Х17 на панели B."
        msg_2 = "Вставьте заведомо исправные блок БИ в разъем Х26  и блок БДЗ в разъем Х16, " \
                "расположенные на панели B."
        if my_msg(msg_1):
            if my_msg(msg_2):
                pass
            else:
                return False
        else:
            return False
        # 1.1.	Проверка вероятности наличия короткого замыкания на входе измерительной цепи блока
        fault.debug_msg("тестим шкаф", 3)
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
        fault.debug_msg("вычисляем коэффициент сети", 3)
        coef_volt = proc.procedure_1_22_32()
        if coef_volt != False:
            pass
        else:
            mysql_conn.mysql_ins_result("неисправен TV1", "1")
            return False
        reset.stop_procedure_32()
        fault.debug_msg("включаем хуеву тучу релюшек", 3)
        mb_ctrl.ctrl_relay('KL21', True)
        mb_ctrl.ctrl_relay('KL2', True)
        mb_ctrl.ctrl_relay('KL66', True)
        sleep(6)
        mb_ctrl.ctrl_relay('KL84', True)
        sleep(2)
        mb_ctrl.ctrl_relay('KL84', False)
        sleep(1)
        mb_ctrl.ctrl_relay('KL80', True)
        sleep(0.1)
        mb_ctrl.ctrl_relay('KL24', True)
        sleep(5)
        in_a1, in_a2 = self.__inputs_a()
        if in_a1 == True and in_a2 == True:
            pass
        else:
            fault.debug_msg("тест 1.3 положение выходов не соответствует", 1)
            mysql_conn.mysql_ins_result("неисправен", "1")
            return False
        fault.debug_msg("тест 1.3 положение выходов соответствует", 4)
        # 1.4.	Выключение блока
        sleep(1)
        mb_ctrl.ctrl_relay('KL80', False)
        sleep(0.1)
        mb_ctrl.ctrl_relay('KL24', False)
        sleep(5)
        in_a1, in_a2 = self.__inputs_a()
        if in_a1 == False and in_a2 == False:
            pass
        else:
            fault.debug_msg("тест 1.4 положение выходов не соответствует", 1)
            mysql_conn.mysql_ins_result("неисправен", "1")
            return False
        fault.debug_msg("тест 1.4 положение выходов соответствует", 4)
        mysql_conn.mysql_ins_result("исправен", "1")
        # Тест 2. Проверка работоспособности защиты МТЗ:
        # 2.1. Пуск блока
        fault.debug_msg("тест 2 начало", 3)
        mb_ctrl.ctrl_relay('KL66', False)
        sleep(0.3)
        mb_ctrl.ctrl_relay('KL82', True)
        sleep(0.3)
        mb_ctrl.ctrl_relay('KL66', True)
        msg_3 = "Установите с помощью кнопок SB1, SB2 следующие уровни уставок: ПМЗ – 2000 А; ТЗП – 400 А"
        if my_msg(msg_3):
            pass
        else:
            return False
        fault.debug_msg("включаем хуеву тучу релюшек", 3)
        mb_ctrl.ctrl_relay('KL66', False)
        sleep(1)
        mb_ctrl.ctrl_relay('KL82', False)
        sleep(1)
        mb_ctrl.ctrl_relay('KL66', True)
        sleep(1)
        mb_ctrl.ctrl_relay('KL84', True)
        sleep(2)
        mb_ctrl.ctrl_relay('KL84', False)
        sleep(1)
        mb_ctrl.ctrl_relay('KL80', True)
        sleep(0.1)
        mb_ctrl.ctrl_relay('KL24', True)
        sleep(2)
        in_a1, in_a2 = self.__inputs_a()
        if in_a1 == True and in_a2 == True:
            pass
        else:
            fault.debug_msg("тест 2.1 положение выходов не соответствует", 1)
            mysql_conn.mysql_ins_result("неисправен", "2")
            return False
        fault.debug_msg("тест 2.1 положение выходов соответствует", 4)
        if proc.start_procedure_1():
            calc_volt = proc.start_procedure_24(coef_volt=coef_volt, setpoint_volt=ust_1)
            if calc_volt != False:
                if proc.start_procedure_34(calc_volt=calc_volt, setpoint_volt=ust_1):
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
        sleep(2)
        in_a1, in_a2 = self.__inputs_a()
        if in_a1 == False and in_a2 == False:
            pass
        else:
            fault.debug_msg("тест 2.1 положение выходов не соответствует", 1)
            reset.stop_procedure_3()
            mysql_conn.mysql_ins_result("неисправен", "2")
            return False
        fault.debug_msg("тест 2.1 положение выходов соответствует", 4)
        reset.stop_procedure_3()
        # 2.3.  Финишные операции при положительном завершении теста:
        fault.debug_msg("включаем хуеву тучу релюшек", 3)
        mb_ctrl.ctrl_relay('KL80', False)
        mb_ctrl.ctrl_relay('KL24', False)
        sleep(6)
        mb_ctrl.ctrl_relay('KL84', True)
        sleep(2)
        mb_ctrl.ctrl_relay('KL84', False)
        sleep(1)
        mysql_conn.mysql_ins_result("исправен", "2")
        # Тест 3. Проверка работоспособности защиты ТЗП
        # 3.1. Пуск блока
        mb_ctrl.ctrl_relay('KL80', True)
        sleep(0.1)
        mb_ctrl.ctrl_relay('KL24', True)
        sleep(2)
        in_a1, in_a2 = self.__inputs_a()
        if in_a1 == True and in_a2 == True:
            pass
        else:
            fault.debug_msg("тест 3.1 положение выходов не соответствует", 1)
            mysql_conn.mysql_ins_result("неисправен", "3")
            return False
        fault.debug_msg("тест 3.1 положение выходов соответствует", 4)
        if proc.start_procedure_1():
            calc_volt = proc.start_procedure_24(coef_volt=coef_volt, setpoint_volt=ust_2)
            if calc_volt != False:
                if proc.start_procedure_34(calc_volt=calc_volt, setpoint_volt=ust_2):
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
        mb_ctrl.ctrl_relay('KL63', True)
        in_b1 = self.__inputs_b()
        k = 0
        while in_b1 == False and k <= 10:
            in_b1 = self.__inputs_b()
            k += 1
        start_timer = time()
        in_a1 = self.__inputs_a1()
        stop_timer = 0
        while in_a1 == True and stop_timer <= 360:
            in_a1 = self.__inputs_a1()
            stop_timer = time() - start_timer
            fault.debug_msg(f'таймер тест 3.2 {stop_timer}', 2)
        timer_test_3 = stop_timer
        in_a1, in_a2 = self.__inputs_a()
        if in_a1 == False and in_a2 == False and timer_test_3 <= 360:
            pass
        else:
            fault.debug_msg("тест 3.2 положение выходов не соответствует", 1)
            mysql_conn.mysql_ins_result("неисправен", "3")
            reset.sbros_kl63_proc_all()
            return False
        fault.debug_msg("тест 3.2 положение выходов соответствует", 4)
        reset.sbros_kl63_proc_all()
        mysql_conn.mysql_ins_result(f'исправен, {timer_test_3:.1f} сек', "3")
        return True
    
    @staticmethod
    def __inputs_a():
        in_a1 = read_mb.read_discrete(1)
        in_a2 = read_mb.read_discrete(2)
        return in_a1, in_a2
    
    @staticmethod
    def __inputs_a1():
        in_a1 = read_mb.read_discrete(1)
        return in_a1

    @staticmethod
    def __inputs_b():
        in_a9 = read_mb.read_discrete(9)
        return in_a9


if __name__ == '__main__':
    try:
        test_buz_2 = TestBUZ2()
        if test_buz_2.st_test_buz_2():
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
