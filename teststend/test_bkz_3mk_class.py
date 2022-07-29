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
import logging

from time import sleep, time

from my_msgbox import *
from my_msgbox_2 import *
from gen_func_procedure import *
from gen_func_utils import *
from gen_mb_client import *
from gen_mysql_connect import *
from gen_exception import *

__all__ = ["TestBKZ3MK"]


class TestBKZ3MK:

    def __init__(self):
        self.proc = Procedure()
        self.reset = ResetRelay()
        self.resist = Resistor()
        self.ctrl_kl = CtrlKL()
        self.read_mb = ReadMB()
        self.di_read = DIRead()
        self.mysql_conn = MySQLConnect()
        self.fault = Bug(True)

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
        self.health_flag: bool = False

        self.msg_1 = "Убедитесь в отсутствии других блоков в панелях разъемов и вставьте " \
                     "блок в соответствующий разъем панели С»"
        self.msg_2 = "«Переключите регулятор МТЗ на корпусе блока в положение «1», регулятор ТЗП в положение " \
                     "«1.1» «Переключите тумблеры в положение «Работа» и «660В»"
        self.msg_3 = "Установите регулятор МТЗ (1-11), расположенный на корпусе блока, в положение"
        self.msg_4 = "Установите регулятор МТЗ (1-11), расположенный на блоке, в положение «11»"
        self.msg_5 = "Установите регулятор ТЗП (0.3-1.1), расположенный на блоке в положение"

        logging.basicConfig(filename="C:\Stend\project_class\TestBKZ3MK.log",
                            level=logging.DEBUG,
                            encoding="utf-8",
                            format='[%(asctime)s: %(name)s: %(levelname)s] %(message)s')
        logging.getLogger('mysql').setLevel('WARNING')
        self.logger = logging.getLogger(__name__)

    def st_test_0_bkz_3mk(self) -> bool:
        self.di_read.di_read('in_a0')
        if my_msg(self.msg_1):
            if my_msg(self.msg_2):
                self.mysql_conn.mysql_ins_result('---', '1')
                self.mysql_conn.mysql_ins_result('---', '2')
                self.mysql_conn.mysql_ins_result('---', '3')
                return True
        return False

    def st_test_10_bkz_3mk(self) -> bool:
        """
        Тест 1. Проверка исходного состояния блока:
        """
        self.logger.debug("тест 1.0")
        self.mysql_conn.mysql_ins_result('идет тест 1', '1')
        self.fault.debug_msg("Тест 1. Проверка исходного состояния блока", 'blue')
        self.ctrl_kl.ctrl_relay('KL21', True)
        self.logger.debug("включение KL21")
        sleep(2)
        self.reset.sbros_zashit_kl30_1s5()
        sleep(1)
        in_a5, in_a6 = self.di_read.di_read('in_a5', 'in_a6')
        self.logger.debug(f"{in_a5 = } (True), {in_a6 = } (True)")
        if in_a5 is True and in_a6 is True:
            self.fault.debug_msg("состояние выходов соответствует", 'green')
        else:
            self.mysql_conn.mysql_ins_result('неисправен', '1')
            self.logger.debug("неисправен")
            if in_a5 is False:
                self.fault.debug_msg("вход 5 не соответствует", 'red')
                self.mysql_conn.mysql_error(317)
            elif in_a6 is False:
                self.fault.debug_msg("вход 6 не соответствует", 'red')
                self.mysql_conn.mysql_error(318)
            return False
        return True

    def st_test_11_bkz_3mk(self) -> bool:
        """
        1.1.2. Проверка отсутствия короткого замыкания на входе измерительной части блока:
        """
        self.logger.debug("тест 1.1")
        meas_volt_ust = self.proc.procedure_1_21_31()
        if meas_volt_ust != 0.0:
            pass
        else:
            self.logger.debug("неисправен")
            self.mysql_conn.mysql_ins_result('неисправен', '1')
            return False
        self.mysql_conn.mysql_ins_result('идет тест 1.1.2', '1')
        self.ctrl_kl.ctrl_relay('KL63', True)
        self.logger.debug("включение KL63")
        sleep(1)
        min_volt = 0.6 * meas_volt_ust
        max_volt = 1.1 * meas_volt_ust
        meas_volt = self.read_mb.read_analog()
        self.fault.debug_msg(f"напряжение после включения KL63 "
                             f"{min_volt:.2f} <= {meas_volt:.2f} <= {max_volt:.2f}", 'orange')
        self.logger.info(f"напряжение после включения KL63 {min_volt:.2f} <= {meas_volt:.2f} <= {max_volt:.2f}")
        if min_volt <= meas_volt <= max_volt:
            pass
        else:
            self.logger.debug("напряжение не соответствует")
            self.fault.debug_msg("напряжение не соответствует", 'red')
            self.mysql_conn.mysql_ins_result('неисправен', '1')
            self.mysql_conn.mysql_error(32)
            self.reset.sbros_kl63_proc_1_21_31()
            self.logger.debug("отключение реле")
            return False
        self.logger.debug("напряжение соответствует")
        self.fault.debug_msg("напряжение соответствует", 'green')
        self.reset.sbros_kl63_proc_1_21_31()
        self.logger.debug("отключение реле")
        return True

    def st_test_12_bkz_3mk(self) -> bool:
        """
        1.2. Определение коэффициента Кс отклонения фактического напряжения от номинального
        """
        self.logger.debug("тест 1.2")
        self.mysql_conn.mysql_ins_result('идет тест 1.2', '1')
        self.coef_volt = self.proc.procedure_1_22_32()
        self.logger.info(f"коэффициент напряжения: {self.coef_volt}")
        if self.coef_volt != 0.0:
            pass
        else:
            self.logger.debug("неисправен")
            self.reset.stop_procedure_32()
            self.logger.debug("отключение реле процедуры 3.2")
            self.mysql_conn.mysql_ins_result('неисправен', '1')
            return False
        self.logger.debug("исправен")
        self.reset.stop_procedure_32()
        self.logger.debug("отключение реле процедуры 3.2")
        self.mysql_conn.mysql_ins_result('исправен', '1')
        self.fault.debug_msg("тест 1 пройден", 'green')
        return True

    def st_test_20_bkz_3mk(self) -> bool:
        """
        Тест 2. Проверка работы блока при нормальном сопротивлении изоляции контролируемого присоединения
        """
        self.logger.debug("тест 2.0")
        self.mysql_conn.mysql_ins_result('идет тест 2', '2')
        self.resist.resist_kohm(200)
        self.logger.debug("включение 200 ком")
        sleep(1)
        in_a5, in_a6 = self.di_read.di_read('in_a5', 'in_a6')
        self.logger.debug(f"{in_a5 = } (True), {in_a6 = } (True)")
        if in_a5 is True and in_a6 is True:
            pass
        else:
            self.logger.debug("неисправен")
            self.mysql_conn.mysql_ins_result('неисправен', '2')
            if in_a5 is False:
                self.fault.debug_msg("вход 5 не соответствует", 'red')
                self.mysql_conn.mysql_error(319)
            elif in_a6 is False:
                self.fault.debug_msg("вход 6 не соответствует", 'red')
                self.mysql_conn.mysql_error(320)
            return False
        self.fault.debug_msg("состояние выходов соответствует", 'green')
        self.mysql_conn.mysql_ins_result('исправен', '2')
        self.fault.debug_msg("тест 2 пройден", 'green')
        self.logger.debug("тест 2.0 пройден")
        return True

    def st_test_30_bkz_3mk(self) -> bool:
        """
        Тест 3. Проверка работы блока при снижении уровня сопротивлении изоляции ниже аварийной уставки
        """
        self.logger.debug("тест 3.0")
        self.mysql_conn.mysql_ins_result('идет тест 3', '3')
        self.ctrl_kl.ctrl_relay('KL22', True)
        self.logger.debug("включение KL22")
        sleep(1)
        in_a5, in_a6 = self.di_read.di_read('in_a5', 'in_a6')
        self.logger.debug(f"{in_a5 = } (True), {in_a6 = } (False)")
        if in_a5 is True and in_a6 is False:
            pass
        else:
            self.logger.debug("неисправен")
            self.mysql_conn.mysql_ins_result('неисправен', '3')
            if in_a5 is False:
                self.fault.debug_msg("вход 5 не соответствует", 'red')
                self.mysql_conn.mysql_error(321)
            elif in_a6 is True:
                self.fault.debug_msg("вход 6 не соответствует", 'red')
                self.mysql_conn.mysql_error(322)
            return False
        self.logger.debug("блок сработал")
        self.fault.debug_msg("состояние выходов блока соответствует", 'green')
        self.mysql_conn.mysql_ins_result('исправен', '3')
        self.resist.resist_kohm(590)
        self.logger.debug("включение 590 ком")
        self.ctrl_kl.ctrl_relay('KL22', False)
        self.logger.debug("отключение KL22")
        sleep(2)
        self.reset.sbros_zashit_kl30_1s5()
        self.logger.debug("сброс защиты")
        in_a5, in_a6 = self.di_read.di_read('in_a5', 'in_a6')
        self.logger.debug(f"положение входов \t {in_a5 = } (True), {in_a6 = } (True)")
        self.fault.debug_msg(f'положение входов \t {in_a5 = } (True) {in_a6 = } (True)', 'blue')
        if in_a5 is True and in_a6 is True:
            pass
        else:
            self.logger.debug("блок не вернулся в исходное положение после сброса защиты")
            return False
        self.logger.debug("тест 3.0 пройден")
        self.fault.debug_msg("тест 3 пройден", 'green')
        return True

    def st_test_40_bkz_3mk(self) -> bool:
        """
        Тест 4. Проверка срабатывания защиты МТЗ блока по уставкам
        """
        self.logger.debug("тест 4.0")
        self.mysql_conn.mysql_ins_result('идет тест 4', '4')
        k = 0
        for i in self.list_ust_mtz_volt:
            msg_result_mtz = my_msg_2(f'{self.msg_3} {self.list_ust_mtz_num[k]}')
            self.logger.debug(f"значение полученное от пользователя: {msg_result_mtz}")
            if msg_result_mtz == 0:
                pass
            elif msg_result_mtz == 1:
                return False
            elif msg_result_mtz == 2:
                self.mysql_conn.mysql_add_message(f'уставка МТЗ {self.list_ust_mtz_num[k]} пропущена')
                self.list_delta_percent_mtz.append('пропущена')
                self.list_delta_t_mtz.append('пропущена')
                k += 1
                continue
            if self.proc.procedure_x4_to_x5(coef_volt=self.coef_volt, setpoint_volt=i):
                pass
            else:
                self.logger.debug(f"уставка {self.list_ust_mtz_num[k]}, процедура 1, 2.4, 3.4 не пройдена")
                self.mysql_conn.mysql_ins_result('неисправен', '4')
                return False
            # 4.1.  Проверка срабатывания блока от сигнала нагрузки:
            # Δ% = 9,19125*U4
            meas_volt_test4 = self.read_mb.read_analog()
            self.logger.info(f'напряжение \t {meas_volt_test4:.2f}')
            self.fault.debug_msg(f'напряжение \t {meas_volt_test4:.2f}', 'orange')
            calc_delta_percent_mtz = meas_volt_test4 * 9.19125
            self.logger.info(f'дельта % \t {calc_delta_percent_mtz:.2f}')
            self.fault.debug_msg(f'дельта % \t {calc_delta_percent_mtz:.2f}', 'orange')
            self.list_delta_percent_mtz.append(f'{calc_delta_percent_mtz:.2f}')
            self.mysql_conn.mysql_ins_result('идет тест 4.1', '4')
            for qw in range(4):
                self.calc_delta_t_mtz = self.ctrl_kl.ctrl_ai_code_v0(code=105)
                self.logger.info(f"уставка МТЗ {self.list_ust_mtz_num[k]}: "
                                 f"попытка: {qw}: "
                                 f"время: {self.calc_delta_t_mtz}")
                self.mysql_conn.mysql_add_message(f'уставка МТЗ {self.list_ust_mtz_num[k]}  '
                                                  f'дельта t: {self.calc_delta_t_mtz:.1f} ')
                in_a5, in_a6 = self.di_read.di_read('in_a5', 'in_a6')
                self.logger.debug(f"{in_a5 = } (False), {in_a6 = } (True)")
                self.fault.debug_msg(f'положение входов \t {in_a5 = } (False) {in_a6 = } (True)', 'blue')
                if self.calc_delta_t_mtz == 9999:
                    self.reset.sbros_zashit_kl30_1s5()
                    self.logger.debug("сброс защиты")
                    sleep(3)
                    qw += 1
                    self.logger.debug("блок не сработал по времени, повтор проверки блока")
                    continue
                elif self.calc_delta_t_mtz != 9999 and in_a5 is False and in_a6 is True:
                    self.logger.debug(f"блок сработал, время срабатывания: {self.calc_delta_t_mtz}")
                    break
                else:
                    self.logger.debug("блок не сработал по положению контактов, повтор проверки блока")
                    qw += 1
                    continue
            self.fault.debug_msg(f'дельта t \t {self.calc_delta_t_mtz:.1f}', 'orange')
            if self.calc_delta_t_mtz < 10:
                self.list_delta_t_mtz.append(f'< 10')
            elif self.calc_delta_t_mtz == 9999:
                self.list_delta_t_mtz.append(f'неисправен')
            else:
                self.list_delta_t_mtz.append(f'{self.calc_delta_t_mtz:.1f}')
            self.mysql_conn.mysql_add_message(f'уставка МТЗ {self.list_ust_mtz_num[k]}  '
                                              f'дельта t: {self.calc_delta_t_mtz:.1f} '
                                              f'дельта %: {calc_delta_percent_mtz:.2f}')
            self.reset.stop_procedure_3()
            self.logger.debug("останов процедуры 3")
            in_a5, in_a6 = self.di_read.di_read('in_a5', 'in_a6')
            if in_a5 is False and in_a6 is True:
                if self.subtest_45():
                    self.fault.debug_msg("подтест 4.5 пройден", 'green')
                    self.logger.debug("подтест 4.5 пройден")

                    self.logger.debug(f"уставка {self.list_ust_mtz_num[k]}, блок исправен, "
                                      f"переход на проверку следующей уставки")
                    k += 1
                    continue
                else:
                    self.logger.debug(f"уставка {self.list_ust_mtz_num[k]}, неисправен")
                    self.fault.debug_msg("подтест 4.5 не пройден", 'red')
                    self.mysql_conn.mysql_ins_result('неисправен', '4')
                    self.logger.debug(f"уставка {self.list_ust_mtz_num[k]}, блок не исправен, "
                                      f"переход на проверку следующей уставки")
                    k += 1
                    continue
            else:
                if self.subtest_42(i, k):
                    self.logger.debug(f"подтест 4.2 пройден")
                    self.fault.debug_msg("подтест 4.2 пройден", 'green')
                    self.logger.debug(f"уставка {self.list_ust_mtz_num[k]}, блок исправен, "
                                      f"переход на проверку следующей уставки")
                    k += 1
                    continue
                else:
                    self.logger.debug(f"подтест 4.2 не пройден")
                    self.fault.debug_msg("подтест 4.2 не пройден", 'red')
                    self.mysql_conn.mysql_ins_result('неисправен', '4')
                    self.logger.debug(f"уставка {self.list_ust_mtz_num[k]}, блок не исправен, "
                                      f"переход на проверку следующей уставки")
                    k += 1
                    continue
        self.mysql_conn.mysql_ins_result('исправен', '4')
        self.fault.debug_msg(f'{self.list_result_mtz}', 'orange')
        self.logger.info(f"результат проверки: {self.list_result_mtz}")
        self.fault.debug_msg("тест 4 пройден", 'green')
        self.logger.debug("тест 4 завершен")
        return True

    def st_test_50_bkz_3mk(self) -> bool:
        """
        Тест 5. Проверка срабатывания защиты ТЗП блока по уставкам
        """
        self.logger.debug("тест 5.0")
        if my_msg(self.msg_4):
            pass
        else:
            return False
        self.mysql_conn.mysql_ins_result('идет тест 5', '5')
        m = 0
        for n in self.list_ust_tzp_volt:
            self.logger.debug(f"проверка уставки: {self.list_ust_tzp_volt[m]}")
            self.reset.sbros_zashit_kl30_1s5()
            self.logger.debug("сброс защит")
            msg_result_tzp = my_msg_2(f'{self.msg_5} {self.list_ust_tzp_num[m]}')
            if msg_result_tzp == 0:
                pass
            elif msg_result_tzp == 1:
                return False
            elif msg_result_tzp == 2:
                self.mysql_conn.mysql_add_message(f'уставка ТЗП {self.list_ust_tzp_num[m]} пропущена')
                self.list_delta_percent_tzp.append('пропущена')
                self.list_delta_t_tzp.append('пропущена')
                m += 1
                continue
            if self.proc.procedure_x4_to_x5(coef_volt=self.coef_volt, setpoint_volt=n):
                pass
            else:
                self.mysql_conn.mysql_ins_result('неисправен', '5')
                return False
            # Δ%= 0.06075*(U4)2 + 8.887875*U4
            meas_volt_test5 = self.read_mb.read_analog()
            self.fault.debug_msg(f'напряжение \t {meas_volt_test5}', 'orange')
            calc_delta_percent_tzp = 0.06075 * meas_volt_test5 ** 2 + 8.887875 * meas_volt_test5
            self.list_delta_percent_tzp.append(f'{calc_delta_percent_tzp:.2f}')
            self.fault.debug_msg(f'дельта % \t {calc_delta_percent_tzp:.2f}', 'orange')
            # 5.4.  Проверка срабатывания блока от сигнала нагрузки:
            self.mysql_conn.mysql_ins_result('идет тест 5.4', '5')
            self.mysql_conn.progress_level(0.0)
            calc_delta_t_tzp = self.delta_t_tzp()
            self.mysql_conn.progress_level(0.0)
            self.fault.debug_msg(f'дельта t \t {calc_delta_t_tzp:.1f}', 'orange')
            self.list_delta_t_tzp.append(f'{calc_delta_t_tzp:.1f}')
            self.mysql_conn.mysql_add_message(f'уставка ТЗП {self.list_ust_tzp_num[m]}: '
                                              f'дельта t: {calc_delta_t_tzp:.1f}, '
                                              f'дельта %: {calc_delta_percent_tzp:.2f}')
            self.reset.sbros_kl63_proc_all()
            if calc_delta_t_tzp != 0:
                in_a5, in_a6 = self.di_read.di_read('in_a5', 'in_a6')
                self.logger.debug(f"{in_a5 = } (True), {in_a6 = } (False)")
                if calc_delta_t_tzp <= 360 and in_a5 is True and in_a6 is False:
                    if self.subtest_56():
                        m += 1
                        continue
                    else:
                        self.logger.debug(f"уставка {self.list_ust_tzp_num[m]}, неисправен")
                        self.mysql_conn.mysql_ins_result('неисправен', '5')
                        m += 1
                        continue
                elif calc_delta_t_tzp > 360 and in_a5 is False:
                    self.mysql_conn.mysql_error(327)
                    if self.subtest_55():
                        m += 1
                        continue
                    else:
                        self.logger.debug(f"уставка {self.list_ust_tzp_num[m]}, неисправен")
                        self.mysql_conn.mysql_ins_result('неисправен', '5')
                        m += 1
                        continue
                elif calc_delta_t_tzp > 360 and in_a6 is True:
                    self.mysql_conn.mysql_error(328)
                    if self.subtest_55():
                        m += 1
                        continue
                    else:
                        self.logger.debug(f"уставка {self.list_ust_tzp_num[m]}, неисправен")
                        self.mysql_conn.mysql_ins_result('неисправен', '5')
                        m += 1
                        continue
                elif calc_delta_t_tzp < 360 and in_a5 is True and in_a6 is True:
                    self.mysql_conn.mysql_error(328)
                    if self.subtest_55():
                        m += 1
                        continue
                    else:
                        self.logger.debug(f"уставка {self.list_ust_tzp_num[m]}, неисправен")
                        self.mysql_conn.mysql_ins_result('неисправен', '5')
                        m += 1
                        continue
            else:
                self.logger.debug(f"уставка {self.list_ust_tzp_num[m]}, неисправен")
                self.mysql_conn.mysql_ins_result('неисправен', '5')
                m += 1
                continue
        self.mysql_conn.mysql_ins_result('исправен', '5')
        return True

    def subtest_42(self, i, k):
        """
        3.2. Формирование нагрузочного сигнала 1,1*calc_volt[i]:
        """
        self.logger.debug("тест 4.2, повышение уставки")
        self.mysql_conn.mysql_ins_result('идет тест 4.2', '4')
        self.reset.sbros_zashit_kl30_1s5()
        self.logger.debug(f"сброс защит")
        in_a5, in_a6 = self.di_read.di_read('in_a5', 'in_a6')
        self.logger.debug(f"{in_a5 = } (True), {in_a6 = } (True)")
        self.fault.debug_msg(f'положение входов \t {in_a5 = } (True), {in_a6 = } (True)', 'blue')
        if in_a5 is True and in_a6 is True:
            self.logger.debug(f"блок в исходном состоянии")
        else:
            self.logger.debug(f"блок не исправен, не работает сброс защит")
            if in_a5 is False:
                self.mysql_conn.mysql_error(325)
            elif in_a5 is False:
                self.mysql_conn.mysql_error(326)
            return False
        if self.proc.procedure_1_24_34(coef_volt=self.coef_volt, setpoint_volt=i, factor=1.1):
            pass
        else:
            return False
        meas_volt_test4 = self.read_mb.read_analog()
        self.logger.debug(f"напряжение для проверки: {meas_volt_test4:.2f}")
        calc_delta_percent_mtz = meas_volt_test4 * 9.19125
        self.logger.debug(f"дельта %: {calc_delta_percent_mtz:.2f}")
        self.fault.debug_msg(f'{calc_delta_percent_mtz:.2f}', 'orange')
        self.list_delta_percent_mtz[-1] = f'{calc_delta_percent_mtz:.2f}'
        # 3.2.2.  Проверка срабатывания блока от сигнала нагрузки:
        self.mysql_conn.mysql_ins_result('идет тест 4.2.2', '4')
        for wq in range(4):
            self.calc_delta_t_mtz = self.ctrl_kl.ctrl_ai_code_v0(code=105)
            self.mysql_conn.mysql_add_message(f'уставка МТЗ {self.list_ust_mtz_num[k]}:  '
                                              f'дельта t: {self.calc_delta_t_mtz:.1f}')
            self.logger.debug(f"время срабатывания блока: {self.calc_delta_t_mtz:.1f}")
            in_a5, in_a6 = self.di_read.di_read('in_a5', 'in_a6')
            self.logger.debug(f"{in_a5 = } (False), {in_a6 = } (True)")
            if self.calc_delta_t_mtz == 9999:
                self.reset.sbros_zashit_kl30_1s5()
                self.logger.debug(f"сброс защит")
                sleep(3)
                wq += 1
                self.logger.debug(f"повторная проверка")
                continue
            elif self.calc_delta_t_mtz != 9999 and in_a5 is False and in_a6 is True:
                self.logger.debug(f"блок сработал, выход из цикла")
                break
            else:
                wq += 1
                self.logger.debug(f"блок не сработал, повторная проверка")
                continue
        self.fault.debug_msg(f'дельта t \t {self.calc_delta_t_mtz}', 'orange')
        if self.calc_delta_t_mtz < 10:
            self.list_delta_t_mtz[-1] = f'< 10'
        elif self.calc_delta_t_mtz == 9999:
            self.list_delta_t_mtz[-1] = f'неисправен'
        else:
            self.list_delta_t_mtz[-1] = f'{self.calc_delta_t_mtz:.1f}'
        self.mysql_conn.mysql_add_message(f'уставка МТЗ {self.list_ust_mtz_num[k]} '
                                          f'дельта t: {self.calc_delta_t_mtz:.1f}')
        self.reset.stop_procedure_3()
        self.logger.debug(f"останов процедуры 3")
        in_a5, in_a6 = self.di_read.di_read('in_a5', 'in_a6')
        self.logger.debug(f"{in_a5 = } (False), {in_a6 = } (True)")
        self.fault.debug_msg(f'положение входов \t {in_a5 = } (False), {in_a6 = } (True)', 'blue')
        if in_a5 is False and in_a6 is True:
            if self.subtest_45():
                return True
            else:
                return False
        elif in_a5 is True:
            self.mysql_conn.mysql_error(323)
            if self.subtest_43():
                return True
            else:
                return False
        elif in_a6 is False:
            self.mysql_conn.mysql_error(324)
            if self.subtest_43():
                return True
            else:
                return False

    def subtest_43(self):
        self.logger.debug("тест 4.3")
        self.mysql_conn.mysql_ins_result('идет тест 4.3', '4')
        self.reset.sbros_zashit_kl30_1s5()
        self.logger.debug("сброс защит")
        in_a5, in_a6 = self.di_read.di_read('in_a5', 'in_a6')
        self.logger.debug(f"{in_a5 = } (True), {in_a6 = } (True)")
        self.fault.debug_msg(f'положение входов \t {in_a5 = } (True), {in_a6 = } (True)', 'blue')
        if in_a5 is True and in_a6 is True:
            pass
        else:
            self.logger.debug("блок не исправен, не работает сброс защит")
            if in_a5 is False:
                self.mysql_conn.mysql_error(325)
            elif in_a6 is False:
                self.mysql_conn.mysql_error(326)
            return False
        self.logger.debug("защита в исходном состоянии")
        return True

    def subtest_45(self):
        self.logger.debug("тест 4.5")
        self.mysql_conn.mysql_ins_result('идет тест 4.5', '4')
        # 4.5. Расчет времени и кратности срабатывания
        self.reset.sbros_zashit_kl30_1s5()
        self.logger.debug("сброс защит")
        in_a5, in_a6 = self.di_read.di_read('in_a5', 'in_a6')
        self.logger.debug(f"{in_a5 = } (True), {in_a6 = } (True)")
        self.fault.debug_msg(f'положение входов \t {in_a5 = } (True), {in_a6 = } (True)', 'blue')
        if in_a5 is True and in_a6 is True:
            self.logger.debug("защита в исходном состоянии")
            self.fault.debug_msg("положение входов соответствует", 'green')
            return True
        else:
            self.logger.debug("блок не исправен, не работает сброс защит")
            if in_a5 is False:
                self.mysql_conn.mysql_error(325)
            elif in_a6 is False:
                self.mysql_conn.mysql_error(326)
            return False

    def subtest_55(self):
        self.logger.debug("тест 5.5")
        self.mysql_conn.mysql_ins_result('идет тест 5.5', '5')
        self.fault.debug_msg('идет тест 5.5', 'blue')
        self.reset.sbros_zashit_kl30_1s5()
        self.logger.debug("сброс защит")
        in_a5, in_a6 = self.di_read.di_read('in_a5', 'in_a6')
        self.logger.debug(f"{in_a5 = } (True), {in_a6 = } (True)")
        self.fault.debug_msg(f'положение входов \t {in_a5 = } (True), {in_a6 = } (True)', 'blue')
        if in_a5 is True and in_a6 is True:
            self.logger.debug("блок в исходном состоянии")
            return True
        else:
            self.logger.debug("блок не исправен, не работает сброс защит")
            if in_a5 is False:
                self.mysql_conn.mysql_error(329)
            elif in_a6 is False:
                self.mysql_conn.mysql_error(330)
            return False

    def subtest_56(self):
        self.logger.debug("тест 5.6")
        self.mysql_conn.mysql_ins_result('идет тест 5.6', '5')
        self.fault.debug_msg('идет тест 5.6', 'blue')
        self.reset.sbros_zashit_kl30_1s5()
        self.logger.debug("сброс защит")
        in_a5, in_a6 = self.di_read.di_read('in_a5', 'in_a6')
        self.logger.debug(f"{in_a5 = } (True), {in_a6 = } (True)")
        self.fault.debug_msg(f'положение входов \t {in_a5 = } (True), {in_a6 = } (True)', 'blue')
        if in_a5 is True and in_a6 is True:
            self.logger.debug("блок в исходном состоянии")
            return True
        else:
            self.logger.debug("блок не исправен, не работает сброс защит")
            if in_a5 is False:
                self.mysql_conn.mysql_error(329)
            elif in_a6 is False:
                self.mysql_conn.mysql_error(330)
            return False

    def delta_t_tzp(self):
        self.ctrl_kl.ctrl_relay('KL63', True)
        in_b1, *_ = self.di_read.di_read('in_b1')
        i = 0
        while in_b1 is False and i <= 20:
            in_b1, *_ = self.di_read.di_read('in_b1')
            i += 1
        if in_b1 is True:
            start_timer = time()
            meas_time = 0
            in_a6 = self.di_read.di_read('in_a6')
            while in_a6 is True and meas_time <= 370:
                in_a6 = self.di_read.di_read('in_a6')
                meas_time = time() - start_timer
                self.mysql_conn.progress_level(meas_time)
            if in_a6 is False:
                stop_timer = time()
                delta_t_calc = stop_timer - start_timer
                return delta_t_calc
            else:
                return 0
        else:
            return 0

    def st_test_bkz_3mk(self) -> [bool, bool]:
        if self.st_test_0_bkz_3mk():
            if self.st_test_10_bkz_3mk():
                if self.st_test_11_bkz_3mk():
                    if self.st_test_12_bkz_3mk():
                        if self.st_test_20_bkz_3mk():
                            if self.st_test_30_bkz_3mk():
                                if self.st_test_40_bkz_3mk():
                                    if self.st_test_50_bkz_3mk():
                                        return True, self.health_flag
        return False, self.health_flag

    def result_test_bkz_3mk(self):
        for g1 in range(len(self.list_delta_percent_mtz)):
            self.list_result_mtz.append((self.list_ust_mtz_num[g1],
                                         self.list_delta_percent_mtz[g1],
                                         self.list_delta_t_mtz[g1]))
        self.mysql_conn.mysql_pmz_result(self.list_result_mtz)
        self.logger.info(f"результат проверки МТЗ: {self.list_result_mtz}")
        for g2 in range(len(self.list_delta_percent_tzp)):
            self.list_result_tzp.append((self.list_ust_tzp_num[g2],
                                         self.list_delta_percent_tzp[g2],
                                         self.list_delta_t_tzp[g2]))
        self.mysql_conn.mysql_tzp_result(self.list_result_tzp)
        self.logger.info(f"результат проверки ТЗП: {self.list_result_tzp}")


if __name__ == '__main__':
    test_bkz_3mk = TestBKZ3MK()
    reset_test_bkz_3mk = ResetRelay()
    mysql_conn_bkz_3mk = MySQLConnect()
    fault = Bug(True)
    try:
        test, health_flag = test_bkz_3mk.st_test_bkz_3mk()
        if test and not health_flag:
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
    except HardwareException as hwe:
        my_msg(f'{hwe}', 'red')
    finally:
        reset_test_bkz_3mk.reset_all()
        sys.exit()
