#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Алгоритм проверки

Тип блока	Производитель
ПМЗ	Нет производителя
ПМЗ	Углеприбор
ПМЗ-П	Нет производителя
ПМЗ-П	Пульсар

"""

__all__ = ["TestPMZ"]

import sys

from time import sleep

from my_msgbox import *
from my_msgbox_2 import *
from gen_func_procedure import *
from gen_func_utils import *
from gen_mb_client import *
from gen_mysql_connect import *


class TestPMZ(object):

    __proc = Procedure()
    __reset = ResetRelay()
    __read_mb = ReadMB()
    __ctrl_kl = CtrlKL()
    __mysql_conn = MySQLConnect()
    __fault = Bug(True)

    list_ust_num = (1, 2, 3, 4, 5, 6, 7, 8, 9)
    list_ust_volt = (75.4, 92, 114, 125, 141, 156.4, 172, 182.4, 196)
    list_delta_t = []
    list_delta_percent = []
    list_result = []

    meas_volt_ust = 0.0
    coef_volt = 0.0
    calc_delta_t = 0.0

    msg_1 = "Убедитесь в отсутствии в панелях разъемов установленных блоков Подключите " \
            "блок ПМЗ в разъем Х14 на панели B"
    msg_2 = "Переключите тумблер режимов, расположенный на корпусе блока, в положение «Работа»"
    msg_3 = 'Установите регулятор уставок на блоке в положение'
    msg_4 = "Переключите тумблер на корпусе блока в положение «Проверка»"

    def __init__(self):
        pass

    def st_test_10(self) -> bool:
        if my_msg(self.msg_1):
            if my_msg(self.msg_2):
                return True
        return False

    def st_test_11(self) -> bool:
        """
        Тест 1. Проверка исходного состояния блока:
        :return:
        """
        self.__ctrl_kl.ctrl_relay('KL21', True)
        self.__reset.sbros_zashit_kl30_1s5()
        self.__fault.debug_msg("сброс защит", 3)
        in_a1, in_a2, in_a5 = self.__inputs_a()
        if in_a1 is False and in_a2 is False and in_a5 is True:
            pass
        else:
            self.__mysql_conn.mysql_ins_result('неисправен', '1')
            self.__fault.debug_msg("положение выходов блока не соответствует", 1)
            return False
        self.__fault.debug_msg("положение выходов блока соответствует", 4)
        self.__mysql_conn.mysql_ins_result('исправен', '1')
        return True

    def st_test_20(self) -> bool:
        """
        Тест 2. Проверка работоспособности блока в режиме «Проверка»
        Процедура 2.1. Проверка вероятности наличия короткого замыкания на входе измерительной цепи блока
        2.1.1. Проверка отсутствия вероятности возникновения межвиткового замыкания на стороне первичной обмотки TV1
        :return:
        """
        self.__mysql_conn.mysql_ins_result('идет тест 2.1', '2')
        self.meas_volt_ust = self.__proc.procedure_1_21_31()
        if self.meas_volt_ust != 0.0:
            return True
        self.__mysql_conn.mysql_ins_result("неисправен", "1")
        return False

    def st_test_21(self) -> bool:
        """
        2.1.4. Проверка отсутствия короткого замыкания на входе измерительной части блока:
        :return:
        """
        self.__fault.debug_msg("тест 2.1.4 начало\t", 3)
        self.__mysql_conn.mysql_ins_result('идет тест 2.1.4', '2')
        self.__ctrl_kl.ctrl_relay('KL63', True)
        sleep(1)
        min_volt = 0.4 * self.meas_volt_ust
        max_volt = 1.1 * self.meas_volt_ust
        meas_volt = self.__read_mb.read_analog()
        self.__fault.debug_msg(f'напряжение после включения KL63\t{meas_volt:.2f}\tдолжно быть '
                               f'от\t{min_volt:.2f}\tдо\t{max_volt:.2f}', 3)
        if min_volt <= meas_volt <= max_volt:
            pass
        else:
            self.__mysql_conn.mysql_ins_result('неисправен', '2')
            self.__mysql_conn.mysql_error(455)
            self.__reset.sbros_kl63_proc_1_21_31()
            return False
        self.__reset.sbros_kl63_proc_1_21_31()
        return True

    def st_test_22(self) -> bool:
        """
        Процедура 2.2. Процедура определения коэффициента отклонения фактического напряжения от номинального
        :return:
        """
        self.__fault.debug_msg("тест 2.2 начало\t", 3)
        self.__mysql_conn.mysql_ins_result('идет тест 2.2', '2')
        self.coef_volt = self.__proc.procedure_1_22_32()
        if self.coef_volt != 0.0:
            pass
        else:
            self.__mysql_conn.mysql_ins_result('неисправен', '2')
            self.__reset.stop_procedure_32()
            return False
        self.__reset.stop_procedure_32()
        return True

    def st_test_23(self) -> bool:
        """
        Процедура 2.3. Формирование нагрузочного сигнала U3:
        :return:
        """
        if my_msg(self.msg_4):
            pass
        else:
            return False
        self.__fault.debug_msg("тест 2.3 начало\t", 3)
        if self.__proc.start_procedure_1():
            calc_volt = self.__proc.start_procedure_212(coef_volt=self.coef_volt)
            if calc_volt != 0.0:
                if self.__proc.start_procedure_312(calc_volt=calc_volt):
                    return True
        self.__mysql_conn.mysql_ins_result('неисправен', '2')
        return False

    def st_test_24(self) -> bool:
        """
        2.4.  Проверка срабатывания блока от сигнала нагрузки:
        :return:
        """
        self.__ctrl_kl.ctrl_ai_code_v1(108)
        in_a1, in_a2, in_a5 = self.__inputs_a()
        if in_a1 is True and in_a2 is True and in_a5 is False:
            pass
        else:
            self.__fault.debug_msg("положение выходов блока не соответствует", 1)
            self.__reset.stop_procedure_3()
            self.__mysql_conn.mysql_ins_result('неисправен', '2')
            return False
        self.__fault.debug_msg("положение выходов блока соответствует", 4)
        self.__reset.stop_procedure_3()
        return True

    def st_test_25(self) -> bool:
        """
        2.4.2. Сброс защит после проверки
        :return:
        """
        self.__reset.sbros_zashit_kl30_1s5()
        self.__fault.debug_msg("сброс защит", 3)
        in_a1, in_a2, in_a5 = self.__inputs_a()
        if in_a1 is False and in_a2 is False and in_a5 is True:
            pass
        else:
            self.__fault.debug_msg("положение выходов блока не соответствует", 1)
            self.__mysql_conn.mysql_ins_result('неисправен', '2')
            return False
        self.__fault.debug_msg("положение выходов блока соответствует", 4)
        self.__mysql_conn.mysql_ins_result('исправен', '2')
        return True

    def st_test_30(self) -> bool:
        """
        Тест 3. Проверка срабатывания блока по уставкам
        :return:
        """
        if my_msg(self.msg_2):
            pass
        else:
            return False
        k = 0
        for i in self.list_ust_volt:
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
                return False
            # Δ%= 0.0038*U42[i]+2.27* U4[i]
            meas_volt = self.__read_mb.read_analog()
            calc_delta_percent = 0.0038 * meas_volt ** 2 + 2.27 * meas_volt
            self.list_delta_percent.append(f'{calc_delta_percent:.2f}')
            # 3.4.  Проверка срабатывания блока от сигнала нагрузки:
            for qw in range(4):
                self.calc_delta_t = self.__ctrl_kl.ctrl_ai_code_v0(104)
                self.__fault.debug_msg(f'время срабатывания, {self.calc_delta_t:.1f} мс', 'orange')
                self.__mysql_conn.mysql_add_message(f'уставка {self.list_ust_num[k]} '
                                                    f'дельта t: {self.calc_delta_t:.1f}')
                if self.calc_delta_t == 9999:
                    sleep(3)
                    qw += 1
                    self.__reset.sbros_zashit_kl30_1s5()
                    continue
                elif 100 < self.calc_delta_t < 9999:
                    sleep(3)
                    qw += 1
                    self.__reset.sbros_zashit_kl30_1s5()
                    continue
                else:
                    break
            self.__fault.debug_msg(f'время срабатывания, мс\t{self.calc_delta_t:.1f}', 2)
            if self.calc_delta_t < 10:
                self.list_delta_t.append(f'< 10')
            elif self.calc_delta_t > 100:
                self.list_delta_t.append(f'> 100')
            else:
                self.list_delta_t.append(f'{self.calc_delta_t:.1f}')
            self.__mysql_conn.mysql_add_message(f'уставка {self.list_ust_num[k]} дельта t: {self.calc_delta_t:.1f}')
            self.__mysql_conn.mysql_add_message(f'уставка {self.list_ust_num[k]} дельта %: {calc_delta_percent:.2f}')
            self.__reset.stop_procedure_3()
            in_a1, in_a2, in_a5 = self.__inputs_a()
            if in_a1 is True and in_a2 is True and in_a5 is False:
                self.__fault.debug_msg("положение выходов блока соответствует", 4)
                if self.__subtest_36():
                    k += 1
                    continue
                return False
            else:
                self.__fault.debug_msg("положение выходов блока не соответствует", 1)
                if self.__subtest_35(i=i, k=k):
                    if self.__subtest_36():
                        k += 1
                        continue
                self.__mysql_conn.mysql_ins_result('неисправен', '3')
                return False
        self.__mysql_conn.mysql_ins_result('исправен', '3')
        return True

    def __subtest_35(self, i: float, k: int) -> bool:
        """
        3.5. Формирование нагрузочного сигнала 1,1*U3[i]:
        :param i:
        :param k:
        :return:
        """
        self.__reset.sbros_zashit_kl30_1s5()
        self.__fault.debug_msg("сброс защит", 3)
        in_a1, in_a2, in_a5 = self.__inputs_a()
        if in_a1 is False and in_a2 is False and in_a5 is True:
            pass
        else:
            self.__fault.debug_msg("положение выходов блока не соответствует", 1)
            self.__mysql_conn.mysql_ins_result('неисправен', '3')
            return False
        self.__fault.debug_msg("положение выходов блока соответствует", 4)
        if self.__proc.procedure_1_25_35(coef_volt=self.coef_volt, setpoint_volt=i):
            pass
        else:
            return False
        # Δ%= 0.0038*U42[i]+2.27* U4[i]
        meas_volt = self.__read_mb.read_analog()
        calc_delta_percent = 0.0038 * meas_volt ** 2 + 2.27 * meas_volt
        self.list_delta_percent[-1] = f'{calc_delta_percent:.2f}'
        for wq in range(4):
            self.calc_delta_t = self.__ctrl_kl.ctrl_ai_code_v0(104)
            self.__fault.debug_msg(f'время срабатывания, {self.calc_delta_t:.1f} мс', 'orange')
            self.__mysql_conn.mysql_add_message(f'уставка {self.list_ust_num[k]} '
                                                f'дельта t: {self.calc_delta_t:.1f}')
            if self.calc_delta_t == 9999:
                sleep(3)
                wq += 1
                self.__reset.sbros_zashit_kl30_1s5()
                continue
            elif 100 < self.calc_delta_t < 9999:
                sleep(3)
                wq += 1
                self.__reset.sbros_zashit_kl30_1s5()
                continue
            else:
                break
        self.__fault.debug_msg(f'время срабатывания, {self.calc_delta_t:.1f} мс', 'orange')
        if self.calc_delta_t < 10:
            self.list_delta_t[-1] = f'< 10'
        elif self.calc_delta_t > 100:
            self.list_delta_t.append(f'> 100')
        else:
            self.list_delta_t[-1] = f'{self.calc_delta_t:.1f}'
        self.__mysql_conn.mysql_add_message(f'уставка {self.list_ust_num[k]} дельта t: {self.calc_delta_t:.1f}')
        self.__mysql_conn.mysql_add_message(f'уставка {self.list_ust_num[k]} дельта %: {calc_delta_percent:.2f}')
        in_a1, in_a2, in_a5 = self.__inputs_a()
        if in_a1 is True and in_a2 is True and in_a5 is False:
            pass
        else:
            self.__fault.debug_msg("положение выходов блока не соответствует", 1)
            self.__reset.stop_procedure_3()
            self.__mysql_conn.mysql_ins_result('неисправен', '3')
            return False
        self.__fault.debug_msg("положение выходов блока соответствует", 4)
        self.__reset.stop_procedure_3()
        return True

    def __subtest_36(self) -> bool:
        """
        3.6. Сброс защит после проверки
        :return:
        """
        self.__reset.sbros_zashit_kl30_1s5()
        self.__fault.debug_msg("сброс защит", 3)
        in_a1, in_a2, in_a5 = self.__inputs_a()
        if in_a1 is False and in_a2 is False and in_a5 is True:
            pass
        else:
            self.__fault.debug_msg("положение выходов блока не соответствует", 1)
            self.__mysql_conn.mysql_ins_result('неисправен', '3')
            return False
        self.__fault.debug_msg("положение выходов блока соответствует", 4)
        return True

    def __inputs_a(self):
        in_a1 = self.__read_mb.read_discrete(1)
        in_a2 = self.__read_mb.read_discrete(2)
        in_a5 = self.__read_mb.read_discrete(5)
        if in_a1 is None or in_a2 is None or in_a5 is None:
            raise ModbusConnectException(f'нет связи с контроллером')
        return in_a1, in_a2, in_a5

    def __inputs_b(self):
        in_b0 = self.__read_mb.read_discrete(8)
        if in_b0 is None:
            raise ModbusConnectException(f'нет связи с контроллером')
        return in_b0

    def st_test_pmz(self) -> bool:
        if self.st_test_10():
            if self.st_test_11():
                if self.st_test_20():
                    if self.st_test_21():
                        if self.st_test_22():
                            if self.st_test_23():
                                if self.st_test_24():
                                    if self.st_test_25():
                                        if self.st_test_30():
                                            return True
        return False

    def result_test_pmz(self):
        for g1 in range(len(self.list_delta_percent)):
            self.list_result.append((self.list_ust_num[g1], self.list_delta_percent[g1], self.list_delta_t[g1]))
        self.__mysql_conn.mysql_pmz_result(self.list_result)


if __name__ == '__main__':
    test_pmz = TestPMZ()
    reset_test_pmz = ResetRelay()
    mysql_conn_pmz = MySQLConnect()
    fault = Bug(True)
    try:
        if test_pmz.st_test_pmz():
            test_pmz.result_test_pmz()
            mysql_conn_pmz.mysql_block_good()
            my_msg('Блок исправен', 'green')
        else:
            test_pmz.result_test_pmz()
            mysql_conn_pmz.mysql_block_bad()
            my_msg('Блок неисправен', 'red')
    except OSError:
        my_msg("ошибка системы", 'red')
    except SystemError:
        my_msg("внутренняя ошибка", 'red')
    except ModbusConnectException as mce:
        fault.debug_msg(mce, 'red')
        my_msg(f'{mce}', 'red')
    finally:
        reset_test_pmz.reset_all()
        sys.exit()
