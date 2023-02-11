import os
import json
import argparse
import pandas as pd
import numpy as np
import time, datetime
from tqdm import tqdm
from logging import getLogger
from args import parse_args
import torch
import mlflow
from recbole.quick_start import run_recbole
import wandb
from pathlib import Path
from feature_engineering import FE
from util import inference, make_dataset, make_config, mvti_recommend

# 필수
# python train.py --model_name [] --config []

def main(args):
    """모델 train, inference 파일

    args:
        model_name(default - "EASE") : 모델의 이름을 입력받습니다.

        infer(default - False) : 
            True일 경우 submission을 저장합니다.
            inference 과정이 느리기 때문에 필요없다면 False로 하는게 좋습니다.

        dataset_name(default - "train_data) : 데이터셋의 이름을 불러옵니다.

        config_name(default - "basic_config.yaml") : config 정보가 담긴 yaml 파일 이름을 불러옵니다.
        🔥🔥🔥 주의 )) 모델이 여러 종류이기 때문에, 사용하는 모델에 맞춰서 config 파일 이름을 꼭 입력해주세요 ‼️
        
        topk(default - 10) : inference를 할 경우에 submission에 유저마다 몇 개의 아이템을 추천할지 정할 수 있습니다.

        나머지는 hyper parameter 입니다. 
    """
    ## MLflow 
    remote_server_uri="http://101.101.219.178:30005"
    mlflow.set_tracking_uri(remote_server_uri)

    # ✨ sequential model ✨
    seq_list = ['FPMC', 'GRU4Rec', 'NARM', 'STAMP', 'Caser', 'NextItNet', 'TransRec', 'SASRec',
                 'BERT4Rec', 'SRGNN', 'GCSAN','GRU4RecF', 'SASRecF', 'FDSA', 'S3Rec']
    
    model_name = args.model_name
    infer = args.inference
    config_name = args.config
    top_k = args.top_k
    dataset_name = args.dataset_name
    
    # Set MLflow Experiment
    client = mlflow.tracking.MlflowClient()
    experiment_name = model_name # "EASE" # experiment 이름
    try:
        experiment_id = client.create_experiment(experiment_name)
    except:
        experiment = client.get_experiment_by_name(experiment_name)
        experiment_id = experiment.experiment_id

    # dataset이 하나라도 없을 경우 생성
    # if (not os.path.isfile(f'./dataset/{dataset_name}/{dataset_name}.inter')) or\
    #     (not os.path.isfile(f'./dataset/{dataset_name}/{dataset_name}.item')) or\
    #     (not os.path.isfile(f'./dataset/{dataset_name}/{dataset_name}.user')):
    #     print("Make dataset...")
    #     make_dataset(dataset_name)

    # config 파일이 없을 경우 생성                
    if not os.path.isfile(f'./{config_name}'):
        print("Make config...")
        make_config(config_name)

    parameter_dict = args.__dict__
   
    # Default eval_args를 저장
    if model_name not in seq_list:
        parameter_dict['eval_args'] = {
            'split': {'RS': [9, 1, 0]},
            'group_by': 'user',
            'order': 'RO',
            'mode': 'full',}
    
    # Sequential 모델일 경우 eval_args와 loss_type을 변경
    if model_name in seq_list:
        parameter_dict['eval_args'] = {
            'split': {'RS': [9, 1, 0]},
            'group_by': 'user',
            'order': 'TO',
            'mode': 'full',}
    #     parameter_dict['loss_type'] = 'BPR'
    
    # inference가 필요한 모델일 경우 1:0:0 학습 변경
    # if infer:
    #     parameter_dict['eval_args']['split'] = {'RS' : [1,0,0]}
    
    print(f"running {model_name}...")
    result = run_recbole(
        model = model_name,
        dataset = dataset_name,
        config_file_list = [config_name],
        config_dict = parameter_dict,
    )
    
    # model_name이 들어가는 pth 파일 중 최근에 생성된 걸로 불러옴
    os.makedirs('saved',exist_ok=True)
    save_path = os.listdir('./saved')
    model_path = './saved/' + sorted([file for file in save_path if model_name in file ])[-1]
    model_path_absolute = Path(model_path).absolute()

    run_name=model_name
    desc=f"Model path: {model_path_absolute}"
    with mlflow.start_run(run_name=run_name, description=desc, experiment_id=experiment_id) as run:
        for metric, score in result['best_valid_result'].items():
            print(metric,score)
            mlflow.log_metric(metric.replace('@','.'), score)
    print(result)
    wandb.run.finish()

    if infer:
        mvti_recommend(model_name,top_k)
    
if __name__ == "__main__":
    args = parse_args()
    main(args)