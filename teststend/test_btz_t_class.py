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
    __reset = ResetRelay()
    __proc = Procedure()
    __read_mb = ReadMB()
    __ctrl_kl = CtrlKL()
    __mysql_conn = MySQLConnect()
    __fault = Bug(True)
    # None - отключен, True - включен

    # ust_1 = (23.7, 28.6, 35.56, 37.4, 42.6, 47.3)
    list_ust_tzp = (25.7, 30.6, 37.56, 39.4, 44.6, 49.3)
    list_ust_pmz = (67.9, 86.4, 100.1, 117.2, 140.7, 146.4, 156.6, 164.2, 175.7, 183.7, 192.1)
    list_delta_t_pmz = []
    list_delta_t_tzp = []
    list_delta_percent_pmz = []
    list_delta_percent_tzp = []
    list_ust_tzp_num = (0.5, 0.6, 0.7, 0.8, 0.9, 1.0)
    list_ust_pmz_num = (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11)
    list_result_pmz = []
    list_result_tzp = []

    coef_volt: float

    def __init__(self):
        pass

    def st_test_10_btz_t(self) -> bool:
        """
        Тест 1. Проверка исходного состояния блока:
        """
        msg_1 = "Переключите оба тумблера на корпусе блока в положение «Работа» и установите " \
                "регуляторы уставок в положение 1 (1-11) и положение 1.0 (0.5-1.0)"
        if my_msg(msg_1):
            pass
        else:
            return False
        self.__fault.debug_msg("тест 1", 3)
        self.__mysql_conn.mysql_ins_result('идет тест 1', '1')
        self.__ctrl_kl.ctrl_relay('KL21', True)
        self.__reset.sbros_zashit_kl30()
        in_a1, in_a2, in_a5, in_a6 = self.__inputs_a()
        if in_a1 is False and in_a5 is True and in_a2 is False and in_a6 is True:
            pass
        else:
            self.__mysql_conn.mysql_ins_result('неисправен', '1')
            if in_a1 is True:
                self.__fault.debug_msg("положение входа 1 не соответствует", 1)
                self.__mysql_conn.mysql_error(390)
            elif in_a5 is False:
                self.__fault.debug_msg("положение входа 5 не соответствует", 1)
                self.__mysql_conn.mysql_error(391)
            elif in_a2 is True:
                self.__fault.debug_msg("положение входа 2 не соответствует", 1)
                self.__mysql_conn.mysql_error(392)
            elif in_a6 is False:
                self.__fault.debug_msg("положение входа 6 не соответствует", 1)
                self.__mysql_conn.mysql_error(393)
            return False
        self.__fault.debug_msg("положение выходов блока соответствует", 4)
        return True

    def st_test_11_btz_t(self) -> bool:
        """
        # 1.1. Проверка вероятности наличия короткого замыкания
        # на входе измерительной цепи блока
        """
        self.__fault.debug_msg("тест 1.1", 3)
        self.__mysql_conn.mysql_ins_result('идет тест 1.1', '1')
        meas_volt_ust = self.__proc.procedure_1_21_31()
        self.__fault.debug_msg(f'напряжение в процедуре 1 {meas_volt_ust}', 2)
        if meas_volt_ust is not False:
            pass
        else:
            self.__mysql_conn.mysql_ins_result('неисправен', '1')
        self.__ctrl_kl.ctrl_relay('KL63', True)
        meas_volt = self.__read_mb.read_analog()
        self.__fault.debug_msg(f'напряжение после подключения KL63 {meas_volt}', 2)
        if 0.6 * meas_volt_ust <= meas_volt <= 1.1 * meas_volt_ust:
            pass
        else:
            self.__fault.debug_msg("напряжение не соответствует", 1)
            self.__mysql_conn.mysql_ins_result('неисправен', '1')
            self.__mysql_conn.mysql_error(394)
            self.__reset.sbros_kl63_proc_1_21_31()
            return False
        self.__fault.debug_msg("напряжение соответствует", 4)
        self.__reset.sbros_kl63_proc_1_21_31()
        return True

    def st_test_12_btz_t(self) -> bool:
        """
        1.2. Определение коэффициента Кс отклонения фактического напряжения от номинального
        """
        self.__fault.debug_msg("тест 1.2", 3)
        self.__mysql_conn.mysql_ins_result('идет тест 1.2', '1')
        self.coef_volt = self.__proc.procedure_1_22_32()
        if self.coef_volt is not False:
            pass
        else:
            self.__mysql_conn.mysql_ins_result('неисправен', '1')
            return False
        self.__fault.debug_msg(f'коэффициент {self.coef_volt}', 2)
        self.__mysql_conn.mysql_ins_result('исправен', '1')
        self.__reset.stop_procedure_32()
        self.__fault.debug_msg("тест 1 завершен", 3)
        return True

    def st_test_20_btz_t(self) -> bool:
        """
        Тест 2. Проверка работоспособности защиты ПМЗ блока в режиме «Проверка»
        """
        msg_2 = "Переключите тумблер ПМЗ (1-11) на корпусе блока в положение «Проверка»"
        if my_msg(msg_2):
            pass
        else:
            return False
        self.__fault.debug_msg("тест 2", 3)
        self.__mysql_conn.mysql_ins_result('идет тест 2.1', '2')
        if self.__proc.start_procedure_1():
            calc_volt = self.__proc.start_procedure_23(self.coef_volt)
            if calc_volt is not False:
                if self.__proc.start_procedure_37(calc_volt):
                    return True
        self.__mysql_conn.mysql_ins_result('неисправен', '2')
        return False

    def st_test_21_btz_t(self) -> bool:
        """
        2.2.  Проверка срабатывания блока от сигнала нагрузки:
        """
        self.__fault.debug_msg("тест 2.2", 3)
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
                self.__fault.debug_msg("положение входа 1 не соответствует", 1)
                self.__mysql_conn.mysql_error(395)
            elif in_a5 is False:
                self.__fault.debug_msg("положение входа 5 не соответствует", 1)
                self.__mysql_conn.mysql_error(396)
            elif in_a2 is False:
                self.__fault.debug_msg("положение входа 2 не соответствует", 1)
                self.__mysql_conn.mysql_error(397)
            elif in_a6 is True:
                self.__fault.debug_msg("положение входа 6 не соответствует", 1)
                self.__mysql_conn.mysql_error(398)
            return False
        self.__fault.debug_msg("положение выходов блока соответствует", 4)
        self.__reset.stop_procedure_3()
        return True

    def st_test_22_btz_t(self) -> bool:
        """
        2.4.2. Сброс защит после проверки
        """
        self.__fault.debug_msg("тест 2.4", 3)
        self.__mysql_conn.mysql_ins_result('идет тест 2.4', '2')
        self.__reset.sbros_zashit_kl30()
        in_a1, in_a2, in_a5, in_a6 = self.__inputs_a()
        if in_a1 is False and in_a5 is True and in_a2 is False and in_a6 is True:
            pass
        else:
            self.__mysql_conn.mysql_ins_result('неисправен', '2')
            if in_a1 is True:
                self.__fault.debug_msg("положение входа 1 не соответствует", 1)
                self.__mysql_conn.mysql_error(399)
            elif in_a5 is False:
                self.__fault.debug_msg("положение входа 5 не соответствует", 1)
                self.__mysql_conn.mysql_error(400)
            elif in_a2 is True:
                self.__fault.debug_msg("положение входа 2 не соответствует", 1)
                self.__mysql_conn.mysql_error(401)
            elif in_a6 is False:
                self.__fault.debug_msg("положение входа 6 не соответствует", 1)
                self.__mysql_conn.mysql_error(402)
            return False
        self.__fault.debug_msg("положение выходов блока соответствует", 4)
        self.__mysql_conn.mysql_ins_result('исправен', '2')
        self.__fault.debug_msg("тест 2 завершен", 3)
        msg_9 = "Переключите тумблер ПМЗ (1-11) в положение «Работа»"
        if my_msg(msg_9):
            pass
        else:
            return False
        return True

    def st_test_30_btz_t(self) -> bool:
        """
        Тест 3. Проверка работоспособности защиты ТЗП блока в режиме «Проверка»
        """
        msg_3 = "«Переключите тумблер ТЗП (0.5-1.0) в положение «Проверка»"
        if my_msg(msg_3):
            pass
        else:
            return False
        self.__fault.debug_msg("тест 3", 3)
        self.__mysql_conn.mysql_ins_result('идет тест 3.1', '3')
        in_a1, in_a2, in_a5, in_a6 = self.__inputs_a()
        if in_a1 is True and in_a5 is False and in_a2 is False and in_a6 is True:
            self.__fault.debug_msg("положение выходов блока соответствует", 4)
            pass
        else:
            self.__mysql_conn.mysql_ins_result('неисправен', '3')
            if in_a1 is False:
                self.__fault.debug_msg("положение входа 1 не соответствует", 1)
                self.__mysql_conn.mysql_error(403)
            elif in_a5 is True:
                self.__fault.debug_msg("положение входа 5 не соответствует", 1)
                self.__mysql_conn.mysql_error(404)
            elif in_a2 is True:
                self.__fault.debug_msg("положение входа 2 не соответствует", 1)
                self.__mysql_conn.mysql_error(405)
            elif in_a6 is False:
                self.__fault.debug_msg("положение входа 6 не соответствует", 1)
                self.__mysql_conn.mysql_error(406)
            return False

    def st_test_31_btz_t(self) -> bool:
        """
        3.2. Сброс защит после проверки
        """
        self.__fault.debug_msg("тест 3.2", 3)
        self.__mysql_conn.mysql_ins_result('идет тест 3.2', '3')
        msg_8 = "Переключите тумблер ТЗП (0.5…1.0) на корпусе блока в положение «Работа»"
        if my_msg(msg_8):
            pass
        else:
            return False
        self.__reset.sbros_zashit_kl30()
        in_a1, in_a2, in_a5, in_a6 = self.__inputs_a()
        if in_a1 is False and in_a5 is True and in_a2 is False and in_a6 is True:
            pass
        else:
            self.__mysql_conn.mysql_ins_result('неисправен', '3')
            if in_a1 is True:
                self.__fault.debug_msg("положение входа 1 не соответствует", 1)
                self.__mysql_conn.mysql_error(407)
            elif in_a5 is False:
                self.__fault.debug_msg("положение входа 5 не соответствует", 1)
                self.__mysql_conn.mysql_error(408)
            elif in_a2 is True:
                self.__fault.debug_msg("положение входа 2 не соответствует", 1)
                self.__mysql_conn.mysql_error(409)
            elif in_a6 is False:
                self.__fault.debug_msg("положение входа 6 не соответствует", 1)
                self.__mysql_conn.mysql_error(410)
            return False
        self.__fault.debug_msg("положение выходов блока соответствует", 4)
        self.__mysql_conn.mysql_ins_result('исправен', '3')
        self.__fault.debug_msg("тест 3 завершен", 3)
        return True

    def st_test_40_btz_t(self) -> bool:
        """
        Тест 4. Проверка срабатывания защиты ПМЗ блока по уставкам
        """
        self.__fault.debug_msg("тест 4", 3)
        self.__mysql_conn.mysql_ins_result('идет тест 4', '4')
        k = 0
        for i in self.list_ust_pmz:
            msg_5 = (f'Установите регулятор уставок ПМЗ (1-11) на блоке в положение {self.list_ust_pmz_num[k]}')
            msg_result = my_msg_2(msg_5)
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
            self.list_delta_percent_pmz.append(round(calc_delta_percent_pmz, 0))
            # 4.1.  Проверка срабатывания блока от сигнала нагрузки:
            self.__fault.debug_msg("тест 4.1", 3)
            self.__mysql_conn.mysql_ins_result('идет тест 4.2', '4')
            calc_delta_t_pmz = self.__ctrl_kl.ctrl_ai_code_v0(103)
            if calc_delta_t_pmz != 9999:
                pass
            else:
                self.__mysql_conn.mysql_ins_result('неисправен', '4')
            self.__fault.debug_msg(f'дельта t: {calc_delta_t_pmz}', 2)
            self.list_delta_t_pmz.append(round(calc_delta_t_pmz, 0))
            self.__mysql_conn.mysql_add_message(f'уставка {self.list_ust_pmz_num[k]} '
                                                f'дельта t: {calc_delta_t_pmz:.0f}')
            self.__mysql_conn.mysql_add_message(f'уставка {self.list_ust_pmz_num[k]} '
                                                f'дельта %: {calc_delta_percent_pmz:.0f}')
            in_a1, in_a2, in_a5, in_a6 = self.__inputs_a()
            if in_a1 is False and in_a5 is True and in_a2 is True and in_a6 is False:
                self.__fault.debug_msg("положение выходов блока соответствует", 4)
                self.__reset.stop_procedure_3()
                if self.__subtest_45():
                    k += 1
                    continue
                else:
                    self.__mysql_conn.mysql_ins_result('неисправен', '4')
                    return False
            else:
                self.__fault.debug_msg("положение выходов блока не соответствует", 1)
                self.__mysql_conn.mysql_ins_result('неисправен', '4')
                self.__mysql_conn.mysql_error(389)
                if self.__subtest_42(i, k):
                    if self.__subtest_45():
                        k += 1
                        continue
                    else:
                        self.__mysql_conn.mysql_ins_result('неисправен', '4')
                else:
                    if self.__subtest_43():
                        k += 1
                        continue
                    else:
                        self.__mysql_conn.mysql_ins_result('неисправен', '4')
        self.__mysql_conn.mysql_ins_result('исправен', '4')
        self.__fault.debug_msg("тест 4 завершен", 3)
        return True

    def st_test_50_btz_t(self) -> bool:
        """
        Тест 5. Проверка срабатывания защиты ТЗП блока по уставкам
        """
        self.__fault.debug_msg("тест 5", 3)
        self.__mysql_conn.mysql_ins_result('идет тест 5', '5')
        m = 0
        for n in self.list_ust_tzp:
            msg_7 = (f'Установите регулятор уставок ТЗП (0.5…1.0) на блоке в положение\t{self.list_ust_tzp_num[m]}')
            msg_result = my_msg_2(msg_7)
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
            self.list_delta_percent_tzp.append(round(calc_delta_percent_tzp, 0))
            # 5.4.  Проверка срабатывания блока от сигнала нагрузки:
            self.__fault.debug_msg("тест 5.4", 3)
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
                self.__fault.debug_msg(f'времени прошло {sub_timer}', 2)
                self.__fault.debug_msg(f'{in_a5=}', 3)
                in_a5 = self.__read_in_a5()
            stop_timer_2 = time()
            calc_delta_t_tzp = stop_timer_2 - start_timer_2
            self.__fault.debug_msg(f'дельта t: {calc_delta_t_tzp}', 2)
            self.__ctrl_kl.ctrl_relay('KL63', False)
            self.list_delta_t_tzp.append(round(calc_delta_t_tzp, 0))
            self.__mysql_conn.mysql_add_message(f'уставка {self.list_ust_tzp_num[m]} '
                                                f'дельта t: {calc_delta_t_tzp:.1f}')
            self.__mysql_conn.mysql_add_message(f'уставка {self.list_ust_tzp_num[m]} '
                                                f'дельта %: {calc_delta_percent_tzp:.1f}')
            in_a1, in_a2, in_a5, in_a6 = self.__inputs_a()
            if in_a1 is True and in_a5 is False and in_a2 is False and in_a6 is True and calc_delta_t_tzp <= 360:
                self.__fault.debug_msg("входа соответствуют ", 4)
                if self.__subtest_56():
                    m += 1
                    continue
                else:
                    self.__mysql_conn.mysql_ins_result('неисправен', '5')
                    return False
            else:
                self.__fault.debug_msg("входа не соответствуют ", 1)
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
        self.__fault.debug_msg("тест 4.2", 3)
        self.__mysql_conn.mysql_ins_result('идет тест 4.2', '4')
        self.__reset.sbros_zashit_kl30()
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
        if self.__proc.start_procedure_1():
            calc_volt = self.__proc.start_procedure_25(self.coef_volt, i)
            if calc_volt is not False:
                if self.__proc.start_procedure_35(calc_volt, i):
                    pass
                else:
                    self.__mysql_conn.mysql_ins_result('неисправен', '4')
            else:
                self.__mysql_conn.mysql_ins_result('неисправен', '4')
        else:
            self.__mysql_conn.mysql_ins_result('неисправен', '4')
        meas_volt_pmz = self.__read_mb.read_analog()
        # Δ%= 2.7938*U4
        calc_delta_percent_pmz = 2.7938 * meas_volt_pmz
        self.list_delta_percent_pmz[-1] = round(calc_delta_percent_pmz, 0)
        # 4.2.2.  Проверка срабатывания блока от сигнала нагрузки:
        self.__fault.debug_msg("тест 4.2.2", 3)
        self.__mysql_conn.mysql_ins_result('идет тест 4.2.2', '4')
        calc_delta_t_pmz = self.__ctrl_kl.ctrl_ai_code_v0(103)
        if calc_delta_t_pmz != 9999:
            pass
        else:
            self.__mysql_conn.mysql_ins_result('неисправен', '4')
        self.__fault.debug_msg(f'дельта t: {calc_delta_t_pmz}', 2)
        self.list_delta_t_pmz[-1] = round(calc_delta_t_pmz, 0)
        self.__mysql_conn.mysql_add_message(f'уставка {self.list_ust_pmz_num[k]} '
                                            f'дельта t: {calc_delta_t_pmz:.0f}')
        self.__mysql_conn.mysql_add_message(f'уставка {self.list_ust_pmz_num[k]} '
                                            f'дельта %: {calc_delta_percent_pmz:.0f}')
        in_a1, in_a2, in_a5, in_a6 = self.__inputs_a()
        if in_a1 is False and in_a5 is True and in_a2 is True and in_a6 is False:
            pass
        else:
            return False
        self.__reset.stop_procedure_3()
        return True

    def __subtest_43(self):
        self.__fault.debug_msg("тест 4.3", 3)
        self.__mysql_conn.mysql_ins_result('идет тест 4.3', '4')
        self.__reset.sbros_zashit_kl30()
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
        self.__fault.debug_msg("тест 4.5", 3)
        self.__mysql_conn.mysql_ins_result('идет тест 4.5', '4')
        self.__reset.sbros_zashit_kl30()
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

    def __subtest_55(self):
        self.__fault.debug_msg("тест 5.5", 3)
        self.__mysql_conn.mysql_ins_result('идет тест 5.5', '5')
        self.__reset.stop_procedure_3()
        self.__reset.sbros_zashit_kl30()
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
        self.__fault.debug_msg("тест 5.6", 3)
        self.__mysql_conn.mysql_ins_result('идет тест 5.6', '5')
        self.__reset.stop_procedure_3()
        self.__reset.sbros_zashit_kl30()
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
            my_msg('Блок исправен', '#1E8C1E')
        else:
            test_btz_t.result_test_btz_t()
            mysql_conn_btz_t.mysql_block_bad()
            my_msg('Блок неисправен', '#A61E1E')
    except OSError:
        my_msg("ошибка системы", '#A61E1E')
    except SystemError:
        my_msg("внутренняя ошибка", '#A61E1E')
    except ModbusConnectException as mce:
        fault.debug_msg(mce, 1)
        my_msg(str(mce), '#A61E1E')
    finally:
        reset_test_btz_t.reset_all()
        sys.exit()
