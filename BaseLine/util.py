import torch
import numpy as np
import pandas as pd
from tqdm import tqdm
import pickle
from recbole.data import create_dataset, data_preparation, Interaction
from recbole.utils import init_logger, get_trainer, get_model, init_seed, set_color
from recbole.utils.case_study import full_sort_topk
import os
import glob
from environ import Env
from pathlib import Path
from sqlalchemy import create_engine
import warnings
warnings.filterwarnings('ignore')

def make_config(config_name : str) -> None:
    yamldata="""
    field_separator: "\t"
    USER_ID_FIELD: user_id
    ITEM_ID_FIELD: item_id
    TIME_FIELD: timestamp
    
    load_col:
        inter: [user_id, item_id, timestamp]
        user : [user_id]
        item: [item_id, year, writer, title, genre, director]

    train_neg_sample_args:
        distribution : uniform
        sample_num : 1

    selected_features: [year, writer, title, genre, director]
    
    show_progress : False
    device : torch.device("cuda" if torch.cuda.is_available() else "cpu")
    
    metrics: ['Recall', 'MRR', 'NDCG', 'Hit', 'Precision', 'MAP']
    topk: 10
    valid_metric: Recall@10
    
    stopping_step : 10
    
    log_wandb : True
    wandb_project : Recbole
    """
    
    with open(f"{config_name}", "w") as f:
        f.write(yamldata)

    return

def make_dataset(dataset_name : str) -> None:
    """
        train_data 만드는 함수입니다.
    """
    train = pd.read_csv("/opt/ml/input/data/train/train_ratings.csv")

    # item 부가 정보 load
    data_path = '/opt/ml/input/data/train'
    year_data = pd.read_csv(os.path.join(data_path, 'years.tsv'), sep='\t')
    writer_data = pd.read_csv(os.path.join(data_path, 'writers.tsv'), sep='\t')
    title_data = pd.read_csv(os.path.join(data_path, 'titles.tsv'), sep='\t')
    genre_data = pd.read_csv(os.path.join(data_path, 'genres.tsv'), sep='\t')
    director_data = pd.read_csv(os.path.join(data_path, 'directors.tsv'), sep='\t')

    # train과 부가 정보 merge
    df_merge = pd.merge(train, year_data, on='item', how='left')
    df_merge = pd.merge(df_merge, writer_data, on='item', how='left')
    df_merge = pd.merge(df_merge, title_data, on='item', how='left')
    df_merge = pd.merge(df_merge, genre_data, on='item', how='left')
    df_merge = pd.merge(df_merge, director_data, on='item', how='left')
    
    user_data = df_merge[['user']].drop_duplicates(subset=['user']).reset_index(drop=True)
    item_data = df_merge[['item', 'year', 'writer', 'title', 'genre', 'director']].drop_duplicates(subset=['item']).reset_index(drop=True)
    
    # indexing save
    user2idx = {v:k for k,v in enumerate(sorted(set(train.user)))}
    item2idx = {v:k for k,v in enumerate(sorted(set(train.item)))}

    # indexing
    train.user = train.user.map(user2idx)
    train.item = train.item.map(item2idx)
    user_data.user = user_data.user.map(user2idx)
    item_data.item = item_data.item.map(item2idx)
    
    # train, item_data 컬럼
    train.columns=['user_id:token','item_id:token','timestamp:float']
    user_data.columns=['user_id:token']
    item_data.columns=['item_id:token', 'year:token', 'writer:token', 'title:token_seq', 'genre:token', 'director:token']
    
    # to_csv
    outpath = f"dataset/{dataset_name}"
    os.makedirs(outpath, exist_ok=True)
    train.to_csv(os.path.join(outpath,f"{dataset_name}.inter"),sep='\t',index=False)
    user_data.to_csv(os.path.join(outpath,f"{dataset_name}.user"),sep='\t',index=False)
    item_data.to_csv(os.path.join(outpath,f"{dataset_name}.item"),sep='\t',index=False)

    return

