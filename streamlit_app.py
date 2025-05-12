# app.py - Streamlit 앱의 메인 파일
# 형식: Python (.py)
# 역할: 웹 인터페이스의 진입점으로, 전체 앱의 플로우를 제어합니다.

import os
import time
import streamlit as st
from datetime import datetime
from typing import Dict, List, Any
from utils.pdf_generator import PDFGenerator
from io import BytesIO
import re
import logging
import openai

# 페이지 설정 - 가장 먼저 호출되어야 함
st.set_page_config(
    page_title="AI 마케팅 부스터",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)



# 자체 모듈 임포트
from utils.questions import diagnosis_questions, calculate_score, suggest_improvements
from utils.vector_store import VectorStore
from utils.rag_model import RAGModel

# 설정 로드
from config import APP_TITLE, APP_DESCRIPTION, REPORT_TITLE, COMPANY_NAME, LOGO_PATH

# 나머지 코드는 그대로 유지... 

# # 디버깅 정보
# st.sidebar.write("### 디버깅 정보")
# if "OPENAI_API_KEY" in st.secrets:
#     st.sidebar.success("API 키 설정됨 (secrets)")
# elif os.getenv("OPENAI_API_KEY"):
#     st.sidebar.success("API 키 설정됨 (환경변수)")
# else:
#     st.sidebar.error("API 키 없음")

# # 파일 경로 확인
# current_dir = os.path.dirname(os.path.abspath(__file__))
# data_dir = os.path.join(current_dir, "data")
# ebook_path = os.path.join(data_dir, "ebook_content.txt")

# if os.path.exists(ebook_path):
#     st.sidebar.success(f"ebook_content.txt 파일 존재")
# else:
#     st.sidebar.error(f"ebook_content.txt 파일 없음")

# 전역 변수 설정
if 'answers' not in st.session_state:
    st.session_state.answers = {}
if 'current_stage' not in st.session_state:
    st.session_state.current_stage = list(diagnosis_questions.keys())[0]
if 'diagnosis_result' not in st.session_state:
    st.session_state.diagnosis_result = None
if 'report_data' not in st.session_state:
    st.session_state.report_data = None
if 'page' not in st.session_state:
    st.session_state.page = 'welcome'  # welcome, diagnostic, result
if 'copy_clicked' not in st.session_state:
    st.session_state.copy_clicked = False

# 함수 정의
def reset_diagnostic():
    """진단 상태를 초기화합니다."""
    st.session_state.answers = {}
    st.session_state.current_stage = list(diagnosis_questions.keys())[0]
    st.session_state.diagnosis_result = None
    st.session_state.report_data = None
    st.session_state.page = 'welcome'
    st.session_state.copy_clicked = False

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
    try:
        # 진단 결과 계산
        diagnosis_result = calculate_score(st.session_state.answers)
        
        # 개선 제안 생성
        improvements = suggest_improvements(diagnosis_result)
        diagnosis_result['improvements'] = improvements
        
        # 세션 상태에 저장
        st.session_state.diagnosis_result = diagnosis_result
        
        # RAG 모델 사용 전 API 키 확인
        if "OPENAI_API_KEY" in st.secrets:
            api_key = st.secrets["OPENAI_API_KEY"]
        else:
            api_key = os.getenv("OPENAI_API_KEY")
            
        if not api_key:
            st.error("OpenAI API 키가 설정되지 않았습니다.")
            st.session_state.report_data = {
                "title": "진단 보고서",
                "level": diagnosis_result["level"]["name"],
                "current_diagnosis": "API 키 오류로 자세한 진단을 생성할 수 없습니다.",
                "action_plan": "API 키를 설정해주세요.",
                "upgrade_tips": "API 키 설정 후 다시 시도해주세요."
            }
            return
        
        # 간소화된 보고서 생성 로직
        try:
            # RAG 모델 초기화 시도
            with st.spinner("진단 보고서를 생성하고 있습니다..."):
                rag_model = RAGModel()
                report_data = rag_model.generate_diagnosis_report(
                    answers=st.session_state.answers,
                    diagnosis_result=diagnosis_result
                )
                st.session_state.report_data = report_data
        except Exception as e:
            logging.exception(f"진단 보고서 생성 중 오류: {e}")
            # 기본 보고서 제공
            st.session_state.report_data = {
                "title": "네이버 스마트 플레이스 최적화 전략 가이드",
                "level": diagnosis_result.get("level", {}).get("name", "기본"),
                "current_diagnosis": "진단 결과 생성에 실패했습니다.",
                "action_plan": "진단 결과 생성에 실패했습니다.",
                "upgrade_tips": "진단 결과 생성에 실패했습니다."
            }
    except Exception as e:
        logging.exception(f"진단 계산 중 오류 발생: {e}")
        # 기본 결과 제공
        st.session_state.diagnosis_result = {
            "level": {"name": "오류", "description": "진단 중 오류가 발생했습니다."}
        }
        st.session_state.report_data = {
            "title": "오류 발생",
            "level": "오류",
            "current_diagnosis": "진단 계산 중 오류가 발생했습니다.",
            "action_plan": "다시 시도해주세요.",
            "upgrade_tips": "문제가 지속되면 개발자에게 문의하세요."
        }

