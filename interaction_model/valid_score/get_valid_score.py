import os
import sys
import pandas as pd
from tqdm import tqdm
import numpy as np
import random
from args import parse_args
from scipy import sparse
from scipy.sparse import csr_matrix, lil_matrix
import implicit
import annoy
sys.path.append('../..')
from Utils import model_recommend_movies
from interaction_model import Inference



def get_data(args) -> pd.DataFrame:
    """MBTI와 movielens에 공통으로 있는 영화의 interaction 데이터프레임을 반환하는 함수이다.

    Args:
        args

    Returns:
        ratings (DataFrame): movie와 movielens에 공통적으로 있는 영화의 interaction 데이터프레임
                             shape = (약 1157만, 4) columns = ['userId','movieId','rating','timestamp']
    """
    # raw 데이터 불러오기
    data_path = args.data_path
    ratings = pd.read_csv(data_path+'ml-25m/ratings.csv')
    inter_mbti_ml_title_movieid = pd.read_csv(data_path+"inter_mbti_ml_title_movieId.csv")

    # mbti와 movielens에 공통으로 있는 영화에 대한 interaction만 고려
    inter_mbti_ml_movieid = list(inter_mbti_ml_title_movieid['movieId'].values)
    ratings = ratings[ratings['movieId'].isin(inter_mbti_ml_movieid)]
    
    return ratings


def split_train_test(ratings:pd.DataFrame, test_user_ratio:float = 0.1) -> pd.DataFrame:
    """유저를 test_ratio에 맞게 랜덤하게 나눈 후, 나눠진 유저의 인터렉션을 train_df, test_df로 리턴하는 함수

    Args:
        ratings (DataFrame): 전체 유저의 interaction 데이터프레임
        test_user_ratio (float, optional): 전체 유저중 test 유저의 비율, Defaults to 0.1.

    Returns:
        train_df (DataFrame): train 유저의 interaction이 담긴 데이터프레임
        test_df (DataFrame): test 유저의 interaction이 담긴 데이터프레임
    """
    # user를 비율에 맞게 나누기 (list)
    user_list = list(ratings['userId'].unique())
    test_size = int(len(user_list) * test_user_ratio)
    test_user = random.sample(user_list, test_size)
    train_user = list(set(user_list)-set(test_user))

    # train_df에는 train user만, test_df에는 test user만의 interaction 데이터프레임 만들기 (DataFrame)
    train_df = ratings[ratings['userId'].isin(train_user)]
    test_df = ratings[ratings['userId'].isin(test_user)]

    # 혹시몰라 현재 폴더에 저장
    train_df.to_csv("train_df.csv", index=False)
    test_df.to_csv("test_df.csv", index=False)
    
    return train_df, test_df


def get_als_embedding_vector(args, train_df:pd.DataFrame) -> np.array:
    """interaction 정보가 담긴 Dataframe이 들어오면, 아이템에 대한 임베딩 벡터를 리턴하는 함수

    Args:
        args
        train_df (DataFrame): train 유저의 interactioin이 담긴 데이터프레임

    Returns:
        item_vecs (array): item의 임베딩벡터, shape=(item 개수, 임베딩 차원)
    """
    if 'timestamp' in train_df.columns:
        train_df.drop(columns = "timestamp",inplace = True)
    train_df['rating'] = 1

    user2idx = {k:v for v,k in enumerate(train_df['userId'].unique())}
    item2idx = {k:v for v,k in enumerate(train_df['movieId'].unique())}
    idx2item = {v:k for v,k in enumerate(train_df['movieId'].unique())}

    train_df['useridx'] = train_df['userId'].map(user2idx) # userId -> 인덱스로 바꿔줍니다.
    train_df['movieidx'] = train_df['movieId'].map(item2idx) # movieId -> 인덱스로 바꿔줍니다.

    sparse_user_item = sparse.csr_matrix((train_df['rating'].astype(float),
                                        (train_df['useridx'], train_df['movieidx']))) # csr_matrix 생성

    als_model = implicit.als.AlternatingLeastSquares(
                                    factors = args.embed_size,
                                    regularization = args.als_regularization,
                                    iterations = args.als_iterations,
                                    calculate_training_loss = False,
                                    use_gpu = True
                                ) # 모델 init

    als_model.fit(sparse_user_item) # 학습
    item_vecs = als_model.item_factors.to_numpy() # item vector만 빼옵니다.

    return item_vecs


