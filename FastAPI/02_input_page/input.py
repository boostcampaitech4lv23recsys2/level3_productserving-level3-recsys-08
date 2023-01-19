from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field
from typing import List
from PIL import Image
import uvicorn

app = FastAPI()

class user_info(BaseModel):
    MBTI : str
    enneagram : str
    movie_list : List[int]

Info = user_info
Info.movie_list = [73141,122470,152081]
templates = Jinja2Templates(directory='./')

@app.get("/",response_class = HTMLResponse)
def insert_info_form(request: Request):
    return templates.TemplateResponse('template.html',context = {'request':request})

@app.get("/print")
def get_info():
    
    return {
        "MBTI" : Info.MBTI,
        "enneagram": Info.enneagram,
        "movie list" : Info.movie_list
    }

@app.post("/")
def insert_info(request: Request, MBTI: str = Form(...), enneagram: str = Form(...)):
    Info.MBTI = MBTI
    Info.enneagram = enneagram

    return templates.TemplateResponse('template.html',context = {'request':request})

if __name__ == '__main__':
    uvicorn.run(app, host="0.0.0.0", port=8000)