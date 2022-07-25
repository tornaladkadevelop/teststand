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
from gen_subtest import Subtest2in

__all__ = ["TestTZP"]


class TestTZP:
    
    def __init__(self):
        self.reset = ResetRelay()
        self.proc = Procedure()
        self.read_mb = ReadMB()
        self.read_di = ReadDI()
        self.ctrl_kl = CtrlKL()
        self.mysql_conn = MySQLConnect()
        self.fault = Bug(None)
        self.subtest = Subtest2in()

        self._list_ust_num = (0.5, 0.6, 0.7, 0.8, 0.9, 1.0)
        self._list_ust_volt = (25.7, 29.8, 34.3, 39.1, 43.7, 48.5)
        self._list_delta_t = []
        self._list_delta_percent = []
        self._list_tzp_result = []

        self._coef_volt = 0.0
        self._health_flag: bool = False

        self._msg_1 = "Переключите тумблер на корпусе блока в положение «Проверка» "
        self._msg_2 = "Переключите тумблер на корпусе блока в положение «Работа» "
        self._msg_3 = "Установите регулятор уставок на блоке в положение"

        logging.basicConfig(filename="C:\Stend\project_class\log\TestTZP.log",
                            filemode="w",
                            level=logging.DEBUG,
                            encoding="utf-8",
                            format='[%(asctime)s: %(name)s: %(levelname)s] %(message)s')
        logging.getLogger('mysql').setLevel('DEBUG')
        self.logger = logging.getLogger(__name__)

    def st_test_10(self) -> bool:
        """
        Тест 1. Проверка исходного состояния блока:
        :return:
        """
        self.logger.debug("тест 1")
        self.read_di.inputs_di('in_a0')
        self.mysql_conn.mysql_ins_result('идет тест 1', '1')
        self.ctrl_kl.ctrl_relay('KL21', True)
        self.logger.debug("включен KL21")
        self.reset.sbros_zashit_kl30_1s5()
        if self.subtest.subtest_2di(test_num=1, subtest_num=1.0, err_code_a1=277, err_code_a2=278, position_a1=False,
                                    position_a2=True, inp_2='in_a5'):
            return True
        return False

    def st_test_11(self) -> bool:
        """
        1.1. Проверка вероятности наличия короткого замыкания на входе измерительной цепи блока
        1.1.3. Проверка отсутствия короткого замыкания на входе измерительной части блока:
        :return:
        """
        self.logger.debug("старт теста 1.1")
        self.mysql_conn.mysql_ins_result('идет тест 1.1', '1')
        min_volt, max_volt = self.proc.procedure_1_21_31_v1()
        self.mysql_conn.mysql_ins_result('идет тест 1.2', '1')
        self.logger.debug('тест 1.2')
        self.ctrl_kl.ctrl_relay('KL63', True)
        self.logger.debug('включение KL63')
        sleep(1)
        meas_volt = self.read_mb.read_analog()
        self.logger.debug(f'напряжение после включения KL63 \t{meas_volt:.2f}')
        self.reset.sbros_kl63_proc_1_21_31()
        if min_volt <= meas_volt <= max_volt:
            self.logger.debug("напряжение соответствует")
            return True
        else:
            # self.mysql_conn.mysql_ins_result('неисправен', '1')
            # self.mysql_conn.mysql_error(281)
            self.logger.debug("напряжение не соответствует")
            raise HardwareException("Выходное напряжение не соответствует заданию. \n"
                                    "Неисправность узла формирования напряжения в стенде")

    def st_test_12(self) -> bool:
        """
        1.2. Определение коэффициента отклонения фактического напряжения от номинального
        :return:
        """
        self.mysql_conn.mysql_ins_result('идет тест 1.3', '1')
        self.logger.debug("тест 1.3")
        self._coef_volt = self.proc.procedure_1_22_32()
        self.logger.debug(f"процедура 1, 2.2, 3.2, Ku: {self._coef_volt}")
        self.reset.stop_procedure_32()
        self.logger.debug("сброс всех реле")
        if self._coef_volt != 0.0:
            self.mysql_conn.mysql_ins_result('исправен', '1')
            self.logger.debug("тест 1 завершен")
            return True
        else:
            self.mysql_conn.mysql_ins_result('неисправен', '1')
            return False

    def st_test_20(self) -> bool:
        """
        Тест 2. Проверка работоспособности блока в режиме «Проверка»
        :return:
        """
        self.logger.debug("тест 2.0")
        if my_msg(f'{self._msg_1}'):
            pass
        else:
            return False
        self.mysql_conn.mysql_ins_result('идет тест 2.0', '2')
        if self.subtest.subtest_2di(test_num=2, subtest_num=2.0, err_code_a1=282, err_code_a2=283,
                                    position_a1=True, position_a2=False, inp_2='in_a5'):
            return True
        return False

    def st_test_21(self) -> bool:
        """
        2.2. Сброс защит после проверки
        :return:
        """
        self.logger.debug("тест 2.1")
        if my_msg(f'{self._msg_2}'):
            pass
        else:
            return False
        self.mysql_conn.mysql_ins_result('идет тест 2.1', '2')
        self.reset.sbros_zashit_kl30_1s5()
        if self.subtest.subtest_2di(test_num=2, subtest_num=2.1, err_code_a1=284, err_code_a2=285,
                                    position_a1=False, position_a2=True, inp_2='in_a5'):
            return True
        return False

    def st_test_30(self) -> bool:
        """
        Тест 3. Проверка срабатывания блока по уставкам
        :return:
        """
        self.logger.debug(f'тест 3.0')
        self.mysql_conn.mysql_ins_result('идет тест 3', '3')
        k = 0
        for i in self._list_ust_volt:
            self.logger.debug(f'цикл: {k}, уставка: {i}')
            self.mysql_conn.mysql_ins_result(f'проверка уставки {self._list_ust_num[k]}', '3')
            msg_result = my_msg_2(f'{self._msg_3} {self._list_ust_num[k]}')
            self.logger.debug(f'от пользователя пришло: {msg_result}')
            if msg_result == 0:
                pass
            elif msg_result == 1:
                self.logger.debug(f'отмена')
                return False
            elif msg_result == 2:
                self.mysql_conn.mysql_add_message(f'уставка {self._list_ust_num[k]} пропущена')
                self._list_delta_percent.append('пропущена')
                self._list_delta_t.append('пропущена')
                self.logger.debug(f'уставка: {k} пропущена')
                k += 1
                continue
            if self.proc.procedure_x4_to_x5(coef_volt=self._coef_volt, setpoint_volt=i):
                self.logger.debug(f'процедура 1, 2.4, 3.4: пройдена')
                pass
            else:
                self.mysql_conn.mysql_ins_result('неисправен', '4')
                self.logger.debug(f'процедура 1, 2.4, 3.4: не пройдена')
                return False
            meas_volt = self.read_mb.read_analog()
            self.logger.debug(f'измеренное напряжение: {meas_volt}')
            calc_delta_percent = 0.0044 * meas_volt ** 2 + 2.274 * meas_volt
            self.logger.debug(f'd%: {calc_delta_percent}')
            self._list_delta_percent.append(f'{calc_delta_percent:.2f}')
            if 0.9 * i / self._coef_volt <= meas_volt <= 1.1 * i / self._coef_volt:
                self.logger.debug(f'напряжение соответствует: {meas_volt:.2f}')
                self.mysql_conn.progress_level(0.0)
                self.ctrl_kl.ctrl_relay('KL63', True)
                self.logger.debug("включение KL63")
                in_b0, *_ = self.read_di.inputs_di('in_b0')
                self.logger.debug(f"in_b0 = {in_b0} (True)")
                while in_b0 is False:
                    self.logger.debug(f"in_b0 = {in_b0} (False)")
                    in_b0, *_ = self.read_di.inputs_di('in_b0')
                start_timer = time()
                self.logger.debug(f"начало отсчета: {start_timer}")
                sub_timer = 0
                in_a1, in_a5 = self.read_di.inputs_di("in_a1")
                self.logger.debug(f"in_a1 = {in_a5} (False)")
                while in_a5 is True and sub_timer <= 370:
                    sleep(0.2)
                    sub_timer = time() - start_timer
                    self.logger.debug(f"времени прошло {sub_timer:.1f}")
                    self.mysql_conn.progress_level(sub_timer)
                    in_a5, *_ = self.read_di.inputs_di('in_a5')
                    self.logger.debug(f"in_a1 = {in_a5} (False)")
                stop_timer = time()
                self.logger.debug(f"конец отсчета")
                self.mysql_conn.progress_level(0.0)
                self.ctrl_kl.ctrl_relay('KL63', False)
                self.logger.debug(f"отключение KL63")
                calc_delta_t = stop_timer - start_timer
                self.logger.debug(f"dt: {calc_delta_t}")
                self.reset.stop_procedure_3()
                self.logger.debug(f"останов процедуры 3")
                self._list_delta_t.append(f'{calc_delta_t:.1f}')
                self.mysql_conn.mysql_add_message(f'уставка {self._list_ust_num[k]} '
                                                  f'дельта t: {calc_delta_t:.1f}')
                self.mysql_conn.mysql_add_message(f'уставка {self._list_ust_num[k]} '
                                                  f'дельта %: {calc_delta_percent:.2f}')
                in_a1, in_a5 = self.read_di.inputs_di('in_a1', 'in_a5')
                self.logger.debug(f"in_a1 = {in_a1} (True), in_a5 = {in_a5} (False), время: {calc_delta_t}")
                if calc_delta_t <= 360 and in_a1 is True and in_a5 is False:
                    # Если в период времени до 6 минут входа DI.A1, DI.A5 занимают
                    # состояние, указанное в таблице выше, то переходим к п.3.6.
                    if self.subtest_35():
                        self.logger.debug(f"переход на новую итерацию цикла")
                        k += 1
                        continue
                    else:
                        self.mysql_conn.mysql_add_message(f'уставка {self._list_ust_num[k]}: '
                                                          f'не срабатывает сброс защит')
                        self.logger.debug(f'уставка {self._list_ust_num[k]}: не срабатывает сброс защит')
                        return False
                else:
                    # Если в период времени до 6 минут входа DI.A1, DI.A5 не занимают
                    # состояние, указанное в таблице выше, то переходим к п.3.5.
                    self.logger.debug("время переключения не соответствует")
                    self.mysql_conn.mysql_error(287)
                    if self.subtest_35():
                        k += 1
                        self.logger.debug(f"переход на новую итерацию цикла")
                        continue
                    else:
                        self.mysql_conn.mysql_add_message(f'уставка {self._list_ust_num[k]}: '
                                                          f'не срабатывает сброс защит')
                        self.logger.debug(f'уставка {self._list_ust_num[k]}: не срабатывает сброс защит')
                        return False
            else:
                self.logger.debug("напряжение U4 не соответствует")
                self.mysql_conn.mysql_error(286)
                self.reset.stop_procedure_3()
                self.logger.debug("останов процедуры 3")
        self.mysql_conn.mysql_ins_result('исправен', '3')
        self.logger.debug("тест 3 завершен")
        return True
    
    def subtest_35(self) -> bool:
        self.mysql_conn.mysql_ins_result('идет тест 3.5', '3')
        self.logger.debug("идет тест 3.5")
        self.reset.sbros_zashit_kl30_1s5()
        self.logger.debug("сброс защит")
        sleep(1)
        if self.subtest.subtest_2di(test_num=3, subtest_num=3.5, err_code_a1=284, err_code_a2=285,
                                    position_a1=False, position_a2=True, inp_2='in_a5'):
            return True
        return False

    def st_test_tzp(self) -> [bool, bool]:
        if self.st_test_10():
            if self.st_test_11():
                if self.st_test_12():
                    if self.st_test_20():
                        if self.st_test_21():
                            if self.st_test_30():
                                return True, self._health_flag
        return False, self._health_flag

    def result_test_tzp(self):
        for t in range(len(self._list_delta_percent)):
            self._list_tzp_result.append((self._list_ust_num[t], self._list_delta_percent[t], self._list_delta_t[t]))
            self.logger.debug(f'{self._list_ust_num[t]}, {self._list_delta_percent[t]}, {self._list_delta_t[t]}')
        self.mysql_conn.mysql_tzp_result(self._list_tzp_result)


if __name__ == '__main__':
    test_tzp = TestTZP()
    reset_test_tzp = ResetRelay()
    mysql_conn_tzp = MySQLConnect()
    fault = Bug(True)
    try:
        test, health_flag = test_tzp.st_test_tzp()
        if test and not health_flag:
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
    except HardwareException as hwe:
        my_msg(f'{hwe}', 'red')
    finally:
        reset_test_tzp.reset_all()
        sys.exit()
