#!/usr/bin/env python
#-*- coding: utf-8 -*-

"""
- 트위터 트윗 수집기 (Collect Twitter Twits)

Author By. Karsei
"""

CONSTANTS_PROGRAM_VERSION = "1.2"

"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
* IMPORT SETTING
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
# 문자 인코딩과 시스템 입력 관련
import sys
#reload(sys)
#sys.setdefaultencoding("utf8")*/

# json 포멧 관련
import json

# 수집 시 날짜 출력
import time, datetime

"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
* SOCKET
* http://jonnung.blogspot.kr/2014/10/python-socket-chat-programing.html
* https://www.reddit.com/r/learnpython/comments/35mruv/help_trying_to_write_a_simple_tcp_serverclient/
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
import socket
from select import *

HOST = 'localhost'
PORT = 3001
BUFSIZE = 1024
ADDR = (HOST, PORT)

"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
* THREAD
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
import nlp_thread

"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
* 메인
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
# 키워드 목록
workList = []
def checkWorkList(keyword):
    chk = False
    for item in workList:
        if item['searchWord'] == keyword:
            chk = True
            break
    return chk

def main():
    # 소켓 객체 생성
    serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # 옵션 설정 (연결 해제 시 바로 연결할 수 있도록)
    serverSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    # 소켓 정보 바인드
    serverSocket.bind(ADDR)

    # 클라이언트 요청 대기
    serverSocket.listen(10)
    # 클라이언트 소켓 목록
    clientSockets = set()

    print ('-------------------------------------------------------------')
    print (' Twitter Collector (v%s)' % CONSTANTS_PROGRAM_VERSION)
    print (' (c) 2017 Karsei')
    print (' ')
    print (' 수집 서버가 실행되었습니다. %s 포트로 접속을 기다립니다.' % str(PORT))
    print ('-------------------------------------------------------------')

    while True:
        try:
            #print "[INFO] 요청을 기다립니다..."
            # SELECT로 요청을 받고 10초마다 블럭킹을 해제하도록 함
            read_socket, write_socket, error_socket = select([serverSocket] + list(clientSockets), [], [], 10)

            for sock in read_socket:
                if sock == serverSocket:
                    # 새로운 접속
                    clientSocket, addr_info = serverSocket.accept()
                    clientSockets.add(clientSocket)
                    clientSocket.send('수집기 :: 서버에 정상적으로 연결되었습니다.'.encode('utf-8'))
                    print ('[INFO] 클라이언트(%s:%s)가 새롭게 연결되었습니다.' % (addr_info[0], addr_info[1]))
                else:
                    # 접속한 사용자로부터 새로운 데이터 받음
                    data = sock.recv(BUFSIZE)
                    data_decoded = data.decode('utf-8')

                    if data:
                        print ('[INFO] 클라이언트로부터 데이터를 전달받았습니다: %s' % data_decoded)
                        checkCommand(data_decoded, sock)
                    else:
                        clientSockets.remove(sock)
                        sock.close()
        except (OSError, socket.error) as err:
            print (err)
        except KeyboardInterrupt:
            print ('[INFO] 서버 소켓을 종료합니다...')

            # 부드럽게 종료하기
            serverSocket.close()

            # 모든 스레드 종료하기
            for item in workList:
                item['workthread'].doExit()
                workList.remove(item)

            sys.exit()


