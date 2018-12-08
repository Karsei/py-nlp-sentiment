#!/usr/bin/env python
#-*- coding: utf-8 -*-

"""
- 로그 생성기 (LogWriter)

Author By. Karsei
"""

# 수집 시 날짜 출력
from datetime import datetime

"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
* 로그 생성
 - 로그 메세지 형성
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
class LogWriter():
    """""""""""""""""""""""""""""""""""""""""""""""
    # 현재 시간 문자열 출력
    """""""""""""""""""""""""""""""""""""""""""""""
    def getCurrentDate(self):
        return datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    """""""""""""""""""""""""""""""""""""""""""""""
    # 정보
    # ex) log.i("{0} yay {1}!", ("so", "1"))
    """""""""""""""""""""""""""""""""""""""""""""""
    def i(self, msg, formats=(), dateset=False):
        self.custom('정보', msg, formats, dateset)

    """""""""""""""""""""""""""""""""""""""""""""""
    # 오류
    # ex) log.e("{0} yay {1}!", ("so", "1"))
    """""""""""""""""""""""""""""""""""""""""""""""
    def e(self, msg, formats=(), dateset=False):
        self.custom('오류', msg, formats, dateset)

    """""""""""""""""""""""""""""""""""""""""""""""
    # 경고
    # ex) log.w("{0} yay {1}!", ("so", "1"))
    """""""""""""""""""""""""""""""""""""""""""""""
    def w(self, msg, formats=(), dateset=False):
        self.custom('경고', msg, formats, dateset)

    """""""""""""""""""""""""""""""""""""""""""""""
    # 수동
    # ex) log.custom("LOG", "{0} yay {1}!", ("so", "1"))
    """""""""""""""""""""""""""""""""""""""""""""""
    def custom(self, title, msg, formats=(), dateset=False):
        if len(formats) > 0:
            #print "[" + title + "] " + msg.format(*formats)
            if dateset == True:
                print ('[' + title + '][' + self.getCurrentDate() + '] ' + msg.format(formats))
            else:
                print ('[' + title + '] ' + msg.format(formats))
        else:
            if dateset == True:
                print ('[' + title + '][' + self.getCurrentDate() + '] ' + msg)
            else:
                print ('[' + title + '] ' + msg)
