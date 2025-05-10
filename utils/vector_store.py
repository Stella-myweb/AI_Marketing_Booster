# utils/vector_store.py - 벡터 DB 관련 기능
# 형식: Python (.py)
# 역할: 전자책 데이터 처리, 텍스트 분할, 벡터화 및 저장 기능
import os
import re
import time
import streamlit as st  # st.warning과 st.error를 사용하기 위해 추가
from pathlib import Path
from typing import List, Dict, Any, Optional

import chromadb
from chromadb.utils import embedding_functions

from langchain.text_splitter import RecursiveCharacterTextSplitter

from langchain_community.vectorstores import Chroma
from langchain.schema.document import Document
from langchain.embeddings.openai import OpenAIEmbeddings

# config.py에서 설정 로드
from config import OPENAI_API_KEY, DATA_DIR, EBOOK_PATH, DB_DIR, CHUNK_SIZE, CHUNK_OVERLAP, EMBEDDING_MODEL

class VectorStore:
    """
    전자책 내용을 벡터화하고 검색할 수 있는 벡터 스토어 클래스
    """
    
    def __init__(self, recreate_db: bool = False):
        """
        벡터 스토어 객체를 초기화합니다.
        
        Args:
            recreate_db: 기존 DB를 재생성할지 여부
        """
        try:
            # API 키 확인
            if "OPENAI_API_KEY" in st.secrets:
                api_key = st.secrets["OPENAI_API_KEY"]
            else:
                api_key = OPENAI_API_KEY
                
            if not api_key:
                st.error("OpenAI API 키가 설정되지 않았습니다.")
                raise ValueError("API 키가 없습니다")
                
            self.embedding = OpenAIEmbeddings(openai_api_key=api_key, model=EMBEDDING_MODEL)
            self.db_path = DB_DIR
            self.ebook_path = EBOOK_PATH
            
            # DB 디렉토리 생성
            os.makedirs(self.db_path, exist_ok=True)
            
            if recreate_db or not os.path.exists(os.path.join(self.db_path, "chroma.sqlite3")):
                print("벡터 데이터베이스를 새로 생성합니다...")
                self._create_vector_store()
            else:
                print("기존 벡터 데이터베이스를 로드합니다...")
                try:
                    self.db = Chroma(
                        persist_directory=self.db_path,
                        embedding_function=self.embedding
                    )
                    print(f"데이터베이스 로드 완료. 총 {self.db._collection.count()} 개의 문서 조각이 있습니다.")
                except Exception as db_error:
                    st.warning(f"DB 로드 중 오류 발생: {db_error}. 새로운 임시 DB를 생성합니다.")
                    # 메모리에만 존재하는 임시 DB 생성
                    ebook_content = self._load_ebook()
                    chunks = self._split_text(ebook_content)
                    self.db = Chroma.from_documents(
                        documents=chunks,
                        embedding=self.embedding,
                        persist_directory=None  # 인메모리 DB
                    )
        except Exception as e:
            st.error(f"VectorStore 초기화 오류: {e}")
            # 기본 DB 초기화 (fallback)
            self.db = None
            self.embedding = None

    def _create_vector_store(self):
        """전자책 콘텐츠를 로드하고 벡터 스토어를 생성합니다."""
        try:
            # 전자책 콘텐츠 로드
            ebook_content = self._load_ebook()
            
            # 문서 분할
            chunks = self._split_text(ebook_content)
            
            # 벡터 스토어 생성
            self.db = Chroma.from_documents(
                documents=chunks,
                embedding=self.embedding,
                persist_directory=self.db_path
            )
            
            # 영구 저장
            self.db.persist()
            print(f"벡터 데이터베이스 생성 완료. 총 {len(chunks)} 개의 문서 조각이 생성되었습니다.")
        except Exception as e:
            st.error(f"벡터 스토어 생성 오류: {e}")
            raise
    
    def _load_ebook(self) -> str:
        """전자책 콘텐츠를 로드합니다."""
        try:
            # 절대 경로 사용
            if os.path.exists(self.ebook_path):
                with open(self.ebook_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                return content
            else:
                st.warning(f"파일을 찾을 수 없습니다: {self.ebook_path}")
                # 대체 데이터 반환
                return """
                # 네이버 스마트 플레이스 최적화 가이드
                
                ## 검색 노출 최적화
                정확한 카테고리 선택과 핵심 키워드를 포함한 상세한 비즈니스 설명이 중요합니다.
                
                ## 클릭율 높이는 전략
                고품질 이미지와 매력적인 제목으로 첫인상을 개선하세요.
                
                ## 체류시간 늘리는 방법
                정기적인 콘텐츠 업데이트와 다양한 메뉴/서비스 정보를 제공하세요.
                
                ## 문의/예약 전환율 높이기
                간편한 예약 시스템과 빠른 응답으로 고객 만족도를 높이세요.
                
                ## 고객 재방문 유도 전략
                긍정적인 리뷰 관리와 프로모션을 활용해 재방문을 유도하세요.
                """
        except Exception as e:
            st.error(f"전자책 로드 오류: {e}")
            # 기본 데이터 반환
            return "네이버 스마트 플레이스 최적화를 위한 기본 정보입니다."
    
    def _split_text(self, text: str) -> List[Document]:
        """텍스트를 청크로 분할합니다."""
        try:
            # 분할 단위로 챕터, 섹션, 문단 경계 등을 설정
            splitter = RecursiveCharacterTextSplitter(
                separators=["\n\n# ", "\n## ", "\n### ", "\n\n", "\n", ".", "!", "?", ",", " ", ""],
                chunk_size=CHUNK_SIZE,
                chunk_overlap=CHUNK_OVERLAP,
                length_function=len
            )
            
            # 텍스트를 적절히 정제
            cleaned_text = self._preprocess_text(text)
            
            # 문서 분할
            raw_chunks = splitter.split_text(cleaned_text)
            
            # Document 객체로 변환
            chunks = []
            for i, chunk in enumerate(raw_chunks):
                # 너무 짧은 청크는 건너뜀
                if len(chunk) < 50:
                    continue
                    
                # 문서 메타데이터 추가
                metadata = {
                    "chunk_id": i,
                    "source": "ebook_content.txt",
                    "chunk_length": len(chunk)
                }
                
                # 섹션/챕터 정보 추가
                section_match = re.search(r"^(#+ .+?)(?=\n|$)", chunk)
                if section_match:
                    metadata["section"] = section_match.group(1).strip()
                
                chunks.append(Document(page_content=chunk, metadata=metadata))
            
            print(f"텍스트 분할 완료. 총 {len(chunks)} 개의 청크가 생성되었습니다.")
            return chunks
        except Exception as e:
            st.error(f"텍스트 분할 오류: {e}")
            # 기본 청크 반환
            return [Document(page_content="네이버 스마트 플레이스 최적화 정보", metadata={"source": "fallback"})]
    
    def _preprocess_text(self, text: str) -> str:
        """텍스트를 전처리합니다."""
        try:
            # 연속된 빈 줄 제거
            text = re.sub(r'\n{3,}', '\n\n', text)
            
            # 페이지 번호 등 불필요한 텍스트 제거
            text = re.sub(r'\n\s*\d+\s*\n', '\n', text)
            
            return text
        except Exception as e:
            st.warning(f"텍스트 전처리 오류 (원본 반환): {e}")
            return text
    
    def search(self, query: str, n_results: int = 5) -> List[Document]:
        """
        쿼리와 관련된 문서를 검색합니다.
        
        Args:
            query: 검색 쿼리
            n_results: 반환할 결과 개수
            
        Returns:
            관련 문서 목록
        """
        try:
            if self.db is None:
                return [Document(page_content="검색 기능을 사용할 수 없습니다.", metadata={"error": "db_not_initialized"})]
                
            results = self.db.similarity_search(query, k=n_results)
            return results
        except Exception as e:
            st.error(f"검색 오류: {e}")
            return [Document(page_content=f"검색 중 오류가 발생했습니다: {e}", metadata={"error": "search_error"})]
    
    def search_with_score(self, query: str, n_results: int = 5) -> List[tuple]:
        """
        쿼리와 관련된 문서를 유사도 점수와 함께 검색합니다.
        
        Args:
            query: 검색 쿼리
            n_results: 반환할 결과 개수
            
        Returns:
            (문서, 유사도 점수) 튜플 목록
        """
        try:
            if self.db is None:
                doc = Document(page_content="검색 기능을 사용할 수 없습니다.", metadata={"error": "db_not_initialized"})
                return [(doc, 0.0)]
                
            results = self.db.similarity_search_with_score(query, k=n_results)
            return results
        except Exception as e:
            st.error(f"점수 검색 오류: {e}")
            doc = Document(page_content=f"검색 중 오류가 발생했습니다: {e}", metadata={"error": "search_error"})
            return [(doc, 0.0)]
    
    def search_by_category(self, query: str, category: str, n_results: int = 5) -> List[Document]:
        """
        특정 카테고리 내에서 쿼리와 관련된 문서를 검색합니다.
        
        Args:
            query: 검색 쿼리
            category: 검색할 카테고리 (메타데이터의 section 필드)
            n_results: 반환할 결과 개수
            
        Returns:
            관련 문서 목록
        """
        try:
            if self.db is None:
                return [Document(page_content="검색 기능을 사용할 수 없습니다.", metadata={"error": "db_not_initialized"})]
                
            # 메타데이터 필터 설정
            filter_dict = {"section": {"$contains": category}}
            
            results = self.db.similarity_search(
                query, 
                k=n_results,
                filter=filter_dict
            )
            return results
        except Exception as e:
            st.error(f"카테고리 검색 오류: {e}")
            return [Document(page_content=f"카테고리 검색 중 오류가 발생했습니다: {e}", metadata={"error": "search_error"})]
    
    def get_relevant_content(self, query: str, n_results: int = 5) -> str:
        """
        쿼리와 관련된 문서들의 내용을 하나의 문자열로 결합합니다.
        
        Args:
            query: 검색 쿼리
            n_results: 사용할 결과 개수
            
        Returns:
            관련 문서들의 내용을 결합한 문자열
        """
        try:
            results = self.search(query, n_results=n_results)
            
            if not results:
                return "관련 정보를 찾을 수 없습니다."
            
            # 에러 검사
            if len(results) == 1 and "error" in results[0].metadata:
                return """
                네이버 스마트 플레이스 최적화를 위한 일반적인 팁:
                
                1. 매력적인 대표 이미지를 업로드하세요: 첫인상은 클릭율에 큰 영향을 미칩니다.
                2. 핵심 키워드를 적절히 포함시키세요: 검색 노출에 중요합니다.
                3. 상세한 비즈니스 설명을 작성하세요: 고객이 서비스를 이해하는 데 도움이 됩니다.
                4. 리뷰를 적극적으로 관리하세요: 긍정적인 리뷰는 신뢰도를 높입니다.
                5. 정기적으로 콘텐츠를 업데이트하세요: 최신 정보는 검색 순위에 영향을 줍니다.
                """
            
            combined_content = "\n\n".join([doc.page_content for doc in results])
            return combined_content
        except Exception as e:
            st.error(f"관련 콘텐츠 검색 오류: {e}")
            return """
            네이버 스마트 플레이스 최적화를 위한 기본 정보:
            
            - 매력적인 이미지 사용하기
            - 정확한 카테고리 선택하기
            - 핵심 키워드 포함하기
            - 상세한 비즈니스 설명 제공하기
            - 리뷰 관리하기
            """
    
    def get_relevant_content_for_diagnosis(self, answers: Dict[str, str], weak_areas: List[str], n_results: int = 3) -> str:
        """
        자가진단 결과에 기반하여 관련 콘텐츠를 검색합니다.
        
        Args:
            answers: 질문 ID를 키로, 선택한 옵션(A-E)을 값으로 하는 딕셔너리
            weak_areas: 개선이 필요한 영역 목록
            n_results: 각 영역별로 검색할 결과 개수
            
        Returns:
            관련 문서들의 내용을 결합한 문자열
        """
        try:
            # 약점 영역 영어 이름을 한글로 변환
            area_translation = {
                "인식하게 한다": "키워드 최적화 상호명 업종 설정",
                "클릭하게 한다": "대표 이미지 최적화 시각적 매력",
                "머물게 한다": "콘텐츠 품질 체류시간 증가",
                "연락오게 한다": "전환율 향상 예약 전화",
                "후속 피드백 받는다": "리뷰 관리 단골 고객"
            }
            
            if self.db is None:
                # 기본 콘텐츠 반환
                return """
                네이버 스마트 플레이스 최적화를 위한 일반적인 정보입니다:
                
                검색 노출 최적화: 정확한 카테고리와 키워드 설정이 중요합니다.
                클릭율 높이기: 고품질 이미지와 매력적인 제목을 사용하세요.
                체류시간 늘리기: 상세한 정보와 콘텐츠를 자주 업데이트하세요.
                전환율 높이기: 예약 시스템을 간편하게 하고 연락처를 명확히 표시하세요.
                재방문 유도: 리뷰에 적극 응대하고 프로모션을 활용하세요.
                """
            
            all_results = []
            
            # 각 약점 영역에 대해 관련 콘텐츠 검색
            for area in weak_areas:
                search_query = area_translation.get(area, area)
                area_results = self.search(search_query, n_results=n_results)
                all_results.extend(area_results)
            
            # 중복 제거
            unique_contents = {}
            for doc in all_results:
                # 오류 검증
                if "error" in doc.metadata:
                    continue
                    
                content_hash = hash(doc.page_content)
                if content_hash not in unique_contents:
                    unique_contents[content_hash] = doc
            
            # 결합
            if not unique_contents:
                return """
                자가진단 결과에 따른 개선이 필요한 영역:
                
                - 매력적인 이미지 사용으로 클릭율 높이기
                - 핵심 키워드를 활용한 검색 노출 최적화
                - 고객 리뷰 관리와 빠른 응답으로 신뢰도 구축
                - 주기적인 콘텐츠 업데이트로 검색 순위 향상
                - 간편한 예약 시스템으로 전환율 개선
                """
            
            combined_content = "\n\n".join([doc.page_content for doc in unique_contents.values()])
            return combined_content
        except Exception as e:
            st.error(f"진단 관련 콘텐츠 검색 오류: {e}")
            return """
            네이버 스마트 플레이스 최적화를 위한 주요 전략:
            
            1. 매력적인 이미지와 상세한 정보로 고객의 관심을 끌어보세요.
            2. 자주 검색되는 키워드를 포함하여 검색 노출을 높이세요.
            3. 리뷰에 빠르게 응답하고 부정적인 리뷰도 적절히 관리하세요.
            4. 정기적으로 콘텐츠를 업데이트하여 플레이스를 활성화하세요.
            5. 예약과 문의가 쉽도록 연락처와 버튼을 명확히 표시하세요.
            """

# 테스트 코드
if __name__ == "__main__":
    try:
        # 벡터 스토어 초기화
        vector_store = VectorStore(recreate_db=True)
        
        # 검색 테스트
        test_query = "네이버 플레이스 키워드 최적화 방법"
        results = vector_store.search(test_query, n_results=3)
        
        print("\n검색 결과:")
        for i, doc in enumerate(results, 1):
            print(f"\n--- 결과 {i} ---")
            print(f"내용 일부: {doc.page_content[:200]}...")
            print(f"메타데이터: {doc.metadata}")
    except Exception as e:
        print(f"테스트 실행 중 오류 발생: {e}")