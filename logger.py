#!/usr/bin/env python3

import logging
import datetime

# now = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
# logfilename = f"{now}.log"
# print(logfilename)

logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger("bot_logger")

# c_handler = logging.StreamHandler()
# f_handler = logging.FileHandler(f"./log/{logfilename}")
# c_handler.setLevel(logging.INFO)
# f_handler.setLevel(logging.DEBUG)
#
# c_format = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
# f_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
# c_handler.setFormatter(c_format)
# f_handler.setFormatter(f_format)

