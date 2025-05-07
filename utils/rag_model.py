# utils/vector_store.py - 벡터 DB 관련 기능
# 형식: Python (.py)
# 역할: 전자책 데이터 처리, 텍스트 분할, 벡터화 및 저장 기능
import os
from typing import Dict, List, Any, Optional, Tuple

from langchain.llms import OpenAI
from langchain.chat_models import ChatOpenAI
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain.schema.document import Document

# 자체 모듈 임포트
from utils.vector_store import VectorStore
from utils.questions import suggest_improvements

# 설정 로드
from config import OPENAI_API_KEY, LLM_MODEL, TEMPERATURE

class RAGModel:
    """
    Retrieval-Augmented Generation 모델 클래스
    벡터 DB에서 검색된 정보를 활용하여 고품질 응답을 생성합니다.
    """
    
    def __init__(self):
        """RAG 모델 초기화"""
        self.vector_store = VectorStore()
        self.llm = ChatOpenAI(
            openai_api_key=OPENAI_API_KEY,
            model_name=LLM_MODEL,
            temperature=TEMPERATURE
        )
    
    def generate_response(self, query: str, context: str = None, n_results: int = 3) -> str:
        """
        쿼리에 대한 응답을 생성합니다.
        
        Args:
            query: 사용자 질문
            context: 기존 컨텍스트 (없으면 자동으로 검색)
            n_results: 검색할 결과 수
            
        Returns:
            생성된 응답
        """
        # 컨텍스트가 없으면 벡터 DB에서 검색
        if not context:
            context = self.vector_store.get_relevant_content(query, n_results=n_results)
        
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
    
    def generate_diagnosis_report(self, answers: Dict[str, str], diagnosis_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        자가진단 결과를 바탕으로 진단 보고서를 생성합니다.
        
        Args:
            answers: 질문 ID를 키로, 선택한 옵션(A-E)을 값으로 하는 딕셔너리
            diagnosis_result: calculate_score 함수의 반환값
            
        Returns:
            진단 보고서 (제목, 요약, 강점, 개선점, 액션 플랜 등)
        """
        # 개선이 필요한 영역 파악
        improvements = diagnosis_result.get("improvements", {})
        weak_areas = [area['stage'] for area in improvements.get('weak_areas', [])]
        
        # 관련 콘텐츠 검색
        context = self.vector_store.get_relevant_content_for_diagnosis(
            answers=answers,
            weak_areas=weak_areas,
            n_results=3
        )
        
        # 강점 영역 파악 (평균 4점 이상)
        stage_scores = diagnosis_result.get("stage_scores", {})
        strength_areas = [
            stage for stage, score_info in stage_scores.items() 
            if score_info['avg_score'] >= 4.0
        ]
        
        # 진단 개요 생성
        overview = self._generate_diagnosis_overview(
            diagnosis_result=diagnosis_result,
            strength_areas=strength_areas,
            weak_areas=weak_areas
        )
        
        # 강점 분석 생성
        strengths_analysis = self._generate_strengths_analysis(
            diagnosis_result=diagnosis_result,
            strength_areas=strength_areas
        )
        
        # 개선점 분석 생성
        improvements_analysis = self._generate_improvements_analysis(
            diagnosis_result=diagnosis_result,
            improvements=improvements
        )
        
        # 액션 플랜 생성 - 관련 콘텐츠 활용
        action_plan = self._generate_action_plan(
            diagnosis_result=diagnosis_result,
            weak_areas=weak_areas,
            context=context
        )
        
        # 종합 보고서 생성
        return {
            "title": f"네이버 스마트 플레이스 최적화 진단 보고서",
            "level": diagnosis_result["level"]["name"],
            "overview": overview,
            "strengths_analysis": strengths_analysis,
            "improvements_analysis": improvements_analysis,
            "action_plan": action_plan
        }
    
    def _generate_diagnosis_overview(self, diagnosis_result: Dict[str, Any], 
                                    strength_areas: List[str], weak_areas: List[str]) -> str:
        """진단 개요를 생성합니다."""
        level = diagnosis_result["level"]["name"]
        avg_score = diagnosis_result["avg_score"]
        level_description = diagnosis_result["level"]["description"]
        
        # 프롬프트 생성
        prompt_template = f"""
        네이버 스마트 플레이스 마케팅 전문가로서, 다음 정보를 바탕으로 종합적인 진단 개요를 작성해 주세요.
        
        진단 결과:
        - 레벨: {level}
        - 평균 점수: {avg_score}/5
        - 레벨 설명: {level_description}
        - 강점 영역: {', '.join(strength_areas) if strength_areas else '없음'}
        - 개선 필요 영역: {', '.join(weak_areas) if weak_areas else '없음'}
        
        진단 개요에는 현재 플레이스 마케팅 현황에 대한 종합적인 평가, 강점과 약점의 균형, 그리고 
        개선을 통해 얻을 수 있는 기대 효과를 포함해 주세요. 비즈니스 측면에서의 의미도 언급해 주세요.
        
        진단 개요:
        """
        
        overview = self.llm.predict(prompt_template)
        return overview
    
    def _generate_strengths_analysis(self, diagnosis_result: Dict[str, Any], 
                                   strength_areas: List[str]) -> str:
        """강점 영역 분석을 생성합니다."""
        if not strength_areas:
            return "현재 플레이스 마케팅에서 특별히 뛰어난 강점 영역은 식별되지 않았습니다. 모든 영역에서 체계적인 개선이 필요합니다."
        
        # 강점 영역에 대한 세부 정보 수집
        stage_scores = diagnosis_result.get("stage_scores", {})
        strengths_details = []
        
        for area in strength_areas:
            score_info = stage_scores.get(area, {})
            strengths_details.append(f"- {area}: 평균 {score_info.get('avg_score', 0)}/5")
        
        # 프롬프트 생성
        prompt_template = f"""
        네이버 스마트 플레이스 마케팅 전문가로서, 다음 강점 영역에 대한 분석을 제공해 주세요.
        
        강점 영역:
        {', '.join(strength_areas)}
        
        세부 점수:
        {'\n'.join(strengths_details)}
        
        각 강점 영역이 비즈니스에 어떤 가치를 제공하는지, 이러한 강점을 어떻게 더 발전시키고 
        활용할 수 있는지에 대한 인사이트를 제공해 주세요. 또한 이러한 강점이 약점 영역을 보완하는 데
        어떻게 활용될 수 있는지도 언급해 주세요.
        
        강점 분석:
        """
        
        strengths_analysis = self.llm.predict(prompt_template)
        return strengths_analysis
    
    def _generate_improvements_analysis(self, diagnosis_result: Dict[str, Any], 
                                      improvements: Dict[str, Any]) -> str:
        """개선 영역 분석을 생성합니다."""
        weak_areas = improvements.get('weak_areas', [])
        if not weak_areas:
            return "현재 특별히 개선이 필요한 약점 영역은 식별되지 않았습니다. 전반적으로 균형 잡힌 플레이스 마케팅을 하고 있습니다."
        
        # 약점 영역에 대한 세부 정보 수집
        weak_areas_details = []
        for area_info in weak_areas:
            area = area_info['stage']
            score = area_info['avg_score']
            weak_areas_details.append(f"- {area}: 평균 {score}/5")
        
        # 프롬프트 생성
        prompt_template = f"""
        네이버 스마트 플레이스 마케팅 전문가로서, 다음 개선이 필요한 영역에 대한 분석을 제공해 주세요.
        
        개선 필요 영역:
        {', '.join([area_info['stage'] for area_info in weak_areas])}
        
        세부 점수:
        {'\n'.join(weak_areas_details)}
        
        각 영역이 현재 어떤 문제점을 가지고 있는지, 이로 인해 비즈니스에 어떤 부정적 영향이 있는지,
        그리고 이를 개선했을 때 얻을 수 있는 구체적인 비즈니스 효과에 대해 설명해 주세요.
        또한 우선 순위를 두고 개선해야 할 사항도 언급해 주세요.
        
        개선점 분석:
        """
        
        improvements_analysis = self.llm.predict(prompt_template)
        return improvements_analysis
    
    def _generate_action_plan(self, diagnosis_result: Dict[str, Any], 
                            weak_areas: List[str], context: str) -> str:
        """액션 플랜을 생성합니다."""
        level = diagnosis_result["level"]["name"]
        
        # 약점 영역에 대한 세부 정보 수집
        weak_areas_str = ', '.join(weak_areas)
        
        # 프롬프트 생성
        prompt_template = f"""
        네이버 스마트 플레이스 최적화 전문가로서, 다음 정보를 바탕으로 구체적인 액션 플랜을 제안해 주세요.
        
        현재 레벨: {level}
        개선 필요 영역: {weak_areas_str}
        
        참고 자료:
        {context}
        
        각 개선 영역별로 3-5개의 구체적이고 실행 가능한 액션 아이템을 제안해 주세요.
        각 액션 아이템은 다음 요소를 포함해야 합니다:
        1. 무엇을 해야 하는지 (What)
        2. 어떻게 수행해야 하는지 (How)
        3. 예상되는 효과 (Expected Impact)
        4. 난이도와 우선순위 (Difficulty & Priority)
        
        제안된 액션 아이템은 현재 레벨과 상황에 맞게 단계적으로 구성되어야 합니다.
        
        액션 플랜:
        """
        
        action_plan = self.llm.predict(prompt_template)
        return action_plan

# 테스트 코드
if __name__ == "__main__":
    # RAG 모델 초기화
    rag_model = RAGModel()
    
    # 간단한 쿼리 테스트
    test_query = "네이버 플레이스에서 대표 키워드를 어떻게 최적화해야 하나요?"
    response = rag_model.generate_response(test_query)
    
    print("\n=== 테스트 응답 ===")
    print(f"질문: {test_query}")
    print(f"응답: {response}")