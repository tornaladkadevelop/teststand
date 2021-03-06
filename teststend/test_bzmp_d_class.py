#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Алгоритм проверки

Тип блока	Производитель
БЗМП-Д	ДИГ, ООО

"""

__all__ = ["TestBZMPD"]

import sys

from time import sleep, time

from my_msgbox import *
from gen_func_procedure import *
from gen_func_utils import *
from gen_mb_client import *
from gen_mysql_connect import *


class TestBZMPD(object):

    __proc = Procedure()
    __reset = ResetRelay()
    __resist = Resistor()
    __read_mb = ReadMB()
    __mb_ctrl = CtrlKL()
    __mysql_conn = MySQLConnect()
    __fault = Bug(True)

    ust_1 = 22.6
    ust_2 = 15.0

    coef_volt: float
    timer_test_5: float

    def __init__(self):
        pass
    
    def st_test_10_bzmp_d(self) -> bool:
        """
        Тест 1. Проверка исходного состояния блока:
        """
        self.__mysql_conn.mysql_ins_result('идёт тест 1.1', '1')
        self.__mysql_conn.mysql_ins_result('---', '2')
        self.__mysql_conn.mysql_ins_result('---', '3')
        self.__mysql_conn.mysql_ins_result('---', '4')
        self.__mysql_conn.mysql_ins_result('---', '5')
        msg_1 = "Убедитесь в отсутствии других блоков и подключите блок БЗМП-Д к испытательной панели"
        if my_msg(msg_1):
            return True
        else:
            return False

    def st_test_11_bzmp_d(self) -> bool:
        """
        1.1.	Проверка вероятности наличия короткого замыкания на входе измерительной цепи блока
        """
        meas_volt_ust = self.__proc.procedure_1_21_31()
        if meas_volt_ust is not False:
            pass
        else:
            self.__mysql_conn.mysql_ins_result("неисправен TV1", "1")
            return False
        self.__mb_ctrl.ctrl_relay('KL73', True)
        sleep(5)
        self.__mb_ctrl.ctrl_relay('KL90', True)
        sleep(5)
        self.__mb_ctrl.ctrl_relay('KL63', True)
        min_volt = 0.6 * meas_volt_ust
        max_volt = 1.0 * meas_volt_ust
        meas_volt = self.__read_mb.read_analog()
        self.__fault.debug_msg(f'напряжение после включения KL63\t{meas_volt}\t'
                               f'должно быть от\t{min_volt}\tдо\t{max_volt}', 3)
        if min_volt <= meas_volt <= max_volt:
            pass
        else:
            self.__mysql_conn.mysql_ins_result('неисправен', '1')
            self.__mysql_conn.mysql_error(455)
            self.__reset.sbros_kl63_proc_1_21_31()
            return False
        self.__reset.sbros_kl63_proc_1_21_31()
        return True

    def st_test_12_bzmp_d(self) -> bool:
        """
        1.2. Определение коэффициента Кс отклонения фактического напряжения от номинального
        """
        self.__mysql_conn.mysql_ins_result('идёт тест 1.2', '1')
        self.coef_volt = self.__proc.procedure_1_22_32()
        if self.coef_volt is not False:
            pass
        else:
            self.__reset.stop_procedure_32()
            self.__mysql_conn.mysql_ins_result("неисправен TV1", "1")
            return False
        self.__reset.stop_procedure_32()
        return True

    def st_test_13_bzmp_d(self) -> bool:
        """
        Подача напряжения питания ~50В
        """
        self.__mysql_conn.mysql_ins_result('идёт тест 1.3', '1')
        self.__mb_ctrl.ctrl_relay('KL67', True)
        timer_test_1 = 0
        start_timer_test_1 = time()
        while timer_test_1 <= 120:
            self.__mb_ctrl.ctrl_relay('KL24', True)
            sleep(0.2)
            self.__mb_ctrl.ctrl_relay('KL24', False)
            timer_test_1 = time() - start_timer_test_1
            in_a1, in_a5, in_a6 = self.__inputs_a()
            self.__fault.debug_msg(f'времени прошло\t{timer_test_1:.2f}', 2)
            if in_a1 is True and in_a5 is True and in_a6 is False:
                break
            else:
                continue
        in_a1, in_a5, in_a6 = self.__inputs_a()
        if in_a1 is True and in_a5 is True and in_a6 is False:
            pass
        else:
            self.__fault.debug_msg("тест 1.2 положение выходов не соответствует", 1)
            self.__mysql_conn.mysql_ins_result("неисправен", "1")
            return False
        self.__fault.debug_msg("тест 1.2 положение выходов соответствует", 4)
        self.__mysql_conn.mysql_ins_result("исправен", "1")
        return True

    @staticmethod
    def st_test_20_bzmp_d() -> bool:
        """
        Тест 2. Проверка срабатывания блока при снижении изоляции цепей 36В
        """
        msg_2 = "С помощью кнопок SB1…SB3, расположенных на панели разъемов, установите следующие параметры блока, " \
                "при их наличии в зависимости от исполнения блока:\n" \
                "- Номинальный ток: 160А (все исполнения);- Кратность пускового тока: 7.5 (все исполнения);\n" \
                "- Номинальное рабочее напряжение: 1140В (все исполнения);\n" \
                "- Перекос фаз по току: 0% (все исполнения); - Датчик тока: ДТК-1 (некоторые исполнения);\n" \
                "- Режим работы: пускатель (некоторые исполнения) или БРУ ВКЛ, БКИ ВКЛ (некоторые исполнения)"
        msg_3 = "С помощью кнопки SB3 перейдите в главное окно меню блока"
        if my_msg(msg_2):
            if my_msg(msg_3):
                return True
        return False

    def st_test_21_bzmp_d(self) -> bool:
        self.__mysql_conn.mysql_ins_result('идёт тест 2.1', '2')
        self.__mb_ctrl.ctrl_relay('KL21', True)
        sleep(1)
        self.__mb_ctrl.ctrl_relay('KL84', True)
        sleep(5)
        self.__mb_ctrl.ctrl_relay('KL84', False)
        sleep(0.2)
        in_a6 = self.__inputs_a6()
        if in_a6 is True:
            pass
        else:
            self.__fault.debug_msg("тест 2.1 положение выходов не соответствует", 1)
            self.__mysql_conn.mysql_ins_result("неисправен", "2")
            return False
        self.__fault.debug_msg("тест 2.1 положение выходов соответствует", 4)
        return True

    def st_test_22_bzmp_d(self) -> bool:
        """
        2.2. Сброс защит после проверки
        """
        self.__mysql_conn.mysql_ins_result('идёт тест 2.2', '2')
        self.__mb_ctrl.ctrl_relay('KL24', True)
        sleep(0.3)
        self.__mb_ctrl.ctrl_relay('KL24', False)
        sleep(0.7)
        in_a1, in_a5, in_a6 = self.__inputs_a()
        if in_a1 is True and in_a5 is True and in_a6 is False:
            pass
        else:
            self.__fault.debug_msg("тест 2.2 положение выходов не соответствует", 1)
            self.__mysql_conn.mysql_ins_result("неисправен", "2")
            return False
        self.__mysql_conn.mysql_ins_result("исправен", "2")
        self.__fault.debug_msg("тест 2.2 положение выходов соответствует", 4)
        return True

    def st_test_30_bzmp_d(self) -> bool:
        """
        Тест 3. Проверка срабатывания блока при снижении силовой изоляции
        """
        msg_4 = "С помощью кнопки SB3 перейдите в главное окно меню блока"
        if my_msg(msg_4):
            pass
        else:
            return False
        self.__mysql_conn.mysql_ins_result('идёт тест 3.1', '3')
        self.__resist.resist_kohm(61)
        sleep(2)
        in_a1, in_a5, in_a6 = self.__inputs_a()
        if in_a1 is False and in_a5 is False and in_a6 is True:
            pass
        else:
            self.__fault.debug_msg("тест 3 положение выходов не соответствует", 1)
            self.__mysql_conn.mysql_ins_result("неисправен", "3")
            return False
        self.__fault.debug_msg("тест 3 положение выходов соответствует", 4)
        return True

    def st_test_31_bzmp_d(self) -> bool:
        self.__resist.resist_kohm(590)
        sleep(2)
        self.__mysql_conn.mysql_ins_result('идёт тест 3.2', '3')
        self.__mb_ctrl.ctrl_relay('KL24', True)
        sleep(0.3)
        self.__mb_ctrl.ctrl_relay('KL24', False)
        sleep(0.7)
        in_a1, in_a5, in_a6 = self.__inputs_a()
        if in_a1 is True and in_a5 is True and in_a6 is False:
            pass
        else:
            self.__fault.debug_msg("положение выходов не соответствует", 1)
            self.__mysql_conn.mysql_ins_result("неисправен", "3")
            return False
        self.__fault.debug_msg("тест 3 положение выходов соответствует", 4)
        self.__mysql_conn.mysql_ins_result("исправен", "3")
        return True

    def st_test_40_bzmp_d(self) -> bool:
        """
        Тест 4. Проверка защиты ПМЗ
        """
        msg_5 = "С помощью кнопки SB3 перейдите в главное окно меню блока"
        if my_msg(msg_5):
            pass
        else:
            return False
        self.__mysql_conn.mysql_ins_result('идёт тест 4.1', '4')
        if self.__proc.procedure_1_24_34(coef_volt=self.coef_volt, setpoint_volt=self.ust_1):
            pass
        else:
            self.__mysql_conn.mysql_ins_result("неисправен", "4")
            return False

    def st_test_41_bzmp_d(self) -> bool:
        """
        4.2.  Проверка срабатывания блока от сигнала нагрузки:
        """
        self.__mysql_conn.mysql_ins_result('идёт тест 4.2', '4')
        self.__mb_ctrl.ctrl_relay('KL63', True)
        sleep(0.5)
        self.__mb_ctrl.ctrl_relay('KL63', False)
        in_a1, in_a5, in_a6 = self.__inputs_a()
        if in_a1 is False and in_a5 is False and in_a6 is True:
            pass
        else:
            self.__fault.debug_msg("положение выходов не соответствует", 1)
            self.__mysql_conn.mysql_ins_result("неисправен", "4")
            self.__reset.stop_procedure_3()
            return False
        self.__fault.debug_msg("положение выходов соответствует", 4)
        self.__reset.stop_procedure_3()
        return True

    def st_test_42_bzmp_d(self) -> bool:
        self.__mysql_conn.mysql_ins_result('идёт тест 4.3', '4')
        self.__mb_ctrl.ctrl_relay('KL24', True)
        sleep(0.3)
        self.__mb_ctrl.ctrl_relay('KL24', False)
        sleep(0.7)
        in_a1, in_a5, in_a6 = self.__inputs_a()
        if in_a1 is True and in_a5 is True and in_a6 is False:
            pass
        else:
            self.__fault.debug_msg("положение выходов не соответствует", 1)
            self.__mysql_conn.mysql_ins_result("неисправен", "4")
            return False
        self.__fault.debug_msg("положение выходов соответствует", 4)
        self.__mysql_conn.mysql_ins_result("исправен", "4")
        return True

    def st_test_50_bzmp_d(self) -> bool:
        """
        Тест 5. Проверка защиты от перегрузки
        """
        self.__mysql_conn.mysql_ins_result('идёт тест 5.1', '5')
        if self.__proc.procedure_1_24_34(coef_volt=self.coef_volt, setpoint_volt=self.ust_2):
            pass
        else:
            self.__mysql_conn.mysql_ins_result("неисправен TV1", "4")
            return False
        return True

    def st_test_51_bzmp_d(self) -> bool:
        """
        5.2.  Проверка срабатывания блока от сигнала нагрузки:
        """
        self.__mysql_conn.mysql_ins_result('идёт тест 5.2', '5')
        self.__mb_ctrl.ctrl_relay('KL63', True)
        in_b1 = self.__inputs_b()
        k = 0
        while in_b1 is False and k <= 10:
            in_b1 = self.__inputs_b()
            k += 1
        start_timer_test_5 = time()
        in_a5 = self.__inputs_a5()
        stop_timer = 0
        while in_a5 is True and stop_timer <= 360:
            in_a5 = self.__inputs_a5()
            sleep(0.2)
            stop_timer_test_5 = time() - start_timer_test_5
            self.__fault.debug_msg(f'таймер тест 5: {stop_timer_test_5}', 2)
        stop_timer_test_5 = time()
        self.timer_test_5 = stop_timer_test_5 - start_timer_test_5
        self.__fault.debug_msg(f'таймер тест 5: {self.timer_test_5}', 2)
        sleep(2)
        self.__mysql_conn.mysql_ins_result('идёт тест 5.2', '5')
        in_a1, in_a5, in_a6 = self.__inputs_a()
        if in_a1 is False and in_a5 is False and in_a6 is True and self.timer_test_5 <= 360:
            pass
        else:
            self.__fault.debug_msg("положение выходов не соответствует", 1)
            self.__mysql_conn.mysql_ins_result("неисправен", "5")
            self.__reset.sbros_kl63_proc_all()
            return False
        self.__fault.debug_msg("положение выходов соответствует", 4)
        self.__reset.sbros_kl63_proc_all()
        return True

    def st_test_52_bzmp_d(self) -> bool:
        self.__mysql_conn.mysql_ins_result('идёт тест 5.3', '5')
        self.__sbros_zashit()
        in_a1, in_a5, in_a6 = self.__inputs_a()
        if in_a1 is True and in_a5 is True and in_a6 is False:
            pass
        else:
            self.__fault.debug_msg("положение выходов не соответствует", 1)
            self.__mysql_conn.mysql_ins_result("неисправен", "5")
            return False
        self.__fault.debug_msg("положение выходов соответствует", 4)
        self.__mysql_conn.mysql_ins_result(f'исправен, {self.timer_test_5:.1f} сек', "5")
        return True
    
    def __sbros_zashit(self):
        self.__mb_ctrl.ctrl_relay('KL24', True)
        sleep(3)
        self.__mb_ctrl.ctrl_relay('KL24', False)
        sleep(0.7)
    
    def __inputs_a(self):
        in_a1 = self.__read_mb.read_discrete(1)
        in_a5 = self.__read_mb.read_discrete(5)
        in_a6 = self.__read_mb.read_discrete(6)
        if in_a1 is None or in_a5 is None or in_a6 is None:
            raise ModbusConnectException(f'нет связи с контроллером')
        return in_a1, in_a5, in_a6
    
    def __inputs_a5(self):
        in_a5 = self.__read_mb.read_discrete(5)
        if in_a5 is None:
            raise ModbusConnectException(f'нет связи с контроллером')
        return in_a5

    def __inputs_a6(self):
        in_a6 = self.__read_mb.read_discrete(6)
        if in_a6 is None:
            raise ModbusConnectException(f'нет связи с контроллером')
        return in_a6
    
    def __inputs_b(self):
        in_a9 = self.__read_mb.read_discrete(9)
        if in_a9 is None:
            raise ModbusConnectException(f'нет связи с контроллером')
        return in_a9

    def st_test_bzmp_d(self) -> bool:
        if self.st_test_10_bzmp_d():
            if self.st_test_11_bzmp_d():
                if self.st_test_12_bzmp_d():
                    if self.st_test_13_bzmp_d():
                        if self.st_test_20_bzmp_d():
                            if self.st_test_21_bzmp_d():
                                if self.st_test_22_bzmp_d():
                                    if self.st_test_30_bzmp_d():
                                        if self.st_test_31_bzmp_d():
                                            if self.st_test_40_bzmp_d():
                                                if self.st_test_41_bzmp_d():
                                                    if self.st_test_42_bzmp_d():
                                                        if self.st_test_50_bzmp_d():
                                                            if self.st_test_51_bzmp_d():
                                                                if self.st_test_52_bzmp_d():
                                                                    return True
        return False


if __name__ == '__main__':
    test_bzmp_d = TestBZMPD()
    reset_test_bzmp_d = ResetRelay()
    mysql_conn_bzmp_d = MySQLConnect()
    fault = Bug(True)
    try:

        if test_bzmp_d.st_test_bzmp_d():
            mysql_conn_bzmp_d.mysql_block_good()
            my_msg('Блок исправен', '#1E8C1E')
        else:
            mysql_conn_bzmp_d.mysql_block_bad()
            my_msg('Блок неисправен', '#A61E1E')
    except OSError:
        my_msg("ошибка системы", '#A61E1E')
    except SystemError:
        my_msg("внутренняя ошибка", '#A61E1E')
    except ModbusConnectException as mce:
        fault.debug_msg(mce, 1)
        my_msg(str(mce), '#A61E1E')
    finally:
        reset_test_bzmp_d.reset_all()
        sys.exit()
