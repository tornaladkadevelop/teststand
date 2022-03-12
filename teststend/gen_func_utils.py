#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import ctypes
from time import time, sleep
from my_msgbox import *
from gen_mb_client import *

__all__ = ["Bug", "ResetRelay", "Resistor", "DeltaTimeNoneKL63", "ModbusConnectException", "ResultMsg"]

kernel32 = ctypes.windll.kernel32
kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
ctrl_kl = CtrlKL()
read_mb = ReadMB()


class DeltaTimeNoneKL63(object):
    """
        расчет дельты времени переключения выходов блока
        Сброс или запоминание состояние таймера текущего времени CPU T0[i], сек
        KL63 - ВКЛ	DQ5:1B - ВКЛ
        Запуск таймера происходит по условию замыкания DI.b1 (контакт реле KL63)
        Остановка таймера происходит по условию размыкания DI.a6 T1[i]

    """

    def calc_dt(self):
        ctrl_kl.ctrl_relay('KL63', True)
        in_b1 = self.__inputs_b1()
        while in_b1 is False:
            in_b1 = self.__inputs_b1()
        start_timer = time()
        in_ax = self.__inputs_a6()
        while in_ax is True:
            in_ax = self.__inputs_a6()
        stop_timer = time()
        delta_t_calc = stop_timer - start_timer
        return delta_t_calc

    @staticmethod
    def __inputs_a6():
        in_a6 = read_mb.read_discrete(6)
        return in_a6

    @staticmethod
    def __inputs_b1():
        in_b1 = read_mb.read_discrete(9)
        return in_b1


class Bug(object):
    """
        вывод сообщений в консоль
    """
    def __init__(self, dbg=None):
        self.dbg = dbg

    def debug_msg(self, msg, lev):
        if self.dbg is True:
            if lev == 1:
                # красный
                print("\033[31m {}".format(msg))
            elif lev == 2:
                # желтый
                print("\033[33m {}".format(msg))
            elif lev == 3:
                # голубой
                print("\033[36m {}".format(msg))
            elif lev == 4:
                # зеленый
                print("\033[32m {}".format(msg))
            elif lev == 5:
                # фиолетовый
                print("\033[35m {}".format(msg))
        else:
            pass


