# config.py - 설정 파일
# 형식: Python (.py)
# 역할: API 키, 파일 경로 등 설정 정보 관리
import os
from dotenv import load_dotenv

# .env 파일에서 환경 변수 로드
load_dotenv()

# OpenAI API 키 설정
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# 파일 경로 설정
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(PROJECT_ROOT, "data")
EBOOK_PATH = os.path.join(DATA_DIR, "ebook_content.txt")
DB_DIR = os.path.join(PROJECT_ROOT, "db")

# 앱 설정
APP_TITLE = "사장님 AI 마케팅 부스터"
APP_DESCRIPTION = "네이버 스마트 플레이스 최적화를 위한 AI 기반 자가 진단 및 개선 전략 제공 서비스"

# RAG 모델 설정
CHUNK_SIZE = 500
CHUNK_OVERLAP = 50
EMBEDDING_MODEL = "text-embedding-3-small"
# LLM 모델 설정 (최신 gpt-4o-mini-2024-07-18 사용)
LLM_MODEL = "gpt-4o-mini-2024-07-18"  # 기존 "gpt-4o"에서 변경
TEMPERATURE = 0.2

# PDF 설정
COMPANY_NAME = "스마트 플레이스 최적화 컨설팅"
REPORT_TITLE = "스마트 플레이스 최적화 진단 보고서"
LOGO_PATH = os.path.join(PROJECT_ROOT, "assets", "logo.png") 