import pandas as pd
import pickle


def final_movie_select(num):
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
    data = pd.read_pickle('/opt/ml/input/Data/DataProcessing/Movie_select/movie_random_select_final.pkl')
 
    # 각 군집에서 영화 랜덤 추출
    data_0 = data.loc[data['cluster'] == 0, :]
    data_0 = data_0.loc[((data_0['contents_year'] >= 2008) & (data_0['npop'] >= 20000)) | \
        ((data_0['contents_year'] <= 2000) & (data_0['npop'] >= 100000))] 
    
    data_1 = data.loc[data['cluster'] == 1, :]
    data_1 = data_1.loc[((data_1['contents_year'] >= 2008) & (data_1['npop'] >= 20000)) | \
        ((data_1['contents_year'] <= 2000) & (data_1['npop'] >= 100000))]
    
    data_2 = data.loc[data['cluster'] == 2, :]
    data_2 = data_2.loc[((data_2['contents_year'] >= 2008) & (data_2['npop'] >= 20000)) | \
        ((data_2['contents_year'] <= 2000) & (data_2['npop'] >= 100000))]
    
    movieId_list = []
    for i in range(3):
        if i == 0: n = round(num * 0.47); df = data_0
        elif i == 1: n = round(num * 0.399); df = data_1
        elif i == 2: n = round(num * 0.13); df = data_2
        movieId_list.extend(list(df.sample(n, replace=False)['movieId']))
    
    return movieId_list