class ResetRelay(object):
    """
        сбросы реле в различных вариациях в зависимости от алгоритма
    """

    @staticmethod
    def sbros_zashit_kl1():
        ctrl_kl.ctrl_relay('KL1', True)
        sleep(1.5)
        ctrl_kl.ctrl_relay('KL1', False)
        sleep(2)

    @staticmethod
    def sbros_zashit_kl30():
        ctrl_kl.ctrl_relay('KL30', True)
        sleep(0.5)
        ctrl_kl.ctrl_relay('KL30', False)
        sleep(0.5)

    @staticmethod
    def sbros_zashit_kl30_1s5():
        ctrl_kl.ctrl_relay('KL30', True)
        sleep(1.5)
        ctrl_kl.ctrl_relay('KL30', False)
        sleep(2.0)

    def reset_all(self):
        ctrl_kl.ctrl_relay('KL1', False)
        ctrl_kl.ctrl_relay('KL2', False)
        ctrl_kl.ctrl_relay('KL3', False)
        ctrl_kl.ctrl_relay('KL4', False)
        ctrl_kl.ctrl_relay('KL5', False)
        ctrl_kl.ctrl_relay('KL6', False)
        ctrl_kl.ctrl_relay('KL7', False)
        ctrl_kl.ctrl_relay('KL8', False)
        ctrl_kl.ctrl_relay('KL9', False)
        ctrl_kl.ctrl_relay('KL10', False)
        ctrl_kl.ctrl_relay('KL11', False)
        ctrl_kl.ctrl_relay('KL12', False)
        ctrl_kl.ctrl_relay('KL13', False)
        ctrl_kl.ctrl_relay('KL14', False)
        ctrl_kl.ctrl_relay('KL15', False)
        ctrl_kl.ctrl_relay('KL16', False)
        ctrl_kl.ctrl_relay('KL17', False)
        ctrl_kl.ctrl_relay('KL18', False)
        ctrl_kl.ctrl_relay('KL19', False)
        ctrl_kl.ctrl_relay('KL20', False)
        ctrl_kl.ctrl_relay('KL21', False)
        ctrl_kl.ctrl_relay('KL22', False)
        ctrl_kl.ctrl_relay('KL23', False)
        ctrl_kl.ctrl_relay('KL24', False)
        ctrl_kl.ctrl_relay('KL25', False)
        ctrl_kl.ctrl_relay('KL26', False)
        ctrl_kl.ctrl_relay('KL27', False)
        ctrl_kl.ctrl_relay('KL28', False)
        ctrl_kl.ctrl_relay('KL29', False)
        ctrl_kl.ctrl_relay('KL30', False)
        ctrl_kl.ctrl_relay('KL31', False)
        ctrl_kl.ctrl_relay('KL32', False)
        ctrl_kl.ctrl_relay('KL33', False)
        # #
        ctrl_kl.ctrl_relay('KL36', False)
        ctrl_kl.ctrl_relay('KL37', False)
        self.sbros_perv_obm()
        self.sbros_vtor_obm()
        ctrl_kl.ctrl_relay('KL60', False)
        # #
        ctrl_kl.ctrl_relay('KL62', False)
        ctrl_kl.ctrl_relay('KL63', False)
        ctrl_kl.ctrl_relay('KL65', False)
        ctrl_kl.ctrl_relay('KL66', False)
        ctrl_kl.ctrl_relay('KL67', False)
        ctrl_kl.ctrl_relay('KL68', False)
        ctrl_kl.ctrl_relay('KL69', False)
        # #
        ctrl_kl.ctrl_relay('KL70', False)
        ctrl_kl.ctrl_relay('KL71', False)
        ctrl_kl.ctrl_relay('KL72', False)
        ctrl_kl.ctrl_relay('KL73', False)
        ctrl_kl.ctrl_relay('KL74', False)
        ctrl_kl.ctrl_relay('KL75', False)
        ctrl_kl.ctrl_relay('KL76', False)
        ctrl_kl.ctrl_relay('KL77', False)
        ctrl_kl.ctrl_relay('KL78', False)
        ctrl_kl.ctrl_relay('KL79', False)
        ctrl_kl.ctrl_relay('KL80', False)
        ctrl_kl.ctrl_relay('KL81', False)
        ctrl_kl.ctrl_relay('KL82', False)
        ctrl_kl.ctrl_relay('KL83', False)
        ctrl_kl.ctrl_relay('KL84', False)
        ctrl_kl.ctrl_relay('KL88', False)
        ctrl_kl.ctrl_relay('KL89', False)
        ctrl_kl.ctrl_relay('KL90', False)
        ctrl_kl.ctrl_relay('KL91', False)
        ctrl_kl.ctrl_relay('KL92', False)
        ctrl_kl.ctrl_relay('KL93', False)
        ctrl_kl.ctrl_relay('KL94', False)
        ctrl_kl.ctrl_relay('KL95', False)
        ctrl_kl.ctrl_relay('KL97', False)
        ctrl_kl.ctrl_relay('KL98', False)
        ctrl_kl.ctrl_relay('KL99', False)
        ctrl_kl.ctrl_relay('KL100', False)
        ctrl_kl.ctrl_relay('Q113_4', False)
        ctrl_kl.ctrl_relay('Q113_5', False)
        ctrl_kl.ctrl_relay('Q113_6', False)
        ctrl_kl.ctrl_relay('Q113_7', False)
        
    @staticmethod
    def sbros_perv_obm():
        ctrl_kl.ctrl_relay('KL38', False)
        ctrl_kl.ctrl_relay('KL39', False)
        ctrl_kl.ctrl_relay('KL40', False)
        ctrl_kl.ctrl_relay('KL41', False)
        ctrl_kl.ctrl_relay('KL42', False)
        ctrl_kl.ctrl_relay('KL43', False)
        ctrl_kl.ctrl_relay('KL44', False)
        ctrl_kl.ctrl_relay('KL45', False)
        ctrl_kl.ctrl_relay('KL46', False)
        ctrl_kl.ctrl_relay('KL47', False)
        
    @staticmethod
    def sbros_vtor_obm():
        ctrl_kl.ctrl_relay('KL48', False)
        ctrl_kl.ctrl_relay('KL49', False)
        ctrl_kl.ctrl_relay('KL50', False)
        ctrl_kl.ctrl_relay('KL51', False)
        ctrl_kl.ctrl_relay('KL52', False)
        ctrl_kl.ctrl_relay('KL53', False)
        ctrl_kl.ctrl_relay('KL54', False)
        ctrl_kl.ctrl_relay('KL55', False)
        ctrl_kl.ctrl_relay('KL56', False)
        ctrl_kl.ctrl_relay('KL57', False)
        ctrl_kl.ctrl_relay('KL58', False)
        ctrl_kl.ctrl_relay('KL59', False)
        ctrl_kl.ctrl_relay('KL60', False)

    @staticmethod
    def stop_procedure_1():
        ctrl_kl.ctrl_relay('KL62', False)
        ctrl_kl.ctrl_relay('KL37', False)

    def stop_procedure_21(self):
        self.stop_procedure_1()
        ctrl_kl.ctrl_relay('KL43', False)

    def stop_procedure_22(self):
        self.stop_procedure_1()
        ctrl_kl.ctrl_relay('KL44', False)

    def stop_procedure_2(self):
        self.stop_procedure_1()
        self.sbros_perv_obm()

    @staticmethod
    def stop_procedure_31():
        ctrl_kl.ctrl_relay('KL62', False)
        sleep(1)
        ctrl_kl.ctrl_relay('KL37', False)
        ctrl_kl.ctrl_relay('KL43', False)
        ctrl_kl.ctrl_relay('KL60', False)

    @staticmethod
    def stop_procedure_32():
        ctrl_kl.ctrl_relay('KL62', False)
        sleep(1)
        ctrl_kl.ctrl_relay('KL37', False)
        ctrl_kl.ctrl_relay('KL44', False)
        ctrl_kl.ctrl_relay('KL54', False)

    def stop_procedure_3(self):
        ctrl_kl.ctrl_relay('KL62', False)
        sleep(1)
        ctrl_kl.ctrl_relay('KL37', False)
        self.sbros_perv_obm()
        self.sbros_vtor_obm()

    def sbros_kl63_proc_1_21_31(self):
        """
        используется для сброса после процедуры 1 -> 2.1 -> 3.1
        :return:
        """
        ctrl_kl.ctrl_relay('KL63', False)
        sleep(0.1)
        self.stop_procedure_31()

    def sbros_kl63_proc_1_22_32(self):
        """
        используется для сброса после процедуры 1 -> 2.2 -> 3.2
        :return:
        """
        ctrl_kl.ctrl_relay('KL63', False)
        sleep(0.1)
        self.stop_procedure_32()

    def sbros_kl63_proc_all(self):
        ctrl_kl.ctrl_relay('KL63', False)
        sleep(0.1)
        self.stop_procedure_3()


