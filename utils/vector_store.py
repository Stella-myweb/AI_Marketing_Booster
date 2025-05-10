# utils/vector_store.py
import os
import streamlit as st
from typing import List, Optional

# 임포트 경로 수정
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.document_loaders import TextLoader

from config import OPENAI_API_KEY

class VectorStore:
    """벡터 스토어 클래스: 텍스트 데이터를 벡터화하고 검색 기능을 제공합니다."""
    
    def __init__(self):
        """벡터 스토어 초기화"""
        try:
            # API 키 확인
            if "OPENAI_API_KEY" in st.secrets:
                api_key = st.secrets["OPENAI_API_KEY"]
            else:
                api_key = OPENAI_API_KEY
                
            if not api_key:
                st.error("OpenAI API 키가 설정되지 않았습니다.")
                raise ValueError("API 키가 없습니다")
            
            # 임베딩 초기화
            self.embeddings = OpenAIEmbeddings(
                openai_api_key=api_key,
                model="text-embedding-ada-002"
            )
            
            # 데이터 디렉토리 경로 설정
            self.data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
            
            # 벡터 스토어 로드 또는 생성
            vectorstore_path = os.path.join(self.data_dir, "vectorstore")
            if os.path.exists(vectorstore_path):
                self.vectorstore = FAISS.load_local(vectorstore_path, self.embeddings)
            else:
                # 초기 데이터 로드 및 벡터 스토어 생성
                self._create_vectorstore()
        except Exception as e:
            st.error(f"벡터 스토어 초기화 오류: {e}")
            raise
    
    def _create_vectorstore(self):
        """초기 데이터를 로드하고 벡터 스토어를 생성합니다."""
        try:
            # 텍스트 데이터 파일 목록 가져오기
            content_dir = os.path.join(self.data_dir, "content")
            if not os.path.exists(content_dir):
                os.makedirs(content_dir, exist_ok=True)
                
            text_files = []
            for root, _, files in os.walk(content_dir):
                for file in files:
                    if file.endswith(".txt"):
                        text_files.append(os.path.join(root, file))
            
            # 이북 컨텐츠 파일 추가
            ebook_file = os.path.join(self.data_dir, "ebook_content.txt")
            if os.path.exists(ebook_file):
                text_files.append(ebook_file)
            
            if not text_files:
                # 기본 텍스트 파일 생성
                default_file = os.path.join(content_dir, "default_content.txt")
                with open(default_file, "w", encoding="utf-8") as f:
                    f.write("""
                    네이버 스마트 플레이스 최적화를 위한 기본 가이드:
                    
                    1. 정확한 기본 정보 입력하기
                    2. 매력적인 이미지 사용하기
                    3. 키워드 최적화하기
                    4. 고객 리뷰 관리하기
                    5. 정기적인 업데이트하기
                    """)
                text_files.append(default_file)
            
            # 문서 로드 및 분할
            documents = []
            for file_path in text_files:
                try:
                    loader = TextLoader(file_path, encoding="utf-8")
                    documents.extend(loader.load())
                except Exception as e:
                    st.warning(f"파일 로드 오류 ({file_path}): {e}")
            
            # 텍스트 분할 설정
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000, 
                chunk_overlap=200
            )
            
            # 문서 분할
            split_documents = text_splitter.split_documents(documents)
            
            # 벡터 스토어 생성
            self.vectorstore = FAISS.from_documents(split_documents, self.embeddings)
            
            # 벡터 스토어 저장
            vectorstore_path = os.path.join(self.data_dir, "vectorstore")
            self.vectorstore.save_local(vectorstore_path)
        except Exception as e:
            st.error(f"벡터 스토어 생성 오류: {e}")
            raise
    
    def get_relevant_content(self, query: str, n_results: int = 3) -> str:
        """
        쿼리와 관련된 콘텐츠를 검색합니다.
        
        Args:
            query: 검색 쿼리
            n_results: 반환할 검색 결과 수
            
        Returns:
            관련 콘텐츠를 포함한 문자열
        """
        try:
            # 벡터 스토어에서 유사한 문서 검색
            docs = self.vectorstore.similarity_search(query, k=n_results)
            
            # 검색 결과를 하나의 문자열로 결합
            context = "\n\n".join([doc.page_content for doc in docs])
            return context
        except Exception as e:
            st.error(f"콘텐츠 검색 오류: {e}")
            return "콘텐츠 검색 중 오류가 발생했습니다."
    
    def get_relevant_content_for_diagnosis(self, answers, weak_areas, n_results: int = 3) -> str:
        """
        진단 결과에 맞는 콘텐츠를 검색합니다.
        
        Args:
            answers: 사용자 응답
            weak_areas: 개선이 필요한 영역
            n_results: 반환할 검색 결과 수
            
        Returns:
            관련 콘텐츠를 포함한 문자열
        """
        try:
            # 약점 영역을 바탕으로 검색 쿼리 생성
            title_map = {
                "인식하게 한다": "검색 노출 최적화",
                "클릭하게 한다": "클릭율 높이는 전략",
                "머물게 한다": "체류시간 늘리는 방법", 
                "연락오게 한다": "문의/예약 전환율 높이기",
                "후속 피드백 받는다": "고객 재방문 유도 전략"
            }
            
            # 약점 영역별로 맞춤 쿼리 생성 및 검색
            all_contents = []
            
            # weak_areas가 빈 리스트이거나 None인 경우 처리
            if not weak_areas:
                return "개선 필요 영역이 확인되지 않았습니다."
            
            for area in weak_areas[:2]:  # 상위 2개 영역에 집중
                area_term = title_map.get(area, area)
                # 더 구체적인 쿼리 생성
                query = f"네이버 스마트 플레이스 {area_term} 최신 전략과 성공 사례"
                
                # 벡터 스토어에서 유사한 문서 검색
                docs = self.vectorstore.similarity_search(query, k=n_results)
                
                # 검색 결과를 리스트에 추가
                area_content = f"\n## {area_term} 관련 콘텐츠:\n"
                area_content += "\n\n".join([doc.page_content for doc in docs])
                all_contents.append(area_content)
            
            # 모든 영역의 콘텐츠를 하나의 문자열로 결합
            combined_content = "\n\n".join(all_contents)
            return combined_content
        except Exception as e:
            st.error(f"진단 콘텐츠 검색 오류: {e}")
            return f"콘텐츠 검색 중 오류가 발생했습니다: {str(e)}"
    
    def raw_similarity_search(self, query: str, k: int = 5):
        """
        쿼리와 유사한 원본 문서를 검색합니다.
        
        Args:
            query: 검색 쿼리
            k: 반환할 결과 수
            
        Returns:
            유사한 문서 객체 리스트
        """
        try:
            if not query:
                return []
                
            # 벡터 스토어에서 유사한 문서 검색
            docs = self.vectorstore.similarity_search(query, k=k)
            return docs
        except Exception as e:
            st.error(f"문서 검색 오류: {e}")
            # 오류 발생 시 빈 리스트 반환
            return [] 