def uniquify(path:str) -> str:
    """중복파일이 있는 경우 Numbering

    Args:
        path (str): 파일 경로

    Returns:
        str: Numbering된 파일 경로
    """

    filename, extension = os.path.splitext(path)
    counter = 1

    while os.path.exists(path):
        path = filename + f"-{str(counter)}" + extension
        counter += 1

    return path

def filter_trainset(sub:pd.DataFrame)->pd.DataFrame:
    """train set과 겹치는 Interaction을 필터링합니다.

    Args:
        sub (pd.DataFrame): 필터링 전 submission dataframe

    Returns:
        pd.DataFrame: 필터링 후 submission dataframe
    """
    train = pd.read_csv("/opt/ml/input/data/train/train_ratings.csv")
    sub = sub.merge(train,on=['user','item'],how='left')
    return sub[sub.time.isna()][['user','item']]

def filter_after_review_interaction(sub:pd.DataFrame) -> pd.DataFrame:
    """마지막 리뷰날짜 이후에 개봉된 영화 Interaction 제외

    Args:
        sub (pd.DataFrame): submission dataframe

    Returns:
        pd.DataFrame: filtering된 submission dataframe
    """
    
    with open('./index/item2year.pickle','rb') as f:
        item2year = pickle.load(f)
    with open('./index/userid2lastyear.pickle','rb') as f:
        userid2lastyear = pickle.load(f)

    sub['lastyear']=sub.user.map(userid2lastyear)
    sub['m_year'] = sub.item.map(item2year)

    sub = sub[sub.lastyear >= sub.m_year]
    return sub[['user','item']]

def mvti_recommend(model_name : str, topk : int, model_path=None)->None:
    """
    train.py에서 학습했던 모델로 inference를 하는 함수입니다.
    submission 폴더에 저장됩니다.

    Args:
        model_name (str): 돌렸던 모델의 이름입니다. 해당 모델의 이름이 들어가는 pth파일 중 최근 걸로 불러옵니다.
        topk (int): submission에 몇 개의 아이템을 출력할지 정합니다.
    """
    
    print("create_engine!")
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

    # engine 생성
    engine = create_engine(f'mysql+mysqldb://{user}:{pw}@{host}:3306/{dbname}?charset=utf8')
    print('inference start!')
    if model_path is None:
        # model_name이 들어가는 pth 파일 중 최근에 생성된 걸로 불러옴
        os.makedirs('saved',exist_ok=True)
        save_path = glob.glob('./saved/*')
        latest_model_path = max(save_path, key=os.path.getctime)
    model_path_absolute = Path(latest_model_path).absolute()
    K = topk
    print(f"{model_path_absolute = }")

    # config, model, dataset 불러오기
    checkpoint = torch.load(model_path_absolute)
    config = checkpoint['config']

    init_seed(config['seed'], config['reproducibility'])
    config['dataset'] = 'train_data'
    if model_name=="S3Rec":
        config['eval_args']['split']={'RS':[99999,0,1]}
    else:
        config['eval_args']['split']['RS']=[999999,0,1]
    print("create dataset start!")
    dataset = create_dataset(config)
    train_data, valid_data, test_data = data_preparation(config, dataset)
    print("create dataset done!")

    model = get_model(config['model'])(config, train_data.dataset).to(config['device'])
    model.load_state_dict(checkpoint['state_dict'])
    model.load_other_parameter(checkpoint.get('other_parameter'))

    # device 설정
    device = config.final_config_dict['device']

    # user, item id -> token 변환 array
    user_id = config['USER_ID_FIELD']
    item_id = config['ITEM_ID_FIELD']
    user_id2token = dataset.field2id_token[user_id]
    item_id2token = dataset.field2id_token[item_id]

    # 30만 번 이상 유저만, user tensor list 생성
    user_list=[]
    for idx,i in enumerate(user_id2token):
        if i!='[PAD]':
            if int(i)>=300_000:
                user_list.append(idx)
    user_tensor_list = torch.tensor(user_list)
    print(f"{user_tensor_list = }, {len(user_tensor_list) = }")
    # 예측
    try:
        pred_list = full_sort_topk(user_tensor_list, model, test_data, topk, device=device)[1]
    except:
        print(f"Real User가 없습니다. tail train_data.inter를 확인해주세요!")


    # user별 item 추천 결과 하나로 합쳐주기
    result = []
    for user, pred in zip(user_list, pred_list):
        for item in pred:
            result.append((int(user_id2token[user]), int(item_id2token[item])))
    sub = pd.DataFrame(result, columns=["user", "item"])

    # DB에 쓸 결과 파일 생성
    result = sub.groupby('user').item.apply(list).reset_index()

    # 결과 파일 정제
    result['model_name'] = model_name
    result['model_path'] = model_path_absolute
    result['create_time'] = str(pd.Timestamp.now())
    result['id'] = 0

    # 유저 번호 30만 내려주기
    result.user -= 300_000

    result.rename(columns={'user':'LoginUser_id','item':'recommended_movie_list'},inplace=True)
    cols = ['id','LoginUser_id', 'model_name','model_path', 'recommended_movie_list', 'create_time']
    result = result[cols]
    print(f"{result.shape = }")
    print(result[:3])
    # DB에 쓰기
    result.astype(str).to_sql(name='common_batchtrain', con=engine, index=False, if_exists='append')
    print("DB wirte done!")
    print('inference done!')
    return

