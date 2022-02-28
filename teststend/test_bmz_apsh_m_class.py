#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Алгоритм проверки

Тип блока	Производитель
БМЗ АПШ.М	Нет производителя
БМЗ АПШ.М	Электроаппарат-Развитие

"""

from sys import exit
from time import sleep

from gen_func_procedure import *
from gen_func_utils import *
from my_msgbox import *
from gen_mb_client import *
from gen_mysql_connect import *

__all__ = ["TestBMZAPSHM"]


class TestBMZAPSHM(object):

    __proc = Procedure()
    __reset = ResetRelay()
    __ctrl_kl = CtrlKL()
    __read_mb = ReadMB()
    __mysql_conn = MySQLConnect()
    __fault = Bug(True)

    coef_volt: float

    def __init__(self):
        pass
    
    def st_test_10_bmz_apsh_m(self) -> bool:
        """
        Тест 1. Проверка исходного состояния блока:
        """
        msg_1 = "Убедитесь в отсутствии блоков во всех испытательных разъемах. " \
                "Вставьте блок в соответствующий испытательный разъем»"
        if my_msg(msg_1):
            pass
        else:
            return False
        self.__fault.debug_msg("тест 1", 4)
        self.__ctrl_kl.ctrl_relay('KL21', True)
        self.__reset.sbros_zashit_kl30()
        in_a1, in_a2, in_a5, in_a6 = self.__inputs_a()
        if in_a1 is False and in_a5 is True and in_a2 is False and in_a6 is True:
            pass
        else:
            self.__mysql_conn.mysql_ins_result('неисправен', '1')
            if in_a1 is True:
                self.__fault.debug_msg("вход 1 не соответствует", 1)
                self.__mysql_conn.mysql_error(347)
            elif in_a5 is False:
                self.__fault.debug_msg("вход 5 не соответствует", 1)
                self.__mysql_conn.mysql_error(348)
            elif in_a2 is True:
                self.__fault.debug_msg("вход 2 не соответствует", 1)
                self.__mysql_conn.mysql_error(349)
            elif in_a6 is False:
                self.__fault.debug_msg("вход 6 не соответствует", 1)
                self.__mysql_conn.mysql_error(350)
            return False
        self.__fault.debug_msg("состояние выходов соответствует", 3)
        return True

    def st_test_11_bmz_apsh_m(self) -> bool:
        """
        1.1. Проверка вероятности наличия короткого замыкания на входе измерительной цепи блока
        """
        self.__fault.debug_msg("тест 1.1", 4)
        meas_volt_ust = self.__proc.procedure_1_21_31()
        if meas_volt_ust is not False:
            pass
        else:
            self.__mysql_conn.mysql_ins_result('неисправен', '1')
            return False
        self.__fault.debug_msg("тест 1.1.2", 4)
        self.__ctrl_kl.ctrl_relay('KL63', True)
        meas_volt = self.__read_mb.read_analog()
        self.__fault.debug_msg(f'измеряем напряжение:\t {meas_volt}', 4)
        if 0.9 * meas_volt_ust <= meas_volt <= 1.1 * meas_volt_ust:
            pass
        else:
            self.__fault.debug_msg("напряжение не соответствует", 1)
            self.__mysql_conn.mysql_ins_result('неисправен', '1')
            self.__reset.sbros_kl63_proc_1_21_31()
            return False
        self.__fault.debug_msg("напряжение соответствует", 3)
        self.__fault.debug_msg("тест 1.1.3", 4)
        self.__reset.sbros_kl63_proc_1_21_31()
        return True

    def st_test_12_bmz_apsh_m(self) -> bool:
        """
        1.2. Определение коэффициента Кс отклонения фактического напряжения от номинального
        """
        self.__fault.debug_msg("тест 1.2", 4)
        coef_volt = self.__proc.procedure_1_22_32()
        if coef_volt is not False:
            pass
        else:
            self.__mysql_conn.mysql_ins_result('неисправен', '1')
            return False
        self.__fault.debug_msg(f'вычисляем коэффициент сети:\t {coef_volt}', 4)
        self.__reset.stop_procedure_32()
        self.__mysql_conn.mysql_ins_result('исправен', '1')
        self.__fault.debug_msg("тест 1 завершен", 3)
        self.__fault.debug_msg("тест 2", 4)
        return True

    def st_test_20_bmz_apsh_m(self) -> bool:
        """
        Тест 2. Проверка работы 1 канала блока
        """

        if self.__proc.start_procedure_1():
            calc_volt = self.__proc.start_procedure_26(self.coef_volt)
            if calc_volt is not False:
                if self.__proc.start_procedure_33(calc_volt):
                    pass
                else:
                    self.__mysql_conn.mysql_ins_result('неисправен', '2')
                    return False
            else:
                self.__mysql_conn.mysql_ins_result('неисправен', '2')
                return False
        else:
            self.__mysql_conn.mysql_ins_result('неисправен', '2')
            return False

    def st_test_21_bmz_apsh_m(self) -> bool:
        """
        2.1.  Проверка срабатывания блока от сигнала нагрузки:
        """
        self.__fault.debug_msg("тест 2.1", 4)
        self.__ctrl_kl.ctrl_relay('KL63', True)
        sleep(3)
        self.__ctrl_kl.ctrl_relay('KL63', False)
        sleep(1)
        in_a1, in_a2, in_a5, in_a6 = self.__inputs_a()
        if in_a1 is True and in_a5 is False and in_a2 is False and in_a6 is True:
            pass
        else:
            self.__mysql_conn.mysql_ins_result('неисправен', '2')
            if in_a1 is False:
                self.__fault.debug_msg("вход 1 не соответствует", 1)
                self.__mysql_conn.mysql_error(352)
            elif in_a5 is True:
                self.__fault.debug_msg("вход 5 не соответствует", 1)
                self.__mysql_conn.mysql_error(353)
            elif in_a2 is True:
                self.__fault.debug_msg("вход 2 не соответствует", 1)
                self.__mysql_conn.mysql_error(354)
            elif in_a6 is False:
                self.__fault.debug_msg("вход 6 не соответствует", 1)
                self.__mysql_conn.mysql_error(355)
            return False
        self.__fault.debug_msg("выходы блока соответствуют", 3)
        self.__reset.stop_procedure_3()
        return True

    def st_test_22_bmz_apsh_m(self) -> bool:
        """
        2.2. Сброс защит после проверки
        """
        self.__fault.debug_msg("тест 2.2", 4)
        self.__reset.sbros_zashit_kl30()
        in_a1, in_a2, in_a5, in_a6 = self.__inputs_a()
        if in_a1 is False and in_a5 is True and in_a2 is False and in_a6 is True:
            pass
        else:
            self.__mysql_conn.mysql_ins_result('неисправен', '2')
            if in_a1 is True:
                self.__fault.debug_msg("вход 1 не соответствует", 1)
                self.__mysql_conn.mysql_error(356)
            elif in_a5 is False:
                self.__fault.debug_msg("вход 5 не соответствует", 1)
                self.__mysql_conn.mysql_error(357)
            elif in_a2 is True:
                self.__fault.debug_msg("вход 2 не соответствует", 1)
                self.__mysql_conn.mysql_error(358)
            elif in_a6 is False:
                self.__fault.debug_msg("вход 6 не соответствует", 1)
                self.__mysql_conn.mysql_error(359)
            return False
        self.__fault.debug_msg("выхода блока соответствуют", 3)
        self.__mysql_conn.mysql_ins_result('исправен', '2')
        self.__fault.debug_msg("тест 2 пройден", 3)
        return True

    def st_test_30_bmz_apsh_m(self) -> bool:
        """
        Тест 3. Проверка работы 2 канала блока
        """
        self.__fault.debug_msg("тест 3", 4)
        self.__ctrl_kl.ctrl_relay('KL73', True)
        if self.__proc.start_procedure_1():
            calc_volt = self.__proc.start_procedure_26(self.coef_volt)
            if calc_volt is not False:
                if self.__proc.start_procedure_33(calc_volt):
                    pass
                else:
                    self.__mysql_conn.mysql_ins_result('неисправен', '3')
                    return False
            else:
                self.__mysql_conn.mysql_ins_result('неисправен', '3')
                return False
        else:
            self.__mysql_conn.mysql_ins_result('неисправен', '3')
            return False

    def st_test_31_bmz_apsh_m(self) -> bool:
        self.__ctrl_kl.ctrl_relay('KL63', True)
        sleep(3)
        self.__ctrl_kl.ctrl_relay('KL63', False)
        sleep(1)
        in_a1, in_a2, in_a5, in_a6 = self.__inputs_a()
        if in_a1 is False and in_a5 is True and in_a2 is True and in_a6 is False:
            pass
        else:
            self.__mysql_conn.mysql_ins_result('неисправен', '3')
            if in_a1 is True:
                self.__fault.debug_msg("вход 1 не соответствует", 1)
                self.__mysql_conn.mysql_error(360)
            elif in_a5 is False:
                self.__fault.debug_msg("вход 5 не соответствует", 1)
                self.__mysql_conn.mysql_error(361)
            elif in_a2 is False:
                self.__fault.debug_msg("вход 2 не соответствует", 1)
                self.__mysql_conn.mysql_error(362)
            elif in_a6 is True:
                self.__fault.debug_msg("вход 6 не соответствует", 1)
                self.__mysql_conn.mysql_error(363)
            return False
        self.__fault.debug_msg("состояние выходов соответствует", 3)
        self.__reset.stop_procedure_3()
        return True

    def st_test_32_bmz_apsh_m(self) -> bool:
        """
        3.2. Сброс защит после проверки
        """
        self.__fault.debug_msg("тест 3.2", 4)
        self.__reset.sbros_zashit_kl30()
        sleep(1)
        in_a1, in_a2, in_a5, in_a6 = self.__inputs_a()
        if in_a1 is False and in_a5 is True and in_a2 is False and in_a6 is True:
            pass
        else:
            self.__mysql_conn.mysql_ins_result('неисправен', '3')
            if in_a1 is True:
                self.__fault.debug_msg("вход 1 не соответствует", 1)
                self.__mysql_conn.mysql_error(364)
            elif in_a5 is False:
                self.__fault.debug_msg("вход 5 не соответствует", 1)
                self.__mysql_conn.mysql_error(365)
            elif in_a2 is False:
                self.__fault.debug_msg("вход 2 не соответствует", 1)
                self.__mysql_conn.mysql_error(366)
            elif in_a6 is True:
                self.__fault.debug_msg("вход 6 не соответствует", 1)
                self.__mysql_conn.mysql_error(367)
            return False
        self.__fault.debug_msg("состояние выходов блока соответсвует", 3)
        self.__mysql_conn.mysql_ins_result('исправен', '3')
        return True
    
    def __inputs_a(self):
        in_a1 = self.__read_mb.read_discrete(1)
        in_a2 = self.__read_mb.read_discrete(2)
        in_a5 = self.__read_mb.read_discrete(5)
        in_a6 = self.__read_mb.read_discrete(6)
        if in_a1 is None or in_a2 is None or in_a5 is None or in_a6 is None:
            raise ModbusConnectException(f'нет связи с контроллером')
        return in_a1, in_a2, in_a5, in_a6

    def st_test_bmz_apsh_m(self) -> bool:
        if self.st_test_10_bmz_apsh_m():
            if self.st_test_11_bmz_apsh_m():
                if self.st_test_12_bmz_apsh_m():
                    if self.st_test_20_bmz_apsh_m():
                        if self.st_test_21_bmz_apsh_m():
                            if self.st_test_22_bmz_apsh_m():
                                if self.st_test_30_bmz_apsh_m():
                                    if self.st_test_31_bmz_apsh_m():
                                        if self.st_test_32_bmz_apsh_m():
                                            return True
        return False


if __name__ == '__main__':
    test_bmz_apsh_m = TestBMZAPSHM()
    reset_test_bmz_apsh_m = ResetRelay()
    mysql_conn_bmz_apsh_m = MySQLConnect()
    fault = Bug(True)
    try:
        test_bmz_apsh_m = TestBMZAPSHM()
        if test_bmz_apsh_m.st_test_bmz_apsh_m():
            mysql_conn_bmz_apsh_m.mysql_block_good()
            my_msg('Блок исправен')
        else:
            mysql_conn_bmz_apsh_m.mysql_block_bad()
            my_msg('Блок неисправен', '#A61E1E')
    except OSError:
        my_msg("ошибка системы")
    except SystemError:
        my_msg("внутренняя ошибка")
    except ModbusConnectException as mce:
        fault.debug_msg(mce, 1)
        my_msg(str(mce), '#A61E1E')
    finally:
        reset_test_bmz_apsh_m.reset_all()
        exit()
