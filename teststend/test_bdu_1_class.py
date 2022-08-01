#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Алгоритм проверки
Тип блока Производитель
БДУ-1	Без Производителя
БДУ-1	Углеприбор

"""

import sys
import logging

from time import sleep

from general_func.exception import *
from general_func.subtest import *
from general_func.utils import *
from general_func.database import *
from general_func.modbus import *
from general_func.resistance import Resistor
from general_func.reset import ResetRelay
from gui.msgbox_1 import *

__all__ = ["TestBDU1"]


class TestBDU1:

    def __init__(self):
        self.resist = Resistor()
        self.ctrl_kl = CtrlKL()
        self.read_mb = ReadMB()
        self.mysql_conn = MySQLConnect()
        self.fault = Bug(True)

        file_log = logging.FileHandler('C:\Stend\project_class\log\TestBDU1.log')
        console_out = logging.StreamHandler()
        logging.basicConfig(handlers=(file_log, console_out),
                            filemode="w",
                            level=logging.DEBUG,
                            encoding="utf-8",
                            format='[%(asctime)s: %(name)s: %(levelname)s] %(message)s')
        logging.getLogger('mysql').setLevel('WARNING')
        self.logger = logging.getLogger(__name__)

    def st_test_1_bdu_1(self) -> bool:
        """
            Тест 1. Проверка исходного состояния блока
        """
        self.logger.debug("тест 1.0")
        in_a1 = self.inputs_a()
        self.logger.debug(f"{in_a1 = } is False")
        if in_a1 is False:
            pass
        else:
            self.fault.debug_msg(f'{in_a1 = } \tблок неисправен', 'red')
            self.mysql_conn.mysql_ins_result('неисправен', '1')
            return False
        self.mysql_conn.mysql_ins_result('исправен', '1')
        self.fault.debug_msg(f'{in_a1 = } \tтест 1 пройден', 'green')
        return True

    def st_test_20_bdu_1(self) -> bool:
        """
            Тест-2 Проверка включения/отключения блока от кнопки пуск
        """
        self.ctrl_kl.ctrl_relay('KL2', True)
        sleep(3)
        in_a1 = self.inputs_a()
        if in_a1 is False:
            pass
        else:
            self.fault.debug_msg(f'{in_a1=} \tблок неисправен', 'red')
            self.mysql_conn.mysql_ins_result('неисправен', '2')
            return False
        self.fault.debug_msg(f'{in_a1=} \tтест 2.1 пройден', 'green')
        return True

    def st_test_22_bdu_1(self) -> bool:
        """
            Тест-2.2 Проверка канала блока от кнопки "Пуск"
        """
        self.resist.resist_ohm(10)
        sleep(3)
        self.ctrl_kl.ctrl_relay('KL12', True)
        sleep(3)
        in_a1 = self.inputs_a()
        if in_a1 is True:
            pass
        else:
            self.fault.debug_msg(f'{in_a1=} \tТест 2.2 блок неисправен', 'red')
            self.mysql_conn.mysql_ins_result('неисправен', '2')
            return False
        self.fault.debug_msg(f'{in_a1=} \tтест 2.2 пройден', 'green')
        return True

    def st_test_23_bdu_1(self) -> bool:
        """
            Тест 2.3 Выключение канала блока от кнопки «Пуск» при сопротивлении 10 Ом
        """
        sleep(3)
        self.ctrl_kl.ctrl_relay('KL12', False)
        sleep(3)
        in_a1 = self.inputs_a()
        if in_a1 is False:
            pass
        else:
            self.fault.debug_msg(f'{in_a1=} \tТест 2.3 блок неисправен', 'red')
            self.mysql_conn.mysql_ins_result('неисправен', '2')
            return False
        self.fault.debug_msg(f'{in_a1=} \tтест 2.3 пройден', 'green')
        self.mysql_conn.mysql_ins_result('исправен', '2')
        return True

    def st_test_30_bdu_1(self) -> bool:
        # Тест-3. Удержание исполнительного элемента при сопротивлении цепи заземления до 35 Ом
        sleep(3)
        self.ctrl_kl.ctrl_relay('KL12', True)
        sleep(0.5)
        # Отключаем KL5, KL8 для формирования 35 Ом
        self.ctrl_kl.ctrl_relay('KL5', False)
        self.ctrl_kl.ctrl_relay('KL8', False)
        sleep(1)
        in_a1 = self.inputs_a()
        if in_a1 is False:
            pass
        else:
            self.fault.debug_msg(f'{in_a1=} \tТест 3 блок неисправен', 'red')
            self.mysql_conn.mysql_ins_result('неисправен', '3')
            return False
        self.fault.debug_msg(f'{in_a1=} \tтест 3 пройден', 'green')
        self.mysql_conn.mysql_ins_result('исправен', '3')
        return True

    def st_test_40_bdu_1(self) -> bool:
        """
            Тест 4. Отключение исполнительного элемента при сопротивлении цепи заземления свыше 50 Ом
        """
        self.ctrl_kl.ctrl_relay('KL7', False)
        self.ctrl_kl.ctrl_relay('KL9', False)
        self.ctrl_kl.ctrl_relay('KL4', True)
        self.ctrl_kl.ctrl_relay('KL6', True)
        self.ctrl_kl.ctrl_relay('KL10', True)
        sleep(2)
        in_a1 = self.inputs_a()
        if in_a1 is False:
            pass
        else:
            self.fault.debug_msg(f'{in_a1=} \tТест 4 блок неисправен', 'red')
            self.mysql_conn.mysql_ins_result('неисправен', '4')
            return False
        self.fault.debug_msg(f'{in_a1=} \tтест 4 пройден', 'green')
        self.mysql_conn.mysql_ins_result('исправен', '4')
        self.ctrl_kl.ctrl_relay('KL12', True)
        sleep(0.5)
        return True

    def st_test_50_bdu_1(self) -> bool:
        """
            Тест 5. Защита от потери управляемости при замыкании проводов ДУ
        """
        self.resist.resist_ohm(10)
        sleep(1)
        self.ctrl_kl.ctrl_relay('KL12', True)
        sleep(0.5)
        self.ctrl_kl.ctrl_relay('KL11', True)
        sleep(1)
        in_a1 = self.inputs_a()
        if in_a1 is False:
            pass
        else:
            self.fault.debug_msg(f'{in_a1=} \tТест 5 блок неисправен', 'red')
            self.mysql_conn.mysql_ins_result('неисправен', '5')
            return False
        self.fault.debug_msg(f'{in_a1=} \tтест 5 пройден', 'green')
        self.mysql_conn.mysql_ins_result('исправен', '5')
        self.ctrl_kl.ctrl_relay('KL12', False)
        self.ctrl_kl.ctrl_relay('KL11', False)
        self.ctrl_kl.ctrl_relay('KL1', False)
        return True

    def st_test_60_bdu_1(self) -> bool:
        """
            Тест 6. Защита от потери управляемости при обрыве проводов ДУ
        """
        self.resist.resist_ohm(10)
        sleep(1)
        self.ctrl_kl.ctrl_relay('KL12', True)
        sleep(1)
        self.ctrl_kl.ctrl_relay('KL12', False)
        sleep(2)
        in_a1 = self.inputs_a()
        if in_a1 is False:
            pass
        else:
            self.fault.debug_msg(f'{in_a1=} \tТест 6 блок неисправен', 'red')
            self.mysql_conn.mysql_ins_result('неисправен', '6')
            return False
        self.fault.debug_msg(f'{in_a1=} \tтест 6 пройден', 'green')
        self.mysql_conn.mysql_ins_result('исправен', '6')
        self.fault.debug_msg(f'{in_a1=} \tтест завершен', 'blue')
        return True
    
    # def __inputs_a(self) -> bool:
    #     in_a1 = self.read_mb.read_discrete(1)
    #     if in_a1 is None:
    #         raise ModbusConnectException(f'нет связи с контроллером')
    #     return in_a1

    def st_test_bdu_1(self) -> bool:
        """
            главная функция которая собирает все остальные
        """
        if self.st_test_1_bdu_1():
            if self.st_test_20_bdu_1():
                if self.st_test_22_bdu_1():
                    if self.st_test_23_bdu_1():
                        if self.st_test_23_bdu_1():
                            if self.st_test_30_bdu_1():
                                if self.st_test_40_bdu_1():
                                    if self.st_test_50_bdu_1():
                                        if self.st_test_60_bdu_1():
                                            return True
        return False


if __name__ == '__main__':
    test_bdu_1 = TestBDU1()
    reset_test_bdu_1 = ResetRelay()
    mysql_conn_bdu_1 = MySQLConnect()
    fault = Bug(True)
    try:
        if test_bdu_1.st_test_bdu_1():
            mysql_conn_bdu_1.mysql_block_good()
            my_msg('Блок исправен', 'green')
        else:
            mysql_conn_bdu_1.mysql_block_bad()
            my_msg('Блок неисправен', 'red')
    except OSError:
        fault.debug_msg("ошибка системы", 'red')
    except SystemError:
        fault.debug_msg("внутренняя ошибка", 'red')
    except ModbusConnectException as mce:
        fault.debug_msg(mce, 'red')
        my_msg(f'{mce}', 'red')
    finally:
        reset_test_bdu_1.reset_all()
        sys.exit()
