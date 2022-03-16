#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Алгоритм проверки

Тип блока	Производитель
УМЗ	        Нет производителя

"""

import sys

from time import sleep

from gen_func_procedure import *
from gen_func_utils import *
from my_msgbox import *
from my_msgbox_2 import *
from gen_mb_client import *
from gen_mysql_connect import *

__all__ = ["TestUMZ"]


class TestUMZ(object):

    __reset = ResetRelay()
    __proc = Procedure()
    __read_mb = ReadMB()
    __ctrl_kl = CtrlKL()
    __mysql_conn = MySQLConnect()
    __fault = Bug(True)

    list_ust_volt = (22.6, 27.1, 31.9, 36.5, 41.3, 46.4, 50.2, 54.7, 59.3, 63.8, 68.4)
    list_ust_num = (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11)
    list_delta_t_ab = []
    list_delta_t_vg = []
    list_delta_percent_ab = []
    list_delta_percent_vg = []
    list_result = []
    meas_volt_ab = 0
    meas_volt_vg = 0
    test_setpoint_ab = False
    test_setpoint_vg = False
    coef_volt: float

    msg_1 = "Убедитесь в отсутствии в панелях разъемов установленных блоков Подключите " \
            "блок УМЗ в разъем Х8 на панели B с помощью соответствующей кабельной сборки"
    msg_2 = "Переключите тумблер режимов, расположенный на корпусе блока, в положение «Работа»"
    msg_3 = "Переведите оба регулятора уставок на корпусе блока в положение «1»"
    msg_4 = "Произведите взвод защит, нажав на корпусе блока на кнопку «Взвод»"
    msg_5 = 'Установите оба регулятора уставок на блоке в положение'

    def __init__(self):
        pass
    
    def st_test_10(self) -> bool:
        """
        Тест 1. Проверка исходного состояния блока:
        :return:
        """
        if my_msg(self.msg_1):
            if my_msg(self.msg_2):
                if my_msg(self.msg_3):
                    if my_msg(self.msg_4):
                        return True
        return False

    def st_test_11(self) -> bool:
        self.__mysql_conn.mysql_ins_result("идет тест 1.0", "1")
        in_a1, in_a5 = self.__inputs_a()
        if in_a1 is False and in_a5 is True:
            pass
        else:
            self.__mysql_conn.mysql_ins_result("неисправен", "1")
            if in_a1 is True:
                self.__mysql_conn.mysql_error(476)
            elif in_a5 is False:
                self.__mysql_conn.mysql_error(477)
            return False
        return True

    def st_test_12(self) -> bool:
        """
        1.1. Проверка вероятности наличия короткого замыкания на входе измерительной цепи блока
        :return:
        """
        self.__mysql_conn.mysql_ins_result("идет тест 1.1", "1")
        meas_volt_ust = self.__proc.procedure_1_21_31()
        if meas_volt_ust != 0.0:
            pass
        else:
            self.__mysql_conn.mysql_ins_result("неисправен", "1")
            return False
        # 1.1.2. Проверка отсутствия короткого замыкания на входе измерительной части блока:
        self.__mysql_conn.mysql_ins_result("идет тест 1.1.2", "1")
        self.__ctrl_kl.ctrl_relay('KL63', True)
        sleep(1)
        min_volt = 0.4 * meas_volt_ust
        max_volt = 1.1 * meas_volt_ust
        meas_volt = self.__read_mb.read_analog()
        self.__fault.debug_msg(f'напряжение после включения KL63 \t{meas_volt:.2f}', 'orange')
        if min_volt <= meas_volt <= max_volt:
            pass
        else:
            self.__fault.debug_msg("измеренное напряжение не соответствует заданному", 'red')
            self.__mysql_conn.mysql_ins_result('неисправен', '1')
            self.__mysql_conn.mysql_error(478)
            self.__reset.sbros_kl63_proc_1_21_31()
            return False
        self.__fault.debug_msg("измеренное напряжение соответствует заданному", 'green')
        self.__reset.sbros_kl63_proc_1_21_31()
        return True

    def st_test_13(self) -> bool:
        """
        1.2. Определение коэффициента Кс отклонения фактического напряжения от номинального
        :return:
        """
        self.__mysql_conn.mysql_ins_result("идет тест 1.2", "1")
        self.coef_volt = self.__proc.procedure_1_22_32()
        if self.coef_volt != 0.0:
            pass
        else:
            self.__mysql_conn.mysql_ins_result('неисправен', '1')
            self.__mysql_conn.mysql_error(150)
            return False
        self.__fault.debug_msg(f'коэф. сети\t {self.coef_volt:.2f}', 'orange')
        self.__mysql_conn.mysql_ins_result('исправен', '1')
        self.__reset.stop_procedure_32()
        return True

    def st_test_20(self) -> bool:
        """
        Тест 2. Проверка срабатывания защиты канала АБ по уставкам
        :return:
        """
        if my_msg(self.msg_4):
            pass
        else:
            return False
        k = 0
        for i in self.list_ust_volt:
            self.__mysql_conn.mysql_ins_result("идет тест", "2")
            msg_result = my_msg_2(f'{self.msg_5} {self.list_ust_num[k]}')
            if msg_result == 0:
                pass
            elif msg_result == 1:
                return False
            elif msg_result == 2:
                self.__mysql_conn.mysql_add_message(f'уставка {self.list_ust_num[k]} пропущена')
                self.list_delta_percent_ab.append('пропущена')
                self.list_delta_t_ab.append('пропущена')
                self.list_delta_percent_vg.append('пропущена')
                self.list_delta_t_vg.append('пропущена')
                k += 1
                continue
            progress_msg = f'формируем U уставки'
            self.__mysql_conn.mysql_ins_result(f'{progress_msg} {k}', '2')
            if self.__proc.procedure_1_24_34(coef_volt=self.coef_volt, setpoint_volt=i):
                pass
            else:
                self.__mysql_conn.mysql_ins_result('неисправен', '2')
                return False
            progress_msg = f'канал АБ дельта t'
            self.__mysql_conn.mysql_ins_result(f'{progress_msg} {k}', '2')
            calc_delta_t_ab = self.__ctrl_kl.ctrl_ai_code_v0(109)
            if calc_delta_t_ab != 9999:
                pass
            else:
                return False
            self.list_delta_t_ab.append(f'{calc_delta_t_ab:.1f}')
            in_a1, in_a5 = self.__inputs_a()
            if in_a1 is True and in_a5 is False:
                # Δ%= 0,00004762*(U4)2+9,5648* U4
                progress_msg = f'канал АБ дельта %'
                self.__mysql_conn.mysql_ins_result(f'{progress_msg} {k}', '2')
                self.meas_volt_ab = self.__read_mb.read_analog()
                calc_delta_percent_ab = 0.00004762 * self.meas_volt_ab ** 2 + 9.5648 * self.meas_volt_ab
                self.list_delta_percent_ab.append(f'{calc_delta_percent_ab:.2f}')
                self.test_setpoint_ab = True
                self.__mysql_conn.mysql_add_message(f'уставка {self.list_ust_num[k]} '
                                                    f'дельта t: {calc_delta_t_ab:.1f}')
                self.__mysql_conn.mysql_add_message(f'уставка {self.list_ust_num[k]} '
                                                    f'дельта %: {calc_delta_percent_ab:.2f}')
            else:
                self.test_setpoint_ab = False
            self.__ctrl_kl.ctrl_relay('KL73', True)
            if my_msg(self.msg_4):
                pass
            else:
                return False
            progress_msg = f'канал ВГ дельта t'
            self.__mysql_conn.mysql_ins_result(f'{progress_msg} {k}', '2')
            calc_delta_t_vg = self.__ctrl_kl.ctrl_ai_code_v0(109)
            if calc_delta_t_ab != 9999:
                pass
            else:
                return False
            self.list_delta_t_vg.append(f'{calc_delta_t_vg:.1f}')
            in_a1, in_a5 = self.__inputs_a()
            if in_a1 is True and in_a5 is False:
                # Δ%= 0,00004762*(U4)2+9,5648* U4
                progress_msg = f'канал ВГ дельта %'
                self.__mysql_conn.mysql_ins_result(f'{progress_msg} {k}', '2')
                self.meas_volt_vg = self.__read_mb.read_analog()
                calc_delta_percent_vg = 0.00004762 * self.meas_volt_vg ** 2 + 9.5648 * self.meas_volt_vg
                self.list_delta_percent_vg.append(f'{calc_delta_percent_vg:.2f}')
                self.test_setpoint_vg = True
                self.__mysql_conn.mysql_add_message(f'уставка {self.list_ust_num[k]} '
                                                    f'дельта t: {calc_delta_t_vg:.1f}')
                self.__mysql_conn.mysql_add_message(f'уставка {self.list_ust_num[k]} '
                                                    f'дельта %: {calc_delta_percent_vg:.2f}')
            else:
                self.test_setpoint_vg = False
            self.__ctrl_kl.ctrl_relay('KL73', False)
            if my_msg(self.msg_4):
                pass
            else:
                return False
            self.__reset.stop_procedure_3()
            if self.test_setpoint_ab is True and self.test_setpoint_vg is True:
                k += 1
                continue
            elif self.test_setpoint_ab is False and self.test_setpoint_vg is False:
                progress_msg = f'повышаем U уставки'
                self.__mysql_conn.mysql_ins_result(f'{progress_msg} {k}', '2')
                if self.__proc.procedure_1_25_35(coef_volt=self.coef_volt, setpoint_volt=i):
                    pass
                else:
                    self.__mysql_conn.mysql_ins_result('неисправен', '2')
                    return False
                calc_delta_t_ab = self.__ctrl_kl.ctrl_ai_code_v0(109)
                if calc_delta_t_ab != 9999:
                    pass
                else:
                    return False
                self.list_delta_t_ab[-1] = f'{calc_delta_t_ab:.1f}'
                in_a1, in_a5 = self.__inputs_a()
                if in_a1 is True and in_a5 is False:
                    # Δ%= 0,00004762*(U4)2+9,5648* U4
                    self.meas_volt_ab = self.__read_mb.read_analog()
                    calc_delta_percent_ab = 0.00004762 * self.meas_volt_ab ** 2 + 9.5648 * self.meas_volt_ab
                    self.list_delta_percent_ab[-1] = f'{calc_delta_percent_ab:.2f}'
                    self.test_setpoint_ab = True
                    self.__mysql_conn.mysql_add_message(f'уставка {self.list_ust_num[k]} '
                                                        f'дельта t: {calc_delta_t_ab:.1f}')
                else:
                    self.test_setpoint_ab = False
                self.__ctrl_kl.ctrl_relay('KL73', True)
                if my_msg(self.msg_4):
                    pass
                else:
                    return False
                calc_delta_t_vg = self.__ctrl_kl.ctrl_ai_code_v0(109)
                if calc_delta_t_ab != 9999:
                    pass
                else:
                    return False
                self.list_delta_t_vg[-1] = f'{calc_delta_t_vg:.1f}'
                in_a1, in_a5 = self.__inputs_a()
                if in_a1 is True and in_a5 is False:
                    # Δ%= 0,00004762*(U4)2+9,5648* U4
                    self.meas_volt_vg = self.__read_mb.read_analog()
                    calc_delta_percent_vg = 0.00004762 * self.meas_volt_vg ** 2 + 9.5648 * self.meas_volt_vg
                    self.list_delta_percent_vg[-1] = f'{calc_delta_percent_vg:.2f}'
                    self.test_setpoint_vg = True
                    self.__mysql_conn.mysql_add_message(f'уставка {self.list_ust_num[k]} '
                                                        f'дельта t: {calc_delta_t_vg:.1f}')
                    self.__mysql_conn.mysql_add_message(f'уставка {self.list_ust_num[k]} '
                                                        f'дельта %: {calc_delta_percent_vg:.2f}')
                else:
                    self.test_setpoint_vg = False
                self.__ctrl_kl.ctrl_relay('KL73', False)
                if my_msg(self.msg_4):
                    pass
                else:
                    return False
                self.__reset.stop_procedure_3()
                if self.test_setpoint_ab is True and self.test_setpoint_vg is True:
                    k += 1
                    continue
                else:
                    return False
            elif self.test_setpoint_ab is False and self.test_setpoint_vg is True:
                if self.__proc.procedure_1_25_35(coef_volt=self.coef_volt, setpoint_volt=i):
                    pass
                else:
                    self.__mysql_conn.mysql_ins_result('неисправен', '2')
                    return False
                if my_msg(self.msg_4):
                    pass
                else:
                    return False
                calc_delta_t_ab = self.__ctrl_kl.ctrl_ai_code_v0(109)
                if calc_delta_t_ab != 9999:
                    pass
                else:
                    return False
                self.list_delta_t_ab[-1] = f'{calc_delta_t_ab:.1f}'
                in_a1, in_a5 = self.__inputs_a()
                if in_a1 is True and in_a5 is False:
                    # Δ%= 0,00004762*(U4)2+9,5648* U4
                    self.meas_volt_ab = self.__read_mb.read_analog()
                    calc_delta_percent_ab = 0.00004762 * self.meas_volt_ab ** 2 + 9.5648 * self.meas_volt_ab
                    self.list_delta_percent_ab[-1] = f'{calc_delta_percent_ab:.2f}'
                    self.test_setpoint_ab = True
                    self.__mysql_conn.mysql_add_message(f'уставка {self.list_ust_num[k]} '
                                                        f'дельта t: {calc_delta_t_ab:.1f}')
                    self.__mysql_conn.mysql_add_message(f'уставка {self.list_ust_num[k]} '
                                                        f'дельта %: {calc_delta_percent_ab:.2f}')
                else:
                    self.test_setpoint_ab = False
                self.__reset.stop_procedure_3()
                if my_msg(self.msg_4):
                    pass
                else:
                    return False
                if self.test_setpoint_ab is True:
                    k += 1
                    continue
                else:
                    return False
            elif self.test_setpoint_ab is True and self.test_setpoint_vg is False:
                if self.__proc.procedure_1_25_35(coef_volt=self.coef_volt, setpoint_volt=i):
                    pass
                else:
                    self.__mysql_conn.mysql_ins_result('неисправен', '2')
                    return False
                self.__ctrl_kl.ctrl_relay('KL73', True)
                if my_msg(self.msg_4):
                    pass
                else:
                    return False
                calc_delta_t_vg = self.__ctrl_kl.ctrl_ai_code_v0(109)
                if calc_delta_t_vg != 9999:
                    pass
                else:
                    return False
                self.list_delta_t_vg[-1] = f'{calc_delta_t_vg:.1f}'
                in_a1, in_a5 = self.__inputs_a()
                if in_a1 is True and in_a5 is False:
                    # Δ%= 0,00004762*(U4)2+9,5648* U4
                    self.meas_volt_vg = self.__read_mb.read_analog()
                    calc_delta_percent_vg = 0.00004762 * self.meas_volt_vg ** 2 + 9.5648 * self.meas_volt_vg
                    self.list_delta_percent_vg[-1] = f'{calc_delta_percent_vg:.2f}'
                    self.test_setpoint_vg = True
                    self.__mysql_conn.mysql_add_message(f'уставка {self.list_ust_num[k]} '
                                                        f'дельта t: {calc_delta_t_vg:.1f}')
                    self.__mysql_conn.mysql_add_message(f'уставка {self.list_ust_num[k]} '
                                                        f'дельта %: {calc_delta_percent_vg:.2f}')
                else:
                    self.test_setpoint_vg = False
                self.__ctrl_kl.ctrl_relay('KL73', False)
                if my_msg(self.msg_4):
                    pass
                else:
                    return False
                self.__reset.stop_procedure_3()
                if self.test_setpoint_vg is True:
                    k += 1
                    continue
                else:
                    return False
        self.__mysql_conn.mysql_ins_result('исправен', '2')
        if my_msg(self.msg_4):
            pass
        else:
            return False
        in_a1, in_a5 = self.__inputs_a()
        if in_a1 is False and in_a5 is True:
            return True
        elif in_a1 is True:
            self.__mysql_conn.mysql_error(480)
            return False
        elif in_a5 is False:
            self.__mysql_conn.mysql_error(481)
            return False
    
    def __inputs_a(self):
        in_a1 = self.__read_mb.read_discrete(1)
        in_a5 = self.__read_mb.read_discrete(5)
        if in_a1 is None or in_a5 is None:
            raise ModbusConnectException(f'нет связи с контроллером')
        return in_a1, in_a5

    def result_umz(self):
        """

        :return:
        """
        for g1 in range(len(self.list_delta_percent_ab)):
            self.list_result.append((self.list_ust_num[g1], self.list_delta_percent_ab[g1], self.list_delta_t_ab[g1],
                                     self.list_ust_num[g1], self.list_delta_percent_vg[g1], self.list_delta_t_vg[g1]))
        self.__mysql_conn.mysql_umz_result(self.list_result)

    def st_test_umz(self) -> bool:
        """

        :return:
        """
        if self.st_test_10():
            if self.st_test_11():
                if self.st_test_12():
                    if self.st_test_13():
                        if self.st_test_20():
                            return True
        return False


if __name__ == '__main__':
    test_umz = TestUMZ()
    reset_test_umz = ResetRelay()
    mysql_conn_umz = MySQLConnect()
    fault = Bug(True)
    try:
        if test_umz.st_test_umz():
            test_umz.result_umz()
            mysql_conn_umz.mysql_block_good()
            my_msg('Блок исправен', 'green')
        else:
            test_umz.result_umz()
            mysql_conn_umz.mysql_block_bad()
            my_msg('Блок неисправен', 'red')
    except OSError:
        my_msg("ошибка системы", 'red')
    except SystemError:
        my_msg("внутренняя ошибка", 'red')
    except ModbusConnectException as mce:
        fault.debug_msg(mce, 'red')
        my_msg(f'{mce}', 'red')
    finally:
        reset_test_umz.reset_all()
        sys.exit()
