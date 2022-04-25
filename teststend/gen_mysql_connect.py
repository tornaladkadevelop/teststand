#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
класс mysql для чтения и записи в БД
"""

__all__ = ['MySQLConnect']

import mysql.connector
from datetime import datetime


class MySQLConnect(object):

    def __init__(self):
        self.host = 'localhost'
        self.user = 'simple_user'
        self.password = 'user'
        self.database = 'simple_database'
        self.auth_plugin = 'mysql_native_password'
        self.mysql_err = mysql.connector.Error

    def mysql_ins_result(self, my_result, num_test):
        self.my_result = my_result
        self.num_test = num_test
        try:
            conn = mysql.connector.connect(host=self.host, user=self.user, password=self.password,
                                           database=self.database, auth_plugin=self.auth_plugin)
            c = conn.cursor()
            retrive = ('UPDATE simple_database.test_results SET result_text = "' + self.my_result +
                       '" WHERE id_test_result = "' + self.num_test + '"')
            c.execute(retrive)
            conn.commit()
            conn.close()
        except self.mysql_err:
            print('Error! Ошибка связи с базой данных MySQL.')

    def mysql_pmz_result(self, my_result):
        self.my_result = my_result
        sql = 'insert into pmz_result(pmz_set, pmz_proc, pmz_time) values(%s, %s, %s)'

        try:
            conn = mysql.connector.connect(host=self.host, user=self.user, password=self.password,
                                           database=self.database, auth_plugin=self.auth_plugin)
            c = conn.cursor()
            aquery = 'TRUNCATE simple_database.pmz_result;'
            c.execute(aquery)
            c.executemany(sql, my_result)
            conn.commit()
            print(c.rowcount, "\trecords inserted!")
            conn.close()
        except self.mysql_err:
            print('result: \t', my_result)
            print('Error! Ошибка связи с базой данных MySQL.')

    def mysql_tzp_result(self, my_result):
        self.my_result = my_result
        sql = 'insert into tzp_result(tzp_set, tzp_proc, tzp_time) values(%s, %s, %s)'

        try:
            conn = mysql.connector.connect(host=self.host, user=self.user, password=self.password,
                                           database=self.database, auth_plugin=self.auth_plugin)
            c = conn.cursor()
            aquery = 'TRUNCATE simple_database.tzp_result;'
            c.execute(aquery)
            c.executemany(sql, self.my_result)
            conn.commit()
            print(c.rowcount, "\trecords inserted!")
            conn.close()
        except self.mysql_err:
            print('Error! Ошибка связи с базой данных MySQL.')

    def mysql_umz_result(self, my_result):
        self.my_result = my_result
        sql = 'insert into umz_result(umz_set_ab, umz_proc_ab, umz_time_ab, umz_set_vg, umz_proc_vg, umz_time_vg) ' + \
              'values(%s, %s, %s, %s, %s, %s)'
        try:
            conn = mysql.connector.connect(host=self.host, user=self.user, password=self.password,
                                           database=self.database, auth_plugin=self.auth_plugin)
            c = conn.cursor()
            aquery = 'TRUNCATE simple_database.umz_result;'
            c.execute(aquery)
            c.executemany(sql, self.my_result)
            conn.commit()
            print(c.rowcount, "records inserted!")
            conn.close()
        except self.mysql_err:
            print('Error! Ошибка связи с базой данных MySQL.')

    def mysql_ubtz_btz_result(self, my_result):
        self.my_result = my_result
        sql = 'insert into ubtz_btz_result(ubtz_btz_ust, ubtz_btz_time) ' + 'values(%s, %s)'
        try:
            conn = mysql.connector.connect(host=self.host, user=self.user, password=self.password,
                                           database=self.database, auth_plugin=self.auth_plugin)
            c = conn.cursor()
            aquery = 'TRUNCATE simple_database.ubtz_btz_result;'
            c.execute(aquery)
            c.executemany(sql, self.my_result)
            conn.commit()
            print(c.rowcount, "records inserted!")
            conn.close()
        except self.mysql_err:
            print('Error! Ошибка связи с базой данных MySQL.')

    def mysql_ubtz_tzp_result(self, my_result):
        self.my_result = my_result
        sql = 'insert into ubtz_tzp_result(ubtz_tzp_ust, ubtz_tzp_time) ' + 'values(%s, %s)'
        try:
            conn = mysql.connector.connect(host=self.host, user=self.user, password=self.password,
                                           database=self.database, auth_plugin=self.auth_plugin)
            c = conn.cursor()
            aquery = 'TRUNCATE simple_database.ubtz_tzp_result;'
            c.execute(aquery)
            c.executemany(sql, self.my_result)
            conn.commit()
            print(c.rowcount, "records inserted!")
            conn.close()
        except self.mysql_err:
            print('Error! Ошибка связи с базой данных MySQL.')

    def mysql_connect(self, request: str):
        self.request = request
        try:
            conn = mysql.connector.connect(host=self.host, user=self.user, password=self.password,
                                           database=self.database, auth_plugin=self.auth_plugin)
            c = conn.cursor()
            c.execute(self.request)
            conn.commit()
            conn.close()
        except self.mysql_err:
            print('Error! Ошибка связи с базой данных MySQL.')

    def mysql_block_bad(self):
        upd_bad = ('UPDATE simple_database.python_message SET pyth_block_bad = 1 WHERE id_pyth_mes = 1')
        upd_good = ('UPDATE simple_database.python_message SET pyth_block_good = 0 WHERE id_pyth_mes = 1')
        self.mysql_connect(upd_bad)
        self.mysql_connect(upd_good)

    def mysql_block_good(self):
        upd_bad = ('UPDATE simple_database.python_message SET pyth_block_bad = 0 WHERE id_pyth_mes = 1')
        upd_good = ('UPDATE simple_database.python_message SET pyth_block_good = 1 WHERE id_pyth_mes = 1')
        self.mysql_connect(upd_bad)
        self.mysql_connect(upd_good)

    def mysql_error(self, n_err: int):
        self.n_err = n_err
        upd = ('UPDATE simple_database.python_message SET pyth_error = "' + str(n_err) + '" WHERE id_pyth_mes = 1')
        self.mysql_connect(upd)

    def mysql_add_message(self, mess: str):
        self.mess = mess
        mytime = datetime.now()
        self.mess = self.mess[:170]
        request = "INSERT INTO simple_database.messages_alg(mess_alg_time, mess_text) " \
                  "VALUES('" + str(mytime) + "','" + self.mess + "'); "
        print(request)
        try:
            conn = mysql.connector.connect(host=self.host, user=self.user, password=self.password,
                                           database=self.database, auth_plugin=self.auth_plugin)
            c = conn.cursor()
            c.execute(request)
            conn.commit()
            conn.close()
        except self.mysql_err:
            print('Error! Ошибка связи с базой данных MySQL.')

    def progress_level(self, level: float):
        level = f'{level:.1f}'
        upd = f'UPDATE simple_database.progress SET level_progress = {level} WHERE (id_pro = 1);'
        self.mysql_connect(upd)
