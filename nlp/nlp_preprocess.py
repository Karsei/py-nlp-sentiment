#!/usr/bin/env python
#-*- coding: utf-8 -*-

"""
- 트위터 트윗 수집기 (Collect Twitter Twits)
-- 데이터 전처리기

Author By. Karsei
"""

# 문자 인코딩 관련
#import sys
#reload(sys)
#sys.setdefaultencoding("utf8")

"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
* BASIC SETTING
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
# json 포멧 관련
import json
# 정규화
import re

"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
* pprint
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
# 예쁘게 출력
import pprint

"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
* Konlpy
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
# 형태소 분석
import jpype
from konlpy.tag import Twitter

"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
* MongoDB
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
import nlp_db

"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
* 데이터 전처리
 - 1. 영어 소문자화
 - 2. 정규화로 불필요한 문자 삭제
 - 3. 명사 추출
 - 4. 불용어 제거
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
class SentenceProcessing():
    """""""""""""""""""""""""""""""""""""""""""""""
    # 생성자
    """""""""""""""""""""""""""""""""""""""""""""""
    def __init__(self):
        # 정규화 목록
        self.pre_regex_list = [
            r'<[^>]+>',         # HTML 태그
            r'(?:@[\w_]+)',     # @ 트윗 태그
            r'(http|https):\/\/([\xA1-\xFEa-z0-9_\-]+\.[\xA1-\xFEa-z0-9:;&#@=_~%\?\/\.\,\+\-]+)',   # URL 주소
            #r"(?:([a-zㄱ-ㅎㅏ-ㅣ가-힣0-9]+[\"'\-_]+[a-zㄱ-ㅎㅏ-ㅣ가-힣0-9]+)|([\"'\-_]+[a-zㄱ-ㅎㅏ-ㅣ가-힣0-9]+))",    # 하이픈과 언더바, 작은 따옴표로 연결된 단어
            #r"(?:[a-zㄱ-ㅎㅏ-ㅣ가-힣0-9]+[\"'\-_]+[a-zㄱ-ㅎㅏ-ㅣ가-힣0-9]+)",   # 하이픈과 언더바로 연결된 단어
            r'(?:\#([0-9a-zA-Z가-힣]*))',    # 해시 태그
            #r"(?:[\"'\-_,.]+)"  # 문장 부호
            r'(?:[\"\'＂＇“”‘’\-_,!@#$%^&*()\[\].、,…]+)',  # 문장 부호
            r"[^\w'|_]" # 특수문자 제거
            #r'(?:[a-zㄱ-ㅎㅏ-ㅣ가-힣0-9_]+)' # 나머지
        ]
        # 계속 사용할 정규화를 컴파일
        self.pre_regex_token = re.compile(r'('+'|'.join(self.pre_regex_list)+')', re.UNICODE)

        # 불용어 파일 로드
        self.pre_stopwords_file = None
        with open('./ko_stopwords.json') as fp:
            self.pre_stopwords_file = json.load(fp)

    """""""""""""""""""""""""""""""""""""""""""""""
    # 문자열 정규화
    @return 문자열
    """""""""""""""""""""""""""""""""""""""""""""""
    def getRegexString(self, msg):
        return self.pre_regex_token.sub(' ', msg)

    """""""""""""""""""""""""""""""""""""""""""""""
    # 문자열에서 명사 추출
    @return 리스트
    """""""""""""""""""""""""""""""""""""""""""""""
    def getNounList(self, msg):
        return postag.nouns(msg)

    """""""""""""""""""""""""""""""""""""""""""""""
    # 불용어 제거
    @return 리스트
    """""""""""""""""""""""""""""""""""""""""""""""
    def removeStopwords(self, list):
        for nouns in list:
            for stopwords in self.pre_stopwords_file:
                if nouns == stopwords:
                    if nouns in list:
                        list.remove(nouns)
        return list

    """""""""""""""""""""""""""""""""""""""""""""""
    # 리스트 내부 문자 출력
    """""""""""""""""""""""""""""""""""""""""""""""
    def printList(self, listset):
        # 이 작업을 안하면 콘솔에 유니코드 포멧이 그대로 찍혀서 나타난다.
        print (repr([str(x).encode(sys.stdout.encoding) for x in listset]).decode('string-escape'))

    """""""""""""""""""""""""""""""""""""""""""""""
    # 딕셔너리 내부 문자 출력
    """""""""""""""""""""""""""""""""""""""""""""""
    def printDict(self, Dictset):
        # 이 작업을 안하면 콘솔에 유니코드 포멧이 그대로 찍혀서 나타난다.
        print (repr({str(x).encode(sys.stdout.encoding) for x in Dictset}).decode('string-escape'))

    """""""""""""""""""""""""""""""""""""""""""""""
    # Bag of Word 생성
    @return dict
    """""""""""""""""""""""""""""""""""""""""""""""
    def createBOW(self, msg):
        bow = {}

        # 전처리 수행
        tokens = self.preprocess(msg)
        tokens_removestop = self.removeStopwords(tokens)

        # 토큰 갯수 파악
        for token in tokens:
            # 토큰이 없으면 기본적으로 0으로 잡고 있으면 무시해라
            bow.setdefault(token, 0)
            bow[token] += 1

        return bow

    """""""""""""""""""""""""""""""""""""""""""""""
    # 데이터 전처리 수행
    @return 리스트
    """""""""""""""""""""""""""""""""""""""""""""""
    def preprocess(self, msg):
        if jpype.isJVMStarted():
            jpype.attachThreadToJVM()

        postag = Twitter()

        msg = msg.lower()
        msg = self.getRegexString(msg)
        #msg = msg.split()
        msg = postag.nouns(msg)
        return self.removeStopwords(msg)
