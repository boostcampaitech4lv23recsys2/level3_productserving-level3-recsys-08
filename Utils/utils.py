import os
import sys
sys.path.append(os.path.join(os.path.abspath(os.path.dirname(__file__)),'..'))
import pandas as pd
import warnings
warnings.filterwarnings('ignore')
from interaction_model import Inference

# 현재 파일 기준 경로잡기
cur_filepath = lambda path: os.path.join(os.path.abspath(os.path.dirname(__file__)),path)

def get_en_sim(engram, engram_sim):
    """에니어그램 시밀러리티 딕셔너리 생성

    Args:
        engram (str): 애니어그램 3글자 문자열 ex) '1w9'
        engram_sim (dataframe) : 애니어그램 18x18 유사도 매트릭스
    Returns:
        dict: 주어진 애니어그램과 다른 애니어그램 사이의 유사도 딕셔너리
    """
    engram_sim.index = engram_sim.columns
    return engram_sim[[engram]].to_dict()[engram]

def model_recommend_movies(prefer_movie_ids, top_k, model_path=cur_filepath('../interaction_model/LightGCN_64')):
    """주어진 movie ids로 부터 추천 영화 ids 반환

    Args:
        prefer_movie_ids (list): 선택된 movie id 리스트
        top_k (int): 영화별 추천 영화 Topk
        model_path (str, optional): annoy model path. Defaults to '../interaction_model/ALS_64'.

    Returns:
        list: 추천 영화 리스트
    """
    ## 사용자가 선호하는 movie id로 부터 모델 추천 받기
    print(model_path)
    recommend_movie_ids=[]
    score = {}
    for mid in prefer_movie_ids:
        ids = Inference(model_path, int(mid), top_k)[0]
        dist = Inference(model_path, int(mid), top_k)[1]
        for i in range(len(ids)):
            if ids[i] in score:
                score[ids[i]] += dist[i]
            else:
                score[ids[i]] = dist[i]

    recommend_movie_ids = sorted(score.items(), key=lambda x: x[1], reverse=True)[:top_k]
    recommend_movie_ids = [i[0] for i in recommend_movie_ids]
    print(len(recommend_movie_ids))
    # recommend_movie_ids = list(set(recommend_movie_ids)) # 중복제거
    return recommend_movie_ids

def mbti_filtering(mbti_list, mbti_mv, recommend_movie_ids):
    """입력받은 mbti로 필터링

    Args:
        mbti_list (list): mbti_list
        mbti_mv (dataframe): mbti와 movie lens의 movie_id가 결합된 데이터프레임
        recommend_movie_ids (list): 추천된 movie id list

    Returns:
        dataframe: mbti로 필터링된 데이터프레임
    """
    ## MBTI 필터링 -> 유사도 내림차순 정렬
    recommend_chars = mbti_mv[mbti_mv.movieId.isin(recommend_movie_ids)]
    mbti_rec = recommend_chars[recommend_chars.MBTI.isin(mbti_list)]
    return mbti_rec

def engram_sorting(engram, mbti_rec, engram_sim) -> pd.DataFrame:
    """애니어그램 유사도로 내림차순 정렬

    Args:
        engram (str): 애니어그램 string
        mbti_rec (dataframe): 추천 결과 datafrmae
        engram_sim (datafrmae): 애니어그램 유사도 매트릭스
    Returns:
        pd.DataFrame: 애니어그램 정렬결과 datafrmae
    """
    engram_dict = get_en_sim(engram, engram_sim)
    mbti_rec['Enneagram_sim'] = mbti_rec.Enneagram.map(engram_dict)
    mbti_rec_sort = mbti_rec.sort_values('Enneagram_sim', ascending=False)
    return mbti_rec_sort

def user_input_to_recommend(mbti_list, engram, prefer_movie_ids, top_k=10)->pd.DataFrame:
    """Form 으로 입력받은 User Input으로 부터 추천 데이터프레임 반환

    Args:
        mbti_list (list): mbti_list
        engram (str): 애니어그램 string
        prefer_movie_ids (list): 유저가 선호하는 movie list
        top_k (int, optional): Top K 추천. Defaults to 10.

    Returns:
        pd.DataFrame: 추천 데이터프레임. 결과 df.to_dict(orient='records') 하면 결과 딕셔너리 리스트 생성 가능.
    """

    ## mbti movie, 애니어그램 유사도 매트릭스 불러오기
    mbti_movie = pd.read_pickle(cur_filepath('Pickle/230213_character_movie_merge.pickle'))
    engram_sim = pd.read_pickle(cur_filepath('Pickle/enneagram_similarity_075_099.pickle'))
    model_path=cur_filepath('../interaction_model/LightGCN_64')
    recommend_movie_ids = model_recommend_movies(prefer_movie_ids, top_k, model_path=model_path)
    mbti_rec = mbti_filtering(mbti_list, mbti_movie, recommend_movie_ids)
    mbti_rec_sort = engram_sorting(engram, mbti_rec, engram_sim)
    result = mbti_rec_sort.drop_duplicates(subset=['Character', 'Contents'])[:top_k]
    return result

if __name__ == "__main__":
    ## Test
    prefer_movie_ids =  [1704, 1721, 2021, 72998, 73141] #, 91500, 164909]
    mbti="INTJ"
    engram="3w2"
    print(user_input_to_recommend(mbti, engram, prefer_movie_ids, top_k=60))
    # print(os.path.dirname(os.path.abspath(__file__)))