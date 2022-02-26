#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Алгоритм проверки

Тип блока	Производитель
МКЗП-6-4Ш	ЗМТ «Энергия»
"""

from sys import exit
from time import sleep
from gen_func_procedure import *
from gen_func_utils import *
from my_msgbox import *
from gen_mb_client import *
from gen_mysql_connect import *


__all__ = ["TestMKZP6"]

reset = ResetRelay()
proc = Procedure()
resist = Resistor()
read_mb = ReadMB()
ctrl_kl = CtrlKL()
mysql_conn = MySQLConnect()
fault = Bug(True)

ust_1 = 45.1
ust_2 = 15.0


class TestMKZP6(object):
    def __init__(self):
        pass

    def st_test_mkzp_6_4sh(self):
        # Сообщение	Убедитесь в отсутствии других блоков или соединительных кабелей в панели разъемов D
        #Подключите в разъемы X33, X34, расположенные на панели разъемов D соединительные кабеля
        # для проверки блока МКЗП-6-4Ш
        msg_1 = "Убедитесь в отсутствии других блоков или соединительных кабелей в панели разъемов D " \
                "Подключите в разъемы X33, X34, расположенные на панели разъемов D соединительные кабеля " \
                "для проверки блока МКЗП-6-4Ш"
        if my_msg(msg_1):
            pass
        else:
            return False
        fault.debug_msg('тест 1.1', 3)
        mysql_conn.mysql_ins_result("идёт тест 1.1", '1')
        meas_volt_ust = proc.procedure_1_21_31()
        if meas_volt_ust != False:
            pass
        else:
            fault.debug_msg('неисправен TV1', 1)
            mysql_conn.mysql_ins_result("неисправен TV1", '1')
            return False
        ctrl_kl.ctrl_relay('KL73', True)
        sleep(5)
        ctrl_kl.ctrl_relay('KL90', True)
        sleep(5)
        ctrl_kl.ctrl_relay('KL63', True)
        meas_volt = read_mb.read_analog()
        fault.debug_msg(f'измеренное напряжение:\t{meas_volt}', 2)
        if 0.8 * meas_volt_ust <= meas_volt <= 1.0 * meas_volt_ust:
            pass
        else:
            mysql_conn.mysql_ins_result('неисправен', '1')
            reset.sbros_kl63_proc_1_21_31()
            return False
        reset.sbros_kl63_proc_1_21_31()
        fault.debug_msg('тест 1.2', 3)
        mysql_conn.mysql_ins_result("идёт тест 1.2", '1')
        coef_volt = proc.procedure_1_22_32()
        if coef_volt != False:
            pass
        else:
            mysql_conn.mysql_ins_result('неисправен', '1')
            return False
        reset.stop_procedure_32()
        ctrl_kl.ctrl_relay('KL100', True)
        sleep(0.3)
        ctrl_kl.ctrl_relay('KL21', True)
        sleep(0.3)
        ctrl_kl.ctrl_relay('KL36', True)
        sleep(0.3)
        ctrl_kl.ctrl_relay('KL88', True)
        sleep(2.5)
        ctrl_kl.ctrl_relay('KL66', True)
        sleep(1)
        ctrl_kl.ctrl_relay('KL92', True)
        fault.debug_msg('тест 1.3', 3)
        mysql_conn.mysql_ins_result("идёт тест 1.3", '1')
        # Сообщение	Нажмите несколько раз кнопку «SB5», расположенную на панели D до появления окна со временем
        msg_2 = "Нажмите несколько раз кнопку «SB5», расположенную на панели D до появления окна со временем"
        # Сообщение	Если на дисплее блока горят надписи «ОТКЛ» и «ПИТАНИЕ» нажмите кнопку «ОК».
        # Иначе, нажмите кнопку  «ОТМЕНА»
        msg_3 = "Если на дисплее блока горят надписи «ОТКЛ» и «ПИТАНИЕ» нажмите кнопку «ОК». " \
                "Иначе, нажмите кнопку  «ОТМЕНА»"
        # При нажатии кнопки «ОТМЕНА» выдаем сообщение: «Блок не переходит в исходное состояние».
        msg_4 = "Блок не переходит в исходное состояние"
        if my_msg(msg_2):
            if my_msg(msg_3):
                pass
            else:
                fault.debug_msg('тест 1.4 неисправен', 1)
                mysql_conn.mysql_ins_result("неисправен", '1')
                my_msg(msg_4)
                return False
        else:
            return False
        sleep(10)
        ctrl_kl.ctrl_relay('KL99', True)
        sleep(5)
        fault.debug_msg('тест 1.4', 3)
        mysql_conn.mysql_ins_result("идёт тест 1.4", '1')
        # Сообщение	Если на дисплее загорелась надпись «ВКЛ» и погасла надпись «ОТКЛ» нажмите кнопку «ОК».
        # Иначе нажмите кнопку «ОТМЕНА»
        msg_5 = "Если на дисплее загорелась надпись «ВКЛ» и погасла надпись «ОТКЛ» нажмите кнопку «ОК». " \
                "Иначе нажмите кнопку «ОТМЕНА»"
        # Блок не исправен. Блок не включается от кнопки «ПУСК»
        msg_6 = "Блок не исправен. Блок не включается от кнопки «ПУСК»"
        if my_msg(msg_5):
            pass
        else:
            fault.debug_msg('тест 1.5 неисправен', 1)
            mysql_conn.mysql_ins_result("неисправен", '1')
            my_msg(msg_6)
            return False
        sleep(5)
        ctrl_kl.ctrl_relay('KL99', False)
        sleep(5)
        fault.debug_msg('тест 1.5', 3)
        mysql_conn.mysql_ins_result("идёт тест 1.5", '1')
        # Сообщение	Если на дисплее погасла надпись «ВКЛ» и загорелась надпись «ОТКЛ» нажмите кнопку «ОК».
        # Иначе нажмите кнопку «ОТМЕНА»
        msg_7 = "Если на дисплее погасла надпись «ВКЛ» и загорелась надпись «ОТКЛ» нажмите кнопку «ОК». " \
                "Иначе нажмите кнопку «ОТМЕНА»"
        # При нажатии кнопки «ОТМЕНА» выдаем сообщение: «Блок не исправен. Блок не выключается от кнопки «СТОП»»..
        msg_8 = "Блок не исправен. Блок не выключается от кнопки «СТОП»"
        if my_msg(msg_7):
            pass
        else:
            fault.debug_msg('тест 1.6 неисправен', 1)
            mysql_conn.mysql_ins_result("неисправен", '1')
            my_msg(msg_8)
            return False
        fault.debug_msg('тест 1 пройден', 4)
        mysql_conn.mysql_ins_result("исправен", '1')
        # Тест 2. Контроль изоляции
        fault.debug_msg('тест 2.1', 3)
        mysql_conn.mysql_ins_result("идёт тест 2.1", '2')
        sleep(5)
        ctrl_kl.ctrl_relay('KL99', True)
        sleep(5)
        # Сообщение	Если на дисплее загорелась надпись «ВКЛ» и погасла надпись «ОТКЛ» нажмите кнопку «ОК».
        # Иначе нажмите кнопку «ОТМЕНА»
        msg_9 = "Если на дисплее загорелась надпись «ВКЛ» и погасла надпись «ОТКЛ» нажмите кнопку «ОК». " \
                "Иначе нажмите кнопку «ОТМЕНА»"
        # При нажатии кнопки «ОТМЕНА» выдаем сообщение: «Тест 2 не пройден. Блок не исправен.
        # Блок не включается от кнопки «ПУСК»».
        msg_10 = "Тест 2 не пройден. Блок не исправен. Блок не включается от кнопки «ПУСК»"
        if my_msg(msg_9):
            pass
        else:
            fault.debug_msg('тест 2.1 неисправен', 1)
            mysql_conn.mysql_ins_result("неисправен", '2')
            my_msg(msg_10)
            return False
        ctrl_kl.ctrl_relay('KL98', True)
        sleep(3)
        fault.debug_msg('тест 2.2', 3)
        mysql_conn.mysql_ins_result("идёт тест 2.2", '2')
        # Сообщение	Если на дисплее стали активны надписи АВАРИЯ, ВКЛ и на дисплее появилась надпись
        # «НЕИСПРАВНОСТЬ БКИ» нажмите кнопку «ОК».
        # Иначе нажмите кнопку «ОТМЕНА»
        msg_11 = "Если на дисплее стали активны надписи АВАРИЯ, ВКЛ и на дисплее появилась надпись " \
                 "«НЕИСПРАВНОСТЬ БКИ» нажмите кнопку «ОК». Иначе нажмите кнопку «ОТМЕНА»"
        # При нажатии кнопки «ОТМЕНА» выдаем сообщение:
        # «Тест 2 не пройден. Блок не исправен. Блок не контролирует неисправность «БКИ»».
        msg_12 = "Тест 2 не пройден. Блок не исправен. Блок не контролирует неисправность «БКИ»"
        if my_msg(msg_11):
            pass
        else:
            fault.debug_msg('тест 2.2 неисправен', 1)
            mysql_conn.mysql_ins_result("неисправен", '2')
            my_msg(msg_12)
            return False
        ctrl_kl.ctrl_relay('KL98', False)
        fault.debug_msg('тест 2.3', 3)
        mysql_conn.mysql_ins_result("идёт тест 2.3", '2')
        # Сообщение	Нажмите кнопку «SB5» (Сброс), расположенную на панели D
        msg_13 = "Нажмите кнопку «SB5» (Сброс), расположенную на панели D"
        if my_msg(msg_13):
            pass
        else:
            return False
        sleep(5)
        ctrl_kl.ctrl_relay('KL97', True)
        sleep(1.5)
        fault.debug_msg('тест 2.4', 3)
        mysql_conn.mysql_ins_result("идёт тест 2.4", '2')
        # Сообщение	Если на дисплее стали активны надписи АВАРИЯ, УТЕЧКА, ВКЛ и на дисплее появилась надпись
        # «Сработала защита УТЕЧКА» нажмите кнопку «ОК».
        # Иначе нажмите кнопку «ОТМЕНА»
        msg_14 = "Если на дисплее стали активны надписи АВАРИЯ, УТЕЧКА, ВКЛ и на дисплее появилась надпись " \
                 "«Сработала защита УТЕЧКА» нажмите кнопку «ОК». Иначе нажмите кнопку «ОТМЕНА»"
        # При нажатии кнопки «ОТМЕНА» выдаем сообщение:
        # «Тест 2 не пройден. Блок не исправен. Блок не контролирует «Аварию БКИ»».
        msg_15 = "Тест 2 не пройден. Блок не исправен. Блок не контролирует «Аварию БКИ»"
        if my_msg(msg_14):
            pass
        else:
            fault.debug_msg('тест 2.4 неисправен', 1)
            mysql_conn.mysql_ins_result("неисправен", '2')
            my_msg(msg_15)
            return False
        sleep(1.5)
        ctrl_kl.ctrl_relay('KL97', False)
        sleep(5)
        fault.debug_msg('тест 2 пройден', 3)
        mysql_conn.mysql_ins_result("исправен", '2')
        if my_msg(msg_13):
            pass
        else:
            return False
        # Тест 3. Работа защиты минимального напряжения
        fault.debug_msg('тест 3.1', 3)
        mysql_conn.mysql_ins_result("идёт тест 3.1", '3')
        ctrl_kl.ctrl_relay('KL69', True)
        sleep(1)
        # Сообщение	Если на дисплее стали активны надписи ПИТАНИЕ, ОТКЛ и на дисплее появилась надпись
        # «Сработала защита ЗМН» нажмите кнопку «ОК».
        # Иначе нажмите кнопку «ОТМЕНА»
        msg_16 = "Если на дисплее стали активны надписи ПИТАНИЕ, ОТКЛ и на дисплее появилась надпись " \
                 "«Сработала защита ЗМН» нажмите кнопку «ОК». Иначе нажмите кнопку «ОТМЕНА»"
        # При нажатии кнопки «ОТМЕНА» выдаем сообщение: «Тест 3 не пройден. Блок не исправен. Не работает ЗМН»».
        msg_17 = "Тест 3 не пройден. Блок не исправен. Не работает ЗМН»"
        if my_msg(msg_16):
            pass
        else:
            fault.debug_msg('тест 3.1 неисправен', 1)
            mysql_conn.mysql_ins_result("неисправен", '3')
            my_msg(msg_17)
            return False
        ctrl_kl.ctrl_relay('KL69', False)
        sleep(1)
        fault.debug_msg('тест 3.2', 3)
        mysql_conn.mysql_ins_result("идёт тест 3.2", '3')
        # Сообщение	Нажмите кнопку «SB5» (Сброс), расположенную на панели D
        # Сообщение	Если на дисплее стали активны надписи ПИТАНИЕ, ОТКЛ нажмите кнопку «ОК».
        # Иначе нажмите кнопку «ОТМЕНА»
        msg_18 = "Если на дисплее стали активны надписи ПИТАНИЕ, ОТКЛ нажмите кнопку «ОК». " \
                 "Иначе нажмите кнопку «ОТМЕНА»"
        # Сообщение	Тест 3 не пройден. Блок не исправен. Не работает сброс ЗМН
        msg_19 = "Тест 3 не пройден. Блок не исправен. Не работает сброс ЗМН"
        if my_msg(msg_13):
            if my_msg(msg_18):
                pass
            else:
                fault.debug_msg('тест 3.2 неисправен', 1)
                mysql_conn.mysql_ins_result("неисправен", '3')
                my_msg(msg_19)
                return False
        else:
            return False
        fault.debug_msg('тест 3 пройден', 3)
        mysql_conn.mysql_ins_result("исправен", '3')
        # Тест 4. Проверка работоспособности токовой защиты
        fault.debug_msg('тест 4.1', 3)
        mysql_conn.mysql_ins_result("идёт тест 4.1", '4')
        # Сообщение	С помощью кнопок на лицевой панели установите следующие значения:
        # - I>>> 400А;
        msg_20 = "С помощью кнопок на лицевой панели установите следующие значения: - I>>> 400А;"
        if my_msg(msg_20):
            pass
        else:
            return False
        ctrl_kl.ctrl_relay('KL99', False)
        sleep(5)
        ctrl_kl.ctrl_relay('KL99', True)
        sleep(5)
        fault.debug_msg('тест 4.2', 3)
        mysql_conn.mysql_ins_result("идёт тест 4.2", '4')
        # Сообщение	Если на дисплее загорелась надпись «ВКЛ» и погасла надпись «ОТКЛ» нажмите кнопку «ОК».
        # Иначе нажмите кнопку «ОТМЕНА»
        msg_21 = "Если на дисплее загорелась надпись «ВКЛ» и погасла надпись «ОТКЛ» нажмите кнопку «ОК». " \
                 "Иначе нажмите кнопку «ОТМЕНА»"
        # При нажатии кнопки «ОТМЕНА» выдаем сообщение: «Тест 4 не пройден.
        # Блок не исправен. Блок не включается от кнопки «ПУСК»».
        msg_22 = "Тест 4 не пройден. Блок не исправен. Блок не включается от кнопки «ПУСК»"
        if my_msg(msg_21):
            pass
        else:
            fault.debug_msg('тест 4.2 неисправен', 1)
            mysql_conn.mysql_ins_result("неисправен", '4')
            my_msg(msg_22)
            return False
        if proc.procedure_1_24_34(setpoint_volt=ust_1, coef_volt=coef_volt):
            pass
        else:
            mysql_conn.mysql_ins_result('неисправен TV1', '4')
            return False
        sleep(1)
        ctrl_kl.ctrl_relay('KL63', True)
        sleep(0.5)
        ctrl_kl.ctrl_relay('KL63', False)
        reset.stop_procedure_3()
        # Сообщение	Если на дисплее стали активны надписи АВАРИЯ, ПИТАНИЕ, ОТКЛ и на дисплее появилась надпись
        # «Сработала защита МТЗ» нажмите кнопку «ОК».
        # Иначе нажмите кнопку «ОТМЕНА»
        msg_23 = "Если на дисплее стали активны надписи АВАРИЯ, ПИТАНИЕ, ОТКЛ и на дисплее появилась надпись " \
                 "«Сработала защита МТЗ» нажмите кнопку «ОК». Иначе нажмите кнопку «ОТМЕНА»"
        # При нажатии кнопки «ОТМЕНА» выдаем сообщение: «Тест 4 не пройден. Блок не исправен.
        # Блок не работает в режиме МТЗ»
        msg_24 = "Тест 4 не пройден. Блок не исправен. Блок не работает в режиме МТЗ»"
        if my_msg(msg_23):
            pass
        else:
            fault.debug_msg('тест 4.3 неисправен', 1)
            mysql_conn.mysql_ins_result("неисправен", '4')
            my_msg(msg_24)
            return False
        # Сообщение	Нажмите кнопку «SB5» (Сброс), расположенную на панели D
        if my_msg(msg_13):
            pass
        else:
            return False
        fault.debug_msg('тест 4 пройден', 3)
        mysql_conn.mysql_ins_result("исправен", '4')
        # Тест 5. Проверка работоспособности защит от несимметрии фаз
        fault.debug_msg('тест 5.1', 3)
        mysql_conn.mysql_ins_result("идёт тест 5.1", '5')
        ctrl_kl.ctrl_relay('KL99', False)
        sleep(5)
        ctrl_kl.ctrl_relay('KL99', True)
        sleep(5)
        # Сообщение	Если на дисплее загорелась надпись «ВКЛ» и погасла надпись «ОТКЛ» нажмите кнопку «ОК».
        # Иначе нажмите кнопку «ОТМЕНА»
        msg_25 = "Если на дисплее загорелась надпись «ВКЛ» и погасла надпись «ОТКЛ» нажмите кнопку «ОК». " \
                 "Иначе нажмите кнопку «ОТМЕНА»"
        # При нажатии кнопки «ОТМЕНА» выдаем сообщение:
        # «Тест 5 не пройден. Блок не исправен. Блок не включается от кнопки «ПУСК»».
        msg_26 = "Тест 5 не пройден. Блок не исправен. Блок не включается от кнопки «ПУСК»"
        if my_msg(msg_25):
            pass
        else:
            fault.debug_msg('тест 5.1 неисправен', 1)
            mysql_conn.mysql_ins_result("неисправен", '5')
            my_msg(msg_26)
            return False
        fault.debug_msg('тест 5.2', 3)
        mysql_conn.mysql_ins_result("идёт тест 5.2", '5')
        if proc.procedure_1_24_34(setpoint_volt=ust_2, coef_volt=coef_volt):
            pass
        else:
            mysql_conn.mysql_ins_result('неисправен TV1', '5')
            return False
        sleep(1)
        ctrl_kl.ctrl_relay('KL63', True)
        sleep(0.1)
        ctrl_kl.ctrl_relay('KL81', True)
        sleep(15)
        ctrl_kl.ctrl_relay('KL63', False)
        reset.stop_procedure_3()
        # Сообщение	Если на дисплее стали активны надписи ПИТАНИЕ, ОТКЛ и на дисплее появилась надпись
        # «Сработала защита ЗНФ» нажмите кнопку «ОК».
        # Иначе нажмите кнопку «ОТМЕНА»
        msg_27 = "Если на дисплее стали активны надписи ПИТАНИЕ, ОТКЛ и на дисплее появилась надпись  " \
                 "«Сработала защита ЗНФ» нажмите кнопку «ОК». Иначе нажмите кнопку «ОТМЕНА»"
        # При нажатии кнопки «ОТМЕНА» выдаем сообщение:
        # «Тест 5 не пройден. Блок не исправен.Нет отключения от защиты ЗНФ»»
        msg_28 = "Тест 5 не пройден. Блок не исправен.Нет отключения от защиты ЗНФ»"
        if my_msg(msg_27):
            pass
        else:
            fault.debug_msg('тест 5.2 неисправен', 1)
            mysql_conn.mysql_ins_result("неисправен", '5')
            my_msg(msg_28)
            return False
        # Сообщение	Нажмите кнопку «SB5» (Сброс), расположенную на панели D
        if my_msg(msg_13):
            pass
        else:
            return False
        fault.debug_msg('тест 5 пройден', 4)
        mysql_conn.mysql_ins_result("исправен", '5')
        return True


if __name__ == '__main__':
    try:
        test_mkzp = TestMKZP6()
        if test_mkzp.st_test_mkzp_6_4sh():
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
