# Model

## A. 모델 개요
<p align="center"><img src="https://user-images.githubusercontent.com/71438046/217650869-9b7a0720-0261-4b28-be0b-afbd7a6ae5ed.png" /><br><br></p>

## B. 모델 선정 및 분석  
<br>

1️⃣ **BTS**

![BTS](https://user-images.githubusercontent.com/79351899/220557592-93a94d11-7384-4a6a-a2b3-01ac769072ec.png)

- **<span style='color:red'>B</span>ERT + <span style='color:red'>T</span>F-IDF + Cosine <span style='color:red'>S</span>imilarity** (자체 제작)
- 한 영화의 **장르, 줄거리 정보**를 각각 **BERT**와 **TF-IDF**를 통해 벡터화
- 벡터 값을 통해 영화 간 **Cosine Similarity Matrix**를 생성
- 입력 받은 영화와 장르, 줄거리가 가장 유사한 영화를 순서대로 출력

<br>

2️⃣ **LEA**

![LEA](https://user-images.githubusercontent.com/79351899/220557568-b40ee931-59c7-4d5e-bd48-ed075c4a9f86.png)

- **<span style='color:red'>L</span>ightGCN <span style='color:red'>E</span>mbedding + <span style='color:red'>A</span>nnoy** (자체 제작)
- 영화와 유저 간의 관계를 **그래프 형태로 모델링** 후 임베딩 벡터 추출
    - 인접한 노드의 정보를 고려하여 임베딩 벡터를 학습하기 때문에, **유저와 영화의 관계를 잘 표현**
- 학습된 임베딩 벡터를 **Annoy**에 넣어 특정 벡터와 **유사한 벡터를 찾아 Top-N 추천**

<br>

3️⃣ **ADER**

![ADER_1](https://user-images.githubusercontent.com/79351899/220560123-5f680fec-3a4c-4f04-990f-707f78ec1e58.png)
![ADER_2](https://user-images.githubusercontent.com/79351899/220557400-dd26edd7-42a0-4e80-9dbf-721771a2cb14.png)

- **<span style='color:red'>AD</span>MMSLIMM + <span style='color:red'>E</span>ASE + <span style='color:red'>R</span>ecVAE** (자체 제작)
- **AutoEncoder** 기반의 모델들은 **Sparse한 데이터**를 학습할 때 좋은 성능을 검증
- **앙상블** 하여 영화를 최종 추천

<br>

## C. 모델 파이프라인

![모델 파이프라인](https://user-images.githubusercontent.com/79351899/220557363-f7163d90-bae0-4828-a975-7cf4ed6148e2.png)
- **배치 추천**
    - MovieLens 인터랙션과 **Real User Interaction**을 학습 데이터로 사용
    - **Airflow**를 통해 매일 추천 결과를 갱신
- **실시간 추천**
    - 유저의 성향과 테스트 결과를 바탕으로 학습된 모델을 통해 추천

