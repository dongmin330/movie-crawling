from flask import Flask, render_template, request
import json
from selenium import webdriver as wb
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup as bs
import time
import os
import requests
import pandas as pd

app = Flask(__name__)

# 영화 검색 크롤링
def get_movie_info(query):
    """네이버에서 영화 정보를 크롤링하는 함수"""
    movie_url = "https://www.naver.com/"
    driver = wb.Chrome()  
    driver.get(movie_url)

    # 영화 검색
    search_box = driver.find_element(By.ID, "query")
    search_box.send_keys(f"영화 {query}")
    search_box.send_keys(Keys.ENTER)
    time.sleep(1)

    # 포스터 URL 가져오기
    try:
        poster = driver.find_element(By.CSS_SELECTOR, ".thumb._item img")
        poster_url = poster.get_attribute("src")  # 'href' → 'src'로 변경
    except:
        poster_url = "이미지를 찾을 수 없음"

    # 기본 정보 가져오기
    find_info_buttons = driver.find_element(By.CSS_SELECTOR, ".tab_list li+li a .menu")
    find_info_buttons.click()
    time.sleep(1)

    # 장르 가져오기
    genre = driver.find_element(By.CSS_SELECTOR, ".info.txt_4 div+div+div dt+dd").text

    # 시놉시스 가져오기
    desc_info = driver.find_element(By.CSS_SELECTOR, ".text._content_text").text

    # OTT 정보 가져오기 - 보러가기 클릭릭
    find_ott_buttons = driver.find_element(By.CSS_SELECTOR, ".button_watch")
    find_ott_buttons.click()
    time.sleep(1)

    ott_name_list = []
    ott_url_list = []
    ott_price_list = []

    # OTT 이름 가져오기
    try:
        ott_names = driver.find_elements(By.CSS_SELECTOR,".ott_list_area.state_open li .thumb a")
        for name in ott_names:
            ott_name_list.append(name.get_attribute("class"))  # 'class' → 'alt' 변경
    except:
        ott_name_list.append("OTT 정보를 가져올 수 없음")

    if "ico_n_plus" in ott_name_list:
        ott_name_list.remove("ico_n_plus")
    if "link" in ott_name_list:
        ott_name_list.remove("link")

    # OTT 링크 가져오기
    try:
        ott_links = driver.find_elements(By.CSS_SELECTOR,".ott_list_area.state_open li .price_area a")
        for link in ott_links:
            ott_url_list.append(link.get_attribute("href") or "링크 없음")
    except:
        ott_url_list.append("링크 정보를 가져올 수 없음")

    # OTT 가격 가져오기
    try:
        ott_prices = driver.find_elements(By.CSS_SELECTOR, ".ott_list_area.state_open li .price_area .info_price .text")
        for price in ott_prices:
            ott_price_list.append(price.text)
    except:
        ott_price_list.append("가격 정보를 가져올 수 없음")

    driver.quit()

    print("OTT 플랫폼:", ott_name_list)
    print("OTT 링크:", ott_url_list)
    print("OTT 가격:", ott_price_list)
    
    return {
        "title": query,
        "poster": poster_url,
        "genre": genre,
        "description": desc_info,
        "ott_names": ott_name_list,
        "ott_links": ott_url_list,
        "ott_prices": ott_price_list
    }


# 연도별 영화 데이터 json 열기(임시 데이터, 실제 데이터는 API 또는 DB 활용 가능)
with open("movies_data.json","r") as file :
    movies_data = json.load(file)

@app.route('/')
def index():
    return render_template('movie_index.html')

@app.route('/movies/<year>')
#  <> : 변수를 지칭 
def movies(year):
    movies_list = movies_data.get(year, [])
    return render_template('movie_info.html', year=year, movies=movies_list)

@app.route('/search')
def movie_search():
    query = request.args.get("query")  # 사용자가 입력한 검색어 가져오기
    if not query:
        return render_template("movie_search.html", error="검색어를 입력하세요!")
    
    movie_data = get_movie_info(query)
    # 크롤링된 영화 정보를 'movie'로 전달
    return render_template("movie_search.html", movie=movie_data)

if __name__ == '__main__':
    app.run(host="0.0.0.0")


