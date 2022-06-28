#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Алгоритм проверки

Тип блока	Производитель
БКЗ-ЗМК	    Без Производителя
БКЗ-ЗМК	    ДонЭнергоЗавод
БКЗ-ЗМК	    ИТЭП
БКЗ-Д	    Без Производителя
БКЗ-Д	    ДонЭнергоЗавод
БКЗ-З	    Без Производителя
БКЗ-З	    ДонЭнергоЗавод
БКЗ-З	    ИТЭП
"""

import sys

from time import sleep, time

from my_msgbox import *
from my_msgbox_2 import *
from gen_func_procedure import *
from gen_func_utils import *
from gen_mb_client import *
from gen_mysql_connect import *

__all__ = ["TestBKZ3MK"]


class TestBKZ3MK(object):

    def __init__(self):
        self.__proc = Procedure()
        self.__reset = ResetRelay()
        self.__resist = Resistor()
        self.__ctrl_kl = CtrlKL()
        self.__read_mb = ReadMB()
        self.__mysql_conn = MySQLConnect()
        self.__fault = Bug(True)

        # Тест 5. Проверка срабатывания защиты ТЗП блока по уставкам
        # медленные
        self.list_ust_tzp_num = (0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 1.1)
        self.list_ust_tzp_volt = (4.7, 7.2, 8.7, 10.2, 11.6, 13.0, 14.4, 15.7, 17.6)
        self.list_delta_t_tzp = []
        self.list_delta_percent_tzp = []
        self.list_result_tzp = []
        # Тест 4. Проверка срабатывания защиты МТЗ блока по уставкам
        # быстрые
        self.list_ust_mtz_num = (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11)
        self.list_ust_mtz_volt = (21.8, 27.2, 32.7, 38.1, 43.6, 49.0, 54.4, 59.9, 65.3, 70.8, 76.2)
        self.list_delta_t_mtz = []
        self.list_delta_percent_mtz = []
        self.list_result_mtz = []

        self.coef_volt: float = 0.0
        self.calc_delta_t_mtz: float = 0.0

        self.msg_1 = "Убедитесь в отсутствии других блоков в панелях разъемов и вставьте " \
                     "блок в соответствующий разъем панели С»"
        self.msg_2 = "«Переключите регулятор МТЗ на корпусе блока в положение «1», регулятор ТЗП в положение " \
                     "«1.1» «Переключите тумблеры в положение «Работа» и «660В»"
        self.msg_3 = "Установите регулятор МТЗ (1-11), расположенный на корпусе блока, в положение"
        self.msg_4 = "Установите регулятор МТЗ (1-11), расположенный на блоке, в положение «11»"
        self.msg_5 = "Установите регулятор ТЗП (0.3-1.1), расположенный на блоке в положение"

    def st_test_0_bkz_3mk(self) -> bool:
        in_a0 = self.__inputs_a0()
        if in_a0 is None:
            return False
        if my_msg(self.msg_1):
            if my_msg(self.msg_2):
                self.__mysql_conn.mysql_ins_result('---', '1')
                self.__mysql_conn.mysql_ins_result('---', '2')
                self.__mysql_conn.mysql_ins_result('---', '3')
                return True
        return False

    def st_test_10_bkz_3mk(self) -> bool:
        """
        Тест 1. Проверка исходного состояния блока:
        """
        self.__mysql_conn.mysql_ins_result('идет тест 1', '1')
        self.__fault.debug_msg("Тест 1. Проверка исходного состояния блока", 'blue')
        self.__ctrl_kl.ctrl_relay('KL21', True)
        sleep(2)
        self.__reset.sbros_zashit_kl30_1s5()
        sleep(1)
        in_a5, in_a6 = self.__inputs_a()
        if in_a5 is True and in_a6 is True:
            self.__fault.debug_msg("состояние выходов соответствует", 'green')
            pass
        else:
            self.__mysql_conn.mysql_ins_result('неисправен', '1')
            if in_a5 is False:
                self.__fault.debug_msg("вход 5 не соответствует", 'red')
                self.__mysql_conn.mysql_error(317)
            elif in_a6 is False:
                self.__fault.debug_msg("вход 6 не соответствует", 'red')
                self.__mysql_conn.mysql_error(318)
            return False
        return True

    def st_test_11_bkz_3mk(self) -> bool:
        """
        1.1.2. Проверка отсутствия короткого замыкания на входе измерительной части блока:
        """
        meas_volt_ust = self.__proc.procedure_1_21_31()
        if meas_volt_ust != 0.0:
            pass
        else:
            self.__mysql_conn.mysql_ins_result('неисправен', '1')
            return False
        self.__mysql_conn.mysql_ins_result('идет тест 1.1.2', '1')
        self.__ctrl_kl.ctrl_relay('KL63', True)
        sleep(1)
        min_volt = 0.6 * meas_volt_ust
        max_volt = 1.1 * meas_volt_ust
        meas_volt = self.__read_mb.read_analog()
        self.__fault.debug_msg(f"напряжение после включения KL63 "
                               f"{min_volt:.2f} <= {meas_volt:.2f} <= {max_volt:.2f}", 'orange')
        if min_volt <= meas_volt <= max_volt:
            pass
        else:
            self.__fault.debug_msg("напряжение не соответствует", 'red')
            self.__mysql_conn.mysql_ins_result('неисправен', '1')
            self.__mysql_conn.mysql_error(32)
            self.__reset.sbros_kl63_proc_1_21_31()
            return False
        self.__fault.debug_msg("напряжение соответствует", 'green')
        self.__reset.sbros_kl63_proc_1_21_31()
        return True

    def st_test_12_bkz_3mk(self) -> bool:
        """
        1.2. Определение коэффициента Кс отклонения фактического напряжения от номинального
        """
        self.__mysql_conn.mysql_ins_result('идет тест 1.2', '1')
        self.coef_volt = self.__proc.procedure_1_22_32()
        if self.coef_volt != 0.0:
            pass
        else:
            self.__reset.stop_procedure_32()
            self.__mysql_conn.mysql_ins_result('неисправен', '1')
            return False
        self.__reset.stop_procedure_32()
        self.__mysql_conn.mysql_ins_result('исправен', '1')
        self.__fault.debug_msg("тест 1 пройден", 'green')
        return True

    def st_test_20_bkz_3mk(self) -> bool:
        """
        Тест 2. Проверка работы блока при нормальном сопротивлении изоляции контролируемого присоединения
        """
        self.__mysql_conn.mysql_ins_result('идет тест 2', '2')
        self.__resist.resist_kohm(200)
        sleep(1)
        in_a5, in_a6 = self.__inputs_a()
        if in_a5 is True and in_a6 is True:
            pass
        else:
            self.__mysql_conn.mysql_ins_result('неисправен', '2')
            if in_a5 is False:
                self.__fault.debug_msg("вход 5 не соответствует", 'red')
                self.__mysql_conn.mysql_error(319)
            elif in_a6 is False:
                self.__fault.debug_msg("вход 6 не соответствует", 'red')
                self.__mysql_conn.mysql_error(320)
            return False
        self.__fault.debug_msg("состояние выходов соответствует", 'green')
        self.__mysql_conn.mysql_ins_result('исправен', '2')
        self.__fault.debug_msg("тест 2 пройден", 'green')
        return True

    def st_test_30_bkz_3mk(self) -> bool:
        """
        Тест 3. Проверка работы блока при снижении уровня сопротивлении изоляции ниже аварийной уставки
        """
        self.__mysql_conn.mysql_ins_result('идет тест 3', '3')
        self.__ctrl_kl.ctrl_relay('KL22', True)
        sleep(1)
        in_a5, in_a6 = self.__inputs_a()
        if in_a5 is True and in_a6 is False:
            pass
        else:
            self.__mysql_conn.mysql_ins_result('неисправен', '3')
            if in_a5 is False:
                self.__fault.debug_msg("вход 5 не соответствует", 'red')
                self.__mysql_conn.mysql_error(321)
            elif in_a6 is True:
                self.__fault.debug_msg("вход 6 не соответствует", 'red')
                self.__mysql_conn.mysql_error(322)
            return False
        self.__fault.debug_msg("состояние выходов блока соответствует", 'green')
        self.__mysql_conn.mysql_ins_result('исправен', '3')
        self.__resist.resist_kohm(590)
        self.__ctrl_kl.ctrl_relay('KL22', False)
        sleep(2)
        self.__reset.sbros_zashit_kl30_1s5()
        in_a5, in_a6 = self.__inputs_a()
        self.__fault.debug_msg(f'положение входов \t {in_a5 = } (True) {in_a6 = } (True)', 'blue')
        if in_a5 is True and in_a6 is True:
            pass
        else:
            return False
        self.__fault.debug_msg("тест 3 пройден", 'green')
        return True

    def st_test_40_bkz_3mk(self) -> bool:
        """
        Тест 4. Проверка срабатывания защиты МТЗ блока по уставкам
        """
        self.__mysql_conn.mysql_ins_result('идет тест 4', '4')
        k = 0
        for i in self.list_ust_mtz_volt:
            msg_result_mtz = my_msg_2(f'{self.msg_3} {self.list_ust_mtz_num[k]}')
            if msg_result_mtz == 0:
                pass
            elif msg_result_mtz == 1:
                return False
            elif msg_result_mtz == 2:
                self.__mysql_conn.mysql_add_message(f'уставка МТЗ {self.list_ust_mtz_num[k]} пропущена')
                self.list_delta_percent_mtz.append('пропущена')
                self.list_delta_t_mtz.append('пропущена')
                k += 1
                continue
            if self.__proc.procedure_1_24_34(coef_volt=self.coef_volt, setpoint_volt=i):
                pass
            else:
                self.__mysql_conn.mysql_ins_result('неисправен', '4')
                return False
            # 4.1.  Проверка срабатывания блока от сигнала нагрузки:
            # Δ% = 9,19125*U4
            meas_volt_test4 = self.__read_mb.read_analog()
            self.__fault.debug_msg(f'напряжение \t {meas_volt_test4:.2f}', 'orange')
            calc_delta_percent_mtz = meas_volt_test4 * 9.19125
            self.__fault.debug_msg(f'дельта % \t {calc_delta_percent_mtz:.2f}', 'orange')
            self.list_delta_percent_mtz.append(f'{calc_delta_percent_mtz:.2f}')
            self.__mysql_conn.mysql_ins_result('идет тест 4.1', '4')
            for qw in range(4):
                self.calc_delta_t_mtz = self.__ctrl_kl.ctrl_ai_code_v0(code=105)
                self.__mysql_conn.mysql_add_message(f'уставка МТЗ {self.list_ust_mtz_num[k]}  '
                                                    f'дельта t: {self.calc_delta_t_mtz:.1f} ')
                if self.calc_delta_t_mtz == 9999:
                    self.__reset.sbros_zashit_kl30_1s5()
                    sleep(3)
                    qw += 1
                    continue
                else:
                    qw = 0
                    break
            in_a5, in_a6 = self.__inputs_a()
            self.__fault.debug_msg(f'дельта t \t {self.calc_delta_t_mtz:.1f}', 'orange')
            if self.calc_delta_t_mtz < 10:
                self.list_delta_t_mtz.append(f'< 10')
            elif self.calc_delta_t_mtz == 9999:
                self.list_delta_t_mtz.append(f'неисправен')
            else:
                self.list_delta_t_mtz.append(f'{self.calc_delta_t_mtz:.1f}')
            self.__mysql_conn.mysql_add_message(f'уставка МТЗ {self.list_ust_mtz_num[k]}  '
                                                f'дельта t: {self.calc_delta_t_mtz:.1f} '
                                                f'дельта %: {calc_delta_percent_mtz:.2f}')
            self.__fault.debug_msg(f'положение входов \t {in_a5 = } (False) {in_a6 = } (True)', 'blue')
            self.__reset.stop_procedure_3()
            if in_a5 is False and in_a6 is True:
                if self.__subtest_45():
                    self.__fault.debug_msg("подтест 4.5 пройден", 'green')
                    k += 1
                    continue
                else:
                    self.__fault.debug_msg("подтест 4.5 не пройден", 'red')
                    self.__mysql_conn.mysql_ins_result('неисправен', '4')
                    k += 1
                    continue
            else:
                if self.__subtest_42(i, k):
                    self.__fault.debug_msg("подтест 4.2 пройден", 'green')
                    k += 1
                    continue
                else:
                    self.__fault.debug_msg("подтест 4.2 не пройден", 'red')
                    self.__mysql_conn.mysql_ins_result('неисправен', '4')
                    k += 1
                    continue
        self.__mysql_conn.mysql_ins_result('исправен', '4')
        self.__fault.debug_msg(f'{self.list_result_mtz}', 'orange')
        self.__fault.debug_msg("тест 4 пройден", 'green')
        return True

    def st_test_50_bkz_3mk(self) -> bool:
        """
        Тест 5. Проверка срабатывания защиты ТЗП блока по уставкам
        """
        if my_msg(self.msg_4):
            pass
        else:
            return False
        self.__mysql_conn.mysql_ins_result('идет тест 5', '5')
        m = 0
        for n in self.list_ust_tzp_volt:
            self.__reset.sbros_zashit_kl30_1s5()
            msg_result_tzp = my_msg_2(f'{self.msg_5} {self.list_ust_tzp_num[m]}')
            if msg_result_tzp == 0:
                pass
            elif msg_result_tzp == 1:
                return False
            elif msg_result_tzp == 2:
                self.__mysql_conn.mysql_add_message(f'уставка ТЗП {self.list_ust_tzp_num[m]} пропущена')
                self.list_delta_percent_tzp.append('пропущена')
                self.list_delta_t_tzp.append('пропущена')
                m += 1
                continue
            if self.__proc.procedure_1_24_34(coef_volt=self.coef_volt, setpoint_volt=n):
                pass
            else:
                self.__mysql_conn.mysql_ins_result('неисправен', '5')
                return False
            # Δ%= 0.06075*(U4)2 + 8.887875*U4
            meas_volt_test5 = self.__read_mb.read_analog()
            self.__fault.debug_msg(f'напряжение \t {meas_volt_test5}', 'orange')
            calc_delta_percent_tzp = 0.06075 * meas_volt_test5 ** 2 + 8.887875 * meas_volt_test5
            self.list_delta_percent_tzp.append(f'{calc_delta_percent_tzp:.2f}')
            self.__fault.debug_msg(f'дельта % \t {calc_delta_percent_tzp:.2f}', 'orange')
            # 5.4.  Проверка срабатывания блока от сигнала нагрузки:
            self.__mysql_conn.mysql_ins_result('идет тест 5.4', '5')
            self.__mysql_conn.progress_level(0.0)
            calc_delta_t_tzp = self.__delta_t_tzp()
            self.__mysql_conn.progress_level(0.0)
            self.__fault.debug_msg(f'дельта t \t {calc_delta_t_tzp:.1f}', 'orange')
            self.list_delta_t_tzp.append(f'{calc_delta_t_tzp:.1f}')
            self.__mysql_conn.mysql_add_message(f'уставка ТЗП {self.list_ust_tzp_num[m]}: '
                                                f'дельта t: {calc_delta_t_tzp:.1f}, '
                                                f'дельта %: {calc_delta_percent_tzp:.2f}')
            self.__reset.sbros_kl63_proc_all()
            if calc_delta_t_tzp != 0:
                in_a5, in_a6 = self.__inputs_a()
                if calc_delta_t_tzp <= 360 and in_a5 is True and in_a6 is False:
                    if self.__subtest_56():
                        m += 1
                        continue
                    else:
                        self.__mysql_conn.mysql_ins_result('неисправен', '5')
                        m += 1
                        continue
                elif calc_delta_t_tzp > 360 and in_a5 is False:
                    self.__mysql_conn.mysql_error(327)
                    if self.__subtest_55():
                        m += 1
                        continue
                    else:
                        self.__mysql_conn.mysql_ins_result('неисправен', '5')
                        m += 1
                        continue
                elif calc_delta_t_tzp > 360 and in_a6 is True:
                    self.__mysql_conn.mysql_error(328)
                    if self.__subtest_55():
                        m += 1
                        continue
                    else:
                        self.__mysql_conn.mysql_ins_result('неисправен', '5')
                        m += 1
                        continue
                elif calc_delta_t_tzp < 360 and in_a5 is True and in_a6 is True:
                    self.__mysql_conn.mysql_error(328)
                    if self.__subtest_55():
                        m += 1
                        continue
                    else:
                        self.__mysql_conn.mysql_ins_result('неисправен', '5')
                        m += 1
                        continue
            else:
                self.__mysql_conn.mysql_ins_result('неисправен', '5')
                m += 1
                continue
        self.__mysql_conn.mysql_ins_result('исправен', '5')
        return True

    def __subtest_42(self, i, k):
        """
        3.2. Формирование нагрузочного сигнала 1,1*calc_volt[i]:
        """
        self.__mysql_conn.mysql_ins_result('идет тест 4.2', '4')
        self.__reset.sbros_zashit_kl30_1s5()
        in_a5, in_a6 = self.__inputs_a()
        self.__fault.debug_msg(f'положение входов \t {in_a5 = } (True), {in_a6 = } (True)', 'blue')
        if in_a5 is True and in_a6 is True:
            pass
        else:
            if in_a5 is False:
                self.__mysql_conn.mysql_error(325)
            elif in_a5 is False:
                self.__mysql_conn.mysql_error(326)
            return False
        if self.__proc.procedure_1_25_35(coef_volt=self.coef_volt, setpoint_volt=i):
            pass
        else:
            return False
        meas_volt_test4 = self.__read_mb.read_analog()
        calc_delta_percent_mtz = meas_volt_test4 * 9.19125
        self.__fault.debug_msg(f'{calc_delta_percent_mtz:.2f}', 'orange')
        self.list_delta_percent_mtz[-1] = f'{calc_delta_percent_mtz:.2f}'
        # 3.2.2.  Проверка срабатывания блока от сигнала нагрузки:
        self.__mysql_conn.mysql_ins_result('идет тест 4.2.2', '4')
        for wq in range(4):
            self.calc_delta_t_mtz = self.__ctrl_kl.ctrl_ai_code_v0(code=105)
            self.__mysql_conn.mysql_add_message(f'уставка МТЗ {self.list_ust_mtz_num[k]}:  '
                                                f'дельта t: {self.calc_delta_t_mtz:.1f}')
            if self.calc_delta_t_mtz == 9999:
                self.__reset.sbros_zashit_kl30_1s5()
                sleep(3)
                wq += 1
                continue
            else:
                wq = 0
                break
        self.__fault.debug_msg(f'дельта t \t {self.calc_delta_t_mtz}', 'orange')
        if self.calc_delta_t_mtz < 10:
            self.list_delta_t_mtz[-1] = f'< 10'
        elif self.calc_delta_t_mtz == 9999:
            self.list_delta_t_mtz[-1] = f'неисправен'
        else:
            self.list_delta_t_mtz[-1] = f'{self.calc_delta_t_mtz:.1f}'
        self.__mysql_conn.mysql_add_message(f'уставка МТЗ {self.list_ust_mtz_num[k]} '
                                            f'дельта t: {self.calc_delta_t_mtz:.1f}')
        self.__reset.stop_procedure_3()
        in_a5, in_a6 = self.__inputs_a()
        self.__fault.debug_msg(f'положение входов \t {in_a5 = } (False), {in_a6 = } (True)', 'blue')
        if in_a5 is False and in_a6 is True:
            if self.__subtest_45():
                return True
            else:
                return False
        elif in_a5 is True:
            self.__mysql_conn.mysql_error(323)
            if self.__subtest_43():
                return True
            else:
                return False
        elif in_a6 is False:
            self.__mysql_conn.mysql_error(324)
            if self.__subtest_43():
                return True
            else:
                return False

    def __subtest_43(self):
        self.__mysql_conn.mysql_ins_result('идет тест 4.3', '4')
        self.__reset.sbros_zashit_kl30_1s5()
        in_a5, in_a6 = self.__inputs_a()
        self.__fault.debug_msg(f'положение входов \t {in_a5 = } (True), {in_a6 = } (True)', 'blue')
        if in_a5 is True and in_a6 is True:
            pass
        else:
            if in_a5 is False:
                self.__mysql_conn.mysql_error(325)
            elif in_a6 is False:
                self.__mysql_conn.mysql_error(326)
            return False
        return True

    def __subtest_45(self):
        self.__mysql_conn.mysql_ins_result('идет тест 4.5', '4')
        # 4.5. Расчет времени и кратности срабатывания
        self.__reset.sbros_zashit_kl30_1s5()
        in_a5, in_a6 = self.__inputs_a()
        self.__fault.debug_msg(f'положение входов \t {in_a5 = } (True), {in_a6 = } (True)', 'blue')
        if in_a5 is True and in_a6 is True:
            self.__fault.debug_msg("положение входов соответствует", 'green')
            return True
        elif in_a5 is False:
            self.__mysql_conn.mysql_error(325)
            return False
        elif in_a6 is False:
            self.__mysql_conn.mysql_error(326)
            return False

    def __subtest_55(self):
        self.__mysql_conn.mysql_ins_result('идет тест 5.5', '5')
        self.__fault.debug_msg('идет тест 5.5', 'blue')
        self.__reset.sbros_zashit_kl30_1s5()
        in_a5, in_a6 = self.__inputs_a()
        self.__fault.debug_msg(f'положение входов \t {in_a5 = } (True), {in_a6 = } (True)', 'blue')
        if in_a5 is True and in_a6 is True:
            return True
        elif in_a5 is False:
            self.__mysql_conn.mysql_error(329)
            return False
        elif in_a6 is False:
            self.__mysql_conn.mysql_error(330)
            return False

    def __subtest_56(self):
        self.__mysql_conn.mysql_ins_result('идет тест 5.6', '5')
        self.__fault.debug_msg('идет тест 5.6', 'blue')
        self.__reset.sbros_zashit_kl30_1s5()
        in_a5, in_a6 = self.__inputs_a()
        self.__fault.debug_msg(f'положение входов \t {in_a5 = } (True), {in_a6 = } (True)', 'blue')
        if in_a5 is True and in_a6 is True:
            return True
        elif in_a5 is False:
            self.__mysql_conn.mysql_error(329)
            return False
        elif in_a6 is False:
            self.__mysql_conn.mysql_error(330)
            return False

    def __inputs_a0(self):
        in_a0 = self.__read_mb.read_discrete(0)
        if in_a0 is None:
            # logging.error(f'нет связи с контроллером')
            raise ModbusConnectException(f'нет связи с контроллером')
        return in_a0

    def __inputs_a(self):
        in_a5 = self.__read_mb.read_discrete(5)
        in_a6 = self.__read_mb.read_discrete(6)
        if in_a5 is None or in_a5 is None:
            raise ModbusConnectException(f'нет связи с контроллером')
        return in_a5, in_a6

    def __inputs_b(self):
        in_b0 = self.__read_mb.read_discrete(8)
        in_b1 = self.__read_mb.read_discrete(9)
        if in_b0 is None or in_b1 is None:
            raise ModbusConnectException(f'нет связи с контроллером')
        return in_b0, in_b1

    def __inputs_b1(self):
        in_b1 = self.__read_mb.read_discrete(9)
        if in_b1 is None:
            raise ModbusConnectException(f'нет связи с контроллером')
        return in_b1

    def __inputs_a6(self):
        in_a6 = self.__read_mb.read_discrete(6)
        if in_a6 is None:
            raise ModbusConnectException(f'нет связи с контроллером')
        return in_a6

    def __delta_t_tzp(self):
        self.__ctrl_kl.ctrl_relay('KL63', True)
        in_b1 = self.__inputs_b1()
        i = 0
        while in_b1 is False and i <= 20:
            in_b1 = self.__inputs_b1()
            i += 1
        if in_b1 is True:
            start_timer = time()
            meas_time = 0
            in_a6 = self.__inputs_a6()
            while in_a6 is True and meas_time <= 370:
                in_a6 = self.__inputs_a6()
                meas_time = time() - start_timer
                self.__mysql_conn.progress_level(meas_time)
            if in_a6 is False:
                stop_timer = time()
                delta_t_calc = stop_timer - start_timer
                return delta_t_calc
            else:
                return 0
        else:
            return 0

    def st_test_bkz_3mk(self) -> bool:
        if self.st_test_0_bkz_3mk():
            if self.st_test_10_bkz_3mk():
                if self.st_test_11_bkz_3mk():
                    if self.st_test_12_bkz_3mk():
                        if self.st_test_20_bkz_3mk():
                            if self.st_test_30_bkz_3mk():
                                if self.st_test_40_bkz_3mk():
                                    if self.st_test_50_bkz_3mk():
                                        return True
        return False

    def result_test_bkz_3mk(self):
        for g1 in range(len(self.list_delta_percent_mtz)):
            self.list_result_mtz.append((self.list_ust_mtz_num[g1],
                                         self.list_delta_percent_mtz[g1],
                                         self.list_delta_t_mtz[g1]))
        self.__mysql_conn.mysql_pmz_result(self.list_result_mtz)
        for g2 in range(len(self.list_delta_percent_tzp)):
            self.list_result_tzp.append((self.list_ust_tzp_num[g2],
                                         self.list_delta_percent_tzp[g2],
                                         self.list_delta_t_tzp[g2]))
        self.__mysql_conn.mysql_tzp_result(self.list_result_tzp)


if __name__ == '__main__':
    test_bkz_3mk = TestBKZ3MK()
    reset_test_bkz_3mk = ResetRelay()
    mysql_conn_bkz_3mk = MySQLConnect()
    fault = Bug(True)
    try:
        if test_bkz_3mk.st_test_bkz_3mk():
            mysql_conn_bkz_3mk.mysql_block_good()
            test_bkz_3mk.result_test_bkz_3mk()
            my_msg('Блок исправен', 'green')
        else:
            mysql_conn_bkz_3mk.mysql_block_bad()
            test_bkz_3mk.result_test_bkz_3mk()
            my_msg('Блок неисправен', 'red')
    except OSError:
        my_msg("ошибка системы", 'red')
    except SystemError:
        my_msg("внутренняя ошибка", 'red')
    except ModbusConnectException as mce:
        fault.debug_msg(mce, 'red')
        my_msg(f'{mce}', 'red')
    finally:
        reset_test_bkz_3mk.reset_all()
        sys.exit()
