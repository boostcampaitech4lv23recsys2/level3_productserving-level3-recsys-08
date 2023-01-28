import pandas as pd
import numpy as np
from sklearn import cluster 
from sklearn import preprocessing

### inter_movie_select() 함수에서 필요한 함수들
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
        return None
    
def get_encoding(genre, encoding, genre_dic):
    g_encoding = np.zeros(len(genre_dic))
    for g in genre:
        g_encoding += encoding[genre_dic[g]]
    return g_encoding
###


def inter_movie_select():
    """
        유저가 선호하는 영화를 선택하는 페이지에서 사용되는 영화 랜덤 추출 함수입니다.
        처리 내용 : year(>=2008), inter(>=3000), cluster(0 : 6개, 1 : 12개, 2 : 2개)
        리턴 값 : 20개의 movieId가 담긴 리스트
    """
    
    # 데이터 불러오기 - 자료실에서 해당 데이터 다운받아서 사용하시면 됩니다.
    data_3229 = pd.read_csv("/data/3229_plus_side_info_plus_korean_genre_and_plot.csv")
    ml_inter = pd.read_csv("/data/ml-25m/ratings.csv")

    # 데이터프레임 제작 과정
    data = data_3229[['Contents', 'movieId', 'genres']]
    data = data.drop_duplicates(subset=['movieId'])
    data['movieId'] = data['movieId'].apply(lambda x : int(x))
    
    # 장르 클러스터링 컬럼 생성
    data['genres_list'] = data['genres'].apply(lambda x:delete(x))
    data.dropna(axis=0, inplace=True)
    
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
    X = preprocessing.StandardScaler().fit_transform(X)
    
    kmeans = cluster.KMeans(n_clusters=3, random_state=2023)
    kmeans.fit(X)
    
    cluster_label = kmeans.labels_ 
    encode_df['cluster'] = cluster_label
    
    data = pd.merge(data, encode_df[['movieId','cluster']], on='movieId', how='inner')
    
    # 인터랙션 컬럼 생성
    inter = pd.DataFrame(ml_inter.groupby('movieId')['userId'].count().reset_index())
    data = pd.merge(data, inter, on='movieId', how='left')
    data.columns = ['Contents', 'movieId', 'genres', 'genres_list', 'genre_encode', 'cluster', 'inter']
    
    # 연도 컬럼 생성
    year = data['Contents'].apply(lambda x: x.strip()[-5:-1])
    year_li = []
    for y in year:
        try:
            year_li.append(int(y))
        except:
            year_li.append(None)
    data['year'] = year_li
    data.dropna(axis=0, inplace=True)
    data['year'] = data['year'].apply(lambda x: int(x))
    
    # 각 군집에서 영화 랜덤 추출
    data_0 = data.loc[data['cluster'] == 0, :]
    data_0 = data_0.loc[(data_0['year'] >= 2008) & (data_0['inter'] >= 3000)]
    
    data_1 = data.loc[data['cluster'] == 1, :]
    data_1 = data_1.loc[(data_1['year'] >= 2008) & (data_1['inter'] >= 3000)]
    
    data_2 = data.loc[data['cluster'] == 2, :]
    data_2 = data_2.loc[(data_2['year'] >= 2008) & (data_2['inter'] >= 3000)]
    
    movieId_list = []
    for i in range(3):
        if i == 0: n = 6; df = data_0
        elif i == 1: n = 12; df = data_1
        elif i == 2: n = 2; df = data_2
        movieId_list.extend(list(df.sample(n, replace=False)['movieId']))
    
    return movieId_list


def inter_movie_select_2():
    """
        위의 inter_movie_select() 함수와 동일한 결과를 얻는 함수입니다.
        다만 "movie_random_select_3229.csv" 파일을 바로 불러와서 각 군집별로 상위 인터랙션, 최신 영화의 추천 결과만 바로 뽑아줍니다.
    """
    
    # 데이터 불러오기 - 트렐로 페이지나 자료실에서 해당 데이터 다운받아서 사용하시면 됩니다.
    data = pd.read_csv("/movie_random_select_3229.csv")
    
    # 각 군집에서 영화 랜덤 추출
    data_0 = data.loc[data['cluster'] == 0, :]
    data_0 = data_0.loc[(data_0['year'] >= 2008) & (data_0['inter'] >= 3000)]
    
    data_1 = data.loc[data['cluster'] == 1, :]
    data_1 = data_1.loc[(data_1['year'] >= 2008) & (data_1['inter'] >= 3000)]
    
    data_2 = data.loc[data['cluster'] == 2, :]
    data_2 = data_2.loc[(data_2['year'] >= 2008) & (data_2['inter'] >= 3000)]
    
    movieId_list = []
    for i in range(3):
        if i == 0: n = 6; df = data_0
        elif i == 1: n = 12; df = data_1
        elif i == 2: n = 2; df = data_2
        movieId_list.extend(list(df.sample(n, replace=False)['movieId']))
    
    return movieId_list



