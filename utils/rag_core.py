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
    벡터 DB에서 검색된 정보를 활용하여 고품질 응답을 생성합니다.
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
                st.warning(f"벡터 스토어 초기화 오류: {e}. 일부 기능이 제한될 수 있습니다.")
                self.vector_store = None
                
            # LLM 초기화
            self.llm = ChatOpenAI(
                openai_api_key=api_key,
                model_name=LLM_MODEL,
                temperature=TEMPERATURE
            )
            
            # 서브모듈 초기화
            self.response_generator = ResponseGenerator(self.llm, self.vector_store)
            self.diagnosis_generator = DiagnosisReportGenerator(self.llm, self.vector_store)
            
        except Exception as e:
            st.error(f"RAG 모델 초기화 오류: {e}")
            self.llm = None
            self.vector_store = None
    
    def generate_response(self, query: str, context: str = None, n_results: int = 3) -> str:
        """쿼리에 대한 응답을 생성합니다."""
        try:
            if self.llm is None:
                return "모델이 초기화되지 않았습니다. API 키를 확인해주세요."
            
            return self.response_generator.generate(query, context, n_results)
        except Exception as e:
            st.error(f"응답 생성 중 오류: {e}")
            return "응답 생성 중 오류가 발생했습니다. 다시 시도해주세요."
    
    def generate_diagnosis_report(self, answers: Dict[str, str], diagnosis_result: Dict[str, Any]) -> Dict[str, Any]:
        """자가진단 결과를 바탕으로 진단 보고서를 생성합니다."""
        try:
            if self.llm is None:
                raise ValueError("모델이 초기화되지 않았습니다.")
            
            return self.diagnosis_generator.generate_report(answers, diagnosis_result)
        except Exception as e:
            st.error(f"진단 보고서 생성 중 오류: {e}")
            # 기본 보고서 제공
            level = diagnosis_result.get("level", {}).get("name", "기본")
            return {
                "title": "네이버 스마트 플레이스 최적화 진단 보고서",
                "level": level,
                "summary": "# 📑 전체 보고서 요약\n\n기본적인 설정은 완료되었으나 체계적인 관리가 필요합니다.",
                "current_diagnosis": "# 📊 현재 진단\n\n현재 스마트 플레이스는 기초 단계입니다. 클릭율, 검색 노출, 전환율 개선이 필요합니다.",
                "action_plan": "# 🎯 액션 플랜\n\n핵심 키워드 최적화, 이미지 품질 향상, 리뷰 관리 시스템 구축을 우선적으로 실행하세요.",
                "upgrade_tips": "# 💡 업그레이드 팁\n\n매력적인 사진 업로드, 차별화된 설명 작성, 고객 리뷰 활성화로 경쟁사와 차별화하세요."
            }

# 테스트 코드
if __name__ == "__main__":
    try:
        rag_model = RAGModel()
        
        # 간단한 쿼리 테스트
        test_query = "네이버 플레이스에서 대표 키워드를 어떻게 최적화해야 하나요?"
        response = rag_model.generate_response(test_query)
        
        print("\n=== 테스트 응답 ===")
        print(f"질문: {test_query}")
        print(f"응답: {response}")
    except Exception as e:
        print(f"테스트 중 오류 발생: {e}") 