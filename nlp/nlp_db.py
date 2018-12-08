#!/usr/bin/env python
#-*- coding: utf-8 -*-

"""
- 트위터 트윗 수집기 (Collect Twitter Twits)
-- 데이터베이스

Author By. Karsei
"""

# 문자 인코딩과 시스템 입력 관련
#import sys
#reload(sys)
#sys.setdefaultencoding("utf8")

"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
* MongoDB
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
# mongodb 접속 관련
import pymongo

# SQL 데이터베이스 접속 (없을 시에는 생성)
db_connection = pymongo.MongoClient("localhost", 65000)
db_connection['ytgraph'].authenticate('ytgraph', 'ytgraphpass', mechanism='SCRAM-SHA-1')
db_database = db_connection['ytgraph']
