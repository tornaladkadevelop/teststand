#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Алгоритм проверки
Тип блока Производитель
БУР ПМВИР (пускатель)	Нет производителя

"""

import sys
import logging

from time import sleep

from gen_func_utils import *
from my_msgbox import *
from gen_mb_client import *
from gen_mysql_connect import *
from gen_subtest import SubtestA1A2

__all__ = ["TestBURPMVIR"]


class TestBURPMVIR(object):

    def __init__(self):
        self.__resist = Resistor()
        self.__read_mb = ReadMB()
        self.__ctrl_kl = CtrlKL()
        self.__mysql_conn = MySQLConnect()
        # self.__fault = Bug(True)
        self.subtest = SubtestA1A2()

        logging.basicConfig(filename="C:\Stend\project_class\log\TestBURPMVIR.log",
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
        if self.subtest.subtest_inp_a1a2(test_num=1, subtest_num=1.0, err_code_a1=166, err_code_a2=167,
                                         position_a1=False, position_a2=False):
            return True
        return False

    def st_test_20(self) -> bool:
        """
        Тест 2. Проверка включения/выключения блока от кнопки «Пуск/Стоп» в режиме «Вперёд».
        """
        self.__ctrl_kl.ctrl_relay('KL21', True)
        if self.subtest.subtest_inp_a1a2(test_num=2, subtest_num=2.0, err_code_a1=168, err_code_a2=169,
                                         position_a1=False, position_a2=False):
            if self.subtest.subtest_a_bur(test_num=2, subtest_num=2.1, forward=True):
                if self.subtest.subtest_b_bur(test_num=2, subtest_num=2.2, forward=True):
                    # 2.4. Выключение блока от кнопки «Стоп» режима «Вперёд»
                    self.__ctrl_kl.ctrl_relay('KL12', False)
                    sleep(1)
                    if self.subtest.subtest_inp_a1a2(test_num=2, subtest_num=2.3,
                                                     err_code_a1=174, err_code_a2=175,
                                                     position_a1=False, position_a2=False):
                        self.__ctrl_kl.ctrl_relay('KL25', False)
                        return True
        return False

    def st_test_30(self) -> bool:
        """
        3. Отключение контакта «Вперёд» при увеличении сопротивления цепи заземления
        """
        if self.subtest.subtest_a_bur(test_num=3, subtest_num=3.0, forward=True):
            if self.subtest.subtest_b_bur(test_num=3, subtest_num=3.1, forward=True):
                # Формирование 100 Ом
                self.__resist.resist_0_to_100_ohm()
                sleep(1)
                if self.subtest.subtest_inp_a1a2(test_num=3, subtest_num=3.2, err_code_a1=176, err_code_a2=177,
                                                 position_a1=False, position_a2=False):
                    self.__ctrl_kl.ctrl_relay('KL12', False)
                    self.__ctrl_kl.ctrl_relay('KL25', False)
                    return True
        return False

    def st_test_40(self) -> bool:
        """
        4. Защита от потери управляемости канала «Вперёд» при замыкании проводов ДУ
        """
        if self.subtest.subtest_a_bur(test_num=4, subtest_num=4.0, forward=True):
            if self.subtest.subtest_b_bur(test_num=4, subtest_num=4.1, forward=True):
                self.__ctrl_kl.ctrl_relay('KL11', True)
                sleep(2)
                if self.subtest.subtest_inp_a1a2(test_num=4, subtest_num=4.2, err_code_a1=178, err_code_a2=179,
                                                 position_a1=False, position_a2=False):
                    self.__ctrl_kl.ctrl_relay('KL12', False)
                    self.__ctrl_kl.ctrl_relay('KL25', False)
                    self.__ctrl_kl.ctrl_relay('KL11', False)
                    return True
        return False

    def st_test_50(self) -> bool:
        """
        Тест 5. Защита от потери управляемости канала «Вперёд» при обрыве проводов ДУ
        """
        if self.subtest.subtest_a_bur(test_num=5, subtest_num=5.0, forward=True):
            if self.subtest.subtest_b_bur(test_num=5, subtest_num=5.1, forward=True):
                self.__ctrl_kl.ctrl_relay('KL12', False)
                sleep(2)
                if self.subtest.subtest_inp_a1a2(test_num=5, subtest_num=5.2, err_code_a1=180, err_code_a2=181,
                                                 position_a1=False, position_a2=False):
                    self.__ctrl_kl.ctrl_relay('KL25', False)
                    return True
        return False

    def st_test_60(self) -> bool:
        """
        Тест 6. Проверка включения/выключения блока от кнопки «Пуск/Стоп» в режиме «Назад».
        Переключение в режим ДУ «Назад»	KL26 - ВКЛ
        """
        self.__ctrl_kl.ctrl_relay('KL26', True)
        sleep(2)
        if self.subtest.subtest_inp_a1a2(test_num=6, subtest_num=6.0, err_code_a1=168, err_code_a2=169,
                                         position_a1=False, position_a2=False):
            if self.subtest.subtest_a_bur(test_num=6, subtest_num=6.1, back=True):
                if self.subtest.subtest_b_bur(test_num=6, subtest_num=6.2, back=True):
                    # 6.4. Выключение блока от кнопки «Стоп» режима «Назад»
                    self.__ctrl_kl.ctrl_relay('KL12', False)
                    sleep(2)
                    if self.subtest.subtest_inp_a1a2(test_num=6, subtest_num=6.3, err_code_a1=186, err_code_a2=187,
                                                     position_a1=False, position_a2=False):
                        self.__ctrl_kl.ctrl_relay('KL25', False)
                        return True
        return False

    def st_test_70(self) -> bool:
        """
        7. Отключение контакта «Назад» при увеличении сопротивления цепи заземления
        """
        if self.subtest.subtest_a_bur(test_num=7, subtest_num=7.0, back=True):
            if self.subtest.subtest_b_bur(test_num=7, subtest_num=7.1, back=True):
                self.__resist.resist_0_to_100_ohm()
                sleep(2)
                if self.subtest.subtest_inp_a1a2(test_num=7, subtest_num=7.2, err_code_a1=188, err_code_a2=189,
                                                 position_a1=False, position_a2=False):
                    self.__ctrl_kl.ctrl_relay('KL12', False)
                    self.__ctrl_kl.ctrl_relay('KL25', False)
                    return True
        return False

    def st_test_80(self) -> bool:
        """
        8. Защита от потери управляемости канала «Назад» при замыкании проводов ДУ
        """
        if self.subtest.subtest_a_bur(test_num=8, subtest_num=8.0, back=True):
            if self.subtest.subtest_b_bur(test_num=8, subtest_num=8.1, back=True):
                self.__ctrl_kl.ctrl_relay('KL11', True)
                sleep(2)
                if self.subtest.subtest_inp_a1a2(test_num=8, subtest_num=8.2, err_code_a1=190, err_code_a2=191,
                                                 position_a1=False, position_a2=False):
                    self.__ctrl_kl.ctrl_relay('KL12', False)
                    self.__ctrl_kl.ctrl_relay('KL25', False)
                    self.__ctrl_kl.ctrl_relay('KL11', False)
                    return True
        return False

    def st_test_90(self) -> bool:
        """
        Тест 9. Защита от потери управляемости канала «Назад» при обрыве проводов ДУ
        """
        if self.subtest.subtest_a_bur(test_num=9, subtest_num=9.0, back=True):
            if self.subtest.subtest_b_bur(test_num=9, subtest_num=9.1, back=True):
                self.__ctrl_kl.ctrl_relay('KL12', False)
                sleep(2)
                if self.subtest.subtest_inp_a1a2(test_num=9, subtest_num=9.2, err_code_a1=192, err_code_a2=193,
                                                 position_a1=False, position_a2=False):
                    self.__ctrl_kl.ctrl_relay('KL25', False)
                    return True
        return False

    def st_test_100(self) -> bool:
        """
        Тест 10. Блокировка включения блока при снижении сопротивления изоляции контролируемого присоединения
        """
        self.__resist.resist_kohm(30)
        sleep(2)
        self.__ctrl_kl.ctrl_relay('KL12', True)
        sleep(2)
        if self.subtest.subtest_inp_a1a2(test_num=10, subtest_num=10.0, err_code_a1=194, err_code_a2=195,
                                         position_a1=False, position_a2=False):
            self.__ctrl_kl.ctrl_relay('KL12', False)
            return True
        return False

    def st_test_101(self) -> bool:
        """
        Тест 11. Проверка работы режима «Проверка БРУ»
        """
        self.__ctrl_kl.ctrl_relay('KL22', True)
        self.__ctrl_kl.ctrl_relay('KL12', True)
        sleep(2)
        if self.subtest.subtest_inp_a1a2(test_num=10, subtest_num=10.1, err_code_a1=196, err_code_a2=197,
                                         position_a1=False, position_a2=False):
            return True
        return False

    def st_test_bur_pmvir(self) -> bool:
        if self.st_test_10():
            if self.st_test_20():
                if self.st_test_30():
                    if self.st_test_40():
                        if self.st_test_50():
                            if self.st_test_60():
                                if self.st_test_70():
                                    if self.st_test_80():
                                        if self.st_test_90():
                                            if self.st_test_100():
                                                if self.st_test_101():
                                                    return True
        return False


if __name__ == '__main__':
    test_bur_pmvir = TestBURPMVIR()
    reset_test_bur_pmvir = ResetRelay()
    mysql_conn_bur_pmvir = MySQLConnect()
    fault = Bug(True)
    try:
        if test_bur_pmvir.st_test_bur_pmvir():
            mysql_conn_bur_pmvir.mysql_block_good()
            my_msg('Блок исправен', 'green')
        else:
            mysql_conn_bur_pmvir.mysql_block_bad()
            my_msg('Блок неисправен', 'red')
    except OSError:
        my_msg("ошибка системы", 'red')
    except SystemError:
        my_msg("внутренняя ошибка", 'red')
    except ModbusConnectException as mce:
        fault.debug_msg(mce, 'red')
        my_msg(f'{mce}', 'red')
    finally:
        reset_test_bur_pmvir.reset_all()
        sys.exit()
