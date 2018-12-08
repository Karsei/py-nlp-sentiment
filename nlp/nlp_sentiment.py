#!/usr/bin/env python
#-*- coding: utf-8 -*-

"""
- 감정분석 (Semtiment Analizing)
-- Naive Bayes Model

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
# 수학
import math

class SentimentProcessing():
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

        # 감정 자료 가져오기
        self.training_sentences = self.read_data()

        # 감정 자료 BOW 생성
        self.training_model_pos = self.create_BOW(self.training_sentences[1])
        self.training_model_neg = self.create_BOW(self.training_sentences[0])

    """""""""""""""""""""""""""""""""""""""""""""""
    # 감정 분석을 위한 감정 자료값 로드
    @return list
    """""""""""""""""""""""""""""""""""""""""""""""
    def read_data(self):
        # 한 리스트에 2개로 나누어 [부정, 긍정]으로 나눔
        training_sentences = [[], []]

        # 자료를 가져오자!
        # https://github.com/e9t/nsmc
        with open('./ratings.txt') as fp:
            # 맨 위에 있는 라벨은 스킵
            next(fp)
            count = 0
            for line in fp:
                # 탭으로 구분되어 있음
                # 8112052 어릴때보고 지금다시봐도 재밌어요ㅋㅋ    1
                splitted = line.split('\t')
                # 컬럼값 가져옴
                document = splitted[1]
                label = int(splitted[2])
                # 종류에 따라 값 저장(0 부정, 1 긍정)
                training_sentences[label].append(document)

        return [' '.join(training_sentences[0]), ' '.join(training_sentences[1])]

    """""""""""""""""""""""""""""""""""""""""""""""
    # 로그 확률값 표준화
    @return tuple
    """""""""""""""""""""""""""""""""""""""""""""""
    def normalize_log_prob(self, prob1, prob2):
        maxprob = max(prob1, prob2)

        prob1 -= maxprob
        prob2 -= maxprob
        prob1 = math.exp(prob1)
        prob2 = math.exp(prob2)

        normalize_constant = 1.0 / float(prob1 + prob2)
        prob1 *= normalize_constant
        prob2 *= normalize_constant

        return (prob1, prob2)

    """""""""""""""""""""""""""""""""""""""""""""""
    # Naive Bayes 모델 수행
    @return tuple
    """""""""""""""""""""""""""""""""""""""""""""""
    def naive_bayes(self, training_sentences, testing_sentence):
        #log_prob_negative = self.calcalate_doc_prob(training_sentences[0], testing_sentence, 0.1) + math.log(0.5)
        #log_prob_positive = self.calcalate_doc_prob(training_sentences[1], testing_sentence, 0.1) + math.log(0.5)
        log_prob_negative = self.calcalate_doc_prob(0, testing_sentence, 0.1) + math.log(0.5)
        log_prob_positive = self.calcalate_doc_prob(1, testing_sentence, 0.1) + math.log(0.5)
        prob_pair = self.normalize_log_prob(log_prob_negative, log_prob_positive)

        return prob_pair

    """""""""""""""""""""""""""""""""""""""""""""""
    # 부정, 긍정 문서에 따른 확률 구하기
    @return 확률
    """""""""""""""""""""""""""""""""""""""""""""""
    #def calcalate_doc_prob(self, training_sentences, testing_sentence, alpha):
    def calcalate_doc_prob(self, mode, testing_sentence, alpha):
        logprob = 0 # log(1) = 0

        #training_model = self.create_BOW(training_sentences)
        training_model = None
        testing_model = self.create_BOW(testing_sentence)
        if mode == 0:
            training_model = self.training_model_neg
        else:
            training_model = self.training_model_pos

        # 감정 모델에 있는 모든 토큰수를 구한다
        num_all_tokens = 0
        for token in training_model:
            num_all_tokens += training_model[token]

        for token in testing_model:
            # 같은 단어가 연속으로 들어간 경우도 있기에 단어의 갯수를 신경쓴다
            for i in range(testing_model[token]):
                # 없는 단어에 대해서는 상당히 작은 값을 넣어준다
                if token in training_model:
                    # 단어가 있는 경우
                    logprob += math.log(training_model[token])
                    logprob -= math.log(num_all_tokens)
                else:
                    # 단어가 없는 경우
                    logprob += math.log(alpha)
                    logprob -= math.log(num_all_tokens)

        return logprob

    """""""""""""""""""""""""""""""""""""""""""""""
    # Bag of Words 수행
    @return dict
    """""""""""""""""""""""""""""""""""""""""""""""
    def create_BOW(self, sentence):
        bow = {}

        # 소문자로 만들어준다
        sentence = sentence.lower()
        # 특수문자를 제거한다
        sentence = self.getRegexString(sentence)
        # 토큰으로 나눈다
        tokens = sentence.split()
        # 1보다 작으면 패스
        for token in tokens:
            if len(token) < 1:
                continue
            bow.setdefault(token, 0)
            bow[token] += 1

        return bow

    """""""""""""""""""""""""""""""""""""""""""""""
    # 감정 분석
    @return list
    """""""""""""""""""""""""""""""""""""""""""""""
    def sentiment_analysis(self, sentence):
        return list(self.naive_bayes(self.training_sentences, sentence))

    """""""""""""""""""""""""""""""""""""""""""""""
    # 문자열 정규화
    @return 문자열
    """""""""""""""""""""""""""""""""""""""""""""""
    def getRegexString(self, msg):
        return self.pre_regex_token.sub(' ', msg)

"""
def main():
    p = SentimentProcessing()
    sentence = "@Michelle_ahn @drmaengyi @moonlover333 아니 이보세요. 그동안 반대하던 문재인이 입장 바꿔 배치완료했는데, 왜 문재인당도 아닌 정의당, 그것도 옛나 지금이나 여전히 반대하는 김… https://t.co/7LgflW4EJK"
    sentence_result = p.sentiment_analysis(sentence)

    print("부정: %f, 긍정: %f" % (sentence_result[0], sentence_result[1]))

if __name__ == "__main__":
    main()
"""
