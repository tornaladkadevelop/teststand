#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from time import sleep
from gen_func_tv1 import *
from gen_func_utils import *
from gen_mb_client import *

__all__ = ["Procedure"]


class Procedure(object):
    """
        U2 - это уставка
        U3 - напряжение вычисленное в процедуре 2х
        напряжение измеренное = measured voltage = measured_vol
        напряжение уставки = setpoint voltage  = setpoint_volt
        коэффициент = coef_volt
        # primary winding
        # secondary winding
    """
    perv_obm = PervObmTV1()
    vtor_obm = VtorObmTV1()
    reset = ResetRelay()
    ctrl_kl = CtrlKL()
    read_mb = ReadMB()
    fault = Bug(True)

    coef_volt: float
    setpoint_volt: float
    calc_volt: float

    def start_procedure_1(self) -> bool:
        self.reset.sbros_vtor_obm()
        self.reset.sbros_perv_obm()
        self.ctrl_kl.ctrl_relay('KL62', True)
        sleep(1)
        self.ctrl_kl.ctrl_relay('KL37', True)
        sleep(1)
        in_b0 = self.read_mb.read_discrete(8)
        if in_b0 is False:
            self.fault.debug_msg("процедура 1 пройдена", 3)
            return True
        else:
            self.fault.debug_msg("процедура 1 не пройдена", 1)
            self.ctrl_kl.ctrl_relay('KL62', False)
            self.ctrl_kl.ctrl_relay('KL37', False)
            return False

    def start_procedure_21(self) -> bool:
        """
            Включение контакта первичной обмотки
            :return:
        """
        self.ctrl_kl.ctrl_relay('KL43', True)
        sleep(1)
        if self.__subtest_meas_volt():
            self.fault.debug_msg("процедура 2.1 пройдена", 3)
            return True
        else:
            self.fault.debug_msg("процедура 2.1 не пройдена", 1)
            self.reset.stop_procedure_21()
            return False

    def start_procedure_22(self) -> bool:
        """
            Включение контакта первичной обмотки
            :return:
        """
        self.ctrl_kl.ctrl_relay('KL44', True)
        sleep(1)
        if self.__subtest_meas_volt():
            self.fault.debug_msg("процедура 2.2 пройдена", 3)
            return True
        else:
            self.fault.debug_msg("процедура 2.2 не пройдена", 1)
            self.reset.stop_procedure_22()
            return False

    def start_procedure_23(self, coef_volt: float) -> float:
        """
            Включение контакта первичной обмотки, соответствующей напряжению U3=U2/Кс.
            Где U2 =80В.
            Сочетание контактов берем из файла «(Тор) TV1.xls»
            :param coef_volt:
            :return:
        """
        self.coef_volt = coef_volt
        calc_volt = 80.0 / self.coef_volt
        self.perv_obm.perv_obm_tv1(calc_volt)
        sleep(1)
        if self.__subtest_meas_volt():
            self.fault.debug_msg("процедура 2.3 пройдена", 3)
            return calc_volt
        else:
            self.fault.debug_msg("процедура 2.3 не пройдена", 1)
            self.reset.stop_procedure_2()
            return False

    def start_procedure_24(self, coef_volt: float, setpoint_volt: float):
        """
            Включение контакта первичной обмотки, соответствующей напряжению U3[i]=U2[i]/Кс.
            Где U2[i] = напряжение, соответствующее i-ой уставке Сочетание контактов для напряжения U2[i]
            берем из файла «(Тор) TV1.xls»
            :param coef_volt:
            :param setpoint_volt:
            :return:
        """
        self.coef_volt = coef_volt
        self.setpoint_volt = setpoint_volt
        calc_volt = self.setpoint_volt / self.coef_volt
        self.perv_obm.perv_obm_tv1(calc_volt)
        sleep(1)
        if self.__subtest_meas_volt():
            self.fault.debug_msg("процедура 2.4 пройдена", 3)
            return calc_volt
        else:
            self.fault.debug_msg("процедура 2.4 не пройдена", 1)
            self.reset.stop_procedure_2()
            return False

    def start_procedure_25(self, coef_volt: float, setpoint_volt: float):
        """
            Включение контакта первичной обмотки, соответствующей напряжению U3[i]=1,1*U2[i]/Кс.
            Где U2[i] = напряжение, соответствующее i-ой уставке Сочетание контактов для напряжения U2[i]
            берем из файла «(Тор) TV1.xls»
        """
        self.coef_volt = coef_volt
        self.setpoint_volt = setpoint_volt
        calc_volt = 1.1 * self.setpoint_volt / self.coef_volt
        self.perv_obm.perv_obm_tv1(calc_volt)
        sleep(1)
        if self.__subtest_meas_volt():
            self.fault.debug_msg("процедура 2.5 пройдена", 3)
            return calc_volt
        else:
            self.fault.debug_msg("процедура 2.5 не пройдена", 1)
            self.reset.stop_procedure_2()
            return False

    def start_procedure_26(self, coef_volt: float):
        """
            Включение контакта первичной обмотки, соответствующей напряжению U3=U2/Кс.
            Где U2 =85.6В.
            Сочетание контактов берем из файла «(Тор) TV1.xls»
            :param coef_volt:
            :return:
        """
        self.coef_volt = coef_volt
        calc_volt = 85.6 / self.coef_volt
        self.perv_obm.perv_obm_tv1(calc_volt)
        sleep(1)
        if self.__subtest_meas_volt():
            self.fault.debug_msg("процедура 2.6 пройдена", 3)
            return calc_volt
        else:
            self.fault.debug_msg("процедура 2.6 не пройдена", 1)
            self.reset.stop_procedure_2()
            return False

    def start_procedure_27(self, coef_volt: float):
        """
            Включение контакта первичной обмотки, соответствующей напряжению U3=U2/Кс.
            Где U2 =20В.
            Сочетание контактов берем из файла «(Тор) TV1.xls»
            :param coef_volt:
            :return:
        """
        self.coef_volt = coef_volt
        calc_volt = 20 / self.coef_volt
        self.perv_obm.perv_obm_tv1(calc_volt)
        sleep(1)
        if self.__subtest_meas_volt():
            self.fault.debug_msg("процедура 2.7 пройдена", 3)
            return calc_volt
        else:
            self.fault.debug_msg("процедура 2.7 не пройдена", 1)
            self.reset.stop_procedure_2()
            return False

    def start_procedure_28(self, coef_volt: float, setpoint_volt: float):
        """
            Включение контакта первичной обмотки, соответствующей напряжению U3[i]=1,15*U2[i]/Кс.
            Где U2[i] = напряжение, соответствующее i-ой уставке Сочетание контактов для напряжения U2[i]
            берем из файла «(Тор) TV1.xls»
            :param coef_volt:
            :param setpoint_volt:
            :return:
        """
        self.coef_volt = coef_volt
        self.setpoint_volt = setpoint_volt
        calc_volt = 1.15 * self.setpoint_volt / self.coef_volt
        self.perv_obm.perv_obm_tv1(calc_volt)
        sleep(1)
        if self.__subtest_meas_volt():
            self.fault.debug_msg("процедура 2.8 пройдена", 3)
            return calc_volt
        else:
            self.fault.debug_msg("процедура 2.8 не пройдена", 1)
            self.reset.stop_procedure_2()
            return False

    def start_procedure_29(self, coef_volt: float):
        """
            Включение контакта первичной обмотки, соответствующей напряжению U3=U2/Кс.
            Где U2 =25.2В.
            Сочетание контактов берем из файла «(Тор) TV1.xls»TV1.xls»
            :param coef_volt:
            :return:
        """
        self.coef_volt = coef_volt
        calc_volt = 25.2 / self.coef_volt
        self.perv_obm.perv_obm_tv1(calc_volt)
        sleep(1)
        if self.__subtest_meas_volt():
            self.fault.debug_msg("процедура 2.9 пройдена", 3)
            return calc_volt
        else:
            self.fault.debug_msg("процедура 2.9 не пройдена", 1)
            self.reset.stop_procedure_2()
            return False

    def start_procedure_210(self, coef_volt: float):
        """
            Включение контакта первичной обмотки, соответствующей напряжению U3=U2/Кс.
            Где U2 =8,2В.
            Сочетание контактов берем из файла «(Тор) TV1.xls»TV1.xls»
            :param coef_volt:
            :return:
        """
        self.coef_volt = coef_volt
        calc_volt = 8.2 / self.coef_volt
        self.perv_obm.perv_obm_tv1(calc_volt)
        sleep(1)
        if self.__subtest_meas_volt():
            self.fault.debug_msg("процедура 2.10 пройдена", 3)
            return calc_volt
        else:
            self.fault.debug_msg("процедура 2.10 не пройдена", 1)
            self.reset.stop_procedure_2()
            return False

    def start_procedure_211(self, coef_volt: float):
        """
            Включение контакта первичной обмотки, соответствующей напряжению U3=U2/Кс.
            Где U2 =10,7В.
            Сочетание контактов берем из файла «(Тор) TV1.xls»TV1.xls»
            :param coef_volt:
            :return:
        """
        self.coef_volt = coef_volt
        calc_volt = 10.7 / self.coef_volt
        self.perv_obm.perv_obm_tv1(calc_volt)
        sleep(1)
        if self.__subtest_meas_volt():
            self.fault.debug_msg("процедура 2.11 пройдена", 3)
            return calc_volt
        else:
            self.fault.debug_msg("процедура 2.11 не пройдена", 1)
            self.reset.stop_procedure_2()
            return False

    def start_procedure_212(self, coef_volt: float):
        """
            Включение контакта первичной обмотки, соответствующей напряжению U3=U2/Кс.
            Где U2 =38В.
            Сочетание контактов берем из файла «(Тор) TV1.xls»
        """
        self.coef_volt = coef_volt
        calc_volt = 80.0 / self.coef_volt
        self.perv_obm.perv_obm_tv1(calc_volt)
        sleep(1)
        if self.__subtest_meas_volt():
            self.fault.debug_msg("процедура 2.12 пройдена", 3)
            return calc_volt
        else:
            self.fault.debug_msg("процедура 2.12 не пройдена", 1)
            self.reset.stop_procedure_2()
            return False

    def __subtest_meas_volt(self) -> bool:
        meas_volt = self.read_mb.read_analog()
        self.fault.debug_msg(f'измеренное напряжение в процедуре 2х:\t {meas_volt:.2f}', 2)
        if meas_volt <= 1.0:
            return True
        return False

    def start_procedure_31(self):
        """
            a=1
            Формирование испытательного сигнала
            ~ 5.96В
            KL60 – ВКЛ
        """
        min_volt = 4.768
        max_volt = 7.152
        self.ctrl_kl.ctrl_relay('KL60', True)
        sleep(2)
        meas_volt = self.read_mb.read_analog()
        self.fault.debug_msg(f'процедура 3.1 напряжение:\t {meas_volt:.2f} \tдолжно быть в пределах '
                             f'от\t {min_volt:.2f} \tдо\t {max_volt:.2f}', 2)
        if min_volt <= meas_volt <= max_volt:
            self.fault.debug_msg("процедура 3.1 пройдена", 3)
            return meas_volt
        elif meas_volt < 4.768 or meas_volt > 7.152:
            self.fault.debug_msg("процедура 3.1 не пройдена", 1)
            self.reset.stop_procedure_31()
            return 0

    def start_procedure_32(self):
        """
            a=2	Формирование испытательного сигнала
            ~ 51,54 В
            KL54 – ВКЛ
            AI.0*K=U21 должен быть в диапазоне (0.8…1.2)*51.54
            41.232
            61.848
        """
        self.ctrl_kl.ctrl_relay('KL54', True)
        sleep(2)
        min_volt = 41.232
        max_volt = 61.848
        meas_volt = self.read_mb.read_analog()
        self.fault.debug_msg(f'процедура 3.2 напряжение:\t {meas_volt:.2f} \tдолжно быть в пределах '
                             f'от\t {min_volt:.2f} \tдо\t {max_volt:.2f}', 2)
        if 41.232 <= meas_volt <= 61.848:
            self.fault.debug_msg("процедура 3.2 пройдена", 3)
            coef_volt = meas_volt / 51.54
            return coef_volt
        elif meas_volt < 41.232 or meas_volt > 61.848:
            self.fault.debug_msg("процедура 3.2 не пройдена", 1)
            self.reset.stop_procedure_32()
            return 0

    def start_procedure_33(self, calc_volt: float):
        """
            а=3, a=6, a=7	Включение контакта вторичной обмотки, соответствующей напряжению U3,
            определенному в Процедуре 2:
            KL48…KL59 – ВКЛ
            AI.0*K=U21 должен быть в диапазоне
            (0,9…1.1)*85.6
            77,04
            94,16
        """
        self.calc_volt = calc_volt
        self.vtor_obm.vtor_obm_tv1(self.calc_volt)
        sleep(2)
        min_volt = 77.04
        max_volt = 94.17
        meas_volt = self.read_mb.read_analog()
        self.fault.debug_msg(f'процедура 3.3 напряжение:\t {meas_volt:.2f} \tдолжно быть в пределах '
                             f'от\t {min_volt:.2f} \tдо\t {max_volt:.2f}', 2)
        if 77.04 <= meas_volt <= 94.16:
            self.fault.debug_msg("процедура 3.3 пройдена", 3)
            return True
        elif meas_volt <= 77.03 or meas_volt >= 94.17:
            self.fault.debug_msg("процедура 3.3 не пройдена", 1)
            self.reset.stop_procedure_3()
            return False

    def start_procedure_34(self, calc_volt: float, setpoint_volt: float):
        """
            а=4	Включение контакта вторичной обмотки, соответствующей напряжению U3[i],
            определенному в Процедуре 2: а=4.
            KL48…KL59 – ВКЛ
            Рассчитываем и сравниваем	AI.0*K=U21 должен быть в диапазоне
            (0,9…1.1)* U2[i]
        """
        self.setpoint_volt = setpoint_volt
        self.calc_volt = calc_volt
        self.vtor_obm.vtor_obm_tv1(self.calc_volt)
        sleep(2)
        min_volt = 0.9 * self.setpoint_volt
        max_volt = 1.1 * self.setpoint_volt
        meas_volt = self.read_mb.read_analog()
        self.fault.debug_msg(f'процедура 3.4 напряжение:\t {meas_volt:.2f} \tдолжно быть в пределах '
                             f'от\t {min_volt:.2f} \tдо\t {max_volt:.2f}', 2)
        if 0.9 * self.setpoint_volt <= meas_volt <= 1.1 * self.setpoint_volt:
            self.fault.debug_msg("процедура 3.4 пройдена", 3)
            return True
        else:
            self.fault.debug_msg("процедура 3.4 не пройдена", 1)
            self.reset.stop_procedure_3()
            return False

    def start_procedure_35(self, calc_volt: float, setpoint_volt: float):
        """
            а=5	Включение контакта вторичной обмотки, соответствующей напряжению U3[i],
            определенному в Процедуре 2: а=5.
            KL48…KL59 – ВКЛ
            Рассчитываем и сравниваем	AI.0*K=U21 должен быть в диапазоне
            (0,9…1.1)* 1,1*U2[i]
            0.99
            1.21
        """
        self.calc_volt = calc_volt
        self.setpoint_volt = setpoint_volt
        self.vtor_obm.vtor_obm_tv1(self.calc_volt)
        sleep(2)
        min_volt = 0.99 * self.setpoint_volt
        max_volt = 1.21 * self.setpoint_volt
        meas_volt = self.read_mb.read_analog()
        self.fault.debug_msg(f'процедура 3.5 напряжение:\t {meas_volt:.2f} \tдолжно быть в пределах '
                             f'от\t {min_volt:.2f} \tдо\t {max_volt:.2f}', 2)
        if 0.99 * self.setpoint_volt <= meas_volt <= 1.21 * self.setpoint_volt:
            self.fault.debug_msg("процедура 3.5 пройдена", 3)
            return True
        else:
            self.fault.debug_msg("процедура 3.5 не пройдена", 1)
            self.reset.stop_procedure_3()
            return False

    def start_procedure_36(self, calc_volt: float):
        """
            а=3, a=6, a=7	Включение контакта вторичной обмотки, соответствующей напряжению U3,
            определенному в Процедуре 2: а=3.
            KL48…KL59 – ВКЛ
            Рассчитываем и сравниваем	AI.0*K=U21 должен быть в диапазоне
            (0,9…1.1)*20
            18
            22
        """
        self.calc_volt = calc_volt
        self.vtor_obm.vtor_obm_tv1(self.calc_volt)
        sleep(2)
        min_volt = 18.0
        max_volt = 22.0
        meas_volt = self.read_mb.read_analog()
        self.fault.debug_msg(f'процедура 3.6 напряжение:\t {meas_volt:.2f} \tдолжно быть в пределах '
                             f'от\t {min_volt:.2f} \tдо\t {max_volt:.2f}', 2)
        if 18.0 <= meas_volt <= 22.0:
            self.fault.debug_msg("процедура 3.6 пройдена", 3)
            return True
        else:
            self.fault.debug_msg("процедура 3.6 не пройдена", 1)
            self.reset.stop_procedure_3()
            return False

    def start_procedure_37(self, calc_volt: float):
        """
            а=3, a=6, a=7	Включение контакта вторичной обмотки, соответствующей напряжению U3,
            определенному в Процедуре 2: а=3.
            KL48…KL59 – ВКЛ
            Рассчитываем и сравниваем	AI.0*K=U21 должен быть в диапазоне
            (0,9…1.1)*80
            72
            88
        """
        self.calc_volt = calc_volt
        self.vtor_obm.vtor_obm_tv1(self.calc_volt)
        sleep(2)
        min_volt = 72.0
        max_volt = 88.0
        meas_volt = self.read_mb.read_analog()
        self.fault.debug_msg(f'процедура 3.7 напряжение:\t {meas_volt:.2f} \tдолжно быть в пределах '
                             f'от\t {min_volt:.2f} \tдо\t {max_volt:.2f}', 2)
        if 72.0 <= meas_volt <= 88.0:
            self.fault.debug_msg("процедура 3.7 пройдена", 3)
            return True
        else:
            self.fault.debug_msg("процедура 3.7 не пройдена", 1)
            self.reset.stop_procedure_3()
            return False

    def start_procedure_38(self, calc_volt: float):
        """
            а=3, a=6, a=7	Включение контакта вторичной обмотки, соответствующей напряжению U3,
            определенному в Процедуре 2: а=3.
            KL48…KL59 – ВКЛ
            Рассчитываем и сравниваем	AI.0*K=U21 должен быть в диапазоне
            AI.0*K=U21 должен быть в диапазоне
            (0,9…1.1)*25.2
            22.68 27.72
        """
        self.calc_volt = calc_volt
        self.vtor_obm.vtor_obm_tv1(self.calc_volt)
        sleep(2)
        min_volt = 22.68
        max_volt = 27.72
        meas_volt = self.read_mb.read_analog()
        self.fault.debug_msg(f'процедура 3.8 напряжение:\t {meas_volt:.2f} \tдолжно быть в пределах '
                             f'от\t {min_volt:.2f} \tдо\t {max_volt:.2f}', 2)
        if min_volt <= meas_volt <= max_volt:
            self.fault.debug_msg("процедура 3.8 пройдена", 3)
            return True
        else:
            self.fault.debug_msg("процедура 3.8 не пройдена", 1)
            self.reset.stop_procedure_3()
            return False

    def start_procedure_39(self, calc_volt: float):
        """
            Включение контакта вторичной обмотки, соответствующей напряжению U3,
            определенному в Процедуре 2
            KL48…KL59 – ВКЛ
            Рассчитываем и сравниваем	AI.0*K=U21 должен быть в диапазоне
            AI.0*K=U21 должен быть в диапазоне
            (0,9…1.1)*8.2
            7.38 9.02
        """
        self.calc_volt = calc_volt
        self.vtor_obm.vtor_obm_tv1(self.calc_volt)
        sleep(2)
        min_volt = 7.38
        max_volt = 9.02
        meas_volt = self.read_mb.read_analog()
        self.fault.debug_msg(f'процедура 3.9 напряжение:\t {meas_volt:.2f} \tдолжно быть в пределах '
                             f'от\t {min_volt:.2f} \tдо\t {max_volt:.2f}', 2)
        if min_volt <= meas_volt <= max_volt:
            self.fault.debug_msg("процедура 3.9 пройдена", 3)
            return True
        else:
            self.fault.debug_msg("процедура 3.9 не пройдена", 1)
            self.reset.stop_procedure_3()
            return False

    def start_procedure_310(self, calc_volt: float):
        """
            Включение контакта вторичной обмотки, соответствующей напряжению U3,
            определенному в Процедуре 2
            KL48…KL59 – ВКЛ
            Рассчитываем и сравниваем	AI.0*K=U21 должен быть в диапазоне
            AI.0*K=U21 должен быть в диапазоне
            (0,9…1.1)*10.7
            9.63 11.77
        """
        self.calc_volt = calc_volt
        self.vtor_obm.vtor_obm_tv1(self.calc_volt)
        sleep(2)
        min_volt = 9.63
        max_volt = 11.77
        meas_volt = self.read_mb.read_analog()
        self.fault.debug_msg(f'процедура 3.10 напряжение:\t {meas_volt:.2f} \tдолжно быть в пределах '
                             f'от\t {min_volt:.2f} \tдо\t {max_volt:.2f}', 2)
        if min_volt <= meas_volt <= max_volt:
            self.fault.debug_msg("процедура 3.9 пройдена", 3)
            return True
        else:
            self.fault.debug_msg("процедура 3.9 не пройдена", 1)
            self.reset.stop_procedure_3()
            return False

    def start_procedure_311(self, calc_volt: float, setpoint_volt: float):
        """
            а=4	Включение контакта вторичной обмотки, соответствующей напряжению U3[i],
            определенному в Процедуре 2: а=4.
            KL48…KL59 – ВКЛ
            Рассчитываем и сравниваем	AI.0*K=U21 должен быть в диапазоне
            (0,9…1.1)* U2[i]
        """
        self.setpoint_volt = setpoint_volt
        self.calc_volt = calc_volt
        self.vtor_obm.vtor_obm_tv1(self.calc_volt)
        sleep(2)
        min_volt = 0.85 * self.setpoint_volt
        max_volt = 1.1 * self.setpoint_volt
        meas_volt = self.read_mb.read_analog()
        self.fault.debug_msg(f'процедура 3.11 напряжение:\t {meas_volt:.2f} \tдолжно быть в пределах '
                             f'от\t {min_volt:.2f} \tдо\t {max_volt:.2f}', 2)
        if min_volt <= meas_volt <= max_volt:
            self.fault.debug_msg("процедура 3.4 пройдена", 3)
            return True
        else:
            self.fault.debug_msg("процедура 3.4 не пройдена", 1)
            self.reset.stop_procedure_3()
            return False

    def start_procedure_312(self, calc_volt: float):
        """
            а=12	Включение контакта вторичной обмотки, соответствующей напряжению U3,
            определенному в Процедуре 2: а=12.
            KL48…KL59 – ВКЛ
            Рассчитываем и сравниваем	AI.0*K=U21 должен быть в диапазоне
            (0,9…1.1)* U2
        """
        self.calc_volt = calc_volt
        self.vtor_obm.vtor_obm_tv1(self.calc_volt)
        sleep(2)
        min_volt = 72.0
        max_volt = 88.0
        meas_volt = self.read_mb.read_analog()
        self.fault.debug_msg(f'процедура 3.12 напряжение:\t {meas_volt:.2f} \tдолжно быть в пределах '
                             f'от\t {min_volt:.2f} \tдо\t {max_volt:.2f}', 2)
        if min_volt <= meas_volt <= max_volt:
            self.fault.debug_msg("процедура 3.4 пройдена", 3)
            return True
        else:
            self.fault.debug_msg("процедура 3.4 не пройдена", 1)
            self.reset.stop_procedure_3()
            return False

    def procedure_1_21_31(self):
        """
        1.1. Проверка вероятности наличия короткого замыкания на входе измерительной цепи блока
        :return:
        """
        if self.start_procedure_1():
            if self.start_procedure_21():
                meas_volt = self.start_procedure_31()
                if meas_volt != 0:
                    return meas_volt
        return False

    def procedure_1_22_32(self) -> bool:
        """
        1.2. Определение коэффициента Кс отклонения фактического напряжения от номинального
        Процедура 1. Проверка отсутствия вероятности возникновения межвиткового замыкания
            на стороне первичной обмотки TV1
        Процедура 2: a=2. Проверка отсутствия вероятности возникновения межвиткового замыкания
            на стороне вторичной обмотки TV1:
        Процедура 3: a=2. Формирование испытательного сигнала для определения поправочного коэффициента сети:

        :return:
        """
        if self.start_procedure_1():
            if self.start_procedure_22():
                coef_volt = self.start_procedure_32()
                if coef_volt != 0:
                    self.fault.debug_msg(f'коэффициент сети:\t {coef_volt:.2f}', 2)
                    return coef_volt
        return False

    def procedure_1_24_34(self, coef_volt: float, setpoint_volt: float) -> bool:
        """
            выполняется последовательно процедура 1 --> 2.4 --> 3.4
            :return:
        """
        self.coef_volt = coef_volt
        self.setpoint_volt = setpoint_volt
        if self.start_procedure_1():
            calc_volt = self.start_procedure_24(coef_volt=self.coef_volt, setpoint_volt=self.setpoint_volt)
            if calc_volt is not False:
                if self.start_procedure_34(calc_volt=calc_volt, setpoint_volt=self.setpoint_volt):
                    return True
        return False

    def procedure_1_25_35(self, coef_volt: float, setpoint_volt: float) -> bool:
        """
            выполняется последовательно процедура 1 --> 2.5 --> 3.5
            :return:
        """
        self.coef_volt = coef_volt
        self.setpoint_volt = setpoint_volt
        if self.start_procedure_1():
            calc_volt = self.start_procedure_25(coef_volt=self.coef_volt, setpoint_volt=self.setpoint_volt)
            if calc_volt is not False:
                if self.start_procedure_35(calc_volt=calc_volt, setpoint_volt=self.setpoint_volt):
                    return True
        return False
