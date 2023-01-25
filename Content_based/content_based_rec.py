import pandas as pd
import pickle
import random

mbti_all = pd.read_csv('/opt/ml/input/final_project/data/Personality_All_168000_rows.csv')
data = pd.read_csv('/opt/ml/input/final_project/Crawling/imdb_side_df_EmptyList_to_None.csv') # side information data
data = data.drop_duplicates('Contents',keep='first') # 중복 제거
data = data.drop(['produceers', 'composers'], axis=1) # 수집 하나도 안되서 쓸모 없음

def remove_list_symbol(row):  # DataFrame 만들때 조금 문제가 있었는듯
    try:
        return row['plot'][2:-2]  # 리스트 형태가 아니고 str이다 ex "['Batman ...']" 이런식으로 저장되어있어서 ['와 ']를 제거하는 목적
    except TypeError:
        pass

def remove_list_symbol_2(row):  # DataFrame 만들때 조금 문제가 있었는듯
    try:
        return row['genres'][1:-1]  # 리스트 형태가 아니고 str이다 ex "['Batman ...']" 이런식으로 저장되어있어서 ['와 ']를 제거하는 목적
    except TypeError:
        pass

data['plot'] = data.apply(remove_list_symbol, axis=1)
data['genres'] = data.apply(remove_list_symbol_2, axis=1)
data['plot'] = data['plot'].fillna('')
data['genres'] = data['genres'].fillna('')

# index로 접근하기 위한 처리
content2idx = {}
idx2content = {}
for i, c in enumerate(data['Contents']):
    content2idx[c] = i
    idx2content[i] = c

show_idx = []
for _ in range(10):
    show_idx.append(random.randint(0,4034))
for si in show_idx:
    print((si,idx2content[si]))
    
with open('/opt/ml/input/final_project/Content_based/p_sim.pkl', 'rb') as file:
    p_sim = pickle.load(file)

### p_sim이 만들어지는 과정
# plot을 TF-IDF를 통해 유사도 측정한것
# sklearn의 코사인 유사도 사용
###

with open('/opt/ml/input/final_project/Content_based/g_sim.pkl', 'rb') as file:
    g_sim = pickle.load(file)

### g_sim이 만들어지는 과정

# with open(file='/opt/ml/input/final_project/Content_based/bert_em_plot_vec_dict_2.pkl', mode='rb') as f: <- BERT를 통한 장르 임베딩
#     genre_em_vec = pickle.load(f)

# list_of_arrays = [t.detach().numpy() for t in genre_em_vec['genre_vec']] <- tensor를 np.array로 변환

# g_sim = cosine_similarity(list_of_arrays) <- sklearn의 코사인 유사도 이용
###

total_sim = (p_sim+g_sim)/2

checked = list(map(int,input('영화 인덱스를 공백을 두고 입력하세요').split()))
candi_list = []
for k in checked:
    sim_scores = [(i,c) for i, c in enumerate(total_sim[k]) if i != 0] # 자기 자신을 제외한 영화들의 유사도 및 인덱스를 추출
    # 유사도가 높은 순서로 정렬
    sim_scores = sorted(sim_scores, key= lambda x: x[1],reverse=True)
    sim_scores[0:10] # 상위 10개
    candi_list += sim_scores
candi_list = sorted(candi_list, key= lambda x: x[1],reverse=True)
# candi_list[0:10]

# id를 title로 변환
top10 = [(idx2content[i], score) for i , score in candi_list[0:10]]

top10_movie_and_charactors = {}
for t in top10:
    found_charactors = list(set(mbti_all.loc[mbti_all['Contents'] == t[0]]['Character'].to_list()))
    top10_movie_and_charactors[t[0]] = found_charactors

print(top10_movie_and_charactors)