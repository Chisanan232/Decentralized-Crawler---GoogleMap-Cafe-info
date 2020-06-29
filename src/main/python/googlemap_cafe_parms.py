#! /etc/anaconda/python3

import sys
import re


class GoogleMapCafeParam:

    code_os = sys.platform
    mac_operator_system = re.search(r"darwin", code_os, re.IGNORECASE)
    win_operator_system = re.search(r"win[0-9]{1,3}", code_os, re.IGNORECASE)
    linux_operator_system = re.search(r"linux", code_os, re.IGNORECASE)
    if mac_operator_system:
        ChromeExecutorPath = "/Users/bryantliu/DevelopProject/KobeDevelopProject/Crawler/chromedriver"
    elif win_operator_system:
        ChromeExecutorPath = None
    else:
        ChromeExecutorPath = None

    CAFE_SHUTDOWN = None
    ALL_COMMENTS = 0