def toggle_copy():
    """복사 상태를 토글합니다."""
    st.session_state.copy_clicked = not st.session_state.copy_clicked

def clipboard_button(text_to_copy: str, label: str = "📄", tooltip: str = "복사하기"):
    # 버튼을 오른쪽 상단에 띄우기 위해 columns 사용
    col1, col2 = st.columns([10, 1])
    with col2:
        # HTML+JS로 복사 버튼 구현
        st.components.v1.html(f"""
        <button id="copy-btn" title="{tooltip}" style="font-size:1.2em; border:none; background:transparent; cursor:pointer;">
            {label}
        </button>
        <script>
        const btn = document.getElementById('copy-btn');
        btn.onclick = function() {{
            navigator.clipboard.writeText({repr(text_to_copy)});
            btn.innerText = "✅";
            setTimeout(()=>{{btn.innerText="{label}";}}, 1200);
        }};
        </script>
        """, height=35)

def clean_text(text):
    # 큰따옴표, 별표 등 불필요한 특수문자 제거
    return re.sub(r'["*]', '', text)

def clean_pdf_text(text):
    text = re.sub(r'\n+', '\n', text)
    text = re.sub(r'[ \t]+', ' ', text)
    text = re.sub(r'\n\s*\n', '\n', text)
    return text.strip()

def check_openai_api_key(api_key):
    try:
        openai.api_key = api_key
        openai.Model.list()  # 가장 간단한 API 호출
        return True, "API 키가 정상적으로 작동합니다."
    except Exception as e:
        return False, f"API 키 오류: {e}"

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
    3. 진단 결과를 바탕으로 맞춤형 개선 전략을 확인할 수 있습니다.
    """)
    
    st.markdown("### 🔍 진단 영역")
    st.markdown("""
    - **검색 노출 최적화**: 키워드 설정, 상세 설명, 위치 정보 등 기본 정보 최적화
    - **클릭율 높이는 전략**: 이미지 품질, 차별점 표현, 캐치프레이즈 등 흥미 유발 요소
    - **머물게 한다**: 콘텐츠 품질, 업데이트 주기, 이벤트 활용 등 체류시간 증가 요소
    - **문의/예약 전환율 높이기**: 예약 기능, 전화 응대, 쿠폰, 전환 유도 문구 등 전환율 향상 요소
    - **고객 재방문 유도 전략**: 리뷰 관리, 저장/알림 유도, 단골 고객 관리 등 재방문 유도 요소
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
    
    questions = diagnosis_questions[current_stage]
    
    with st.form(key="diagnosis_form"):
        for question in questions:
            q_id = question["id"]
            st.markdown(f"### {question['question']}")
            options = [f"{opt['value']}. {opt['text']}" for opt in question["options"]]
            default_index = 0
            if q_id in st.session_state.answers:
                selected_value = st.session_state.answers[q_id]
                option_values = [opt["value"] for opt in question["options"]]
                if selected_value in option_values:
                    default_index = option_values.index(selected_value)
            option = st.radio(
                f"현재 상태를 선택하세요:",
                options=options,
                key=f"radio_{q_id}",
                index=default_index
            )
            selected_value = option.split(".")[0]
            save_answer(q_id, selected_value)
            st.markdown("---")
        # 네비게이션 버튼
        col1, col2, col3 = st.columns([1, 1, 1])
        with col1:
            prev = st.form_submit_button("이전 단계")
        with col3:
            if current_stage == list(diagnosis_questions.keys())[-1]:
                next_ = st.form_submit_button("진단 완료")
            else:
                next_ = st.form_submit_button("다음 단계")
    # 버튼 동작
    if prev:
        prev_stage()
    if 'next_' in locals() and next_:
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
    
    # 핵심 정보만 표시
    st.markdown(f"**진단 레벨:** {diagnosis_result['level']['name']}")
    st.markdown(f"**레벨 설명:** {diagnosis_result['level']['description']}")
    
    # 각 소제목별 결과 (비어 있으면 안내문구)
    current = report_data.get("current_diagnosis", "진단 결과 생성에 실패했습니다.")
    action = report_data.get("action_plan", "진단 결과 생성에 실패했습니다.")
    upgrade = report_data.get("upgrade_tips", "진단 결과 생성에 실패했습니다.")
    full_report = f"""# 📊 현재 진단\n{current}\n\n# 🎯 액션 플랜\n{action}\n\n# 💡 업그레이드 팁\n{upgrade}"""
    
    # 복사 기능
    copy_container = st.container()
    with copy_container:
        if st.button("📋 전체 보고서 복사하기", key="copy_all", help="클릭하면 전체 보고서 내용을 복사할 수 있습니다"):
            toggle_copy()
    if st.session_state.copy_clicked:
        with copy_container:
            st.text_area("아래 내용을 선택하여 복사하세요 (Ctrl+A, Ctrl+C)", full_report, height=300)
            st.info("👆 위 텍스트를 선택하고 Ctrl+A, Ctrl+C를 눌러 복사하세요!")
            if st.button("닫기", key="close_copy"):
                toggle_copy()
    # 전체 보고서 내용을 항상 바로 아래에 출력
    st.markdown("---")
    st.markdown(full_report)
    st.markdown("## 새 진단 시작")
    if st.button("새로운 진단 시작하기"):
        reset_diagnostic()

