import os
import pandas as pd
import pickle

# 현재 파일 기준 경로잡기
cur_filepath = lambda path: os.path.join(os.path.abspath(os.path.dirname(__file__)),path)
popular_movie = pd.read_pickle(cur_filepath('Pickle/230213_character_movie_merge.pickle')) # 유명황 영화로 걸러주기 위해
data = pd.read_pickle(cur_filepath('Pickle/content_based_4035.pickle')) # side information data

with open(cur_filepath('Pickle/content_based_plot_sim.pkl'), 'rb') as file:
    '''
    p_sim이 만들어지는 과정
    - plot을 TF-IDF를 통해 유사도 측정한것
    - sklearn의 코사인 유사도 사용
    '''
    p_sim = pickle.load(file)
    
with open(cur_filepath('Pickle/content_based_genre_sim.pkl'), 'rb') as file:
    '''
    g_sim이 만들어지는 과정

    with open(file='/opt/ml/input/final_project/Content_based/bert_em_plot_vec_dict_2.pkl', mode='rb') as f: <- BERT를 통한 장르 임베딩
        genre_em_vec = pickle.load(f)

    list_of_arrays = [t.detach().numpy() for t in genre_em_vec['genre_vec']] <- tensor를 np.array로 변환
    g_sim = cosine_similarity(list_of_arrays) <- sklearn의 코사인 유사도 이용
    '''
    g_sim = pickle.load(file)

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

def mbti_filtering(mbti_list, mbti_mv, recommend_movie_ids):
    """입력받은 mbti로 필터링

    Args:
        mbti_list (list): mbti list
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

def content_based_filtering(movieIds:list, topk:int):
    '''
    user가 선호하는 movie_list를 입력으로 받아 유사도 높은 컨텐츠의 movieId topk개를 반환합니다.
    - 장르를 pre-train된 BERT모델을 통해 벡터화
    - 줄거리를 TF-IDF를 통해 벡터화 (구동 환경 여건상 길이가 긴 줄거리를 반복적으로 BERT을 통과 시키는 것이 부담되기 때문이다)
    위 과정을 통해 만들어진 벡터를 코사인 유사도 기반으로 유사도를 측정한다

    Args:
        movieIds (list): 유저가 선택한 영화 리스트입니다.
        topk (int): 유사도 높은 아이템을 리턴할 개수

    Returns:
       recommended_movie_ids (list): 유사도 높은 아이템의 movieId topk개를 담고 있는 list 입니다.
    '''
    checked = []
    for mid in movieIds:
        index = data.index[data['movieId']==mid][0]
        checked.append((index,mid))

    # index로 접근하기 위한 처리
    content2idx = {}
    idx2content = {}
    for i, c in enumerate(data['Contents']):
        content2idx[c] = i
        idx2content[i] = c

    total_sim = (p_sim+g_sim)/2

    
    def check_latest(idx):
        '''
        데이터 프레임에서 해당 인덱스의 영화가 설정한 연도 이후 영화인지 확인한다.

        Args:
            idx: 데이터프레임의 인덱스

        Returns:
            True/False
        '''
        content_name = idx2content[idx]
        if data.loc[data['Contents'] == content_name]['year'].iloc[0] >= '2015':
            if data.loc[data['Contents'] == content_name]['year'].iloc[0] == 'no_data':
                return False
            return True
        return False

    candi_dictionary = {}
    for k,m in checked:
        sim_scores = [(i,c) for i, c in enumerate(total_sim[k]) if i != 0] # 자기 자신을 제외한 영화들의 유사도 및 인덱스를 추출
        sim_scores = sorted(sim_scores, key= lambda x: x[1],reverse=True) # 유사도가 높은 순서로 정렬
        cnt = 0
        for idx, sc in sim_scores:
            if cnt >= 60:  # 하나의 영화 당 60개의 후보를 생성
                break
            if idx in checked or not check_latest(idx) or m not in popular_movie['movieId'].values:
                continue
            if idx in candi_dictionary:
                candi_dictionary[idx] += sc
            else:
                candi_dictionary[idx] = sc
            cnt+=1

    candi_list = list(candi_dictionary.items())
    candi_list = sorted(candi_list, key= lambda x: x[1],reverse=True)


    # id를 title로 변환
    top_k = [(idx2content[i], score) for i , score in candi_list[0:topk]] # topk추천
    # topk는 (영화 제목, 유사도)의 리스트로 이루어져있다

    recommended_movie_ids = []
    for i,j in top_k:
        m_id = int(data.loc[data['Contents']==i]['movieId'].values[0])
        recommended_movie_ids.append((m_id,j)) # (movieId, Score)

    return recommended_movie_ids

def user_input_to_side_recommend(mbti_list, engram, prefer_movie_ids, top_k=10)->pd.DataFrame:
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
    mbti_movie = pd.read_pickle(cur_filepath('Pickle/230130_Popular_movie_character_2867_cwj.pickle'))
    engram_sim = pd.read_pickle(cur_filepath('Pickle/enneagram_similarity_075_099.pickle'))
    sideinfo_movie_list,scores = zip(*content_based_filtering(prefer_movie_ids, top_k))
    mbti_rec = mbti_filtering(mbti_list, mbti_movie, sideinfo_movie_list)
    mbti_rec_sort = engram_sorting(engram, mbti_rec, engram_sim)
    result = mbti_rec_sort.drop_duplicates(subset=['Character', 'Contents'])[:top_k]
    return result

if __name__=='__main__':
    prefer_movie_ids =  [1704, 1721, 2021, 72998, 73141] #, 91500, 164909]
    mbti="INTJ"
    engram="3w2"
    print(user_input_to_side_recommend(mbti, engram, prefer_movie_ids, top_k=60))