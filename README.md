# py-nlp-sentiment

[nsmc](https://github.com/e9t/nsmc) 자료를 이용하여 나이브 베이즈 분류법으로 문장으로부터 긍/부정 의 결과와 그에 따른 관련 단어가 얼마나 자주 등장하는지 빈도수를 알기 위해 제작한 프로그램

모델 뿐만 아니라 특정 단어와 시작/종료날짜를 입력하면 트위터의 스트리밍 API 를 이용하여 mongodb 로 실시간으로 데이터를 수집하고, 수집한 데이터를 토대로 단어를 나누어 긍/부정 결과를 알 수 있도록 하였다.
