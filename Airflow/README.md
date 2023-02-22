# Airflow

## A. Orchestrator 개요

![Airflow](https://user-images.githubusercontent.com/57648890/220565436-a246ce6a-48c8-4a3b-bbff-72a16eacb45f.png)

- **Batch Training Pipeline**

    - 배치 추천 모델인 **ADER**와 실시간 추천 모델인 **LEA** 학습 → Valid Score는 mlflow에 기록

- **Orchestrator**

    - Airflow를 이용해 aistage 서버를 최대한 활용

<br>

## B. ADER DAG

![ADER](https://user-images.githubusercontent.com/57648890/220566480-442c4609-2185-4f81-8fb7-1e5eef2da013.png)

- <span style='color:red'>AD</span>MMSLIMM + <span style='color:red'>E</span>ASE + <span style='color:red'>R</span>ecVAE

<br>

## C. MLflow 기록
![MLflow](https://user-images.githubusercontent.com/57648890/220566786-4af9d145-8ae0-4904-899c-ca20f903c773.png)

- **배치 추천**

    - ADMMSLIM, RecVAE, EASE의 성능 기록

- **실시간 추천**

    - LightGCN의 성능 기록
