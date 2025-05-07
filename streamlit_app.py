# app.py - Streamlit 앱의 메인 파일
# 형식: Python (.py)
# 역할: 웹 인터페이스의 진입점으로, 전체 앱의 플로우를 제어합니다.


import os
import time
import streamlit as st
from datetime import datetime
from typing import Dict, List, Any

# 자체 모듈 임포트
from utils.questions import diagnosis_questions, calculate_score, suggest_improvements
from utils.vector_store import VectorStore
from utils.rag_model import RAGModel
from utils.pdf_generator import PDFGenerator

# 설정 로드
from config import APP_TITLE, APP_DESCRIPTION

# 전역 변수 설정
if 'answers' not in st.session_state:
    st.session_state.answers = {}
if 'current_stage' not in st.session_state:
    st.session_state.current_stage = list(diagnosis_questions.keys())[0]
if 'diagnosis_result' not in st.session_state:
    st.session_state.diagnosis_result = None
if 'report_data' not in st.session_state:
    st.session_state.report_data = None
if 'pdf_path' not in st.session_state:
    st.session_state.pdf_path = None
if 'page' not in st.session_state:
    st.session_state.page = 'welcome'  # welcome, diagnostic, result

# 함수 정의
def reset_diagnostic():
    """진단 상태를 초기화합니다."""
    st.session_state.answers = {}
    st.session_state.current_stage = list(diagnosis_questions.keys())[0]
    st.session_state.diagnosis_result = None
    st.session_state.report_data = None
    st.session_state.pdf_path = None
    st.session_state.page = 'welcome'

def save_answer(question_id, answer):
    """질문에 대한 응답을 저장합니다."""
    st.session_state.answers[question_id] = answer

def get_progress():
    """진단 진행 상황을 백분율로 반환합니다."""
    total_questions = sum(len(qs) for qs in diagnosis_questions.values())
    answered_questions = len(st.session_state.answers)
    return int((answered_questions / total_questions) * 100)

def next_stage():
    """다음 단계로 이동합니다."""
    stages = list(diagnosis_questions.keys())
    current_index = stages.index(st.session_state.current_stage)
    
    # 마지막 단계가 아니면 다음 단계로 이동
    if current_index < len(stages) - 1:
        st.session_state.current_stage = stages[current_index + 1]
    # 마지막 단계면 결과 페이지로 이동
    else:
        calculate_diagnosis()
        st.session_state.page = 'result'

def prev_stage():
    """이전 단계로 이동합니다."""
    stages = list(diagnosis_questions.keys())
    current_index = stages.index(st.session_state.current_stage)
    
    # 첫 단계가 아니면 이전 단계로 이동
    if current_index > 0:
        st.session_state.current_stage = stages[current_index - 1]

def calculate_diagnosis():
    """진단 결과를 계산하고 보고서 데이터를 생성합니다."""
    # 진단 결과 계산
    diagnosis_result = calculate_score(st.session_state.answers)
    
    # 개선 제안 생성
    improvements = suggest_improvements(diagnosis_result)
    diagnosis_result['improvements'] = improvements
    
    # 세션 상태에 저장
    st.session_state.diagnosis_result = diagnosis_result
    
    # RAG 모델을 사용해 보고서 데이터 생성
    with st.spinner("진단 보고서를 생성하고 있습니다..."):
        rag_model = RAGModel()
        report_data = rag_model.generate_diagnosis_report(
            answers=st.session_state.answers,
            diagnosis_result=diagnosis_result
        )
        st.session_state.report_data = report_data

def generate_pdf_report():
    """PDF 보고서를 생성합니다."""
    if not st.session_state.diagnosis_result or not st.session_state.report_data:
        st.error("진단 결과가 없습니다. 먼저 진단을 완료해주세요.")
        return
    
    with st.spinner("PDF 보고서를 생성하고 있습니다..."):
        # 임시 디렉토리 생성
        os.makedirs("reports", exist_ok=True)
        
        # PDF 생성
        pdf_generator = PDFGenerator()
        pdf_path = pdf_generator.generate_report(
            diagnosis_result=st.session_state.diagnosis_result,
            report_data=st.session_state.report_data,
            output_path="reports"
        )
        
        st.session_state.pdf_path = pdf_path

# 페이지 레이아웃
def show_welcome_page():
    """환영 페이지를 표시합니다."""
    st.title(APP_TITLE)
    st.markdown(APP_DESCRIPTION)
    
    st.markdown("### 🚀 네이버 스마트 플레이스 자가진단 테스트")
    st.markdown("""
    이 자가진단 테스트는 네이버 스마트 플레이스의 최적화 상태를 진단하고 개선 전략을 제안합니다.
    20개의 간단한 질문에 답하고 맞춤형 진단 보고서를 받아보세요.
    """)
    
    st.markdown("### 📋 테스트 진행 방법")
    st.markdown("""
    1. 각 질문에 가장 적합한 현재 상태를 선택하세요.
    2. 5개 영역의 모든 질문에 답변 후 진단 결과를 확인할 수 있습니다.
    3. 진단 결과를 바탕으로 맞춤형 개선 전략을 PDF로 다운로드할 수 있습니다.
    """)
    
    st.markdown("### 🔍 진단 영역")
    st.markdown("""
    - **인식하게 한다**: 키워드 설정, 상세 설명, 위치 정보 등 기본 정보 최적화
    - **클릭하게 한다**: 이미지 품질, 차별점 표현, 캐치프레이즈 등 흥미 유발 요소
    - **머물게 한다**: 콘텐츠 품질, 업데이트 주기, 이벤트 활용 등 체류시간 증가 요소
    - **연락오게 한다**: 예약 기능, 전화 응대, 쿠폰, 전환 유도 문구 등 전환율 향상 요소
    - **후속 피드백 받는다**: 리뷰 관리, 저장/알림 유도, 단골 고객 관리 등 재방문 유도 요소
    """)
    
    if st.button("진단 시작하기", type="primary"):
        st.session_state.page = 'diagnostic'

