import os
import sys
import pandas as pd
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


app = FastAPI()
app.mount(
    "/static",
    StaticFiles(directory=Path(__file__).parent.absolute()/"static")
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
@app.post("/result", response_class=HTMLResponse)
def insert_info(request: Request, movies: List = Form(...)):
    movie_list = [int(i.split('_')[0]) for i in movies]
    result = user_input_to_recommend(Info.MBTI, Info.engram, movie_list)
    result = result[result.Enneagram_sim.notna()]
    print(result)
    result.Enneagram_sim = result.Enneagram_sim.map(lambda x: int(round(x*100)))
    cols=['Character','Contents','MBTI','img_src','Enneagram_sim']
    result_list = result[cols].to_dict(orient='records')
    return templates.TemplateResponse('result.html', context={"request": request, "data": result_list})

@app.get('/character/{character_name}', response_class=HTMLResponse)
async def character_info(request:Request, character_name):
    print(request)
    character ={
        'name': character_name,
        'movie' : 'Harry Potter',
        'img_path' : 'https://www.vintagemovieposters.co.uk/wp-content/uploads/2015/07/hpphilosopherquadlarge1.jpg',
        'similarity' : 100
    }
    print(character)
    return templates.TemplateResponse('character.html', context={'request':request, 'data': character})


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
    uvicorn.run("main:app", host="0.0.0.0", port=30001, reload=True)