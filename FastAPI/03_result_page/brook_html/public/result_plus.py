from fastapi import FastAPI, Request
import uvicorn
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

import sys
import os
os.chdir(os.path.dirname(__file__))
root = os.path.dirname(os.path.abspath(__file__))
app = FastAPI()
templates = Jinja2Templates(directory='./')


origins = ["*"]
app.mount("/static", StaticFiles(directory=os.path.join(root, 'static')), name='static')
#app.mount("/css", StaticFiles(directory=os.path.join(root, 'css')), name='css')
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Info(BaseModel):
    title: str
    genre: str
    director: str
    plot: str

@app.get("/")
def hello():
    return 

movie_info = []
movie_info.append(Info(
                title = "겨울왕국",
                genre = "애니메이션, 어드밴쳐, 가족, 로맨스",
                director = "Chris Buck, Jennifer Lee",
                plot = "아렌델 왕국의 두 공주, 어릴 때부터 무엇이든 얼릴 수 있는 신비한 마법의 힘을 가지고 태어난 엘사와 그녀의 여동생 안나는 누구보다 친한 자매다. \
                    그러나 어린 시절 엘사의 마법으로 인해 안나가 다치게 되고 그녀의 부모님은 마법의 위험성을 트롤에게 전해 듣고 엘사의 마법을 감추려 외부와 어떠한 접촉도 할 수 없게 한다. \
                    심지어 하나뿐인 여동생 안나까지도. 안나를 다치게 한 것이 죄책감이 되어 엘사는 안나와 거리를 두며 누구보다 가깝던 두 자매 사이는 멀어진다. \
                    세월이 흐르고, 아버지와 어머니가 타고 가던 배가 폭풍우를 만나 침몰사고로 급작스레 부모님이 돌아가신 뒤 언니 엘사는 왕국의 후계자로서 대관식을 치르고 여왕의 자리에 오르게 된다. \
                    그러나 대관식 날 밤, 안나와의 말다툼 도중 엘사의 비밀은 온 세상에 드러나고 통제할 수 없는 자신의 능력이 사람들을 다치게 하는 것을 두려워한 엘사는 모든 것을 내려놓고 어딘가로 사라진다. \
                    한편 엘사가 떠난 뒤 아렌델 왕국은 완전히 얼어붙게 되어 극심한 겨울이 닥쳐온다. 동생 안나는 언니 엘사를 찾아 모든 일을 해결하기 위해 모험을 나서게 되는데…"
))
print(movie_info)

@app.get("/result/",  response_class=HTMLResponse)
async def show_result(request: Request):
    results = []
    for info in movie_info:
        results.append({'title': info.title,
                    'genre': info.genre,
                    'director': info.director,
                    'plot': info.plot
                    })
    print(results)
    
    return templates.TemplateResponse('result_plus_bootstrap.html', {"request": request, "data": results})


if __name__=='__main__':
    uvicorn.run(app, host="0.0.0.0", port=8000)