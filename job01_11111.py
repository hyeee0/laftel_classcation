import re
import pandas as pd
import time
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException

category = ['음식', '음악', '이세계', '일상', '', '추리', '치유', '', '판타지']
pages = [50, 124, 138, 417, 0, 101, 130, 0, 1072]

options = webdriver.ChromeOptions()
options.add_argument('lang=kr_KR')
driver = webdriver.Chrome('./chromedriver', options=options)
df_title = pd.DataFrame()
url = 'https://laftel.net/finder'

for i in range(27, 28): # 음식 - 판타지
    titles = []
    multi_category = []
    driver.get(url)
    driver.maximize_window()

    category_xpath1 = '//*[@id="root"]/div/div[2]/div[2]/div[1]/div/div/div/div[1]/div[2]/div/div/div/div/section[1]/div[1]/div'  # 장르
    driver.find_element('xpath', category_xpath1).click()
    time.sleep(1)

    category_xpath2 = '//*[@id="modal-portal"]/div/div[2]/div[2]/div[{}]'.format(i)     # 카테고리 선택버튼
    driver.find_element('xpath', category_xpath2).click()
    time.sleep(1)

    category_xpath3 = '//*[@id="modal-portal"]/div/div[2]/div[1]/div[2]/button[2]'     # 확인버튼
    driver.find_element('xpath', category_xpath3).click()
    time.sleep(1)

    prev_height = driver.execute_script("return document.body.scrollHeight")

    while True:  # 무한스크롤 루프
        driver.execute_script("window.scrollTo(0,document.body.scrollHeight)")
        time.sleep(1)  # 페이지가 완전히 내려갈때까지 대기 -> 페이지 길이가 길면 시간을 증가시킨다
        curr_height = driver.execute_script("return document.body.scrollHeight")
        if (curr_height == prev_height):
            break
        else:
            prev_height = driver.execute_script("return document.body.scrollHeight")

    for j in range(281, pages[i-19]):
        title_xpath4 = '//*[@id="root"]/div/div[2]/div[2]/div[2]/div[3]/div[{}]/div/img'.format(j) # 이미지클릭해서 창 열게함
        title_xpath5 = '//*[@id="item-modal"]/div[1]/div/div[2]/div/header/h1' # 바깥 창의 제목
        driver.find_element('xpath', title_xpath4).click()
        time.sleep(5)

        category_xpath5 = '//*[@id="item-modal"]/div[1]/div/div[2]/div/header/div/span[1]' # 장르


        title = driver.find_element('xpath', title_xpath5).text
        mul_category = driver.find_element('xpath', category_xpath5).text


        title = re.compile('[^가-힣A-Za-z ]').sub(' ', title)
        print(title)
        titles.append(title)

        mul_category = re.compile('[^가-힣A-Za-z ]').sub(' ', mul_category)
        multi_category.append(mul_category)


        category_xpath7 = '//*[@id="item-modal"]/div[1]/div/div[2]/nav/button[2]' # 클릭
        driver.find_element('xpath', category_xpath7).click()


        if j % 10 == 0:     # 10개마다 저장
            df_section_title = pd.DataFrame(titles, columns=['titles'])
            df_section_multi_category = pd.DataFrame(multi_category, columns=['multi_category'])
            df_section_title['category'] = category[i-19]
            temp = pd.concat([df_section_title, df_section_multi_category], axis=1)
            df_title = pd.concat([df_title, temp], ignore_index=True)
            df_title.to_csv('./crawling_data_1/crawling_data_{}_{}.csv'.format(category[i-19], j), index=True)
            titles = []
            multi_category = []