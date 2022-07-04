#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from gen_mb_client import CtrlKL
from gen_func_utils import ResetRelay

__all__ = ["PervObmTV1", "VtorObmTV1"]


class PervObmTV1(object):
    """
    Включение первичной обмотки в зависимости от напряжения
    """

    def __init__(self):
        self.ctrl_kl = CtrlKL()
        self.reset = ResetRelay()

    def perv_obm_tv1(self, calc_vol=0.0):

        self.calc_vol = calc_vol

        if self.calc_vol <= 3.63:
            self.reset.sbros_perv_obm()
        elif 3.67 <= self.calc_vol < 3.89:
            self.ctrl_kl.ctrl_relay('KL38', True)
        elif 3.89 <= self.calc_vol < 4.11:
            self.ctrl_kl.ctrl_relay('KL39', True)
        elif 4.11 <= self.calc_vol < 4.35:
            self.ctrl_kl.ctrl_relay('KL40', True)
        elif 4.35 <= self.calc_vol < 4.57:
            self.ctrl_kl.ctrl_relay('KL41', True)
        elif 4.57 <= self.calc_vol < 4.77:
            self.ctrl_kl.ctrl_relay('KL42', True)
        elif 4.77 <= self.calc_vol < 5.03:
            self.ctrl_kl.ctrl_relay('KL43', True)
        elif 5.03 <= self.calc_vol < 5.25:
            self.ctrl_kl.ctrl_relay('KL44', True)
        elif 5.25 <= self.calc_vol < 5.48:
            self.ctrl_kl.ctrl_relay('KL45', True)
        elif 5.48 <= self.calc_vol < 5.71:
            self.ctrl_kl.ctrl_relay('KL46', True)
        elif 5.71 <= self.calc_vol < 5.97:
            self.ctrl_kl.ctrl_relay('KL47', True)
        elif 5.97 <= self.calc_vol < 6.31:
            self.ctrl_kl.ctrl_relay('KL38', True)
        elif 6.31 <= self.calc_vol < 6.68:
            self.ctrl_kl.ctrl_relay('KL39', True)
        elif 6.68 <= self.calc_vol < 7.06:
            self.ctrl_kl.ctrl_relay('KL40', True)
        elif 7.06 <= self.calc_vol < 7.43:
            self.ctrl_kl.ctrl_relay('KL41', True)
        elif 7.43 <= self.calc_vol < 7.75:
            self.ctrl_kl.ctrl_relay('KL42', True)
        elif 7.75 <= self.calc_vol < 8.17:
            self.ctrl_kl.ctrl_relay('KL43', True)
        elif 8.17 <= self.calc_vol < 8.54:
            self.ctrl_kl.ctrl_relay('KL44', True)
        elif 8.54 <= self.calc_vol < 8.91:
            self.ctrl_kl.ctrl_relay('KL45', True)
        elif 8.91 <= self.calc_vol < 9.29:
            self.ctrl_kl.ctrl_relay('KL46', True)
        elif 9.29 <= self.calc_vol < 9.65:
            self.ctrl_kl.ctrl_relay('KL47', True)
        elif 9.65 <= self.calc_vol < 10.20:
            self.ctrl_kl.ctrl_relay('KL38', True)
        elif 10.20 <= self.calc_vol < 10.79:
            self.ctrl_kl.ctrl_relay('KL39', True)
        elif 10.79 <= self.calc_vol < 11.41:
            self.ctrl_kl.ctrl_relay('KL40', True)
        elif 11.41 <= self.calc_vol < 12.0:
            self.ctrl_kl.ctrl_relay('KL41', True)
        elif 12.0 <= self.calc_vol < 12.52:
            self.ctrl_kl.ctrl_relay('KL42', True)
        elif 12.52 <= self.calc_vol < 13.2:
            self.ctrl_kl.ctrl_relay('KL43', True)
        elif 13.2 <= self.calc_vol < 13.79:
            self.ctrl_kl.ctrl_relay('KL44', True)
        elif 13.79 <= self.calc_vol < 14.39:
            self.ctrl_kl.ctrl_relay('KL45', True)
        elif 14.39 <= self.calc_vol < 15.0:
            self.ctrl_kl.ctrl_relay('KL46', True)
        elif 15.0 <= self.calc_vol < 15.16:
            self.ctrl_kl.ctrl_relay('KL47', True)
        elif 15.16 <= self.calc_vol < 16.03:
            self.ctrl_kl.ctrl_relay('KL38', True)
        elif 16.03 <= self.calc_vol < 16.96:
            self.ctrl_kl.ctrl_relay('KL39', True)
        elif 16.96 <= self.calc_vol < 17.93:
            self.ctrl_kl.ctrl_relay('KL40', True)
        elif 17.93 <= self.calc_vol < 18.86:
            self.ctrl_kl.ctrl_relay('KL41', True)
        elif 18.86 <= self.calc_vol < 19.67:
            self.ctrl_kl.ctrl_relay('KL42', True)
        elif 19.67 <= self.calc_vol < 20.74:
            self.ctrl_kl.ctrl_relay('KL43', True)
        elif 20.74 <= self.calc_vol < 21.67:
            self.ctrl_kl.ctrl_relay('KL44', True)
        elif 21.67 <= self.calc_vol < 22.62:
            self.ctrl_kl.ctrl_relay('KL45', True)
        elif 22.62 <= self.calc_vol < 23.57:
            self.ctrl_kl.ctrl_relay('KL46', True)
        elif 23.57 <= self.calc_vol < 23.88:
            self.ctrl_kl.ctrl_relay('KL47', True)
        elif 23.88 <= self.calc_vol < 25.25:
            self.ctrl_kl.ctrl_relay('KL38', True)
        elif 25.25 <= self.calc_vol < 26.73:
            self.ctrl_kl.ctrl_relay('KL39', True)
        elif 26.73 <= self.calc_vol < 28.25:
            self.ctrl_kl.ctrl_relay('KL40', True)
        elif 28.25 <= self.calc_vol < 29.71:
            self.ctrl_kl.ctrl_relay('KL41', True)
        elif 29.71 <= self.calc_vol < 31.0:
            self.ctrl_kl.ctrl_relay('KL42', True)
        elif 31.0 <= self.calc_vol < 32.69:
            self.ctrl_kl.ctrl_relay('KL43', True)
        elif 32.69 <= self.calc_vol < 34.15:
            self.ctrl_kl.ctrl_relay('KL44', True)
        elif 34.15 <= self.calc_vol < 35.64:
            self.ctrl_kl.ctrl_relay('KL45', True)
        elif 35.64 <= self.calc_vol < 37.14:
            self.ctrl_kl.ctrl_relay('KL46', True)
        elif 37.14 <= self.calc_vol < 37.66:
            self.ctrl_kl.ctrl_relay('KL47', True)
        elif 37.66 <= self.calc_vol < 39.82:
            self.ctrl_kl.ctrl_relay('KL38', True)
        elif 39.82 <= self.calc_vol < 42.15:
            self.ctrl_kl.ctrl_relay('KL39', True)
        elif 42.15 <= self.calc_vol < 44.54:
            self.ctrl_kl.ctrl_relay('KL40', True)
        elif 44.54 <= self.calc_vol < 46.86:
            self.ctrl_kl.ctrl_relay('KL41', True)
        elif 46.86 <= self.calc_vol < 48.89:
            self.ctrl_kl.ctrl_relay('KL42', True)
        elif 48.89 <= self.calc_vol < 51.54:
            self.ctrl_kl.ctrl_relay('KL43', True)
        elif 51.54 <= self.calc_vol < 53.85:
            self.ctrl_kl.ctrl_relay('KL44', True)
        elif 53.85 <= self.calc_vol < 56.2:
            self.ctrl_kl.ctrl_relay('KL45', True)
        elif 56.2 <= self.calc_vol < 58.57:
            self.ctrl_kl.ctrl_relay('KL46', True)
        elif 58.57 <= self.calc_vol < 59.71:
            self.ctrl_kl.ctrl_relay('KL47', True)
        elif 59.71 <= self.calc_vol < 63.13:
            self.ctrl_kl.ctrl_relay('KL38', True)
        elif 63.13 <= self.calc_vol < 66.82:
            self.ctrl_kl.ctrl_relay('KL39', True)
        elif 66.82 <= self.calc_vol < 70.62:
            self.ctrl_kl.ctrl_relay('KL40', True)
        elif 70.62 <= self.calc_vol < 74.29:
            self.ctrl_kl.ctrl_relay('KL41', True)
        elif 74.29 <= self.calc_vol < 77.51:
            self.ctrl_kl.ctrl_relay('KL42', True)
        elif 77.51 <= self.calc_vol < 81.71:
            self.ctrl_kl.ctrl_relay('KL43', True)
        elif 81.71 <= self.calc_vol < 85.37:
            self.ctrl_kl.ctrl_relay('KL44', True)
        elif 85.37 <= self.calc_vol < 89.1:
            self.ctrl_kl.ctrl_relay('KL45', True)
        elif 89.1 <= self.calc_vol < 92.86:
            self.ctrl_kl.ctrl_relay('KL46', True)
        elif 92.86 <= self.calc_vol < 93.7:
            self.ctrl_kl.ctrl_relay('KL47', True)
        elif 93.7 <= self.calc_vol < 99.07:
            self.ctrl_kl.ctrl_relay('KL38', True)
        elif 99.07 <= self.calc_vol < 104.86:
            self.ctrl_kl.ctrl_relay('KL39', True)
        elif 104.86 <= self.calc_vol < 110.81:
            self.ctrl_kl.ctrl_relay('KL40', True)
        elif 110.81 <= self.calc_vol < 116.57:
            self.ctrl_kl.ctrl_relay('KL41', True)
        elif 116.57 <= self.calc_vol < 121.63:
            self.ctrl_kl.ctrl_relay('KL42', True)
        elif 121.63 <= self.calc_vol < 128.23:
            self.ctrl_kl.ctrl_relay('KL43', True)
        elif 128.23 <= self.calc_vol < 133.97:
            self.ctrl_kl.ctrl_relay('KL44', True)
        elif 133.97 <= self.calc_vol < 139.81:
            self.ctrl_kl.ctrl_relay('KL45', True)
        elif 139.81 <= self.calc_vol < 145.71:
            self.ctrl_kl.ctrl_relay('KL46', True)
        elif 145.71 <= self.calc_vol < 146.51:
            self.ctrl_kl.ctrl_relay('KL47', True)
        elif 146.51 <= self.calc_vol < 154.92:
            self.ctrl_kl.ctrl_relay('KL38', True)
        elif 154.92 <= self.calc_vol < 156.16:
            self.ctrl_kl.ctrl_relay('KL39', True)
        elif 156.16 <= self.calc_vol < 163.97:
            self.ctrl_kl.ctrl_relay('KL38', True)
        elif 163.97 <= self.calc_vol < 165.12:
            self.ctrl_kl.ctrl_relay('KL40', True)
        elif 165.12 <= self.calc_vol < 173.28:
            self.ctrl_kl.ctrl_relay('KL39', True)
        elif 173.28 <= self.calc_vol < 174.77:
            self.ctrl_kl.ctrl_relay('KL41', True)
        elif 174.77 <= self.calc_vol < 180.04:
            self.ctrl_kl.ctrl_relay('KL40', True)
        elif 180.04 <= self.calc_vol < 182.29:
            self.ctrl_kl.ctrl_relay('KL38', True)
        elif 182.29 <= self.calc_vol < 184.69:
            self.ctrl_kl.ctrl_relay('KL42', True)
        elif 184.69 <= self.calc_vol < 186.01:
            self.ctrl_kl.ctrl_relay('KL41', True)
        elif 186.01 <= self.calc_vol < 190.19:
            self.ctrl_kl.ctrl_relay('KL38', True)
        elif 190.19 <= self.calc_vol < 190.38:
            self.ctrl_kl.ctrl_relay('KL43', True)
        elif 190.38 <= self.calc_vol < 194.29:
            self.ctrl_kl.ctrl_relay('KL39', True)
        elif 194.29 <= self.calc_vol < 196.69:
            self.ctrl_kl.ctrl_relay('KL42', True)
        elif 196.69 <= self.calc_vol < 200.51:
            self.ctrl_kl.ctrl_relay('KL39', True)
        elif 200.51 <= self.calc_vol < 201.5:
            self.ctrl_kl.ctrl_relay('KL44', True)
        elif 201.5 <= self.calc_vol < 202.71:
            self.ctrl_kl.ctrl_relay('KL40', True)
        elif 202.71 <= self.calc_vol < 208.18:
            self.ctrl_kl.ctrl_relay('KL43', True)
        elif 208.18 <= self.calc_vol < 209.49:
            self.ctrl_kl.ctrl_relay('KL40', True)
        elif 209.49 <= self.calc_vol < 212.94:
            self.ctrl_kl.ctrl_relay('KL45', True)
        elif 212.94 <= self.calc_vol < 213.71:
            self.ctrl_kl.ctrl_relay('KL41', True)
        elif 213.71 <= self.calc_vol < 218.63:
            self.ctrl_kl.ctrl_relay('KL44', True)
        elif 218.63 <= self.calc_vol < 220.0:
            self.ctrl_kl.ctrl_relay('KL46', True)
        elif 220.0 <= self.calc_vol < 223.28:
            self.ctrl_kl.ctrl_relay('KL41', True)
        elif 223.28 <= self.calc_vol < 224.0:
            self.ctrl_kl.ctrl_relay('KL45', True)
        elif 224.0 <= self.calc_vol < 227.86:
            self.ctrl_kl.ctrl_relay('KL42', True)
        elif 227.86 <= self.calc_vol < 231.43:
            self.ctrl_kl.ctrl_relay('KL47', True)
        elif 231.43 <= self.calc_vol < 233.02:
            self.ctrl_kl.ctrl_relay('KL42', True)
        elif 233.02 <= self.calc_vol < 233.71:
            self.ctrl_kl.ctrl_relay('KL46', True)
        elif 233.71 <= self.calc_vol < 242.86:
            self.ctrl_kl.ctrl_relay('KL43', True)
        elif 242.86 <= self.calc_vol < 246.4:
            self.ctrl_kl.ctrl_relay('KL47', True)
        elif 246.4 <= self.calc_vol < 257.43:
            self.ctrl_kl.ctrl_relay('KL44', True)
        elif 257.43 <= self.calc_vol < 268.66:
            self.ctrl_kl.ctrl_relay('KL45', True)
        elif 268.66 <= self.calc_vol < 280.0:
            self.ctrl_kl.ctrl_relay('KL46', True)
        elif 280.0 <= self.calc_vol < 289.29:
            self.ctrl_kl.ctrl_relay('KL47', True)
        else:
            self.reset.sbros_perv_obm()


