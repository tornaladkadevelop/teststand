#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Алгоритм проверки

Тип блока	Производитель
МТЗП-2	Frecon
"""

from sys import exit
from time import sleep, time
from gen_func_procedure import *
from gen_func_utils import *
from my_msgbox import *
from gen_mb_client import *
from gen_mysql_connect import *

__all__ = ["TestMTZP2"]

reset = ResetRelay()
proc = Procedure()
resist = Resistor()
read_mb = ReadMB()
ctrl_kl = CtrlKL()
mysql_conn = MySQLConnect()
fault = Bug(True)

# U2 =10.9В
# U2 =8,2В
# U2 =5,5В
ust_1 = 10.9 * 8.2
ust_2 = 8.2 * 8.2
ust_3 = 5.5 * 8.2

# list_delta_t_tzp = []
# list_delta_t_bmz = []
# list_bmz_result = []
# list_tzp_result = []


class TestMTZP2(object):
    def __init__(self):
        pass

    def st_test_mtzp_2(self):
        # reset.reset_all()
        # Сообщение	«Убедитесь в отсутствии других блоков и подключите блок МТЗП-2 в соответствующие разъемы»
        msg_1 = "Убедитесь в отсутствии других блоков и подключите блок МТЗП-2 в соответствующие разъемы"
        if my_msg(msg_1):
            pass
        else:
            return False
        fault.debug_msg('тест 1.1', 3)
        mysql_conn.mysql_ins_result("идёт тест 1.2", '1')
        meas_volt_ust = proc.procedure_1_21_31()
        if meas_volt_ust != False:
            pass
        else:
            return False
        ctrl_kl.ctrl_relay('KL73', True)
        sleep(5)
        ctrl_kl.ctrl_relay('KL91', True)
        sleep(5)
        ctrl_kl.ctrl_relay('KL63', True)
        meas_volt = read_mb.read_analog()
        fault.debug_msg(f'измеренное напряжение\t{meas_volt}', 2)
        if 0.8 * meas_volt_ust <= meas_volt <= 1.0 * meas_volt_ust:
            pass
        else:
            mysql_conn.mysql_ins_result('неисправен', '1')
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
        ctrl_kl.ctrl_relay('KL88', True)
        sleep(10)
        ctrl_kl.ctrl_relay('KL24', True)
        ctrl_kl.ctrl_relay('KL24', False)
        sleep(10)
        ctrl_kl.ctrl_relay('KL84', True)
        sleep(0.5)
        ctrl_kl.ctrl_relay('KL84', False)
        sleep(1)
        in_a1, in_b2 = self.__inputs_a1_b2()
        if in_b2 == True and in_a1 == False:
            pass
        else:
            fault.debug_msg('тест 1.3 положение выходов не соответствует', 1)
            mysql_conn.mysql_ins_result('неисправен', '1')
            return False
        mysql_conn.mysql_ins_result('исправен', '1')
        fault.debug_msg('тест 1.3 положение выходов соответствует', 4)
        # Тест 2. Пуск и стоп от выносного пульта:
        mysql_conn.mysql_ins_result('идёт тест 2.1', '2')
        ctrl_kl.ctrl_relay('KL92', True)
        sleep(1)
        ctrl_kl.ctrl_relay('KL93', True)
        sleep(0.5)
        ctrl_kl.ctrl_relay('KL93', False)
        sleep(2)
        in_a1, in_b2 = self.__inputs_a1_b2()
        if in_b2 == False and in_a1 == True:
            pass
        else:
            fault.debug_msg('тест 2.1 положение выходов не соответствует', 1)
            mysql_conn.mysql_ins_result('неисправен', '2')
            return False
        mysql_conn.mysql_ins_result('идёт тест 2.2', '2')
        fault.debug_msg('тест 2.1 положение выходов соответствует', 4)
        sleep(0.5)
        ctrl_kl.ctrl_relay('KL94', True)
        sleep(1)
        ctrl_kl.ctrl_relay('KL94', False)
        sleep(2)
        in_a1, in_b2 = self.__inputs_a1_b2()
        if in_b2 == True and in_a1 == False:
            pass
        else:
            fault.debug_msg('тест 2.2 положение выходов не соответствует', 1)
            mysql_conn.mysql_ins_result('неисправен', '2')
            return False
        fault.debug_msg('тест 2.2 положение выходов соответствует', 4)
        mysql_conn.mysql_ins_result('исправен', '2')
        # Тест 3. Пуск и стоп от пульта дистанционного управления:
        mysql_conn.mysql_ins_result('идёт тест 3.1', '3')
        resist.resist_ohm(0)
        sleep(1)
        ctrl_kl.ctrl_relay('KL12', True)
        sleep(0.5)
        in_a1, in_b2 = self.__inputs_a1_b2()
        if in_b2 == False and in_a1 == True:
            pass
        else:
            fault.debug_msg('тест 3.1 положение выходов не соответствует', 1)
            mysql_conn.mysql_ins_result('неисправен', '3')
            return False
        mysql_conn.mysql_ins_result('идёт тест 3.2', '3')
        fault.debug_msg('тест 3.1 положение выходов соответствует', 4)
        ctrl_kl.ctrl_relay('KL25', True)
        resist.resist_ohm(255)
        sleep(0.5)
        in_a1, in_b2 = self.__inputs_a1_b2()
        if in_b2 == False and in_a1 == True:
            pass
        else:
            fault.debug_msg('тест 3.2 положение выходов не соответствует', 1)
            mysql_conn.mysql_ins_result('неисправен', '3')
            return False
        fault.debug_msg('тест 3.2 положение выходов соответствует', 4)
        mysql_conn.mysql_ins_result('идёт тест 3.3', '3')
        ctrl_kl.ctrl_relay('KL12', False)
        sleep(0.2)
        ctrl_kl.ctrl_relay('KL12', True)
        in_a1, in_b2 = self.__inputs_a1_b2()
        if in_b2 == True and in_a1 == False:
            pass
        else:
            fault.debug_msg('тест 3.3 положение выходов не соответствует', 1)
            mysql_conn.mysql_ins_result('неисправен', '3')
            return False
        fault.debug_msg('тест 3.3 положение выходов соответствует', 4)
        ctrl_kl.ctrl_relay('KL12', False)
        ctrl_kl.ctrl_relay('KL25', False)
        resist.resist_ohm(255)
        mysql_conn.mysql_ins_result('исправен', '3')
        # Тест 4. Проверка защиты МТЗ-1
        # Сообщение	С помощью кнопок на лицевой панели установите следующие значения режима МТЗ-1:
        # - Защита введена: ДА;
        # - Уставка по току: 400А;
        # - Уставка по времени: 20 мс;
        # - Отключение КА – ДА.
        msg_2 = "С помощью кнопок на лицевой панели установите следующие значения режима МТЗ-1:\n " \
                "- Защита введена: ДА; - Уставка по току: 400А;\n" \
                " - Уставка по времени: 20 мс; - Отключение КА – ДА."
        if my_msg(msg_2):
            pass
        else:
            return False
        mysql_conn.mysql_ins_result('идёт тест 4.1', '4')
        resist.resist_ohm(0)
        ctrl_kl.ctrl_relay('KL12', True)
        sleep(0.5)
        in_a1, in_b2 = self.__inputs_a1_b2()
        if in_b2 == False and in_a1 == True:
            pass
        else:
            fault.debug_msg('тест 4.1 положение выходов не соответствует', 1)
            mysql_conn.mysql_ins_result('неисправен', '4')
            return False
        fault.debug_msg('тест 4.1 положение выходов соответствует', 4)
        if proc.procedure_1_24_34(setpoint_volt=ust_1, coef_volt=coef_volt):
            pass
        else:
            mysql_conn.mysql_ins_result('неисправен TV1', '4')
            return False
        # 4.2.  Проверка срабатывания блока от сигнала нагрузки:
        mysql_conn.mysql_ins_result('идёт тест 4.2', '4')
        ctrl_kl.ctrl_relay('KL63', True)
        sleep(0.5)
        ctrl_kl.ctrl_relay('KL63', False)
        in_a1, in_b2 = self.__inputs_a1_b2()
        if in_b2 == True and in_a1 == False:
            pass
        else:
            fault.debug_msg('тест 4.2 положение выходов не соответствует', 1)
            mysql_conn.mysql_ins_result('неисправен', '4')
            return False
        fault.debug_msg('тест 4.2 положение выходов соответствует', 4)
        reset.stop_procedure_3()
        ctrl_kl.ctrl_relay('KL12', False)
        ctrl_kl.ctrl_relay('KL24', True)
        sleep(0.5)
        ctrl_kl.ctrl_relay('KL24', False)
        sleep(0.5)
        ctrl_kl.ctrl_relay('KL84', True)
        sleep(0.5)
        ctrl_kl.ctrl_relay('KL84', False)
        mysql_conn.mysql_ins_result('исправен', '4')
        # Тест 5. Проверка защиты МТЗ-2
        # Сообщение	С помощью кнопок на лицевой панели установите следующие значения режима МТЗ-2:
        # - Защита введена: ДА;
        # - Уставка по току: 300А;
        # - Уставка по времени: 31000 мс;
        # - Отключение КА – ДА.
        msg_3 = "С помощью кнопок на лицевой панели установите следующие значения режима МТЗ-2:\n" \
                " - Защита введена: ДА; - Уставка по току: 300А; \n" \
                "- Уставка по времени: 31000 мс; - Отключение КА – ДА."
        if my_msg(msg_3):
            pass
        else:
            return False
        mysql_conn.mysql_ins_result('идёт тест 5.1', '5')
        resist.resist_ohm(0)
        sleep(1)
        ctrl_kl.ctrl_relay('KL12', True)
        sleep(1)
        ctrl_kl.ctrl_relay('KL25', True)
        sleep(1)
        resist.resist_ohm(255)
        sleep(0.5)
        in_a1, in_b2 = self.__inputs_a1_b2()
        if in_b2 == False and in_a1 == True:
            pass
        else:
            fault.debug_msg('тест 5.1 положение выходов не соответствует', 1)
            mysql_conn.mysql_ins_result('неисправен', '5')
            return False
        fault.debug_msg('тест 5.1 положение выходов соответствует', 4)
        mysql_conn.mysql_ins_result('идёт тест 5.2', '5')
        if proc.procedure_1_24_34(setpoint_volt=ust_2, coef_volt=coef_volt):
            pass
        else:
            mysql_conn.mysql_ins_result('неисправен TV1', '5')
            return False
        mysql_conn.mysql_ins_result('идёт тест 5.3', '5')
        ctrl_kl.ctrl_relay('KL63', True)
        start_timer = time()
        __timer = 0
        in_a1, in_b2 = self.__inputs_a1_b2()
        while (in_a1 == True or in_b2 == False) and __timer <= 41:
            sleep(0.2)
            in_a1, in_b2 = self.__inputs_a1_b2()
            __timer = time() - start_timer
            fault.debug_msg(f'времени прошло\t{__timer}', 2)
        in_a1, in_b2 = self.__inputs_a1_b2()
        if in_b2 == True and in_a1 == False and __timer <= 35:
            pass
        else:
            fault.debug_msg('тест 5.3 положение выходов не соответствует', 1)
            mysql_conn.mysql_ins_result('неисправен', '5')
            return False
        fault.debug_msg('тест 5.3 положение выходов соответствует', 4)
        ctrl_kl.ctrl_relay('KL63', False)
        reset.stop_procedure_3()
        ctrl_kl.ctrl_relay('KL12', False)
        ctrl_kl.ctrl_relay('KL25', False)
        resist.resist_ohm(255)
        ctrl_kl.ctrl_relay('KL24', True)
        sleep(0.5)
        ctrl_kl.ctrl_relay('KL24', False)
        sleep(0.5)
        ctrl_kl.ctrl_relay('KL84', True)
        sleep(0.5)
        ctrl_kl.ctrl_relay('KL84', False)
        mysql_conn.mysql_ins_result('исправен', '5')
        # Тест 6. Проверка защиты УМТЗ
        # Сообщение	С помощью кнопок на лицевой панели установите следующие значения режима УМТЗ:
        # - Защита введена: ДА;
        # - Уставка по току: 300А;
        # - Уставка по времени: 20 мс;
        # - Отключение КА – ДА.
        msg_4 = "С помощью кнопок на лицевой панели установите следующие значения режима УМТЗ: \n" \
                "- Защита введена: ДА; - Уставка по току: 300А; \n" \
                "- Уставка по времени: 20 мс; - Отключение КА – ДА."
        if my_msg(msg_4):
            pass
        else:
            return False
        mysql_conn.mysql_ins_result('идёт тест 6.1', '6')
        resist.resist_ohm(0)
        if proc.procedure_1_24_34(setpoint_volt=ust_2, coef_volt=coef_volt):
            pass
        else:
            mysql_conn.mysql_ins_result('неисправен TV1', '6')
            return False
        ctrl_kl.ctrl_relay('KL63', True)
        ctrl_kl.ctrl_relay('KL12', True)
        sleep(0.2)
        ctrl_kl.ctrl_relay('KL25', True)
        resist.resist_ohm(255)
        sleep(0.5)
        ctrl_kl.ctrl_relay('KL63', False)
        sleep(0.2)
        in_a1, in_b2 = self.__inputs_a1_b2()
        if in_b2 == True and in_a1 == False:
            pass
        else:
            reset.stop_procedure_3()
            fault.debug_msg('тест 6.1 положение выходов не соответствует', 1)
            mysql_conn.mysql_ins_result('неисправен', '6')
            return False
        fault.debug_msg('тест 6.1 положение выходов соответствует', 4)
        reset.stop_procedure_3()
        ctrl_kl.ctrl_relay('KL12', False)
        ctrl_kl.ctrl_relay('KL25', False)
        resist.resist_ohm(255)
        ctrl_kl.ctrl_relay('KL24', True)
        sleep(0.5)
        ctrl_kl.ctrl_relay('KL24', False)
        sleep(0.5)
        ctrl_kl.ctrl_relay('KL84', True)
        sleep(0.5)
        ctrl_kl.ctrl_relay('KL84', False)
        mysql_conn.mysql_ins_result('исправен', '6')
        # Тест 7. Проверка защиты МТЗ-3
        # Сообщение	С помощью кнопок на лицевой панели установите следующие значения режима МТЗ-3:
        # - Защита введена: ДА;
        # - Уставка по току: 200А;
        # - Уставка по времени: 60000 мс;
        # - Отключение КА – ДА.
        msg_5 = "С помощью кнопок на лицевой панели установите следующие значения режима МТЗ-3: \n" \
                "- Защита введена: ДА; - Уставка по току: 200А; \n" \
                "- Уставка по времени: 60000 мс; - Отключение КА – ДА."
        if my_msg(msg_5):
            pass
        else:
            return False
        mysql_conn.mysql_ins_result('идёт тест 7.1', '7')
        resist.resist_ohm(0)
        sleep(1)
        ctrl_kl.ctrl_relay('KL12', True)
        sleep(1)
        ctrl_kl.ctrl_relay('KL25', True)
        sleep(1)
        resist.resist_ohm(255)
        sleep(1)
        in_a1, in_b2 = self.__inputs_a1_b2()
        if in_b2 == False and in_a1 == True:
            pass
        else:
            fault.debug_msg('тест 7.1 положение выходов не соответствует', 1)
            mysql_conn.mysql_ins_result('неисправен', '7')
            return False
        fault.debug_msg('тест 7.1 положение выходов соответствует', 4)
        if proc.procedure_1_24_34(setpoint_volt=ust_3, coef_volt=coef_volt):
            pass
        else:
            mysql_conn.mysql_ins_result('неисправен TV1', '6')
            return False
        mysql_conn.mysql_ins_result('идёт тест 7.2', '7')
        ctrl_kl.ctrl_relay('KL63', True)
        start_timer_2 = time()
        __timer_2 = 0
        in_a1, in_b2 = self.__inputs_a1_b2()
        while (in_b2 == False or in_a1 == True) and __timer_2 <= 75:
            sleep(0.2)
            in_a1, in_b2 = self.__inputs_a1_b2()
            __timer_2 = time() - start_timer_2
            fault.debug_msg(f'времени прошло\t{__timer_2}', 2)
        in_a1, in_b2 = self.__inputs_a1_b2()
        if in_b2 == True and in_a1 == False and __timer_2 <= 65:
            pass
        else:
            reset.sbros_kl63_proc_all()
            fault.debug_msg('тест 7.2 положение выходов не соответствует', 1)
            mysql_conn.mysql_ins_result('неисправен', '7')
            return False
        fault.debug_msg('тест 7.2 положение выходов соответствует', 4)
        reset.sbros_kl63_proc_all()
        ctrl_kl.ctrl_relay('KL12', False)
        ctrl_kl.ctrl_relay('KL25', False)
        resist.resist_ohm(255)
        ctrl_kl.ctrl_relay('KL24', True)
        sleep(0.5)
        ctrl_kl.ctrl_relay('KL24', False)
        sleep(0.5)
        ctrl_kl.ctrl_relay('KL84', True)
        sleep(0.5)
        ctrl_kl.ctrl_relay('KL84', False)
        mysql_conn.mysql_ins_result('исправен', '7')
        return True
    
    @staticmethod
    def __inputs_a1_b2():
        in_a1 = read_mb.read_discrete(1)
        in_b2 = read_mb.read_discrete(10)
        return in_a1, in_b2
    

if __name__ == '__main__':
    try:
        test_mtzp_2 = TestMTZP2()
        if test_mtzp_2.st_test_mtzp_2():
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
