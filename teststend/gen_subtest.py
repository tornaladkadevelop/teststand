#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
    Общие модули для алгоритмов
"""

import logging

from typing import Union
from time import sleep

from gen_func_utils import *
from gen_mb_client import *
from gen_func_procedure import *
from gen_mysql_connect import *

__all__ = ["SubtestMTZ5", "SubtestProcAll", "SubtestBDU"]


class SubtestMTZ5(object):
    """
        Методы используемые в алгоритмах проверки МТЗ-5-2.7, МТЗ-5-2.8, МТЗ-5-4.11
    """

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.reset = ResetRelay()
        self.ctrl_kl = CtrlKL()
        self.read_mb = ReadMB()
        self.read_di = ReadDI()

        self.delta_t_mtz: Union[float, int] = 0
        self.in_1 = False
        self.in_5 = False

    def subtest_time_calc_mtz(self) -> [float, bool, bool]:
        self.logger.debug("подтест проверки времени срабатывания")
        for stc in range(3):
            self.logger.debug(f"попытка: {stc}")
            self.reset.sbros_zashit_mtz5()
            self.delta_t_mtz = self.ctrl_kl.ctrl_ai_code_v0(110)
            self.in_1, self.in_5 = self.read_di.inputs_di("in_a1", "in_a5")
            self.logger.debug(f"время срабатывания: {self.delta_t_mtz}, "
                              f"{self.in_1 = } is False, "
                              f"{self.in_5 = } is True")
            if self.delta_t_mtz == 9999:
                stc += 1
                continue
            elif self.delta_t_mtz != 9999 and self.in_1 is False and self.in_5 is True:
                break
            else:
                stc += 1
                continue
        return self.delta_t_mtz, self.in_1, self.in_5


class SubtestProcAll(object):

    def __init__(self):
        self.proc = Procedure()
        self.logger = logging.getLogger(__name__)
        self.reset = ResetRelay()
        self.ctrl_kl = CtrlKL()
        self.read_mb = ReadMB()
        self.read_di = ReadDI()
        self.mysql_conn = MySQLConnect()

    def sub_proc_1(self):
        """
        1.1. Проверка вероятности наличия короткого замыкания на входе измерительной цепи блока.
        :return: bool
        """
        self.logger.debug("тест 1.2")
        self.mysql_conn.mysql_ins_result('идёт тест 1.2', '1')
        meas_volt_ust = self.proc.procedure_1_21_31()
        if meas_volt_ust != 0.0:
            pass
        else:
            self.mysql_conn.mysql_error(433)
            self.mysql_conn.mysql_ins_result('неисправен', '1')
            return False
        self.ctrl_kl.ctrl_relay('KL63', True)
        min_volt = 0.6 * meas_volt_ust
        max_volt = 1.0 * meas_volt_ust
        meas_volt = self.read_mb.read_analog()
        self.logger.debug(f'напряжение после включения KL63:\t{meas_volt:.2f}\tдолжно быть '
                          f'от\t{min_volt:.2f}\tдо\t{max_volt:.2f}')
        if min_volt <= meas_volt <= max_volt:
            pass
        else:
            self.mysql_conn.mysql_ins_result('неисправен', '1')
            self.mysql_conn.mysql_error(455)
            self.reset.sbros_kl63_proc_1_21_31()
            return False
        self.reset.sbros_kl63_proc_1_21_31()
        return True


class SubtestBDU(object):

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.reset = ResetRelay()
        self.ctrl_kl = CtrlKL()
        self.read_mb = ReadMB()
        self.read_di = ReadDI()
        self.resist = Resistor()
        self.mysql_conn = MySQLConnect()

    def subtest_bdu_inp_a1(self, position: bool = False, **kwargs) -> bool:
        """
        Тест 1. Проверка исходного состояния блока:
        Возвращает True если на входе False
        модуль используется в алгоритмах у которых только один вход in_a1
        общий тест для bdu_4_3, bdu_014tp, bdu, bdu_d, bru_2s, bu_pmvir
        :param: test_num: int, subtest_num: float, err_code: int, position: bool
        :return: bool
        """
        test_num = kwargs.get("test_num")
        subtest_num = kwargs.get("subtest_num")
        err_code = kwargs.get("err_code")
        self.logger.debug(f"тест: {test_num}, подтест: {subtest_num}")
        self.mysql_conn.mysql_ins_result(f"идёт тест {subtest_num}", f'{test_num}')
        self.mysql_conn.mysql_add_message(f"идёт тест: {subtest_num}, подтест: {test_num}")
        in_a1, *_ = self.read_di.inputs_di('in_a1')
        self.logger.debug(f"состояние входа: {in_a1 = } is {position}")
        if in_a1 is position:
            self.logger.debug("состояние выхода блока соответствует")
            self.mysql_conn.mysql_ins_result(f"исправен", f'{test_num}')
            self.mysql_conn.mysql_add_message(f"Исправен. тест: {subtest_num}, подтест: {test_num}")
            return True
        else:
            self.mysql_conn.mysql_error(err_code)
            self.mysql_conn.mysql_ins_result("неисправен", f'{test_num}')
            self.mysql_conn.mysql_add_message(f"Несправен. тест: {subtest_num}, подтест: {test_num}")
            read_err = self.mysql_conn.read_err(err_code)
            self.mysql_conn.mysql_add_message(read_err)
            self.logger.debug(f'код неисправности {err_code}: {read_err}')
            return False

    def subtest_a_bdu43_bru2s(self, *, test_num: int, subtest_num: float) -> bool:
        """
        2.2. Включение блока от кнопки «Пуск»
        подтест проверки блока БДУ-4-3
        подтест проверки блока БРУ-2С
        :param subtest_num: float
        :param test_num: int
        :return: bool
        """
        self.logger.debug(f"старт теста: {test_num}, подтест: {subtest_num}")
        self.mysql_conn.mysql_add_message(f"старт теста: {test_num}, подтест: {subtest_num}")
        self.mysql_conn.mysql_ins_result(f"идёт тест {subtest_num}", f'{test_num}')
        self.resist.resist_ohm(0)
        self.ctrl_kl.ctrl_relay('KL12', True)
        self.logger.debug("включение KL12")
        sleep(1)
        if self.subtest_bdu_inp_a1(test_num=test_num, subtest_num=subtest_num, err_code=21, position=True):
            return True
        return False

    def subtest_b_bdu43_d(self, *,  test_num: int, subtest_num: float) -> bool:
        """
            2.3. Проверка удержания блока во включенном состоянии при подключении Rш пульта управления:
            подтест проверки блока БДУ-4-3
            подтест проверки блока БДУ-Д
            :param test_num: int
            :param subtest_num: float
            :return bool:
        """
        self.logger.debug(f"старт теста: {test_num}, подтест: {subtest_num}")
        self.mysql_conn.mysql_add_message(f"старт теста: {test_num}, подтест: {subtest_num}")
        self.mysql_conn.mysql_ins_result(f"идёт тест {subtest_num}", f'{test_num}')
        self.ctrl_kl.ctrl_relay('KL1', True)
        self.ctrl_kl.ctrl_relay('KL25', True)
        self.logger.debug('включение KL1, KL25')
        sleep(1)
        if self.subtest_bdu_inp_a1(test_num=test_num, subtest_num=subtest_num, err_code=22, position=True):
            return True
        return False

    def subtest_a_bdud(self, *, test_num: int, subtest_num: float) -> bool:
        """
        2.2. Включение блока от кнопки «Пуск»
        подтест проверки блока БДУ-Д
        :param test_num: int
        :param subtest_num: float
        :return bool:
        """
        self.logger.debug(f"старт теста: {test_num}, подтест: {subtest_num}")
        self.mysql_conn.mysql_add_message(f"старт теста: {test_num}, подтест: {subtest_num}")
        self.mysql_conn.mysql_ins_result(f"идёт тест {subtest_num}", f'{test_num}')
        self.resist.resist_ohm(15)
        sleep(3)
        self.ctrl_kl.ctrl_relay('KL12', True)
        self.logger.debug(f'включение KL12')
        sleep(3)
        if self.subtest_bdu_inp_a1(test_num=test_num, subtest_num=subtest_num, err_code=21, position=True):
            return True
        return False

    def subtest_a_bdu014tp(self, *, test_num: int, subtest_num: float) -> bool:
        """
        подтест проверки блока БДУ-0,1,4,Т,П
        :param subtest_num:
        :param test_num:
        :return:
        """
        self.logger.debug(f"старт теста: {test_num}, подтест: {subtest_num}")
        self.mysql_conn.mysql_add_message(f"старт теста: {test_num}, подтест: {subtest_num}")
        self.mysql_conn.mysql_ins_result(f'идёт тест {subtest_num}', f'{test_num}')
        self.resist.resist_ohm(255)
        sleep(1)
        self.resist.resist_ohm(10)
        sleep(2)
        self.ctrl_kl.ctrl_relay('KL1', True)
        self.logger.debug(f'включение KL1')
        sleep(1)
        self.ctrl_kl.ctrl_relay('KL12', True)
        self.logger.debug(f'включение KL12')
        sleep(1)
        if self.subtest_bdu_inp_a1(test_num=test_num, subtest_num=subtest_num, err_code=26, position=True):
            return True
        return False

    def subtest_b_bru2s(self, *, test_num: int, subtest_num: float) -> bool:
        """
        2.3. Проверка удержания блока во включенном состоянии при подключении Rш пульта управления:
        подтест проверки блока БРУ-2С
        :param subtest_num: float
        :param test_num: int
        :return: bool
        """
        self.logger.debug(f"старт теста: {test_num}, подтест: {subtest_num}")
        self.mysql_conn.mysql_add_message(f"старт теста: {test_num}, подтест: {subtest_num}")
        self.mysql_conn.mysql_ins_result(f'идёт тест {subtest_num}', f'{test_num}')
        self.ctrl_kl.ctrl_relay('KL25', True)
        self.logger.debug(f'включение KL25')
        if self.subtest_bdu_inp_a1(test_num=test_num, subtest_num=subtest_num, err_code=50, position=True):
            return True
        return False

    def subtest_a_bupmvir(self, *, test_num: int, subtest_num: float) -> bool:
        """
        2.1. Включение блока от кнопки «Пуск» при сопротивлении 10 Ом
        подтест проверки БУ-ПМВИР
        """
        self.logger.debug(f"старт теста: {test_num}, подтест: {subtest_num}")
        self.mysql_conn.mysql_add_message(f"старт теста: {test_num}, подтест: {subtest_num}")
        self.mysql_conn.mysql_ins_result(f'идёт тест {subtest_num}', f'{test_num}')
        self.resist.resist_ohm(10)
        sleep(1)
        self.ctrl_kl.ctrl_relay('KL12', True)
        self.logger.debug(f'включение KL12')
        sleep(3)
        if self.subtest_bdu_inp_a1(test_num=test_num, subtest_num=subtest_num, err_code=91, position=True):
            return True
        return False
