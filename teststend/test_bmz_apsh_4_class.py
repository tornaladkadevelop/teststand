#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Алгоритм проверки

Тип блока	Производитель
БМЗ АПШ 4.0	Нет производителя
БМЗ АПШ 4.0	Горэкс-Светотехника

"""

from time import sleep
from sys import exit

from gen_func_procedure import *
from gen_func_utils import *
from my_msgbox import *
from my_msgbox_2 import *
from gen_mb_client import *
from gen_mysql_connect import *

__all__ = ["TestBMZAPSH4"]


class TestBMZAPSH4(object):

    __proc = Procedure()
    __reset = ResetRelay()
    __ctrl_kl = CtrlKL()
    __read_mb = ReadMB()
    __mysql_conn = MySQLConnect()
    __fault = Bug(True)

    list_ust_num = (1, 2, 3, 4, 5)
    list_ust = (9.84, 16.08, 23.28, 34.44, 50.04)

    list_delta_t = []
    list_result = []

    coef_volt: float

    def __init__(self):
        pass
    
    def st_test_10_bmz_apsh_4(self) -> bool:
        """
        # Тест 1. Проверка исходного состояния блока:
        """
        msg_1 = "Установите переключатель уставок на блоке в положение 1"
        if my_msg(msg_1):
            pass
        else:
            return False
        self.__mysql_conn.mysql_ins_result('идёт тест 1.1', '1')
        self.__ctrl_kl.ctrl_relay('KL66', True)
        self.__reset.sbros_zashit_kl1()
        in_a1 = self.__inputs_a()
        if in_a1 is False:
            pass
        else:
            self.__fault.debug_msg("вход 1 не соответствует", 1)
            self.__mysql_conn.mysql_ins_result('неисправен', '1')
            self.__mysql_conn.mysql_error(342)
            return False
        self.__fault.debug_msg("вход 1 соответствует", 4)
        return True

    def st_test_11_bmz_apsh_4(self) -> bool:
        """
        Проверка на КЗ входа блока, и межвиткового замыкания трансформатора
        """
        self.__mysql_conn.mysql_ins_result('идёт тест 1.2', '1')
        meas_volt_ust = self.__proc.procedure_1_21_31()
        if meas_volt_ust is not False:
            pass
        else:
            self.__mysql_conn.mysql_ins_result('неисправен TV1', '1')
        self.__ctrl_kl.ctrl_relay('KL63', True)
        meas_volt = self.__read_mb.read_analog()
        if 0.9 * meas_volt_ust <= meas_volt <= 1.1 * meas_volt_ust:
            pass
        else:
            self.__fault.debug_msg("напряжение не соответствует", 1)
            self.__mysql_conn.mysql_ins_result('неисправен', '1')
            self.__mysql_conn.mysql_error(343)
            self.__reset.sbros_kl63_proc_1_21_31()
        self.__fault.debug_msg(f'напряжение соответствует заданному \t {meas_volt}', 2)
        self.__reset.sbros_kl63_proc_1_21_31()
        return True

    def st_test_12_bmz_apsh_4(self) -> bool:
        """
        Коэффициент сети
        """
        self.__mysql_conn.mysql_ins_result('идёт тест 1.3', '1')
        coef_volt = self.__proc.procedure_1_22_32()
        self.__fault.debug_msg(f'коэф. сети \t {coef_volt}', 2)
        if coef_volt is not False:
            pass
        else:
            self.__reset.stop_procedure_32()
            self.__mysql_conn.mysql_ins_result('неисправен', '1')
            return False
        self.__mysql_conn.mysql_ins_result('тест 1 исправен', '1')
        self.__reset.stop_procedure_32()
        return True

    def st_test_20_bmz_apsh_4(self) -> bool:
        """
        Тест 2. Проверка срабатывания защиты блока по уставкам
        """
        self.__fault.debug_msg("запуск теста 2", 3)
        self.__mysql_conn.mysql_ins_result('идёт тест 2', '1')
        k = 0
        for i in self.list_ust:
            msg_4 = (f'Установите регулятор уставок на блоке в положение: {self.list_ust_num[k]}')
            msg_result = my_msg_2(msg_4)
            if msg_result == 0:
                pass
            elif msg_result == 1:
                return False
            elif msg_result == 2:
                self.__mysql_conn.mysql_add_message(f'уставка {self.list_ust_num[k]} пропущена')
                self.list_delta_t.append('пропущена')
                k += 1
                continue
            self.__mysql_conn.mysql_ins_result(f'уставка {self.list_ust_num[k]}', '4')
            if self.__proc.procedure_1_24_34(coef_volt=self.coef_volt, setpoint_volt=i):
                pass
            else:
                self.__mysql_conn.mysql_ins_result('неисправен TV1', '1')
            # 2.1.  Проверка срабатывания блока от сигнала нагрузки:
            calc_delta_t = self.__ctrl_kl.ctrl_ai_code_v0(111)
            self.__fault.debug_msg(f'delta t:\t {calc_delta_t}', 2)
            self.list_delta_t.append(round(calc_delta_t, 0))
            self.__mysql_conn.mysql_add_message(f'уставка {self.list_ust_num[k]} дельта t: {calc_delta_t:.1f}')
            in_a1 = self.__inputs_a()
            if in_a1 is True:
                self.__fault.debug_msg("вход 1 соответствует", 4)
                self.__reset.stop_procedure_3()
                if self.__sbros_zashit():
                    k += 1
                    continue
                else:
                    return False
            else:
                self.__fault.debug_msg("вход 1 не соответствует", 1)
                self.__mysql_conn.mysql_ins_result('неисправен', '1')
                self.__mysql_conn.mysql_error(344)
                self.__reset.stop_procedure_3()
                if self.__subtest_2_2(i=i, k=k):
                    if self.__sbros_zashit():
                        k += 1
                        continue
                    else:
                        return False
                else:
                    return False
        self.__mysql_conn.mysql_ins_result('исправен', '1')
        self.__fault.debug_msg("тест 2 пройден", 3)
        self.__fault.debug_msg("сбрасываем все и завершаем проверку", 3)
        for t1 in range(len(self.list_delta_t)):
            self.list_result.append((self.list_ust_num[t1], self.list_delta_t[t1]))
        self.__mysql_conn.mysql_ubtz_btz_result(self.list_result)
        return True
    
    def __subtest_2_2(self, i, k):
        if self.__sbros_zashit():
            pass
        else:
            return False
        if self.__proc.procedure_1_25_35(coef_volt=self.coef_volt, setpoint_volt=i):
            pass
        else:
            return False
        calc_delta_t = self.__ctrl_kl.ctrl_ai_code_v0(111)
        self.__fault.debug_msg('delta t\t' + str(calc_delta_t), 2)
        self.list_delta_t[-1] = round(calc_delta_t, 0)
        self.__mysql_conn.mysql_add_message(f'уставка {self.list_ust_num[k]} дельта t: {calc_delta_t:.1f}')
        in_a1 = self.__inputs_a()
        if in_a1 is True:
            pass
        else:
            self.__fault.debug_msg("вход 1 не соответствует", 1)
            self.__mysql_conn.mysql_ins_result('неисправен', '1')
            self.__mysql_conn.mysql_error(346)
            return False
        self.__reset.stop_procedure_3()
        return True
    
    def __sbros_zashit(self):
        self.__ctrl_kl.ctrl_relay('KL1', True)
        sleep(1.5)
        self.__ctrl_kl.ctrl_relay('KL1', False)
        sleep(2)
        in_a1 = self.__inputs_a()
        if in_a1 is False:
            pass
        else:
            self.__fault.debug_msg("вход 1 не соответствует", 1)
            self.__mysql_conn.mysql_ins_result('неисправен', '1')
            self.__mysql_conn.mysql_error(344)
            return False
        self.__fault.debug_msg("вход 1 соответствует", 4)
        return True
    
    def __inputs_a(self):
        in_a1 = self.__read_mb.read_discrete(1)
        if in_a1 is None:
            raise ModbusConnectException(f'нет связи с контроллером')
        return in_a1
    
    def __inputs_b(self):
        in_b0 = self.__read_mb.read_discrete(8)
        in_b1 = self.__read_mb.read_discrete(9)
        if in_b0 is None or in_b1 is None:
            raise ModbusConnectException(f'нет связи с контроллером')
        return in_b0, in_b1

    def st_test_bmz_apsh_4(self) -> bool:
        if self.st_test_10_bmz_apsh_4():
            if self.st_test_11_bmz_apsh_4():
                if self.st_test_12_bmz_apsh_4():
                    if self.st_test_20_bmz_apsh_4():
                        return True
        return False


if __name__ == '__main__':
    test_bmz_apsh_4 = TestBMZAPSH4()
    reset_test_bmz_apsh_4 = ResetRelay()
    mysql_conn_bmz_apsh_4 = MySQLConnect()
    fault = Bug(True)
    try:
        if test_bmz_apsh_4.st_test_bmz_apsh_4():
            mysql_conn_bmz_apsh_4.mysql_block_good()
            my_msg('Блок исправен')
        else:
            mysql_conn_bmz_apsh_4.mysql_block_bad()
            my_msg('Блок неисправен', '#A61E1E')
    except OSError:
        my_msg("ошибка системы")
    except SystemError:
        my_msg("внутренняя ошибка")
    except ModbusConnectException as mce:
        fault.debug_msg(mce, 1)
        my_msg(str(mce), '#A61E1E')
    finally:
        reset_test_bmz_apsh_4.reset_all()
        exit()
