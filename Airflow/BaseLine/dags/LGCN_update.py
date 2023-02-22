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

host2 = env.get_value('HOST2')
host2_port = env.get_value('HOST2_PORT')
host2_pw = env.get_value('HOST2_PW')

ssh_hook = SSHHook(remote_host=host2, username='root', password=host2_pw, port=int(host2_port))

default_args = {
    'owner': 'cwj',
    'depends_on_past': False,  
    'start_date': datetime(2023, 2, 15),
    'retires': 1,  
    'retry_delay': timedelta(minutes=5) 
}

with DAG(
        dag_id = 'LGCN_update',
        description = 'LGCN daily update',
        tags = ['test'],
        schedule_interval='0 15 * * *',
        default_args = default_args
) as dag:
    make_dataset_cmd="""
    cd /opt/ml/input/project/BaseLine
    python LGCN_update.py --task make_dataset
    """
    make_dataset = SSHOperator(task_id="Make_Dataset", command=make_dataset_cmd, ssh_hook=ssh_hook, get_pty=True, conn_timeout=60)

    train_LGCN_cmd="""
    cd /opt/ml/input/project/BaseLine
    python LGCN_update.py --task train
    """
    train_LGCN = SSHOperator(task_id="Train_LGCN", command=train_LGCN_cmd, ssh_hook=ssh_hook, get_pty=True, conn_timeout=30000, cmd_timeout=9000)

    save_annoy_cmd="""
    cd /opt/ml/input/project/BaseLine
    python LGCN_update.py --task save_annoy
    """
    save_annoy = SSHOperator(task_id="Save_annoy", command=save_annoy_cmd, ssh_hook=ssh_hook, get_pty=True, conn_timeout=30000, cmd_timeout=9000)
    
    share_annoy_cmd=f"""
    sshpass -p {host2_pw} scp -o StrictHostKeyChecking=no -P {host2_port} -r /opt/ml/input/project/BaseLine/LightGCN_64 root@{host2}:/opt/ml/input/project/interaction_model
    """
    share_annoy = SSHOperator(task_id="Share_annoy", command=share_annoy_cmd, ssh_hook=ssh_hook, get_pty=True, conn_timeout=30000, cmd_timeout=9000)

    make_dataset >> train_LGCN >> save_annoy >> share_annoy