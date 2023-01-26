import os, sys, pickle, random
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
from pathlib import Path
## Custom library
from Utils import user_input_to_recommend, movie_select_2


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

movieId2poster_path='/opt/ml/project/Utils/Pickle/movieid_to_poster_file.pickle'
with open(movieId2poster_path,'rb') as f:
    movieId_to_posterfile = pickle.load(f)

ch2mv_path='/opt/ml/project/Utils/Pickle/characterId_to_movieId.pickle'
with open(ch2mv_path,'rb') as f:
    characterId_to_movieId = pickle.load(f)

mbti_df = pd.read_pickle('/opt/ml/project/Utils/Pickle/MBTI_merge_movieLens_3229_movie.pickle')
movie_genre_plot = pd.read_pickle('/opt/ml/project/Utils/Pickle/movie_genre_plot.pickle')
watch_link =  pd.read_pickle('/opt/ml/project/Utils/Pickle/watch_link_3229movie_4462_rows.pickle')

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
def insert_engram( request: Request, MBTI: str = Form(...)):
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
    # print(enneagram2)
    Info.engram_list.append(enneagram2)
    engram_crite = ''.join(Info.engram_list)
    df = pd.read_pickle('/opt/ml/project/Utils/Pickle/enneagram_question.pickle')
    add_quest = df[df.base==engram_crite][['question','three_letter']].copy()
    add_quest_list = add_quest.to_dict(orient='records')
    print(engram_crite)
    # print('>>>',add_quest_list)
    return templates.TemplateResponse('enneagram3.html', context={'request' : request, "add_quest_list":add_quest_list})

# 선호 영화 선택 페이지
@app.post('/movie', response_class=HTMLResponse)
def insert_movie(request:Request, enneagram3: str = Form(...)):
    Info.engram = enneagram3
    seed = random.randint(0,int(1e6))
    print(f">>>{seed = }")
    selec_movie_ids = movie_select_2(seed, 20)
    poster_file_list = [movieId_to_posterfile[id] for id in selec_movie_ids]
    return templates.TemplateResponse('movie.html', context={'request':request, "movies":poster_file_list, "length":len(poster_file_list)})

# 결과 페이지
@app.post("/result", response_class=HTMLResponse)
def insert_info(request: Request, movies: List = Form(...)):
    movie_list = [int(i.split('_')[0]) for i in movies]
    print(">>>>>>>",Info.MBTI, Info.engram, movie_list)
    result = user_input_to_recommend(Info.MBTI, Info.engram, movie_list)
    result = result[result.Enneagram_sim.notna()]
    print(">>>>>>>>>>",result)
    result.Enneagram_sim = result.Enneagram_sim.map(lambda x: int(round(x*100)))
    cols=['CharacterId','Character','Contents','MBTI','img_src','Enneagram_sim']
    result_list = result[cols].to_dict(orient='records')
    return templates.TemplateResponse('result.html', context={"request": request, "data": result_list})

# 캐릭터 상세페이지
@app.get('/character/{character_id}', response_class=HTMLResponse)
async def character_info(request:Request, character_id):
    print(character_id)
    need_cols=['Character','Contents','movieId']
    character_name, movie_title, movie_id = mbti_df[mbti_df.CharacterId==int(character_id)][need_cols].values[0]
    posterfile_path = movieId_to_posterfile[movie_id]
    genres, plot = movie_genre_plot[movie_genre_plot.movieId==movie_id][['ko_genres','ko_plot']].values[0]
    result_movie ={
        'name': character_name,
        'movie' : movie_title,
        'img_path' : posterfile_path,
        'genres' : genres,
        'plot' : plot
    }
    print(result_movie)
    links_df = watch_link[watch_link.movieId==movie_id][['platform','link']]
    links = links_df.to_dict(orient='records')
    print(links)
   
    return templates.TemplateResponse('result_movie.html', context={'request':request, 'data': result_movie, 'links' : links})




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