class VtorObmTV1(object):
    """
        Включение вторичной обмотки в зависимости от напряжения
    """

    def __init__(self):

        self.ctrl_kl = CtrlKL()
        self.reset = ResetRelay()

    def vtor_obm_tv1(self, calc_vol=0.0):

        self.calc_vol = calc_vol

        if self.calc_vol < 3.66:
            self.reset.sbros_vtor_obm()
        elif 3.67 <= self.calc_vol <= 5.96:
            self.ctrl_kl.ctrl_relay('KL59', True)
        elif 5.97 <= self.calc_vol <= 9.64:
            self.ctrl_kl.ctrl_relay('KL58', True)
        elif 9.65 <= self.calc_vol <= 15.15:
            self.ctrl_kl.ctrl_relay('KL57', True)
        elif 15.16 <= self.calc_vol <= 23.87:
            self.ctrl_kl.ctrl_relay('KL56', True)
        elif 23.88 <= self.calc_vol <= 37.65:
            self.ctrl_kl.ctrl_relay('KL55', True)
        elif 37.66 <= self.calc_vol <= 59.7:
            self.ctrl_kl.ctrl_relay('KL54', True)
        elif 59.71 <= self.calc_vol <= 93.69:
            self.ctrl_kl.ctrl_relay('KL53', True)
        elif 93.7 <= self.calc_vol <= 146.5:
            self.ctrl_kl.ctrl_relay('KL52', True)
        elif 146.51 <= self.calc_vol <= 156.15:
            self.ctrl_kl.ctrl_relay('KL51', True)
        elif 156.16 <= self.calc_vol <= 163.96:
            self.ctrl_kl.ctrl_relay('KL50', True)
        elif 163.97 <= self.calc_vol <= 165.11:
            self.ctrl_kl.ctrl_relay('KL51', True)
        elif 165.12 <= self.calc_vol <= 173.27:
            self.ctrl_kl.ctrl_relay('KL50', True)
        elif 173.28 <= self.calc_vol <= 174.76:
            self.ctrl_kl.ctrl_relay('KL51', True)
        elif 174.77 <= self.calc_vol <= 180.03:
            self.ctrl_kl.ctrl_relay('KL50', True)
        elif 180.04 <= self.calc_vol <= 182.28:
            self.ctrl_kl.ctrl_relay('KL49', True)
        elif 182.29 <= self.calc_vol <= 184.68:
            self.ctrl_kl.ctrl_relay('KL51', True)
        elif 184.69 <= self.calc_vol <= 186.0:
            self.ctrl_kl.ctrl_relay('KL50', True)
        elif 186.01 <= self.calc_vol <= 190.18:
            self.ctrl_kl.ctrl_relay('KL48', True)
        elif 190.19 <= self.calc_vol <= 190.37:
            self.ctrl_kl.ctrl_relay('KL51', True)
        elif 190.38 <= self.calc_vol <= 194.28:
            self.ctrl_kl.ctrl_relay('KL49', True)
        elif 194.29 <= self.calc_vol <= 196.68:
            self.ctrl_kl.ctrl_relay('KL50', True)
        elif 196.69 <= self.calc_vol <= 200.5:
            self.ctrl_kl.ctrl_relay('KL48', True)
        elif 200.51 <= self.calc_vol <= 201.49:
            self.ctrl_kl.ctrl_relay('KL51', True)
        elif 201.5 <= self.calc_vol <= 202.7:
            self.ctrl_kl.ctrl_relay('KL49', True)
        elif 202.71 <= self.calc_vol <= 208.17:
            self.ctrl_kl.ctrl_relay('KL50', True)
        elif 208.18 <= self.calc_vol <= 209.48:
            self.ctrl_kl.ctrl_relay('KL48', True)
        elif 209.49 <= self.calc_vol <= 212.93:
            self.ctrl_kl.ctrl_relay('KL51', True)
        elif 212.94 <= self.calc_vol <= 213.7:
            self.ctrl_kl.ctrl_relay('KL49', True)
        elif 213.71 <= self.calc_vol <= 218.62:
            self.ctrl_kl.ctrl_relay('KL50', True)
        elif 218.63 <= self.calc_vol <= 219.99:
            self.ctrl_kl.ctrl_relay('KL51', True)
        elif 220.0 <= self.calc_vol <= 223.27:
            self.ctrl_kl.ctrl_relay('KL48', True)
        elif 223.28 <= self.calc_vol <= 223.99:
            self.ctrl_kl.ctrl_relay('KL50', True)
        elif 224.0 <= self.calc_vol < 227.87:
            self.ctrl_kl.ctrl_relay('KL49', True)
        elif 227.87 <= self.calc_vol <= 231.42:
            self.ctrl_kl.ctrl_relay('KL51', True)
        elif 231.43 <= self.calc_vol <= 233.01:
            self.ctrl_kl.ctrl_relay('KL48', True)
        elif 233.02 <= self.calc_vol <= 233.7:
            self.ctrl_kl.ctrl_relay('KL50', True)
        elif 233.71 <= self.calc_vol <= 241.45:
            self.ctrl_kl.ctrl_relay('KL49', True)
        elif 241.46 <= self.calc_vol <= 242.85:
            self.ctrl_kl.ctrl_relay('KL48', True)
        elif 242.86 <= self.calc_vol <= 246.39:
            self.ctrl_kl.ctrl_relay('KL50', True)
        elif 246.4 <= self.calc_vol <= 254.56:
            self.ctrl_kl.ctrl_relay('KL49', True)
        elif 254.57 <= self.calc_vol <= 257.42:
            self.ctrl_kl.ctrl_relay('KL48', True)
        elif 257.43 <= self.calc_vol <= 265.96:
            self.ctrl_kl.ctrl_relay('KL49', True)
        elif 265.97 <= self.calc_vol <= 268.65:
            self.ctrl_kl.ctrl_relay('KL48', True)
        elif 268.66 <= self.calc_vol <= 277.56:
            self.ctrl_kl.ctrl_relay('KL49', True)
        elif 277.57 <= self.calc_vol <= 279.99:
            self.ctrl_kl.ctrl_relay('KL48', True)
        elif 280.0 <= self.calc_vol <= 289.28:
            self.ctrl_kl.ctrl_relay('KL49', True)
        elif 289.29 <= self.calc_vol:
            self.ctrl_kl.ctrl_relay('KL48', True)
        else:
            self.reset.sbros_vtor_obm()
