#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from gen_func_utils import ResetRelay
from time import time

rr = ResetRelay()
start_time = time()
rr.reset_all()
stop_time = time()
timer = stop_time - start_time
print(timer)
