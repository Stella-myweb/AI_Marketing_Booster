# utils/rag_generator.py
import streamlit as st
from typing import Optional

class ResponseGenerator:
    """
    쿼리에 대한 응답을 생성하는 클래스
    """
    
    def __init__(self, llm, vector_store):
        """초기화"""
        self.llm = llm
        self.vector_store = vector_store
    
    def generate(self, query: str, context: str = None, n_results: int = 3) -> str:
        """
        쿼리에 대한 응답을 생성합니다.
        
        Args:
            query: 사용자 질문
            context: 기존 컨텍스트 (없으면 자동으로 검색)
            n_results: 검색할 결과 수
            
        Returns:
            생성된 응답
        """
        try:
            # 컨텍스트가 없으면 벡터 DB에서 검색
            if not context:
                if self.vector_store:
                    context = self.vector_store.get_relevant_content(query, n_results=n_results)
                else:
                    context = """
                    네이버 스마트 플레이스 최적화를 위한 일반적인 팁:
                    1. 매력적인 이미지 사용하기
                    2. 핵심 키워드 포함하기
                    3. 상세한 비즈니스 설명 제공하기
                    4. 정기적인 콘텐츠 업데이트하기
                    5. 고객 리뷰 관리하기
                    """
            
            # 프롬프트 템플릿 생성
            prompt_template = f"""
            네이버 스마트 플레이스 최적화 전문가로서 아래 질문에 답변해 주세요.
            다음 참고 자료를 활용하여 정확하고 도움이 되는 답변을 제공하세요.
            
            참고 자료:
            {context}
            
            질문: {query}
            
            답변:
            """
            
            # 응답 생성
            response = self.llm.predict(prompt_template)
            return response
        except Exception as e:
            st.error(f"응답 생성 중 오류: {e}")
            return "응답 생성 중 오류가 발생했습니다. 다시 시도해주세요." 