from requests.exceptions import RequestException
from bs4 import BeautifulSoup

import pandas as pd
import requests
import re

section_to_label = {'IT':0, '과학':0, '경제':1, '사회':2, '생활':3, '문화':3, '세계':4, '스포츠':5, '정치':6}

def crawl(company_code:str, start:int, end:int, target:str):
    """NAVER뉴스의 기사를 크롤링해주는 함수

    Args:
        company_code (str): 언론사 코드(예시 : 연합뉴스 001, 조선일보 023)
        start (int): 탐색시작할 기사 코드
        end (int): 탐색종료할 기사 코드
        target (str): 찾고자 하는 레이블
    """
    curr_idx = 0
    
    file_name = f'{company_code}_train.csv'
    
    data = {'ID':[],
            'text':[], # title of article
            'target':[], # label of article,
            'url':[], # URL of article
            'date':[]} # written date of article
    
    for article_code in range(start, end+1, 5):
        article_code = str(article_code)
        article_code = '0'*(10-len(article_code)) + article_code
        
        id = f'crawl_train_{company_code}_{curr_idx}'
        
        URL = f'https://n.news.naver.com/mnews/article/{company_code}/{article_code}?sid=100'
        
        # 현재 크롤링 중인 URL확인
        print(URL)
        
        try:
            response = requests.get(URL)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # get 'title'
            title = soup.select_one('div.media_end_head_title h2#title_area')
            title = title.get_text(strip=True) if title else 'Title not found'
            
            # get 'label'
            label = soup.select_one('em.media_end_categorize_item')
            label = label.get_text(strip=True) if label else 'Label not found'
            
            # get 'date'
            date = soup.select_one('span[data-date-time]')
            date = date.get_text(strip=True) if date else 'Date not found'
            date_pattern = re.compile(r'(\d{4}\.\d{2}\.\d{2}\.\s[오전|오후]+\s\d{1,2}:\d{2})')
            date_match = date_pattern.search(date)
            if date_match:
                date = date_match.group()
                year = date.split('.')[0]
                year = int(year)
            else:
                date = "Date not found"
                year = 2020
            
            print(title)
            print(label)
            print(date)
            print(year)
            print(id)
            
            # 기사가 2021년 이후의 기사에, 원하는 섹션인 경우에만 포함
            if year > 2020 and label == target and curr_idx < 10000:
                    data['ID'].append(id)
                    data['text'].append(title)
                    data['target'].append( section_to_label[label] )
                    data['url'].append(URL)
                    data['date'].append(date)
                    curr_idx += 1
            
            
            # 20000개 채우면 실행시간 문제로 인해 가차없이 강제종료                
            if curr_idx == 10000:
                break
                
        except RequestException as e:
            print(f"Request failed: {e}")
            
    df = pd.DataFrame(data)
    df.to_csv(file_name, index=False)

def crawl_sport(company_code:str, start:int, end:int):
    """NAVER 스포츠 뉴스의 기사를 크롤링해주는 함수

    Args:
        company_code (str): 언론사 코드(예시 : 연합뉴스 001, 조선일보 023)
        start (int): 탐색시작할 기사 코드
        end (int): 탐색종료할 기사 코드
    """
    curr_idx = 0
    
    file_name = f'{company_code}_5_train.csv'
    
    data = {'ID':[],
            'text':[], # title of article
            'target':[], # label of article,
            'url':[], # URL of article
            'date':[]} # written date of article
    
    for article_code in range(start, end+1, 5):
        article_code = str(article_code)
        article_code = '0'*(10-len(article_code)) + article_code
        
        id = f'crawl_train_{company_code}_{curr_idx}'
        
        URL = f'https://sports.news.naver.com/news?oid={company_code}&aid={article_code}'
        
        # 현재 크롤링 중인 URL확인
        print(URL)
        
        try:
            response = requests.get(URL)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # 날짜 추출
            date_element = soup.select_one('.info > span')
            date = date_element.get_text(strip=True) if date_element else 'Date not found'
            date_pattern = re.compile(r'(\d{4}\.\d{2}\.\d{2}\.\s[오전|오후]+\s\d{1,2}:\d{2})')
            date_match = date_pattern.search(date)
            if date_match:
                date = date_match.group()
                year = date.split('.')[0]
                year = int(year)
            else:
                date = "Date not found"
                year = 2020

            # 제목 추출
            title_element = soup.select_one('.title')
            title = title_element.get_text(strip=True) if title_element else 'Title not found'
                        
            print(title)
            print(date)
            print(year)
            print(id)
            
            # 기사가 2021년 이후의 기사인 경우에만 포함
            if year > 2020 and curr_idx < 10000:
                    data['ID'].append(id)
                    data['text'].append(title)
                    data['target'].append(5)
                    data['url'].append(URL)
                    data['date'].append(date)
                    curr_idx += 1
            
            
            # 100000개 채우면 실행시간 문제로 인해 가차없이 강제종료                
            if curr_idx == 10000:
                break
                
        except RequestException as e:
            print(f"Request failed: {e}")
            
    df = pd.DataFrame(data)
    df.to_csv(file_name, index=False)
 
"""
[아래 6개의 URL구조]
f'https://n.news.naver.com/mnews/article/{company_code}/{article_code}?sid=100'
"""
# 정치 섹션에서 크롤링 가능한 조선일보(023)의 기사를 10000개 크롤링 함    
# crawl('023', 3600000, 3800000, '정치') #[재혁]이 이거 풀고 하면 됨  

# # 경제 섹션에서 크롤링 가능한 한국경제TV(215)의 기사를 10000개 크롤링 함
# crawl('215', 930000, 1145331, '경제') #[상기형]이 이거 주석 풀고 하면 됨

# # 사회 섹션에서 크롤링 가능한 국민일보(005)의 기사를 10000개 크롤링함
# crawl('005', 1400000, 1669570, '사회') #[건우형]이 이거 주석 풀고 하면 됨

# 생활/문화 섹션에서 크롤링 가능한 헬스조선(346)의 기사를 어느정도 크롤링 함(10000개가 어려울 수도 있을듯)
# crawl('346', 36000, 69689, '생활') #[재혁]이 이거 풀고 하면 됨 완료

# IT/과학 섹션에서 크롤링 가능한 지디넷코리아(092)의 기사를 어느정도 크롤링 함(10000개가 어려울 수도 있을듯)
# crawl('092', 2220000, 2319480, 'IT')  #[신근이형]이 이거 주석 풀고 하면 됨

# 세계 섹션에서 크롤링 가능한 조선일보(023)의 기사를 10000개 크롤링 함
# crawl('023', 3600000, 3800000, '세계') #[재혁]이 이거 풀고 하면 됨



"""
[아래 1개의 URL구조]
f'https://sports.news.naver.com/news?oid={company_code}&aid={article_code}'
"""
# 스포츠 섹션에서 크롤링 가능한 스포티비뉴스(477)의 기사를 10000개 크롤링함
# crawl_sport('477', 321043, 461043)


# 위에 사용된 모든 언론사는 'AI학습 이용금지'가 아님을 확인하고 사용함
