# utils/rag_model.py - RAG 모델 구현
# 형식: Python (.py)
# 역할: OpenAI API를 사용한 임베딩 및 응답 생성 기능
import os
import re
import time
from pathlib import Path
from typing import List, Dict, Any, Optional

import chromadb
from chromadb.utils import embedding_functions

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import Chroma
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
        self.embedding = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY, model=EMBEDDING_MODEL)
        self.db_path = DB_DIR
        self.ebook_path = EBOOK_PATH
        
        # DB 디렉토리 생성
        os.makedirs(self.db_path, exist_ok=True)
        
        if recreate_db or not os.path.exists(os.path.join(self.db_path, "chroma.sqlite3")):
            print("벡터 데이터베이스를 새로 생성합니다...")
            self._create_vector_store()
        else:
            print("기존 벡터 데이터베이스를 로드합니다...")
            self.db = Chroma(
                persist_directory=self.db_path,
                embedding_function=self.embedding
            )
            print(f"데이터베이스 로드 완료. 총 {self.db._collection.count()} 개의 문서 조각이 있습니다.")

    def _create_vector_store(self):
        """전자책 콘텐츠를 로드하고 벡터 스토어를 생성합니다."""
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
    
    def _load_ebook(self) -> str:
        """전자책 텍스트 파일을 로드합니다."""
        try:
            with open(self.ebook_path, 'r', encoding='utf-8') as f:
                content = f.read()
            print(f"전자책 콘텐츠 로드 완료. 총 {len(content)} 자의 텍스트가 로드되었습니다.")
            return content
        except Exception as e:
            print(f"전자책 로드 중 오류 발생: {e}")
            raise
    
    def _split_text(self, text: str) -> List[Document]:
        """텍스트를 청크로 분할합니다."""
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
    
    def _preprocess_text(self, text: str) -> str:
        """텍스트를 전처리합니다."""
        # 연속된 빈 줄 제거
        text = re.sub(r'\n{3,}', '\n\n', text)
        
        # 페이지 번호 등 불필요한 텍스트 제거
        text = re.sub(r'\n\s*\d+\s*\n', '\n', text)
        
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
        results = self.db.similarity_search(query, k=n_results)
        return results
    
    def search_with_score(self, query: str, n_results: int = 5) -> List[tuple]:
        """
        쿼리와 관련된 문서를 유사도 점수와 함께 검색합니다.
        
        Args:
            query: 검색 쿼리
            n_results: 반환할 결과 개수
            
        Returns:
            (문서, 유사도 점수) 튜플 목록
        """
        results = self.db.similarity_search_with_score(query, k=n_results)
        return results
    
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
        # 메타데이터 필터 설정
        filter_dict = {"section": {"$contains": category}}
        
        results = self.db.similarity_search(
            query, 
            k=n_results,
            filter=filter_dict
        )
        return results
    
    def get_relevant_content(self, query: str, n_results: int = 5) -> str:
        """
        쿼리와 관련된 문서들의 내용을 하나의 문자열로 결합합니다.
        
        Args:
            query: 검색 쿼리
            n_results: 사용할 결과 개수
            
        Returns:
            관련 문서들의 내용을 결합한 문자열
        """
        results = self.search(query, n_results=n_results)
        
        if not results:
            return "관련 정보를 찾을 수 없습니다."
        
        combined_content = "\n\n".join([doc.page_content for doc in results])
        return combined_content
    
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
        # 약점 영역 영어 이름을 한글로 변환
        area_translation = {
            "인식하게 한다": "키워드 최적화 상호명 업종 설정",
            "클릭하게 한다": "대표 이미지 최적화 시각적 매력",
            "머물게 한다": "콘텐츠 품질 체류시간 증가",
            "연락오게 한다": "전환율 향상 예약 전화",
            "후속 피드백 받는다": "리뷰 관리 단골 고객"
        }
        
        all_results = []
        
        # 각 약점 영역에 대해 관련 콘텐츠 검색
        for area in weak_areas:
            search_query = area_translation.get(area, area)
            area_results = self.search(search_query, n_results=n_results)
            all_results.extend(area_results)
        
        # 중복 제거
        unique_contents = {}
        for doc in all_results:
            content_hash = hash(doc.page_content)
            if content_hash not in unique_contents:
                unique_contents[content_hash] = doc
        
        # 결합
        if not unique_contents:
            return "자가진단 결과에 관련된 정보를 찾을 수 없습니다."
        
        combined_content = "\n\n".join([doc.page_content for doc in unique_contents.values()])
        return combined_content

# 테스트 코드
if __name__ == "__main__":
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