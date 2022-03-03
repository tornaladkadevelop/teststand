#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Алгоритм проверки

Тип блока	Производитель
БЗМП-П	Пульсар

"""

__all__ = ["TestBZMPP"]

import sys

from time import sleep, time

from my_msgbox import *
from gen_func_procedure import *
from gen_func_utils import *
from gen_mb_client import *
from gen_mysql_connect import *


class TestBZMPP(object):

    __proc = Procedure()
    __reset = ResetRelay()
    __resist = Resistor()
    __read_mb = ReadMB()
    __mb_ctrl = CtrlKL()
    __mysql_conn = MySQLConnect()
    __fault = Bug(True)

    coef_volt: float

    def __init__(self):
        pass
    
    def st_test_10_bzmp_p(self) -> bool:
        """
        Тест 1. Проверка исходного состояния блока:
        1.1.	Проверка вероятности наличия короткого замыкания на входе измерительной цепи блока
        """
        msg_1 = "Убедитесь в отсутствии других блоков и вставьте блок БЗМП-П в соответствующий разъем"
        if my_msg(msg_1):
            pass
        else:
            return False
        meas_volt_ust = self.__proc.procedure_1_21_31()
        if meas_volt_ust is not False:
            pass
        else:
            self.__mysql_conn.mysql_ins_result("неисправен TV1", "1")
            return False
        self.__mb_ctrl.ctrl_relay('KL73', True)
        sleep(5)
        self.__mb_ctrl.ctrl_relay('KL90', True)
        sleep(5)
        self.__mb_ctrl.ctrl_relay('KL63', True)
        min_volt = 0.6 * meas_volt_ust
        max_volt = 1.0 * meas_volt_ust
        meas_volt = self.__read_mb.read_analog()
        self.__fault.debug_msg(f'напряжение после включения KL63\t{meas_volt}\t'
                               f'должно быть от\t{min_volt}\tдо\t{max_volt}', 3)
        if min_volt <= meas_volt <= max_volt:
            pass
        else:
            self.__mysql_conn.mysql_ins_result('неисправен', '1')
            self.__mysql_conn.mysql_error(455)
            self.__reset.sbros_kl63_proc_1_21_31()
            return False
        self.__reset.sbros_kl63_proc_1_21_31()
        return True

    def st_test_11_bzmp_p(self) -> bool:
        """
        1.2. Определение коэффициента Кс отклонения фактического напряжения от номинального
        """
        self.coef_volt = self.__proc.procedure_1_22_32()
        if self.coef_volt is not False:
            pass
        else:
            self.__mysql_conn.mysql_ins_result("неисправен", "1")
            self.__reset.stop_procedure_32()
            return False
        self.__reset.stop_procedure_32()
        return True

    def st_test_12_bzmp_p(self) -> bool:
        self.__mb_ctrl.ctrl_relay('KL67', True)
        timer_test_1 = 0
        start_timer_test_1 = time()
        while timer_test_1 <= 120:
            sleep(0.2)
            timer_test_1 = time() - start_timer_test_1
            in_a1, in_a5, in_a6 = self.__inputs_a()
            self.__fault.debug_msg(f'времени прошло:\t{timer_test_1}', 2)
            if in_a1 is True and in_a5 is True and in_a6 is False:
                break
            else:
                continue
        self.__mysql_conn.mysql_ins_result("исправен", "1")
        return True

    @staticmethod
    def st_test_20_bzmp_p() -> bool:
        """
        Тест 2. Проверка срабатывания блока при снижении изоляции цепей 36В
        """
        msg_2 = "С помощью кнопок SB1…SB3, расположенных на панели разъемов, установите следующие параметры блока:" \
                "Iном = 200А; Iпер = 1.2; Iпуск= 7.5; Uном = 660В»"
        msg_3 = "С помощью кнопки SB3 перейдите к окну на дисплее блока с надписью «Uном=660В»"
        if my_msg(msg_2):
            if my_msg(msg_3):
                return True
        return False

    def st_test_21_bzmp_p(self) -> bool:
        self.__mb_ctrl.ctrl_relay('KL21', True)
        sleep(1)
        self.__mb_ctrl.ctrl_relay('KL27', True)
        sleep(0.1)
        self.__mb_ctrl.ctrl_relay('KL27', False)
        sleep(0.2)
        in_a6 = self.__inputs_a6()
        if in_a6 is True:
            pass
        else:
            self.__fault.debug_msg("положение выходов не соответствует", 1)
            self.__mysql_conn.mysql_ins_result("неисправен", "2")
            return False
        sleep(2)
        in_a1, in_a5, in_a6 = self.__inputs_a()
        if in_a1 is True and in_a5 is True and in_a6 is False:
            pass
        else:
            self.__fault.debug_msg("положение выходов не соответствует", 1)
            self.__mysql_conn.mysql_ins_result("неисправен", "2")
            return False
        self.__mysql_conn.mysql_ins_result("исправен", "2")
        return True

    def st_test_30_bzmp_p(self) -> bool:
        """
        Тест 3. Проверка срабатывания блока при снижении силовой изоляции
        """
        msg_4 = "С помощью кнопки SB3 перейдите к окну на дисплее блока с надписью «Uном=660В»"
        if my_msg(msg_4):
            pass
        else:
            return False
        self.__resist.resist_kohm(61)
        in_a1, in_a5, in_a6 = self.__inputs_a()
        if in_a1 is False and in_a5 is False and in_a6 is True:
            pass
        else:
            self.__fault.debug_msg("положение выходов не соответствует", 1)
            self.__mysql_conn.mysql_ins_result("неисправен", "3")
            return False
        return True

    def st_test_31_bzmp_p(self) -> bool:
        self.__resist.resist_kohm(590)
        sleep(2)
        in_a1, in_a5, in_a6 = self.__inputs_a()
        if in_a1 is True and in_a5 is True and in_a6 is False:
            pass
        else:
            self.__fault.debug_msg("положение выходов не соответствует", 1)
            self.__mysql_conn.mysql_ins_result("неисправен", "3")
            return False
        self.__mysql_conn.mysql_ins_result("исправен", "3")
        return True

    def st_test_40_bzmp_p(self) -> bool:
        """
        Тест 4. Проверка защиты ПМЗ
        """
        msg_5 = "С помощью кнопки SB3 перейдите к окну на дисплее блока с надписью «Токи фаз»"
        if my_msg(msg_5):
            pass
        else:
            return False
        if self.__proc.start_procedure_1():
            calc_volt = self.__proc.start_procedure_29(coef_volt=self.coef_volt)
            if calc_volt is not False:
                if self.__proc.start_procedure_38(calc_volt=calc_volt):
                    return True
        self.__mysql_conn.mysql_ins_result("неисправен TV1", "4")
        return False

    def st_test_41_bzmp_p(self) -> bool:
        """
        4.2.  Проверка срабатывания блока от сигнала нагрузки:
        """
        self.__mb_ctrl.ctrl_relay('KL63', True)
        sleep(0.5)
        self.__mb_ctrl.ctrl_relay('KL63', False)
        sleep(1)
        in_a1, in_a5, in_a6 = self.__inputs_a()
        if in_a1 is False and in_a5 is False and in_a6 is True:
            pass
        else:
            self.__fault.debug_msg("положение выходов не соответствует", 1)
            self.__mysql_conn.mysql_ins_result("неисправен", "4")
            self.__reset.stop_procedure_3()
            return False
        self.__reset.stop_procedure_3()
        return True

    def st_test_42_bzmp_p(self) -> bool:
        """
        4.2.2. Сброс защит после проверки
        """
        self.__sbros_zashit()
        in_a1, in_a5, in_a6 = self.__inputs_a()
        if in_a1 is True and in_a5 is True and in_a6 is False:
            pass
        else:
            self.__fault.debug_msg("положение выходов не соответствует", 1)
            self.__mysql_conn.mysql_ins_result("неисправен", "4")
            return False
        self.__mysql_conn.mysql_ins_result("исправен", "4")
        return True

    def st_test_50_bzmp_p(self) -> bool:
        """
        Тест 5. Проверка защиты от несимметрии фаз
        """
        msg_6 = "С помощью кнопок SB1…SB3 перейдите к окну на дисплее блока с надписью «Токи фаз»"
        if my_msg(msg_6):
            pass
        else:
            return False
        if self.__proc.start_procedure_1():
            calc_volt = self.__proc.start_procedure_210(coef_volt=self.coef_volt)
            if calc_volt is not False:
                if self.__proc.start_procedure_39(calc_volt=calc_volt):
                    return True
        self.__mysql_conn.mysql_ins_result("неисправен TV1", "5")
        return False

    def st_test_51_bzmp_p(self) -> bool:
        """
        5.2.  Проверка срабатывания блока от сигнала нагрузки:
        """
        self.__mb_ctrl.ctrl_relay('KL81', True)
        sleep(0.1)
        self.__mb_ctrl.ctrl_relay('KL63', True)
        in_b1 = self.__inputs_b()
        i = 0
        while in_b1 is False and i <= 10:
            in_b1 = self.__inputs_b()
            i += 1
        start_timer = time()
        in_a5 = self.__inputs_a5()
        stop_timer = 0
        while in_a5 is True and stop_timer <= 12:
            in_a5 = self.__inputs_a5()
            stop_timer = time() - start_timer
        timer_test_5_2 = stop_timer
        self.__fault.debug_msg(f'таймер тест 6.2: {timer_test_5_2}', 2)
        in_a1, in_a5, in_a6 = self.__inputs_a()
        if in_a1 is False and in_a5 is False and in_a6 is True and timer_test_5_2 <= 12:
            pass
        else:
            self.__fault.debug_msg("положение выходов не соответствует", 1)
            self.__mysql_conn.mysql_ins_result("неисправен", "5")
            self.__reset.sbros_kl63_proc_all()
            self.__mb_ctrl.ctrl_relay('KL81', False)
            return False
        self.__reset.sbros_kl63_proc_all()
        self.__mb_ctrl.ctrl_relay('KL81', False)
        self.__mb_ctrl.ctrl_relay('KL24', True)
        sleep(4)
        self.__mb_ctrl.ctrl_relay('KL24', False)
        sleep(0.7)
        in_a1, in_a5, in_a6 = self.__inputs_a()
        if in_a1 is True and in_a5 is True and in_a6 is False:
            pass
        else:
            self.__fault.debug_msg("положение выходов не соответствует", 1)
            self.__mysql_conn.mysql_ins_result("неисправен", "5")
            return False
        self.__mysql_conn.mysql_ins_result(f'исправен, {timer_test_5_2:.1f} сек', "5")

    def st_test_60_bzmp_p(self) -> bool:
        """
        Тест 6. Проверка защиты от перегрузки
        """
        msg_7 = "С помощью кнопок SB1…SB3 перейдите к окну на дисплее блока с надписью «Токи фаз»"
        if my_msg(msg_7):
            pass
        else:
            return False
        if self.__proc.start_procedure_1():
            calc_volt = self.__proc.start_procedure_211(coef_volt=coef_volt)
            if calc_volt is not False:
                if self.__proc.start_procedure_310(calc_volt=calc_volt):
                    pass
                else:
                    self.__mysql_conn.mysql_ins_result("неисправен TV1", "6")
                    return False
            else:
                self.__mysql_conn.mysql_ins_result("неисправен TV1", "6")
                return False
        else:
            self.__mysql_conn.mysql_ins_result("неисправен TV1", "6")
            return False
        # 6.2.  Проверка срабатывания блока от сигнала нагрузки:
        self.__mb_ctrl.ctrl_relay('KL63', True)
        in_b1 = self.__inputs_b()
        k = 0
        while in_b1 is False and k <= 10:
            in_b1 = self.__inputs_b()
            k += 1
        start_timer = time()
        in_a5 = self.__inputs_a5()
        stop_timer = 0
        while in_a5 is True and stop_timer <= 360:
            in_a5 = self.__inputs_a5()
            stop_timer = time() - start_timer
        timer_test_6_2 = stop_timer
        self.__fault.debug_msg(f'таймер тест 6.2: {timer_test_6_2}', 2)
        in_a1, in_a5, in_a6 = self.__inputs_a()
        if in_a1 is False and in_a5 is False and in_a6 is True and timer_test_6_2 <= 360:
            pass
        else:
            self.__fault.debug_msg("положение выходов не соответствует", 1)
            self.__mysql_conn.mysql_ins_result("неисправен", "6")
            self.__reset.sbros_kl63_proc_all()
            return False
        self.__reset.sbros_kl63_proc_all()
        # Выдаем сообщение: «Сработала защита от перегрузки»
        # 6.6. Сброс защит после проверки
        self.__sbros_zashit()
        in_a1, in_a5, in_a6 = self.__inputs_a()
        if in_a1 is True and in_a5 is True and in_a6 is False:
            pass
        else:
            self.__fault.debug_msg("положение выходов не соответствует", 1)
            self.__mysql_conn.mysql_ins_result("неисправен", "6")
            return False
        self.__mysql_conn.mysql_ins_result(f'исправен, {timer_test_6_2:.1f} сек', "6")
        return True
    
    def __sbros_zashit(self):
        self.__mb_ctrl.ctrl_relay('KL24', True)
        sleep(3)
        self.__mb_ctrl.ctrl_relay('KL24', False)
        sleep(0.7)
    
    def __inputs_a(self):
        in_a1 = self.__read_mb.read_discrete(1)
        in_a5 = self.__read_mb.read_discrete(5)
        in_a6 = self.__read_mb.read_discrete(6)
        if in_a1 is None or in_a5 is None or in_a6 is None:
            raise ModbusConnectException(f'нет связи с контроллером')
        return in_a1, in_a5, in_a6
    
    def __inputs_a5(self):
        in_a5 = self.__read_mb.read_discrete(5)
        if in_a5 is None:
            raise ModbusConnectException(f'нет связи с контроллером')
        return in_a5
    
    def __inputs_a6(self):
        in_a6 = self.__read_mb.read_discrete(6)
        if in_a6 is None:
            raise ModbusConnectException(f'нет связи с контроллером')
        return in_a6
    
    def __inputs_b(self):
        in_a9 = self.__read_mb.read_discrete(9)
        if in_a9 is None:
            raise ModbusConnectException(f'нет связи с контроллером')
        return in_a9


if __name__ == '__main__':
    test_bzmp_p = TestBZMPP()
    reset_test_bzmp_p = ResetRelay()
    mysql_conn_bzmp_p = MySQLConnect()
    fault = Bug(True)
    try:
        if test_bzmp_p.st_test_bzmp_p():
            mysql_conn_bzmp_p.mysql_block_good()
            my_msg('Блок исправен', '#1E8C1E')
        else:
            mysql_conn_bzmp_p.mysql_block_bad()
            my_msg('Блок неисправен', '#A61E1E')
    except OSError:
        my_msg("ошибка системы", '#A61E1E')
    except SystemError:
        my_msg("внутренняя ошибка", '#A61E1E')
    except ModbusConnectException as mce:
        fault.debug_msg(mce, 1)
        my_msg(str(mce), '#A61E1E')
    finally:
        reset_test_bzmp_p.reset_all()
        sys.exit()
