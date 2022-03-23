#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Алгоритм проверки
Тип блока           Производитель
МТЗ-5 вер.2-7/0.4-2	Завод Электромашина

"""

import sys

from time import sleep, time

from gen_func_utils import *
from my_msgbox import *
from my_msgbox_2 import *
from gen_func_procedure import *
from gen_mb_client import *
from gen_mysql_connect import *

__all__ = ["TestMTZ5V27"]


class TestMTZ5V27(object):

    def __init__(self):
        self.__reset = ResetRelay()
        self.__proc = Procedure()
        self.__read_mb = ReadMB()
        self.__ctrl_kl = CtrlKL()
        self.__mysql_conn = MySQLConnect()
        self.__fault = Bug(True)

        self.list_ust_tzp_num = (0.4, 0.7, 1.0, 1.3, 1.6, 1.8, 2.0)
        self.list_ust_tzp_volt = (10.8, 18.8, 26.55, 34.05, 41.4, 46.2, 50.85)
        self.list_ust_mtz_num = (2, 2.5, 3, 3.5, 4, 4.5, 5, 5.5, 6, 6.5, 7)
        self.list_ust_mtz_volt = (37.6, 46.8, 55.8, 64.8, 73.6, 82.4, 91.0, 99.6, 108, 116.4, 124.6)
        self.list_delta_t_mtz = []
        self.list_delta_t_tzp = []
        self.list_delta_percent_mtz = []
        self.list_delta_percent_tzp = []
        self.list_mtz_result = []
        self.list_tzp_result = []
        self.ust_mtz = 30.0

        self.coef_volt: float = 0.0
        self.calc_delta_t_mtz = 0.0

        self.msg_1 = "Убедитесь в отсутствии других блоков в панелях разъемов " \
                     "и вставьте блок в соответствующий разъем панели B"
        self.msg_2 = "«Переключите тумблер на корпусе блока в положение «Работа» и установите регуляторы уставок " \
                     "в положение 7 (2-7) и в положение 2 (0.4-2)»"
        self.msg_3 = "Переключите регулятор МТЗ, расположенный на корпусе блока в положение «Проверка»"
        self.msg_4 = "установите регуляторы уставок в положение 2 (2-7) и в положение 0.4 (0.4-2)»"
        self.msg_5 = "Переключите тумблер, расположенный на корпусе блока в положение «Работа»"
        self.msg_6 = "Установите регулятор уставок на блоке в положение \t"
        self.msg_7 = "Установите регулятор времени перегруза на блоке в положение «21 сек»"
        self.msg_8 = "Установите регулятор уставок на блоке в положение\t"

    def st_test_10(self) -> bool:
        """
        Тест 1.0
        :return: bool
        """
        if my_msg(self.msg_1):
            if my_msg(self.msg_2):
                pass
            else:
                return False
        else:
            return False
        self.__mysql_conn.mysql_ins_result('идёт тест 1', '1')
        self.__ctrl_kl.ctrl_relay('KL1', True)
        sleep(0.5)
        self.__ctrl_kl.ctrl_relay('KL2', True)
        sleep(1)
        self.__sbros_zashit()
        in_a1, in_a5 = self.__inputs_a()
        if in_a1 is True and in_a5 is False:
            pass
        else:
            self.__fault.debug_msg("тест 1.1 положение выходов не соответствует", 'red')
            self.__mysql_conn.mysql_ins_result('неисправен', '1')
            return False
        self.__fault.debug_msg("тест 1.1 положение выходов соответствует", 'green')
        return True

    def st_test_11(self) -> bool:
        """
        1.1. Проверка вероятности наличия короткого замыкания на входе измерительной цепи блока
        :return: bool
        """
        self.__mysql_conn.mysql_ins_result('идёт тест 1.1', '1')
        meas_volt_ust = self.__proc.procedure_1_21_31()
        if meas_volt_ust != 0.0:
            pass
        else:
            self.__mysql_conn.mysql_error(433)
            self.__mysql_conn.mysql_ins_result('неисправен', '1')
            return False
        self.__ctrl_kl.ctrl_relay('KL63', True)
        min_volt = 0.6 * meas_volt_ust
        max_volt = 1.0 * meas_volt_ust
        meas_volt = self.__read_mb.read_analog()
        self.__fault.debug_msg(f'напряжение после включения KL63 '
                               f'{min_volt:.2f} <= {meas_volt:.2f} <= {max_volt:.2f}', 'orange')
        if min_volt <= meas_volt <= max_volt:
            pass
        else:
            self.__mysql_conn.mysql_ins_result('неисправен', '1')
            self.__mysql_conn.mysql_error(455)
            self.__reset.sbros_kl63_proc_1_21_31()
            return False
        self.__reset.sbros_kl63_proc_1_21_31()
        return True

    def st_test_12(self) -> bool:
        """
        1.2. Определение коэффициента Кс отклонения фактического напряжения от номинального.
        :return: bool
        """
        self.__mysql_conn.mysql_ins_result('идёт тест 1.2', '1')
        self.__fault.debug_msg("1.2. Определение коэффициента Кс отклонения "
                               "фактического напряжения от номинального", 'blue')
        self.coef_volt = self.__proc.procedure_1_22_32()
        if self.coef_volt != 0.0:
            pass
        else:
            self.__mysql_conn.mysql_ins_result("неисправен TV1", "1")
            self.__reset.stop_procedure_32()
            return False
        self.__reset.stop_procedure_32()
        self.__mysql_conn.mysql_ins_result('исправен', '1')
        return True

    def st_test_20(self) -> bool:
        """
        Тест 2. Проверка работоспособности защиты МТЗ блока в режиме «Проверка»
        :return: bool
        """
        self.__mysql_conn.mysql_ins_result('идёт тест 2', '2')
        if my_msg(self.msg_3):
            if my_msg(self.msg_4):
                pass
            else:
                return False
        else:
            return False
        if self.__proc.procedure_1_24_34(setpoint_volt=self.ust_mtz, coef_volt=self.coef_volt):
            pass
        else:
            self.__mysql_conn.mysql_ins_result("неисправен TV1", "2")
            return False
        return True

    def st_test_21(self) -> bool:
        """
        2.2.  Проверка срабатывания блока от сигнала нагрузки:
        :return: bool
        """
        self.__fault.debug_msg("2.2.  Проверка срабатывания блока от сигнала нагрузки:", 'blue')
        self.__mysql_conn.mysql_ins_result('идёт тест 2.2', '2')
        self.__ctrl_kl.ctrl_relay('KL63', True)
        sleep(0.5)
        self.__ctrl_kl.ctrl_relay('KL63', False)
        sleep(0.2)
        in_a1, in_a5 = self.__inputs_a()
        if in_a1 is False and in_a5 is True:
            pass
        else:
            self.__mysql_conn.mysql_ins_result('неисправен', '2')
            if in_a1 is True:
                self.__mysql_conn.mysql_error(444)
            elif in_a5 is False:
                self.__mysql_conn.mysql_error(445)
            self.__reset.stop_procedure_3()
            return False
        self.__reset.stop_procedure_3()
        return True

    def st_test_22(self) -> bool:
        """
        2.4.2. Сброс защит после проверки
        :return: bool
        """
        self.__mysql_conn.mysql_ins_result('идёт тест 2.4', '2')
        self.__fault.debug_msg("2.4.2. Сброс защит после проверки", 'blue')
        self.__sbros_zashit()
        in_a1, in_a5 = self.__inputs_a()
        if in_a1 is True and in_a5 is False:
            pass
        else:
            self.__fault.debug_msg("положение выходов не соответствует", 'red')
            self.__mysql_conn.mysql_ins_result('неисправен', '2')
            if in_a1 is False:
                self.__mysql_conn.mysql_error(446)
            elif in_a5 is True:
                self.__mysql_conn.mysql_error(447)
            return False
        self.__fault.debug_msg("положение выходов соответствует", 'green')
        self.__mysql_conn.mysql_ins_result('исправен', '2')
        return True

    def st_test_30(self) -> bool:
        """
        Тест 3. Проверка срабатывания защиты ПМЗ блока по уставкам.
        :return: bool
        """
        if my_msg(self.msg_5):
            pass
        else:
            return False
        self.__mysql_conn.mysql_ins_result('идёт тест 3', '3')
        k = 0
        for i in self.list_ust_mtz_volt:
            msg_result_mtz = my_msg_2(f'{self.msg_6} {self.list_ust_mtz_num[k]}')
            if msg_result_mtz == 0:
                pass
            elif msg_result_mtz == 1:
                return False
            elif msg_result_mtz == 2:
                self.__mysql_conn.mysql_add_message(f'уставка {self.list_ust_mtz_num[k]} пропущена')
                self.list_delta_percent_mtz.append('пропущена')
                self.list_delta_t_mtz.append('пропущена')
                k += 1
                continue
            if self.__proc.procedure_1_24_34(setpoint_volt=i, coef_volt=self.coef_volt):
                pass
            else:
                self.__mysql_conn.mysql_ins_result("неисправен TV1", "3")
                return False
            self.__fault.debug_msg("3.1.  Проверка срабатывания блока от сигнала нагрузки:", 'blue')
            # 3.1.  Проверка срабатывания блока от сигнала нагрузки:
            self.__mysql_conn.mysql_ins_result(f'уставка {self.list_ust_mtz_num[k]}', '3')
            # Δ%= 0.0029*(U4)2+5.192*U4
            meas_volt = self.__read_mb.read_analog()
            calc_delta_percent_mtz = 0.0029 * meas_volt ** 2 + 5.192 * meas_volt
            self.__fault.debug_msg(f'дельта %:\t{calc_delta_percent_mtz:.2f}', 'orange')
            self.list_delta_percent_mtz.append(f'{calc_delta_percent_mtz:.2f}')
            for qw in range(4):
                self.calc_delta_t_mtz = self.__ctrl_kl.ctrl_ai_code_v0(110)
                if 500 < self.calc_delta_t_mtz <= 9999:
                    self.__sbros_zashit()
                    sleep(3)
                    qw += 1
                    continue
                else:
                    qw = 0
                    break
            self.__fault.debug_msg(f'дельта t:\t{self.calc_delta_t_mtz:.1f}', 'orange')
            if self.calc_delta_t_mtz < 10:
                self.list_delta_t_mtz.append(f'<10')
            elif self.calc_delta_t_mtz > 500:
                self.list_delta_t_mtz.append(f'> 500')
            else:
                self.list_delta_t_mtz.append(f'{self.calc_delta_t_mtz:.1f}')
            self.__mysql_conn.mysql_add_message(f'уставка {self.list_ust_mtz_num[k]} '
                                                f'дельта t: {self.calc_delta_t_mtz:.1f}')
            self.__mysql_conn.mysql_add_message(f'уставка {self.list_ust_mtz_num[k]} '
                                                f'дельта %: {calc_delta_percent_mtz:.2f}')
            self.__reset.stop_procedure_3()
            in_a1, in_a5 = self.__inputs_a()
            if in_a1 is False and in_a5 is True:
                self.__subtest_33()
            else:
                self.__mysql_conn.mysql_error(448)
                if self.__subtest_32(i, k):
                    if self.__subtest_33():
                        k += 1
                        continue
                    else:
                        self.__mysql_conn.mysql_ins_result('неисправен', '3')
                        return False
                else:
                    if self.__subtest_33():
                        k += 1
                        continue
                    else:
                        self.__mysql_conn.mysql_ins_result('неисправен', '3')
                        return False
        self.__mysql_conn.mysql_ins_result('исправен', '3')
        return True

    def st_test_40(self) -> bool:
        """
        Тест 4. Проверка срабатывания защиты от перегрузки блока по уставкам.
        :return: bool
        """
        if my_msg(self.msg_7):
            pass
        else:
            return False
        self.__mysql_conn.mysql_ins_result('идёт тест 4', '4')
        m = 0
        for n in self.list_ust_tzp_volt:
            msg_result_tzp = my_msg_2(f'{self.msg_8} {self.list_ust_tzp_num[m]}')
            if msg_result_tzp == 0:
                pass
            elif msg_result_tzp == 1:
                return False
            elif msg_result_tzp == 2:
                self.__mysql_conn.mysql_add_message(f'уставка {self.list_ust_tzp_num[m]} пропущена')
                self.list_delta_percent_tzp.append('пропущена')
                self.list_delta_t_tzp.append('пропущена')
                m += 1
                continue
            self.__mysql_conn.mysql_ins_result(f'уставка {self.list_ust_tzp_num[m]}', '4')
            if self.__proc.procedure_1_24_34(setpoint_volt=n, coef_volt=self.coef_volt):
                pass
            else:
                self.__mysql_conn.mysql_ins_result("неисправен TV1", "4")
                return False
            # Δ%= 0.0132*U42[i]+5.4183* U4[i]
            meas_volt = self.__read_mb.read_analog()
            calc_delta_percent_tzp = 0.0132 * meas_volt ** 2 + 5.4183 * meas_volt
            self.__fault.debug_msg(f'дельта %:\t{calc_delta_percent_tzp:.2f}', 'orange')
            self.list_delta_percent_tzp.append(f'{calc_delta_percent_tzp:.2f}')
            # 4.4.  Проверка срабатывания блока от сигнала нагрузки:
            self.__ctrl_kl.ctrl_relay('KL63', True)
            self.__mysql_conn.progress_level(0.0)
            r = 0
            in_b1 = self.__inputs_b()
            while in_b1 is False and r <= 5:
                in_b1 = self.__inputs_b()
                r += 1
            start_timer_tzp = time()
            delta_t_tzp = 0
            in_a5 = self.__inputs_a5()
            while in_a5 is False and delta_t_tzp <= 21:
                delta_t_tzp = time() - start_timer_tzp
                self.__mysql_conn.progress_level(delta_t_tzp)
                in_a5 = self.__inputs_a5()
            stop_timer_tzp = time()
            self.__ctrl_kl.ctrl_relay('KL63', False)
            calc_delta_t_tzp = stop_timer_tzp - start_timer_tzp
            self.__mysql_conn.progress_level(0.0)
            self.__fault.debug_msg(f'тест 3 delta t: {calc_delta_t_tzp:.1f}', 'orange')
            self.list_delta_t_tzp.append(f'{calc_delta_t_tzp:.1f}')
            self.__mysql_conn.mysql_add_message(f'уставка {self.list_ust_tzp_num[m]} '
                                                f'дельта t: {calc_delta_t_tzp:.1f}')
            self.__mysql_conn.mysql_add_message(f'уставка {self.list_ust_tzp_num[m]} '
                                                f'дельта %: {calc_delta_percent_tzp:.2f}')
            self.__reset.stop_procedure_3()
            in_a1, in_a5 = self.__inputs_a()
            if in_a1 is False and in_a5 is True and calc_delta_t_tzp <= 21:
                self.__fault.debug_msg("положение выходов соответствует", 'green')
                if self.__subtest_46():
                    m += 1
                    continue
                else:
                    return False
            else:
                self.__fault.debug_msg("положение выходов не соответствует", 'red')
                self.__mysql_conn.mysql_error(448)
                if self.__subtest_46():
                    m += 1
                    continue
                else:
                    return False
        self.__mysql_conn.mysql_ins_result('исправен', '4')
        return True

    def __subtest_32(self, i, k):
        """
        3.2. Формирование нагрузочного сигнала 1,15*U3[i]:
        :param i: уставка
        :param k: счетчик цикла
        :return: bool
        """
        self.__sbros_zashit()
        in_a1, in_a5 = self.__inputs_a()
        if in_a1 is True and in_a5 is False:
            pass
        else:
            self.__mysql_conn.mysql_ins_result('неисправен', '3')
            if in_a1 is False:
                self.__mysql_conn.mysql_error(446)
            elif in_a5 is True:
                self.__mysql_conn.mysql_error(447)
            return False
        if self.__proc.start_procedure_1():
            calc_vol = self.__proc.start_procedure_28(coef_volt=self.coef_volt, setpoint_volt=i)
            if self.__proc.start_procedure_35(calc_volt=calc_vol, setpoint_volt=i):
                pass
            else:
                self.__mysql_conn.mysql_ins_result('неисправен', '3')
                return False
        else:
            self.__mysql_conn.mysql_ins_result('неисправен', '3')
            return False
        # 3.2.2.  Проверка срабатывания блока от сигнала нагрузки:
        meas_volt = self.__read_mb.read_analog()
        calc_delta_percent_mtz = 0.0029 * meas_volt ** 2 + 5.192 * meas_volt
        self.list_delta_percent_mtz[-1] = f'{calc_delta_percent_mtz:.2f}'
        for wq in range(4):
            self.calc_delta_t_mtz = self.__ctrl_kl.ctrl_ai_code_v0(110)
            if 500 < self.calc_delta_t_mtz <= 9999:
                self.__sbros_zashit()
                sleep(3)
                wq += 1
                continue
            else:
                wq = 0
                break
        in_a1, in_a5 = self.__inputs_a()
        if self.calc_delta_t_mtz < 10:
            self.list_delta_t_mtz[-1] = f'< 10'
        elif self.calc_delta_t_mtz > 500:
            self.list_delta_t_mtz[-1] = f'> 500'
        else:
            self.list_delta_t_mtz[-1] = f'{self.calc_delta_t_mtz:.1f}'
        self.__mysql_conn.mysql_add_message(f'уставка {self.list_ust_mtz_num[k]} '
                                            f'дельта t: {self.calc_delta_t_mtz:.1f}')
        self.__mysql_conn.mysql_add_message(f'уставка {self.list_ust_mtz_num[k]} '
                                            f'дельта %: {calc_delta_percent_mtz:.2f}')
        if in_a1 is False and in_a5 is True:
            self.__reset.stop_procedure_3()
            return True
        else:
            self.__reset.stop_procedure_3()
            self.__mysql_conn.mysql_error(448)
            return False

    def __subtest_33(self) -> bool:
        """
        3.3. Сброс защит после проверки
        3.5. Расчет относительной нагрузки сигнала
        Δ%= 3.4364*(U4[i])/0.63
        :return: bool
        """
        self.__sbros_zashit()
        in_a1, in_a5 = self.__inputs_a()
        if in_a1 is True and in_a5 is False:
            self.__fault.debug_msg("подтест 3.3 пройден", 'green')
            return True
        else:
            self.__mysql_conn.mysql_ins_result('неисправен', '3')
            self.__fault.debug_msg("подтест 3.3 не пройден", 'red')
            if in_a1 is False:
                self.__mysql_conn.mysql_error(446)
            elif in_a5 is True:
                self.__mysql_conn.mysql_error(447)
            return False

    def __subtest_46(self):
        """
        4.6.1. Сброс защит после проверки
        Определение кратности сигнала нагрузки: Δ%= 3.4364*U4[i]/0.63
        :return:
        """
        self.__sbros_zashit()
        in_a1, in_a5 = self.__inputs_a()
        if in_a1 is True and in_a5 is False:
            self.__fault.debug_msg("тест 4.6 положение выходов соответствует", 'green')
            return True
        else:
            self.__mysql_conn.mysql_ins_result('неисправен', '4')
            self.__fault.debug_msg("тест 4.6 положение выходов не соответствует", 'red')
            if in_a1 is False:
                self.__mysql_conn.mysql_error(449)
            elif in_a5 is True:
                self.__mysql_conn.mysql_error(450)
            return False

    def __inputs_a(self):
        """
        Считывает из OPC сервера положение входов ПЛК
        :return: in_a1, in_a5
        """
        in_a1, in_a5 = self.__read_mb.read_discrete_v1('in_a1', 'in_a5')
        if in_a1 is None or in_a5 is None:
            raise ModbusConnectException(f'нет связи с контроллером')
        return in_a1, in_a5

    def __inputs_a5(self):
        """
        Считывает из OPC сервера положение входов ПЛК
        :return: in_a5
        """
        in_a5 = self.__read_mb.read_discrete_v1('in_a5')
        if in_a5 is None:
            raise ModbusConnectException(f'нет связи с контроллером')
        return in_a5

    def __sbros_zashit(self):
        """
        Сброс защит.
        :return:
        """
        self.__ctrl_kl.ctrl_relay('KL1', False)
        sleep(1.5)
        self.__ctrl_kl.ctrl_relay('KL1', True)
        sleep(2)

    def __inputs_b(self):
        """
        Считывает из OPC сервера положение входов ПЛК
        :return: in_b1
        """
        in_b1 = self.__read_mb.read_discrete_v1('in_b1')
        if in_b1 is None:
            raise ModbusConnectException(f'нет связи с контроллером')
        return in_b1

    def result_test(self):
        """
        Записывает результаты проверки в БД.
        :return:
        """
        for g1 in range(len(self.list_delta_percent_mtz)):
            self.list_mtz_result.append((self.list_ust_mtz_num[g1],
                                         self.list_delta_percent_mtz[g1],
                                         self.list_delta_t_mtz[g1]))
        self.__mysql_conn.mysql_pmz_result(self.list_mtz_result)
        for g2 in range(len(self.list_delta_percent_tzp)):
            self.list_tzp_result.append((self.list_ust_tzp_num[g2],
                                         self.list_delta_percent_tzp[g2],
                                         self.list_delta_t_tzp[g2]))
        self.__mysql_conn.mysql_tzp_result(self.list_tzp_result)

    def st_test_mtz_5_v2_7(self) -> bool:
        """
        Функция собирающая все тесты в один тест.
        :return: bool
        """
        if self.st_test_10():
            if self.st_test_11():
                if self.st_test_12():
                    if self.st_test_20():
                        if self.st_test_21():
                            if self.st_test_22():
                                if self.st_test_30():
                                    if self.st_test_40():
                                        return True
        return False


if __name__ == '__main__':
    test_mtz = TestMTZ5V27()
    reset_test_mtz = ResetRelay()
    mysql_conn_mtz = MySQLConnect()
    fault = Bug(True)
    try:
        if test_mtz.st_test_mtz_5_v2_7():
            test_mtz.result_test()
            mysql_conn_mtz.mysql_block_good()
            my_msg('Блок исправен', 'green')
        else:
            test_mtz.result_test()
            mysql_conn_mtz.mysql_block_bad()
            my_msg('Блок неисправен', 'red')
    except OSError:
        my_msg("ошибка системы", 'red')
    except SystemError:
        my_msg("внутренняя ошибка", 'red')
    except ModbusConnectException as mce:
        fault.debug_msg(mce, 'red')
        my_msg(f'{mce}', 'red')
    finally:
        reset_test_mtz.reset_all()
        sys.exit()
