import argparse

class ParseAction(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        print('%r %r %r' % (namespace, values, option_string))
        values = list(map(int, values.split()))
        setattr(namespace, self.dest, values)


def parse_args():
    """
    parameter를 전달해주는 함수입니다.

    sweep을 이용하려면 이 함수에 추가를 하셔야 합니다.

    default 값만 사용하신다면 굳이 추가 안하셔도 됩니다.

    예시로 EASE, MultiVAE, MultiDAE, CDAE를 추가하였습니다.

    Returns:
        parser : main에 전달될 args
    """
    parser = argparse.ArgumentParser()

    parser.add_argument("--epochs", default=1, type=int)

    parser.add_argument("--model_name", default="EASE", type=str)

    parser.add_argument("--dataset_name", default="train_data", type=str)

    parser.add_argument("--inference", default=True, type=lambda s : s.lower() in ['true','1'])

    parser.add_argument("--config",default = "basic_config.yaml",type=str)

    parser.add_argument("--top_k",default = 500,type=int)

    parser.add_argument("--mvti",default=False, type=lambda s : s.lower() in ['true','1'])

    parser.add_argument("--wandb",default=False, type=lambda s : s.lower() in ['true','1'])

#     #EASE
    parser.add_argument("--reg_weight", default=250.0, type=float)

#     #ADMMSLIM
    parser.add_argument("--lambda1", default=3.0, type=float)

    parser.add_argument("--lambda2", default=200.0, type=float)

    parser.add_argument("--alpha", default=0.5, type=float)

    parser.add_argument("--rho", default=4000.0, type=float)

    parser.add_argument("--k", default=100, type=int)

#     #MultiVAE, MultiDAE, NeuMF
    parser.add_argument("--latent_dimendion", default=128, type=int)

    parser.add_argument("--mlp_hidden_size", default=[600], type=list) # list 형태 sweep 적용

    parser.add_argument("--dropout_prob", default=0.5, type=float)
    
#     #MultiVAE
#     parser.add_argument("--anneal_cap", default=0.2, type=float)

#     parser.add_argument("--total_anneal_steps", default=200000, type=int)

#     #CDAE
    parser.add_argument("--hid_activation", default="relu", type=str)

    parser.add_argument("--out_activation", default="sigmoid", type=str)

    parser.add_argument("--corruption_ratio", default=0.5, type=float)

    parser.add_argument("--embedding_size", default=64, type=int)

#     parser.add_argument("--reg_weight_1", default=0., type=float)

#     parser.add_argument("--reg_weight_2", default=0.01, type=float)

#     # NeuMF
    parser.add_argument("--mf_embedding_size", default=64, type=int)

    parser.add_argument("--mlp_embedding_size", default=64, type=int)
    
#     # SLIMElastic
#     parser.add_argument("--l1_ratio", default=0.02, type=float)
    
    # RecVAE
    parser.add_argument("--hidden_dimension", default=600, type=int)
    
    parser.add_argument("--latent_dimension", default=200, type=int)
    
    parser.add_argument("--beta", default=0.2, type=float)
    
    parser.add_argument("--gamma", default=0.005, type=float)
    
    # DCN

    parser.add_argument("--cross_layer_num", default=6, type=int)

    # S3Rec

    parser.add_argument("--pretrain_epochs", default=10, type=int)

    parser.add_argument("--save_step", default=10, type=int)

    parser.add_argument("--pre_model_path", default='', type=str)

    parser.add_argument("--train_stage", default='pretrain', type=str)

    # LightGCN

    parser.add_argument("--n_layers", default=2, type=int)

    args = parser.parse_args()

    return args