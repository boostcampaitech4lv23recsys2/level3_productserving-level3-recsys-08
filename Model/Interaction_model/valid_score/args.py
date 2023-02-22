import argparse

def parse_args():
    """
    parameter를 전달해주는 함수입니다.

    sweep을 이용하려면 이 함수에 추가를 하셔야 합니다.
    
    Returns:
        parser : main에 전달될 args
    """

    parser = argparse.ArgumentParser()

    parser.add_argument("--seed", default=2023, type=int)

    parser.add_argument("--test_user_ratio", default=0.1, type=float)

    parser.add_argument("--embed_size", default=64, type=int)

    parser.add_argument("--als_regularization", default=0.1, type=float)

    parser.add_argument("--als_iterations", default=200, type=int)

    parser.add_argument("--annoy_n_trees", default=40, type=int)

    parser.add_argument("--model_name", default='./ALS_angular_64', type=str)

    parser.add_argument("--valid_ratio", default=0.5, type=float)

    args = parser.parse_args()

    return args

