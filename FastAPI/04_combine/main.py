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


app = FastAPI()
app.mount(
    "/css",
    StaticFiles(directory=Path(__file__).parent.absolute() / "css"),
)
templates = Jinja2Templates(directory='./')


class Character(BaseModel):
    name: str
    movie: str
    img_path: str
    similarity: int

class user_info(BaseModel):
    MBTI : str
    enneagram : str
    movie_list : List[int]

Info = user_info
Info.movie_list = [1704, 1721, 2021, 72998, 73141, 91500, 164909]
# templates = Jinja2Templates(directory='./')


@app.get("/",response_class = HTMLResponse)
def insert_info_form(request: Request):
    return templates.TemplateResponse('input.html',context = {'request':request})

@app.post('/enneagram', response_class = HTMLResponse)
def insert_enneagram(request: Request, MBTI: str = Form(...)):
    print(MBTI)
    Info.MBTI = MBTI
    return templates.TemplateResponse('enneagram.html', context={'request' : request})

@app.post("/result")
def insert_info(request: Request):
    enneagram = '1w9'
    Info.movie_list
    print(Info.MBTI, enneagram)
    result = user_input_to_recommend(Info.MBTI, enneagram, Info.movie_list)
    cols=['Character','Contents','MBTI','img_src','Enneagram_sim']
    result_list = result[cols].to_dict(orient='records')
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