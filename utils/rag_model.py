# utils/rag_model.py - 벡터 DB 관련 기능
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
            진단 보고서 (현재 진단, 액션 플랜, 업그레이드 팁)
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
        
        # 현재 진단 생성
        current_diagnosis = self._generate_current_diagnosis(
            diagnosis_result=diagnosis_result,
            strength_areas=strength_areas,
            weak_areas=weak_areas
        )
        
        # 액션 플랜 생성
        action_plan = self._generate_action_plan(
            diagnosis_result=diagnosis_result,
            weak_areas=weak_areas,
            context=context
        )
        
        # 업그레이드 팁 생성
        upgrade_tips = self._generate_upgrade_tips(
            diagnosis_result=diagnosis_result,
            weak_areas=weak_areas,
            context=context
        )
        
        # 종합 보고서 생성
        return {
            "title": f"네이버 스마트 플레이스 최적화 진단 보고서",
            "level": diagnosis_result["level"]["name"],
            "current_diagnosis": current_diagnosis,
            "action_plan": action_plan,
            "upgrade_tips": upgrade_tips
        }
    
    def _generate_current_diagnosis(self, diagnosis_result: Dict[str, Any], 
                                 strength_areas: List[str], weak_areas: List[str]) -> str:
        """현재 진단 요약을 생성합니다."""
        level = diagnosis_result["level"]["name"]
        level_description = diagnosis_result["level"]["description"]
        
        # 새로운 제목 매핑
        title_map = {
            "인식하게 한다": "검색 노출 최적화",
            "클릭하게 한다": "클릭율 높이는 전략",
            "머물게 한다": "체류시간 늘리는 방법",
            "연락오게 한다": "문의/예약 전환율 높이기",
            "후속 피드백 받는다": "고객 재방문 유도 전략"
        }
        
        # 강점 영역과 약점 영역에 새 제목 적용
        strength_areas_mapped = [title_map.get(area, area) for area in strength_areas]
        weak_areas_mapped = [title_map.get(area, area) for area in weak_areas]
        
        # 프롬프트 생성
        prompt_template = f"""
        네이버 스마트 플레이스 마케팅 전문가로서, 다음 정보를 바탕으로 현재 진단 요약을 작성해 주세요.
        
        진단 결과:
        - 레벨: {level}
        - 레벨 설명: {level_description}
        - 강점 영역: {', '.join(strength_areas_mapped) if strength_areas_mapped else '없음'}
        - 개선 필요 영역: {', '.join(weak_areas_mapped) if weak_areas_mapped else '없음'}
        
        다음 요구사항에 따라 진단 요약을 작성해 주세요:
        1. 반드시 "# 📊 현재 진단"으로 시작하는 마크다운 제목을 포함해 주세요.
        2. 진단 시작 부분에 현재 스마트 플레이스 최적화 상태에 대한 간략한 총평을 1-2문장으로 추가해 주세요.
        3. 아래 4가지 섹션으로 구성해 주세요:
           ## 👁️ 현재 상태
           * 현재 스마트 플레이스의 전반적인 상태와 레벨에 대한 설명
           * 핵심 지표와 점수에 대한 간략한 요약
           
           ## 💪 강점
           * 현재 잘하고 있는 부분에 대한 설명
           * 강점이 없다면 "현재 특별히 두드러진 강점이 발견되지 않았습니다."와 같은 문구로 대체
           
           ## 🔍 개선점
           * 개선이 필요한 부분에 대한 명확한 설명
           * 구체적으로 어떤 측면이 부족한지 설명
           
           ## 💰 비즈니스 영향
           * 현재 상태가 비즈니스에 미치는 영향과 개선 시 기대효과 설명
           * 구체적인 비즈니스 메트릭(방문자 수, 전환율 등)에 미치는 영향 포함
           
        4. 각 섹션은 2-3문장으로 간결하게 작성해 주세요.
        5. 업그레이드 팁 및 액션 플랜과 동일한 스타일로 깔끔하게 작성해 주세요.
        6. 마크다운 기호가 최종 출력물에서 그대로 보이지 않도록 주의해 주세요.
        
        현재 진단:
        """
        
        diagnosis = self.llm.predict(prompt_template)
        return diagnosis
    
    def _generate_action_plan(self, diagnosis_result: Dict[str, Any], 
                           weak_areas: List[str], context: str) -> str:
        """액션 플랜을 생성합니다."""
        level = diagnosis_result["level"]["name"]
        
        # 새로운 제목 매핑
        title_map = {
            "인식하게 한다": "검색 노출 최적화",
            "클릭하게 한다": "클릭율 높이는 전략",
            "머물게 한다": "체류시간 늘리는 방법",
            "연락오게 한다": "문의/예약 전환율 높이기",
            "후속 피드백 받는다": "고객 재방문 유도 전략"
        }
        
        # 이모지 매핑
        emoji_map = {
            "검색 노출 최적화": "🔍",
            "클릭율 높이는 전략": "🖱️",
            "체류시간 늘리는 방법": "⏱️",
            "문의/예약 전환율 높이기": "📱",
            "고객 재방문 유도 전략": "💬"
        }
        
        # 약점 영역 이름을 새 제목으로 변경
        new_weak_areas = [title_map.get(area, area) for area in weak_areas]
        weak_areas_str = ', '.join(new_weak_areas)
        
        # 프롬프트 생성
        prompt_template = f"""
        네이버 스마트 플레이스 최적화 전문가로서, 다음 정보를 바탕으로 구체적인 액션 플랜을 제안해 주세요.
        
        현재 레벨: {level}
        개선 필요 영역: {weak_areas_str}
        
        참고 자료:
        {context}
        
        다음 요구사항에 따라 액션 플랜을 작성해 주세요:
        1. 반드시 "# 🎯 액션 플랜"으로 시작하는 마크다운 제목을 포함해 주세요.
        2. 액션 플랜 시작 부분에 "성공적인 네이버 플레이스 마케팅을 위해 실행해야 할 핵심 전략입니다. 각 액션 아이템을 실행하면 고객 유입과 전환율을 높일 수 있습니다."와 같은 간단한 설명을 추가해 주세요.
        3. 각 개선 영역은 다음과 같이 구성해 주세요:
           ## ✅ [영역 이름]
           * 각 영역에 대한 간단한 설명을 추가하세요: 왜 이 영역이 중요한지, 어떤 효과를 기대할 수 있는지 1-2문장으로 설명
           * 항목별로 업그레이드 팁과 같은 형식으로 작성하세요:
             * 🔹 **[액션 제목]**: 간결한 설명과 왜 중요한지 이유 포함
             * 🔸 **[액션 제목]**: 간결한 설명과 왜 중요한지 이유 포함
           → *기대 효과: 이 영역의 액션을 실행했을 때 기대할 수 있는 결과*
        
        4. 각 영역은 최소 2개, 최대 3개의 구체적인 액션 아이템을 포함해야 합니다.
        5. 모든 액션은 실행 가능하고 구체적이어야 하며, 그 이유와 중요성을 설명해야 합니다.
        6. 업그레이드 팁과 동일한 스타일로 깔끔하게 작성해 주세요.
        
        예시 형식:
        # 🎯 액션 플랜
        
        성공적인 네이버 플레이스 마케팅을 위해 실행해야 할 핵심 전략입니다. 각 액션 아이템을 실행하면 고객 유입과 전환율을 높일 수 있습니다.
        
        ## ✅ 클릭율 높이는 전략
        클릭율을 높이면 더 많은 잠재 고객이 페이지를 방문하게 되어 궁극적으로 매출 증가로 이어집니다.
        
        * 🔹 **매력적인 대표 이미지 업로드**: 고품질 사진은 첫인상을 결정하며, 전문적인 이미지는 신뢰도를 높입니다.
        * 🔸 **핵심 키워드가 포함된 제목 작성**: 검색 시 노출 빈도를 높이고 고객의 관심을 끌 수 있습니다.
        
        → *기대 효과: 클릭률 30% 이상 증가와 방문자 수 확대*
        """
        
        action_plan = self.llm.predict(prompt_template)
        return action_plan
    
    def _generate_upgrade_tips(self, diagnosis_result: Dict[str, Any], 
                             weak_areas: List[str], context: str) -> str:
        """맞춤형 업그레이드 팁을 생성합니다."""
        level = diagnosis_result["level"]["name"]
        
        # 새로운 제목 매핑
        title_map = {
            "인식하게 한다": "검색 노출 최적화",
            "클릭하게 한다": "클릭율 높이는 전략",
            "머물게 한다": "체류시간 늘리는 방법",
            "연락오게 한다": "문의/예약 전환율 높이기",
            "후속 피드백 받는다": "고객 재방문 유도 전략"
        }
        
        # 약점 영역 이름 변경
        new_weak_areas = [title_map.get(area, area) for area in weak_areas]
        
        # 프롬프트 생성
        prompt_template = f"""
        네이버 스마트 플레이스 최적화 전문가로서, 다음 정보를 바탕으로 맞춤형 업그레이드 팁을 제공해 주세요.
        
        현재 레벨: {level}
        개선 필요 영역: {', '.join(new_weak_areas)}
        
        참고 자료:
        {context}
        
        다음 요구사항에 따라 업그레이드 팁을 작성해 주세요:
        1. 반드시 "# 💡 업그레이드 팁"으로 시작하는 마크다운 제목을 포함해 주세요.
        2. 내용은 3단계로 구성하세요:
           - ## ✅ 초보 단계
           - ## ✅ 중급 단계
           - ## ✅ 고급 단계
        3. 각 단계별로 2개의 핵심 팁만 제공하세요.
        4. 각 팁은 이모지와 볼드체 제목으로 시작하고, 간결한 설명을 덧붙이세요:
           * 🖼️ **매력적인 사진 업로드**: 고화질의 매력적인 사진을 업로드하여 고객의 시선을 끌어보세요.
           * 📝 **두 번째 팁 제목**: 간결한 설명...
        5. 각 단계 끝에는 화살표(→)와 함께 기대 효과를 한 줄로 추가하세요:
           → *효과: 이 단계의 기대 효과 한 줄*
        6. 마지막으로 한 문장의 결론을 추가하세요.
        
        깔끔하고 시각적으로 보기 좋게 구성하며, 모든 이모지와 마크다운 형식을 정확히 사용해 주세요.
        """
        
        upgrade_tips = self.llm.predict(prompt_template)
        return upgrade_tips

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