#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Алгоритм проверки

Тип блока	Производитель
БДЗ	Строй-энергомаш
БДЗ	ТЭТЗ-Инвест
БДЗ	нет производителя

"""

from sys import exit
from time import sleep
from my_msgbox import *
from gen_func_utils import *
from gen_mb_client import *
from gen_mysql_connect import *

__all__ = ["TestBDZ"]


class TestBDZ(object):

    __mb_ctrl = CtrlKL()
    __read_mb = ReadMB()
    __mysql_conn = MySQLConnect()
    __fault = Bug(True)

    def __init__(self):
        pass
    
    def st_test_10_bdz(self) -> bool:
        """
        Тест 1. Включение/выключение блока при нормальном уровне сопротивления изоляции:
        """
        # Сообщение	Убедитесь в отсутствии блоков в панелях разъемов.
        # Вставьте испытуемый блок БДЗ в разъем Х16 на панели B.
        # Вставьте заведомо исправные блок БИ в разъем Х26 и блок БУЗ-2 в разъем Х17, расположенные на панели B.
        msg_1 = "Убедитесь в отсутствии блоков в панелях разъемов. " \
                "Вставьте испытуемый блок БДЗ в разъем Х16 на панели B"
        msg_2 = "Вставьте заведомо исправные блок БИ в разъем Х26 и блок БУЗ-2 в разъем Х17, " \
                "расположенные на панели B"
        if my_msg(msg_1):
            if my_msg(msg_2):
                pass
            else:
                return False
        else:
            return False
        self.__mb_ctrl.ctrl_relay('KL21', True)
        self.__mb_ctrl.ctrl_relay('KL2', True)
        self.__mb_ctrl.ctrl_relay('KL66', True)
        sleep(6)
        self.__mb_ctrl.ctrl_relay('KL84', True)
        sleep(2)
        self.__mb_ctrl.ctrl_relay('KL84', False)
        sleep(1)
        self.__mb_ctrl.ctrl_relay('KL80', True)
        sleep(0.1)
        self.__mb_ctrl.ctrl_relay('KL24', True)
        sleep(5)
        in_a1, in_a2 = self.__inputs_a()
        if in_a1 is True and in_a2 is True:
            pass
        else:
            self.__fault.debug_msg("положение выходов блока не соответствует", 1)
            self.__mysql_conn.mysql_ins_result("неисправен", "1")
            return False
        self.__fault.debug_msg("положение выходов блока соответствует", 4)
        return True

    def st_test_11_bdz(self) -> bool:
        """
        1.2.	Выключение блока
        """
        sleep(1)
        self.__mb_ctrl.ctrl_relay('KL80', False)
        sleep(0.1)
        self.__mb_ctrl.ctrl_relay('KL24', False)
        sleep(5)
        in_a1, in_a2 = self.__inputs_a()
        if in_a1 is False and in_a2 is False:
            pass
        else:
            self.__fault.debug_msg("положение выходов блока не соответствует", 1)
            self.__mysql_conn.mysql_ins_result("неисправен", "1")
            return False
        self.__fault.debug_msg("положение выходов блока соответствует", 4)
        self.__mysql_conn.mysql_ins_result("исправен", "1")
        return True

    def st_test_20_bdz(self) -> bool:
        """
        # Тест 2. Блокировка включения при снижении уровня сопротивления изоляции:
        """
        sleep(1)
        self.__mb_ctrl.ctrl_relay('KL22', True)
        sleep(1)
        self.__mb_ctrl.ctrl_relay('KL80', True)
        sleep(0.1)
        self.__mb_ctrl.ctrl_relay('KL24', True)
        sleep(5)
        in_a1, in_a2 = self.__inputs_a()
        if in_a1 is False and in_a2 is False:
            pass
        else:
            self.__fault.debug_msg("положение выходов блока не соответствует", 1)
            self.__mysql_conn.mysql_ins_result("неисправен", "2")
            return False
        self.__fault.debug_msg("положение выходов блока соответствует", 4)
        self.__mysql_conn.mysql_ins_result("исправен", "2")
        return True
    
    def __inputs_a(self):
        in_a1 = self.__read_mb.read_discrete(1)
        in_a2 = self.__read_mb.read_discrete(2)
        if in_a1 is None or in_a2 is None:
            raise ModbusConnectException(f'нет связи с контроллером')
        return in_a1, in_a2

    def st_test_bdz(self) -> bool:
        if self.st_test_10_bdz():
            if self.st_test_11_bdz():
                if self.st_test_20_bdz():
                    return True
        return False


if __name__ == '__main__':
    test_bdz = TestBDZ()
    reset_test_bdz = ResetRelay()
    mysql_conn_bdz = MySQLConnect()
    fault = Bug(True)
    try:
        if test_bdz.st_test_bdz():
            mysql_conn_bdz.mysql_block_good()
            my_msg('Блок исправен')
        else:
            mysql_conn_bdz.mysql_block_bad()
            my_msg('Блок неисправен', '#A61E1E')
    except OSError:
        my_msg("ошибка системы")
    except SystemError:
        my_msg("внутренняя ошибка")
    except ModbusConnectException as mce:
        fault.debug_msg(mce, 1)
        my_msg(str(mce), '#A61E1E')
    finally:
        reset_test_bdz.reset_all()
        exit()