def checkCommand(socketData, socketClient):
    lines_arg = socketData.split(' ')

    # 명령어 구분
    if lines_arg[0] == 'start':
        # 인자값 받기
        if len(lines_arg) < 5:
            socketClient.send('수집기 :: 사용법 -> start KEYWORD_NAME COLLECTION_NAME START_DATE(unix) END_DATE(unix)'.encode('utf-8'))
            print ('[INFO] 클라이언트가 요청한 명령어 파라메터가 적습니다. - %s' % socketData)
            return

        # 이미 있는 경우 걸러냄
        if checkWorkList(lines_arg[1]):
            socketClient.send('수집기 :: 이미 등록된 키워드입니다.'.encode('utf-8'))
            print ('[INFO] 클라이언트가 이미 등록된 키워드 작업 요청을 하였습니다. - %s' % lines_arg[1])
            return

        ### 파라메터 이름 명명
        sys_searchWord = lines_arg[1]
        sys_dbName = lines_arg[2]

        ### 날짜
        # DEBUG
        start_date = int(time.mktime(datetime.datetime.now().timetuple()) * 1000)
        end_date = int(time.mktime((datetime.datetime.now() + datetime.timedelta(seconds = 20)).timetuple()) * 1000)
        # PRODUCTION
        #start_date = int(lines_arg[3])
        #end_date = int(lines_arg[4])

        ### 결과 정리를 위한 변수
        #search_word = u'새해'
        search_word = sys_searchWord                # 검색할 단어

        ## 쓰레드 설정
        thList = nlp_thread.MakeCollectThread(search_word, start_date, end_date, sys_dbName)

        ### 정리
        workset = {}
        workset['searchWord'] = sys_searchWord
        workset['startDate'] = start_date
        workset['endDate'] = end_date
        workset['workthread'] = thList
        workset['dbName'] = sys_dbName
        workset['status'] = 1
        workList.append(workset)

        ##### 시작!!!
        socketClient.send(('수집기 :: 수집이 시작되었습니다 - %s' % search_word).encode('utf-8'))
        print ('[INFO] 수집이 시작되었습니다 - %s' % search_word)

        return
        """
        lock = threading.Lock()
        th.start()
        print 'TEST THREAD'
        time.sleep(1)

        th.doSuspend()
        with lock:
            print 'Suspend Thread...'
        time.sleep(15)

        th.doResume()
        with lock:
            print 'Resume Thread...'
        time.sleep(5)

        th.doExit()
        """

    elif lines_arg[0] == 'stop':
        # 인자값 받기
        if len(lines_arg) < 2:
            socketClient.send('수집기 :: 사용법 -> stop KEYWORD_NAME'.encode('utf-8'))
            print ('[INFO] 클라이언트가 요청한 명령어 파라메터가 적습니다. - %s' % socketData)
            return

        KEYWORD = lines_arg[1];
        count = 0

        for item in workList:
            # 알맞는 키워드 찾음
            if item['searchWord'] == lines_arg[1]:
                # 유효성 검사
                count += 1
                # 기존에 실행되던 스레드 종료
                item['workthread'].getCollectThread().doExit()
                item['workthread'].doExit()
                # 작업정지 상태로 변경
                item['status'] = 0

                # 컬렉션 삭제
                item['workthread'].deleteCurrentKeyword()

                # 스레드 초기화
                del item['workthread']
                # 해당 스레드를 작업 목록에서 지움
                workList.remove(item)

                socketClient.send(('수집기 :: 수집이 정지되었습니다. - %s' % KEYWORD).encode('utf-8'))
                print ('[INFO] 수집이 정지되었습니다. - %s' % KEYWORD)
                break

        if count == 0:
            socketClient.send(('수집기 :: 수집 작업 목록에 존재하지 않습니다. - %s' % KEYWORD).encode('utf-8'))
            print ('[INFO] 클라이언트가 수집 작업 목록에 존재하지 않는 키워드 작업 정지 요청을 했습니다. - %s' % KEYWORD)

        return
    elif lines_arg[0] == 'list':
        print (workList)
        return
    elif lines_arg[0] == 'help':
        print ('')
        return
    elif lines_arg[0] == 'exit':
        sys.exit()
    elif lines_arg[0] == '':
        return
    else:
        socketClient.send(('수집기 :: %s 는(은) 지원하지 않는 명령어입니다.' % lines_arg[0]).encode('utf-8'))
        print ('[INFO] 클라이언트가 지원하지 않는 명령어를 요청했습니다. - %s' % lines_arg[0])
        return

# 프로세스 시작
if __name__ == '__main__':
    main()