# 메인 앱 구성
def main():
    """메인 애플리케이션 실행"""
    try:
        # 페이지 설정
        
        
        # 사이드바
        with st.sidebar:
            st.title("🔍 AI 마케팅 부스터")
            st.markdown("---")
            
            if st.session_state.page != 'welcome':
                if st.button("처음으로 돌아가기"):
                    reset_diagnostic()
            
            if st.session_state.page == 'result':
                st.markdown("### 목차")
                st.markdown("- [📊 현재 진단](#현재-진단)")
                st.markdown("- [🎯 액션 플랜](#액션-플랜)")  
                st.markdown("- [💡 업그레이드 팁](#업그레이드-팁)")
                
                # 전체 보고서 복사 버튼 (사이드바에도 추가)
                if st.button("📋 전체 보고서 복사", key="sidebar_copy"):
                    toggle_copy()
            
            st.markdown("---")
            st.markdown("### 개발자 정보")
            st.markdown("스마트 플레이스 최적화 컨설팅")
            st.markdown("연락처: stella.cholong.jung@gmail.com")
            
            st.markdown("---")
            st.markdown("© 2025 스마트 플레이스 최적화 컨설팅")
        
        # 페이지 표시
        if st.session_state.page == 'welcome':
            show_welcome_page()
        elif st.session_state.page == 'diagnostic':
            show_diagnostic_page()
        elif st.session_state.page == 'result':
            show_result_page()
            
        # 맨 밑에 고정된 복사 버튼 추가 (결과 페이지인 경우)
        if st.session_state.page == 'result' and not st.session_state.copy_clicked:
            # 고정된 위치에 복사 버튼 표시
            st.markdown(
                """
                <style>
                .floating-button {
                    position: fixed;
                    bottom: 20px;
                    right: 20px;
                    z-index: 1000;
                    border-radius: 50%;
                    width: 60px;
                    height: 60px;
                    font-size: 24px;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    background-color: #ff4b4b;
                    color: white;
                    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
                    cursor: pointer;
                    border: none;
                }
                .floating-button:hover {
                    background-color: #ff2e2e;
                }
                </style>
                
                <button class="floating-button" onclick="document.getElementById('copy_all').click()">
                    📋
                </button>
                """,
                unsafe_allow_html=True
            )
    except Exception as e:
        st.error(f"애플리케이션 실행 중 오류 발생: {e}")
# streamlit_app.py에서 vector_store 임포트 부분 수정
try:
    from utils.vector_store import VectorStore
    vector_store_available = True
except Exception as e:
    st.sidebar.error(f"VectorStore 임포트 오류: {e}")
    vector_store_available = False

try:
    from utils.rag_model import RAGModel
    rag_model_available = True
except Exception as e:
    st.sidebar.error(f"RAGModel 임포트 오류: {e}")
    rag_model_available = False 
if __name__ == "__main__":
    main()