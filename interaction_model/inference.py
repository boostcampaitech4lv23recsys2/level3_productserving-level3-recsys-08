import annoy
import pandas as pd



def Inference(file_name: str, movieId: int, topk: int):
    """movieId를 입력으로 받아 유사도 높은 컨텐츠의 movieId를 반환합니다.

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