### side_movie_select() 함수에서 필요한 함수들
def cleaning(pop):
    if "만" in pop:
        return int(pop.replace("만","0000"))
    if "," in pop:
        return int(pop.replace(",", ""))
    return int(pop)

def delete2(genre_sentence):
    try:
        genre_sentence = genre_sentence.replace("'","")
        genre_sentence = list(map(delete_s, genre_sentence.split(",")))
        return genre_sentence
    except:
        return None
###
    
    
def side_movie_select():
    """
        유저가 선호하는 영화를 선택하는 페이지에서 사용되는 영화 랜덤 추출 함수입니다.
        처리 내용 : year(>=2008), popular(>=20000), cluster (0 : 10개, 1 : 4개, 2 : 6개)
        리턴 값 : 20개의 movieId가 담긴 리스트
    """
    
    # 데이터 불러오기 - 자료실에서 해당 데이터 다운받아서 사용하시면 됩니다.
    data_4035 = pd.read_csv("/data/content_based_4035.csv")
    data = data_4035[['Contents', 'movieId', 'genres', 'popular', 'year']]
    
    # "no_data" 결측치 처리 과정
    data[data['popular'] != "no_data"][data['year'] == "no_data"]
    data.loc[data['movieId'] == 156002, 'year'] = 2015
    data = data[data['popular'] != "no_data"]
    data = data[data['year'] != "no_data"]
    data.dropna(axis=0, inplace=True)
    data['year'] = data.loc[:, 'year'].apply(lambda x: int(x))
    
    # popular 컬럼 처리 과정
    data['popular'] = data.loc[:,'popular'].apply(lambda x: cleaning(x))
    
    # 장르 클러스터링 컬럼 생성
    data['genres_list'] = data['genres'].apply(lambda x:delete2(x))
    
    genre = []
    for genres in list(data['genres_list']):
        genre.extend(genres)
    genre = list(set(genre))
    
    values = []
    for x in range(len(genre)):
        values.append(x)

    genre_dic = dict()
    for idx, g in enumerate(genre):
        genre_dic[g] = idx

    encoding = np.eye(len(values))[values]
    
    data['genre_encode'] = data['genres_list'].apply(lambda x: get_encoding(x, encoding, genre_dic))
    encode_df = pd.merge(data['movieId'], pd.DataFrame(list(data['genre_encode']), index=data['movieId']), on='movieId',how='inner')
    
    X = encode_df.iloc[:,1:]
    X = preprocessing.StandardScaler().fit_transform(X)
    
    kmeans = cluster.KMeans(n_clusters=3, random_state=2023)
    kmeans.fit(X)
    
    cluster_label = kmeans.labels_ 
    encode_df['cluster'] = cluster_label
    
    data = pd.merge(data, encode_df[['movieId','cluster']], on='movieId', how='inner')
    
    # 각 군집에서 영화 랜덤 추출
    data_0 = data.loc[data['cluster'] == 0, :]
    data_0 = data_0.loc[(data_0['year'] >= 2008) & (data_0['popular'] >= 20000)]
    
    data_1 = data.loc[data['cluster'] == 1, :]
    data_1 = data_1.loc[(data_1['year'] >= 2008) & (data_1['popular'] >= 20000)]
    
    data_2 = data.loc[data['cluster'] == 2, :]
    data_2 = data_2.loc[(data_2['year'] >= 2008) & (data_2['popular'] >= 20000)]
    
    movieId_list = []
    for i in range(3):
        if i == 0: n = 10; df = data_0
        elif i == 1: n = 4; df = data_1
        elif i == 2: n = 6; df = data_2
        movieId_list.extend(list(df.sample(n, replace=False)['movieId']))
    
    return movieId_list
    
    
    
def side_movie_select_2():
    """
        위의 side_movie_select() 함수와 동일한 결과를 얻는 함수입니다.
        다만 "movie_random_select_4035.csv" 파일을 바로 불러와서 각 군집별로 상위 popular, 최신 영화의 추천 결과만 바로 뽑아줍니다.
    """
    
    # 데이터 불러오기 - 트렐로 페이지나 자료실에서 해당 데이터 다운받아서 사용하시면 됩니다.
    data = pd.read_csv("/movie_random_select_4035.csv")
    
    # 각 군집에서 영화 랜덤 추출
    data_0 = data.loc[data['cluster'] == 0, :]
    data_0 = data_0.loc[(data_0['year'] >= 2008) & (data_0['popular'] >= 20000)]
    
    data_1 = data.loc[data['cluster'] == 1, :]
    data_1 = data_1.loc[(data_1['year'] >= 2008) & (data_1['popular'] >= 20000)]
    
    data_2 = data.loc[data['cluster'] == 2, :]
    data_2 = data_2.loc[(data_2['year'] >= 2008) & (data_2['popular'] >= 20000)]
    
    movieId_list = []
    for i in range(3):
        if i == 0: n = 10; df = data_0
        elif i == 1: n = 4; df = data_1
        elif i == 2: n = 6; df = data_2
        movieId_list.extend(list(df.sample(n, replace=False)['movieId']))
    
    return 