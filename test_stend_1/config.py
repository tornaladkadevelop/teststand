#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json

set_point_btz_3 = {
    'list_ust_tzp_num': (0.5, 0.6, 0.7, 0.8, 0.9, 1.0),
    'list_ust_tzp': (23.7, 28.6, 35.56, 37.4, 42.6, 47.3),
    'list_ust_pmz_num': (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11),
    'list_ust_pmz': (67.9, 86.4, 100.1, 117.2, 140.7, 146.4, 156.6, 164.2, 175.7, 183.7, 192.1),
    'ust_prov': 80.0
}

set_point_btz_t = {
    'list_ust_1': (25.7, 30.6, 37.56, 39.4, 44.6, 49.3),
    'list_ust_2': (67.9, 86.4, 100.1, 117.2, 140.7, 146.4, 156.6, 164.2, 175.7, 183.7, 192.1),
    'list_ust_1_num': (0.5, 0.6, 0.7, 0.8, 0.9, 1.0),
    'list_ust_2_num': (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11)
}

set_point_bkz_3mk = {
    'list_ust_tzp_num': (0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 1.1),
    'list_ust_tzp': (4.7, 6.2, 7.7, 9.2, 10.6, 12.0, 13.4, 14.7, 16.6),
    'list_ust_mtz_num': (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11),
    'list_ust_mtz': (21.8, 27.2, 32.7, 38.1, 43.6, 49.0, 54.4, 59.9, 65.3, 70.8, 76.2)
}

set_point_bmz_2 = {
    'list_ust_num': (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11),
    'list_ust': (32.2, 40.2, 48.2, 56.3, 64.3, 72.3, 80.4, 88.4, 98.5, 106.5, 114.5)
}

set_point_bmz_apsh_4 = {
    'list_ust_num': (1, 2, 3, 4, 5),
    'list_ust': (9.84, 16.08, 23.28, 34.44, 50.04)
}

set_point_buz_2 = {
    'ust_1': 75.8,
    'ust_2': 20.3
}

set_point_bzmp_2 = {
    'ust_1': 22.6,
    'ust_2': 15.0
}

set_point_bzmp_p1 = {
    'ust': 14.64
}

set_point_mmtz_d = {
    'list_ust_num': (10, 20, 30, 40, 50),
    'list_ust': (8.0, 16.5, 25.4, 31.9, 39.4),
    'list_num_yach_test_2': ("3", "4", "5", "6", "7"),
    'list_num_yach_test_3': ("9", "10", "11", "12", "13"),
    'list_ust_str': ('10', '20', '30', '40', '50')
}

set_point_mtz_5_v2_7 = {
    'list_ust_tzp_num': (0.4, 0.7, 1.0, 1.3, 1.6, 1.8, 2.0),
    'list_ust_tzp': (10.8, 18.8, 26.55, 34.05, 41.4, 46.2, 50.85),
    'list_ust_mtz_num': (2, 2.5, 3, 3.5, 4, 4.5, 5, 5.5, 6, 6.5, 7),
    'list_ust_mtz': (37.6, 46.8, 55.8, 64.8, 73.6, 82.4, 91.0, 99.6, 108, 116.4, 124.6),
    'ust_mtz': 30.0
}

set_point_mtz_5_v2_8 = {
    'list_ust_tzp_num': (0.8, 1, 2, 2.5, 3),
    'list_ust_tzp': (22.1, 27.6, 55.1, 68.9, 82.5),
    'list_ust_mtz_num': (2, 3, 4, 5, 6, 7, 8),
    'list_ust_mtz': (36.7, 55.0, 73.4, 91.7, 110.0, 128.4, 146.7),
    'ust_mtz': 20.0
}

set_point_mtz_5_v411 = {
    'list_ust_tzp_num': (0.8, 1, 1.5, 2, 2.25, 2.5, 3),
    'list_ust_tzp': (15.4, 19.3, 29.0, 38.5, 43.4, 48.2, 57.9),
    'list_ust_mtz_num': (2, 3, 4, 5, 6, 7, 8),
    'list_ust_mtz': (38.5, 57.8, 77.1, 96.3, 115.5, 134.8, 154.0),
    'ust_mtz': 30.0
}

set_point_pmz = {
    'list_ust_num': (1, 2, 3, 4, 5, 6, 7, 8, 9),
    'list_ust': (75.4, 92, 114, 125, 141, 156.4, 172, 182.4, 196)
}

set_point_tzp = {
    'list_ust_num': (0.5, 0.6, 0.7, 0.8, 0.9, 1.0),
    'list_ust': (25.7, 29.8, 34.3, 39.1, 43.7, 48.5)
}

set_point_umz = {
    'list_ust_num': (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11),
    'list_ust': (22.6, 27.1, 31.9, 36.5, 41.3, 46.4, 50.2, 54.7, 59.3, 63.8, 68.4)
}

set_point_ubtz = {
    'list_ust_bmz_num': (1, 2, 3, 4, 5, 6, 7),
    'list_ust_tzp_num': (1, 2, 3, 4, 5, 6, 7),
    'list_ust_bmz': (6.9, 13.8, 27.4, 41.1, 54.8, 68.5, 82.2),
    'list_ust_tzp': (11.2, 15.0, 18.7, 22.4, 26.2, 29.9, 33.6)
}

connect_mysql = {
    'host': 'localhost',
    'user': 'simple_user',
    'password': 'user',
    'database': 'simple_database',
    'auth_plugin': 'mysql_native_password'
}

connect_mysql_v2 = {
    'host': 'localhost',
    'user': 'simple_user',
    'password': 'user',
    'database': 'simple_database',
    'auth_plugin': 'mysql_native_password'
}

to_json = {'set_point_btz_3': set_point_btz_3,
           'set_point_btz_t': set_point_btz_t,
           'set_point_bkz_3mk': set_point_bkz_3mk,
           'set_point_bmz_2': set_point_bmz_2,
           'set_point_bmz_apsh_4': set_point_bmz_apsh_4,
           'set_point_buz_2': set_point_buz_2,
           'set_point_bzmp_2': set_point_bzmp_2,
           'set_point_bzmp_p1': set_point_bzmp_p1,
           'set_point_mmtz_d': set_point_mmtz_d,
           'set_point_mtz_5_v2_7': set_point_mtz_5_v2_7,
           'set_point_mtz_5_v2_8': set_point_mtz_5_v2_8,
           'set_point_mtz_5_v411': set_point_mtz_5_v411,
           'set_point_pmz': set_point_pmz,
           'set_point_tzp': set_point_tzp,
           'set_point_umz': set_point_umz,
           'set_point_ubtz': set_point_ubtz,
           'connect_mysql': connect_mysql,
           'connect_mysql_v2': connect_mysql_v2
}

with open('config.json', 'w') as f:
    json.dump(to_json, f)
