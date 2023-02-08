import os
from ast import literal_eval
import pandas as pd
from pathlib import Path
from environ import Env
import pickle
from collections import OrderedDict
import warnings
import argparse
from sqlalchemy import create_engine

import torch
import numpy as np
from tqdm import tqdm

import annoy
import mlflow
from recbole.data import create_dataset, data_preparation, Interaction
from recbole.utils import init_logger, get_trainer, get_model, init_seed, set_color
from recbole.utils.case_study import full_sort_topk

from train import main
warnings.filterwarnings('ignore')

def ml_django_interaction_merge():

    # Build paths inside the project like this: BASE_DIR / 'subdir'.
    BASE_DIR = Path(os.curdir).resolve().parent
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

    PKL_DIR = BASE_DIR / "Utils/Pickle"
    

    # movieLens 데이터 로드
    rating = pd.read_csv(BASE_DIR / 'Data/EDA/ml-25m/ratings.csv')

    # 서비스에 사용된 영화 로드
    cdf = pd.read_pickle(PKL_DIR / '230130_Popular_movie_character_2867_cwj.pickle')
    mdf = pd.read_pickle(PKL_DIR / '230130_Popular_movie_1192_cwj.pickle')

    # django DB 데이터 로드
    auth_cols=['id','username']
    tmp_cols = ['LoginUser_id','MBTI','ennea_res','prefer_movie_id','create_time']
    tmp_user = pd.read_sql_query("select * from test_rec_tmpuser", engine)[tmp_cols]
    auth_user = pd.read_sql_query("select * from auth_user", engine)[auth_cols]

    # real_user와 tmp_user 내 기록과 합치기
    real_user = auth_user[auth_user.id.notna()]
    real_user_df = real_user[auth_cols].merge(tmp_user[tmp_cols], left_on='id',right_on='LoginUser_id')
    real_user_df.prefer_movie_id = real_user_df.prefer_movie_id.map(literal_eval)

    # rating 중 서비스에 사용된 영화의 interaction만 불러오기
    mdf_rating = rating[rating.movieId.isin(mdf.movieId)]
    mdf_rating['rating'] = 1

    # real_user의 perfer_movie_id를 interaction data처럼 펴줍니다.
    common_cols = ['userId','movieId']
    real_user_inter = real_user_df[['id','prefer_movie_id']].explode('prefer_movie_id')
    real_user_inter.columns=common_cols
    real_user_inter.dropna(inplace=True)
    real_user_inter.drop_duplicates(subset=['userId','movieId'], inplace=True)
    real_user_inter.userId+=300000
    real_user_inter.movieId = real_user_inter.movieId.astype(int)

    # recbole에 들어갈 데이터 양식에 맞게 column 변경
    merge_rating = pd.concat([mdf_rating[common_cols],real_user_inter])
    merge_rating.columns = ['user_id:token', 'item_id:token']
    merge_rating_user = pd.DataFrame(merge_rating['user_id:token'])
    merge_rating_item = pd.DataFrame(merge_rating['item_id:token'])

    if not os.path.exists("./dataset"):
        os.mkdir("./dataset")
        if not os.path.exists("./dataset/train_data"):
            os.mkdir("./dataset/train_data")

    merge_rating.to_csv("./dataset/train_data/train_data.inter",sep='\t',index = False)
    merge_rating_user.to_csv("./dataset/train_data/train_data.user",sep='\t',index = False)
    merge_rating_item.to_csv("./dataset/train_data/train_data.item",sep='\t',index = False)

def train_LGCN():
    args = argparse.Namespace(
    epochs = 1,
    model_name="LightGCN",
    dataset_name = "train_data",
    inference = False,
    config = "Model_config/LGCN_update.yaml",
    top_k = 10,
    mvti = True,
    wandb = "False"
    )
    result = main(args)
    return result

def save_annoy():
    model_name = "LightGCN"
    
    # model_name이 들어가는 pth 파일 중 최근에 생성된 걸로 불러옴
    os.makedirs('saved',exist_ok=True)
    save_path = os.listdir('./saved')
    model_path = './saved/' + sorted([file for file in save_path if model_name in file ])[-1]

    checkpoint = torch.load(model_path)
    config = checkpoint['config']

    init_seed(config['seed'], config['reproducibility'])
    config['dataset'] = 'train_data'

    config['eval_args']['split']['RS']=[999999,0,1]

    dataset = create_dataset(config)
    train_data, valid_data, test_data = data_preparation(config, dataset)

    model = get_model(config['model'])(config, train_data.dataset).to(config['device'])
    model.load_state_dict(checkpoint['state_dict'])
    model.load_other_parameter(checkpoint.get('other_parameter'))
        
    emb = model.get_ego_embeddings()

    user_id = config['USER_ID_FIELD']
    item_id = config['ITEM_ID_FIELD']
    user_id2token = dataset.field2id_token[user_id]
    item_id2token = dataset.field2id_token[item_id]

    item_emb = emb[len(user_id2token)+1:]
    item_id2token = item_id2token[1:]

    annoy_lgcn = annoy.AnnoyIndex(64,'angular')
    n_trees = 40
    for idx,emb in enumerate(item_emb):
        annoy_lgcn.add_item(int(item_id2token[idx]),emb) 
    annoy_lgcn.build(n_trees)

    annoy_lgcn.save("LightGCN_test_64")

def mlflow_upload(result:dict):
    remote_server_uri="http://101.101.219.178:30005"
    mlflow.set_tracking_uri(remote_server_uri)

    client = mlflow.tracking.MlflowClient()
    experiment_name = "LightGCN" # experiment 이름
    try:
        experiment_id = client.create_experiment(experiment_name)
    except:
        experiment = client.get_experiment_by_name(experiment_name)
        experiment_id = experiment.experiment_id
    experiment_id

    run_name="LightGCN"

    model_name = "LightGCN"

    # model_name이 들어가는 pth 파일 중 최근에 생성된 걸로 불러옴
    os.makedirs('saved',exist_ok=True)
    save_path = os.listdir('./saved')
    model_path = './saved/' + sorted([file for file in save_path if model_name in file ])[-1]

    desc="Model path: " + model_path
    with mlflow.start_run(run_name=run_name, description=desc, experiment_id=experiment_id) as run:
        for metric, score in result['best_valid_result'].items():
            print(metric,score)
            mlflow.log_metric(metric.replace('@','.'), score)