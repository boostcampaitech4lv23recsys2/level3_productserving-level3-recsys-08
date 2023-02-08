import os
from ast import literal_eval
import pandas as pd
from pathlib import Path
from environ import Env
import pickle
import warnings
warnings.filterwarnings('ignore')
from sqlalchemy import create_engine

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(os.curdir).resolve().parent.parent
env = Env()
env_path = BASE_DIR / "django/.env"
if env_path.exists():
    with env_path.open("rt", encoding="utf8") as f:
        env.read_env(f, overwrite=True)

dbname = env.get_value('GCPDB_NAME')
user = env.get_value('GCPDB_USER')
pw = env.get_value('GCPDB_PASSWORD')
host = env.get_value('GCPDB_HOST')


# echo를 true로 설정하면 command창에 실행된 sql문이 뜨게 됨
engine = create_engine(f'mysql+mysqldb://{user}:{pw}@{host}:3306/{dbname}?charset=utf8')

# Pickle 베이스 경로
PKL_DIR = Path(os.curdir).resolve().parent.parent
PKL_DIR = PKL_DIR / "Utils/Pickle"

mdf_rating = pd.read_pickle('~/movieLens_1192_movie.pkl')
print(f"MovieLens Interaction: {mdf_rating.shape[0]}")
cdf = pd.read_pickle(PKL_DIR / '230130_Popular_movie_character_2867_cwj.pickle')
mdf = pd.read_pickle(PKL_DIR / '230130_Popular_movie_1192_cwj.pickle')

## Fake User DB에서 불러오기
tmp_user = pd.read_sql_query("select * from test_rec_tmpuser", engine)
auth_user = pd.read_sql_query("select * from auth_user", engine)

auth_cols=['id','username']
tmp_cols = ['LoginUser_id','MBTI','ennea_res','prefer_movie_id','create_time']

# auth user에서 실제 사용자 불러오기
real_user = auth_user[auth_user.id.notna()]

# tmp_user에서 테스트 결과 가져오기
real_user_df = real_user[auth_cols].merge(tmp_user[tmp_cols], left_on='id',right_on='LoginUser_id')
real_user_df.prefer_movie_id = real_user_df.prefer_movie_id.map(literal_eval)


### MBTI, ennea_res가 바뀐 다면 create_time이 가장 마지막인 것을 기준으로 추천하기

## Fake User의 Interaction 합치기
### Fake User의 userID 변환 (Django DB user id: rating에 쓰일 user id)
common_cols = ['userId','movieId']
real_user_inter = real_user_df[['id','prefer_movie_id']].explode('prefer_movie_id')
# real_user_inter['rating']=1
real_user_inter.columns=common_cols
print(f"유저별 중복 영화 제거 전 Interaction: {real_user_inter.shape[0]}")
real_user_inter.dropna(inplace=True)
real_user_inter.drop_duplicates(subset=['userId','movieId'], inplace=True)
print(f"유저별 중복 영화 제거 후 Interaction: {real_user_inter.shape[0]}")
real_user_inter.userId+=300000
real_user_inter.movieId = real_user_inter.movieId.astype(int)

### 합치기
merge_rating = pd.concat([mdf_rating[common_cols],real_user_inter])
## Recbole input 만들기 (.inter, .data 등)
merge_rating.columns = ['user_id:token', 'item_id:token']
print(f"총 Interation: {merge_rating.shape[0]}\ntrain.inter의 shape:{merge_rating.shape}")
export_path = BASE_DIR / "BaseLine/dataset/train_data/train_data.inter"
print(f"write path: {export_path}")
merge_rating.to_csv(export_path,sep='\t',index=False)