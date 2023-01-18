from fastapi import FastAPI, Request
from pydantic import BaseModel
import uvicorn
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

app = FastAPI()
templates = Jinja2Templates(directory='./')


class Character(BaseModel):
    name: str
    movie: str
    img_path: str
    similarity: int


db = []
db.append(Character(name='이나현', movie='영화1', img_path='https://storage.cloud.google.com/jjanggu/%E1%84%8D%E1%85%A1%E1%86%BC%E1%84%8B%E1%85%A1.jpeg', similarity=100))
db.append(Character(name='전해리', movie='영화2', img_path='https://storage.cloud.google.com/jjanggu/%E1%84%8D%E1%85%A1%E1%86%BC%E1%84%80%E1%85%AE.jpeg', similarity=100))
db.append(Character(name='정의준', movie='영화3', img_path='https://storage.cloud.google.com/jjanggu/%E1%84%86%E1%85%A2%E1%86%BC%E1%84%80%E1%85%AE.jpeg', similarity=100))
db.append(Character(name='조원준', movie='영화4', img_path='https://storage.cloud.google.com/jjanggu/%E1%84%8E%E1%85%A5%E1%86%AF%E1%84%89%E1%85%AE.jpeg', similarity=100))
db.append(Character(name='채민수', movie='영화5', img_path='https://storage.cloud.google.com/jjanggu/%E1%84%8B%E1%85%B2%E1%84%85%E1%85%B5.jpeg', similarity=100))


@app.get("/result/")
async def show_result(request: Request):
    results = []
    for character in db:
        results.append({'name': character.name,
                        'movie': character.movie,
                        'img_path': character.img_path,
                        'similarity': character.similarity
                        })
    return templates.TemplateResponse('result_bootstrap.html', {"request": request, "data": results})


if __name__=='__main__':
    uvicorn.run(app, host="0.0.0.0", port=8000)