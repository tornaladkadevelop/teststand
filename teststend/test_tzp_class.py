#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Алгоритм проверки

Тип блока Производитель Уникальный номер
ТЗП Нет производителя 61
ТЗП Углеприбор 62
ТЗП-П Нет производителя 63
ТЗП-П Пульсар 64

"""

import sys
import logging

from time import time, sleep

from gen_func_procedure import *
from gen_func_utils import *
from my_msgbox import *
from my_msgbox_2 import *
from gen_mb_client import *
from gen_mysql_connect import *

__all__ = ["TestTZP"]


class TestTZP(object):
    
    def __init__(self):
        self.__reset = ResetRelay()
        self.__proc = Procedure()
        self.__read_mb = ReadMB()
        self.__ctrl_kl = CtrlKL()
        self.__mysql_conn = MySQLConnect()
        self.__fault = Bug(True)

        self.list_ust_num = (0.5, 0.6, 0.7, 0.8, 0.9, 1.0)
        self.list_ust_volt = (25.7, 29.8, 34.3, 39.1, 43.7, 48.5)
        self.list_delta_t = []
        self.list_delta_percent = []
        self.list_tzp_result = []

        self.coef_volt = 0.0

        self.msg_1 = "Переключите тумблер на корпусе блока в положение «Проверка» "
        self.msg_2 = "Переключите тумблер на корпусе блока в положение «Работа» "
        self.msg_3 = "Установите регулятор уставок на блоке в положение"

        logging.basicConfig(filename="TestTZP.log", level=logging.DEBUG, encoding="utf-8")

    def st_test_10(self) -> bool:
        """
        Тест 1. Проверка исходного состояния блока:
        :return:
        """
        in_a0 = self.__inputs_a0()
        if in_a0 is None:
            return False
        self.__mysql_conn.mysql_ins_result('идет тест 1', '1')
        logging.info("тест 1")
        self.__ctrl_kl.ctrl_relay('KL21', True)
        logging.info("включение KL21")
        self.__reset.sbros_zashit_kl30_1s5()
        in_a1, in_a5 = self.__inputs_a()
        logging.info(f'in_a1 = {in_a1} (False), in_a5 = {in_a5} (True)')
        if in_a1 is False and in_a5 is True:
            pass
        else:
            self.__mysql_conn.mysql_ins_result('неисправен', '1')
            if in_a1 is True:
                self.__fault.debug_msg("вход 1 не соответствует", 'red')
                self.__mysql_conn.mysql_error(277)
            elif in_a5 is False:
                self.__fault.debug_msg("вход 5 не соответствует", 'red')
                self.__mysql_conn.mysql_error(278)
            return False
        self.__fault.debug_msg("состояние выходов блока соответствует", 'green')
        return True

    def st_test_11(self) -> bool:
        """
        1.1. Проверка вероятности наличия короткого замыкания на входе измерительной цепи блока
        :return:
        """
        self.__mysql_conn.mysql_ins_result('идет тест 1.1', '1')
        meas_volt_ust = self.__proc.procedure_1_21_31()
        if meas_volt_ust != 0.0:
            pass
        else:
            self.__mysql_conn.mysql_ins_result('неисправен', '1')
            return False
        # 1.1.3. Проверка отсутствия короткого замыкания на входе измерительной части блока:
        self.__mysql_conn.mysql_ins_result('идет тест 1.2', '1')
        self.__ctrl_kl.ctrl_relay('KL63', True)
        sleep(1)
        min_volt = 0.6 * meas_volt_ust
        max_volt = 1.1 * meas_volt_ust
        meas_volt = self.__read_mb.read_analog()
        self.__fault.debug_msg(f'напряжение \t{meas_volt:.2f}', 'orange')
        if min_volt <= meas_volt <= max_volt:
            self.__fault.debug_msg("напряжение соответствует", 'green')
            pass
        else:
            self.__fault.debug_msg("напряжение не соответствует", 'red')
            self.__mysql_conn.mysql_ins_result('неисправен', '1')
            self.__mysql_conn.mysql_error(281)
            self.__reset.sbros_kl63_proc_1_21_31()
            return False
        self.__reset.sbros_kl63_proc_1_21_31()
        return True

    def st_test_12(self) -> bool:
        """
        1.2. Определение коэффициента отклонения фактического напряжения от номинального
        :return:
        """
        self.__mysql_conn.mysql_ins_result('идет тест 1.3', '1')
        self.coef_volt = self.__proc.procedure_1_22_32()
        if self.coef_volt != 0.0:
            pass
        else:
            self.__reset.stop_procedure_32()
            self.__mysql_conn.mysql_ins_result('неисправен', '1')
            return False
        self.__reset.stop_procedure_32()
        self.__fault.debug_msg("тест 1 пройден", 'green')
        self.__mysql_conn.mysql_ins_result('исправен', '1')
        return True

    def st_test_20(self) -> bool:
        """
        Тест 2. Проверка работоспособности блока в режиме «Проверка»
        :return:
        """
        if my_msg(f'{self.msg_1}'):
            pass
        else:
            return False
        self.__fault.debug_msg("тест 2.1", 'blue')
        self.__mysql_conn.mysql_ins_result('идет тест 2', '2')
        in_a1, in_a5 = self.__inputs_a()
        if in_a1 is True and in_a5 is False:
            pass
        elif in_a1 is False:
            self.__fault.debug_msg("положение входа 1 не соответствует", 'red')
            self.__mysql_conn.mysql_ins_result('неисправен', '2')
            self.__mysql_conn.mysql_error(282)
            return False
        elif in_a5 is True:
            self.__fault.debug_msg("положение входа 5 не соответствует", 'red')
            self.__mysql_conn.mysql_ins_result('неисправен', '2')
            self.__mysql_conn.mysql_error(283)
            return False
        self.__fault.debug_msg("положение выходов блока соответствует", 'green')
        return True

    def st_test_21(self) -> bool:
        """
        2.2. Сброс защит после проверки
        :return:
        """
        if my_msg(f'{self.msg_2}'):
            pass
        else:
            return False
        self.__fault.debug_msg("тест 2.2", 'blue')
        self.__mysql_conn.mysql_ins_result('идет тест 2.1', '2')
        self.__reset.sbros_zashit_kl30_1s5()
        in_a1, in_a5 = self.__inputs_a()
        if in_a1 is False and in_a5 is True:
            pass
        elif in_a1 is True:
            self.__fault.debug_msg("положение входа 1 не соответствует", 'red')
            self.__mysql_conn.mysql_ins_result('неисправен', '2')
            self.__mysql_conn.mysql_error(284)
            return False
        elif in_a5 is False:
            self.__fault.debug_msg("положение входа 5 не соответствует", 'red')
            self.__mysql_conn.mysql_ins_result('неисправен', '2')
            self.__mysql_conn.mysql_error(285)
            return False
        self.__fault.debug_msg("положение выходов блока соответствует", 'green')
        self.__mysql_conn.mysql_ins_result('исправен', '2')
        self.__fault.debug_msg("тест 2 пройден", 'green')
        return True

    def st_test_30(self) -> bool:
        """
        Тест 3. Проверка срабатывания блока по уставкам
        :return:
        """
        self.__fault.debug_msg("тест 3", 'blue')
        self.__mysql_conn.mysql_ins_result('идет тест 3', '3')
        k = 0
        for i in self.list_ust_volt:
            self.__mysql_conn.mysql_ins_result(f'проверка уставки {self.list_ust_num[k]}', '3')
            msg_result = my_msg_2(f'{self.msg_3} {self.list_ust_num[k]}')
            if msg_result == 0:
                pass
            elif msg_result == 1:
                return False
            elif msg_result == 2:
                self.__mysql_conn.mysql_add_message(f'уставка {self.list_ust_num[k]} пропущена')
                self.list_delta_percent.append('пропущена')
                self.list_delta_t.append('пропущена')
                k += 1
                continue
            if self.__proc.procedure_1_24_34(coef_volt=self.coef_volt, setpoint_volt=i):
                pass
            else:
                self.__mysql_conn.mysql_ins_result('неисправен', '4')
                return False
            meas_volt = self.__read_mb.read_analog()
            calc_delta_percent = 0.0044 * meas_volt ** 2 + 2.274 * meas_volt
            self.list_delta_percent.append(f'{calc_delta_percent:.2f}')
            if 0.9 * i / self.coef_volt <= meas_volt <= 1.1 * i / self.coef_volt:
                self.__fault.debug_msg(f'напряжение соответствует {meas_volt:.2f}', 'orange')
                self.__mysql_conn.progress_level(0.0)
                self.__ctrl_kl.ctrl_relay('KL63', True)
                in_b0, in_b1 = self.__inputs_b()
                while in_b0 is False:
                    in_b0, in_b1 = self.__inputs_b()
                start_timer = time()
                sub_timer = 0
                in_a1, in_a5 = self.__inputs_a()
                while in_a5 is True and sub_timer <= 370:
                    sleep(0.2)
                    sub_timer = time() - start_timer
                    self.__fault.debug_msg(f'времени прошло {sub_timer:.1f}', 'orange')
                    self.__mysql_conn.progress_level(sub_timer)
                    in_a1, in_a5 = self.__inputs_a()
                stop_timer = time()
                self.__mysql_conn.progress_level(0.0)
                self.__ctrl_kl.ctrl_relay('KL63', False)
                calc_delta_t = stop_timer - start_timer
                self.__reset.stop_procedure_3()
                self.__fault.debug_msg(f'тест 3 delta t: {calc_delta_t:.1f}', 'orange')
                self.list_delta_t.append(f'{calc_delta_t:.1f}')
                self.__mysql_conn.mysql_add_message(f'уставка {self.list_ust_num[k]} '
                                                    f'дельта t: {calc_delta_t:.1f}')
                self.__mysql_conn.mysql_add_message(f'уставка {self.list_ust_num[k]} '
                                                    f'дельта %: {calc_delta_percent:.2f}')
                in_a1, in_a5 = self.__inputs_a()
                if calc_delta_t <= 360 and in_a1 is True and in_a5 is False:
                    # Если в период времени до 6 минут входа DI.A1, DI.A5 занимают
                    # состояние, указанное в таблице выше, то переходим к п.3.6.
                    self.__fault.debug_msg("время переключения соответствует", 'green')
                    if self.__subtest_35():
                        k += 1
                        continue
                    else:
                        self.__mysql_conn.mysql_add_message(f'уставка {self.list_ust_num[k]}: '
                                                            f'не срабатывает сброс защит')
                        return False
                else:
                    # Если в период времени до 6 минут входа DI.A1, DI.A5 не занимают
                    # состояние, указанное в таблице выше, то переходим к п.3.5.
                    self.__fault.debug_msg("время переключения не соответствует", 'red')
                    self.__mysql_conn.mysql_error(287)
                    if self.__subtest_35():
                        k += 1
                        continue
                    else:
                        self.__mysql_conn.mysql_add_message(f'уставка {self.list_ust_num[k]}: '
                                                            f'не срабатывает сброс защит')
                        return False
            else:
                self.__fault.debug_msg("напряжение U4 не соответствует", 'red')
                self.__mysql_conn.mysql_error(286)
                self.__reset.stop_procedure_3()
        self.__mysql_conn.mysql_ins_result('исправен', '3')
        return True
    
    def __subtest_35(self) -> bool:
        self.__mysql_conn.mysql_ins_result('идет тест 3.5', '3')
        self.__reset.sbros_zashit_kl30_1s5()
        sleep(1)
        in_a1, in_a5 = self.__inputs_a()
        if in_a1 is False and in_a5 is True:
            self.__fault.debug_msg("положение выходов блока соответствует", 'green')
            return True
        else:
            self.__mysql_conn.mysql_ins_result('неисправен', '3')
            if in_a1 is True:
                self.__fault.debug_msg("положение входа 1 не соответствует", 'red')
                self.__mysql_conn.mysql_error(284)
            elif in_a5 is False:
                self.__fault.debug_msg("положение входа 5 не соответствует", 'red')
                self.__mysql_conn.mysql_error(285)
            return False

    def __inputs_a0(self):
        in_a0 = self.__read_mb.read_discrete(0)
        if in_a0 is None:
            logging.error(f'нет связи с контроллером')
            raise ModbusConnectException(f'нет связи с контроллером')
        return in_a0

    def __inputs_a(self):
        in_a1 = self.__read_mb.read_discrete(1)
        in_a5 = self.__read_mb.read_discrete(5)
        if in_a1 is None or in_a5 is None:
            logging.error(f'нет связи с контроллером')
            raise ModbusConnectException(f'нет связи с контроллером')
        return in_a1, in_a5
    
    def __inputs_b(self):
        in_b0 = self.__read_mb.read_discrete(8)
        in_b1 = self.__read_mb.read_discrete(9)
        if in_b0 is None or in_b1 is None:
            logging.error(f'нет связи с контроллером')
            raise ModbusConnectException(f'нет связи с контроллером')
        return in_b0, in_b1

    def st_test_tzp(self) -> bool:
        if self.st_test_10():
            if self.st_test_11():
                if self.st_test_12():
                    if self.st_test_20():
                        if self.st_test_21():
                            if self.st_test_30():
                                return True
        return False

    def result_test_tzp(self):
        for t in range(len(self.list_delta_percent)):
            self.list_tzp_result.append((self.list_ust_num[t], self.list_delta_percent[t], self.list_delta_t[t]))
        self.__mysql_conn.mysql_tzp_result(self.list_tzp_result)


if __name__ == '__main__':
    test_tzp = TestTZP()
    reset_test_tzp = ResetRelay()
    mysql_conn_tzp = MySQLConnect()
    fault = Bug(True)
    try:
        if test_tzp.st_test_tzp():
            test_tzp.result_test_tzp()
            mysql_conn_tzp.mysql_block_good()
            my_msg('Блок исправен', 'green')
        else:
            test_tzp.result_test_tzp()
            mysql_conn_tzp.mysql_block_bad()
            my_msg('Блок неисправен', 'red')
    except OSError:
        my_msg("ошибка системы", 'red')
    except SystemError:
        my_msg("внутренняя ошибка", 'red')
    except ModbusConnectException as mce:
        fault.debug_msg(mce, 'red')
        my_msg(f'{mce}', 'red')
    finally:
        reset_test_tzp.reset_all()
        sys.exit()
