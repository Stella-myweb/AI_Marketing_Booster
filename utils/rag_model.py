# utils/rag_model.py - 벡터 DB 관련 기능
import os
import streamlit as st
from typing import Dict, List, Any

from langchain.chat_models import ChatOpenAI
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
                
            # OpenAI API 연결
            self.llm = ChatOpenAI(
                openai_api_key=api_key,
                model_name=LLM_MODEL,
                temperature=TEMPERATURE
            )
        except Exception as e:
            st.error(f"RAG 모델 초기화 오류: {e}")
            self.vector_store = None
            # 기본 LLM 초기화 시도
            try:
                api_key = st.secrets.get("OPENAI_API_KEY") or OPENAI_API_KEY
                self.llm = ChatOpenAI(
                    openai_api_key=api_key,
                    model_name=LLM_MODEL,
                    temperature=TEMPERATURE
                )
            except Exception:
                self.llm = None
    
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
        try:
            if self.llm is None:
                return "모델이 초기화되지 않았습니다. API 키를 확인해주세요."
                
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
    
    def generate_diagnosis_report(self, answers: Dict[str, str], diagnosis_result: Dict[str, Any]) -> Dict[str, Any]:
        """자가진단 결과를 바탕으로 간결한 진단 보고서를 생성합니다."""
        try:
            if self.llm is None:
                raise ValueError("모델이 초기화되지 않았습니다.")
                
            # 데이터 분석
            level = diagnosis_result["level"]["name"]
            improvements = diagnosis_result.get("improvements", {})
            weak_areas = [area['stage'] for area in improvements.get('weak_areas', [])]
            
            # 관련 콘텐츠 검색
            context = ""
            if self.vector_store:
                try:
                    context = self.vector_store.get_relevant_content_for_diagnosis(
                        answers=answers,
                        weak_areas=weak_areas,
                        n_results=3
                    )
                except Exception as e:
                    st.warning(f"콘텐츠 검색 오류: {e}")
            
            # 간결한 보고서 생성
            title_map = {
                "인식하게 한다": "검색 노출 최적화",
                "클릭하게 한다": "클릭율 높이는 전략",
                "머물게 한다": "체류시간 늘리는 방법",
                "연락오게 한다": "문의/예약 전환율 높이기",
                "후속 피드백 받는다": "고객 재방문 유도 전략"
            }
            
            # 약점 영역 이름 변경
            new_weak_areas = [title_map.get(area, area) for area in weak_areas]
            
            # 전체 요약 보고서 생성
            summary = f"""
            # 📑 전체 보고서 요약
            
            **현재 상태**: {level} 단계로, {diagnosis_result["level"]["description"]}
            
            **주요 개선 필요 영역**: {', '.join(new_weak_areas)}
            
            **우선 실행 액션**: 
            1. {title_map.get(weak_areas[0], weak_areas[0]) if weak_areas else '기본 정보'} 최적화
            2. {title_map.get(weak_areas[1], weak_areas[1]) if len(weak_areas) > 1 else '콘텐츠 품질'} 개선
            3. 리뷰 수집 및 관리 체계화
            
            **기대 효과**: 위 액션 수행 시 약 30-50% 성과 향상 예상
            """
            
            # 현재 진단 생성
            current_diagnosis = self._generate_short_diagnosis(diagnosis_result, weak_areas)
            
            # 액션 플랜 생성
            action_plan = self._generate_short_action_plan(diagnosis_result, weak_areas)
            
            # 업그레이드 팁 생성
            upgrade_tips = self._generate_short_upgrade_tips(diagnosis_result, weak_areas)
            
            # 종합 보고서 반환
            return {
                "title": f"네이버 스마트 플레이스 최적화 진단 보고서",
                "level": level,
                "summary": summary,
                "current_diagnosis": current_diagnosis,
                "action_plan": action_plan, 
                "upgrade_tips": upgrade_tips
            }
        except Exception as e:
            st.error(f"진단 보고서 생성 중 오류: {e}")
            # 기본 보고서 제공
            return {
                "title": "네이버 스마트 플레이스 최적화 진단 보고서",
                "level": diagnosis_result.get("level", {}).get("name", "기본"),
                "summary": "# 📑 전체 보고서 요약\n\n기본적인 설정은 완료되었으나 체계적인 관리가 필요합니다.",
                "current_diagnosis": "# 📊 현재 진단\n\n현재 스마트 플레이스는 기초 단계입니다. 클릭율, 검색 노출, 전환율 개선이 필요합니다.",
                "action_plan": "# 🎯 액션 플랜\n\n핵심 키워드 최적화, 이미지 품질 향상, 리뷰 관리 시스템 구축을 우선적으로 실행하세요.",
                "upgrade_tips": "# 💡 업그레이드 팁\n\n매력적인 사진 업로드, 차별화된 설명 작성, 고객 리뷰 활성화로 경쟁사와 차별화하세요."
            }

    def _generate_short_diagnosis(self, diagnosis_result: Dict[str, Any], weak_areas: List[str]) -> str:
        """간결한 현재 진단을 생성합니다."""
        try:
            level = diagnosis_result["level"]["name"]
            
            title_map = {
                "인식하게 한다": "검색 노출 최적화",
                "클릭하게 한다": "클릭율 높이는 전략",
                "머물게 한다": "체류시간 늘리는 방법",
                "연락오게 한다": "문의/예약 전환율 높이기",
                "후속 피드백 받는다": "고객 재방문 유도 전략"
            }
            
            weak_areas_str = ', '.join([title_map.get(area, area) for area in weak_areas])
            
            diagnosis = f"""
            # 📊 현재 진단
            
            현재 스마트 플레이스는 **{level}** 단계로, {diagnosis_result["level"]["description"]}
            
            **주요 개선 필요 영역**: {weak_areas_str}
            
            **현재 상태가 미치는 영향**: 검색 노출 제한, 클릭률 저하, 방문/구매 전환율 감소로 인한 매출 기회 손실이 발생하고 있습니다.
            
            **즉각 개선 필요**: {title_map.get(weak_areas[0], weak_areas[0]) if weak_areas else '기본 정보'} 영역부터 집중적인 개선이 필요합니다.
            """
            
            return diagnosis
        except Exception as e:
            st.error(f"진단 생성 중 오류: {e}")
            return """
            # 📊 현재 진단
            
            현재 스마트 플레이스는 기초 단계입니다. 클릭율, 검색 노출, 전환율 개선이 필요합니다.
            """

    def _generate_short_action_plan(self, diagnosis_result: Dict[str, Any], weak_areas: List[str]) -> str:
        """간결한 액션 플랜을 생성합니다."""
        try:
            title_map = {
                "인식하게 한다": "검색 노출 최적화",
                "클릭하게 한다": "클릭율 높이는 전략",
                "머물게 한다": "체류시간 늘리는 방법",
                "연락오게 한다": "문의/예약 전환율 높이기",
                "후속 피드백 받는다": "고객 재방문 유도 전략"
            }
            
            action_items = {
                "인식하게 한다": ["지역명+업종+상황별 키워드 20개 등록", "상세 설명에 키워드 자연스럽게 통합"],
                "클릭하게 한다": ["고품질 대표 이미지 업로드", "매력적인 캐치프레이즈 개발"],
                "머물게 한다": ["메뉴/서비스 상세 정보 강화", "정기적 콘텐츠 업데이트"],
                "연락오게 한다": ["스마트콜 응답률 개선", "예약 인센티브 도입"],
                "후속 피드백 받는다": ["영수증 리뷰 시스템 구축", "리뷰 관리 루틴 설정"]
            }
            
            action_plan = "# 🎯 액션 플랜\n\n"
            action_plan += "다음 액션을 30일 내로 집중적으로 수행하여 즉각적인 성과 개선을 도모하세요:\n\n"
            
            for area in weak_areas[:2]:  # 최대 2개 영역만 집중
                actions = action_items.get(area, ["기본 정보 업데이트", "차별화 포인트 강화"])
                action_plan += f"## {title_map.get(area, area)}\n"
                for action in actions:
                    action_plan += f"* **{action}**\n"
                action_plan += "\n"
            
            action_plan += "## 우선순위\n"
            action_plan += "1. 고품질 이미지와 키워드 최적화\n"
            action_plan += "2. 메뉴/서비스 정보 상세화\n"
            action_plan += "3. 리뷰 수집 시스템 구축\n"
            
            return action_plan
        except Exception as e:
            st.error(f"액션 플랜 생성 중 오류: {e}")
            return """
            # 🎯 액션 플랜
            
            핵심 키워드 최적화, 이미지 품질 향상, 리뷰 관리 시스템 구축을 우선적으로 실행하세요.
            """

    def _generate_short_upgrade_tips(self, diagnosis_result: Dict[str, Any], weak_areas: List[str]) -> str:
        """간결한 업그레이드 팁을 생성합니다."""
        try:
            upgrade_tips = """
            # 💡 업그레이드 팁
            
            ## 즉시 실행 팁 (당장 오늘)
            * 🔍 **핵심 키워드 5개 추가**: 지역명+업종+상황 조합 키워드 추가
            * 📱 **스마트콜 활성화**: 실시간 고객 전화 응대 체계 구축
            * 📝 **정확한 영업시간 등록**: 휴무일, 브레이크타임 포함
            
            ## 단기 개선 팁 (1-2주)
            * 🖼️ **매력적인 사진 업로드**: 매장 공간과 메뉴/서비스 고화질 사진
            * 📋 **차별화 포인트 강조**: 경쟁사와 구분되는 특장점 강조
            
            ## 경쟁사 차별화 전략
            * 🌟 **독특한 스토리텔링**: 비즈니스만의 스토리 강조
            * 🎁 **특별한 경험 제공**: 경쟁사에 없는 차별점 부각
            """
            
            return upgrade_tips
        except Exception as e:
            st.error(f"업그레이드 팁 생성 중 오류: {e}")
            return """
            # 💡 업그레이드 팁
            
            매력적인 사진 업로드, 차별화된 설명 작성, 고객 리뷰 활성화로 경쟁사와 차별화하세요.
            """

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
