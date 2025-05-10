# utils/rag_core.py
import os
import streamlit as st
from typing import Dict, List, Any

# 수정된 임포트 경로 사용
from langchain_openai import ChatOpenAI

# 자체 모듈 임포트
from utils.vector_store import VectorStore
from utils.questions import suggest_improvements
from utils.rag_generator import ResponseGenerator
from utils.rag_diagnosis import DiagnosisReportGenerator

# 설정 로드
from config import OPENAI_API_KEY, LLM_MODEL, TEMPERATURE

class RAGModel:
    """
    Retrieval-Augmented Generation 모델 클래스
    이북 데이터에서 검색된 정보를 활용하여 실용적인 인사이트와 전략을 제공합니다.
    """
    
    def __init__(self):
        """RAG 모델 초기화"""
        try:
            # API 키 확인
            if "OPENAI_API_KEY" in st.secrets:
                api_key = st.secrets["OPENAI_API_KEY"]
            else:
                api_key = OPENAI_API_KEY
                
            if not api_key:
                st.error("OpenAI API 키가 설정되지 않았습니다.")
                raise ValueError("API 키가 없습니다")
                
            # 벡터 스토어 초기화 시도
            try:
                self.vector_store = VectorStore()
            except Exception as e:
                st.warning(f"벡터 스토어 초기화 오류: {e}. 이북 데이터를 활용한 일부 기능이 제한될 수 있습니다.")
                self.vector_store = None
                
            # LLM 초기화 - 더 창의적인 응답을 위해 temperature 약간 상향
            self.llm = ChatOpenAI(
                openai_api_key=api_key,
                model_name=LLM_MODEL,
                temperature=0.7  # 기존보다 약간 높게 설정하여 더 다양한 인사이트 생성
            )
            
            # 서브모듈 초기화
            self.response_generator = ResponseGenerator(self.llm, self.vector_store)
            self.diagnosis_generator = DiagnosisReportGenerator(self.llm, self.vector_store)
            
        except Exception as e:
            st.error(f"RAG 모델 초기화 오류: {e}")
            self.llm = None
            self.vector_store = None
    
    def generate_response(self, query: str, context: str = None, n_results: int = 3) -> str:
        """
        쿼리에 대한 응답을 생성합니다.
        이북 데이터를 활용하여 실용적이고 차별화된 인사이트를 제공합니다.
        """
        try:
            if self.llm is None:
                return "모델이 초기화되지 않았습니다. API 키를 확인해주세요."
            
            return self.response_generator.generate_enhanced_response(query, context, n_results)
        except Exception as e:
            st.error(f"응답 생성 중 오류: {e}")
            return "응답 생성 중 오류가 발생했습니다. 다시 시도해주세요."
    
    def generate_diagnosis_report(self, answers: Dict[str, str], diagnosis_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        자가진단 결과를 바탕으로 실용적인 전략 가이드를 생성합니다.
        이북 데이터 기반의 실제 사례와 차별화된 전략을 제공합니다.
        """
        try:
            if self.llm is None:
                raise ValueError("모델이 초기화되지 않았습니다.")
            
            return self.diagnosis_generator.generate_report(answers, diagnosis_result)
        except Exception as e:
            st.error(f"진단 보고서 생성 중 오류: {e}")
            # 기본 보고서 제공
            level = diagnosis_result.get("level", {}).get("name", "기본")
            return {
                "title": "네이버 스마트 플레이스 최적화 전략 가이드",
                "level": level,
                "summary": "# 📑 네이버 스마트 플레이스 최적화 인사이트\n\n실용적인 최적화 전략과 차별화 방안이 필요합니다.",
                "current_diagnosis": "# 📊 현재 상황 분석\n\n검색 노출, 클릭율, 전환율 개선이 필요한 상태입니다.",
                "action_plan": "# 🎯 실행 전략\n\n핵심 키워드 최적화, 이미지 품질 향상, 리뷰 관리 시스템 구축을 단계적으로 실행하세요.",
                "upgrade_tips": "# 💡 차별화 전략\n\n경쟁사와 차별화된 시각적 요소, 스토리텔링, 고객 경험 전략을 개발하세요."
            }

    def search_ebook_content(self, query: str, n_results: int = 5) -> List[Dict[str, Any]]:
        """
        이북 콘텐츠에서 특정 쿼리와 관련된 정보를 검색합니다.
        """
        try:
            if self.vector_store is None:
                return [{"content": "이북 데이터를 사용할 수 없습니다.", "source": "시스템"}]
                
            # 벡터 스토어에서 관련 문서 검색
            docs = self.vector_store.raw_similarity_search(query, n_results)
            
            # 결과 포맷팅
            results = []
            for i, doc in enumerate(docs):
                results.append({
                    "content": doc.page_content,
                    "source": doc.metadata.get("source", f"이북 섹션 {i+1}"),
                    "relevance": round((1.0 - (i * 0.1)), 2)  # 간단한 관련성 점수
                })
                
            return results
        except Exception as e:
            st.error(f"이북 콘텐츠 검색 오류: {e}")
            return [{"content": "검색 중 오류가 발생했습니다.", "source": "시스템"}]

# 테스트 코드
if __name__ == "__main__":
    try:
        rag_model = RAGModel()
        
        # 간단한 쿼리 테스트
        test_query = "네이버 플레이스에서 경쟁사와 차별화하는 방법?"
        response = rag_model.generate_response(test_query)
        
        print("\n=== 테스트 응답 ===")
        print(f"질문: {test_query}")
        print(f"응답: {response}")
        
        # 이북 콘텐츠 검색 테스트
        results = rag_model.search_ebook_content("클릭률 높이는 최신 전략")
        print("\n=== 이북 검색 결과 ===")
        for result in results:
            print(f"소스: {result['source']} (관련성: {result['relevance']})")
            print(f"내용: {result['content'][:200]}...\n")
            
    except Exception as e:
        print(f"테스트 중 오류 발생: {e}") 
