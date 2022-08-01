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
import logging

from time import time, sleep

from general_func.exception import *
from general_func.database import *
from general_func.modbus import *
from general_func.procedure import *
from general_func.reset import ResetRelay, ResetProtection
from general_func.subtest import ProcedureFull
from gui.msgbox_1 import *
from gui.msgbox_2 import *

__all__ = ["TestBTZT"]


class TestBTZT:

    def __init__(self):
        self.reset_relay = ResetRelay()
        self.reset_protect = ResetProtection()
        self.proc = Procedure()
        self.proc_full = ProcedureFull()
        self.read_mb = ReadMB()
        self.ctrl_kl = CtrlKL()
        self.di_read = DIRead()
        self.mysql_conn = MySQLConnect()

        self.ust_test: float = 80.0
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
        self.health_flag: bool = False

        self.msg_1 = "Переключите оба тумблера на корпусе блока в положение «Работа» и установите " \
                     "регуляторы уставок в положение 1 (1-11) и положение 1.0 (0.5-1.0)"
        self.msg_2 = "Переключите тумблер ПМЗ (1-11) на корпусе блока в положение «Проверка»"
        self.msg_9 = "Переключите тумблер ПМЗ (1-11) в положение «Работа»"
        self.msg_3 = "«Переключите тумблер ТЗП (0.5-1.0) в положение «Проверка»"
        self.msg_8 = "Переключите тумблер ТЗП (0.5…1.0) на корпусе блока в положение «Работа»"
        self.msg_5 = f'Установите регулятор уставок ПМЗ (1-11) на блоке в положение'
        self.msg_7 = f'Установите регулятор уставок ТЗП (0.5…1.0) на блоке в положение'

        logging.basicConfig(filename="C:\Stend\project_class\TestBTZT.log",
                            filemode="w",
                            level=logging.DEBUG,
                            encoding="utf-8",
                            format='[%(asctime)s: %(name)s: %(levelname)s] %(message)s')
        logging.getLogger('mysql').setLevel('WARNING')
        self.logger = logging.getLogger(__name__)
        # self.logger.addHandler(logging.StreamHandler(self.logger.setLevel(10)))

    def st_test_10_btz_t(self) -> bool:
        """
        Тест 1. Проверка исходного состояния блока:
        """
        self.di_read.di_read('in_a0')
        if my_msg(self.msg_1):
            pass
        else:
            return False
        self.logger.debug("тест 1", 'blue')
        self.mysql_conn.mysql_ins_result('идет тест 1', '1')
        self.ctrl_kl.ctrl_relay('KL21', True)
        self.reset_protect.sbros_zashit_kl30()
        in_a1, in_a2, in_a5, in_a6 = self.di_read.di_read('in_a1', 'in_a2', 'in_a5', 'in_a6')
        if in_a1 is False and in_a5 is True and in_a2 is False and in_a6 is True:
            pass
        else:
            self.mysql_conn.mysql_ins_result('неисправен', '1')
            if in_a1 is True:
                self.logger.debug("положение входа 1 не соответствует", 'red')
                self.mysql_conn.mysql_error(390)
            elif in_a5 is False:
                self.logger.debug("положение входа 5 не соответствует", 'red')
                self.mysql_conn.mysql_error(391)
            elif in_a2 is True:
                self.logger.debug("положение входа 2 не соответствует", 'red')
                self.mysql_conn.mysql_error(392)
            elif in_a6 is False:
                self.logger.debug("положение входа 6 не соответствует", 'red')
                self.mysql_conn.mysql_error(393)
            return False
        self.logger.debug("положение выходов блока соответствует", 'green')
        return True

    def st_test_11_btz_t(self) -> bool:
        """
        # 1.1. Проверка вероятности наличия короткого замыкания
        # на входе измерительной цепи блока
        """
        if self.proc_full.procedure_1_full(test_num=1, subtest_num=1.1, coef_min_volt=0.4):
            return True
        return False

    def st_test_12_btz_t(self) -> bool:
        """
        1.2. Определение коэффициента Кс отклонения фактического напряжения от номинального
        """
        self.logger.debug("тест 1.2", 'blue')
        self.mysql_conn.mysql_ins_result('идет тест 1.2', '1')
        self.coef_volt = self.proc.procedure_1_22_32()
        if self.coef_volt != 0.0:
            pass
        else:
            self.mysql_conn.mysql_ins_result('неисправен', '1')
            return False
        self.mysql_conn.mysql_ins_result('исправен', '1')
        self.reset_relay.stop_procedure_32()
        self.logger.debug("тест 1 завершен", 'blue')
        return True

    def st_test_20_btz_t(self) -> bool:
        """
        Тест 2. Проверка работоспособности защиты ПМЗ блока в режиме «Проверка»
        """
        if my_msg(self.msg_2):
            pass
        else:
            return False
        self.logger.debug("тест 2", 'blue')
        self.mysql_conn.mysql_ins_result('идет тест 2.1', '2')
        if self.proc.procedure_x4_to_x5(coef_volt=self.coef_volt, setpoint_volt=self.ust_test):
            return True
        self.mysql_conn.mysql_ins_result('неисправен', '2')
        return False

    def st_test_21_btz_t(self) -> bool:
        """
        2.2.  Проверка срабатывания блока от сигнала нагрузки:
        """
        self.logger.debug("тест 2.2", 'blue')
        self.mysql_conn.mysql_ins_result('идет тест 2.2', '2')
        self.ctrl_kl.ctrl_relay('KL63', True)
        sleep(2)
        self.ctrl_kl.ctrl_relay('KL63', False)
        in_a1, in_a2, in_a5, in_a6 = self.di_read.di_read('in_a1', 'in_a2', 'in_a5', 'in_a6')
        if in_a1 is False and in_a5 is True and in_a2 is True and in_a6 is False:
            pass
        else:
            self.mysql_conn.mysql_ins_result('неисправен', '2')
            if in_a1 is True:
                self.logger.debug("положение входа 1 не соответствует", 'red')
                self.mysql_conn.mysql_error(395)
            elif in_a5 is False:
                self.logger.debug("положение входа 5 не соответствует", 'red')
                self.mysql_conn.mysql_error(396)
            elif in_a2 is False:
                self.logger.debug("положение входа 2 не соответствует", 'red')
                self.mysql_conn.mysql_error(397)
            elif in_a6 is True:
                self.logger.debug("положение входа 6 не соответствует", 'red')
                self.mysql_conn.mysql_error(398)
            return False
        self.logger.debug("положение выходов блока соответствует", 'green')
        self.reset_relay.stop_procedure_3()
        return True

    def st_test_22_btz_t(self) -> bool:
        """
        2.4.2. Сброс защит после проверки
        """
        self.logger.debug("тест 2.4", 'blue')
        self.mysql_conn.mysql_ins_result('идет тест 2.4', '2')
        self.reset_protect.sbros_zashit_kl30()
        in_a1, in_a2, in_a5, in_a6 = self.di_read.di_read('in_a1', 'in_a2', 'in_a5', 'in_a6')
        if in_a1 is False and in_a5 is True and in_a2 is False and in_a6 is True:
            pass
        else:
            self.mysql_conn.mysql_ins_result('неисправен', '2')
            if in_a1 is True:
                self.logger.debug("положение входа 1 не соответствует", 'red')
                self.mysql_conn.mysql_error(399)
            elif in_a5 is False:
                self.logger.debug("положение входа 5 не соответствует", 'red')
                self.mysql_conn.mysql_error(400)
            elif in_a2 is True:
                self.logger.debug("положение входа 2 не соответствует", 'red')
                self.mysql_conn.mysql_error(401)
            elif in_a6 is False:
                self.logger.debug("положение входа 6 не соответствует", 'red')
                self.mysql_conn.mysql_error(402)
            return False
        self.logger.debug("положение выходов блока соответствует", 'green')
        self.mysql_conn.mysql_ins_result('исправен', '2')
        self.logger.debug("тест 2 завершен", 'blue')
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
        self.logger.debug("тест 3", 'blue')
        self.mysql_conn.mysql_ins_result('идет тест 3.1', '3')
        in_a1, in_a2, in_a5, in_a6 = self.di_read.di_read('in_a1', 'in_a2', 'in_a5', 'in_a6')
        if in_a1 is True and in_a5 is False and in_a2 is False and in_a6 is True:
            pass
        else:
            self.mysql_conn.mysql_ins_result('неисправен', '3')
            if in_a1 is False:
                self.logger.debug("положение входа 1 не соответствует", 'red')
                self.mysql_conn.mysql_error(403)
            elif in_a5 is True:
                self.logger.debug("положение входа 5 не соответствует", 'red')
                self.mysql_conn.mysql_error(404)
            elif in_a2 is True:
                self.logger.debug("положение входа 2 не соответствует", 'red')
                self.mysql_conn.mysql_error(405)
            elif in_a6 is False:
                self.logger.debug("положение входа 6 не соответствует", 'red')
                self.mysql_conn.mysql_error(406)
            return False
        self.logger.debug("положение выходов блока соответствует", 'green')
        return True

    def st_test_31_btz_t(self) -> bool:
        """
        3.2. Сброс защит после проверки
        """
        self.logger.debug("тест 3.2", 'blue')
        self.mysql_conn.mysql_ins_result('идет тест 3.2', '3')
        if my_msg(self.msg_8):
            pass
        else:
            return False
        self.reset_protect.sbros_zashit_kl30()
        sleep(1)
        in_a1, in_a2, in_a5, in_a6 = self.di_read.di_read('in_a1', 'in_a2', 'in_a5', 'in_a6')
        if in_a1 is False and in_a5 is True and in_a2 is False and in_a6 is True:
            pass
        else:
            self.mysql_conn.mysql_ins_result('неисправен', '3')
            if in_a1 is True:
                self.logger.debug("положение входа 1 не соответствует", 'red')
                self.mysql_conn.mysql_error(407)
            elif in_a5 is False:
                self.logger.debug("положение входа 5 не соответствует", 'red')
                self.mysql_conn.mysql_error(408)
            elif in_a2 is True:
                self.logger.debug("положение входа 2 не соответствует", 'red')
                self.mysql_conn.mysql_error(409)
            elif in_a6 is False:
                self.logger.debug("положение входа 6 не соответствует", 'red')
                self.mysql_conn.mysql_error(410)
            return False
        self.logger.debug("положение выходов блока соответствует", 'green')
        self.mysql_conn.mysql_ins_result('исправен', '3')
        self.logger.debug("тест 3 завершен", 'blue')
        return True

    def st_test_40_btz_t(self) -> bool:
        """
        Тест 4. Проверка срабатывания защиты ПМЗ блока по уставкам
        """
        self.logger.debug("тест 4", 'blue')
        self.mysql_conn.mysql_ins_result('идет тест 4', '4')
        k = 0
        for i in self.list_ust_pmz_volt:
            msg_result = my_msg_2(f'{self.msg_5} {self.list_ust_pmz_num[k]}')
            if msg_result == 0:
                pass
            elif msg_result == 1:
                return False
            elif msg_result == 2:
                self.mysql_conn.mysql_add_message(f'уставка {self.list_ust_pmz_num[k]} пропущена')
                self.list_delta_percent_pmz.append('пропущена')
                self.list_delta_t_pmz.append('пропущена')
                k += 1
                continue
            self.mysql_conn.mysql_ins_result('идет тест 4.1', '4')
            if self.proc.procedure_x4_to_x5(coef_volt=self.coef_volt, setpoint_volt=i):
                pass
            else:
                self.mysql_conn.mysql_ins_result('неисправен', '4')
                return False
            meas_volt_pmz = self.read_mb.read_analog()
            # Δ%= 2.7938*U4
            calc_delta_percent_pmz = 2.7938 * meas_volt_pmz
            self.list_delta_percent_pmz.append(f'{calc_delta_percent_pmz:.2f}')
            # 4.1.  Проверка срабатывания блока от сигнала нагрузки:
            self.logger.debug("тест 4.1", 'blue')
            self.mysql_conn.mysql_ins_result('идет тест 4.2', '4')
            for qw in range(4):
                self.calc_delta_t_pmz = self.ctrl_kl.ctrl_ai_code_v0(103)
                self.logger.debug(f'дельта t: {self.calc_delta_t_pmz:.1f}', 'orange')
                if self.calc_delta_t_pmz == 9999:
                    self.reset_protect.sbros_zashit_kl30()
                    sleep(3)
                    qw += 1
                    continue
                elif 3000 < self.calc_delta_t_pmz < 9999:
                    self.reset_protect.sbros_zashit_kl30()
                    sleep(3)
                    qw += 1
                    continue
                else:
                    break
            in_a1, in_a2, in_a5, in_a6 = self.di_read.di_read('in_a1', 'in_a2', 'in_a5', 'in_a6')
            self.logger.debug(f'дельта t: {self.calc_delta_t_pmz}', 'orange')
            self.mysql_conn.mysql_add_message(f'уставка {self.list_ust_pmz_num[k]} '
                                              f'дельта t: {self.calc_delta_t_pmz:.1f}')
            self.mysql_conn.mysql_add_message(f'уставка {self.list_ust_pmz_num[k]} '
                                              f'дельта %: {calc_delta_percent_pmz:.2f}')
            if self.calc_delta_t_pmz < 10:
                self.list_delta_t_pmz.append(f'< 10')
            elif self.calc_delta_t_pmz > 3000:
                self.list_delta_t_pmz.append(f'> 3000')
            else:
                self.list_delta_t_pmz.append(f'{self.calc_delta_t_pmz:.1f}')
            self.reset_relay.stop_procedure_3()
            if in_a1 is False and in_a5 is True and in_a2 is True and in_a6 is False:
                self.logger.debug("положение выходов блока соответствует", 'green')
                if self.subtest_45():
                    k += 1
                    continue
                else:
                    self.mysql_conn.mysql_ins_result('неисправен', '4')
                    return False
            else:
                self.logger.debug("положение выходов блока не соответствует", 'red')
                self.mysql_conn.mysql_ins_result('неисправен', '4')
                self.mysql_conn.mysql_error(389)
                if self.subtest_42(i, k):
                    if self.subtest_45():
                        k += 1
                        continue
                    else:
                        self.mysql_conn.mysql_ins_result('неисправен', '4')
                        return False
                else:
                    if self.subtest_43():
                        k += 1
                        continue
                    else:
                        self.mysql_conn.mysql_ins_result('неисправен', '4')
                        return False
        self.mysql_conn.mysql_ins_result('исправен', '4')
        self.logger.debug("тест 4 завершен", 'blue')
        return True

    def st_test_50_btz_t(self) -> bool:
        """
        Тест 5. Проверка срабатывания защиты ТЗП блока по уставкам
        """
        self.logger.debug("тест 5", 'blue')
        self.mysql_conn.mysql_ins_result('идет тест 5', '5')
        m = 0
        for n in self.list_ust_tzp_volt:
            msg_result = my_msg_2(f'{self.msg_7} {self.list_ust_tzp_num[m]}')
            if msg_result == 0:
                pass
            elif msg_result == 1:
                return False
            elif msg_result == 2:
                self.mysql_conn.mysql_add_message(f'уставка {self.list_ust_tzp_num[m]} пропущена')
                self.list_delta_percent_tzp.append('пропущена')
                self.list_delta_t_tzp.append('пропущена')
                m += 1
                continue
            self.mysql_conn.mysql_ins_result('идет тест 5.1', '5')
            if self.proc.procedure_x4_to_x5(coef_volt=self.coef_volt, setpoint_volt=n):
                pass
            else:
                self.mysql_conn.mysql_ins_result('неисправен', '5')
                return False
            meas_volt_tzp = self.read_mb.read_analog()
            # Δ%= 0.0044*U42[i]+2.274* U4[i]
            calc_delta_percent_tzp = 0.0044 * meas_volt_tzp ** 2 + 2.274 * meas_volt_tzp
            self.list_delta_percent_tzp.append(f'{calc_delta_percent_tzp:.2f}')
            # 5.4.  Проверка срабатывания блока от сигнала нагрузки:
            self.mysql_conn.progress_level(0.0)
            self.logger.debug("тест 5.4", 'blue')
            self.mysql_conn.mysql_ins_result('идет тест 5.4', '5')
            self.ctrl_kl.ctrl_relay('KL63', True)
            in_b1, *_ = self.di_read.di_read('in_b1')
            while in_b1 is False:
                in_b1, *_ = self.di_read.di_read('in_b1')
            start_timer_2 = time()
            in_a5, *_ = self.di_read.di_read('in_a5')
            sub_timer = 0
            while in_a5 is True and sub_timer <= 360:
                sleep(0.2)
                sub_timer = time() - start_timer_2
                self.logger.debug(f'времени прошло {sub_timer:.1f}', 'orange')
                self.mysql_conn.progress_level(sub_timer)
                self.logger.debug(f'{in_a5=}', 'purple')
                in_a5, *_ = self.di_read.di_read('in_a5')
            stop_timer_2 = time()
            calc_delta_t_tzp = stop_timer_2 - start_timer_2
            self.mysql_conn.progress_level(0.0)
            self.logger.debug(f'дельта t: {calc_delta_t_tzp:.1f}', 'orange')
            self.ctrl_kl.ctrl_relay('KL63', False)
            self.list_delta_t_tzp.append(f'{calc_delta_t_tzp:.1f}')
            self.mysql_conn.mysql_add_message(f'уставка {self.list_ust_tzp_num[m]} '
                                              f'дельта t: {calc_delta_t_tzp:.1f}')
            self.mysql_conn.mysql_add_message(f'уставка {self.list_ust_tzp_num[m]} '
                                              f'дельта %: {calc_delta_percent_tzp:.2f}')
            in_a1, in_a2, in_a5, in_a6 = self.di_read.di_read('in_a1', 'in_a2', 'in_a5', 'in_a6')
            if in_a1 is True and in_a5 is False and in_a2 is False and in_a6 is True and calc_delta_t_tzp <= 360:
                self.logger.debug("входа соответствуют ", 'green')
                if self.subtest_56():
                    m += 1
                    continue
                else:
                    self.mysql_conn.mysql_ins_result('неисправен', '5')
                    return False
            else:
                self.logger.debug("входа не соответствуют ", 'red')
                self.mysql_conn.mysql_ins_result('неисправен', '5')
                self.mysql_conn.mysql_error(411)
                if self.subtest_55():
                    m += 1
                    continue
                else:
                    self.mysql_conn.mysql_ins_result('неисправен', '5')
                    return False
        self.mysql_conn.mysql_ins_result('исправен', '5')
        return True

    def subtest_42(self, i, k) -> bool:
        """
        4.2. Формирование нагрузочного сигнала 1,1*calc_volt[i]:
        :return:
        """
        self.logger.debug("тест 4.2", 'blue')
        self.mysql_conn.mysql_ins_result('идет тест 4.2', '4')
        self.reset_protect.sbros_zashit_kl30()
        sleep(1)
        in_a1, in_a2, in_a5, in_a6 = self.di_read.di_read('in_a1', 'in_a2', 'in_a5', 'in_a6')
        if in_a1 is False and in_a5 is True and in_a2 is False and in_a6 is True:
            pass
        else:
            self.mysql_conn.mysql_ins_result('неисправен', '4')
            if in_a1 is True:
                self.mysql_conn.mysql_error(399)
            elif in_a5 is False:
                self.mysql_conn.mysql_error(400)
            elif in_a2 is True:
                self.mysql_conn.mysql_error(401)
            elif in_a6 is False:
                self.mysql_conn.mysql_error(402)
            return False
        if self.proc.procedure_1_24_34(coef_volt=self.coef_volt, setpoint_volt=i, factor=1.1):
            pass
        else:
            self.mysql_conn.mysql_ins_result('неисправен', '4')
        meas_volt_pmz = self.read_mb.read_analog()
        # Δ%= 2.7938*U4
        calc_delta_percent_pmz = 2.7938 * meas_volt_pmz
        self.list_delta_percent_pmz[-1] = f'{calc_delta_percent_pmz:.2f}'
        # 4.2.2.  Проверка срабатывания блока от сигнала нагрузки:
        self.logger.debug("тест 4.2.2", 'blue')
        self.mysql_conn.mysql_ins_result('идет тест 4.2.2', '4')
        for wq in range(4):
            self.calc_delta_t_pmz = self.ctrl_kl.ctrl_ai_code_v0(103)
            self.logger.debug(f'дельта t: {self.calc_delta_t_pmz}', 'orange')
            if self.calc_delta_t_pmz == 9999:
                self.reset_protect.sbros_zashit_kl30()
                sleep(3)
                wq += 1
                continue
            elif 3000 < self.calc_delta_t_pmz < 9999:
                self.reset_protect.sbros_zashit_kl30()
                sleep(3)
                wq += 1
                continue
            else:
                break
        in_a1, in_a2, in_a5, in_a6 = self.di_read.di_read('in_a1', 'in_a2', 'in_a5', 'in_a6')
        self.logger.debug(f'дельта t: {self.calc_delta_t_pmz:.1f}', 'orange')
        self.mysql_conn.mysql_add_message(f'уставка {self.list_ust_pmz_num[k]} '
                                          f'дельта t: {self.calc_delta_t_pmz:.1f}')
        self.mysql_conn.mysql_add_message(f'уставка {self.list_ust_pmz_num[k]} '
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
        self.reset_relay.stop_procedure_3()
        return True

    def subtest_43(self):
        self.logger.debug("тест 4.3", 'blue')
        self.mysql_conn.mysql_ins_result('идет тест 4.3', '4')
        self.reset_protect.sbros_zashit_kl30()
        sleep(1)
        in_a1, in_a2, in_a5, in_a6 = self.di_read.di_read('in_a1', 'in_a2', 'in_a5', 'in_a6')
        if in_a1 is False and in_a5 is True and in_a2 is False and in_a6 is True:
            pass
        else:
            self.mysql_conn.mysql_ins_result('неисправен', '4')
            if in_a1 is True:
                self.mysql_conn.mysql_error(399)
            elif in_a5 is False:
                self.mysql_conn.mysql_error(400)
            elif in_a2 is True:
                self.mysql_conn.mysql_error(401)
            elif in_a6 is False:
                self.mysql_conn.mysql_error(402)
            return False
        return True

    def subtest_45(self):
        self.logger.debug("тест 4.5", 'blue')
        self.mysql_conn.mysql_ins_result('идет тест 4.5', '4')
        self.reset_protect.sbros_zashit_kl30()
        sleep(1)
        in_a1, in_a2, in_a5, in_a6 = self.di_read.di_read('in_a1', 'in_a2', 'in_a5', 'in_a6')
        self.logger.debug(f'{in_a1 = } (False), {in_a2 = } (True), '
                             f'{in_a5 = } (False), {in_a6 = } (True)', 'purple')
        if in_a1 is False and in_a5 is True and in_a2 is False and in_a6 is True:
            pass
        else:
            self.mysql_conn.mysql_ins_result('неисправен', '4')
            if in_a1 is True:
                self.mysql_conn.mysql_error(399)
            elif in_a5 is False:
                self.mysql_conn.mysql_error(400)
            elif in_a2 is True:
                self.mysql_conn.mysql_error(401)
            elif in_a6 is False:
                self.mysql_conn.mysql_error(402)
            return False
        return True

    def subtest_55(self):
        self.logger.debug("тест 5.5", 'blue')
        self.mysql_conn.mysql_ins_result('идет тест 5.5', '5')
        self.reset_relay.stop_procedure_3()
        self.reset_protect.sbros_zashit_kl30()
        sleep(1)
        in_a1, in_a2, in_a5, in_a6 = self.di_read.di_read('in_a1', 'in_a2', 'in_a5', 'in_a6')
        if in_a1 is False and in_a5 is True and in_a2 is False and in_a6 is True:
            pass
        else:
            self.mysql_conn.mysql_ins_result('неисправен', '5')
            if in_a1 is True:
                self.mysql_conn.mysql_error(399)
            elif in_a5 is False:
                self.mysql_conn.mysql_error(400)
            elif in_a2 is True:
                self.mysql_conn.mysql_error(401)
            elif in_a6 is False:
                self.mysql_conn.mysql_error(402)
            return False
        return True

    def subtest_56(self):
        """
        5.6.1. Сброс защит после проверки
        """
        self.logger.debug("тест 5.6", 'blue')
        self.mysql_conn.mysql_ins_result('идет тест 5.6', '5')
        self.reset_relay.stop_procedure_3()
        self.reset_protect.sbros_zashit_kl30()
        sleep(1)
        in_a1, in_a2, in_a5, in_a6 = self.di_read.di_read('in_a1', 'in_a2', 'in_a5', 'in_a6')
        if in_a1 is False and in_a5 is True and in_a2 is False and in_a6 is True:
            pass
        else:
            self.mysql_conn.mysql_ins_result('неисправен', '5')
            if in_a1 is True:
                self.mysql_conn.mysql_error(399)
            elif in_a5 is False:
                self.mysql_conn.mysql_error(400)
            elif in_a2 is True:
                self.mysql_conn.mysql_error(401)
            elif in_a6 is False:
                self.mysql_conn.mysql_error(402)
            return False
        return True

    def st_test_btz_t(self) -> [bool, bool]:
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
                                                return True, self.health_flag
        return False, self.health_flag

    def result_test_btz_t(self):
        """
        сведение всех результатов измерения, и запись в БД
        """
        for g1 in range(len(self.list_delta_percent_pmz)):
            self.list_result_pmz.append((self.list_ust_pmz_num[g1],
                                         self.list_delta_percent_pmz[g1],
                                         self.list_delta_t_pmz[g1]))
        self.mysql_conn.mysql_pmz_result(self.list_result_pmz)
        for g2 in range(len(self.list_delta_percent_tzp)):
            self.list_result_tzp.append((self.list_ust_tzp_num[g2],
                                         self.list_delta_percent_tzp[g2],
                                         self.list_delta_t_tzp[g2]))
        self.mysql_conn.mysql_tzp_result(self.list_result_tzp)


if __name__ == '__main__':
    test_btz_t = TestBTZT()
    reset_test_btz_t = ResetRelay()
    mysql_conn_btz_t = MySQLConnect()
    try:
        test, health_flag = test_btz_t.st_test_btz_t()
        if test and not health_flag:
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
        my_msg(f'{mce}', 'red')
    except HardwareException as hwe:
        my_msg(f'{hwe}', 'red')
    finally:
        reset_test_btz_t.reset_all()
        sys.exit()
