import argparse
from util import inference, general_inference
import warnings
warnings.filterwarnings('ignore')

def main(args):
    model_path = args.model_path
    topk = int(args.top_k)
    mode = args.mode
    model_name = model_path[8:-4].split('-')[0]

    if mode=="global":
        inference(model_name=model_name, topk=topk, model_path=model_path)
    elif mode=="general":
        general_inference(model_name=model_name, topk=topk, model_path=model_path)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--model_path", required=True, type=str)
    parser.add_argument("--top_k", default = 10, type=int)
    parser.add_argument("--mode", default = "global", type=str)
    args = parser.parse_args()

    main(args)