def inference(model_name : str, topk : int, model_path=None)->None:
    """
    train.py에서 학습했던 모델로 inference를 하는 함수입니다.
    submission 폴더에 저장됩니다.

    Args:
        model_name (str): 돌렸던 모델의 이름입니다. 해당 모델의 이름이 들어가는 pth파일 중 최근 걸로 불러옵니다.
        topk (int): submission에 몇 개의 아이템을 출력할지 정합니다.
    """
    print('inference start!')
    if model_path is None:
        # model_name이 들어가는 pth 파일 중 최근에 생성된 걸로 불러옴
        os.makedirs('saved',exist_ok=True)
        save_path = os.listdir('./saved')
        model_path = './saved/' + sorted([file for file in save_path if model_name in file ])[-1]

    K = topk

    # config, model, dataset 불러오기
    checkpoint = torch.load(model_path)
    config = checkpoint['config']

    init_seed(config['seed'], config['reproducibility'])
    config['dataset'] = 'train_data'
    if model_name=="S3Rec":
        config['eval_args']['split']={'RS':[99999,0,1]}
    else:
        config['eval_args']['split']['RS']=[999999,0,1]
    print("create dataset start!")
    dataset = create_dataset(config)
    train_data, valid_data, test_data = data_preparation(config, dataset)
    print("create dataset done!")

    model = get_model(config['model'])(config, train_data.dataset).to(config['device'])
    model.load_state_dict(checkpoint['state_dict'])
    model.load_other_parameter(checkpoint.get('other_parameter'))

    # device 설정
    device = config.final_config_dict['device']

    # user, item id -> token 변환 array
    user_id = config['USER_ID_FIELD']
    item_id = config['ITEM_ID_FIELD']
    user_id2token = dataset.field2id_token[user_id]
    item_id2token = dataset.field2id_token[item_id]

    # user id list
    all_user_list = torch.arange(1, len(user_id2token)).view(-1,128) # 245, 128

    # user, item 길이
    user_len = len(user_id2token) # 31361 (PAD 포함)
    item_len = len(item_id2token) # 6808 (PAD 포함)

    # user-item sparse matrix
    matrix = dataset.inter_matrix(form='csr') # (31361, 6808)

    # user id, predict item id 저장 변수
    pred_list = None
    user_list = []

    # user id list
    all_user_list = torch.arange(1, len(user_id2token)).view(-1,128) # 245, 128

    tbar = tqdm(all_user_list, desc=set_color(f"Inference", 'pink')) # 245, 128

    for data in tbar:
        batch_pred_list = full_sort_topk(data, model, test_data, K+50, device=device)[1]
        batch_pred_list = batch_pred_list.clone().detach().cpu().numpy()
        if pred_list is None:
            pred_list = batch_pred_list
            user_list = data.numpy()
        else:
            pred_list = np.append(pred_list, batch_pred_list, axis=0)
            user_list = np.append(
                user_list, data.numpy(), axis=0
            )
    tbar.close()

    # user별 item 추천 결과 하나로 합쳐주기
    result = []
    for user, pred in zip(user_list, pred_list):
        for item in pred:
            result.append((int(user_id2token[user]), int(item_id2token[item])))

    sub = pd.DataFrame(result, columns=["user", "item"])

    # 인덱스 -> 유저 아이템번호 dictionary 불러오기
    with open('./index/uidx2user.pickle','rb') as f:
        uidx2user = pickle.load(f)
    with open('./index/iidx2item.pickle','rb') as f:
        iidx2item = pickle.load(f)   

    # submission 생성
    sub = pd.DataFrame(result, columns=["user", "item"])
    sub.user = sub.user.map(uidx2user)
    sub.item = sub.item.map(iidx2item)
    sub = filter_trainset(sub)
    sub = filter_after_review_interaction(sub)

    # extract Top K 
    users = sub.groupby('user').user.head(K).reset_index(drop=True)
    items = sub.groupby('user').item.head(K).reset_index(drop=True)
    sub = pd.concat([users,items],axis=1)
    
    print(f"submission length: {sub.shape[0]}")

    os.makedirs('submission',exist_ok=True)
    submission=f"./submission/{model_path[8:-4]}.csv"
    submission = uniquify(submission)
    sub[['user','item']].to_csv(
        submission, index=False # "./saved/" 와 ".pth" 제거
    )
    print(f"model path: {model_path}")
    print(f"submission path: {os.path.relpath(submission)}")
    print('inference done!')
    return


