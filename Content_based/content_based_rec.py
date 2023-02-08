import pandas as pd
import pickle

popular_movie = pd.read_csv('/opt/ml/input/final_project/Content_based/230129_Popular_movie_1192_cwj.csv') # 유명황 영화로 걸러주기 위해
mbti_all = pd.read_csv('/opt/ml/input/final_project/data/Personality_All_168000_rows.csv') # 캐릭터 검색을 위해
data = pd.read_csv('/opt/ml/input/final_project/Content_based/content_based_4035.csv') # side information data

with open('/opt/ml/input/final_project/Utils/Pickle/content_based_plot_sim.pkl', 'rb') as file:
    '''
    p_sim이 만들어지는 과정
    - plot을 TF-IDF를 통해 유사도 측정한것
    - sklearn의 코사인 유사도 사용
    '''
    p_sim = pickle.load(file)
    
with open('/opt/ml/input/final_project/Utils/Pickle/content_based_genre_sim.pkl', 'rb') as file:
    '''
    g_sim이 만들어지는 과정

    with open(file='/opt/ml/input/final_project/Content_based/bert_em_plot_vec_dict_2.pkl', mode='rb') as f: <- BERT를 통한 장르 임베딩
        genre_em_vec = pickle.load(f)

    list_of_arrays = [t.detach().numpy() for t in genre_em_vec['genre_vec']] <- tensor를 np.array로 변환
    g_sim = cosine_similarity(list_of_arrays) <- sklearn의 코사인 유사도 이용
    '''
    g_sim = pickle.load(file)



def content_based_filtering(movieIds:list, topk:int):
    '''
    user가 선호하는 movie_list를 입력으로 받아 유사도 높은 컨텐츠의 movieId topk개를 반환합니다.
    - 장르를 pre-train된 BERT모델을 통해 벡터화
    - 줄거리를 TF-IDF를 통해 벡터화 (구동 환경 여건상 길이가 긴 줄거리를 반복적으로 BERT을 통과 시키는 것이 부담되기 때문이다)
    위 과정을 통해 만들어진 벡터를 코사인 유사도 기반으로 유사도를 측정한다

    Args:
        checked (list): 유저가 선택한 영화 리스트입니다.
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

if __name__=='__main__':
    print(content_based_filtering([73141,122470,152081], 10)) # 입력 : [모아나, 인사이드 아웃, 주토피아]