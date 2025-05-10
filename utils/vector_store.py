# utils/vector_store.py에 추가할 메소드
import streamlit as st 
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

def get_relevant_content_for_diagnosis(self, answers, weak_areas, n_results: int = 3) -> str:
    """
    진단 결과에 맞는 콘텐츠를 검색합니다.
    
    Args:
        answers: 사용자 응답 (딕셔너리)
        weak_areas: 개선이 필요한 영역 (리스트)
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
        return "콘텐츠 검색 중 오류가 발생했습니다."  
