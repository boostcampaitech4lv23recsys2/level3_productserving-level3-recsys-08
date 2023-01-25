import annoy
import pandas as pd


def sorted_Inference(file_name: str, movie_list: list, topk: int):
    """user가 선호하는 movie_list를 입력으로 받아 유사도 높은 컨텐츠의 movieId topk개를 반환합니다.

    Args:
        file_name (str): 저장한 Annoy 모델의 파일 이름입니다.
        movie_list (list): 유저가 선택한 영화 리스트입니다.
        topk (int): 유사도 높은 아이템을 리턴할 개수

    Returns:
       result (list): 유사도 높은 아이템의 movieId topk개를 담고 있는 list 입니다.
    """
    length_of_vector = int(file_name.split('_')[-1])

    annoy_model = annoy.AnnoyIndex(length_of_vector, "angular")
    annoy_model.load(file_name)  # Annoy load

    movie_list_len = len(movie_list)
    scores = {}

    for mid in movie_list: # prefer_movie와 유사도가 높을수록 높은 점수를 부여합니다.
        neighbour, dist = annoy_model.get_nns_by_item(mid,500,include_distances=True)
        norm = 2 # max( sqrt(2-2cos) )
        cnt = 0
        for n,d in zip(neighbour[1:],dist[1:]):
            if cnt == topk:
                break
            if n not in movie_list: # 유사한 영화가 prefer에 포함되어있으면 안됩니다.
                try:
                    scores[n] += 1-d/norm # angular similarity가 낮을수록 score를 높게 측정합니다.
                except:
                    scores[n] = 0
                    scores[n] += 1-d/norm
                cnt += 1
        assert cnt >= topk, "갯수가 모자라요" #cnt가 topk보다 작을 때 error 발생

    sort_scores = sorted(scores.items(),key = lambda x: -x[1])[:topk] # score를 내림차순 정렬 해줍니다.
    result = [x[0] for x in sort_scores]
    
    return result


def Inference(file_name: str, movieId: int, topk: int):
    """movieId를 입력으로 받아 유사도 높은 컨텐츠의 movieId topk를 반환합니다.
    Args:
        file_name (str): 저장한 Annoy 모델의 파일 이름입니다.
        movieId (int): 유저가 선택한 영화입니다.
        topk (int): 유사도 높은 아이템을 리턴할 개수
    Returns:
       result (list): 유사도 높은 아이템의 movieId topk개를 담고 있는 list 입니다.
    """
    length_of_vector = int(file_name.split('_')[-1])

    loaded_annoy = annoy.AnnoyIndex(length_of_vector, "angular")
    loaded_annoy.load(file_name)  # Annoy load

    neighbour, dist = loaded_annoy.get_nns_by_item(movieId, topk+1, include_distances=True)
    # 첫 번째 인덱스는 입력으로 넣은 movieId 이므로 제외합니다.

    return neighbour[1:], dist


file_name = './ALS_angular_64'
movie_list = [1, 32, 50, 110, 150, 193, 296, 318, 356, 380]
topk = 10
print(sorted_Inference(file_name, movie_list, topk))