# Web

## A. 웹서비스 아키텍처
<p align="center"><img src="https://user-images.githubusercontent.com/71438046/217651274-8669b85b-2e8c-48ab-8e31-fa3b7d2c276f.png" /><br><br></p>

## B. 구글 애널리틱스
![구글 에널리틱스](https://user-images.githubusercontent.com/79351899/220563204-550c1380-6b34-436a-944d-0bc2a9989ecc.png)
- **Django**를 통해 구현, **NginX**와 **Gunicorn**을 통한 배포
- **구글 애널리틱스** 연결 - 유저 데이터 분석

<br>

## C. 웹 배포 자동화

![Untitled (3)](https://user-images.githubusercontent.com/79351899/220563826-47ce6ab5-fa93-424a-96dd-0b53ee9c5e49.png)

- **GitHub Actions** 시용
- master 브랜치에 push 또는 pull request 이벤트가 발생하면, 변경사항을 GCP 서버에 배포하고, 배포 성공여부를 slack에 알림
