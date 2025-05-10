# utils/vector_store.py - 벡터 DB 관련 기능
# 형식: Python (.py)
# 역할: 전자책 데이터 처리, 텍스트 분할, 벡터화 및 저장 기능
import os
import re
import time
import sys
import streamlit as st
from pathlib import Path
from typing import List, Dict, Any, Optional

# pysqlite3 강제 로드 및 sqlite3 대체 시도
try:
    __import__('pysqlite3')
    sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')
except (ImportError, KeyError):
    st.warning("pysqlite3 로드 실패. sqlite3 버전이 낮을 수 있습니다.")

# chromadb 임포트 시도
try:
    import chromadb
    from chromadb.utils import embedding_functions
    CHROMADB_AVAILABLE = True
except Exception as e:
    st.warning(f"chromadb 임포트 실패: {e}. 벡터 검색 기능을 사용할 수 없습니다.")
    CHROMADB_AVAILABLE = False

# langchain 임포트 시도
try:
    from langchain.text_splitter import RecursiveCharacterTextSplitter
    from langchain_community.vectorstores import Chroma
    from langchain.schema.document import Document
    from langchain.embeddings.openai import OpenAIEmbeddings
    LANGCHAIN_AVAILABLE = True
except Exception as e:
    st.warning(f"langchain 임포트 실패: {e}. 벡터 검색 기능을 사용할 수 없습니다.")
    LANGCHAIN_AVAILABLE = False

# config.py에서 설정 로드
try:
    from config import OPENAI_API_KEY, DATA_DIR, EBOOK_PATH, DB_DIR, CHUNK_SIZE, CHUNK_OVERLAP, EMBEDDING_MODEL
except ImportError:
    # 기본값 설정
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
    EBOOK_PATH = os.path.join(DATA_DIR, "ebook_content.txt")
    DB_DIR = os.path.join(DATA_DIR, "chroma_db")
    CHUNK_SIZE = 1000
    CHUNK_OVERLAP = 200
    EMBEDDING_MODEL = "text-embedding-ada-002"

