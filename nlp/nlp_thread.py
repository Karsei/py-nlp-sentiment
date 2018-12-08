#!/usr/bin/env python
#-*- coding: utf-8 -*-

"""
- 트위터 트윗 수집기
-- 스레드 할당 및 작업

Author By. Karsei
"""

import time, datetime

"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
* pprint
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
# 예쁘게 출력
import pprint

"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
* LOGGER
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
import nlp_logger

"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
* DB
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
import nlp_db

"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
* COLLECT
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
import nlp_collect

"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
* PREPROCESSING
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
import nlp_preprocess

"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
* SENTIMENT ANALYSIS
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
import nlp_sentiment

"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
* TWITTER STREAMING
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
# 트위터 스트리밍
import tweepy
from tweepy import OAuthHandler
from tweepy import Stream

# 트윗 과부하 방지를 위한 예외 처리
#from http.client import IncompleteRead # Python 2
#from httplib import IncompleteRead #Python 3
from requests.packages.urllib3.exceptions import ProtocolError

# 트위터 API를 이용하기 위한 Key
CONSUMER_KEY = 't3BbVMuIzeT4X87HXVnuYrqdY'
CONSUMER_SECRET = 'BIpqobHxeC628AxHVojDczlUxhAztNCMQMWmSU98yKmlNwxBo7'
OAUTH_ACCESS_TOKEN = '799211221710880769-pxTTp0tSaN3o8hwuzr7Jq1ogvbavfpm'
OAUTH_ACCESS_SECRET = 'ziIKJQ08N8emrGoDKDo7zoFIfMB6KTEzjbzKEpo4u8ZAI'

### 트위터 API 설정
twitter_auth = OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
twitter_auth.set_access_token(OAUTH_ACCESS_TOKEN, OAUTH_ACCESS_SECRET)
twitter_api = tweepy.API(twitter_auth)


"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
* THREAD
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
# 쓰레딩
import threading

# 스레드 초기화
def MakeCollectThread(searchWord, startDate, endDate, dbName):
    mThread = ManageThread(startDate, endDate, searchWord, dbName)
    mThread.start()
    return mThread

