# Instagram Content Analyzer (인스타그램 컨텐츠 분석기)

인스타그램 포스트의 내용을 분석하여 주요 키워드, 내용 요약, 감정 분석, 컨텐츠 일치성을 제공하는 웹 애플리케이션입니다.

## 주요 기능

- 인스타그램 포스트 URL을 입력하여 컨텐츠 분석
- 실시간 분석 프로세스 로그 표시
- 주요 키워드 추출
- 내용 요약 생성
- 감정 분석
- 컨텐츠 일치성 분석
- 이미지/비디오 분석

## 기술 스택

- Frontend: HTML, CSS, JavaScript
- Backend: Python, Flask
- AI/ML: OpenAI GPT-3.5
- 웹 스크래핑: Selenium
- 스타일링: Bootstrap 5

## 설치 방법

1. 저장소 클론:
```bash
git clone https://github.com/hyunilhlee/insta_analysis.git
cd insta_analysis
```

2. 가상환경 생성 및 활성화:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate  # Windows
```

3. 의존성 설치:
```bash
pip install -r requirements.txt
```

4. 환경 변수 설정:
- `.env` 파일 생성
- OpenAI API 키 추가: `OPENAI_API_KEY=your_api_key_here`

5. 애플리케이션 실행:
```bash
python app.py
```

## 사용 방법

1. 웹 브라우저에서 `http://localhost:5000` 접속
2. 분석하고자 하는 인스타그램 포스트 URL 입력
3. "분석하기" 버튼 클릭
4. 분석 결과 확인

## 기여 방법

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 라이선스

MIT License

## 연락처

- GitHub: [@hyunilhlee](https://github.com/hyunilhlee)
