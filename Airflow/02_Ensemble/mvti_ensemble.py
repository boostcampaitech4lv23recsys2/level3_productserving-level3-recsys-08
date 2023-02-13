import os
import numpy as np
import pandas as pd
from pathlib import Path
from environ import Env
from ast import literal_eval
from tqdm import tqdm
from collections import defaultdict
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

df = pd.read_sql_query("select * from common_batchtrain", engine)
weight_dict={"ADMMSLIM":0.7, "EASE":1, "RecVAE":0.5}


print('순위별 가중치값 입력(ex: 1 0.9 0.8 ...)')
rank_ratio = np.linspace(1,0,501)[:500].tolist() # 추천 500개
rank_len = len(rank_ratio)
print(f"앙상블 모델 개수: {len(weight_dict)}")

## 앙상블할 추천 결과 df 리스트
dataframe_list = []
## 모델 가중치
ratios = []
for model_name in weight_dict:
    ratios.append(weight_dict[model_name])
    df_model = df[df.model_name==model_name].copy()
    last_date = df_model.create_time.max()
    print(f"{model_name} 모델이 추천한 마지막 시간은 {last_date.strftime('%Y년 %m월 %d일 %H시 %M분')}")

    df_model_last = df_model[df_model.create_time==last_date].copy()
    print(f"그 때 추천한 유저는 {df_model_last.shape[0]}명")
    df_model_last.loc[:,'recommended_movie_list'] = df_model_last.recommended_movie_list.map(literal_eval)
    df_model_last = df_model_last[['LoginUser_id','recommended_movie_list']].explode('recommended_movie_list').copy()
    dataframe_list.append(df_model_last)
print(f"가중치 {weight_dict}")

dataframe_len = len(dataframe_list)
user_list = dataframe_list[0]['LoginUser_id'].unique()

K=500 # 추천 500개
result = []
tbar = tqdm(user_list, desc='Ensemble')
for user in tbar:
    temp = defaultdict(float)
    for df_idx in range(dataframe_len):
        items = dataframe_list[df_idx][dataframe_list[df_idx]['LoginUser_id'] == user]['recommended_movie_list'].values
        max_rank = min(len(items), rank_len)
        for rank_idx in range(max_rank):
            temp[items[rank_idx]] += rank_ratio[rank_idx] * ratios[df_idx]

    for key, _ in sorted(temp.items(), key=lambda x: x[1], reverse=True)[:K]:
        result.append((user, key))
# sub 생성
sub = pd.DataFrame(result, columns=['LoginUser_id', 'recommended_movie_list'])

# DB에 쓸 결과 파일 생성
result = sub.groupby('LoginUser_id').recommended_movie_list.apply(list).reset_index()

# 결과 파일 정제
result['model_name'] = "ADER"
result['model_path'] = "No Path"
result['create_time'] = str(pd.Timestamp.now())
result['id'] = 0

cols = ['id','LoginUser_id', 'model_name','model_path', 'recommended_movie_list', 'create_time']
result = result[cols]

# DB에 쓰기
result.astype(str).to_sql(name='common_batchtrain', con=engine, index=False, if_exists='append')