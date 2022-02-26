#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Алгоритм проверки
Тип блока Производитель
БУР ПМВИР (пускатель)	Нет производителя

"""

from sys import exit
from time import sleep
from gen_func_utils import *
from my_msgbox import *
from gen_mb_client import *
from gen_mysql_connect import *

__all__ = ["TestBURPMVIR"]

reset = ResetRelay()
resist = Resistor()
read_mb = ReadMB()
ctrl_kl = CtrlKL()
mysql_conn = MySQLConnect()
fault = Bug(None)


class TestBURPMVIR(object):
    def __init__(self):
        pass
    
    def st_test_bur_pmvir(self):
        # reset.reset_all()
        # Тест 1. Проверка исходного состояния блока:
        in_a1, in_a2 = self.__inputs_a()
        if in_a1 == False and in_a2 == False:
            pass
        elif in_a1 == True:
            mysql_conn.mysql_error(166)
            mysql_conn.mysql_ins_result("неисправен", '1')
            return False
        elif in_a2 == True:
            mysql_conn.mysql_error(167)
            mysql_conn.mysql_ins_result("неисправен", '1')
            return False
        mysql_conn.mysql_ins_result("исправен", '1')
        # Тест 2. Проверка включения/выключения блока от кнопки «Пуск/Стоп» в режиме «Вперёд».
        ctrl_kl.ctrl_relay('KL21', True)
        in_a1, in_a2 = self.__inputs_a()
        if in_a1 == False and in_a2 == False:
            pass
        elif in_a1 == True:
            mysql_conn.mysql_error(168)
            mysql_conn.mysql_ins_result("неисправен", '2')
            return False
        elif in_a2 == True:
            mysql_conn.mysql_error(169)
            mysql_conn.mysql_ins_result("неисправен", '2')
            return False
        if self.__subtest_22_23():
            pass
        else:
            return False
        # 2.4. Выключение блока от кнопки «Стоп» режима «Вперёд»
        ctrl_kl.ctrl_relay('KL12', False)
        in_a1, in_a2 = self.__inputs_a()
        if in_a1 == False and in_a2 == False:
            pass
        elif in_a1 == True:
            mysql_conn.mysql_error(174)
            mysql_conn.mysql_ins_result("неисправен", '2')
            return False
        elif in_a2 == True:
            mysql_conn.mysql_error(175)
            mysql_conn.mysql_ins_result("неисправен", '2')
            return False
        ctrl_kl.ctrl_relay('KL25', False)
        mysql_conn.mysql_ins_result("исправен", '2')
        # 3. Отключение контакта «Вперёд» при увеличении сопротивления цепи заземления
        if self.__subtest_22_23():
            pass
        else:
            return False
        # Формирование 100 Ом
        resist.resist_0_to_100_ohm()
        in_a1, in_a2 = self.__inputs_a()
        if in_a1 == False and in_a2 == False:
            pass
        elif in_a1 == True:
            mysql_conn.mysql_error(176)
            mysql_conn.mysql_ins_result("неисправен", '3')
            return False
        elif in_a2 == True:
            mysql_conn.mysql_error(177)
            mysql_conn.mysql_ins_result("неисправен", '3')
            return False
        mysql_conn.mysql_ins_result("исправен", '3')
        ctrl_kl.ctrl_relay('KL12', False)
        ctrl_kl.ctrl_relay('KL25', False)
        # 4. Защита от потери управляемости канала «Вперёд» при замыкании проводов ДУ
        if self.__subtest_22_23():
            pass
        else:
            return False
        ctrl_kl.ctrl_relay('KL11', True)
        in_a1, in_a2 = self.__inputs_a()
        if in_a1 == False and in_a2 == False:
            pass
        elif in_a1 == True:
            mysql_conn.mysql_error(178)
            mysql_conn.mysql_ins_result("неисправен", '4')
            return False
        elif in_a2 == True:
            mysql_conn.mysql_error(179)
            mysql_conn.mysql_ins_result("неисправен", '4')
            return False
        mysql_conn.mysql_ins_result("исправен", '4')
        ctrl_kl.ctrl_relay('KL12', False)
        ctrl_kl.ctrl_relay('KL25', False)
        ctrl_kl.ctrl_relay('KL11', False)
        # Тест 5. Защита от потери управляемости канала «Вперёд» при обрыве проводов ДУ
        if self.__subtest_22_23():
            pass
        else:
            return False
        ctrl_kl.ctrl_relay('KL12', False)
        in_a1, in_a2 = self.__inputs_a()
        if in_a1 == False and in_a2 == False:
            pass
        elif in_a1 == True:
            mysql_conn.mysql_error(180)
            mysql_conn.mysql_ins_result("неисправен", '5')
            return False
        elif in_a2 == True:
            mysql_conn.mysql_error(181)
            mysql_conn.mysql_ins_result("неисправен", '5')
            return False
        mysql_conn.mysql_ins_result("исправен", '5')
        ctrl_kl.ctrl_relay('KL25', False)
        # Тест 6. Проверка включения/выключения блока от кнопки «Пуск/Стоп» в режиме «Назад».
        # Переключение в режим ДУ «Назад»	KL26 - ВКЛ
        ctrl_kl.ctrl_relay('KL26', True)
        sleep(1)
        in_a1, in_a2 = self.__inputs_a()
        if in_a1 == False and in_a2 == False:
            pass
        elif in_a1 == True:
            mysql_conn.mysql_error(168)
            mysql_conn.mysql_ins_result("неисправен", '6')
            return False
        elif in_a2 == True:
            mysql_conn.mysql_error(169)
            mysql_conn.mysql_ins_result("неисправен", '6')
            return False
        if self.__subtest_62_63():
            pass
        else:
            return False
        # 6.4. Выключение блока от кнопки «Стоп» режима «Назад»
        ctrl_kl.ctrl_relay('KL12', False)
        in_a1, in_a2 = self.__inputs_a()
        if in_a1 == False and in_a2 == False:
            pass
        elif in_a1 == True:
            mysql_conn.mysql_error(186)
            mysql_conn.mysql_ins_result("неисправен", '6')
            return False
        elif in_a2 == True:
            mysql_conn.mysql_error(187)
            mysql_conn.mysql_ins_result("неисправен", '6')
            return False
        mysql_conn.mysql_ins_result("исправен", '6')
        ctrl_kl.ctrl_relay('KL25', False)
        # 7. Отключение контакта «Назад» при увеличении сопротивления цепи заземления
        if self.__subtest_62_63():
            pass
        else:
            return False
        resist.resist_0_to_100_ohm()
        in_a1, in_a2 = self.__inputs_a()
        if in_a1 == False and in_a2 == False:
            pass
        elif in_a1 == True:
            mysql_conn.mysql_error(188)
            mysql_conn.mysql_ins_result("неисправен", '7')
            return False
        elif in_a2 == True:
            mysql_conn.mysql_error(189)
            mysql_conn.mysql_ins_result("неисправен", '7')
            return False
        mysql_conn.mysql_ins_result("исправен", '7')
        ctrl_kl.ctrl_relay('KL12', False)
        ctrl_kl.ctrl_relay('KL25', False)
        # 8. Защита от потери управляемости канала «Назад» при замыкании проводов ДУ
        if self.__subtest_62_63():
            pass
        else:
            return False
        ctrl_kl.ctrl_relay('KL11', True)
        in_a1, in_a2 = self.__inputs_a()
        if in_a1 == False and in_a2 == False:
            pass
        elif in_a1 == True:
            mysql_conn.mysql_error(190)
            mysql_conn.mysql_ins_result("неисправен", '8')
            return False
        elif in_a2 == True:
            mysql_conn.mysql_error(191)
            mysql_conn.mysql_ins_result("неисправен", '8')
            return False
        mysql_conn.mysql_ins_result("исправен", '8')
        ctrl_kl.ctrl_relay('KL12', False)
        ctrl_kl.ctrl_relay('KL25', False)
        ctrl_kl.ctrl_relay('KL11', False)
        # Тест 9. Защита от потери управляемости канала «Назад» при обрыве проводов ДУ
        if self.__subtest_62_63():
            pass
        else:
            return False
        ctrl_kl.ctrl_relay('KL12', False)
        in_a1, in_a2 = self.__inputs_a()
        if in_a1 == False and in_a2 == False:
            pass
        elif in_a1 == True:
            mysql_conn.mysql_error(192)
            mysql_conn.mysql_ins_result("неисправен", '9')
            return False
        elif in_a2 == True:
            mysql_conn.mysql_error(193)
            mysql_conn.mysql_ins_result("неисправен", '9')
            return False
        mysql_conn.mysql_ins_result("исправен", '9')
        ctrl_kl.ctrl_relay('KL25', False)
        # Тест 10. Блокировка включения блока при снижении сопротивления изоляции контролируемого присоединения
        resist.resist_kohm(30)
        ctrl_kl.ctrl_relay('KL12', True)
        in_a1, in_a2 = self.__inputs_a()
        if in_a1 == False and in_a2 == False:
            pass
        elif in_a1 == True:
            mysql_conn.mysql_error(194)
            mysql_conn.mysql_ins_result("неисправен", '10')
            return False
        elif in_a2 == True:
            mysql_conn.mysql_error(195)
            mysql_conn.mysql_ins_result("неисправен", '10')
            return False
        mysql_conn.mysql_ins_result("исправен", '10')
        ctrl_kl.ctrl_relay('KL12', False)
        # Тест 11. Проверка работы режима «Проверка БРУ»
        ctrl_kl.ctrl_relay('KL22', True)
        ctrl_kl.ctrl_relay('KL12', True)
        in_a1, in_a2 = self.__inputs_a()
        if in_a1 == False and in_a2 == False:
            pass
        elif in_a1 == True:
            mysql_conn.mysql_error(196)
            mysql_conn.mysql_ins_result("неисправен", '11')
            return False
        elif in_a2 == True:
            mysql_conn.mysql_error(197)
            mysql_conn.mysql_ins_result("неисправен", '11')
            return False
        mysql_conn.mysql_ins_result("исправен", '11')
        return True
    
    def __subtest_22_23(self):
        # 2.2. Включение блока от кнопки «Пуск» режима «Вперёд»
        resist.resist_ohm(0)
        ctrl_kl.ctrl_relay('KL12', True)
        in_a1, in_a2 = self.__inputs_a()
        if in_a1 == True and in_a2 == False:
            pass
        elif in_a1 == False:
            mysql_conn.mysql_error(170)
            mysql_conn.mysql_ins_result("неисправен", '2')
            return False
        elif in_a2 == True:
            mysql_conn.mysql_error(171)
            mysql_conn.mysql_ins_result("неисправен", '2')
            return False
        # 2.3. Проверка удержания блока во включенном состоянии при подключении Rш пульта управления режима «Вперёд»:
        ctrl_kl.ctrl_relay('KL25', True)
        in_a1, in_a2 = self.__inputs_a()
        if in_a1 == True and in_a2 == False:
            return True
        elif in_a1 == False:
            mysql_conn.mysql_error(172)
            mysql_conn.mysql_ins_result("неисправен", '2')
            return False
        elif in_a2 == True:
            mysql_conn.mysql_error(173)
            mysql_conn.mysql_ins_result("неисправен", '2')
            return False
    
    def __subtest_62_63(self):
        # 6.2. Включение блока от кнопки «Пуск» режима «Назад»
        resist.resist_ohm(0)
        sleep(1)
        ctrl_kl.ctrl_relay('KL12', True)
        in_a1, in_a2 = self.__inputs_a()
        if in_a1 == False and in_a2 == True:
            pass
        elif in_a1 == True:
            mysql_conn.mysql_error(182)
            mysql_conn.mysql_ins_result("неисправен", '6')
            return False
        elif in_a2 == False:
            mysql_conn.mysql_error(183)
            mysql_conn.mysql_ins_result("неисправен", '6')
            return False
        # 6.3. Проверка удержания блока во включенном состоянии
        # при подключении Rш пульта управления режима «Назад»:
        ctrl_kl.ctrl_relay('KL25', True)
        in_a1, in_a2 = self.__inputs_a()
        if in_a1 == False and in_a2 == True:
            return True
        elif in_a1 == True:
            mysql_conn.mysql_error(184)
            mysql_conn.mysql_ins_result("неисправен", '6')
            return False
        elif in_a2 == False:
            mysql_conn.mysql_error(185)
            mysql_conn.mysql_ins_result("неисправен", '6')
            return False
    
    @staticmethod
    def __inputs_a():
        in_a1 = read_mb.read_discrete(1)
        in_a2 = read_mb.read_discrete(2)
        return in_a1, in_a2


if __name__ == '__main__':
    try:
        test_bur_pmvir = TestBURPMVIR()
        if test_bur_pmvir.st_test_bur_pmvir():
            mysql_conn.mysql_block_good()
            my_msg('Блок исправен')
        else:
            mysql_conn.mysql_block_bad()
            my_msg('Блок неисправен')
    except OSError:
        my_msg("ошибка системы")
    except SystemError:
        my_msg("внутренняя ошибка")
    finally:
        reset.reset_all()
        exit()
