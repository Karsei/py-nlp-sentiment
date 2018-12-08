#!/usr/bin/env python
#-*- coding: utf-8 -*-

"""
- Test

Author By. Karsei
"""

import re

import jpype
from konlpy.tag import Twitter
postag = Twitter()
if jpype.isJVMStarted():
    jpype.attachThreadToJVM()

# 특수문자 제거 (정규표현식 이용)
special_chars_remover = re.compile("[^\w'|_]")
regex = [
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
regex_remover = re.compile(r'('+'|'.join(regex)+')', re.UNICODE)

def main():
    #sentence = "안녕하세요!!! Hello World !@#$%"
    sentence = '독립운동하면 3대 대우 받는 나라 위해 3400억 추가 투입 https://t.co/DMpu0qTuSr\n\n이제야\n나라가 나라 다워 지네요..'
    #bow = create_BOW(sentence)
    print(postag.nouns(sentence))
    #print(bow)

def create_BOW(sentence):
    bow = {}

    #preprocessing
    sentence = sentence.lower()
    sentence = remove_special_characters(sentence)
    token_sentence = sentence.split()
    for token in token_sentence:
        # 토큰이 없으면 기본적으로 0으로 잡고 있으면 무시해라
        bow.setdefault(token, 0)
        bow[token] += 1

    return bow

def remove_special_characters(sentence):
    return regex_remover.sub(' ', sentence)

if __name__ == "__main__":
    main()