class VectorStore:
    """대체 벡터 스토어 클래스 - chromadb 오류 발생 시에도 기본 기능 제공"""
    
    def __init__(self, recreate_db: bool = False):
        """벡터 스토어 초기화"""
        self.is_functional = False
        self.db = None
        self.embedding = None
        
        # 기본 예제 콘텐츠
        self.default_content = {
            "검색 노출 최적화": """
            # 검색 노출 최적화 전략
            
            ## 키워드 최적화
            - 핵심 키워드를 상호명, 소개글, 메뉴명에 포함시키세요
            - 지역명과 업종명을 함께 사용하세요 (예: 강남 피부과, 홍대 카페)
            
            ## 카테고리 설정
            - 정확한 카테고리와 세부 카테고리를 선택하세요
            - 업종에 맞는 태그를 추가하세요
            
            ## 위치 정보
            - 정확한 주소와 위치를 등록하세요
            - 주변 랜드마크를 언급하면 도움이 됩니다
            """,
            
            "클릭율 높이는 전략": """
            # 클릭율 향상 방법
            
            ## 이미지 최적화
            - 고품질 매장 사진을 사용하세요
            - 대표 사진은 매력적이고 전문적으로 선택하세요
            
            ## 제목 작성
            - 핵심 키워드가 포함된 매력적인 제목을 사용하세요
            - 독특한 서비스나 제품을 강조하세요
            
            ## 캐치프레이즈
            - 간결하고 기억에 남는 문구를 사용하세요
            - 핵심 가치나 차별점을 표현하세요
            """,
            
            "체류시간 늘리는 방법": """
            # 체류시간 증가 전략
            
            ## 콘텐츠 품질
            - 상세한 메뉴/서비스 정보를 제공하세요
            - 가격 정보를 투명하게 공개하세요
            
            ## 업데이트 관리
            - 정기적으로 새로운 콘텐츠를 업데이트하세요
            - 시즌별 메뉴나 이벤트 정보를 추가하세요
            
            ## 미디어 활용
            - 다양한 매장 사진과 동영상을 추가하세요
            - 고객 후기나 사용 사례를 공유하세요
            """,
            
            "문의/예약 전환율 높이기": """
            # 전환율 향상 전략
            
            ## 예약 시스템
            - 간편한 예약 기능을 활성화하세요
            - 실시간 예약 상태를 표시하세요
            
            ## 연락 정보
            - 전화번호와 영업시간을 명확히 표시하세요
            - 문의에 빠르게 응답하세요
            
            ## 프로모션
            - 첫방문 할인이나 특별 혜택을 표시하세요
            - 쿠폰이나 포인트 적립 정보를 제공하세요
            """,
            
            "고객 재방문 유도 전략": """
            # 재방문 유도 방법
            
            ## 리뷰 관리
            - 고객 리뷰에 정기적으로 응답하세요
            - 부정적인 리뷰에도 친절하게 대응하세요
            
            ## 혜택 프로그램
            - 단골 고객 혜택 프로그램을 운영하세요
            - 재방문 시 추가 할인이나 특전을 제공하세요
            
            ## 알림 활용
            - 신메뉴, 이벤트 소식을 정기적으로 업데이트하세요
            - 고객이 '저장' 버튼을 누르도록 유도하세요
            """
        }
        
        # API 키 유효성 확인
        try:
            if "OPENAI_API_KEY" in st.secrets:
                api_key = st.secrets["OPENAI_API_KEY"]
            else:
                api_key = OPENAI_API_KEY
                
            if not api_key:
                st.warning("OpenAI API 키가 설정되지 않았습니다. 벡터 검색 기능이 제한됩니다.")
                return
                
            # chromadb와 langchain이 사용 가능한지 확인
            if not CHROMADB_AVAILABLE or not LANGCHAIN_AVAILABLE:
                st.warning("벡터 스토어 기능을 사용할 수 없습니다. 기본 기능만 제공됩니다.")
                return
                
            # OpenAI 임베딩 초기화 시도
            self.embedding = OpenAIEmbeddings(openai_api_key=api_key, model=EMBEDDING_MODEL)
            
            # ChromaDB 사용 시도 (실패 시 기본 기능만 제공)
            try:
                # DB 디렉토리 생성
                os.makedirs(DB_DIR, exist_ok=True)
                
                # 인메모리 벡터 스토어 사용
                # 파일 시스템 DB는 SQLite 버전 문제로 사용하지 않음
                self.db = Chroma(
                    collection_name="ebook_chunks",
                    embedding_function=self.embedding,
                    persist_directory=None  # 인메모리 모드
                )
                
                # 기본 문서 생성 및 추가
                if len(self.db.get()["documents"] or []) == 0:
                    docs = self._create_default_docs()
                    if docs:
                        self.db.add_documents(docs)
                
                self.is_functional = True
            except Exception as e:
                st.warning(f"벡터 스토어 초기화 오류: {e}. 기본 기능만 제공됩니다.")
        except Exception as e:
            st.error(f"VectorStore 초기화 중 오류 발생: {e}")

    def _create_default_docs(self) -> List[Document]:
        """기본 문서 생성"""
        docs = []
        for topic, content in self.default_content.items():
            docs.append(Document(
                page_content=content,
                metadata={"topic": topic, "source": "default"}
            ))
        return docs
            
    def search(self, query: str, n_results: int = 3) -> List[Document]:
        """검색 기능"""
        if not self.is_functional or not self.db:
            # 검색어와 관련된 기본 콘텐츠 반환
            return self._get_default_results(query)
            
        try:
            results = self.db.similarity_search(query, k=n_results)
            return results
        except Exception as e:
            st.warning(f"검색 오류: {e}. 기본 결과를 제공합니다.")
            return self._get_default_results(query)
    
    def _get_default_results(self, query: str) -> List[Document]:
        """검색어와 관련된 기본 문서 반환"""
        # 간단한 키워드 매칭으로 관련 결과 찾기
        results = []
        query_terms = query.lower().split()
        
        # 각 기본 콘텐츠에 대해 관련성 점수 계산
        scores = {}
        for topic, content in self.default_content.items():
            score = 0
            content_lower = content.lower()
            for term in query_terms:
                if term in content_lower:
                    score += content_lower.count(term)
                if term in topic.lower():
                    score += 10  # 제목에 있으면 더 높은 점수
            scores[topic] = score
        
        # 점수 기준으로 정렬
        sorted_topics = sorted(scores.keys(), key=lambda x: scores[x], reverse=True)
        
        # 관련된 문서 반환
        for topic in sorted_topics[:3]:  # 최대 3개 반환
            if scores[topic] > 0:  # 관련성이 있는 경우만
                results.append(Document(
                    page_content=self.default_content[topic],
                    metadata={"topic": topic, "source": "default", "score": scores[topic]}
                ))
        
        # 관련 결과가 없으면 기본 정보 제공
        if not results:
            results.append(Document(
                page_content="네이버 스마트 플레이스 최적화에 관한 기본 정보입니다.",
                metadata={"topic": "기본 정보", "source": "default"}
            ))
            
        return results
    
    def get_relevant_content(self, query: str, n_results: int = 3) -> str:
        """관련 콘텐츠 검색"""
        try:
            results = self.search(query, n_results=n_results)
            
            if not results:
                return "관련 정보를 찾을 수 없습니다."
            
            combined_content = "\n\n".join([doc.page_content for doc in results])
            return combined_content
        except Exception as e:
            st.warning(f"관련 콘텐츠 검색 오류: {e}. 기본 정보를 제공합니다.")
            return """
            네이버 스마트 플레이스 최적화를 위한 기본 정보:
            
            1. 정확한 카테고리와 키워드를 설정하세요.
            2. 고품질 이미지와 매력적인 제목을 사용하세요.
            3. 주기적으로 콘텐츠를 업데이트하고 고객 리뷰를 관리하세요.
            4. 간편한 예약 시스템과 빠른 응답으로 고객 만족도를 높이세요.
            5. 방문 혜택과 단골 고객 프로그램으로 재방문을 유도하세요.
            """
    
    def get_relevant_content_for_diagnosis(self, answers: Dict[str, str], weak_areas: List[str], n_results: int = 3) -> str:
        """진단 결과에 관련된 콘텐츠 검색"""
        # 약점 영역 영어 이름을 한글로 변환
        area_translation = {
            "인식하게 한다": "검색 노출 최적화",
            "클릭하게 한다": "클릭율 높이는 전략",
            "머물게 한다": "체류시간 늘리는 방법",
            "연락오게 한다": "문의/예약 전환율 높이기",
            "후속 피드백 받는다": "고객 재방문 유도 전략"
        }
        
        # 약점 영역 관련 콘텐츠 결합
        combined_content = ""
        
        for area in weak_areas:
            translated_area = area_translation.get(area, area)
            if translated_area in self.default_content:
                combined_content += f"\n\n{self.default_content[translated_area]}"
            else:
                # 검색 시도
                query = f"네이버 스마트 플레이스 {translated_area} 방법"
                area_content = self.get_relevant_content(query, n_results=1)
                combined_content += f"\n\n{area_content}"
        
        # 결과가 없으면 기본 정보 제공
        if not combined_content.strip():
            return """
            네이버 스마트 플레이스 최적화를 위한 기본 정보:
            
            1. 검색 노출 최적화: 정확한 카테고리 선택과 핵심 키워드 포함
            2. 클릭율 향상: 고품질 이미지와 매력적인 제목 사용
            3. 체류시간 증가: 상세한 정보 제공과 정기적 콘텐츠 업데이트
            4. 전환율 향상: 간편한 예약 시스템과 명확한 연락 정보
            5. 재방문 유도: 리뷰 관리와 단골 고객 혜택 프로그램
            """
            
        return combined_content

# 테스트 코드
if __name__ == "__main__":
    try:
        vector_store = VectorStore()
        query = "네이버 스마트 플레이스 키워드 최적화"
        results = vector_store.search(query, n_results=2)
        
        print(f"\n검색 결과: {query}")
        for i, doc in enumerate(results, 1):
            print(f"\n--- 결과 {i} ---")
            print(doc.page_content[:200] + "...")
    except Exception as e:
        print(f"테스트 오류: {e}") 