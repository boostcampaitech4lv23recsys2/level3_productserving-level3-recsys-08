import os
import sys
from fastapi import FastAPI, Form, Request
from pydantic import BaseModel, Field
from typing import List
from PIL import Image
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import uvicorn
from fastapi.staticfiles import StaticFiles
sys.path.append('../..')
from Utils import user_input_to_recommend
from pathlib import Path
import pandas as pd


app = FastAPI()
app.mount(
    "/static",
    StaticFiles(directory=Path(__file__).parent.absolute() / "static"),
)
templates = Jinja2Templates(directory='./')


class Character(BaseModel):
    name: str
    movie: str
    img_path: str
    similarity: int

class user_info(BaseModel):
    MBTI : str
    engram_list : List[str]
    engram : str
    movie_list : List[int]

Info = user_info
# Info.movie_list = [1704, 1721, 2021, 72998, 73141, 91500, 164909]
Info.movie_list = ['111_taxi_driver', '253_interview_with_the_vampire', '421_black_beauty', '588_aladdin', '595_beauty_and_the_beast', '628_primal_fear', '4334_yi_yi']
# templates = Jinja2Templates(directory='./')

# main 페이지
@app.get('/')
def main(request: Request):
    return templates.TemplateResponse('main.html', context={'request':request})

# mbti 선택 페이지
@app.get("/mbti",response_class = HTMLResponse)
def insert_info_form(request: Request):
    return templates.TemplateResponse('mbti.html', context = {'request':request})

# enneagram test 페이지1
@app.post('/enneagram', response_class = HTMLResponse)
def insert_engram(request: Request, MBTI: str = Form(...)):
    print(MBTI)
    Info.MBTI = MBTI
    return templates.TemplateResponse('enneagram.html', context={'request' : request})

# enneagram test 페이지2
@app.post('/enneagram2', response_class = HTMLResponse)
def insert_engram2(request: Request, enneagram1: str = Form(...)):
    print(enneagram1)
    Info.engram_list = [enneagram1]
    return templates.TemplateResponse('enneagram2.html', context={'request' : request})

# enneagram test 페이지3
@app.post('/enneagram3', response_class = HTMLResponse)
def insert_engram3(request: Request, enneagram2: str = Form(...)):
    print(enneagram2)
    Info.engram_list.append(enneagram2)
    engram_crite = ''.join(Info.engram_list)
    df = pd.read_csv('enn.csv')
    add_quest = df[df.base==engram_crite][['question','three_letter']].copy()
    add_quest_list = add_quest.to_dict(orient='records')
    print(engram_crite)
    print('>>>',add_quest_list)
    return templates.TemplateResponse('enneagram3.html', context={'request' : request, "add_quest_list":add_quest_list})

# 선호 영화 선택 페이지
@app.post('/movie', response_class=HTMLResponse)
def insert_movie(request:Request, enneagram3: str = Form(...)):
    Info.engram = enneagram3
    print(Info.engram)
    
    return templates.TemplateResponse('movie.html', context={'request':request, "movies":Info.movie_list, "length":len(Info.movie_list)})

# 결과 페이지
@app.post("/result")
def insert_info(request: Request, movies: List = Form(...)):
    print(movies)
    # result = user_input_to_recommend(Info.MBTI, Info.engram_list, Info.movie_list)
    # cols=['Character','Contents','MBTI','img_src','Enneagram_sim']
    # result_list = result[cols].to_dict(orient='records')
    result_list = [{'Character': 'Will Hunting', 
    'Contents': 'Good Will Hunting (1997)', 
    'MBTI': 'INTP', 
    'img_src': 'https://static1.personality-database.com/profile_images/6bf8c8864ce546d08b69e039847fb4bd.png', 
    'Enneagram_sim': 0.719973601967801}, 
    {'Character': 'Walt Berkman', 
    'Contents': 'The Squid and the Whale', 
    'MBTI': 'INTP', 
    'img_src': 'https://static1.personality-database.com/profile_images/c159ca9253354979a908d5159b92f140.png', 
    'Enneagram_sim': 0.719973601967801}, 
    {'Character': 'Yusuf', 
    'Contents': 'Inception (2010)', 
    'MBTI': 'INTP', 
    'img_src': 'https://static1.personality-database.com/profile_images/0f9bda83c5ff4ce2807772818e8adc4a.png', 
    'Enneagram_sim': 0.719973601967801}, 
    {'Character': 'Brian May', 
    'Contents': 'Bohemian Rhapsody (2018)', 
    'MBTI': 'INTP', 
    'img_src': 'https://static1.personality-database.com/profile_images/c53bc6b3b9814b768fe2b070ea0f957e.png', 
    'Enneagram_sim': 0.719973601967801}, 
    {'Character': 'Dr. Cornelius', 
    'Contents': 'Planet of the Apes (1968)', 
    'MBTI': 'INTP', 
    'img_src': 'https://static1.personality-database.com/profile_images/70b3d8bdccb4460cb43519079a416124.png', 
    'Enneagram_sim': 0.5097201729093104}, 
    {'Character': 'Haymitch Abernathy',
    'Contents': 'The Hunger Games (Franchise)',
     'MBTI': 'INTP', 
     'img_src': 'https://static1.personality-database.com/profile_images/a5d118d82c0c46a4a573a9bc485a80ae.png', 
     'Enneagram_sim': 0.5097201729093104}, 
     {'Character': 'John Nash', 
     'Contents': 'A Beautiful Mind (2001)', 
     'MBTI': 'INTP', 
     'img_src': 'https://static1.personality-database.com/profile_images/5cc46e9adfea43459adcc7e3e9687791.png', 
     'Enneagram_sim': 0.5097201729093104}, 
     {'Character': 'Dr. Nefario', 
     'Contents': 'Despicable Me (Franchise)', 
     'MBTI': 'INTP', 
     'img_src': 'https://static1.personality-database.com/profile_images/f51b68c368e747168775479e44cc0dac.png', 
     'Enneagram_sim': 0.5097201729093104}, 
     {'Character': 'Finch Crossley “Foxface”', 
     'Contents': 'The Hunger Games (Franchise)', 
     'MBTI': 'INTP', 
     'img_src': 'https://static1.personality-database.com/profile_images/e4f1d9ccf6f845b3a99f7a2155dd6aea.png', 
     'Enneagram_sim': 0.5097201729093104}, 
     {'Character': 'Beetee Latier', 
     'Contents': 'The Hunger Games (Franchise)', 
     'MBTI': 'INTP', 
     'img_src': 'https://static1.personality-database.com/profile_images/9afe330507b14f5c9f7a95d6678c3f8b.png', 
     'Enneagram_sim': 0.5097201729093104}]
    return templates.TemplateResponse('result_bootstrap.html', {"request": request, "data": result_list})

# @app.get("/result/detail{character_id}")
# def show_result_detail(request:Request, character_id:int):
#     character = db[character_id]
#     result = [{'name': character.name,
#                 'movie': character.movie,
#                 'img_path': character.img_path,
#                 'similarity': character.similarity
#                 }]
#     return templates.TemplateResponse('result_bootstrap.html', {"request": request, "data": result})



if __name__=='__main__':
    uvicorn.run("main:app", host="0.0.0.0", port=8001, reload=True)