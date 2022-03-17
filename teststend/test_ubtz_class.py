#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Алгоритм проверки

Тип блока	Производитель
УБТЗ	Нет производителя
УБТЗ	Горэкс-Светотехника

"""

import sys

from time import sleep, time

from gen_func_procedure import *
from gen_func_utils import *
from my_msgbox import *
from my_msgbox_2 import *
from gen_mb_client import *
from gen_mysql_connect import *

__all__ = ["TestUBTZ"]


class TestUBTZ(object):

    __reset = ResetRelay()
    __proc = Procedure()
    __fault = Bug(True)
    __read_mb = ReadMB()
    __ctrl_kl = CtrlKL()
    __mysql_conn = MySQLConnect()

    list_ust_bmz_num = (1, 2, 3, 4, 5, 6, 7)
    list_ust_tzp_num = (1, 2, 3, 4, 5, 6, 7)
    list_ust_bmz_volt = (6.9, 13.8, 27.4, 41.1, 54.8, 68.5, 82.2)
    list_ust_tzp_volt = (11.2, 15.0, 18.7, 22.4, 26.2, 29.9, 33.6)
    coef_volt: float

    list_delta_t_tzp = []
    list_delta_t_bmz = []
    list_bmz_result = []
    list_tzp_result = []

    msg_1 = "Убедитесь в отсутствии других блоков в панелях разъемов и вставьте " \
            "блок в соответствующий разъем панели С"
    msg_2 = "Переключите регулятор БМЗ на корпусе блока в положение «1», регулятор ТЗП в положение «0»"
    msg_3 = "Установите регулятор БМЗ, расположенный на корпусе блока, в положение\t"
    msg_4 = "Установите регулятор БМЗ, расположенный на блоке, в положение «0»"
    msg_5 = "Установите регулятор ТЗП, расположенный на блоке в положение\t"

    def __init__(self):
        pass
    
    def st_test_10(self) -> bool:
        if my_msg(self.msg_1):
            if my_msg(self.msg_2):
                pass
            else:
                return False
        else:
            return False
        self.__mysql_conn.mysql_ins_result("идёт тест 1.1", '1')
        self.__ctrl_kl.ctrl_relay('KL22', True)
        self.__ctrl_kl.ctrl_relay('KL66', True)
        self.__sbros_zashit()
        sleep(2)
        in_a1, in_a2, in_a5, in_a6 = self.__inputs_a()
        if in_a1 is False and in_a5 is True and in_a2 is False and in_a6 is True:
            pass
        else:
            self.__fault.debug_msg('тест 1 положение выходов не соответствует', 'red')
            self.__mysql_conn.mysql_ins_result("неисправен", '1')
            if in_a1 is True:
                self.__mysql_conn.mysql_error(451)
            elif in_a5 is True:
                self.__mysql_conn.mysql_error(452)
            elif in_a2 is True:
                self.__mysql_conn.mysql_error(453)
            elif in_a6 is True:
                self.__mysql_conn.mysql_error(454)
            return False
        self.__fault.debug_msg('тест 1 положение выходов соответствует', 'green')
        return True

    def st_test_11(self) -> bool:
        """
        1.1. Проверка вероятности наличия короткого замыкания на входе измерительной цепи блока
        :return:
        """
        self.__fault.debug_msg('тест 1.1', 'blue')
        self.__mysql_conn.mysql_ins_result("идёт тест 1.2", '1')
        meas_volt_ust = self.__proc.procedure_1_21_31()
        if meas_volt_ust != 0.0:
            pass
        else:
            return False
        # 1.1.2. Проверка отсутствия короткого замыкания на входе измерительной части блока:
        self.__fault.debug_msg('тест 1.2', 'blue')
        self.__mysql_conn.mysql_ins_result("идёт тест 1.3", '1')
        self.__ctrl_kl.ctrl_relay('KL63', True)
        sleep(1)
        min_volt = 0.6 * meas_volt_ust
        max_volt = 1.1 * meas_volt_ust
        meas_volt = self.__read_mb.read_analog()
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
        1.2. Определение коэффициента Кс отклонения фактического напряжения от номинального
        :return:
        """
        self.__fault.debug_msg('тест 1.3', 'blue')
        self.__mysql_conn.mysql_ins_result("идёт тест 1.4", '1')
        self.coef_volt = self.__proc.procedure_1_22_32()
        if self.coef_volt != 0.0:
            pass
        else:
            self.__mysql_conn.mysql_ins_result('неисправен', '1')
            self.__reset.stop_procedure_32()
            return False
        self.__reset.stop_procedure_32()
        self.__mysql_conn.mysql_ins_result('исправен', '1')
        self.__fault.debug_msg('тест 1 завершён', 'blue')
        return True

    def st_test_20(self) -> bool:
        """
        Тест 2. Проверка срабатывания защиты БМЗ блока по уставкам
        :return:
        """
        k = 0
        for i in self.list_ust_bmz_volt:
            msg_result_bmz = my_msg_2(f'{self.msg_3} {self.list_ust_bmz_num[k]}')
            if msg_result_bmz == 0:
                pass
            elif msg_result_bmz == 1:
                return False
            elif msg_result_bmz == 2:
                self.__mysql_conn.mysql_add_message(f'уставка {self.list_ust_bmz_num[k]} пропущена')
                self.list_delta_t_bmz.append('пропущена')
                k += 1
                continue
            self.__mysql_conn.mysql_ins_result(f'уставка БМЗ {self.list_ust_bmz_num[k]}', '1')
            if self.__proc.procedure_1_24_34(coef_volt=self.coef_volt, setpoint_volt=i):
                pass
            else:
                self.__mysql_conn.mysql_ins_result('неисправен TV1', '1')
                return False
            # 3.1.  Проверка срабатывания блока от сигнала нагрузки:
            calc_delta_t_bmz = self.__ctrl_kl.ctrl_ai_code_v0(109)
            self.__fault.debug_msg(f'тест 2, дельта t\t{calc_delta_t_bmz:.1f}', 'orange')
            self.list_delta_t_bmz.append(f'{calc_delta_t_bmz:.1f}')
            self.__mysql_conn.mysql_add_message(f'уставка {self.list_ust_bmz_num[k]} дельта t: {calc_delta_t_bmz:.1f}')
            in_a1, in_a2, in_a5, in_a6 = self.__inputs_a()
            if in_a1 is True and in_a5 is False and in_a2 is False and in_a6 is True:
                self.__fault.debug_msg('тест 2 положение выходов соответствует', 'green')
                self.__reset.stop_procedure_3()
                if self.__subtest_33_or_45(num_test=2):
                    k += 1
                    continue
                else:
                    self.__mysql_conn.mysql_ins_result("тест 2 неисправен", '1')
                    return False
            else:
                self.__fault.debug_msg('тест 2 положение выходов не соответствует', 'red')
                if in_a1 is False:
                    self.__mysql_conn.mysql_error(456)
                elif in_a5 is True:
                    self.__mysql_conn.mysql_error(457)
                elif in_a2 is True:
                    self.__mysql_conn.mysql_error(458)
                elif in_a6 is False:
                    self.__mysql_conn.mysql_error(459)
                self.__reset.stop_procedure_3()
                if self.__subtest_32(i=i, k=k):
                    if self.__subtest_33_or_45(num_test=2):
                        k += 1
                        continue
                    else:
                        self.__mysql_conn.mysql_ins_result("тест 2 неисправен", '1')
                        return False
                else:
                    if self.__subtest_33_or_45(num_test=2):
                        k += 1
                        continue
                    else:
                        self.__mysql_conn.mysql_ins_result("тест 2 неисправен", '1')
                        return False
        self.__mysql_conn.mysql_ins_result("тест 2 исправен", '1')
        return True

    def st_test_30(self) -> bool:
        """
        Тест 3. Проверка срабатывания защиты ТЗП блока по уставкам
        :return:
        """
        if my_msg(self.msg_4):
            pass
        else:
            return False
        m = 0
        for n in self.list_ust_tzp_volt:
            msg_result_tzp = my_msg_2(f'{self.msg_5} {self.list_ust_tzp_num[m]}')
            if msg_result_tzp == 0:
                pass
            elif msg_result_tzp == 1:
                return False
            elif msg_result_tzp == 2:
                self.__mysql_conn.mysql_add_message(f'уставка {self.list_ust_tzp_num[m]} пропущена')
                self.list_delta_t_tzp.append('пропущена')
                m += 1
                continue
            self.__mysql_conn.mysql_ins_result(f'уставка ТЗП {self.list_ust_tzp_num[m]}', '1')
            if self.__proc.procedure_1_24_34(coef_volt=self.coef_volt, setpoint_volt=n):
                pass
            else:
                self.__mysql_conn.mysql_ins_result("тест 3 неисправен TV1", '1')
                return False
            # 4.4.  Проверка срабатывания блока от сигнала нагрузки:
            self.__ctrl_kl.ctrl_relay('KL63', True)
            self.__mysql_conn.progress_level(0.0)
            in_b1 = self.__inputs_b1()
            while in_b1 is False:
                in_b1 = self.__inputs_b1()
            start_timer = time()
            sub_timer = 0
            in_a6 = self.__inputs_a6()
            while in_a6 is True and sub_timer <= 370:
                sub_timer = time() - start_timer
                self.__fault.debug_msg(f'времени прошло: {sub_timer}', 'orange')
                self.__mysql_conn.progress_level(sub_timer)
                sleep(0.2)
                in_a6 = self.__inputs_a6()
            stop_timer = time()
            self.__reset.stop_procedure_3()
            self.__mysql_conn.progress_level(0.0)
            calc_delta_t_tzp = stop_timer - start_timer
            self.__fault.debug_msg(f'тест 3 delta t:\t{calc_delta_t_tzp:.1f}', 'orange')
            self.list_delta_t_tzp.append(calc_delta_t_tzp)
            self.__mysql_conn.mysql_add_message(f'уставка {self.list_ust_tzp_num[m]} '
                                                f'дельта t: {calc_delta_t_tzp:.1f}')
            in_a1, in_a2, in_a5, in_a6 = self.__inputs_a()
            if in_a1 is False and in_a5 is True and in_a2 is False and in_a6 is True and calc_delta_t_tzp <= 360:
                if self.__subtest_33_or_45(num_test=3):
                    m += 1
                    continue
                else:
                    return False
            else:
                if in_a1 is True:
                    self.__mysql_conn.mysql_error(451)
                elif in_a5 is True:
                    self.__mysql_conn.mysql_error(452)
                elif in_a2 is True:
                    self.__mysql_conn.mysql_error(453)
                elif in_a6 is True:
                    self.__mysql_conn.mysql_error(454)
                self.__mysql_conn.mysql_ins_result("тест 3 неисправен", '1')
                if self.__subtest_33_or_45(num_test=3):
                    m += 1
                    continue
                else:
                    return False
        self.__mysql_conn.mysql_ins_result("исправен", '1')
        return True
    
    def __subtest_32(self, i, k):
        """
        3.2. Формирование нагрузочного сигнала 1,1*U3[i]:
        3.2.1. Сброс защит после проверки
        :return:
        """
        self.__sbros_zashit()
        sleep(2)
        in_a1, in_a2, in_a5, in_a6 = self.__inputs_a()
        if in_a1 is False and in_a5 is True and in_a2 is False and in_a6 is True:
            pass
        else:
            self.__fault.debug_msg("тест 3.1 положение выходов не соответствует", 'red')
            self.__mysql_conn.mysql_ins_result("тест 2 неисправен", '1')
            if in_a1 is True:
                self.__mysql_conn.mysql_error(460)
            elif in_a5 is False:
                self.__mysql_conn.mysql_error(461)
            elif in_a2 is True:
                self.__mysql_conn.mysql_error(462)
            elif in_a6 is False:
                self.__mysql_conn.mysql_error(463)
            return False
        self.__fault.debug_msg("тест 3.1 положение выходов соответствует", 'green')
        if self.__proc.procedure_1_25_35(coef_volt=self.coef_volt, setpoint_volt=i):
            pass
        else:
            self.__mysql_conn.mysql_ins_result("неисправен TV1", '1')
            return False
        # 3.2.2.  Проверка срабатывания блока от сигнала нагрузки:
        calc_delta_t_bmz = self.__ctrl_kl.ctrl_ai_code_v0(109)
        self.__fault.debug_msg(f'тест 3 delta t:\t{calc_delta_t_bmz:.1f}', 'orange')
        self.list_delta_t_bmz[-1] = f'{calc_delta_t_bmz:.1f}'
        self.__mysql_conn.mysql_add_message(f'уставка {self.list_ust_bmz_num[k]} '
                                            f'дельта t: {calc_delta_t_bmz:.1f}')
        in_a1, in_a2, in_a5, in_a6 = self.__inputs_a()
        if in_a1 is True and in_a5 is False and in_a2 is False and in_a6 is True:
            pass
        else:
            self.__fault.debug_msg("тест 3.2 положение выходов не соответствует", 'red')
            self.__reset.stop_procedure_3()
            if in_a1 is True:
                self.__mysql_conn.mysql_error(464)
            elif in_a5 is True:
                self.__mysql_conn.mysql_error(465)
            elif in_a2 is True:
                self.__mysql_conn.mysql_error(466)
            elif in_a6 is True:
                self.__mysql_conn.mysql_error(467)
            return False
        self.__fault.debug_msg("тест 3.2 положение выходов соответствует", 'green')
        self.__reset.stop_procedure_3()
        return True
    
    def __subtest_33_or_45(self, num_test) -> bool:
        """
        3.3. Сброс защит после проверки
        :return:
        """
        self.__sbros_zashit()
        sleep(2)
        in_a1, in_a2, in_a5, in_a6 = self.__inputs_a()
        if in_a1 is False and in_a5 is True and in_a2 is False and in_a6 is True:
            return True
        else:
            self.__mysql_conn.mysql_ins_result(f"тест {num_test} неисправен", f'{num_test}')
            if in_a1 is True:
                self.__mysql_conn.mysql_error(460)
            elif in_a5 is False:
                self.__mysql_conn.mysql_error(461)
            elif in_a2 is True:
                self.__mysql_conn.mysql_error(462)
            elif in_a6 is False:
                self.__mysql_conn.mysql_error(463)
            return False
    
    def __sbros_zashit(self):
        self.__ctrl_kl.ctrl_relay('KL1', True)
        self.__ctrl_kl.ctrl_relay('KL31', True)
        sleep(1.5)
        self.__ctrl_kl.ctrl_relay('KL1', False)
        self.__ctrl_kl.ctrl_relay('KL31', False)

    def __inputs_a(self):
        in_a1 = self.__read_mb.read_discrete(1)
        in_a2 = self.__read_mb.read_discrete(2)
        in_a5 = self.__read_mb.read_discrete(5)
        in_a6 = self.__read_mb.read_discrete(6)
        if in_a1 is None or in_a2 is None or in_a5 is None or in_a6 is None:
            raise ModbusConnectException(f'нет связи с контроллером')
        return in_a1, in_a2, in_a5, in_a6
    
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

    def result_test_ubtz(self):
        for g1 in range(len(self.list_delta_t_bmz)):
            self.list_bmz_result.append((self.list_ust_bmz_num[g1], self.list_delta_t_bmz[g1]))
        for g2 in range(len(self.list_delta_t_tzp)):
            self.list_tzp_result.append((self.list_ust_tzp_num[g2], self.list_delta_t_tzp[g2]))
        self.__mysql_conn.mysql_ubtz_btz_result(self.list_bmz_result)
        self.__mysql_conn.mysql_ubtz_tzp_result(self.list_tzp_result)

    def st_test_ubtz(self) -> bool:
        if self.st_test_10():
            if self.st_test_11():
                if self.st_test_12():
                    if self.st_test_20():
                        if self.st_test_30():
                            return True
        return False


if __name__ == '__main__':
    test_ubtz = TestUBTZ()
    reset_test_ubtz = ResetRelay()
    mysql_conn_ubtz = MySQLConnect()
    fault = Bug(True)
    try:
        if test_ubtz.st_test_ubtz():
            test_ubtz.result_test_ubtz()
            mysql_conn_ubtz.mysql_block_good()
            my_msg('Блок исправен', 'green')
        else:
            test_ubtz.result_test_ubtz()
            mysql_conn_ubtz.mysql_block_bad()
            my_msg('Блок неисправен', 'red')
    except OSError:
        my_msg("ошибка системы", 'red')
    except SystemError:
        my_msg("внутренняя ошибка", 'red')
    except ModbusConnectException as mce:
        fault.debug_msg(mce, 'red')
        my_msg(f'{mce}', 'red')
    finally:
        reset_test_ubtz.reset_all()
        sys.exit()
