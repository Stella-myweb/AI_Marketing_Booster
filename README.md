# README.md - 프로젝트 설명서
# 형식: 마크다운 (.md)
# 역할: 프로젝트 개요, 설치 방법, 사용법 등 문서화

사장님 AI 마케팅 부스터 (Smart Place AI Marketing Booster)
프로젝트 개요
네이버 스마트 플레이스 최적화를 위한 자가진단 및 맞춤형 개선 전략 제공 서비스입니다. RAG(Retrieval-Augmented Generation) 기술을 활용하여 사용자의 현재 스마트 플레이스 상태를 진단하고, 전문적인 개선 방안을 제시합니다.
주요 기능

자가진단 테스트: 20개 질문으로 스마트 플레이스 최적화 상태 진단
종합 분석 보고서: 강점, 개선점, 액션 플랜을 포함한 맞춤형 분석
PDF 보고서 다운로드: 상세한 진단 결과와 개선 전략을 PDF로 제공
RAG 기반 전문 지식: 전자책 자료를 바탕으로 전문적인 개선 전략 제안

기술 스택

Python: 애플리케이션의 기본 프로그래밍 언어
Streamlit: 웹 인터페이스 구현
LangChain: 대규모 언어 모델(LLM) 활용 프레임워크
OpenAI API: 자연어 처리 및 콘텐츠 생성
ChromaDB: 벡터 데이터베이스 구현
ReportLab: PDF 보고서 생성

설치 방법
bash# 저장소 클론
git clone https://github.com/yourusername/AI-Marketing-Booster.git
cd AI-Marketing-Booster

# 필요한 라이브러리 설치
pip install -r requirements.txt

# OpenAI API 키 설정
# .env 파일을 생성하고 API 키 추가
# OPENAI_API_KEY=your_api_key_here
실행 방법
bash# Streamlit 앱 실행
streamlit run app.py
프로젝트 구조
AI_Marketing_Booster/
├── app.py                 # 메인 Streamlit 앱
├── config.py              # 설정 파일
├── requirements.txt       # 필요한 라이브러리 목록
├── README.md              # 프로젝트 설명서
├── data/
│   └── ebook_content.txt  # 전자책 콘텐츠
├── utils/
│   ├── questions.py       # 자가진단 질문 모듈
│   ├── vector_store.py    # 벡터 DB 관리 모듈
│   ├── rag_model.py       # RAG 모델 구현
│   └── pdf_generator.py   # PDF 보고서 생성 모듈
└── reports/               # 생성된 보고서 저장 디렉토리
자가진단 영역

인식하게 한다: 키워드 설정, 상세 설명, 위치 정보 등 기본 정보 최적화
클릭하게 한다: 이미지 품질, 차별점 표현, 캐치프레이즈 등 흥미 유발 요소
머물게 한다: 콘텐츠 품질, 업데이트 주기, 이벤트 활용 등 체류시간 증가 요소
연락오게 한다: 예약 기능, 전화 응대, 쿠폰, 전환 유도 문구 등 전환율 향상 요소
후속 피드백 받는다: 리뷰 관리, 저장/알림 유도, 단골 고객 관리 등 재방문 유도 요소

라이선스
이 프로젝트는 MIT 라이선스 하에 배포됩니다. 자세한 내용은 LICENSE 파일을 참조하세요.