# http://bbolmin.tistory.com/164
# http://hashcode.co.kr/questions/2186/%ED%8C%8C%EC%9D%B4%EC%8D%AC%EC%97%90%EC%84%9C-%EC%93%B0%EB%A0%88%EB%93%9C%EB%A5%BC-%EC%A3%BD%EC%9D%BC-%EC%88%98-%EC%9E%88%EB%8A%94-%EB%B0%A9%EB%B2%95%EC%9D%B4-%EC%9E%88%EB%82%98%EC%9A%94
class CollectThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.__suspend = False
        self.__exit = False

        self.log = nlp_logger.LogWriter()       # 로그 작성
        self.twitter_stream = None              # 트위터 스트리밍
        self.twitter_stream_lis = None          # 트위터 스트리밍 핸들러

        self.search_word = ""                   # 수집 단어
        self.start_date = 0                     # 수집 시작 날짜
        self.end_date = 0                       # 수집 종료 날짜

        self.retry_count = 0                    # 재시도 횟수
        self.total_count = 0                    # 수집된 갯수

    # 수집 단어 설정
    def setSearchWord(self, keyword):
        self.search_word = keyword

    # 수집 단어 가져오기
    def getSearchWord(self):
        return self.search_word

    # 수집 날짜 섲렁
    def setDate(self, startDate, endDate):
        self.start_date = startDate
        self.end_date = endDate

    # 수집 날짜 가져오기
    def getDate(self):
        return { startDate: self.start_date, endDate: self.end_date }

    # 리스너 생성
    def makeListener(self, dbName):
        if self.search_word == "":
            self.log.e("수집 단어가 설정되지 않았습니다.")
            return

        if self.start_date == 0 or self.end_date == 0:
            self.log.e("수집 날짜가 설정되지 않았습니다.")
            return

        if dbName == None:
            self.log.e("저장할 데이터베이스가 설정되지 않았습니다.")
            return

        ### 수집 설정
        self.twitter_stream_lis = nlp_collect.TwitterStreamer()
        self.twitter_stream_lis.setSearchWord(self.search_word)             # 수집 단어 설정
        self.twitter_stream_lis.setDate(self.start_date, self.end_date)     # 슈집 날짜 설정
        self.twitter_stream_lis.setResultCount(self.total_count)            # 이전에 얻었던 메세지 갯수 갱신
        self.twitter_stream_lis.setDatabaseName(dbName)                     # 저장 데이터베이스 이름 설정

    # 스트리밍 생성
    def makeStream(self):
        if self.twitter_stream_lis == None:
            self.log.e("스트리밍을 수행할 리스너가 설정되지 않았습니다.")
            return

        self.twitter_stream = nlp_collect.Stream(auth=twitter_auth, listener=self.twitter_stream_lis)

    # 쓰레드 실행
    def run(self):
        while True:
            try:
                while self.__suspend:
                    time.sleep(0.5)

                if self.__exit:
                    self.twitter_stream.disconnect()
                    break

                self.twitter_stream.filter(track=[self.search_word])
            except KeyError as err:
                ## 키 오류로 중단되면 다시 연결한 후 수집 이어서 하기
                # 재시도 횟수 증가
                self.retry_count += 1

                #이전까지 획득한 메세지 갯수 갱신
                self.total_count = self.twitter_stream_lis.getResultCount()

                self.log.e("KeyError - 다시 시도... (횟수 " + str(self.retry_count) + "번)")
                self.log.e("이유: " + str(err))
                continue
            except (ProtocolError, e) as err:
                ## 끊어지면 다시 연결한 후 수집 이어서 하기
                # 재시도 횟수 증가
                self.retry_count += 1

                #이전까지 획득한 메세지 갯수 갱신
                self.total_count = self.twitter_stream_lis.getResultCount()

                self.log.e("IncompleteRead - 다시 시도... (횟수 " + str(self.retry_count) + "번)")
                continue
            except KeyboardInterrupt:
                # 스트리밍 연결 종료
                self.twitter_stream.disconnect()

                #이전까지 획득한 메세지 갯수 갱신
                self.total_count = self.twitter_stream_lis.getResultCount()

                # 통계 출력
                self._showResult()
                break
            except (Exception, msg) as err:
                self.log.e("예상하지 못한 오류가 발생했습니다.")
                self.log.e("이유: " + str(err))

                ## 끊어지면 다시 연결한 후 수집 이어서 하기
                # 재시도 횟수 증가
                self.retry_count += 1

                #이전까지 획득한 메세지 갯수 갱신
                self.total_count = self.twitter_stream_lis.getResultCount()

                self.log.e("Exception - 다시 시도... (횟수 " + str(self.retry_count) + "번)")
                continue

    # 쓰레드 중단
    def doSuspend(self):
        #self.twitter_stream.disconnect()
        self.__suspend = True

    # 쓰레드 재개
    def doResume(self):
        #self.twitter_stream.filter(track=[self.search_word])
        self.__suspend = False

    # 쓰레드 종료
    def doExit(self):
        self.twitter_stream.disconnect()
        self.__exit = True

    # 결과물 출력
    def _showResult():
        # 시간 계산
        #end_date = datetime.now()
        totaltime = self.end_date - self.start_date

        # 출력
        print (' ')
        self.log.custom("통계", "- 검색 단어 :: {0:s}", self.search_word)
        self.log.custom("통계", "- 메세지 확인 갯수 :: {0:s}개", str(self.total_count))
        self.log.custom("통계", "- 재시도 횟수 :: {0:s}개", str(self.retry_count))
        self.log.custom("통계", "- 시작 시간 :: {0:s}", self.start_date.strftime('%Y-%m-%d %H:%M:%S'))
        self.log.custom("통계", "- 종료 시간 :: {0:s}", self.end_date.strftime('%Y-%m-%d %H:%M:%S'))
        self.log.custom("통계", "- 걸린 시간 :: %s일 %.2d시간 %.2d분 %.2d초" % (totaltime.days, totaltime.seconds // 3600, (totaltime.seconds // 60) % 60, totaltime.seconds % 60))



class ManageThread(threading.Thread):
    def __init__(self, startDate, endDate, searchWord, dbName):
        threading.Thread.__init__(self)
        self.__suspend = False
        self.__exit = False

        self.step = 0                                       # 실행 단계

        # 전처리기 설정
        self.preprocess = nlp_preprocess.SentenceProcessing()
        self.sentiment = nlp_sentiment.SentimentProcessing()

        # 키워드 데이터베이스
        self.keywordDatabase = nlp_db.db_database['collectKeywordList']
        self.rawDatabase = nlp_db.db_database[dbName]
        self.bowDatabase = nlp_db.db_database[dbName + '_BoW']
        self.sentimentDatabase = nlp_db.db_database[dbName + '_Sentiment']
        self.resultDatabase = nlp_db.db_database[dbName + '_Result']

        self.start_date = startDate                         # 시작 날짜
        self.end_date = endDate                             # 종료 날짜
        self.search_word = searchWord                       # 키워드
        self.database_name = dbName                         # 데이터베이스 이름

        # 수집 설정
        self.collectThread = CollectThread()                # 수집 스레드 생성
        self.collectThread.setSearchWord(searchWord)        # 수집 단어 설정
        self.collectThread.setDate(startDate, endDate)      # 수집 날짜 설정
        self.collectThread.makeListener(dbName)             # 리스너 생성
        self.collectThread.makeStream()                     # 스트림 생성

        self.buffer = 0                                     # 버퍼

    # 단계 가져오기
    def getStep(self):
        return self.step

    # 키워드 현황 데이터베이스 가져오기
    def getKeywordDatabase(self):
        return self.keywordDatabase

    # 수집 날짜 가져오기
    def getDate(self):
        return { "startDate": self.start_date, "endDate": self.end_date }

    # 수집 키워드 로드
    def getCollectKeyword(self):
        return self.search_word

    # 수집 스레드 가져오기
    def getCollectThread(self):
        return self.collectThread

    # 전처리 스레드 가져오기
    def getPreprocessThread(self):
        return self.preprocessThread

    def deleteCurrentKeyword(self):
        self.getKeywordDatabase().remove({ 'keyword': self.search_word })

    # 수집 현황 데이터베이스 설정
    def updateKeywordDatabaseStatus(self, status):
        self.getKeywordDatabase().update(
            {'keyword': self.search_word},
                {'$set':
                    {'status': status}
            },
            upsert = True
        )

    # 통합 과정
    def doProcess(self, callback):
        print ('[INFO-MANAGETHREAD][%s] 분석 과정(빈도수, 감정분석)이 시작되었습니다.' % datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

        # 수집된 데이터베이스의 모든 값을 가져옴
        docs = self.rawDatabase.find({'keyword': self.search_word})
        docs_total = docs.count()
        docs_count = 0

        # 단어 갯수 파악
        for record in docs:
            # 진행중
            docs_count += 1

            # 문장을 가져온다
            document = record['text']

            # 토큰화
            token_result = self.preprocess.preprocess(document)
            # 감정분석 실시
            token_sentiment = self.sentiment.sentiment_analysis(document)

            # 빈도수 데이터베이스 업데이트
            for words in token_result:
                self.bowDatabase.update(
                    { 'word': words, 'keyword': self.search_word },
                    { '$inc': { 'count': 1 }},
                    upsert = True
                )

            # 감정분석 데이터베이스 업데이트
            self.sentimentDatabase.update(
                { 'id_str': record['id_str'], 'keyword': record['keyword'] },
                    {'$set':
                        {'timestamp': record['timestamp'],
                        'retweet': record['retweet'],
                        'retcount': record['retcount'],
                        'favcount': record['favcount'],
                        'quocount': record['quocount'],
                        'text': record['text'],
                        'user': {
                            'name': record['user']['name'],
                            'screenname': record['user']['screenname'],
                            'profileimage': record['user']['profileimage']
                        },
                        'sentiment': {
                            'positive': round(token_sentiment[1], 6),
                            'negative': round(token_sentiment[0], 6)
                        }
                    }
                },
                upsert = True
            )

            # 최종 결과 보고서 업데이트
            if token_sentiment[0] > token_sentiment[1]:
                self.resultDatabase.update(
                    { 'keyword': self.search_word, 'docs_count': docs_total },
                    { '$inc': {
                        'negative': 1,
                        'words_count': len(token_result)
                        }
                    },
                    upsert = True
                )
            else:
                self.resultDatabase.update(
                    { 'keyword': self.search_word, 'docs_count': docs_total },
                    { '$inc': {
                        'positive': 1,
                        'words_count': len(token_result)
                        }
                    },
                    upsert = True
                )

            print(document)
            print(token_result)
            print('부정: %f, 긍정: %f' % (token_sentiment[0], token_sentiment[1]))
            print('---------------------------- [%s] %d 중 %d 진행됨 (%d%%) ----------------------------' % (datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), docs_total, docs_count, (docs_count / docs_total) * 100))
            #p.printList(self.preprocess.dataPreprocess(record['text']))

        # 확인
        docs_count = 0
        docs = self.bowDatabase.find().sort('count', -1)
        for wordSet in docs:
            docs_count += 1
            if docs_count == 10:
                break

        callback()

    # 결과 확인
    def stepInc(self):
        print ('[INFO-MANAGETHREAD][%s] 분석 과정(빈도수, 감정분석)이 종료되었습니다.' % datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        self.step += 1

    # 쓰레드 실행
    def run(self):
        print ('[INFO-MANAGETHREAD][%s] 수집 관리 스레드가 생성되었습니다.' % datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

        # 수집 스레드 실행
        self.getCollectThread().start()
        # 데이터베이스 업데이트 - 수집 단계
        self.updateKeywordDatabaseStatus(2)
        print ('[INFO-MANAGETHREAD][%s] 수집 스레드가 실행되었습니다.' % datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

        while True:
            ### Suspend ###
            while self.__suspend:
                time.sleep(0.5)

            ### Process ###
            if self.step == 0:
                if int(time.mktime(datetime.datetime.now().timetuple()) * 1000) >= self.end_date:
                    # 수집 스레드 종료
                    self.getCollectThread().doExit()
                    # 전처리 과정으로 변경
                    self.step = 1
                    # 데이터베이스 업데이트 - 전처리 단계
                    self.updateKeywordDatabaseStatus(3)
                    print ('[INFO-MANAGETHREAD][%s] 수집이 종료되었습니다.' % datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
            elif self.step == 1:
                if self.buffer == 0:
                    self.buffer = 1
                    self.doProcess(self.stepInc)
            elif self.step == 2:
                # 데이터베이스 업데이트 - 종료 단계
                self.updateKeywordDatabaseStatus(4)
                print ('[INFO-MANAGETHREAD][%s] 수집 관리 스레드를 종료합니다.' % datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
                break

            ### Exit ###
            if self.__exit:
                break
    # 쓰레드 중단
    def doSuspend(self):
        #self.twitter_stream.disconnect()
        self.__suspend = True

    # 쓰레드 재개
    def doResume(self):
        #self.twitter_stream.filter(track=[self.search_word])
        self.__suspend = False

    # 쓰레드 종료
    def doExit(self):
        # 데이터베이스 업데이트 - 도중 정지
        if self.getCollectThread().isAlive():
            self.updateKeywordDatabaseStatus(0)
            print ('[INFO-MANAGETHREAD][%s] 수집이 도중 정지되었습니다.' % datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
            self.getCollectThread().doExit()

        print ('[INFO-MANAGETHREAD][%s] 수집 관리 스레드가 종료됩니다.' % datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        self.__exit = True
