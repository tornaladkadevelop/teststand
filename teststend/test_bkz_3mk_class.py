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

from sys import exit
from time import sleep, time

from my_msgbox import *
from my_msgbox_2 import *
from gen_func_procedure import *
from gen_func_utils import *
from gen_mb_client import *
from gen_mysql_connect import *

__all__ = ["TestBKZ3MK"]


class TestBKZ3MK(object):

    __proc = Procedure()
    __reset = ResetRelay()
    __resist = Resistor()
    __ctrl_kl = CtrlKL()
    __read_mb = ReadMB()
    __mysql_conn = MySQLConnect()
    __fault = Bug(True)

    # Тест 5. Проверка срабатывания защиты ТЗП блока по уставкам
    # медленные
    list_ust_tzp_num = (0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 1.1)
    list_ust_tzp = (4.7, 6.2, 7.7, 9.2, 10.6, 12.0, 13.4, 14.7, 16.6)
    list_delta_t_tzp = []
    list_delta_percent_tzp = []
    list_result_tzp = []
    # Тест 4. Проверка срабатывания защиты МТЗ блока по уставкам
    # быстрые
    list_ust_mtz_num = (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11)
    list_ust_mtz = (21.8, 27.2, 32.7, 38.1, 43.6, 49.0, 54.4, 59.9, 65.3, 70.8, 76.2)
    list_delta_t_mtz = []
    list_delta_percent_mtz = []
    list_result_mtz = []

    list_result_mtz_num = ('6', '7', '8', '9', '10', '11', '12', '13', '14', '15', '16')
    list_result_tzp_num = ('17', '18', '19', '20', '21', '22', '23', '24', '25')

    coef_volt: float

    def __init__(self):
        pass
    
    @staticmethod
    def st_test_0_bkz_3mk() -> bool:
        msg_1 = "Убедитесь в отсутствии других блоков в панелях разъемов и вставьте " \
                "блок в соответствующий разъем панели С»"
        msg_2 = "«Переключите регулятор МТЗ на корпусе блока в положение «1», регулятор ТЗП в положение " \
                "«1.1» «Переключите тумблеры в положение «Работа» и «660В»"
        if my_msg(msg_1):
            if my_msg(msg_2):
                pass
            else:
                return False
        else:
            return False

    def st_test_10_bkz_3mk(self) -> bool:
        """
        Тест 1. Проверка исходного состояния блока:
        """
        self.__mysql_conn.mysql_ins_result('идет тест 1', '1')
        self.__fault.debug_msg("Тест 1. Проверка исходного состояния блока", 4)
        self.__ctrl_kl.ctrl_relay('KL21', True)
        sleep(2)
        self.__reset.sbros_zashit_kl30_1s5()
        sleep(1)
        in_a5, in_a6 = self.__inputs_a()
        if in_a5 is True and in_a6 is True:
            self.__fault.debug_msg("состояние выходов соответствует", 3)
            pass
        else:
            self.__mysql_conn.mysql_ins_result('неисправен', '1')
            if in_a5 is False:
                self.__fault.debug_msg("вход 5 не соответствует", 1)
                self.__mysql_conn.mysql_error(317)
            elif in_a6 is False:
                self.__fault.debug_msg("вход 6 не соответствует", 1)
                self.__mysql_conn.mysql_error(318)
            return False
        return True

    def st_test_11_bkz_3mk(self) -> bool:
        """
        1.1.2. Проверка отсутствия короткого замыкания на входе измерительной части блока:
        """
        meas_volt_ust = self.__proc.procedure_1_21_31()
        if meas_volt_ust is not False:
            pass
        else:
            self.__mysql_conn.mysql_ins_result('неисправен', '1')
            return False
        self.__mysql_conn.mysql_ins_result('идет тест 1.1.2', '1')
        self.__ctrl_kl.ctrl_relay('KL63', True)
        meas_volt = self.__read_mb.read_analog()
        if 0.8 * meas_volt_ust <= meas_volt <= 1.1 * meas_volt_ust:
            pass
        else:
            self.__fault.debug_msg("напряжение не соответствует", 1)
            self.__mysql_conn.mysql_ins_result('неисправен', '1')
            self.__mysql_conn.mysql_error(32)
            self.__reset.sbros_kl63_proc_1_21_31()
            return False
        self.__fault.debug_msg("напряжение соответствует", 3)
        self.__reset.sbros_kl63_proc_1_21_31()
        return True

    def st_test_12_bkz_3mk(self) -> bool:
        """
        1.2. Определение коэффициента Кс отклонения фактического напряжения от номинального
        """
        self.__mysql_conn.mysql_ins_result('идет тест 1.2', '1')
        self.coef_volt = self.__proc.procedure_1_22_32()
        if self.coef_volt is not False:
            pass
        else:
            self.__mysql_conn.mysql_ins_result('неисправен', '1')
            return False
        self.__mysql_conn.mysql_ins_result('идет тест 1.2.1', '1')
        self.__fault.debug_msg(f'коэффициент сети\t {self.coef_volt}', 2)
        self.__reset.stop_procedure_32()
        self.__mysql_conn.mysql_ins_result('исправен', '1')
        self.__fault.debug_msg("тест 1 пройден", 3)
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
                self.__fault.debug_msg("вход 5 не соответствует", 1)
                self.__mysql_conn.mysql_error(319)
            elif in_a6 is False:
                self.__fault.debug_msg("вход 6 не соответствует", 1)
                self.__mysql_conn.mysql_error(320)
            return False
        self.__fault.debug_msg("состояние выходов соответствует", 3)
        self.__mysql_conn.mysql_ins_result('исправен', '2')
        self.__fault.debug_msg("тест 2 пройден", 3)
        return True

    def st_test_30_bkz_3mk(self) -> bool:
        """
        Тест 3. Проверка работы блока при снижении уровня сопротивлении изоляции ниже аварийной уставки
        """
        self.__mysql_conn.mysql_ins_result('идет тест 3', '3')
        self.__ctrl_kl.ctrl_relay('KL22', True)
        in_a5, in_a6 = self.__inputs_a()
        if in_a5 is True and in_a6 is False:
            pass
        else:
            self.__mysql_conn.mysql_ins_result('неисправен', '3')
            if in_a5 is False:
                self.__fault.debug_msg("вход 5 не соответствует", 1)
                self.__mysql_conn.mysql_error(321)
            elif in_a6 is True:
                self.__fault.debug_msg("вход 6 не соответствует", 1)
                self.__mysql_conn.mysql_error(322)
            return False
        self.__fault.debug_msg("состояние выходов блока соответствует", 3)
        self.__mysql_conn.mysql_ins_result('исправен', '3')
        self.__resist.resist_kohm(590)
        self.__ctrl_kl.ctrl_relay('KL22', False)
        sleep(2)
        self.__reset.sbros_zashit_kl30_1s5()
        in_a5, in_a6 = self.__inputs_a()
        self.__fault.debug_msg(f'положение входов \t {in_a5=} {in_a6=}', 5)
        if in_a5 is True and in_a6 is True:
            pass
        else:
            return False
        self.__fault.debug_msg("тест 3 пройден", 3)
        return True

    def st_test_40_bkz_3mk(self) -> bool:
        """
        Тест 4. Проверка срабатывания защиты МТЗ блока по уставкам
        """
        self.__mysql_conn.mysql_ins_result('идет тест 4', '4')
        msg_3 = "Установите регулятор МТЗ (1-11), расположенный на корпусе блока, в положение"
        k = 0
        for i in self.list_ust_mtz:
            msg_result_mtz = my_msg_2(f'{msg_3} {self.list_ust_mtz_num[k]}')
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
            self.__fault.debug_msg(f'напряжение \t {meas_volt_test4}', 2)
            calc_delta_percent_mtz = meas_volt_test4 * 9.19125
            self.__fault.debug_msg(f'дельта % \t {calc_delta_percent_mtz}', 2)
            self.list_delta_percent_mtz.append(round(calc_delta_percent_mtz, 0))
            self.__mysql_conn.mysql_ins_result('идет тест 4.1', '4')
            calc_delta_t_mtz = self.__ctrl_kl.ctrl_ai_code_v0(code=105)
            if calc_delta_t_mtz != 9999:
                pass
            else:
                self.__mysql_conn.mysql_ins_result('неисправен', '4')
            self.__fault.debug_msg(f'дельта t \t {calc_delta_t_mtz}', 2)
            self.list_delta_t_mtz.append(round(calc_delta_t_mtz, 0))
            self.__mysql_conn.mysql_add_message(f'уставка МТЗ {self.list_ust_mtz_num[k]}  дельта t: {calc_delta_t_mtz}')
            in_a5, in_a6 = self.__inputs_a()
            self.__fault.debug_msg(f'положение входов \t {in_a5=} {in_a6=}', 5)
            if in_a5 is False and in_a6 is True:
                self.__reset.stop_procedure_3()
                if self.__subtest_45():
                    self.__fault.debug_msg("подтест 4.5 пройден", 3)
                    k += 1
                    continue
                else:
                    self.__fault.debug_msg("подтест 4.5 не пройден", 1)
                    self.__mysql_conn.mysql_ins_result('неисправен', '4')
                    return False
            else:
                if self.__subtest_42(i, k):
                    self.__fault.debug_msg("подтест 4.2 пройден", 3)
                    k += 1
                    continue
                else:
                    self.__fault.debug_msg("подтест 4.2 не пройден", 1)
                    self.__mysql_conn.mysql_ins_result('неисправен', '4')
                    return False
        self.__mysql_conn.mysql_ins_result('исправен', '4')
        self.__fault.debug_msg(self.list_result_mtz, 2)
        self.__fault.debug_msg("тест 4 пройден", 3)
        for g1 in range(len(self.list_delta_percent_mtz)):
            self.list_result_mtz.append((self.list_ust_mtz_num[g1],
                                         self.list_delta_percent_mtz[g1],
                                         self.list_delta_t_mtz[g1]))
        self.__mysql_conn.mysql_pmz_result(self.list_result_mtz)
        return True

    def st_test_50_bkz_3mk(self) -> bool:
        """
        Тест 5. Проверка срабатывания защиты ТЗП блока по уставкам
        """
        msg_4 = "Установите регулятор МТЗ (1-11), расположенный на блоке, в положение «11»"
        if my_msg(msg_4):
            pass
        else:
            return False
        self.__mysql_conn.mysql_ins_result('идет тест 5', '5')
        # Цикл i=1…9 Таблица уставок №1
        m = 0
        for n in self.list_ust_tzp:
            msg_5 = "Установите регулятор ТЗП (0.3-1.1), расположенный на блоке в положение"
            msg_result_tzp = my_msg_2(f'{msg_5} {self.list_ust_tzp_num[m]}')
            if msg_result_tzp == 0:
                pass
            elif msg_result_tzp == 1:
                return False
            elif msg_result_tzp == 2:
                self.__mysql_conn.mysql_add_message('уставка ТЗП ' + str(self.list_ust_tzp_num[m]) + ' пропущена')
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
            self.__fault.debug_msg(f'напряжение \t {meas_volt_test5}', 2)
            calc_delta_percent_tzp = 0.06075 * meas_volt_test5 ** 2 + 8.887875 * meas_volt_test5
            self.list_delta_percent_tzp.append(round(calc_delta_percent_tzp, 0))
            self.__fault.debug_msg(f'дельта % \t {calc_delta_percent_tzp}', 2)
            # 5.4.  Проверка срабатывания блока от сигнала нагрузки:
            self.__mysql_conn.mysql_ins_result('идет тест 5.4', '5')
            calc_delta_t_tzp = self.__delta_t_tzp()
            self.__fault.debug_msg(f'дельта t \t {calc_delta_t_tzp}', 2)
            self.list_delta_t_tzp.append(round(calc_delta_t_tzp, 0))
            self.__mysql_conn.mysql_add_message(f'уставка ТЗП {self.list_ust_tzp_num[m]} дельта t: {calc_delta_t_tzp}')
            self.__reset.sbros_kl63_proc_all()
            if calc_delta_t_tzp != 0:
                in_a5, in_a6 = self.__inputs_a()
                if calc_delta_t_tzp <= 360 and in_a5 is True and in_a6 is False:
                    if self.__subtest_56():
                        m += 1
                        continue
                    else:
                        self.__mysql_conn.mysql_ins_result('неисправен', '5')
                        return False
                elif calc_delta_t_tzp > 360 and in_a5 is False:
                    self.__mysql_conn.mysql_error(327)
                    if self.__subtest_55():
                        m += 1
                        continue
                    else:
                        self.__mysql_conn.mysql_ins_result('неисправен', '5')
                        return False
                elif calc_delta_t_tzp > 360 and in_a6 is True:
                    self.__mysql_conn.mysql_error(328)
                    if self.__subtest_55():
                        m += 1
                        continue
                    else:
                        self.__mysql_conn.mysql_ins_result('неисправен', '5')
                        return False
                elif calc_delta_t_tzp < 360 and in_a5 is True and in_a6 is True:
                    self.__mysql_conn.mysql_error(328)
                    if self.__subtest_55():
                        m += 1
                        continue
                    else:
                        self.__mysql_conn.mysql_ins_result('неисправен', '5')
                        return False
            else:
                self.__mysql_conn.mysql_ins_result('неисправен', '5')
                return False
        self.__mysql_conn.mysql_ins_result('исправен', '5')
        for g2 in range(len(self.list_delta_percent_tzp)):
            self.list_result_tzp.append((self.list_ust_tzp_num[g2],
                                         self.list_delta_percent_tzp[g2],
                                         self.list_delta_t_tzp[g2]))
        self.__mysql_conn.mysql_tzp_result(self.list_result_tzp)
        return True
    
    def __subtest_42(self, i, k):
        """
        3.2. Формирование нагрузочного сигнала 1,1*calc_volt[i]:
        """
        self.__mysql_conn.mysql_ins_result('идет тест 4.2', '4')
        self.__reset.sbros_zashit_kl30_1s5()
        in_a5, in_a6 = self.__inputs_a()
        self.__fault.debug_msg(f'положение входов \t {in_a5=} {in_a6=}', 5)
        if in_a5 is True and in_a6 is True:
            pass
        else:
            if in_a5 is False:
                self.__mysql_conn.mysql_error(325)
            elif in_a5 is False:
                self.__mysql_conn.mysql_error(326)
            return False
        if self.__proc.start_procedure_1():
            calc_volt = self.__proc.start_procedure_25(self.coef_volt, i)
            if calc_volt is not False:
                if self.__proc.start_procedure_35(calc_volt=calc_volt, setpoint_volt=i):
                    pass
                else:
                    return False
            else:
                return False
        else:
            return False
        meas_volt_test4 = self.__read_mb.read_analog()
        calc_delta_percent_mtz = meas_volt_test4 * 9.19125
        self.__fault.debug_msg(calc_delta_percent_mtz, 2)
        self.list_delta_percent_mtz[-1] = round(calc_delta_percent_mtz, 0)
        # 3.2.2.  Проверка срабатывания блока от сигнала нагрузки:
        self.__mysql_conn.mysql_ins_result('идет тест 4.2.2', '4')
        calc_delta_t_mtz = self.__ctrl_kl.ctrl_ai_code_v0(code=105)
        if calc_delta_t_mtz != 9999:
            pass
        else:
            self.__mysql_conn.mysql_ins_result('неисправен', '4')
        self.__fault.debug_msg(f'дельта t \t {calc_delta_t_mtz}', 2)
        self.list_delta_t_mtz[-1] = round(calc_delta_t_mtz, 0)
        self.__mysql_conn.mysql_add_message(f'уставка МТЗ {self.list_ust_mtz_num[k]} дельта t: {calc_delta_t_mtz}')
        in_a5, in_a6 = self.__inputs_a()
        self.__fault.debug_msg(f'положение входов \t {in_a5=} {in_a6=}', 5)
        if in_a5 is False and in_a6 is True:
            self.__reset.stop_procedure_3()
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
        self.__fault.debug_msg(f'положение входов \t {in_a5=} {in_a6=}', 5)
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
        self.__fault.debug_msg(f'положение входов \t {in_a5=} {in_a6=}', 5)
        if in_a5 is True and in_a6 is True:
            self.__fault.debug_msg("положение входов соответствует", 4)
            return True
        elif in_a5 is False:
            self.__mysql_conn.mysql_error(325)
            return False
        elif in_a6 is False:
            self.__mysql_conn.mysql_error(326)
            return False
    
    def __subtest_55(self):
        self.__mysql_conn.mysql_ins_result('идет тест 5.5', '5')
        self.__fault.debug_msg('идет тест 5.5', 3)
        self.__reset.sbros_zashit_kl30_1s5()
        in_a5, in_a6 = self.__inputs_a()
        self.__fault.debug_msg(f'положение входов \t {in_a5=} {in_a6=}', 5)
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
        self.__fault.debug_msg('идет тест 5.6', 3)
        self.__reset.sbros_zashit_kl30_1s5()
        in_a5, in_a6 = self.__inputs_a()
        self.__fault.debug_msg(f'положение входов \t {in_a5=} {in_a6=}', 5)
        if in_a5 is True and in_a6 is True:
            return True
        elif in_a5 is False:
            self.__mysql_conn.mysql_error(329)
            return False
        elif in_a6 is False:
            self.__mysql_conn.mysql_error(330)
            return False
    
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


if __name__ == '__main__':
    test_bkz_3mk = TestBKZ3MK()
    reset_test_bkz_3mk = ResetRelay()
    mysql_conn_bkz_3mk = MySQLConnect()
    fault = Bug(True)
    try:
        if test_bkz_3mk.st_test_bkz_3mk():
            mysql_conn_bkz_3mk.mysql_block_good()
            my_msg('Блок исправен')
        else:
            mysql_conn_bkz_3mk.mysql_block_bad()
            my_msg('Блок неисправен', '#A61E1E')
    except OSError:
        my_msg("ошибка системы")
    except SystemError:
        my_msg("внутренняя ошибка")
    except ModbusConnectException as mce:
        fault.debug_msg(mce, 1)
        my_msg(str(mce), '#A61E1E')
    finally:
        reset_test_bkz_3mk.reset_all()
        exit()