def create_annoy_model(args, train_df:pd.DataFrame, item_vecs) -> None:
    """item 임베딩 벡터를 받은 후 벡터의 유사도를 학습한 annoy 모델이 현재 폴더에 저장된다.

    Args:
        args
        train_df (DataFrame): train 유저의 interactioin이 담긴 데이터프레임
        item_vecs (np.array): (아이템 개수, 임베딩 벡터차원)의 크기를 갖는 array
    """
    data_path = args.data_path
    inter_mbti_ml_title_movieid = pd.read_csv(data_path+"inter_mbti_ml_title_movieId.csv")

    user2idx = {k:v for v,k in enumerate(train_df['userId'].unique())}
    item2idx = {k:v for v,k in enumerate(train_df['movieId'].unique())}
    idx2item = {v:k for v,k in enumerate(train_df['movieId'].unique())}

    # inter_mbti_ml_title_movieid도 인덱싱처리
    inter_mbti_ml_title_movieid['movieidx'] = inter_mbti_ml_title_movieid['movieId'].map(item2idx)
    inter_mbti_ml_title_movieid.dropna(inplace = True)
    inter_mbti_ml_title_movieid['movieidx'] = inter_mbti_ml_title_movieid['movieidx'].astype(int)

    # annoy 모델
    similar_items_index = annoy.AnnoyIndex(args.embed_size,'angular') #'angular','euclidean','manhattan','hamming'
    n_trees = args.annoy_n_trees
    for idx in inter_mbti_ml_title_movieid['movieidx']:
        similar_items_index.add_item(idx2item[idx],item_vecs[idx]) # idx -> movieId로 바꿔서 annoy에 저장합니다.
    similar_items_index.build(n_trees)
    similar_items_index.save(f"ALS_angular_{args.embed_size}") #annoy 모델 저장


def get_test_user_prefer_info(test_df:pd.DataFrame) -> dict:
    """test 유저의 인터렉션이 담긴 데이터프레임을 받으면, 각 test 유저가 선호한 영화 리스트를 dict형으로 리턴하는 함수

    Args:
        test_df (DataFrame): test 유저의 인터렉션이 담긴 데이터프레임

    Returns:
        test_user_movie_dict: test유저가 선호한 영화정보 dict
                              {user1:[item1, item2], ...}의 형식으로 담겨져있다.
    """
    # if test_df == None:
    #     pd.read_csv("./test_df")
    
    grouped = test_df.groupby('userId')
    test_user_movie = grouped['movieId'].apply(list)

    test_user_movie_dict = dict(test_user_movie)

    return test_user_movie_dict


def calculate_valid_score(args, test_user_movie_dict:dict, model_name:str, valid_ratio:float=0.5) -> float:
    """test 유저가 선호하는 영화 정보 dict를 받으면, 각 영화별 10개씩 추천받은 후 valid score 계산해주는 함수

    Args:
        args
        test_user_movie_dict (dict): 각 test 유저(key)가 선호한 영화 리스트(value)를 담은 dict
        model_name (string): 학습된 annoy 모델 경로
        valid_ratio (float, optional): 유저가 선호한 영화들 중 검증에 사용할 valid 비율

    Returns:
        score (float): valid score의 평균, 표준편차
    """
    scores = []
    for user, movie_list in tqdm(test_user_movie_dict.items()):
        movie_list_len = len(movie_list)
        user_prefer_movieids = random.sample(movie_list, int(movie_list_len*(1-valid_ratio)))     # inference 입력 영화 id list
        user_valid_movieids = list(set(movie_list) - set(user_prefer_movieids)) # valid 영화 id list
        user_rec_movieids = model_recommend_movies("INFP","5w4",user_prefer_movieids,10,model_name) #추천 영화 id list
        inter_cnt = len(set(user_valid_movieids) & set(user_rec_movieids))      # valid 영화와 추천 영화 교집합 개수
        score = inter_cnt / len(user_valid_movieids)                            # valid 영화 개수
        scores.append(score)
    
    return np.mean(scores), np.std(scores)


def get_valid_score(args, data:str=None):
    """무비렌즈와 MBTI에 공통으로 있는 아이템에 대한 interaction 파일 경로를 입력받으면, valid score를 리턴하는 함수

    Args:
        data (str, optional): 무비렌즈와 MBTI에 공통으로 있는 아이템에 대한 interaction이 담긴 데이터프레임의 경로
                              데이터프레임의 column에 'userId','movieId','rating'가 들어가있어야한다.
    Returns:
        score (float): valid score의 통계량(평균, 표준편차)
    """
    random.seed(args.seed)
    
    if data:
        data = pd.read_csv(data)
    else:
        print("data가 없군요~ data 생성 시작!")
        data = get_data(args)
        print("data 생성 완료!")
    
    # train_df = pd.read_csv('./train_df.csv')
    # test_df = pd.read_csv('./test_df.csv')

    train_df, test_df = None, None
    train_df, test_df = split_train_test(data, test_user_ratio=args.test_user_ratio)
    print("data 나누기 완료!")


    print("각 아이템의 embedding vector 뽑기 시작!")
    item_vecs = get_als_embedding_vector(args, train_df)
    print("각 아이템의 embedding vector 뽑기 완료!")
    
    create_annoy_model(args, train_df, item_vecs)
    ("😡annoy 모델 생성 완료!")

    test_user_movie_dict = get_test_user_prefer_info(test_df)
    print("test 유저의 선호정보 뽑기 완료!")

    print("valid score 계산 시작!")
    score_mean, score_std = calculate_valid_score(args, test_user_movie_dict, args.model_name, args.valid_ratio)
    print("valid score 계산 완료!")

    print(f'test_유저의 valid 스코어의 평균: {score_mean}')
    print(f'test_유저의 valid 스코어의 표준편차: {score_std}')

    return score_mean, score_std

if __name__ == "__main__":
    args = parse_args()
    args.data_path = "/opt/ml/input/fighting/CSV/"

    get_valid_score(args)