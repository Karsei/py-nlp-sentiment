#!/usr/bin/env python
#-*- coding: utf-8 -*-

"""
- 트위터 트윗 수집기 (Collect Twitter Twits)
-- 트윗 수집기

Author By. Karsei
"""

# 문자 인코딩과 시스템 입력 관련
#import sys
#reload(sys)
#sys.setdefaultencoding("utf8")

"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
* BASIC SETTING
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
# 수집 시 날짜 출력
import time
from datetime import datetime

# json 포멧 관련
import json


"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
* TWITTER STREAMING
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
# 트위터 스트리밍
import tweepy
from tweepy import OAuthHandler
from tweepy import Stream
from tweepy.streaming import StreamListener


"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
* MongoDB
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
import nlp_db


"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
* 데이터 수집
 - 트위터 API를 이용한 스트리밍 데이터 획득
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
class TwitterStreamer(StreamListener):
    def __init__(self):
        # 수집할 단어가?
        self.searchWord = None
        # 수집된 갯수가?
        self.resultCount = 0
        # 저장할 데이터베이스 설정
        self.databaseName = None
        self.databaseCollection = None

        self.start_date = 0
        self.end_date = 0

        # 쓰레드 컨트롤
        #https://stackoverflow.com/questions/33498975/unable-to-stop-streaming-in-tweepy-after-one-minute
        super(TwitterStreamer, self).__init__()

    #def __del__(self):
        # 데이터베이스 연결 종료
        #nlp_db.db_connection.close()

    """""""""""""""""""""""""""""""""""""""""""""""
    # 수집 단어 얻기
    """""""""""""""""""""""""""""""""""""""""""""""
    def getSearchWord(self):
        return self.searchWord

    """""""""""""""""""""""""""""""""""""""""""""""
    # 수집 단어 설정
    """""""""""""""""""""""""""""""""""""""""""""""
    def setSearchWord(self, wordset):
        self.searchWord = wordset

    """""""""""""""""""""""""""""""""""""""""""""""
    # 수집된 갯수 얻기
    """""""""""""""""""""""""""""""""""""""""""""""
    def getResultCount(self):
        return self.resultCount

    """""""""""""""""""""""""""""""""""""""""""""""
    # 수집된 갯수 설정
    """""""""""""""""""""""""""""""""""""""""""""""
    def setResultCount(self, amount):
        self.resultCount = amount

    """""""""""""""""""""""""""""""""""""""""""""""
    # 데이터베이스 이름 얻기
    """""""""""""""""""""""""""""""""""""""""""""""
    def getDatabaseName(self):
        return self.databaseName

    """""""""""""""""""""""""""""""""""""""""""""""
    # 데이터베이스 이름 설정
    """""""""""""""""""""""""""""""""""""""""""""""
    def setDatabaseName(self, name):
        self.databaseName = name
        self.setDatabaseCollection(self.databaseName)

    """""""""""""""""""""""""""""""""""""""""""""""
    # 데이터베이스 컬렉션 얻기
    """""""""""""""""""""""""""""""""""""""""""""""
    def getDatabaseCollection(self):
        return self.databaseCollection

    """""""""""""""""""""""""""""""""""""""""""""""
    # 데이터베이스 컬렉션 설정
    """""""""""""""""""""""""""""""""""""""""""""""
    def setDatabaseCollection(self, name):
        #self.databaseCollection = nlp_db.db_database[self.getDatabaseName() + datetime.now().strftime('_%Y%m%d')]
        self.databaseCollection = nlp_db.db_database[self.getDatabaseName()]
        self.databaseCollection.create_index([("id_str", nlp_db.pymongo.DESCENDING)], unique=True)

    """""""""""""""""""""""""""""""""""""""""""""""
    # 수집 날짜 설정
    """""""""""""""""""""""""""""""""""""""""""""""
    def setDate(self, startDate, endDate):
        self.start_date = startDate
        self.end_date = endDate

    """""""""""""""""""""""""""""""""""""""""""""""
    # 수집 날짜 가져오기
    """""""""""""""""""""""""""""""""""""""""""""""
    def getDate(self):
        return { startDate: self.start_date, endDate: self.end_date }


    """""""""""""""""""""""""""""""""""""""""""""""
    # 간단한 정보를 위한 메서드
    """""""""""""""""""""""""""""""""""""""""""""""
    #def on_status(self, status):
    #    self.count += 1
    #    print str(self.count) + " - " + status.text

    """""""""""""""""""""""""""""""""""""""""""""""
    # 자세한 정보를 위한 메서드
    # https://stackoverflow.com/questions/24663403/stopping-tweepy-steam-after-a-duration-parameter-lines-seconds-tweets-etc
    """""""""""""""""""""""""""""""""""""""""""""""
    def on_data(self, data):
        try:
            # 데이터가 JSON이므로 JSON 형식으로 로드
            stm_json_load = json.loads(data)
        except (Exception, msg) as err:
            print ('[오류] 스트리밍 수집 오류: " + str(err)')
            return False

        if int(time.mktime(datetime.now().timetuple()) * 1000) >= self.end_date:
            return False
        elif int(time.mktime(datetime.now().timetuple()) * 1000) >= self.start_date:
            # 트윗 갯수 증가
            self.resultCount += 1

            # 데이터 정리
            stm_dict_dataset = {}
            stm_dict_dataset['keyword'] = self.searchWord
            if 'retweeted_status' in stm_json_load:
                stm_dict_dataset['id_str'] = stm_json_load['retweeted_status']['id_str']
                stm_dict_dataset['timestamp'] = stm_json_load['retweeted_status']['created_at']
                stm_dict_dataset['retweet'] = 1
                stm_dict_dataset['retcount'] = stm_json_load['retweeted_status']['retweet_count']
                stm_dict_dataset['favcount'] = stm_json_load['retweeted_status']['favorite_count']
                stm_dict_dataset['quocount'] = stm_json_load['retweeted_status']['quote_count']
                stm_dict_dataset['text'] = stm_json_load['retweeted_status']['text']
            else:
                stm_dict_dataset['id_str'] = stm_json_load['id_str']
                stm_dict_dataset['timestamp'] = stm_json_load['created_at']
                stm_dict_dataset['retweet'] = 0
                stm_dict_dataset['retcount'] = stm_json_load['retweet_count']
                stm_dict_dataset['favcount'] = stm_json_load['favorite_count']
                stm_dict_dataset['quocount'] = stm_json_load['quote_count']
                stm_dict_dataset['text'] = stm_json_load['text']

            # 유저 정보
            stm_dict_dataset['user'] = {}
            stm_dict_dataset['user']['name'] = stm_json_load['user']['name']
            stm_dict_dataset['user']['screenname'] = stm_json_load['user']['screen_name']
            stm_dict_dataset['user']['profileimage'] = stm_json_load['user']['profile_image_url']

            # 중복 값을 제거하기 위해 upsert 사용
            #self.databaseCollection.insert(stm_json_load)
            self.databaseCollection.update(
                { 'id_str': stm_dict_dataset['id_str'], 'keyword': stm_dict_dataset['keyword'] },
                    {'$set':
                        {'timestamp': stm_dict_dataset['timestamp'],
                        'retweet': stm_dict_dataset['retweet'],
                        'retcount': stm_dict_dataset['retcount'],
                        'favcount': stm_dict_dataset['favcount'],
                        'quocount': stm_dict_dataset['quocount'],
                        'text': stm_dict_dataset['text'],
                        'user': {
                            'name': stm_dict_dataset['user']['name'],
                            'screenname': stm_dict_dataset['user']['screenname'],
                            'profileimage': stm_dict_dataset['user']['profileimage']
                        }
                    }
                },
                upsert = True
            )
            
            #print "[수집중][%s]" % (datetime.now().strftime('%Y-%m-%d %H:%M:%S')) + stm_dict_dataset["text"]
            print ('[수집중][%s] 지금까지 %s개의 트윗 확인 (%s)' % ((datetime.now().strftime('%Y-%m-%d %H:%M:%S')), str(self.resultCount), self.getSearchWord()))

            return True
        else:
            return True

    """""""""""""""""""""""""""""""""""""""""""""""
    # 오류 메서드
    """""""""""""""""""""""""""""""""""""""""""""""
    def on_error(self, status):
        #Ref. https://dev.twitter.com/overview/api/response-codes
        print ('[오류] 스트리밍 오류가 발생했습니다! (코드 %s)' % str(status))
        if status == 420:
            #Ref. https://dev.twitter.com/rest/public/rate-limiting
            print ('[오류] 오류 코드 %s - Enhance Your Calm :: Rate 제한에 걸렸기 때문에 메세지를 받을 수 없습니다.' % str(status))
        elif status == 500:
            print ('[오류] 오류 코드 %s - Internal Server Error :: 흠, 뭔가 내부적으로 잘못된 것 같습니다!' % str(status))
        return True
