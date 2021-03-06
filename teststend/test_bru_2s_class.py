#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Алгоритм проверки

Тип блока	Производитель	    Уникальный номер
БРУ-2С	Нет производителя

"""

from sys import exit

from my_msgbox import *
from gen_func_utils import *
from gen_mb_client import *
from gen_mysql_connect import *

__all__ = ["TestBRU2S"]


class TestBRU2S(object):

    __resist = Resistor()
    __read_mb = ReadMB()
    __ctrl_kl = CtrlKL()
    __mysql_conn = MySQLConnect()

    def __init__(self):
        pass

    def st_test_10_bru_2s(self) -> bool:
        """
        Тест 1. Проверка исходного состояния блока:
        """
        in_a1 = self.__inputs_a()
        if in_a1 is False:
            pass
        else:
            self.__mysql_conn.mysql_ins_result('неисправен', '1')
            self.__mysql_conn.mysql_error(47)
            return False
        self.__mysql_conn.mysql_ins_result('исправен', '1')

    def st_test_20_bru_2s(self) -> bool:
        """
        Тест 2. Проверка включения/выключения блока от кнопки «Пуск/Стоп»
        """
        self.__ctrl_kl.ctrl_relay('KL21', True)
        in_a1 = self.__inputs_a()
        if in_a1 is False:
            pass
        else:
            self.__mysql_conn.mysql_ins_result('неисправен', '2')
            self.__mysql_conn.mysql_error(48)
            return False

    def st_test_21_bru_2s(self) -> bool:
        """
        2.2. Включение блока от кнопки «Пуск»
        2.3. Проверка удержания блока во включенном состоянии при подключении Rш пульта управления:
        """
        if self.__subtest_22(2.2, 2):
            if self.__subtest_23(2.3, 2):
                return True
        return False

    def st_test_22_bru_2s(self) -> bool:
        """
        2.4. Выключение блока от кнопки «Стоп»
        """
        self.__ctrl_kl.ctrl_relay('KL12', False)
        in_a1 = self.__inputs_a()
        if in_a1 is False:
            pass
        else:
            self.__mysql_conn.mysql_ins_result('неисправен', '2')
            self.__mysql_conn.mysql_error(51)
            return False
        self.__ctrl_kl.ctrl_relay('KL25', False)
        self.__mysql_conn.mysql_ins_result('исправен', '2')
        return True

    def st_test_30_bru_2s(self) -> bool:
        """
        Повторяем подтесты 2.2. Включение блока от кнопки «Пуск»
        Повторяем подтесты 2.3. Проверка удержания блока во включенном состоянии при подключении Rш пульта управления:
        """
        if self.__subtest_22(3.1, 3):
            if self.__subtest_23(3.2, 3):
                return True
        return False

    def st_test_31_bru_2s(self) -> bool:
        """
        3. Отключение выходного контакта блока при увеличении сопротивления цепи заземления
        """
        self.__resist.resist_ohm(150)
        in_a1 = self.__inputs_a()
        if in_a1 is False:
            pass
        else:
            self.__mysql_conn.mysql_ins_result('неисправен', '3')
            self.__mysql_conn.mysql_error(52)
            return False
        self.__ctrl_kl.ctrl_relay('KL12', False)
        self.__ctrl_kl.ctrl_relay('KL25', False)
        self.__mysql_conn.mysql_ins_result('исправен', '3')
        return True

    def st_test_40_bru_2s(self) -> bool:
        """
        Повторяем подтесты 2.2. Включение блока от кнопки «Пуск»
        Повторяем подтесты 2.3. Проверка удержания блока во включенном состоянии при подключении Rш пульта управления:
        """
        if self.__subtest_22(4.1, 4):
            if self.__subtest_23(4.2, 4):
                return True
        return False

    def st_test_41_bru_2s(self) -> bool:
        """
        4. Защита от потери управляемости при замыкании проводов ДУ
        """
        self.__ctrl_kl.ctrl_relay('KL11', True)
        in_a1 = self.__inputs_a()
        if in_a1 is False:
            pass
        else:
            self.__mysql_conn.mysql_error(53)
            self.__mysql_conn.mysql_ins_result('неисправен', '4')
            return False
        self.__ctrl_kl.ctrl_relay('KL12', False)
        self.__ctrl_kl.ctrl_relay('KL25', False)
        self.__ctrl_kl.ctrl_relay('KL11', False)
        self.__mysql_conn.mysql_ins_result('исправен', '4')
        return True

    def st_test_50_bru_2s(self) -> bool:
        """
        Повторяем подтесты 2.2. Включение блока от кнопки «Пуск»
        Повторяем подтесты 2.3. Проверка удержания блока во включенном состоянии при подключении Rш пульта управления:
        """
        if self.__subtest_22(5.1, 5):
            if self.__subtest_23(5.2, 5):
                return True
        return False

    def st_test_51_bru_2s(self) -> bool:
        """
        Тест 5. Защита от потери управляемости блока при обрыве проводов ДУ
        """
        self.__ctrl_kl.ctrl_relay('KL12', False)
        in_a1 = self.__inputs_a()
        if in_a1 is False:
            pass
        else:
            self.__mysql_conn.mysql_error(54)
            self.__mysql_conn.mysql_ins_result('неисправен', '5')
            return False
        self.__ctrl_kl.ctrl_relay('KL25', False)
        self.__mysql_conn.mysql_ins_result('исправен', '5')
        return True

    def st_test_60_bru_2s(self) -> bool:
        msg_1 = "Переведите тумблер «П/А» на блоке в положение «П» и нажмите кнопку «ОК» " \
                "Если на блоке нет тумблера «П/А» нажмите кнопку «Отмена»"
        if my_msg(msg_1):
            if self.__subtest_6():
                self.__mysql_conn.mysql_ins_result('исправен', '6')
                if self.__subtest_7():
                    self.__mysql_conn.mysql_ins_result('исправен', '7')
                else:
                    self.__mysql_conn.mysql_ins_result('неисправен', '7')
                    return False
            else:
                self.__mysql_conn.mysql_ins_result('неисправен', '6')
                return False
        else:
            if self.__subtest_7():
                self.__mysql_conn.mysql_ins_result('пропущен', '6')
                self.__mysql_conn.mysql_ins_result('исправен', '7')
            else:
                self.__mysql_conn.mysql_ins_result('пропущен', '6')
                self.__mysql_conn.mysql_ins_result('неисправен', '7')
                return False
        return True
    
    def __subtest_22(self, subtest_0_num: float, test_0_num: int) -> bool:
        """
        2.2. Включение блока от кнопки «Пуск»
        """
        self.__mysql_conn.mysql_ins_result(f'идёт тест {subtest_0_num}', f'{test_0_num}')
        self.__resist.resist_ohm(0)
        self.__ctrl_kl.ctrl_relay('KL12', True)
        in_a1 = self.__inputs_a()
        if in_a1 is True:
            pass
        else:
            self.__mysql_conn.mysql_error(49)
            self.__mysql_conn.mysql_ins_result('неисправен', f'{test_0_num}')
            return False
        return True

    def __subtest_23(self, subtest_1_num: float, test_1_num: int) -> bool:
        """
        2.3. Проверка удержания блока во включенном состоянии при подключении Rш пульта управления:
        """
        self.__mysql_conn.mysql_ins_result(f'идёт тест {subtest_1_num}', f'{test_1_num}')
        self.__ctrl_kl.ctrl_relay('KL25', True)
        in_a1 = self.__inputs_a()
        if in_a1 is True:
            pass
        else:
            self.__mysql_conn.mysql_error(50)
            self.__mysql_conn.mysql_ins_result('неисправен', f'{test_1_num}')
            return False
        return True
    
    def __subtest_6(self) -> bool:
        """
        Тест 6. Блокировка включения блока при снижении сопротивления изоляции
        контролируемого присоединения до уровня предупредительной уставки
        """
        self.__resist.resist_kohm(200)
        self.__ctrl_kl.ctrl_relay('KL12', True)
        in_a1 = self.__inputs_a()
        if in_a1 is False:
            self.__ctrl_kl.ctrl_relay('KL12', False)
            return True
        else:
            self.__mysql_conn.mysql_error(55)
            return False
    
    def __subtest_7(self):
        """
        Тест 7. Блокировка включения блока при снижении сопротивления изоляции
        контролируемого присоединения до уровня аварийной уставки
        """
        self.__resist.resist_kohm(30)
        self.__ctrl_kl.ctrl_relay('KL12', True)
        in_a1 = self.__inputs_a()
        if in_a1 is False:
            self.__ctrl_kl.ctrl_relay('KL12', False)
            return True
        else:
            self.__mysql_conn.mysql_error(56)
            return False
    
    def __inputs_a(self):
        in_a1 = self.__read_mb.read_discrete(1)
        if in_a1 is None:
            raise ModbusConnectException(f'нет связи с контроллером')
        return in_a1

    def st_test_bru_2s(self) -> bool:
        if self.st_test_10_bru_2s():
            if self.st_test_20_bru_2s():
                if self.st_test_21_bru_2s():
                    if self.st_test_22_bru_2s():
                        if self.st_test_30_bru_2s():
                            if self.st_test_31_bru_2s():
                                if self.st_test_40_bru_2s():
                                    if self.st_test_41_bru_2s():
                                        if self.st_test_50_bru_2s():
                                            if self.st_test_51_bru_2s():
                                                if self.st_test_60_bru_2s():
                                                    return True
        return False


if __name__ == '__main__':
    test_bru_2s = TestBRU2S()
    reset_test_bru_2s = ResetRelay()
    mysql_conn_bru_2s = MySQLConnect()
    fault = Bug(True)
    try:
        if test_bru_2s.st_test_bru_2s():
            mysql_conn_bru_2s.mysql_block_good()
            my_msg('Блок исправен')
        else:
            mysql_conn_bru_2s.mysql_block_bad()
            my_msg('Блок неисправен', '#A61E1E')
    except OSError:
        my_msg("ошибка системы")
    except SystemError:
        my_msg("внутренняя ошибка")
    except ModbusConnectException as mce:
        fault.debug_msg(mce, 1)
        my_msg(str(mce), '#A61E1E')
    finally:
        reset_test_bru_2s.reset_all()
        exit()