class Resistor(object):
    """
        R1		1,2	    Ом	KL3
        R2		2,1	    Ом	KL4
        R3		3,4	    Ом	KL5
        R4		6,9	    Ом	KL6
        R5		15	    Ом	KL7
        R6		29,1	Ом	KL8
        R7		61,3	Ом	KL9
        R8		127,6	Ом	KL10
        R9		46,3	Ом	KL1
        R10		3,9	    кОм	KL13
        R11		4,24	кОм	KL14
        R12		8,82	кОм	KL15
        R13		17,48	кОм	KL16
        R14		35,2	кОм	KL17
        R15		75	    кОм	KL18
        R16		150	    кОм	KL19
        R17		295,5	кОм	KL20
        R18		183,3	кОм	
    """

    @staticmethod
    def resist_ohm(ohm):

        if ohm == 0:
            ctrl_kl.ctrl_relay('KL3', True)
            ctrl_kl.ctrl_relay('KL4', True)
            ctrl_kl.ctrl_relay('KL5', True)
            ctrl_kl.ctrl_relay('KL6', True)
            ctrl_kl.ctrl_relay('KL7', True)
            ctrl_kl.ctrl_relay('KL8', True)
            ctrl_kl.ctrl_relay('KL9', True)
            ctrl_kl.ctrl_relay('KL10', True)
        elif ohm == 10:
            ctrl_kl.ctrl_relay('KL3', False)
            ctrl_kl.ctrl_relay('KL4', False)
            ctrl_kl.ctrl_relay('KL5', True)
            ctrl_kl.ctrl_relay('KL6', False)
            ctrl_kl.ctrl_relay('KL7', True)
            ctrl_kl.ctrl_relay('KL8', True)
            ctrl_kl.ctrl_relay('KL9', True)
            ctrl_kl.ctrl_relay('KL10', True)
        elif ohm == 15:
            ctrl_kl.ctrl_relay('KL3', True)
            ctrl_kl.ctrl_relay('KL4', True)
            ctrl_kl.ctrl_relay('KL5', True)
            ctrl_kl.ctrl_relay('KL6', True)
            ctrl_kl.ctrl_relay('KL7', False)
            ctrl_kl.ctrl_relay('KL8', True)
            ctrl_kl.ctrl_relay('KL9', True)
            ctrl_kl.ctrl_relay('KL10', True)
        elif ohm == 20:
            ctrl_kl.ctrl_relay('KL3', True)
            ctrl_kl.ctrl_relay('KL4', False)
            ctrl_kl.ctrl_relay('KL5', False)
            ctrl_kl.ctrl_relay('KL6', True)
            ctrl_kl.ctrl_relay('KL7', False)
            ctrl_kl.ctrl_relay('KL8', True)
            ctrl_kl.ctrl_relay('KL9', True)
            ctrl_kl.ctrl_relay('KL10', True)
        elif ohm == 35:
            ctrl_kl.ctrl_relay('KL3', False)
            ctrl_kl.ctrl_relay('KL4', False)
            ctrl_kl.ctrl_relay('KL5', False)
            ctrl_kl.ctrl_relay('KL6', True)
            ctrl_kl.ctrl_relay('KL7', True)
            ctrl_kl.ctrl_relay('KL8', False)
            ctrl_kl.ctrl_relay('KL9', True)
            ctrl_kl.ctrl_relay('KL10', True)
        elif ohm == 46:
            ctrl_kl.ctrl_relay('KL3', True)
            ctrl_kl.ctrl_relay('KL4', False)
            ctrl_kl.ctrl_relay('KL5', True)
            ctrl_kl.ctrl_relay('KL6', True)
            ctrl_kl.ctrl_relay('KL7', False)
            ctrl_kl.ctrl_relay('KL8', False)
            ctrl_kl.ctrl_relay('KL9', True)
            ctrl_kl.ctrl_relay('KL10', True)
        elif ohm == 50:
            ctrl_kl.ctrl_relay('KL3', False)
            ctrl_kl.ctrl_relay('KL4', False)
            ctrl_kl.ctrl_relay('KL5', False)
            ctrl_kl.ctrl_relay('KL6', True)
            ctrl_kl.ctrl_relay('KL7', False)
            ctrl_kl.ctrl_relay('KL8', False)
            ctrl_kl.ctrl_relay('KL9', True)
            ctrl_kl.ctrl_relay('KL10', True)
        elif ohm == 100:
            ctrl_kl.ctrl_relay('KL3', True)
            ctrl_kl.ctrl_relay('KL4', True)
            ctrl_kl.ctrl_relay('KL5', False)
            ctrl_kl.ctrl_relay('KL6', False)
            ctrl_kl.ctrl_relay('KL7', True)
            ctrl_kl.ctrl_relay('KL8', False)
            ctrl_kl.ctrl_relay('KL9', False)
            ctrl_kl.ctrl_relay('KL10', True)
        elif ohm == 110:
            ctrl_kl.ctrl_relay('KL3', False)
            ctrl_kl.ctrl_relay('KL4', True)
            ctrl_kl.ctrl_relay('KL5', False)
            ctrl_kl.ctrl_relay('KL6', True)
            ctrl_kl.ctrl_relay('KL7', False)
            ctrl_kl.ctrl_relay('KL8', False)
            ctrl_kl.ctrl_relay('KL9', False)
            ctrl_kl.ctrl_relay('KL10', True)
        elif ohm == 150:
            ctrl_kl.ctrl_relay('KL3', False)
            ctrl_kl.ctrl_relay('KL4', True)
            ctrl_kl.ctrl_relay('KL5', True)
            ctrl_kl.ctrl_relay('KL6', False)
            ctrl_kl.ctrl_relay('KL7', False)
            ctrl_kl.ctrl_relay('KL8', True)
            ctrl_kl.ctrl_relay('KL9', True)
            ctrl_kl.ctrl_relay('KL10', False)
        elif ohm == 255:
            ctrl_kl.ctrl_relay('KL3', False)
            ctrl_kl.ctrl_relay('KL4', False)
            ctrl_kl.ctrl_relay('KL5', False)
            ctrl_kl.ctrl_relay('KL6', False)
            ctrl_kl.ctrl_relay('KL7', False)
            ctrl_kl.ctrl_relay('KL8', False)
            ctrl_kl.ctrl_relay('KL9', False)
            ctrl_kl.ctrl_relay('KL10', False)
        
    @staticmethod
    def resist_kohm(kohm):

        if kohm == 0:
            ctrl_kl.ctrl_relay('KL13', True)
            ctrl_kl.ctrl_relay('KL14', True)
            ctrl_kl.ctrl_relay('KL15', True)
            ctrl_kl.ctrl_relay('KL16', True)
            ctrl_kl.ctrl_relay('KL17', True)
            ctrl_kl.ctrl_relay('KL18', True)
            ctrl_kl.ctrl_relay('KL19', True)
            ctrl_kl.ctrl_relay('KL20', True)
        if kohm == 12:
            ctrl_kl.ctrl_relay('KL13', False)
            ctrl_kl.ctrl_relay('KL14', True)
            ctrl_kl.ctrl_relay('KL15', False)
            ctrl_kl.ctrl_relay('KL16', True)
            ctrl_kl.ctrl_relay('KL17', True)
            ctrl_kl.ctrl_relay('KL18', True)
            ctrl_kl.ctrl_relay('KL19', True)
            ctrl_kl.ctrl_relay('KL20', True)
        if kohm == 21:
            ctrl_kl.ctrl_relay('KL13', True)
            ctrl_kl.ctrl_relay('KL14', False)
            ctrl_kl.ctrl_relay('KL15', True)
            ctrl_kl.ctrl_relay('KL16', False)
            ctrl_kl.ctrl_relay('KL17', True)
            ctrl_kl.ctrl_relay('KL18', True)
            ctrl_kl.ctrl_relay('KL19', True)
            ctrl_kl.ctrl_relay('KL20', True)
        elif kohm == 26:
            ctrl_kl.ctrl_relay('KL13', True)
            ctrl_kl.ctrl_relay('KL14', True)
            ctrl_kl.ctrl_relay('KL15', False)
            ctrl_kl.ctrl_relay('KL16', False)
            ctrl_kl.ctrl_relay('KL17', True)
            ctrl_kl.ctrl_relay('KL18', True)
            ctrl_kl.ctrl_relay('KL19', True)
            ctrl_kl.ctrl_relay('KL20', True)
        elif kohm == 30:
            ctrl_kl.ctrl_relay('KL13', False)
            ctrl_kl.ctrl_relay('KL14', True)
            ctrl_kl.ctrl_relay('KL15', False)
            ctrl_kl.ctrl_relay('KL16', False)
            ctrl_kl.ctrl_relay('KL17', True)
            ctrl_kl.ctrl_relay('KL18', True)
            ctrl_kl.ctrl_relay('KL19', True)
            ctrl_kl.ctrl_relay('KL20', True)
        elif kohm == 61:
            ctrl_kl.ctrl_relay('KL13', True)
            ctrl_kl.ctrl_relay('KL14', True)
            ctrl_kl.ctrl_relay('KL15', False)
            ctrl_kl.ctrl_relay('KL16', False)
            ctrl_kl.ctrl_relay('KL17', False)
            ctrl_kl.ctrl_relay('KL18', True)
            ctrl_kl.ctrl_relay('KL19', True)
            ctrl_kl.ctrl_relay('KL20', True)
        elif kohm == 65:
            ctrl_kl.ctrl_relay('KL13', True)
            ctrl_kl.ctrl_relay('KL14', False)
            ctrl_kl.ctrl_relay('KL15', False)
            ctrl_kl.ctrl_relay('KL16', False)
            ctrl_kl.ctrl_relay('KL17', False)
            ctrl_kl.ctrl_relay('KL18', True)
            ctrl_kl.ctrl_relay('KL19', True)
            ctrl_kl.ctrl_relay('KL20', True)
        elif kohm == 100:
            ctrl_kl.ctrl_relay('KL13', False)
            ctrl_kl.ctrl_relay('KL14', False)
            ctrl_kl.ctrl_relay('KL15', True)
            ctrl_kl.ctrl_relay('KL16', False)
            ctrl_kl.ctrl_relay('KL17', True)
            ctrl_kl.ctrl_relay('KL18', False)
            ctrl_kl.ctrl_relay('KL19', True)
            ctrl_kl.ctrl_relay('KL20', True)
        elif kohm == 200:
            ctrl_kl.ctrl_relay('KL13', False)
            ctrl_kl.ctrl_relay('KL14', False)
            ctrl_kl.ctrl_relay('KL15', False)
            ctrl_kl.ctrl_relay('KL16', True)
            ctrl_kl.ctrl_relay('KL17', False)
            ctrl_kl.ctrl_relay('KL18', True)
            ctrl_kl.ctrl_relay('KL19', False)
            ctrl_kl.ctrl_relay('KL20', True)
        elif kohm == 220:
            ctrl_kl.ctrl_relay('KL13', False)
            ctrl_kl.ctrl_relay('KL14', False)
            ctrl_kl.ctrl_relay('KL15', False)
            ctrl_kl.ctrl_relay('KL16', False)
            ctrl_kl.ctrl_relay('KL17', False)
            ctrl_kl.ctrl_relay('KL18', True)
            ctrl_kl.ctrl_relay('KL19', False)
            ctrl_kl.ctrl_relay('KL20', True)
        elif kohm == 590:
            ctrl_kl.ctrl_relay('KL13', False)
            ctrl_kl.ctrl_relay('KL14', False)
            ctrl_kl.ctrl_relay('KL15', False)
            ctrl_kl.ctrl_relay('KL16', False)
            ctrl_kl.ctrl_relay('KL17', False)
            ctrl_kl.ctrl_relay('KL18', False)
            ctrl_kl.ctrl_relay('KL19', False)
            ctrl_kl.ctrl_relay('KL20', False)
        
    @staticmethod
    def resist_10_to_20_ohm():
        ctrl_kl.ctrl_relay('KL3', True)
        ctrl_kl.ctrl_relay('KL6', True)
        ctrl_kl.ctrl_relay('KL8', True)
        ctrl_kl.ctrl_relay('KL9', True)
        ctrl_kl.ctrl_relay('KL10', True)

    @staticmethod
    def resist_10_to_35_ohm():
        ctrl_kl.ctrl_relay('KL5', False)
        ctrl_kl.ctrl_relay('KL6', True)
        ctrl_kl.ctrl_relay('KL8', False)
        
    @staticmethod
    def resist_10_to_100_ohm():
        ctrl_kl.ctrl_relay('KL9', False)
        ctrl_kl.ctrl_relay('KL8', False)

    @staticmethod
    def resist_10_to_46_ohm():
        ctrl_kl.ctrl_relay('KL7', False)
        ctrl_kl.ctrl_relay('KL6', True)
        ctrl_kl.ctrl_relay('KL8', False)

    @staticmethod
    def resist_10_to_50_ohm():
        ctrl_kl.ctrl_relay('KL7', False)
        ctrl_kl.ctrl_relay('KL5', False)
        ctrl_kl.ctrl_relay('KL6', True)
        ctrl_kl.ctrl_relay('KL8', False)

    @staticmethod
    def resist_10_to_110_ohm():
        ctrl_kl.ctrl_relay('KL9', False)
        ctrl_kl.ctrl_relay('KL4', True)
        ctrl_kl.ctrl_relay('KL5', False)
        ctrl_kl.ctrl_relay('KL8', False)
        ctrl_kl.ctrl_relay('KL6', True)
        ctrl_kl.ctrl_relay('KL7', False)

    @staticmethod
    def resist_35_to_110_ohm():
        ctrl_kl.ctrl_relay('KL9', False)
        ctrl_kl.ctrl_relay('KL7', False)

    @staticmethod
    def resist_10_to_137_ohm():
        ctrl_kl.ctrl_relay('KL10', False)

    @staticmethod
    def resist_0_to_50_ohm():
        ctrl_kl.ctrl_relay('KL3', False)
        ctrl_kl.ctrl_relay('KL4', False)
        ctrl_kl.ctrl_relay('KL5', False)
        ctrl_kl.ctrl_relay('KL7', False)
        ctrl_kl.ctrl_relay('KL8', False)

    @staticmethod
    def resist_0_to_100_ohm():
        ctrl_kl.ctrl_relay('KL5', False)
        ctrl_kl.ctrl_relay('KL6', False)
        ctrl_kl.ctrl_relay('KL8', False)
        ctrl_kl.ctrl_relay('KL9', False)

    @staticmethod
    def resist_0_to_63_ohm():
        ctrl_kl.ctrl_relay('KL9', False)
        ctrl_kl.ctrl_relay('KL4', False)

    @staticmethod
    def resist_220_to_100_kohm():
        ctrl_kl.ctrl_relay('KL18', False)
        ctrl_kl.ctrl_relay('KL19', True)
        ctrl_kl.ctrl_relay('KL17', True)
        ctrl_kl.ctrl_relay('KL15', True)
        

class ModbusConnectException(Exception):
    """вываливается когда нет связи по modbus"""
    pass


class ResultMsg(object):
    """
    исправность/неисправность блока
    """
    reset = ResetRelay()

    def test_error(self, test_number: float):
        msg = (f'Тест: {test_number} не пройден')
        my_msg(msg)
        self.reset.reset_all()

    def test_good(self):
        msg = "Тестирование завершено:\nБлок исправен "
        my_msg(msg)
        self.reset.reset_all()
