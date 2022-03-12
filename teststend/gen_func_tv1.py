#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from gen_mb_client import CtrlKL
from gen_func_utils import ResetRelay

__all__ = ["PervObmTV1", "VtorObmTV1"]


class PervObmTV1(object):

    ctrl_kl = CtrlKL()
    reset = ResetRelay()

    def perv_obm_tv1(self, calc_vol=0.0):

        self.calc_vol = calc_vol

        if self.calc_vol <= 3.63:
            self.reset.sbros_perv_obm()
        elif ((3.67 <= self.calc_vol < 3.89) or (5.97 <= self.calc_vol < 6.31) or
              (9.65 <= self.calc_vol < 10.20) or (15.16 <= self.calc_vol < 16.03) or
              (23.88 <= self.calc_vol < 25.25) or (37.66 <= self.calc_vol < 39.82) or
              (59.71 <= self.calc_vol < 63.13) or (93.7 <= self.calc_vol < 99.07) or
              (146.51 <= self.calc_vol < 154.92) or (156.16 <= self.calc_vol < 163.97) or
              (180.04 <= self.calc_vol < 182.29) or (186.01 <= self.calc_vol < 190.19)):
            self.ctrl_kl.ctrl_relay('KL38', True)

        elif ((3.89 <= self.calc_vol < 4.11) or (6.31 <= self.calc_vol < 6.68) or
              (10.20 <= self.calc_vol < 10.79) or (16.03 <= self.calc_vol < 16.96) or
              (25.25 <= self.calc_vol < 26.73) or (39.82 <= self.calc_vol < 42.15) or
              (63.13 <= self.calc_vol < 66.82) or (99.07 <= self.calc_vol < 104.86) or
              (154.92 <= self.calc_vol < 156.16) or (165.12 <= self.calc_vol < 173.28) or
              (190.38 <= self.calc_vol < 194.29) or (196.69 <= self.calc_vol < 200.51)):
            self.ctrl_kl.ctrl_relay('KL39', True)

        elif ((4.11 <= self.calc_vol < 4.35) or (6.68 <= self.calc_vol < 7.06) or
              (10.79 <= self.calc_vol < 11.41) or (16.96 <= self.calc_vol < 17.93) or
              (26.73 <= self.calc_vol < 28.25) or (42.15 <= self.calc_vol < 44.54) or
              (66.82 <= self.calc_vol < 70.62) or (104.86 <= self.calc_vol < 110.81) or
              (163.97 <= self.calc_vol < 165.12) or (174.77 <= self.calc_vol < 180.04) or
              (201.5 <= self.calc_vol < 202.71) or (208.18 <= self.calc_vol < 209.49)):
            self.ctrl_kl.ctrl_relay('KL40', True)

        elif ((4.35 <= self.calc_vol < 4.57) or (7.06 <= self.calc_vol < 7.43) or
              (11.41 <= self.calc_vol < 12.0) or (17.93 <= self.calc_vol < 18.86) or
              (28.25 <= self.calc_vol < 29.71) or (44.54 <= self.calc_vol < 46.86) or
              (70.62 <= self.calc_vol < 74.29) or (110.81 <= self.calc_vol < 116.57) or
              (173.28 <= self.calc_vol < 174.77) or (184.69 <= self.calc_vol < 186.01) or
              (212.94 <= self.calc_vol < 213.71) or (220.0 <= self.calc_vol < 223.28)):
            self.ctrl_kl.ctrl_relay('KL41', True)

        elif ((4.57 <= self.calc_vol < 4.77) or (7.43 <= self.calc_vol < 7.75) or
              (12.0 <= self.calc_vol < 12.52) or (18.86 <= self.calc_vol < 19.67) or
              (29.71 <= self.calc_vol < 31.0) or (46.86 <= self.calc_vol < 48.89) or
              (74.29 <= self.calc_vol < 77.51) or (116.57 <= self.calc_vol < 121.63) or
              (182.29 <= self.calc_vol < 184.69) or (194.29 <= self.calc_vol < 196.69) or
              (224.0 <= self.calc_vol < 227.86) or (231.43 <= self.calc_vol < 233.02)):
            self.ctrl_kl.ctrl_relay('KL42', True)

        elif ((4.77 <= self.calc_vol < 5.03) or (7.75 <= self.calc_vol < 8.17) or
              (12.52 <= self.calc_vol < 13.2) or (19.67 <= self.calc_vol < 20.74) or
              (31.0 <= self.calc_vol < 32.69) or (48.89 <= self.calc_vol < 51.54) or
              (77.51 <= self.calc_vol < 81.71) or (121.63 <= self.calc_vol < 128.23) or
              (190.19 <= self.calc_vol < 190.38) or (202.71 <= self.calc_vol < 208.18) or
              (233.71 <= self.calc_vol < 242.86)):
            self.ctrl_kl.ctrl_relay('KL43', True)

        elif ((5.03 <= self.calc_vol < 5.25) or (8.17 <= self.calc_vol < 8.54) or
              (13.2 <= self.calc_vol < 13.79) or (20.74 <= self.calc_vol < 21.67) or
              (32.69 <= self.calc_vol < 34.15) or (51.54 <= self.calc_vol < 53.85) or
              (81.71 <= self.calc_vol < 85.37) or (128.23 <= self.calc_vol < 133.97) or
              (200.51 <= self.calc_vol < 201.5) or (213.71 <= self.calc_vol < 218.63) or
              (246.4 <= self.calc_vol < 257.43)):
            self.ctrl_kl.ctrl_relay('KL44', True)

        elif ((5.25 <= self.calc_vol < 5.48) or (8.54 <= self.calc_vol < 8.91) or
              (13.79 <= self.calc_vol < 14.39) or (21.67 <= self.calc_vol < 22.62) or
              (34.15 <= self.calc_vol < 35.64) or (53.85 <= self.calc_vol < 56.2) or
              (85.37 <= self.calc_vol < 89.1) or (133.97 <= self.calc_vol < 139.81) or
              (14448 <= self.calc_vol < 212.94) or (223.28 <= self.calc_vol < 224.0) or
              (257.43 <= self.calc_vol < 268.66)):
            self.ctrl_kl.ctrl_relay('KL45', True)

        elif ((5.48 <= self.calc_vol < 5.71) or (8.91 <= self.calc_vol < 9.29) or
              (14.39 <= self.calc_vol < 15.0) or (22.62 <= self.calc_vol < 23.57) or
              (35.64 <= self.calc_vol < 37.14) or (56.2 <= self.calc_vol < 58.57) or
              (89.1 <= self.calc_vol < 92.86) or (139.81 <= self.calc_vol < 145.71) or
              (218.63 <= self.calc_vol < 220.0) or (233.02 <= self.calc_vol < 233.71) or
              (268.66 <= self.calc_vol < 280.0)):
            self.ctrl_kl.ctrl_relay('KL46', True)

        elif ((5.71 <= self.calc_vol < 5.97) or (9.29 <= self.calc_vol < 9.65) or
              (15.0 <= self.calc_vol < 15.16) or (23.57 <= self.calc_vol < 23.88) or
              (37.14 <= self.calc_vol < 37.66) or (58.57 <= self.calc_vol < 59.71) or
              (92.86 <= self.calc_vol < 93.7) or (145.71 <= self.calc_vol < 146.51) or
              (227.86 <= self.calc_vol < 231.43) or (242.86 <= self.calc_vol < 246.4) or
              (280.0 <= self.calc_vol < 289.29)):
            self.ctrl_kl.ctrl_relay('KL47', True)
        else:
            self.reset.sbros_perv_obm()


