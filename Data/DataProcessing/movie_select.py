import pandas as pd

def movie_select():
    ml = pd.read_csv("/opt/ml/.jupyter/lab/workspaces/data/ml-25m/movies.csv")
    ml_inter = pd.read_csv("/opt/ml/.jupyter/lab/workspaces/data/ml-25m/ratings.csv")

    inter = pd.DataFrame(ml_inter.groupby('movieId')['userId'].count().reset_index())
    ml['inter'] = inter['userId']

    year = ml['title'].apply(lambda x: x.strip()[-5:-1])
    year_li = []
    for y in year:
        try:
            year_li.append(int(y))
        except:
            year_li.append(0)
    ml['year'] = year_li

    ml_select = ml[(ml['inter'] >= 1000) & (ml['year'] >= 2000)]
    movieId_list = list(ml_select.sample(10, replace=False)['movieId'])
    
    return movieId_list