def show_diagnostic_page():
    """진단 페이지를 표시합니다."""
    # 상단 진행 상태바
    progress = get_progress()
    st.progress(progress)
    st.markdown(f"### 진행률: {progress}%")
    
    # 현재 단계 표시
    current_stage = st.session_state.current_stage
    st.title(f"{current_stage} 단계 진단")
    
    # 현재 단계의 질문들 표시
    questions = diagnosis_questions[current_stage]
    for question in questions:
        q_id = question["id"]
        st.markdown(f"### {question['question']}")
        
        # 이미 답변이 있는 경우 선택된 값으로 설정
        default_index = 0
        if q_id in st.session_state.answers:
            options = [opt["value"] for opt in question["options"]]
            selected_value = st.session_state.answers[q_id]
            if selected_value in options:
                default_index = options.index(selected_value)
        
        option = st.radio(
            f"현재 상태를 선택하세요:",
            options=[f"{opt['value']}. {opt['text']}" for opt in question["options"]],
            key=f"radio_{q_id}",
            index=default_index
        )
        
        # 선택한 옵션 값 추출 및 저장
        selected_value = option.split(".")[0]
        save_answer(q_id, selected_value)
        
        st.markdown("---")
    
    # 네비게이션 버튼
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        if st.session_state.current_stage != list(diagnosis_questions.keys())[0]:
            if st.button("이전 단계"):
                prev_stage()
    
    with col3:
        if st.session_state.current_stage == list(diagnosis_questions.keys())[-1]:
            if st.button("진단 완료", type="primary"):
                next_stage()
        else:
            if st.button("다음 단계", type="primary"):
                next_stage()

def show_result_page():
    """결과 페이지를 표시합니다."""
    if not st.session_state.diagnosis_result:
        st.error("진단 결과가 없습니다. 먼저 진단을 완료해주세요.")
        if st.button("진단 페이지로 돌아가기"):
            st.session_state.page = 'diagnostic'
        return
    
    diagnosis_result = st.session_state.diagnosis_result
    report_data = st.session_state.report_data
    
    st.title("네이버 스마트 플레이스 최적화 진단 결과")
    
    # 요약 정보
    st.markdown("## 진단 요약")
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("종합 점수", f"{diagnosis_result['avg_score']}/5")
    with col2:
        st.metric("진단 레벨", diagnosis_result["level"]["name"])
    
    st.markdown(f"**{diagnosis_result['level']['description']}**")
    
    # 영역별 점수
    st.markdown("## 영역별 점수")
    stage_data = []
    for stage, score_info in diagnosis_result["stage_scores"].items():
        stage_data.append({
            "영역": stage,
            "점수": score_info["avg_score"]
        })
    
    st.bar_chart(
        stage_data,
        x="영역",
        y="점수",
        height=300
    )
    
    # 개요
    st.markdown("## 진단 개요")
    st.markdown(report_data.get("overview", ""))
    
    # 강점 분석
    st.markdown("## 강점 분석")
    st.markdown(report_data.get("strengths_analysis", ""))
    
    # 개선점 분석
    st.markdown("## 개선점 분석")
    st.markdown(report_data.get("improvements_analysis", ""))
    
    # 액션 플랜
    st.markdown("## 액션 플랜")
    st.markdown(report_data.get("action_plan", ""))
    
    # PDF 보고서 다운로드
    st.markdown("## 보고서 다운로드")
    if st.session_state.pdf_path:
        st.markdown(f"PDF 보고서가 생성되었습니다. 아래 버튼을 클릭하여 다운로드하세요.")
        
        with open(st.session_state.pdf_path, "rb") as file:
            st.download_button(
                label="PDF 보고서 다운로드",
                data=file,
                file_name=os.path.basename(st.session_state.pdf_path),
                mime="application/pdf"
            )
    else:
        if st.button("PDF 보고서 생성"):
            generate_pdf_report()
    
    # 새 진단 시작
    st.markdown("## 새 진단 시작")
    if st.button("새로운 진단 시작하기"):
        reset_diagnostic()

# 메인 앱 구성
def main():
    """메인 애플리케이션 실행"""
    # 페이지 설정
    st.set_page_config(
        page_title=APP_TITLE,
        page_icon="🔍",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # 사이드바
    with st.sidebar:
        st.title("🔍 스마트 플레이스 마케팅 부스터")
        st.markdown("---")
        
        if st.session_state.page != 'welcome':
            if st.button("처음으로 돌아가기"):
                reset_diagnostic()
        
        st.markdown("### 개발자 정보")
        st.markdown("스마트 플레이스 최적화 컨설팅")
        st.markdown("연락처: contact@placeoptimize.kr")
        
        st.markdown("---")
        st.markdown("© 2025 스마트 플레이스 최적화 컨설팅")
    
    # 페이지 표시
    if st.session_state.page == 'welcome':
        show_welcome_page()
    elif st.session_state.page == 'diagnostic':
        show_diagnostic_page()
    elif st.session_state.page == 'result':
        show_result_page()

if __name__ == "__main__":
    main()
