#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Алгоритм проверки

Тип блока: БТЗ-3
Производитель: Нет производителя, ТЭТЗ-Инвест, Строй-энергомаш, Углеприбор.

"""

import sys
import logging

from time import sleep, time

from general_func.exception import *
from general_func.database import *
from general_func.modbus import *
from general_func.procedure import *
from general_func.reset import ResetRelay
from general_func.subtest import ProcedureFull
from gui.msgbox_1 import *
from gui.msgbox_2 import *

__all__ = ["TestBTZ3"]


class TestBTZ3:

    def __init__(self):
        self.reset = ResetRelay()
        self.proc = Procedure()
        self.proc_full = ProcedureFull()
        self.ctrl_kl = CtrlKL()
        self.read_mb = ReadMB()
        self.di_read = DIRead()
        self.mysql_conn = MySQLConnect()

        self.list_ust_tzp_num = (0.5, 0.6, 0.7, 0.8, 0.9, 1.0)
        self.list_ust_tzp = (23.7, 28.6, 35.56, 37.4, 42.6, 47.3)
        self.list_ust_pmz_num = (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11)
        self.list_ust_pmz = (67.9, 86.4, 100.1, 117.2, 140.7, 146.4, 156.6, 164.2, 175.7, 183.7, 192.1)
        self.ust_prov = 80.0
        self.list_delta_t_tzp = []
        self.list_delta_t_pmz = []
        self.list_delta_percent_tzp = []
        self.list_delta_percent_pmz = []
        self.list_result_tzp = []
        self.list_result_pmz = []

        self.coef_volt: float = 0.0
        self.calc_delta_t_pmz: float = 0.0

        self.health_flag: bool = False

        logging.basicConfig(filename="C:\Stend\project_class\TestBTZ3.log",
                            filemode="w",
                            level=logging.DEBUG,
                            encoding="utf-8",
                            format='[%(asctime)s: %(name)s: %(levelname)s] %(message)s')
        logging.getLogger('mysql').setLevel('WARNING')
        self.logger = logging.getLogger(__name__)
        # self.logger.addHandler(logging.StreamHandler(self.logger.setLevel(10)))

    def st_test_10_btz_3(self) -> bool:
        """
        Тест 1. Проверка исходного состояния блока:
        """
        self.di_read.di_read('in_a0')
        msg_1 = "Переключите оба тумблера на корпусе блока в положение «Работа» и установите " \
                "регуляторы уставок в положение 1 (1-11) и положение 1 (0.5-1)"
        if my_msg(msg_1):
            pass
        else:
            return False
        self.mysql_conn.mysql_ins_result('идёт тест 1', '1')
        self.ctrl_kl.ctrl_relay('KL21', True)
        self.sbros_zashit_kl30()
        in_a1, in_a2, in_a5, in_a6 = self.di_read.di_read('in_a1', 'in_a2', 'in_a5', 'in_a6')
        if in_a1 is False and in_a5 is True and in_a2 is False and in_a6 is True:
            pass
        else:
            self.mysql_conn.mysql_ins_result('неисправен', '1')
            if in_a1 is True:
                self.mysql_conn.mysql_error(368)
            elif in_a5 is False:
                self.mysql_conn.mysql_error(369)
            elif in_a2 is True:
                self.mysql_conn.mysql_error(370)
            elif in_a6 is False:
                self.mysql_conn.mysql_error(371)
            return False
        return True

    def st_test_11_btz_3(self) -> bool:
        """
        1.1.2. Проверка отсутствия короткого замыкания на входе измерительной части блока:
        1.2. Определение коэффициента Кс отклонения фактического напряжения от номинального
        """
        if self.proc_full.procedure_1_full(test_num=1, subtest_num=1.1):
            self.coef_volt = self.proc_full.procedure_2_full(test_num=1, subtest_num=1.2)
            return True
        return False

    def st_test_20_btz_3(self) -> bool:
        """
        Тест 2. Проверка работоспособности защиты ПМЗ блока в режиме «Проверка»
        """
        msg_2 = "Переключите тумблер ПМЗ (1-11) на корпусе блока в положение «Проверка»"
        if my_msg(msg_2):
            pass
        else:
            return False
        self.logger.debug("тест 2.1")
        self.mysql_conn.mysql_ins_result('идёт тест 2', '2')
        if self.proc.procedure_x4_to_x5(setpoint_volt=self.ust_prov, coef_volt=self.coef_volt):
            pass
        else:
            self.mysql_conn.mysql_ins_result("неисправен TV1", "2")
            return False
        return True

    def st_test_21_btz_3(self) -> bool:
        """
        # 2.2.  Проверка срабатывания блока от сигнала нагрузки:
        """
        self.logger.debug("тест 2.2")
        self.mysql_conn.mysql_ins_result('идёт тест 2.2', '2')
        self.ctrl_kl.ctrl_relay('KL63', True)
        sleep(2)
        self.ctrl_kl.ctrl_relay('KL63', False)
        in_a1, in_a2, in_a5, in_a6 = self.di_read.di_read('in_a1', 'in_a2', 'in_a5', 'in_a6')
        if in_a1 is False and in_a5 is True and in_a2 is True and in_a6 is False:
            pass
        else:
            self.logger.debug("тест 2.2 положение выходов не соответствует")
            self.mysql_conn.mysql_ins_result('неисправен', '2')
            if in_a1 is True:
                self.mysql_conn.mysql_error(373)
            elif in_a5 is False:
                self.mysql_conn.mysql_error(374)
            elif in_a2 is False:
                self.mysql_conn.mysql_error(375)
            elif in_a6 is True:
                self.mysql_conn.mysql_error(376)
            return False
        self.logger.debug("тест 2.2 положение выходов соответствует")
        self.reset.stop_procedure_3()
        return True

    def st_test_22_btz_3(self) -> bool:
        self.logger.debug("тест 2.3")
        self.sbros_zashit_kl30()
        in_a1, in_a2, in_a5, in_a6 = self.di_read.di_read('in_a1', 'in_a2', 'in_a5', 'in_a6')
        if in_a1 is False and in_a5 is True and in_a2 is False and in_a6 is True:
            pass
        else:
            self.logger.debug("тест 2.3 положение выходов не соответствует")
            self.mysql_conn.mysql_ins_result('неисправен', '2')
            if in_a1 is True:
                self.mysql_conn.mysql_error(377)
            elif in_a5 is False:
                self.mysql_conn.mysql_error(378)
            elif in_a2 is True:
                self.mysql_conn.mysql_error(379)
            elif in_a6 is False:
                self.mysql_conn.mysql_error(380)
            return False
        self.logger.debug("тест 2.3 положение выходов соответствует")
        self.mysql_conn.mysql_ins_result('исправен', '2')
        return True

    def st_test_30_btz_3(self) -> bool:
        """
        Тест 3. Проверка работоспособности защиты ТЗП блока в режиме «Проверка»
        """
        msg_3 = "Переключите тумблер ПМЗ (1-11) в положение «Работа» " \
                "«Переключите тумблер ТЗП (0.5-1) в положение «Проверка»"
        if my_msg(msg_3):
            pass
        else:
            return False
        self.logger.debug("тест 3.1")
        in_a1, in_a2, in_a5, in_a6 = self.di_read.di_read('in_a1', 'in_a2', 'in_a5', 'in_a6')
        if in_a1 is True and in_a5 is False and in_a2 is False and in_a6 is True:
            pass
        else:
            self.logger.debug("тест 3.1 положение выходов не соответствует")
            self.mysql_conn.mysql_ins_result('неисправен', '3')
            if in_a1 is False:
                self.mysql_conn.mysql_error(381)
            elif in_a5 is True:
                self.mysql_conn.mysql_error(382)
            elif in_a2 is True:
                self.mysql_conn.mysql_error(383)
            elif in_a6 is False:
                self.mysql_conn.mysql_error(384)
            return False
        self.logger.debug("тест 3.1 положение выходов соответствует")
        return True

    def st_test_31_btz_3(self) -> bool:
        """
        3.2. Сброс защит после проверки
        """
        msg_4 = "Переключите тумблер ТЗП (0.5…1) на корпусе блока в положение \"Работа\""
        if my_msg(msg_4):
            pass
        else:
            return False
        self.logger.debug("тест 3.2")
        self.sbros_zashit_kl30()
        in_a1, in_a2, in_a5, in_a6 = self.di_read.di_read('in_a1', 'in_a2', 'in_a5', 'in_a6')
        if in_a1 is False and in_a5 is True and in_a2 is False and in_a6 is True:
            pass
        else:
            self.logger.debug("тест 3.2 положение выходов не соответствует")
            self.mysql_conn.mysql_ins_result('неисправен', '3')
            if in_a1 is True:
                self.mysql_conn.mysql_error(385)
            elif in_a5 is False:
                self.mysql_conn.mysql_error(386)
            elif in_a2 is True:
                self.mysql_conn.mysql_error(387)
            elif in_a6 is False:
                self.mysql_conn.mysql_error(388)
            return False
        self.logger.debug("тест 3.2 положение выходов соответствует")
        self.mysql_conn.mysql_ins_result('исправен', '3')
        return True

    def st_test_40_btz_3(self) -> bool:
        """
        Тест 4. Проверка срабатывания защиты ПМЗ блока по уставкам
        """
        msg_4_1 = "Установите регулятор уставок ТЗП на блоке в положение 1.0"
        if my_msg(msg_4_1):
            pass
        else:
            return False
        k = 0
        for i in self.list_ust_pmz:
            self.logger.debug(f'тест 4 уставка {self.list_ust_pmz_num[k]}')
            msg_5 = 'Установите регулятор уставок ПМЗ на блоке в положение '
            msg_result_pmz = my_msg_2(f'{msg_5} {self.list_ust_pmz_num[k]}')
            if msg_result_pmz == 0:
                pass
            elif msg_result_pmz == 1:
                return False
            elif msg_result_pmz == 2:
                self.mysql_conn.mysql_add_message(f'уставка {self.list_ust_pmz_num[k]} пропущена')
                self.list_delta_percent_pmz.append('пропущена')
                self.list_delta_t_pmz.append('пропущена')
                k += 1
                continue
            self.mysql_conn.mysql_ins_result(f'уставка {self.list_ust_pmz_num[k]}', "4")
            if self.proc.procedure_x4_to_x5(setpoint_volt=i, coef_volt=self.coef_volt):
                pass
            else:
                self.mysql_conn.mysql_ins_result("неисправен TV1", "4")
                return False
            # 4.1.  Проверка срабатывания блока от сигнала нагрузки:
            meas_volt = self.read_mb.read_analog()
            # Δ%= 0.0062*U42+1.992* U4
            calc_delta_percent_pmz = 0.0062 * meas_volt ** 2 + 1.992 * meas_volt
            self.list_delta_percent_pmz.append(f'{calc_delta_percent_pmz:.2f}')
            for qw in range(4):
                self.calc_delta_t_pmz = self.ctrl_kl.ctrl_ai_code_v0(103)
                self.mysql_conn.mysql_add_message(f'уставка {self.list_ust_pmz_num[k]} '
                                                  f'дельта t: {self.calc_delta_t_pmz:.1f}')
                if 3000 < self.calc_delta_t_pmz <= 9999:
                    self.sbros_zashit_kl30()
                    sleep(3)
                    qw += 1
                    continue
                else:
                    break
            self.logger.info(f'тест 4.1 дельта t: {self.calc_delta_t_pmz:.1f} '
                             f'уставка {self.list_ust_pmz_num[k]}')
            if self.calc_delta_t_pmz < 10:
                self.list_delta_t_pmz.append(f'< 10')
            elif self.calc_delta_t_pmz > 3000:
                self.list_delta_t_pmz.append(f'> 3000')
            else:
                self.list_delta_t_pmz.append(f'{self.calc_delta_t_pmz:.1f}')
            self.mysql_conn.mysql_add_message(f'уставка {self.list_ust_pmz_num[k]} '
                                              f'дельта t: {self.calc_delta_t_pmz:.1f}')
            self.mysql_conn.mysql_add_message(f'уставка {self.list_ust_pmz_num[k]} '
                                              f'дельта %: {calc_delta_percent_pmz:.2f}')
            in_a1, in_a2, in_a5, in_a6 = self.di_read.di_read('in_a1', 'in_a2', 'in_a5', 'in_a6')
            if in_a1 is False and in_a5 is True and in_a2 is True and in_a6 is False:
                self.logger.debug("тест 4.1 положение выходов соответствует")
                self.reset.stop_procedure_3()
                if self.subtest_45():
                    k += 1
                    continue
                else:
                    return False
            else:
                self.logger.debug("тест 4.1 положение выходов не соответствует", 1)
                self.mysql_conn.mysql_ins_result('неисправен', '4')
                self.mysql_conn.mysql_error(389)
                if self.subtest_42(i, k):
                    k += 1
                    continue
                else:
                    return False
        self.mysql_conn.mysql_ins_result('исправен', '4')
        return True

    def st_test_50_btz_3(self) -> bool:
        """
        Тест 5. Проверка срабатывания защиты ТЗП блока по уставкам
        """
        m = 0
        for n in self.list_ust_tzp:
            msg_7 = 'Установите регулятор уставок на блоке в положение '
            msg_result_tzp = my_msg_2(f'{msg_7} {self.list_ust_tzp_num[m]}')
            if msg_result_tzp == 0:
                pass
            elif msg_result_tzp == 1:
                return False
            elif msg_result_tzp == 2:
                self.mysql_conn.mysql_add_message(f'уставка {self.list_ust_tzp_num[m]} пропущена')
                self.list_delta_percent_tzp.append('пропущена')
                self.list_delta_t_tzp.append('пропущена')
                m += 1
                continue
            self.mysql_conn.mysql_ins_result(f'уставка {self.list_ust_tzp_num[m]}', "5")
            if self.proc.procedure_x4_to_x5(setpoint_volt=n, coef_volt=self.coef_volt):
                pass
            else:
                self.mysql_conn.mysql_ins_result("неисправен TV1", "5")
                return False
            meas_volt = self.read_mb.read_analog()
            # Δ%= 0.003*U42[i]+2.404* U4[i]
            calc_delta_percent_tzp = 0.003 * meas_volt ** 2 + 2.404 * meas_volt
            self.list_delta_percent_tzp.append(f'{calc_delta_percent_tzp:.2f}')
            # 5.4.  Проверка срабатывания блока от сигнала нагрузки:
            self.mysql_conn.progress_level(0.0)
            self.ctrl_kl.ctrl_relay('KL63', True)
            in_b1, *_ = self.di_read.di_read('in_b1')
            i1 = 0
            while in_b1 is False and i1 <= 4:
                in_b1, *_ = self.di_read.di_read('in_b1')
                i1 += 1
            start_timer_tzp = time()
            calc_delta_t_tzp = 0
            in_a5, *_ = self.di_read.di_read('in_a5')
            while in_a5 is True and calc_delta_t_tzp <= 370:
                in_a5, *_ = self.di_read.di_read('in_a5')
                stop_timer_tzp = time()
                calc_delta_t_tzp = stop_timer_tzp - start_timer_tzp
                self.mysql_conn.progress_level(calc_delta_t_tzp)
            self.ctrl_kl.ctrl_relay('KL63', False)
            self.reset.stop_procedure_3()
            self.mysql_conn.progress_level(0.0)
            self.logger.info(f'тест 5 delta t: {calc_delta_t_tzp:.1f} '
                             f'уставка {self.list_ust_tzp_num[m]}')
            self.list_delta_t_tzp.append(f'{calc_delta_t_tzp:.1f}')
            self.mysql_conn.mysql_add_message(f'уставка ТЗП {self.list_ust_tzp_num[m]} '
                                              f'дельта t: {calc_delta_t_tzp:.1f}')
            self.mysql_conn.mysql_add_message(f'уставка ТЗП {self.list_ust_tzp_num[m]} '
                                              f'дельта %: {calc_delta_percent_tzp:.2f}')
            in_a1, in_a2, in_a5, in_a6 = self.di_read.di_read('in_a1', 'in_a2', 'in_a5', 'in_a6')
            if in_a1 is False and in_a5 is True and in_a2 is True and in_a6 is False and calc_delta_t_tzp <= 360:
                if self.subtest_56():
                    m += 1
                    continue
                else:
                    return False
            else:
                if self.subtest_55():
                    m += 1
                    continue
                else:
                    return False
        self.mysql_conn.mysql_ins_result('исправен', '5')
        return True

    def subtest_55(self):
        self.sbros_zashit_kl30()
        in_a1, in_a2, in_a5, in_a6 = self.di_read.di_read('in_a1', 'in_a2', 'in_a5', 'in_a6')
        if in_a1 is False and in_a5 is True and in_a2 is False and in_a6 is True:
            pass
        else:
            self.mysql_conn.mysql_ins_result('неисправен', '5')
            if in_a1 is True:
                self.mysql_conn.mysql_error(377)
            elif in_a5 is False:
                self.mysql_conn.mysql_error(378)
            elif in_a2 is True:
                self.mysql_conn.mysql_error(379)
            elif in_a6 is False:
                self.mysql_conn.mysql_error(380)
            return False
        return True

    def subtest_56(self):
        self.sbros_zashit_kl30()
        in_a1, in_a2, in_a5, in_a6 = self.di_read.di_read('in_a1', 'in_a2', 'in_a5', 'in_a6')
        if in_a1 is False and in_a5 is True and in_a2 is False and in_a6 is True:
            pass
        else:
            self.mysql_conn.mysql_ins_result('неисправен', '5')
            if in_a1 is True:
                self.mysql_conn.mysql_error(377)
            elif in_a5 is False:
                self.mysql_conn.mysql_error(378)
            elif in_a2 is True:
                self.mysql_conn.mysql_error(379)
            elif in_a6 is False:
                self.mysql_conn.mysql_error(380)
            return False
        return True

    def subtest_42(self, i, k) -> bool:
        """
        4.2. Формирование нагрузочного сигнала 1,1*U3[i]:
        4.2.1. Сброс защит после проверки
        """
        self.sbros_zashit_kl30()
        in_a1, in_a2, in_a5, in_a6 = self.di_read.di_read('in_a1', 'in_a2', 'in_a5', 'in_a6')
        if in_a1 is False and in_a5 is True and in_a2 is False and in_a6 is True:
            pass
        else:
            self.mysql_conn.mysql_ins_result('неисправен', '4')
            if in_a1 is True:
                self.mysql_conn.mysql_error(377)
            elif in_a5 is False:
                self.mysql_conn.mysql_error(378)
            elif in_a2 is True:
                self.mysql_conn.mysql_error(379)
            elif in_a6 is False:
                self.mysql_conn.mysql_error(380)
            return False
        if self.proc.procedure_1_24_34(setpoint_volt=i, coef_volt=self.coef_volt, factor=1.1):
            pass
        else:
            self.mysql_conn.mysql_ins_result("неисправен TV1", "4")
            return False
        # 4.2.2.  Проверка срабатывания блока от сигнала нагрузки:
        meas_volt = self.read_mb.read_analog()
        # Δ%= 0.0062*U42+1.992* U4
        calc_delta_percent_pmz = 0.0062 * meas_volt ** 2 + 1.992 * meas_volt
        self.list_delta_percent_pmz[-1] = f'{calc_delta_percent_pmz:.2f}'
        for wq in range(4):
            self.calc_delta_t_pmz = self.ctrl_kl.ctrl_ai_code_v0(103)
            if 3000 < self.calc_delta_t_pmz <= 9999:
                self.sbros_zashit_kl30()
                sleep(3)
                wq += 1
                continue
            else:
                break
        if self.calc_delta_t_pmz < 10:
            self.list_delta_t_pmz[-1] = f'< 10'
        elif self.calc_delta_t_pmz > 3000:
            self.list_delta_t_pmz[-1] = f'> 3000'
        else:
            self.list_delta_t_pmz[-1] = f'{self.calc_delta_t_pmz:.1f}'
        self.mysql_conn.mysql_add_message(f'уставка ПМЗ {self.list_ust_pmz_num[k]} '
                                          f'дельта t: {self.calc_delta_t_pmz:.1f}')
        self.mysql_conn.mysql_add_message(f'уставка ПМЗ {self.list_ust_pmz_num[k]} '
                                          f'дельта %: {calc_delta_percent_pmz:.2f}')
        in_a1, in_a2, in_a5, in_a6 = self.di_read.di_read('in_a1', 'in_a2', 'in_a5', 'in_a6')
        if in_a1 is False and in_a5 is True and in_a2 is True and in_a6 is False:
            if self.subtest_45():
                pass
            else:
                self.mysql_conn.mysql_ins_result('неисправен', '4')
        else:
            self.mysql_conn.mysql_error(389)
            self.reset.stop_procedure_3()
            # 4.3. Сброс защит после проверки
            self.sbros_zashit_kl30()
            in_a1, in_a2, in_a5, in_a6 = self.di_read.di_read('in_a1', 'in_a2', 'in_a5', 'in_a6')
            if in_a1 is False and in_a5 is True and in_a2 is False and in_a6 is True:
                pass
            else:
                self.mysql_conn.mysql_ins_result('неисправен', '4')
                if in_a1 is True:
                    self.mysql_conn.mysql_error(377)
                elif in_a5 is False:
                    self.mysql_conn.mysql_error(378)
                elif in_a2 is True:
                    self.mysql_conn.mysql_error(379)
                elif in_a6 is False:
                    self.mysql_conn.mysql_error(380)
                return False
        return True

    def subtest_45(self) -> bool:
        """
        4.5. Расчет относительной нагрузки сигнала
        4.6. Сброс защит после проверки
        """
        self.sbros_zashit_kl30()
        in_a1, in_a2, in_a5, in_a6 = self.di_read.di_read('in_a1', 'in_a2', 'in_a5', 'in_a6')
        if in_a1 is False and in_a5 is True and in_a2 is False and in_a6 is True:
            pass
        else:
            self.mysql_conn.mysql_ins_result('неисправен', '4')
            if in_a1 is True:
                self.mysql_conn.mysql_error(377)
            elif in_a5 is False:
                self.mysql_conn.mysql_error(378)
            elif in_a2 is True:
                self.mysql_conn.mysql_error(379)
            elif in_a6 is False:
                self.mysql_conn.mysql_error(380)
            return False
        return True

    def sbros_zashit_kl30(self):
        self.ctrl_kl.ctrl_relay('KL30', True)
        sleep(1.5)
        self.ctrl_kl.ctrl_relay('KL30', False)
        sleep(3)

    def st_test_btz_3(self) -> [bool, bool]:
        if self.st_test_10_btz_3():
            if self.st_test_11_btz_3():
                if self.st_test_20_btz_3():
                    if self.st_test_21_btz_3():
                        if self.st_test_22_btz_3():
                            if self.st_test_30_btz_3():
                                if self.st_test_31_btz_3():
                                    if self.st_test_40_btz_3():
                                        if self.st_test_50_btz_3():
                                            return True, self.health_flag
        return False, self.health_flag

    def result_test_btz_3(self):
        """
        Сведение всех результатов измерения, и запись в БД.
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
    test_btz_3 = TestBTZ3()
    reset_test_btz_3 = ResetRelay()
    mysql_conn_btz_3 = MySQLConnect()
    try:
        test, health_flag = test_btz_3.st_test_btz_3()
        if test and not health_flag:
            test_btz_3.result_test_btz_3()
            mysql_conn_btz_3.mysql_block_good()
            my_msg('Блок исправен', 'green')
        else:
            test_btz_3.result_test_btz_3()
            mysql_conn_btz_3.mysql_block_bad()
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
        reset_test_btz_3.reset_all()
        sys.exit()
