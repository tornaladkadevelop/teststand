#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Алгоритм проверки

Тип блока	Производитель
БТЗ-Т	    Нет производителя
БТЗ-Т	    ТЭТЗ-Инвест
БТЗ-Т	    Строй-энергомаш
БТЗ-Т	    Углеприбор
"""

import sys

from time import time, sleep

from gen_func_procedure import *
from gen_func_utils import *
from my_msgbox import *
from my_msgbox_2 import *
from gen_mb_client import *
from gen_mysql_connect import *

__all__ = ["TestBTZT"]


class TestBTZT(object):

    def __init__(self):
        self.__reset = ResetRelay()
        self.__proc = Procedure()
        self.__read_mb = ReadMB()
        self.__ctrl_kl = CtrlKL()
        self.__mysql_conn = MySQLConnect()
        self.__fault = Bug(True)

        # self.ust_1 = (23.7, 28.6, 35.56, 37.4, 42.6, 47.3)
        self.list_ust_tzp_volt = (25.7, 30.6, 37.56, 39.4, 44.6, 49.3)
        # self.list_ust_pmz_volt = (67.9, 86.4, 99.1, 117.2, 140.7, 146.4, 156.6, 164.2, 175.7, 183.7, 192.1)
        self.list_ust_pmz_volt = (70.9, 89.4, 103.1, 121.2, 144.7, 150.4, 160.6, 168.2, 179.7, 187.7, 196.1)
        self.list_delta_t_pmz = []
        self.list_delta_t_tzp = []
        self.list_delta_percent_pmz = []
        self.list_delta_percent_tzp = []
        self.list_ust_tzp_num = (0.5, 0.6, 0.7, 0.8, 0.9, 1.0)
        self.list_ust_pmz_num = (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11)
        self.list_result_pmz = []
        self.list_result_tzp = []

        self.coef_volt: float = 0.0
        self.calc_delta_t_pmz = 0

        self.msg_1 = "Переключите оба тумблера на корпусе блока в положение «Работа» и установите " \
                     "регуляторы уставок в положение 1 (1-11) и положение 1.0 (0.5-1.0)"
        self.msg_2 = "Переключите тумблер ПМЗ (1-11) на корпусе блока в положение «Проверка»"
        self.msg_9 = "Переключите тумблер ПМЗ (1-11) в положение «Работа»"
        self.msg_3 = "«Переключите тумблер ТЗП (0.5-1.0) в положение «Проверка»"
        self.msg_8 = "Переключите тумблер ТЗП (0.5…1.0) на корпусе блока в положение «Работа»"
        self.msg_5 = f'Установите регулятор уставок ПМЗ (1-11) на блоке в положение'
        self.msg_7 = f'Установите регулятор уставок ТЗП (0.5…1.0) на блоке в положение'

    def st_test_10_btz_t(self) -> bool:
        """
        Тест 1. Проверка исходного состояния блока:
        """
        in_a0 = self.__inputs_a0()
        if in_a0 is None:
            return False
        if my_msg(self.msg_1):
            pass
        else:
            return False
        self.__fault.debug_msg("тест 1", 'blue')
        self.__mysql_conn.mysql_ins_result('идет тест 1', '1')
        self.__ctrl_kl.ctrl_relay('KL21', True)
        self.__reset.sbros_zashit_kl30()
        in_a1, in_a2, in_a5, in_a6 = self.__inputs_a()
        if in_a1 is False and in_a5 is True and in_a2 is False and in_a6 is True:
            pass
        else:
            self.__mysql_conn.mysql_ins_result('неисправен', '1')
            if in_a1 is True:
                self.__fault.debug_msg("положение входа 1 не соответствует", 'red')
                self.__mysql_conn.mysql_error(390)
            elif in_a5 is False:
                self.__fault.debug_msg("положение входа 5 не соответствует", 'red')
                self.__mysql_conn.mysql_error(391)
            elif in_a2 is True:
                self.__fault.debug_msg("положение входа 2 не соответствует", 'red')
                self.__mysql_conn.mysql_error(392)
            elif in_a6 is False:
                self.__fault.debug_msg("положение входа 6 не соответствует", 'red')
                self.__mysql_conn.mysql_error(393)
            return False
        self.__fault.debug_msg("положение выходов блока соответствует", 'green')
        return True

    def st_test_11_btz_t(self) -> bool:
        """
        # 1.1. Проверка вероятности наличия короткого замыкания
        # на входе измерительной цепи блока
        """
        self.__fault.debug_msg("тест 1.1", 'blue')
        self.__mysql_conn.mysql_ins_result('идет тест 1.1', '1')
        meas_volt_ust = self.__proc.procedure_1_21_31()
        if meas_volt_ust != 0.0:
            pass
        else:
            self.__mysql_conn.mysql_ins_result('неисправен', '1')
        self.__ctrl_kl.ctrl_relay('KL63', True)
        meas_volt = self.__read_mb.read_analog()
        min_volt = 0.4 * meas_volt_ust
        max_volt = 1.1 * meas_volt_ust
        self.__fault.debug_msg(f'напряжение после подключения KL63 {meas_volt:.2f}', 'orange')
        if min_volt <= meas_volt <= max_volt:
            pass
        else:
            self.__fault.debug_msg("напряжение не соответствует", 'red')
            self.__mysql_conn.mysql_ins_result('неисправен', '1')
            self.__mysql_conn.mysql_error(394)
            self.__reset.sbros_kl63_proc_1_21_31()
            return False
        self.__fault.debug_msg("напряжение соответствует", 'green')
        self.__reset.sbros_kl63_proc_1_21_31()
        return True

    def st_test_12_btz_t(self) -> bool:
        """
        1.2. Определение коэффициента Кс отклонения фактического напряжения от номинального
        """
        self.__fault.debug_msg("тест 1.2", 'blue')
        self.__mysql_conn.mysql_ins_result('идет тест 1.2', '1')
        self.coef_volt = self.__proc.procedure_1_22_32()
        if self.coef_volt != 0.0:
            pass
        else:
            self.__mysql_conn.mysql_ins_result('неисправен', '1')
            return False
        self.__mysql_conn.mysql_ins_result('исправен', '1')
        self.__reset.stop_procedure_32()
        self.__fault.debug_msg("тест 1 завершен", 'blue')
        return True

    def st_test_20_btz_t(self) -> bool:
        """
        Тест 2. Проверка работоспособности защиты ПМЗ блока в режиме «Проверка»
        """
        if my_msg(self.msg_2):
            pass
        else:
            return False
        self.__fault.debug_msg("тест 2", 'blue')
        self.__mysql_conn.mysql_ins_result('идет тест 2.1', '2')
        if self.__proc.start_procedure_1():
            calc_volt = self.__proc.start_procedure_23(self.coef_volt)
            if calc_volt != 0.0:
                if self.__proc.start_procedure_37(calc_volt):
                    return True
        self.__mysql_conn.mysql_ins_result('неисправен', '2')
        return False

    def st_test_21_btz_t(self) -> bool:
        """
        2.2.  Проверка срабатывания блока от сигнала нагрузки:
        """
        self.__fault.debug_msg("тест 2.2", 'blue')
        self.__mysql_conn.mysql_ins_result('идет тест 2.2', '2')
        self.__ctrl_kl.ctrl_relay('KL63', True)
        sleep(2)
        self.__ctrl_kl.ctrl_relay('KL63', False)
        in_a1, in_a2, in_a5, in_a6 = self.__inputs_a()
        if in_a1 is False and in_a5 is True and in_a2 is True and in_a6 is False:
            pass
        else:
            self.__mysql_conn.mysql_ins_result('неисправен', '2')
            if in_a1 is True:
                self.__fault.debug_msg("положение входа 1 не соответствует", 'red')
                self.__mysql_conn.mysql_error(395)
            elif in_a5 is False:
                self.__fault.debug_msg("положение входа 5 не соответствует", 'red')
                self.__mysql_conn.mysql_error(396)
            elif in_a2 is False:
                self.__fault.debug_msg("положение входа 2 не соответствует", 'red')
                self.__mysql_conn.mysql_error(397)
            elif in_a6 is True:
                self.__fault.debug_msg("положение входа 6 не соответствует", 'red')
                self.__mysql_conn.mysql_error(398)
            return False
        self.__fault.debug_msg("положение выходов блока соответствует", 'green')
        self.__reset.stop_procedure_3()
        return True

    def st_test_22_btz_t(self) -> bool:
        """
        2.4.2. Сброс защит после проверки
        """
        self.__fault.debug_msg("тест 2.4", 'blue')
        self.__mysql_conn.mysql_ins_result('идет тест 2.4', '2')
        self.__reset.sbros_zashit_kl30()
        in_a1, in_a2, in_a5, in_a6 = self.__inputs_a()
        if in_a1 is False and in_a5 is True and in_a2 is False and in_a6 is True:
            pass
        else:
            self.__mysql_conn.mysql_ins_result('неисправен', '2')
            if in_a1 is True:
                self.__fault.debug_msg("положение входа 1 не соответствует", 'red')
                self.__mysql_conn.mysql_error(399)
            elif in_a5 is False:
                self.__fault.debug_msg("положение входа 5 не соответствует", 'red')
                self.__mysql_conn.mysql_error(400)
            elif in_a2 is True:
                self.__fault.debug_msg("положение входа 2 не соответствует", 'red')
                self.__mysql_conn.mysql_error(401)
            elif in_a6 is False:
                self.__fault.debug_msg("положение входа 6 не соответствует", 'red')
                self.__mysql_conn.mysql_error(402)
            return False
        self.__fault.debug_msg("положение выходов блока соответствует", 'green')
        self.__mysql_conn.mysql_ins_result('исправен', '2')
        self.__fault.debug_msg("тест 2 завершен", 'blue')
        if my_msg(self.msg_9):
            pass
        else:
            return False
        return True

    def st_test_30_btz_t(self) -> bool:
        """
        Тест 3. Проверка работоспособности защиты ТЗП блока в режиме «Проверка»
        """
        if my_msg(self.msg_3):
            pass
        else:
            return False
        self.__fault.debug_msg("тест 3", 'blue')
        self.__mysql_conn.mysql_ins_result('идет тест 3.1', '3')
        in_a1, in_a2, in_a5, in_a6 = self.__inputs_a()
        if in_a1 is True and in_a5 is False and in_a2 is False and in_a6 is True:
            pass
        else:
            self.__mysql_conn.mysql_ins_result('неисправен', '3')
            if in_a1 is False:
                self.__fault.debug_msg("положение входа 1 не соответствует", 'red')
                self.__mysql_conn.mysql_error(403)
            elif in_a5 is True:
                self.__fault.debug_msg("положение входа 5 не соответствует", 'red')
                self.__mysql_conn.mysql_error(404)
            elif in_a2 is True:
                self.__fault.debug_msg("положение входа 2 не соответствует", 'red')
                self.__mysql_conn.mysql_error(405)
            elif in_a6 is False:
                self.__fault.debug_msg("положение входа 6 не соответствует", 'red')
                self.__mysql_conn.mysql_error(406)
            return False
        self.__fault.debug_msg("положение выходов блока соответствует", 'green')
        return True

    def st_test_31_btz_t(self) -> bool:
        """
        3.2. Сброс защит после проверки
        """
        self.__fault.debug_msg("тест 3.2", 'blue')
        self.__mysql_conn.mysql_ins_result('идет тест 3.2', '3')
        if my_msg(self.msg_8):
            pass
        else:
            return False
        self.__reset.sbros_zashit_kl30()
        sleep(1)
        in_a1, in_a2, in_a5, in_a6 = self.__inputs_a()
        if in_a1 is False and in_a5 is True and in_a2 is False and in_a6 is True:
            pass
        else:
            self.__mysql_conn.mysql_ins_result('неисправен', '3')
            if in_a1 is True:
                self.__fault.debug_msg("положение входа 1 не соответствует", 'red')
                self.__mysql_conn.mysql_error(407)
            elif in_a5 is False:
                self.__fault.debug_msg("положение входа 5 не соответствует", 'red')
                self.__mysql_conn.mysql_error(408)
            elif in_a2 is True:
                self.__fault.debug_msg("положение входа 2 не соответствует", 'red')
                self.__mysql_conn.mysql_error(409)
            elif in_a6 is False:
                self.__fault.debug_msg("положение входа 6 не соответствует", 'red')
                self.__mysql_conn.mysql_error(410)
            return False
        self.__fault.debug_msg("положение выходов блока соответствует", 'green')
        self.__mysql_conn.mysql_ins_result('исправен', '3')
        self.__fault.debug_msg("тест 3 завершен", 'blue')
        return True

    def st_test_40_btz_t(self) -> bool:
        """
        Тест 4. Проверка срабатывания защиты ПМЗ блока по уставкам
        """
        self.__fault.debug_msg("тест 4", 'blue')
        self.__mysql_conn.mysql_ins_result('идет тест 4', '4')
        k = 0
        for i in self.list_ust_pmz_volt:
            msg_result = my_msg_2(f'{self.msg_5} {self.list_ust_pmz_num[k]}')
            if msg_result == 0:
                pass
            elif msg_result == 1:
                return False
            elif msg_result == 2:
                self.__mysql_conn.mysql_add_message(f'уставка {self.list_ust_pmz_num[k]} пропущена')
                self.list_delta_percent_pmz.append('пропущена')
                self.list_delta_t_pmz.append('пропущена')
                k += 1
                continue
            self.__mysql_conn.mysql_ins_result('идет тест 4.1', '4')
            if self.__proc.procedure_1_24_34(coef_volt=self.coef_volt, setpoint_volt=i):
                pass
            else:
                self.__mysql_conn.mysql_ins_result('неисправен', '4')
                return False
            meas_volt_pmz = self.__read_mb.read_analog()
            # Δ%= 2.7938*U4
            calc_delta_percent_pmz = 2.7938 * meas_volt_pmz
            self.list_delta_percent_pmz.append(f'{calc_delta_percent_pmz:.2f}')
            # 4.1.  Проверка срабатывания блока от сигнала нагрузки:
            self.__fault.debug_msg("тест 4.1", 'blue')
            self.__mysql_conn.mysql_ins_result('идет тест 4.2', '4')
            qw = 0
            for qw in range(4):
                self.calc_delta_t_pmz = self.__ctrl_kl.ctrl_ai_code_v0(103)
                self.__fault.debug_msg(f'дельта t: {self.calc_delta_t_pmz:.1f}', 'orange')
                if self.calc_delta_t_pmz == 9999:
                    self.__reset.sbros_zashit_kl30()
                    sleep(3)
                    qw += 1
                    continue
                elif 3000 < self.calc_delta_t_pmz < 9999:
                    self.__reset.sbros_zashit_kl30()
                    sleep(3)
                    qw += 1
                    continue
                else:
                    break
            in_a1, in_a2, in_a5, in_a6 = self.__inputs_a()
            self.__fault.debug_msg(f'дельта t: {self.calc_delta_t_pmz}', 'orange')
            self.__mysql_conn.mysql_add_message(f'уставка {self.list_ust_pmz_num[k]} '
                                                f'дельта t: {self.calc_delta_t_pmz:.1f}')
            self.__mysql_conn.mysql_add_message(f'уставка {self.list_ust_pmz_num[k]} '
                                                f'дельта %: {calc_delta_percent_pmz:.2f}')
            if self.calc_delta_t_pmz < 10:
                self.list_delta_t_pmz.append(f'< 10')
            elif self.calc_delta_t_pmz > 3000:
                self.list_delta_t_pmz.append(f'> 3000')
            else:
                self.list_delta_t_pmz.append(f'{self.calc_delta_t_pmz:.1f}')
            self.__reset.stop_procedure_3()
            if in_a1 is False and in_a5 is True and in_a2 is True and in_a6 is False:
                self.__fault.debug_msg("положение выходов блока соответствует", 'green')
                if self.__subtest_45():
                    k += 1
                    continue
                else:
                    self.__mysql_conn.mysql_ins_result('неисправен', '4')
                    return False
            else:
                self.__fault.debug_msg("положение выходов блока не соответствует", 'red')
                self.__mysql_conn.mysql_ins_result('неисправен', '4')
                self.__mysql_conn.mysql_error(389)
                if self.__subtest_42(i, k):
                    if self.__subtest_45():
                        k += 1
                        continue
                    else:
                        self.__mysql_conn.mysql_ins_result('неисправен', '4')
                        return False
                else:
                    if self.__subtest_43():
                        k += 1
                        continue
                    else:
                        self.__mysql_conn.mysql_ins_result('неисправен', '4')
                        return False
        self.__mysql_conn.mysql_ins_result('исправен', '4')
        self.__fault.debug_msg("тест 4 завершен", 'blue')
        return True

    def st_test_50_btz_t(self) -> bool:
        """
        Тест 5. Проверка срабатывания защиты ТЗП блока по уставкам
        """
        self.__fault.debug_msg("тест 5", 'blue')
        self.__mysql_conn.mysql_ins_result('идет тест 5', '5')
        m = 0
        for n in self.list_ust_tzp_volt:
            msg_result = my_msg_2(f'{self.msg_7} {self.list_ust_tzp_num[m]}')
            if msg_result == 0:
                pass
            elif msg_result == 1:
                return False
            elif msg_result == 2:
                self.__mysql_conn.mysql_add_message(f'уставка {self.list_ust_tzp_num[m]} пропущена')
                self.list_delta_percent_tzp.append('пропущена')
                self.list_delta_t_tzp.append('пропущена')
                m += 1
                continue
            self.__mysql_conn.mysql_ins_result('идет тест 5.1', '5')
            if self.__proc.procedure_1_24_34(coef_volt=self.coef_volt, setpoint_volt=n):
                pass
            else:
                self.__mysql_conn.mysql_ins_result('неисправен', '5')
                return False
            meas_volt_tzp = self.__read_mb.read_analog()
            # Δ%= 0.0044*U42[i]+2.274* U4[i]
            calc_delta_percent_tzp = 0.0044 * meas_volt_tzp ** 2 + 2.274 * meas_volt_tzp
            self.list_delta_percent_tzp.append(f'{calc_delta_percent_tzp:.2f}')
            # 5.4.  Проверка срабатывания блока от сигнала нагрузки:
            self.__mysql_conn.progress_level(0.0)
            self.__fault.debug_msg("тест 5.4", 'blue')
            self.__mysql_conn.mysql_ins_result('идет тест 5.4', '5')
            self.__ctrl_kl.ctrl_relay('KL63', True)
            in_b0, in_b1 = self.__inputs_b()
            while in_b1 is False:
                in_b0, in_b1 = self.__inputs_b()
            start_timer_2 = time()
            in_a5 = self.__read_in_a5()
            sub_timer = 0
            while in_a5 is True and sub_timer <= 360:
                sleep(0.2)
                sub_timer = time() - start_timer_2
                self.__fault.debug_msg(f'времени прошло {sub_timer:.1f}', 'orange')
                self.__mysql_conn.progress_level(sub_timer)
                self.__fault.debug_msg(f'{in_a5=}', 'purple')
                in_a5 = self.__read_in_a5()
            stop_timer_2 = time()
            calc_delta_t_tzp = stop_timer_2 - start_timer_2
            self.__mysql_conn.progress_level(0.0)
            self.__fault.debug_msg(f'дельта t: {calc_delta_t_tzp:.1f}', 'orange')
            self.__ctrl_kl.ctrl_relay('KL63', False)
            self.list_delta_t_tzp.append(f'{calc_delta_t_tzp:.1f}')
            self.__mysql_conn.mysql_add_message(f'уставка {self.list_ust_tzp_num[m]} '
                                                f'дельта t: {calc_delta_t_tzp:.1f}')
            self.__mysql_conn.mysql_add_message(f'уставка {self.list_ust_tzp_num[m]} '
                                                f'дельта %: {calc_delta_percent_tzp:.2f}')
            in_a1, in_a2, in_a5, in_a6 = self.__inputs_a()
            if in_a1 is True and in_a5 is False and in_a2 is False and in_a6 is True and calc_delta_t_tzp <= 360:
                self.__fault.debug_msg("входа соответствуют ", 'green')
                if self.__subtest_56():
                    m += 1
                    continue
                else:
                    self.__mysql_conn.mysql_ins_result('неисправен', '5')
                    return False
            else:
                self.__fault.debug_msg("входа не соответствуют ", 'red')
                self.__mysql_conn.mysql_ins_result('неисправен', '5')
                self.__mysql_conn.mysql_error(411)
                if self.__subtest_55():
                    m += 1
                    continue
                else:
                    self.__mysql_conn.mysql_ins_result('неисправен', '5')
                    return False
        self.__mysql_conn.mysql_ins_result('исправен', '5')
        return True

    def __subtest_42(self, i, k) -> bool:
        """
        4.2. Формирование нагрузочного сигнала 1,1*calc_volt[i]:
        :return:
        """
        self.__fault.debug_msg("тест 4.2", 'blue')
        self.__mysql_conn.mysql_ins_result('идет тест 4.2', '4')
        self.__reset.sbros_zashit_kl30()
        sleep(1)
        in_a1, in_a2, in_a5, in_a6 = self.__inputs_a()
        if in_a1 is False and in_a5 is True and in_a2 is False and in_a6 is True:
            pass
        else:
            self.__mysql_conn.mysql_ins_result('неисправен', '4')
            if in_a1 is True:
                self.__mysql_conn.mysql_error(399)
            elif in_a5 is False:
                self.__mysql_conn.mysql_error(400)
            elif in_a2 is True:
                self.__mysql_conn.mysql_error(401)
            elif in_a6 is False:
                self.__mysql_conn.mysql_error(402)
            return False
        if self.__proc.procedure_1_25_35(coef_volt=self.coef_volt, setpoint_volt=i):
            pass
        else:
            self.__mysql_conn.mysql_ins_result('неисправен', '4')
        meas_volt_pmz = self.__read_mb.read_analog()
        # Δ%= 2.7938*U4
        calc_delta_percent_pmz = 2.7938 * meas_volt_pmz
        self.list_delta_percent_pmz[-1] = f'{calc_delta_percent_pmz:.2f}'
        # 4.2.2.  Проверка срабатывания блока от сигнала нагрузки:
        self.__fault.debug_msg("тест 4.2.2", 'blue')
        self.__mysql_conn.mysql_ins_result('идет тест 4.2.2', '4')
        wq = 0
        for wq in range(4):
            self.calc_delta_t_pmz = self.__ctrl_kl.ctrl_ai_code_v0(103)
            self.__fault.debug_msg(f'дельта t: {self.calc_delta_t_pmz}', 'orange')
            if self.calc_delta_t_pmz == 9999:
                self.__reset.sbros_zashit_kl30()
                sleep(3)
                wq += 1
                continue
            elif 3000 < self.calc_delta_t_pmz < 9999:
                self.__reset.sbros_zashit_kl30()
                sleep(3)
                wq += 1
                continue
            else:
                break
        in_a1, in_a2, in_a5, in_a6 = self.__inputs_a()
        self.__fault.debug_msg(f'дельта t: {self.calc_delta_t_pmz:.1f}', 'orange')
        self.__mysql_conn.mysql_add_message(f'уставка {self.list_ust_pmz_num[k]} '
                                            f'дельта t: {self.calc_delta_t_pmz:.1f}')
        self.__mysql_conn.mysql_add_message(f'уставка {self.list_ust_pmz_num[k]} '
                                            f'дельта %: {calc_delta_percent_pmz:.2f}')
        if self.calc_delta_t_pmz < 10:
            self.list_delta_t_pmz[-1] = f'< 10'
        elif self.calc_delta_t_pmz > 3000:
            self.list_delta_t_pmz[-1] = f'> 3000'
        else:
            self.list_delta_t_pmz[-1] = f'{self.calc_delta_t_pmz:.1f}'

        if in_a1 is False and in_a5 is True and in_a2 is True and in_a6 is False:
            pass
        else:
            return False
        self.__reset.stop_procedure_3()
        return True

    def __subtest_43(self):
        self.__fault.debug_msg("тест 4.3", 'blue')
        self.__mysql_conn.mysql_ins_result('идет тест 4.3', '4')
        self.__reset.sbros_zashit_kl30()
        sleep(1)
        in_a1, in_a2, in_a5, in_a6 = self.__inputs_a()
        if in_a1 is False and in_a5 is True and in_a2 is False and in_a6 is True:
            pass
        else:
            self.__mysql_conn.mysql_ins_result('неисправен', '4')
            if in_a1 is True:
                self.__mysql_conn.mysql_error(399)
            elif in_a5 is False:
                self.__mysql_conn.mysql_error(400)
            elif in_a2 is True:
                self.__mysql_conn.mysql_error(401)
            elif in_a6 is False:
                self.__mysql_conn.mysql_error(402)
            return False
        return True

    def __subtest_45(self):
        self.__fault.debug_msg("тест 4.5", 'blue')
        self.__mysql_conn.mysql_ins_result('идет тест 4.5', '4')
        self.__reset.sbros_zashit_kl30()
        sleep(1)
        in_a1, in_a2, in_a5, in_a6 = self.__inputs_a()
        self.__fault.debug_msg(f'{in_a1 = } (False), {in_a2 = } (True), '
                               f'{in_a5 = } (False), {in_a6 = } (True)', 'purple')
        if in_a1 is False and in_a5 is True and in_a2 is False and in_a6 is True:
            pass
        else:
            self.__mysql_conn.mysql_ins_result('неисправен', '4')
            if in_a1 is True:
                self.__mysql_conn.mysql_error(399)
            elif in_a5 is False:
                self.__mysql_conn.mysql_error(400)
            elif in_a2 is True:
                self.__mysql_conn.mysql_error(401)
            elif in_a6 is False:
                self.__mysql_conn.mysql_error(402)
            return False
        return True

    def __subtest_55(self):
        self.__fault.debug_msg("тест 5.5", 'blue')
        self.__mysql_conn.mysql_ins_result('идет тест 5.5', '5')
        self.__reset.stop_procedure_3()
        self.__reset.sbros_zashit_kl30()
        sleep(1)
        in_a1, in_a2, in_a5, in_a6 = self.__inputs_a()
        if in_a1 is False and in_a5 is True and in_a2 is False and in_a6 is True:
            pass
        else:
            self.__mysql_conn.mysql_ins_result('неисправен', '5')
            if in_a1 is True:
                self.__mysql_conn.mysql_error(399)
            elif in_a5 is False:
                self.__mysql_conn.mysql_error(400)
            elif in_a2 is True:
                self.__mysql_conn.mysql_error(401)
            elif in_a6 is False:
                self.__mysql_conn.mysql_error(402)
            return False
        return True

    def __subtest_56(self):
        """
        5.6.1. Сброс защит после проверки
        """
        self.__fault.debug_msg("тест 5.6", 'blue')
        self.__mysql_conn.mysql_ins_result('идет тест 5.6', '5')
        self.__reset.stop_procedure_3()
        self.__reset.sbros_zashit_kl30()
        sleep(1)
        in_a1, in_a2, in_a5, in_a6 = self.__inputs_a()
        if in_a1 is False and in_a5 is True and in_a2 is False and in_a6 is True:
            pass
        else:
            self.__mysql_conn.mysql_ins_result('неисправен', '5')
            if in_a1 is True:
                self.__mysql_conn.mysql_error(399)
            elif in_a5 is False:
                self.__mysql_conn.mysql_error(400)
            elif in_a2 is True:
                self.__mysql_conn.mysql_error(401)
            elif in_a6 is False:
                self.__mysql_conn.mysql_error(402)
            return False
        return True

    def __inputs_a0(self):
        in_a0 = self.__read_mb.read_discrete(0)
        if in_a0 is None:
            # logging.error(f'нет связи с контроллером')
            raise ModbusConnectException(f'нет связи с контроллером')
        return in_a0

    def __inputs_a(self):
        in_a1 = self.__read_mb.read_discrete(1)
        in_a2 = self.__read_mb.read_discrete(2)
        in_a5 = self.__read_mb.read_discrete(5)
        in_a6 = self.__read_mb.read_discrete(6)
        if in_a1 is None or in_a2 is None or in_a5 is None or in_a6 is None:
            raise ModbusConnectException(f'нет связи с контроллером')
        return in_a1, in_a2, in_a5, in_a6

    def __read_in_a5(self):
        in_a5 = self.__read_mb.read_discrete(5)
        if in_a5 is None:
            raise ModbusConnectException(f'нет связи с контроллером')
        return in_a5

    def __inputs_b(self):
        in_b0 = self.__read_mb.read_discrete(8)
        in_b1 = self.__read_mb.read_discrete(9)
        if in_b0 is None or in_b1 is None:
            raise ModbusConnectException(f'нет связи с контроллером')
        return in_b0, in_b1

    def st_test_btz_t(self) -> bool:
        if self.st_test_10_btz_t():
            if self.st_test_11_btz_t():
                if self.st_test_12_btz_t():
                    if self.st_test_20_btz_t():
                        if self.st_test_21_btz_t():
                            if self.st_test_22_btz_t():
                                if self.st_test_30_btz_t():
                                    if self.st_test_31_btz_t():
                                        if self.st_test_40_btz_t():
                                            if self.st_test_50_btz_t():
                                                return True
        return False

    def result_test_btz_t(self):
        """
        сведение всех результатов измерения, и запись в БД
        """
        for g1 in range(len(self.list_delta_percent_pmz)):
            self.list_result_pmz.append((self.list_ust_pmz_num[g1],
                                         self.list_delta_percent_pmz[g1],
                                         self.list_delta_t_pmz[g1]))
        self.__mysql_conn.mysql_pmz_result(self.list_result_pmz)
        for g2 in range(len(self.list_delta_percent_tzp)):
            self.list_result_tzp.append((self.list_ust_tzp_num[g2],
                                         self.list_delta_percent_tzp[g2],
                                         self.list_delta_t_tzp[g2]))
        self.__mysql_conn.mysql_tzp_result(self.list_result_tzp)


if __name__ == '__main__':
    test_btz_t = TestBTZT()
    reset_test_btz_t = ResetRelay()
    mysql_conn_btz_t = MySQLConnect()
    fault = Bug(True)
    try:
        if test_btz_t.st_test_btz_t():
            test_btz_t.result_test_btz_t()
            mysql_conn_btz_t.mysql_block_good()
            my_msg('Блок исправен', 'green')
        else:
            test_btz_t.result_test_btz_t()
            mysql_conn_btz_t.mysql_block_bad()
            my_msg('Блок неисправен', 'red')
    except OSError:
        my_msg("ошибка системы", 'red')
    except SystemError:
        my_msg("внутренняя ошибка", 'red')
    except ModbusConnectException as mce:
        fault.debug_msg(mce, 'red')
        my_msg(f'{mce}', 'red')
    finally:
        reset_test_btz_t.reset_all()
        sys.exit()
