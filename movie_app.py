from flask import Flask, render_template, request
import json
import random
from selenium import webdriver as wb
from selenium.webdriver.common.by import By
import time
import requests

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

    driver.quit()

    return {
        "title": query,
        "poster": poster_url,
        "genre": genre,
        "description": desc_info,
    }

# 랜덤으로 3개의 영화 가져오기
def get_random_movies():
    with open("movies_data.json", "r") as file:
        movies_data = json.load(file)
    
    random_movies = []
    for year, movies in movies_data.items():
        random_movies.extend(movies)
    
    return random.sample(random_movies,5)

# 네이버 TV에서 영화 비디오 가져오기
def get_movie_video_url(movie_title):
    search_url = f"https://tv.naver.com/search?query={movie_title} 예고편"
    print(">>> search_url >> ", search_url)



    driver = wb.Chrome()
    driver.get(search_url)
    time.sleep(2)

    try:
        first_result = driver.find_element(By.CSS_SELECTOR, ".ClipHorizontalCardV2_link_thumbnail__QlHkv")
        first_result_url = first_result.get_attribute("href")
        
        driver.get(first_result_url)
        time.sleep(2)

        script_tag = driver.find_element(By.ID, "__NEXT_DATA__")
        #print("script_tag>> ", script_tag)

        json_data = script_tag.get_attribute("innerHTML")
        #print("json_data>> ", json_data)
        
        # JSON 데이터 파싱
        data = json.loads(json_data)
        #print("data>> ", data)
        
        #print("Video URL:", data['props']['pageProps']['vodInfo']['clip']['clipTrailerUrl']['mp4'])

        # 비디오 URL 추출
        video_url = data['props']['pageProps']['vodInfo']['clip']['clipTrailerUrl']['mp4']
    except Exception as e:
        video_url = None
        print(f"Error: {e}")

    driver.quit()
    return video_url


@app.route('/')
def index():
    random_movies = get_random_movies()
    
    # 각 영화의 비디오 URL 가져오기
    for movie in random_movies:
        movie["video_url"] = get_movie_video_url(movie["title"])
        
        #print("############ / 서버 디렉토리 진입 !!!!!!!!!!!")
        #print(">>>>>> ",  movie["video_url"])
        #print("movie >> ", movie)

    return render_template('movie_index.html', movies=random_movies)

@app.route('/movies/<year>')
def movies(year):
    with open("movies_data.json", "r") as file:
        movies_data = json.load(file)
    
    movies_list = movies_data.get(year, [])
    return render_template('movie_info.html', year=year, movies=movies_list)

@app.route('/search')
def movie_search():
    query = request.args.get("query")
    if not query:
        return render_template("movie_search.html", error="검색어를 입력하세요!")
    
    movie_data = get_movie_info(query)
    return render_template("movie_search.html", movie=movie_data)

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5050)
