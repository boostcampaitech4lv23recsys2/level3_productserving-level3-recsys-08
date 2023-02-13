from airflow import DAG
from datetime import datetime
from airflow.providers.ssh.operators.ssh import SSHOperator
from airflow.providers.ssh.hooks.ssh import SSHHook
from airflow.operators.dummy import DummyOperator
from datetime import date,timedelta,datetime
from pathlib import Path
from environ import Env
import os

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent
print(BASE_DIR)
env = Env()
env_path = BASE_DIR / ".env"
if env_path.exists():
    with env_path.open("rt", encoding="utf8") as f:
        env.read_env(f, overwrite=True)

host1 = env.get_value('HOST1')
host1_port = env.get_value('HOST1_PORT')
host1_pw = env.get_value('HOST1_PW')

ssh_hook = SSHHook(remote_host=host1, username='root', password=host1_pw, port=int(host1_port))

default_args = {
    'owner': 'cwj',
    'depends_on_past': False,  
    'start_date': datetime(2023, 2, 13),
    'retires': 1,  
    'retry_delay': timedelta(minutes=5) 
}

with DAG(
        dag_id = 'Batch_Train',
        description = 'sample description',
        tags = ['test'],
        schedule_interval='0 15 * * *',
        default_args = default_args
) as dag:
    make_dataset_cmd="""
    cd /opt/ml/project2/Airflow/00_User_Recommend
    python Real_user_to_train_inter.py
    """
    make_dataset = SSHOperator(task_id="Make_Dataset", command=make_dataset_cmd, ssh_hook=ssh_hook, get_pty=True, conn_timeout=60)

    train_ease_recommend_cmd="""
    cd /opt/ml/project2/BaseLine
    python mvti_recommend.py --model_name EASE
    """
    ease = SSHOperator(task_id="EASE_Recommend", command=train_ease_recommend_cmd, ssh_hook=ssh_hook, get_pty=True, conn_timeout=30000, cmd_timeout=9000)

    train_admm_recommend_cmd="""
    cd /opt/ml/project2/BaseLine
    python mvti_recommend.py --model_name ADMMSLIM
    """
    admmslim = SSHOperator(task_id="ADMMSLIM_Recommend", command=train_admm_recommend_cmd, ssh_hook=ssh_hook, get_pty=True, conn_timeout=30000, cmd_timeout=9000)

    train_recvae_recommend_cmd="""
    cd /opt/ml/project2/BaseLine
    python mvti_recommend.py --model_name RecVAE
    """
    recvae = SSHOperator(task_id="RecVAE_Recommend", command=train_recvae_recommend_cmd, ssh_hook=ssh_hook, get_pty=True, conn_timeout=30000, cmd_timeout=9000)


    dummy = DummyOperator(task_id="dummy")

    ensemble_recommend_cmd="""
    cd /opt/ml/project2/Airflow/02_Ensemble
    python mvti_ensemble.py
    """
    ensemble = SSHOperator(task_id="ADER_Ensemble_Recommend", command=ensemble_recommend_cmd, ssh_hook=ssh_hook, get_pty=True, conn_timeout=30000, cmd_timeout=9000)
    
    make_dataset >> [ease, admmslim, recvae]
    [ease, admmslim, recvae] >> dummy >> ensemble