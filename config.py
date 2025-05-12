# config.py - 설정 파일
# 형식: Python (.py)
# 역할: API 키, 파일 경로 등 설정 정보 관리
import os

# .env 파일이 있을 때만 로드 시도 (로컬 환경용)
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# API 키 설정
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# LLM 모델 설정 - 환경변수에서 가져오거나 기본값 설정
LLM_MODEL = os.getenv("LLM_MODEL", "gpt-4o-mini")

# 온도 설정 - 환경변수에서 가져오거나 기본값 설정
TEMPERATURE = float(os.getenv("TEMPERATURE", "0.7"))

# 경로 설정 - 상대 경로에서 절대 경로로 변경
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(PROJECT_ROOT, "data")
EBOOK_PATH = os.path.join(DATA_DIR, "ebook_content.txt")

# 앱 설정
APP_TITLE = "AI 마케팅 부스터"
APP_DESCRIPTION = "마케팅 효과를 AI로 진단하고 개선하는 도구"

# PDF 보고서용 추가 설정
REPORT_TITLE = "네이버 스마트 플레이스 최적화 진단 보고서"
COMPANY_NAME = "스마트 플레이스 최적화 컨설팅"
LOGO_PATH = os.path.join(PROJECT_ROOT, "assets", "logo.png")  # 실제 로고 경로에 맞게 수정 