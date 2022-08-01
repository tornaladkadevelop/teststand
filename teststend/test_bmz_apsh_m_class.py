#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Алгоритм проверки

Тип блока	Производитель
БМЗ АПШ.М	Нет производителя
БМЗ АПШ.М	Электроаппарат-Развитие

"""

import sys
import logging

from time import sleep

from general_func.exception import *
from general_func.utils import *
from general_func.database import *
from general_func.modbus import *
from general_func.procedure import *
from general_func.subtest import *
from gui.msgbox_1 import *

__all__ = ["TestBMZAPSHM"]


class TestBMZAPSHM:

    def __init__(self):
        self.proc = Procedure()
        self.reset = ResetRelay()
        self.ctrl_kl = CtrlKL()
        self.read_mb = ReadMB()
        self.mysql_conn = MySQLConnect()
        self.fault = Bug(None)
        self.subtest = Subtest4in()

        self.ust_1: float = 85.6

        self.coef_volt: float = 0.0
        self.health_flag: bool = False
        
        self.msg_1 = "Убедитесь в отсутствии блоков во всех испытательных разъемах. " \
                     "Вставьте блок в соответствующий испытательный разъем»"

        logging.basicConfig(filename="C:\Stend\project_class\log\TestBMZAPShM.log",
                            filemode="w",
                            level=logging.DEBUG,
                            encoding="utf-8",
                            format='[%(asctime)s: %(name)s: %(levelname)s] %(message)s')
        logging.getLogger('mysql').setLevel('DEBUG')
        self.logger = logging.getLogger(__name__)

    def st_test_10(self) -> bool:
        """
        Тест 1. Проверка исходного состояния блока:
        """
        if my_msg(self.msg_1):
            pass
        else:
            return False
        self.logger.debug("тест 1")
        self.ctrl_kl.ctrl_relay('KL21', True)
        self.logger.debug('включен KL21')
        self.reset.sbros_zashit_kl30()
        if self.subtest.subtest_4di(test_num=1, subtest_num=1.0,
                                    err_code_a=347, err_code_b=348, err_code_c=349, err_code_d=350,
                                    position_a=False, position_b=True, position_c=False, position_d=True,
                                    inp_a='in_a1', inp_b='in_a5', inp_c='in_a2', inp_d='in_a6'):
            return True
        return False

    def st_test_11(self) -> bool:
        """
        1.1. Проверка вероятности наличия короткого замыкания на входе измерительной цепи блока
        """
        self.logger.debug("старт теста 1.1")
        min_volt, max_volt = self.proc.procedure_1_21_31_v1(coef_min=0.9)
        self.ctrl_kl.ctrl_relay('KL63', True)
        self.logger.debug('включен KL63')
        sleep(1)
        meas_volt = self.read_mb.read_analog()
        self.logger.debug(f'измеряем напряжение:\t {meas_volt}')
        self.reset.sbros_kl63_proc_1_21_31()
        if min_volt <= meas_volt <= max_volt:
            self.logger.debug("напряжение соответствует")
            return True
        self.logger.debug("напряжение не соответствует")
        self.mysql_conn.mysql_ins_result('неисправен', '1')
        return False

    def st_test_12(self) -> bool:
        """
        1.2. Определение коэффициента Кс отклонения фактического напряжения от номинального
        """
        self.logger.debug("старт теста 1.2")
        self.coef_volt = self.proc.procedure_1_22_32()
        self.reset.stop_procedure_32()
        if self.coef_volt != 0.0:
            self.mysql_conn.mysql_ins_result('исправен', '1')
            return True
        self.mysql_conn.mysql_ins_result('неисправен', '1')
        return False

    def st_test_20(self) -> bool:
        """
        Тест 2. Проверка работы 1 канала блока
        """
        self.logger.debug("старт теста 2.0")
        if self.proc.procedure_x4_to_x5(coef_volt=self.coef_volt, setpoint_volt=self.ust_1):
            return True
        self.mysql_conn.mysql_ins_result('неисправен', '2')
        return False

    def st_test_21(self) -> bool:
        """
        2.1.  Проверка срабатывания блока от сигнала нагрузки:
        """
        self.logger.debug("старт теста 2.1")
        self.ctrl_kl.ctrl_relay('KL63', True)
        self.logger.debug('включен KL63')
        sleep(3)
        self.ctrl_kl.ctrl_relay('KL63', False)
        self.logger.debug('отключен KL63')
        sleep(1)
        if self.subtest.subtest_4di(test_num=2, subtest_num=2.1,
                                    err_code_a=352, err_code_b=353, err_code_c=354, err_code_d=355,
                                    position_a=True, position_b=False, position_c=False, position_d=True,
                                    inp_a='in_a1', inp_b='in_a5', inp_c='in_a2', inp_d='in_a6'):
            self.reset.stop_procedure_3()
            return True
        self.reset.stop_procedure_3()
        return False

    def st_test_22(self) -> bool:
        """
        2.2. Сброс защит после проверки
        """
        self.logger.debug("старт теста 2.2")
        self.reset.sbros_zashit_kl30()
        if self.subtest.subtest_4di(test_num=2, subtest_num=2.2,
                                    err_code_a=356, err_code_b=357, err_code_c=358, err_code_d=359,
                                    position_a=False, position_b=True, position_c=False, position_d=True,
                                    inp_a='in_a1', inp_b='in_a5', inp_c='in_a2', inp_d='in_a6'):
            return True
        return False

    def st_test_30(self) -> bool:
        """
        Тест 3. Проверка работы 2 канала блока
        """
        self.logger.debug("старт теста 3.0")
        self.ctrl_kl.ctrl_relay('KL73', True)
        self.logger.debug('включен KL73')
        if self.proc.procedure_x4_to_x5(coef_volt=self.coef_volt, setpoint_volt=self.ust_1):
            return True
        self.mysql_conn.mysql_ins_result('неисправен', '3')
        return False

    def st_test_31(self) -> bool:
        self.ctrl_kl.ctrl_relay('KL63', True)
        self.logger.debug('включен KL63')
        sleep(3)
        self.ctrl_kl.ctrl_relay('KL63', False)
        self.logger.debug('отключен KL63')
        sleep(1)
        if self.subtest.subtest_4di(test_num=3, subtest_num=3.1,
                                    err_code_a=360, err_code_b=361, err_code_c=362, err_code_d=363,
                                    position_a=False, position_b=True, position_c=True, position_d=False,
                                    inp_a='in_a1', inp_b='in_a5', inp_c='in_a2', inp_d='in_a6'):
            self.reset.stop_procedure_3()
            return True
        self.reset.stop_procedure_3()
        return False

    def st_test_32(self) -> bool:
        """
        3.2. Сброс защит после проверки
        """
        self.logger.debug("старт теста 3.2")
        self.reset.sbros_zashit_kl30()
        sleep(1)
        if self.subtest.subtest_4di(test_num=3, subtest_num=3.2,
                                    err_code_a=364, err_code_b=365, err_code_c=366, err_code_d=367,
                                    position_a=False, position_b=True, position_c=False, position_d=True,
                                    inp_a='in_a1', inp_b='in_a5', inp_c='in_a2', inp_d='in_a6'):
            return True
        return False

    def st_test_bmz_apsh_m(self) -> [bool, bool]:
        if self.st_test_10():
            if self.st_test_11():
                if self.st_test_12():
                    if self.st_test_20():
                        if self.st_test_21():
                            if self.st_test_22():
                                if self.st_test_30():
                                    if self.st_test_31():
                                        if self.st_test_32():
                                            return True, self.health_flag
        return False, self.health_flag


if __name__ == '__main__':
    test_bmz_apsh_m = TestBMZAPSHM()
    reset_test_bmz_apsh_m = ResetRelay()
    mysql_conn_bmz_apsh_m = MySQLConnect()
    try:
        test, health_flag = test_bmz_apsh_m.st_test_bmz_apsh_m()
        if test and not health_flag:
            mysql_conn_bmz_apsh_m.mysql_block_good()
            my_msg('Блок исправен', 'green')
        else:
            mysql_conn_bmz_apsh_m.mysql_block_bad()
            my_msg('Блок неисправен', 'red')
    except OSError:
        my_msg("ошибка системы", 'red')
    except SystemError:
        my_msg("внутренняя ошибка", 'red')
    except ModbusConnectException as mce:
        my_msg(f'{mce}', 'red')
    finally:
        reset_test_bmz_apsh_m.reset_all()
        sys.exit()