def general_inference(model_name : str,topk : int, model_path=None)->None:
    """
    train.py에서 학습했던 모델로 inference를 하는 함수입니다.
    submission 폴더에 저장됩니다.
    Args:
        model_name (str): 돌렸던 모델의 이름입니다. 해당 모델의 이름이 들어가는 pth파일 중 최근 걸로 불러옵니다.
        topk (int): submission에 몇 개의 아이템을 출력할지 정합니다.
    """
    print('inference start!')
    if model_path is None:
        # model_name이 들어가는 pth 파일 중 최근에 생성된 걸로 불러옴
        os.makedirs('saved',exist_ok=True)
        save_path = os.listdir('./saved')
        model_path = './saved/' + sorted([file for file in save_path if model_name in file ])[-1]
        
    K = topk+30

    # config, model, dataset 불러오기
    checkpoint = torch.load(model_path)
    config = checkpoint['config']
    config['dataset'] = 'train_data'

    dataset = create_dataset(config)
    train_data, valid_data, test_data = data_preparation(config, dataset)

    model = get_model(config['model'])(config, test_data.dataset).to(config['device'])
    model.load_state_dict(checkpoint['state_dict'])
    model.load_other_parameter(checkpoint.get('other_parameter'))

    # device 설정
    device = config.final_config_dict['device']

    # user, item id -> token 변환 array
    user_id = config['USER_ID_FIELD']
    item_id = config['ITEM_ID_FIELD']
    user_id2token = dataset.field2id_token[user_id]
    item_id2token = dataset.field2id_token[item_id]

    # user id list
    all_user_list = torch.arange(1, len(user_id2token)).view(-1,128) # 245, 128

    # user, item 길이
    user_len = len(user_id2token) # 31361 (PAD 포함)
    item_len = len(item_id2token) # 6808 (PAD 포함)

    # user-item sparse matrix
    matrix = dataset.inter_matrix(form='csr') # (31361, 6808)

    # user id, predict item id 저장 변수
    pred_list = None
    user_list = None

    # model 평가모드 전환
    model.eval()

    # progress bar 설정
    tbar = tqdm(all_user_list, desc=set_color(f"Inference", 'pink')) # 245, 128

    for data in tbar: # data: 128, 
        # interaction 생성
        interaction = dict()
        interaction = Interaction(interaction)
        interaction[user_id] = data
        interaction = interaction.to(device)

        # user item별 score 예측
        score = model.full_sort_predict(interaction) # [1, 871424]
        score = score.view(-1, item_len) # 128, 6808

        rating_pred = score.cpu().data.numpy().copy() # 128, 6808

        user_index = data.numpy() # 128,

        # idx에는 128명의 영화상호작용이 True, False로 있다.
        idx = matrix[user_index].toarray() > 0 # idx shape: 128, 6808

        rating_pred[idx] = -np.inf # idx에서 True부분이 -inf로 변경
        rating_pred[:, 0] = -np.inf # 첫번째 PAD 열도 -inf로 변경

        # np.argpartition(배열, -K) : 배열에서 순서 상관없이 큰 값 K개를 뽑아 오른쪽에 놓겠다 -> 인덱스반환
        # rating_pred에서 각 행마다 K개의 score가 큰 인덱스를 오른쪽에 두고, 그 K개만 가져오기
        ind = np.argpartition(rating_pred, -K)[:, -K:] # rating_pred: (128, 6808) -> ind: (128, 20)

        user_row_index = np.arange(len(rating_pred)).reshape(-1,1) # [[0],[1],...,[127]]
        arr_ind = rating_pred[user_row_index, ind] # 128, 6808 -> 128, 20

        # arr_ind 내부에서 행별로, 내림차순 정렬해서 index 나오도록
        arr_ind_argsort = np.argsort(arr_ind)[np.arange(len(rating_pred)), ::-1]

        # ind는 item의 real index를 갖는 128,20 -> arr_ind_argsort를 통해 pred가 높은 상위 20개 read index 추출
        batch_pred_list = ind[user_row_index, arr_ind_argsort] # 128,20 -> 128,20

        if pred_list is None: # 처음에는 직접 정의
            pred_list = batch_pred_list
            user_list = user_index
        else: # pred_list가 있을 때는, append
            pred_list = np.append(pred_list, batch_pred_list, axis=0)
            user_list = np.append(
                user_list, user_index, axis=0
            )

    result = []
    for user, pred in zip(user_list, pred_list):
        for item in pred:
            result.append((int(user_id2token[user]), int(item_id2token[item])))

    # 인덱스 -> 유저 아이템번호 dictionary 불러오기
    with open('./index/uidx2user.pickle','rb') as f:
        uidx2user = pickle.load(f)
    with open('./index/iidx2item.pickle','rb') as f:
        iidx2item = pickle.load(f)

    # submission 생성
    sub = pd.DataFrame(result, columns=["user", "item"])
    sub.user = sub.user.map(uidx2user)
    sub.item = sub.item.map(iidx2item)
    sub = filter_trainset(sub)
    sub = filter_after_review_interaction(sub)

    # extract Top K 
    users = sub.groupby('user').user.head(topk).reset_index(drop=True)
    items = sub.groupby('user').item.head(topk).reset_index(drop=True)
    sub = pd.concat([users,items],axis=1)
    
    print(f"submission length: {sub.shape[0]}")

    os.makedirs('submission',exist_ok=True)
    submission=f"./submission/{model_path[8:-4]}.csv"
    submission = uniquify(submission)
    sub[['user','item']].to_csv(
        submission, index=False # "./saved/" 와 ".pth" 제거
    )
    print(f"model path: {model_path}")
    print(f"submission path: {os.path.relpath(submission)}")
    print('inference done!')
    return