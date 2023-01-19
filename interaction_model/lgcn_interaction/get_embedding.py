# lightGCN 임베딩 불러서 csv 파일로 저장하기

import torch
import numpy as np
import pandas as pd
from tqdm import tqdm
import pickle
import argparse
from recbole.data import create_dataset, data_preparation, Interaction
from recbole.utils import init_logger, get_trainer, get_model, init_seed, set_color
from recbole.utils.case_study import full_sort_topk
import os

def main(args):
    """Get the embedding of users and items and combine to an embedding matrix.
    
        방법 : python get_embedding.py --model_path "모델 경로"

    Returns:
        Tensor of the embedding matrix. Shape of [n_items+n_users, embedding_dim]
    """
    
    print("start to get embedding!!!")
    
    checkpoint = torch.load(args.model_path)
    config = checkpoint['config']

    init_seed(config['seed'], config['reproducibility'])
    config['dataset'] = 'train_data'
    
    config['eval_args']['split']['RS']=[999999,0,1]

    dataset = create_dataset(config)
    train_data, valid_data, test_data = data_preparation(config, dataset)
    
    model = get_model(config['model'])(config, train_data.dataset).to(config['device'])
    model.load_state_dict(checkpoint['state_dict'])
    model.load_other_parameter(checkpoint.get('other_parameter'))
        
    emb = model.get_ego_embeddings()
    emb = emb.tolist()
    
    print("done!!!👏🏻")
    
    print("saving to file!!!")
    
    import csv
    with open('emb_list.csv','w',newline='') as f:
        writer = csv.writer(f)
        for e in emb:
            writer.writerow(list(e))
            
    print("done!!!👏🏻")
        
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--model_path", default = "/opt/ml/.jupyter/lab/workspaces/BaseLine/saved/LightGCN-model.pth", type=str)
    args = parser.parse_args()
    
    main(args)