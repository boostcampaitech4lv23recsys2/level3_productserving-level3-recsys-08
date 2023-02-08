import os
import pandas as pd
from pathlib import Path
from environ import Env
from airflow import DAG
from airflow.operators.python import PythonOperator
from sqlalchemy import create_engine
from datetime import date,timedelta,datetime
import mysql.connector
import json

default_args = {
    'owner': 'cwj',
    'depends_on_past': False,  
    'start_date': datetime(2023, 2, 2),
    'retires': 1,  
    'retry_delay': timedelta(minutes=5) 
    # 'priority_weight': 10 
    # 'end_date': datetime(2022, 4, 24) 
    # 'execution_timeout': timedelta(seconds=300),
    # 'on_failure_callback': some_function
    # 'on_success_callback': some_other_function
    # 'on_retry_callback': another_function
}

def load_yesterday_summary():
    BASE_DIR = Path(os.curdir).resolve()
    env = Env()
    env_path = BASE_DIR / "level3_productserving-level3-recsys-08/django/.env"
    if env_path.exists():
        with env_path.open("rt",encoding="utf8") as f:
            env.read_env(f,overwite = True)

    dbname = env.get_value("GCPDB_NAME")
    user = env.get_value("GCPDB_USER")
    pw = env.get_value("GCPDB_PASSWORD")
    host = env.get_value("GCPDB_HOST")

    engine = create_engine(f"mysql+mysqldb://{user}:{pw}@{host}:3306/{dbname}")


    today = datetime.today()
    yesterday = datetime.today() - timedelta(1)

    df = pd.read_sql_query(f"select * from test_rec_tmpuser WHERE create_time BETWEEN '{str(yesterday)}' AND '{str(today)}' ",engine)


    MBTI_summary = df.value_counts("MBTI").to_dict()

    prefer_summary = {}
    for p in df['prefer_movie_id']:
        if p != None:
            p = json.loads(p)
            for mid in list(p):
                try :
                    prefer_summary[mid] +=1
                except :
                    prefer_summary[mid] = 1

    recommend_summary = {}
    for r in df['recommended_character_id']:
        if r != None:
            r = json.loads(r)
            for mid in list(r):
                try :
                    recommend_summary[mid] +=1
                except :
                    recommend_summary[mid] = 1


    fit_summary = {}
    for f in df['fit_character_id']:
        if f != None:
            f = json.loads(f)
            for mid in list(f):
                try :
                    fit_summary[mid] +=1
                except :
                    fit_summary[mid] = 1

    prefer_summary = dict(sorted(prefer_summary.items(),key = lambda x: -x[1]))
    recommend_summary = dict(sorted(recommend_summary.items(),key = lambda x: -x[1]))
    fit_summary = dict(sorted(fit_summary.items(),key = lambda x: -x[1]))




    conn = mysql.connector.connect(
        host=host,
        user=user,
        password=pw,
        db=dbname,
        charset='utf8'
    )

    datetime_value = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    cursor = conn.cursor()

    query = "INSERT INTO summary (MBTI_summary, prefer_summary, character_summary, fit_character_summary,create_time) VALUES (%s, %s, %s, %s, %s)"

    cursor.execute(query, (json.dumps(MBTI_summary),json.dumps(prefer_summary),json.dumps(recommend_summary),json.dumps(fit_summary),datetime_value))


    conn.commit()

    cursor.close()
    conn.close()
    


with DAG(
        dag_id='daily_summary',
        default_args=default_args,
        schedule_interval='0 15 * * *',

        tags=['summary']
) as dag:
    python_task = PythonOperator(
        task_id='yesterday_summary',
        python_callable=load_yesterday_summary
    )

    python_task