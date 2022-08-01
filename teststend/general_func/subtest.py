#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
    Общие модули для алгоритмов
"""

import logging

from typing import Union
from time import sleep

from .modbus import *
from .procedure import *
from .database import *
from .resistance import Resistor
from .reset import ResetRelay, ResetProtection

__all__ = ["SubtestMTZ5", "SubtestProcAll", "SubtestBDU", "Subtest2in", "SubtestBDU1M", "Subtest4in"]


class SubtestMTZ5:
    """
        Методы используемые в алгоритмах проверки МТЗ-5-2.7, МТЗ-5-2.8, МТЗ-5-4.11
    """

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.reset_relay = ResetRelay()
        self.reset_protect = ResetProtection()
        self.ctrl_kl = CtrlKL()
        self.read_mb = ReadMB()
        self.di_read = DIRead()

        self.delta_t_mtz: Union[float, int] = 0
        self.in_1 = False
        self.in_5 = False

    def subtest_time_calc_mtz(self) -> [float, bool, bool]:
        self.logger.debug("подтест проверки времени срабатывания")
        for stc in range(3):
            self.logger.debug(f"попытка: {stc}")
            self.reset_protect.sbros_zashit_mtz5()
            self.delta_t_mtz = self.ctrl_kl.ctrl_ai_code_v0(110)
            self.in_1, self.in_5 = self.di_read.di_read("in_a1", "in_a5")
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


class SubtestProcAll:

    def __init__(self):
        self.proc = Procedure()
        self.logger = logging.getLogger(__name__)
        self.reset_relay = ResetRelay()
        self.reset_protect = ResetProtection()
        self.ctrl_kl = CtrlKL()
        self.read_mb = ReadMB()
        self.di_read = DIRead()
        self.mysql_conn = MySQLConnect()

    def procedure_1(self, *, test_num: int = 1, subtest_num: float = 1.0, coef_min_volt: float = 0.6,
                    coef_max_volt: float = 1.1):
        """
        1.1. Проверка вероятности наличия короткого замыкания на входе измерительной цепи блока.
        :return: bool
        """
        self.logger.debug("СТАРТ процедуры 1, 2.1, 3.1 - проверка на КЗ")
        self.mysql_conn.mysql_ins_result(f'идёт тест {subtest_num}', f'{test_num}')
        min_volt, max_volt = self.proc.procedure_1_21_31_v1(coef_min=coef_min_volt, coef_max=coef_max_volt)
        self.ctrl_kl.ctrl_relay('KL63', True)
        meas_volt = self.read_mb.read_analog()
        self.logger.debug(f'напряжение после включения KL63:\t{meas_volt:.2f}\tдолжно быть '
                          f'от\t{min_volt:.2f}\tдо\t{max_volt:.2f}')
        self.reset_relay.sbros_kl63_proc_1_21_31()
        if min_volt <= meas_volt <= max_volt:
            return True
        self.mysql_conn.mysql_ins_result('неисправен', f'{test_num}')
        self.mysql_conn.mysql_error(455)
        return False


class SubtestBDU:

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.reset_relay = ResetRelay()
        self.reset_protect = ResetProtection()
        self.ctrl_kl = CtrlKL()
        self.read_mb = ReadMB()
        self.di_read = DIRead()
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
        in_a1, *_ = self.di_read.di_read('in_a1')
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


class Subtest2in:

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.ctrl_kl = CtrlKL()
        self.di_read = DIRead()
        self.resist = Resistor()
        self.mysql_conn = MySQLConnect()

    def subtest_2di(self, *, test_num: int = 1, subtest_num: float = 1.0, err_code_a1: int = 1, err_code_a2: int = 1,
                    position_a1: bool = False, position_a2: bool = False, inp_1: str = 'in_a1',
                    inp_2: str = 'in_a2') -> bool:
        """
        Тест 1. Проверка исходного состояния блока:
        Возвращает True если на входе False
        модуль используется в алгоритмах у которых только один вход in_a1
        общий тест для bdu_4_2, bdu_d4_2, bdu_r_t, bdz, bru_2sr, bu_apsh_m, bur_pmvir, buz_2
        :param test_num:
        :param subtest_num:
        :param err_code_a1:
        :param err_code_a2:
        :param position_a1:
        :param position_a2:
        :param inp_1:
        :param inp_2:
        :return:
        """
        self.logger.debug(f"тест: {test_num}, подтест: {subtest_num}")
        self.mysql_conn.mysql_ins_result(f"идёт тест {subtest_num}", f'{test_num}')
        self.mysql_conn.mysql_add_message(f"идёт тест: {test_num}, подтест: {subtest_num}")
        in_a1, in_a2 = self.di_read.di_read(inp_1, inp_2)
        self.logger.debug(f"состояние входа: {in_a1 = } is {position_a1} and {in_a2 = } is {position_a2}")
        if in_a1 is position_a1 and in_a2 is position_a2:
            self.logger.debug("состояние выхода блока соответствует")
            self.mysql_conn.mysql_ins_result(f"исправен", f'{test_num}')
            self.mysql_conn.mysql_add_message(f"Исправен. тест: {test_num}, подтест: {subtest_num}")
            return True
        else:
            if in_a1 is not position_a1:
                self._subtest_err(err_code_a1)
            elif in_a2 is not position_a2:
                self._subtest_err(err_code_a2)
            self.mysql_conn.mysql_ins_result("неисправен", f'{test_num}')
            self.mysql_conn.mysql_add_message(f"Неисправен. тест: {test_num}, подтест: {subtest_num}")
            return False

    def _subtest_err(self, err_code):
        self.mysql_conn.mysql_error(err_code)
        read_err = self.mysql_conn.read_err(err_code)
        self.mysql_conn.mysql_add_message(read_err)
        self.logger.debug(f'код неисправности {err_code}: {read_err}')

    def subtest_a_bdu(self, **kwargs) -> bool:
        """
        Общий метод для блока БДУ-4-2, БДУ-Д4-2, БДУ-Д.01, БДУ-Р, БДУ-Т, БРУ-2СР, БУ-АПШ.М

        для БДУ-4-2, БДУ-Д4-2, БДУ-Д-0.1 (bdu_4_2)
            err_code : 15 и 16
            resist : 10 Ом
            position : True & True
        для БДУ-Р, БДУ-Т (bdu_r_t)
            err_code : 292 и 293
            position : True & False
            resist : 10 Ом
        для БРУ-2СР (bru_2sr)
            err_code : 61 & 62 - в прямом: 73 & 74 - в обратном
            position : True & False - в прямом: False & True - обратном
            resist : 0
        для БУ-АПШ.М (bu_apsh_m):
            err_code: в прямом 103 & 104, в обратном 113 & 114
            position: в прямом True & False, в обратном False & True
            resist: 10
            timeout: 3

        2.2. Включение блока от кнопки «Пуск»

        :param: test_num, subtest_num, err_code_a1, err_code_a2, position_a1, position_a2, resistance:
        :return: bool:
        """
        test_num: int = kwargs.get("test_num")
        subtest_num: float = kwargs.get("subtest_num")
        err_a1: int = kwargs.get("err_code_a1")
        err_a2: int = kwargs.get("err_code_a2")
        pos_a1: bool = kwargs.get("position_a1")
        pos_a2: bool = kwargs.get("position_a2")
        resist: int = kwargs.get("resistance", 10)
        timeout: int = kwargs.get("timeout", 2)
        self.logger.debug(f"Общий метод, тест: {test_num}, подтест: {subtest_num}")
        self.mysql_conn.mysql_ins_result(f'идёт тест {subtest_num}', f'{test_num}')
        self.mysql_conn.mysql_add_message(f"старт теста: {test_num}, подтест: {subtest_num}")
        self.resist.resist_ohm(255)
        self.resist.resist_ohm(resist)
        sleep(timeout)
        self.ctrl_kl.ctrl_relay('KL12', True)
        self.logger.debug("включен KL12")
        sleep(timeout)
        if self.subtest_2di(test_num=test_num, subtest_num=subtest_num, err_code_a1=err_a1, err_code_a2=err_a2,
                            position_a1=pos_a1, position_a2=pos_a2):
            return True
        return False

    def subtest_b_bdu(self, **kwargs) -> bool:
        """
        Общий метод для блока БДУ-4-2, БДУ-Д4-2, БДУ-Д.01, БДУ-Р, БДУ-Т, БРУ-2СР

        для БДУ-4-2, БДУ-Д4-2, БДУ-Д-0.1 (bdu_4_2)
            err_code : 7 и 8
            position : True & True
        для БДУ-Р, БДУ-Т (bdu_r_t)
            err_code : 294 и 295
            position : True & False
        для БРУ-2СР (bru_2sr)
            err_sode : 63 & 64 - в прямом : 75 и 76 - в обратном
            position : True & False - в прямом : False & True - в обратном
            KL1 : не используется, необходимо передать False

        2.3. Проверка удержания блока во включенном состоянии при подключении Rш пульта управления:

        :param: test_num, subtest_num, err_code_a1, err_code_a2, position_a1, position_a2, resistance:
        :return: bool:
        """
        test_num: int = kwargs.get("test_num")
        subtest_num: float = kwargs.get("subtest_num")
        err_a1: int = kwargs.get("err_code_a1")
        err_a2: int = kwargs.get("err_code_a2")
        pos_a1: bool = kwargs.get("position_a1")
        pos_a2: bool = kwargs.get("position_a2")
        kl1: bool = kwargs.get("kl1", True)
        self.logger.debug(f"Общий метод, тест: {test_num}, подтест: {subtest_num}")
        self.mysql_conn.mysql_ins_result(f'идёт тест {subtest_num}', f'{test_num}')
        self.mysql_conn.mysql_add_message(f"старт теста: {test_num}, подтест: {subtest_num}")
        if kl1 is False:
            pass
        else:
            self.ctrl_kl.ctrl_relay('KL1', True)
        self.ctrl_kl.ctrl_relay('KL25', True)
        self.logger.debug("включены KL1, KL25")
        sleep(2)
        if self.subtest_2di(test_num=test_num, subtest_num=subtest_num, err_code_a1=err_a1, err_code_a2=err_a2,
                            position_a1=pos_a1, position_a2=pos_a2):
            return True
        return False

    def subtest_a_bur(self, *, test_num: int, subtest_num: float, forward: bool = False, back: bool = False) -> bool:
        """
        Подтест алгоритма проверки блока БУР-ПМВИР
        forward = True - проверка вперед
        back = True - проверка назад
        2.2. Включение блока от кнопки «Пуск» режима «Вперёд»
        6.2. Включение блока от кнопки «Пуск» режима «Назад»
        """
        err_code_a1 = 1
        err_code_a2 = 1
        pos_a1 = False
        pos_a2 = False
        if forward is True:
            err_code_a1 = 170
            err_code_a2 = 171
            pos_a1 = True
            pos_a2 = False
        elif back is True:
            err_code_a1 = 182
            err_code_a2 = 183
            pos_a1 = False
            pos_a2 = True
        self.resist.resist_ohm(0)
        sleep(2)
        self.ctrl_kl.ctrl_relay('KL12', True)
        sleep(2)

        if self.subtest_2di(test_num=test_num, subtest_num=subtest_num, err_code_a1=err_code_a1,
                            err_code_a2=err_code_a2, position_a1=pos_a1, position_a2=pos_a2):
            return True
        return False

    def subtest_b_bur(self, *, test_num: int, subtest_num: float, forward: bool = False, back: bool = False) -> bool:
        """
        Подтест алгоритма проверки блока БУР-ПМВИР
        forward = True - проверка вперед
        back = True - проверка назад
        2.3. Проверка удержания блока во включенном состоянии при подключении Rш пульта управления режима «Вперёд»:
        6.3. Проверка удержания блока во включенном состоянии
        при подключении Rш пульта управления режима «Назад»:
        """
        err_code_a1 = 1
        err_code_a2 = 1
        pos_a1 = False
        pos_a2 = False
        if forward is True:
            err_code_a1 = 172
            err_code_a2 = 173
            pos_a1 = True
            pos_a2 = False
        elif back is True:
            err_code_a1 = 184
            err_code_a2 = 185
            pos_a1 = False
            pos_a2 = True
        self.ctrl_kl.ctrl_relay('KL25', True)
        sleep(2)
        if self.subtest_2di(test_num=test_num, subtest_num=subtest_num, err_code_a1=err_code_a1,
                            err_code_a2=err_code_a2, position_a1=pos_a1, position_a2=pos_a2):
            return True
        return False

    def subtest_bru2sr(self, **kwargs) -> bool:
        """
        Общий подтест для алгоритма БРУ-2СР (bru_2sr)
        Тест 10. Блокировка включения блока при снижении сопротивления изоляции
        контролируемого присоединения до уровня предупредительной уставки
            resist = 200
            err_code = 85 & 86
        Тест 11. Блокировка включения блока при снижении сопротивления
        изоляции контролируемого присоединения до уровня аварийной уставки
            resist = 30
            err_code = 87 & 88
        """
        test_num: int = kwargs.get("test_num")
        subtest_num: float = kwargs.get("subtest_num")
        err_a1: int = kwargs.get("err_code_a1", 85)
        err_a2: int = kwargs.get("err_code_a2", 86)
        resist: int = kwargs.get("resistance", 200)
        self.logger.debug("старт подтеста 10 и 11")
        self.mysql_conn.mysql_add_message(f"тест: {test_num}, подтест: {subtest_num}")
        self.mysql_conn.mysql_ins_result(f"идет тест {subtest_num}", f"{test_num}")
        self.resist.resist_kohm(resist)
        self.ctrl_kl.ctrl_relay('KL12', True)
        self.logger.debug("включен KL12")
        in_a1, in_a2 = self.di_read.di_read('in_a1', 'in_a2')
        self.logger.debug(f'положение выходов блока: {in_a1 = } is False, {in_a2 = } is False')
        if in_a1 is False and in_a2 is False:
            self.ctrl_kl.ctrl_relay('KL12', False)
            self.mysql_conn.mysql_ins_result("исправен", f"{test_num}")
            self.mysql_conn.mysql_add_message(f"Исправен. тест: {test_num}, подтест: {subtest_num}")
            return True
        else:
            self.mysql_conn.mysql_ins_result("неисправен", f"{test_num}")
            self.mysql_conn.mysql_add_message(f"Неисправен. тест: {test_num}, подтест: {subtest_num}")
            if in_a1 is True:
                self._subtest_err(err_a1)
            elif in_a2 is True:
                self._subtest_err(err_a2)
            return False


class SubtestBDU1M:

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.ctrl_kl = CtrlKL()
        self.di_read = DIRead()
        self.resist = Resistor()
        self.mysql_conn = MySQLConnect()

    def subtest_inp_a2(self, **kwargs) -> bool:
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
        position = kwargs.get("position")
        self.logger.debug(f"тест: {test_num}, подтест: {subtest_num}")
        self.mysql_conn.mysql_ins_result(f"идёт тест {subtest_num}", f'{test_num}')
        self.mysql_conn.mysql_add_message(f"идёт тест: {test_num}, подтест: {subtest_num}")
        in_a2, *_ = self.di_read.di_read('in_a1')
        self.logger.debug(f"состояние входа: {in_a2 = } is {position}")
        if in_a2 is position:
            self.logger.debug("состояние выхода блока соответствует")
            self.mysql_conn.mysql_ins_result(f"исправен", f'{test_num}')
            self.mysql_conn.mysql_add_message(f"Исправен. тест: {test_num}, подтест: {subtest_num}")
            return True
        else:
            self.mysql_conn.mysql_error(err_code)
            self.mysql_conn.mysql_ins_result("неисправен", f'{test_num}')
            self.mysql_conn.mysql_add_message(f"Несправен. тест: {test_num}, подтест: {subtest_num}")
            read_err = self.mysql_conn.read_err(err_code)
            self.mysql_conn.mysql_add_message(read_err)
            self.logger.debug(f'код неисправности {err_code}: {read_err}')
            return False

    def subtest_a(self, *, test_num: int, subtest_num: float) -> bool:
        """
            2.2. Включение блока от кнопки «Пуск»
        """
        self.mysql_conn.mysql_ins_result(f'идёт тест {subtest_num}', f'{test_num}')
        self.ctrl_kl.ctrl_relay('KL22', True)
        self.ctrl_kl.ctrl_relay('KL1', False)
        self.ctrl_kl.ctrl_relay('KL25', False)
        sleep(1)
        self.resist.resist_ohm(10)
        sleep(1)
        self.ctrl_kl.ctrl_relay('KL12', True)
        sleep(1)
        if self.subtest_inp_a2(test_num=test_num, subtest_num=subtest_num, err_code=203, position=True):
            return True
        return False

    def subtest_b(self, *, test_num: int, subtest_num: float) -> bool:
        """
            2.3. Проверка удержания блока во включенном состоянии при подключении Rш пульта управления:
        """
        self.mysql_conn.mysql_ins_result(f'идёт тест {subtest_num}', f'{test_num}')
        self.ctrl_kl.ctrl_relay('KL1', True)
        self.ctrl_kl.ctrl_relay('KL22', False)
        sleep(1)
        self.ctrl_kl.ctrl_relay('KL25', True)
        sleep(1)
        if self.subtest_inp_a2(test_num=test_num, subtest_num=subtest_num, err_code=205, position=True):
            return True
        return False


class Subtest4in:

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.ctrl_kl = CtrlKL()
        self.di_read = DIRead()
        self.resist = Resistor()
        self.mysql_conn = MySQLConnect()

    def subtest_4di(self, *, test_num: int = 1, subtest_num: float = 1.0,
                    err_code_a: int = 1, err_code_b: int = 1, err_code_c: int = 1, err_code_d: int = 1,
                    position_a: bool = False, position_b: bool = False,
                    position_c: bool = False, position_d: bool = False,
                    inp_a: str = 'in_a0', inp_b: str = 'in_a1', inp_c: str = 'in_a2', inp_d: str = 'in_a3') -> bool:
        """
        Тест 1. Проверка исходного состояния блока:
        Модуль используется в алгоритмах у которых 4 выхода
        общий тест для БДУ-ДР.01 (bdu_dr01)
        :param test_num: номер теста
        :param subtest_num: номер подтеста
        :param err_code_a: код ошибки для 1-го выхода
        :param err_code_b: код ошибки для 2-го выхода
        :param err_code_c: код ошибки для 3-го выхода
        :param err_code_d: код ошибки для 4-го выхода
        :param position_a: положение которое должен занять 1-й выход блока
        :param position_b: положение которое должен занять 2-й выход блока
        :param position_c: положение которое должен занять 3-й выход блока
        :param position_d: положение которое должен занять 4-й выход блока
        :param inp_a: 1-й вход контроллера
        :param inp_b: 2-й вход контроллера
        :param inp_c: 3-й вход контроллера
        :param inp_d: 4-й вход контроллера
        :return:
        """

        self.logger.debug(f"тест: {test_num}, подтест: {subtest_num}")
        self.mysql_conn.mysql_ins_result(f"идёт тест {subtest_num}", f'{test_num}')
        self.mysql_conn.mysql_add_message(f"идёт тест: {test_num}, подтест: {subtest_num}")
        in_a, in_b, in_c, in_d = self.di_read.di_read(inp_a, inp_b, inp_c, inp_d)
        self.logger.debug(f"состояние входа: {in_a = } is {position_a} and {in_b = } is {position_b}"
                          f"and {in_c = } is {position_c} and {in_d = } is {position_d}")
        if in_a is position_a and in_b is position_b and in_c is position_c and in_d is position_d:
            self.logger.debug("состояние выхода блока соответствует")
            self.mysql_conn.mysql_ins_result(f"исправен", f'{test_num}')
            self.mysql_conn.mysql_add_message(f"Исправен. тест: {test_num}, подтест: {subtest_num}")
            return True
        else:
            if in_a is not position_a:
                self._subtest_err(err_code_a)
            elif in_b is not position_b:
                self._subtest_err(err_code_b)
            elif in_c is not position_c:
                self._subtest_err(err_code_c)
            elif in_d is not position_d:
                self._subtest_err(err_code_d)
            self.mysql_conn.mysql_ins_result("неисправен", f'{test_num}')
            self.mysql_conn.mysql_add_message(f"Неисправен. тест: {test_num}, подтест: {subtest_num}")
            return False

    def _subtest_err(self, err_code):
        self.mysql_conn.mysql_error(err_code)
        read_err = self.mysql_conn.read_err(err_code)
        self.mysql_conn.mysql_add_message(read_err)
        self.logger.debug(f'код неисправности {err_code}: {read_err}')

    def subtest_a(self, *, test_num: int = 1, subtest_num: float = 1.0, resistance: int = 10,
                  err_code_a: int = 1, err_code_b: int = 1, err_code_c: int = 1, err_code_d: int = 1,
                  position_a: bool = False, position_b: bool = False,
                  position_c: bool = False, position_d: bool = False,
                  inp_a: str = 'in_a0', inp_b: str = 'in_a1', inp_c: str = 'in_a2', inp_d: str = 'in_a3') -> bool:
        """
        общий подтест для БДУ-ДР.01
        2.2. Включение 1 канала блока от кнопки «Пуск» 1 канала
        # общий подтест для алгоритма БДУ-ДР.01 (bdu_dr01)
            err_code: 1-й канал 224, 225, 226, 227, 2-й канал 252, 253, 254, 255
            position: 1-й канал True & True & False & False, 2-й канал False & False & True & True
        :param resistance: сопротивление
        :param test_num: номер теста
        :param subtest_num: номер подтеста
        :param err_code_a: код ошибки для 1-го выхода
        :param err_code_b: код ошибки для 2-го выхода
        :param err_code_c: код ошибки для 3-го выхода
        :param err_code_d: код ошибки для 4-го выхода
        :param position_a: положение которое должен занять 1-й выход блока
        :param position_b: положение которое должен занять 2-й выход блока
        :param position_c: положение которое должен занять 3-й выход блока
        :param position_d: положение которое должен занять 4-й выход блока
        :param inp_a: 1-й вход контроллера
        :param inp_b: 2-й вход контроллера
        :param inp_c: 3-й вход контроллера
        :param inp_d: 4-й вход контроллера
        :return:
        """
        self.logger.debug(f"старт теста {test_num}, подтест {subtest_num}")
        self.mysql_conn.mysql_ins_result(f'идёт тест {subtest_num}', f'{test_num}')
        self.mysql_conn.mysql_add_message(f"идёт тест: {test_num}, подтест: {subtest_num}")
        self.resist.resist_ohm(255)
        self.resist.resist_ohm(resistance)
        sleep(1)
        self.ctrl_kl.ctrl_relay('KL12', True)
        self.logger.debug("включен KL12")
        sleep(1)
        if self.subtest_4di(test_num=test_num, subtest_num=subtest_num,
                            err_code_a=err_code_a, err_code_b=err_code_b, err_code_c=err_code_c, err_code_d=err_code_d,
                            position_a=position_a, position_b=position_b, position_c=position_c, position_d=position_d,
                            inp_a=inp_a, inp_b=inp_b, inp_c=inp_c, inp_d=inp_d):
            return True
        return False

    def subtest_b(self, *, test_num: int = 1, subtest_num: float = 1.0, relay: str = 'KL1',
                  err_code_a: int = 1, err_code_b: int = 1, err_code_c: int = 1, err_code_d: int = 1,
                  position_a: bool = False, position_b: bool = False,
                  position_c: bool = False, position_d: bool = False,
                  inp_a: str = 'in_a0', inp_b: str = 'in_a1', inp_c: str = 'in_a2', inp_d: str = 'in_a3') -> bool:
        """
        общий подтест для БДУ-ДР.01
        2.3. Проверка удержания 1 канала блока во включенном состоянии
        при подключении Rш пульта управления 1 каналом блока:
        6.3. Проверка удержания 2 канала блока во включенном состоянии
        при подключении Rш пульта управления 2 каналом блока:
        # общий подтест для алгоритма БДУ-ДР.01 (bdu_dr01)
            err_code: 1-й канал 228, 229, 230, 231, 2-й канал 256, 257, 258, 259
            position: 1-й канал True & True & False & False, 2-й канал False & False & True & True
            relay:  1-й канал KL1, 2-й канал KL29
        :param relay: номер реле в формате 'KL1'
        :param test_num: номер теста
        :param subtest_num: номер подтеста
        :param err_code_a: код ошибки для 1-го выхода
        :param err_code_b: код ошибки для 2-го выхода
        :param err_code_c: код ошибки для 3-го выхода
        :param err_code_d: код ошибки для 4-го выхода
        :param position_a: положение которое должен занять 1-й выход блока
        :param position_b: положение которое должен занять 2-й выход блока
        :param position_c: положение которое должен занять 3-й выход блока
        :param position_d: положение которое должен занять 4-й выход блока
        :param inp_a: 1-й вход контроллера
        :param inp_b: 2-й вход контроллера
        :param inp_c: 3-й вход контроллера
        :param inp_d: 4-й вход контроллера
        :return:
        """
        self.logger.debug(f"старт теста {test_num}, подтест {subtest_num}")
        self.mysql_conn.mysql_ins_result(f'идёт тест {subtest_num}', f'{test_num}')
        self.mysql_conn.mysql_add_message(f"идёт тест: {test_num}, подтест: {subtest_num}")
        self.ctrl_kl.ctrl_relay(relay, True)
        self.ctrl_kl.ctrl_relay('KL25', True)
        sleep(1)
        if self.subtest_4di(test_num=test_num, subtest_num=subtest_num,
                            err_code_a=err_code_a, err_code_b=err_code_b, err_code_c=err_code_c, err_code_d=err_code_d,
                            position_a=position_a, position_b=position_b, position_c=position_c, position_d=position_d,
                            inp_a=inp_a, inp_b=inp_b, inp_c=inp_c, inp_d=inp_d):
            return True
        return False