class VtorObmTV1(object):

    ctrl_kl = CtrlKL()
    reset = ResetRelay()

    def vtor_obm_tv1(self, calc_vol=0.0):

        self.calc_vol = calc_vol

        if self.calc_vol < 3.66:
            # Сброс контактов  вторичной обмотки TV1
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
        elif ((146.51 <= self.calc_vol <= 156.15) or (163.97 <= self.calc_vol <= 165.11) or
              (173.28 <= self.calc_vol <= 174.76) or (182.29 <= self.calc_vol <= 184.68) or
              (190.19 <= self.calc_vol <= 190.37) or (200.51 <= self.calc_vol <= 201.49) or
              (209.49 <= self.calc_vol <= 212.93) or (218.63 <= self.calc_vol <= 219.99) or
              (227.86 <= self.calc_vol <= 231.42)):
            self.ctrl_kl.ctrl_relay('KL51', True)
        elif ((156.16 <= self.calc_vol <= 163.96) or (165.12 <= self.calc_vol <= 173.27) or
              (174.77 <= self.calc_vol <= 180.03) or (184.69 <= self.calc_vol <= 186.0) or
              (194.29 <= self.calc_vol <= 196.68) or (202.71 <= self.calc_vol <= 208.17) or
              (213.71 <= self.calc_vol <= 218.62) or (223.28 <= self.calc_vol <= 223.99) or
              (233.02 <= self.calc_vol <= 233.7) or (242.86 <= self.calc_vol <= 246.39)):
            self.ctrl_kl.ctrl_relay('KL50', True)
        elif ((180.04 <= self.calc_vol <= 182.28) or (190.38 <= self.calc_vol <= 194.28) or
              (201.5 <= self.calc_vol <= 202.7) or (212.94 <= self.calc_vol <= 213.7) or
              (224.0 <= self.calc_vol <= 227.87) or (233.71 <= self.calc_vol <= 241.45) or
              (246.4 <= self.calc_vol <= 254.56) or (257.43 <= self.calc_vol <= 265.96) or
              (268.66 <= self.calc_vol <= 277.56) or (280.0 <= self.calc_vol <= 289.28)):
            self.ctrl_kl.ctrl_relay('KL49', True)
        elif ((186.01 <= self.calc_vol <= 190.18) or (196.69 <= self.calc_vol <= 200.5) or
              (208.18 <= self.calc_vol <= 209.48) or (220.0 <= self.calc_vol <= 223.27) or
              (231.43 <= self.calc_vol <= 233.01) or (241.46 <= self.calc_vol <= 242.85) or
              (254.57 <= self.calc_vol <= 257.42) or (265.97 <= self.calc_vol <= 268.65) or
              (277.57 <= self.calc_vol <= 279.99) or (289.29 <= self.calc_vol)):
            self.ctrl_kl.ctrl_relay('KL48', True)
        else:
            self.reset.sbros_vtor_obm()
