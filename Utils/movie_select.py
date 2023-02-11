import os
import pandas as pd
import numpy as np
from sklearn import cluster 
from sklearn import preprocessing
from pathlib import Path

# 현재 파일 기준 경로잡기
cur_filepath = lambda path: os.path.join(os.path.abspath(os.path.dirname(__file__)),path)

### movie_select() 함수에서 필요한 함수들
def delete_s(sen):
    sen = sen.replace(" ","")
    return sen


def delete(genre_sentence):
    try:
        genre_sentence = genre_sentence.replace("'","")
        genre_sentence = genre_sentence[genre_sentence.index("[")+1:genre_sentence.index("]")]
        genre_sentence = list(map(delete_s, genre_sentence.split(",")))
        return genre_sentence
    except:
        return ["no_genre"]
    
def get_encoding(genre, encoding, genre_dic):
    g_encoding = np.zeros(28)
    for g in genre:
        g_encoding += encoding[genre_dic[g]]
    return g_encoding
###

def movie_select():
    """
        유저가 선호하는 영화를 선택하는 페이지에서 사용되는 영화 랜덤 추출 함수입니다.
        처리 내용 : 연도(>=2000), 인터랙션(>=1000), 클러스터링(0 : 6개, 1 : 1개, 2 : 3개)
        리턴 값 : 10개의 movieId가 담긴 리스트
    """
    
    # 데이터 불러오기 - 자료실에서 해당 데이터 다운받아서 사용하시면 됩니다.
    data_3229 = pd.read_csv("/opt/ml/.jupyter/lab/workspaces/data/3229_plus_side_info_plus_korean_genre_and_plot.csv")
    ml_inter = pd.read_csv("/opt/ml/.jupyter/lab/workspaces/data/ml-25m/ratings.csv")

    # 데이터프레임 제작 과정
    data = data_3229[['Contents', 'Votes', 'movieId', 'genres']]
    data = data.drop_duplicates(subset=['movieId'])
    data['movieId'] = data['movieId'].apply(lambda x : int(x))
    data['genres_list'] = data['genres'].apply(lambda x:delete(x))
    
    genre = []
    for genres in list(data['genres_list']):
        genre.extend(genres)
    genre = list(set(genre))

    values = []
    for x in range(len(genre)):
        values.append(x)

    encoding = np.eye(len(values))[values]

    genre_dic = dict()
    for idx, g in enumerate(genre):
        genre_dic[g] = idx

    data['genre_encode'] = data['genres_list'].apply(lambda x: get_encoding(x, encoding, genre_dic))

    encode_df = pd.merge(data['movieId'], pd.DataFrame(list(data['genre_encode']), index=data['movieId']), on='movieId',how='inner')
    X = encode_df.iloc[:,1:]
    
    kmeans = cluster.KMeans(n_clusters=3, random_state=2023)
    
    X = preprocessing.StandardScaler().fit_transform(X)
    kmeans.fit(X)
    
    cluster_label = kmeans.labels_ 
    encode_df['cluster1'] = cluster_label
    
    data = pd.merge(data, encode_df[['movieId','cluster1']], on='movieId', how='inner')
    
    inter = pd.DataFrame(ml_inter.groupby('movieId')['userId'].count().reset_index())
    data = pd.merge(data, inter, on='movieId', how='left')

    year = data['Contents'].apply(lambda x: x.strip()[-5:-1])
    year_li = []
    for y in year:
        try:
            year_li.append(int(y))
        except:
            year_li.append(0)
    data['year'] = year_li
    
    # 인터랙션 >= 1000, 연도 >= 2000 데이터 필터링
    ml_select = data[(data['userId'] >= 1000) & (data['year'] >= 2000)]
    
    # 각 군집에서 영화 랜덤 추출
    movieId_list = []
    for i in range(3):
        if i == 0: n = 6
        elif i == 1: n = 1
        elif i == 2: n = 3
        movieId_list.extend(list(ml_select[ml_select['cluster1'] == i].sample(n, replace=False)['movieId']))
    
    return movieId_list


def movie_select_2(seed, N):
    """
        위의 movie_select() 함수와 동일한 결과를 얻는 함수입니다.
        다만 연도 처리(2000년 이상 영화), 인터랙션 처리(1000 이상 영화), 클러스터링이 다 끝난 상태로 저장된
        "movie_random_select_3229.csv" 파일을 바로 불러와서 군집별로 추천 결과만 바로 뽑아줍니다.
    """

    np.random.seed(seed)
    select = pd.read_pickle(Path(__file__).parent.absolute() / "Pickle/movie_random_select_3229.pickle")
    
    movieId_list = []
    for i in range(3):
        if i == 0: n = (N//10)*6 + 1
        elif i == 1: n = (N//10)*1 + 1
        elif i == 2: n = (N//10)*3 + 1
        movieId_list.extend(list(select[select['cluster1'] == i].sample(n, replace=False)['movieId']))
        
    return movieId_list[:N]


def final_movie_select(seed, num):
    """
        유저가 선호하는 영화를 선택하는 페이지에서 사용되는 함수입니다.
        "movie_random_select_final.csv" 파일을 바로 불러와서 각 군집별로 상위 popular, 최신 영화의 추천 결과만 바로 뽑아줍니다.
        
        Param num : 랜덤으로 얻고 싶은 영화 개수 (ex. 20)
        
        <군집별 데이터 개수 비율> 
            0 : 약 47.0%
            1 : 약 39.9%
            2 : 약 13.0%
    """
    
    # 데이터 불러오기 - 트렐로 페이지에서 해당 데이터 다운받아서 사용하시면 됩니다.
    data = pd.read_pickle(cur_filepath('Pickle/movie_random_select_final2.pickle'))
 
    # 각 군집에서 영화 랜덤 추출
    data_0 = data.loc[data['cluster'] == 0, :]
    data_0 = data_0[((data_0['contents_year'] >= 2008) & (data_0['npop'] >= 100000)) | \
        ((data_0['contents_year'] <= 2000) & (data_0['npop'] >= 300000)) | \
        ((data_0['contents_year'] >= 2019) & (data_0['npop'] >= 10000)) |  \
        (data_0.country.str.contains("한국"))]
    data_1 = data.loc[data['cluster'] == 1, :]
    data_1 = data_1[((data_1['contents_year'] >= 2008) & (data_1['npop'] >= 100000)) | \
        ((data_1['contents_year'] <= 2000) & (data_1['npop'] >= 300000)) | \
        ((data_1['contents_year'] >= 2019) & (data_1['npop'] >= 10000)) |  \
        (data_1.country.str.contains("한국"))]
    
    data_2 = data.loc[data['cluster'] == 2, :]
    data_2 = data_2[((data_2['contents_year'] >= 2008) & (data_2['npop'] >= 100000)) | \
        ((data_2['contents_year'] <= 2000) & (data_2['npop'] >= 300000)) | \
        ((data_2['contents_year'] >= 2019) & (data_2['npop'] >= 10000)) |  \
        (data_2.country.str.contains("한국"))]
    
    np.random.seed(seed)
    movieId_list = []
    for i in range(3):
        if i == 0: n = round(num * 0.47); df = data_0
        elif i == 1: n = round(num * 0.399); df = data_1
        elif i == 2: n = round(num * 0.13); df = data_2
        movieId_list.extend(list(df.sample(n, replace=False)['movieId']))
    
    return movieId_list

if __name__=="__main__":
    # print(movie_select_2(42,30))
    print(final_movie_select(seed=42, num=30))