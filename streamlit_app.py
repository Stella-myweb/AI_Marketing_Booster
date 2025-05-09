import os
import time
import streamlit as st
import re
from datetime import datetime
from typing import Dict, List, Any

# 자체 모듈 임포트
from utils.questions import diagnosis_questions, calculate_score, suggest_improvements
from utils.vector_store import VectorStore
from utils.rag_model import RAGModel

# 설정 로드
from config import APP_TITLE, APP_DESCRIPTION

# 마크다운 특수기호 및 포맷 제거 함수
def clean_markdown(text):
    """마크다운 특수기호 및 포맷을 제거합니다."""
    if not text:
        return ""
    
    # ** 볼드체 포맷 처리
    text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)
    
    # # 제목 포맷 처리 (# 기호 제거하고 제목 텍스트 유지)
    text = re.sub(r'^# (.*?)$', r'\1', text, flags=re.MULTILINE)
    text = re.sub(r'^## (.*?)$', r'\1', text, flags=re.MULTILINE)
    text = re.sub(r'^### (.*?)$', r'\1', text, flags=re.MULTILINE)
    
    # - 목록 포맷 처리
    text = re.sub(r'^- (.*?)$', r'• \1', text, flags=re.MULTILINE)
    
    # * 목록 포맷 처리 
    text = re.sub(r'^\* (.*?)$', r'• \1', text, flags=re.MULTILINE)
    
    # → 화살표 앞뒤 공백 처리
    text = re.sub(r'→ \*(.*?)\*', r'→ \1', text)
    
    return text

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

# 함수 정의
def reset_diagnostic():
    """진단 상태를 초기화합니다."""
    st.session_state.answers = {}
    st.session_state.current_stage = list(diagnosis_questions.keys())[0]
    st.session_state.diagnosis_result = None
    st.session_state.report_data = None
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
    
    # 진단 영역 매핑
    areas_mapping = {
        "인식하게 한다": "검색 노출 최적화",
        "클릭하게 한다": "클릭율 높이는 전략",
        "머물게 한다": "체류시간 늘리는 방법",
        "연락오게 한다": "문의/예약 전환율 높이기",
        "후속 피드백 받는다": "고객 재방문 유도 전략"
    }
    
    st.markdown("### 🔍 진단 영역")
    areas_description = [
        f"- **{areas_mapping.get(key, key)}**: {description}" 
        for key, description in {
            "인식하게 한다": "키워드 설정, 상세 설명, 위치 정보 등 기본 정보 최적화",
            "클릭하게 한다": "이미지 품질, 차별점 표현, 캐치프레이즈 등 흥미 유발 요소",
            "머물게 한다": "콘텐츠 품질, 업데이트 주기, 이벤트 활용 등 체류시간 증가 요소",
            "연락오게 한다": "예약 기능, 전화 응대, 쿠폰, 전환 유도 문구 등 전환율 향상 요소",
            "후속 피드백 받는다": "리뷰 관리, 저장/알림 유도, 단골 고객 관리 등 재방문 유도 요소"
        }.items()
    ]
    
    st.markdown('\n'.join(areas_description))
    
    if st.button("진단 시작하기", type="primary"):
        st.session_state.page = 'diagnostic'

def show_diagnostic_page():
    """진단 페이지를 표시합니다."""
    # 상단 진행 상태바
    progress = get_progress()
    st.progress(progress)
    st.markdown(f"### 진행률: {progress}%")
    
    # 현재 단계 표시 - 매핑 적용
    areas_mapping = {
        "인식하게 한다": "검색 노출 최적화",
        "클릭하게 한다": "클릭율 높이는 전략",
        "머물게 한다": "체류시간 늘리는 방법", 
        "연락오게 한다": "문의/예약 전환율 높이기",
        "후속 피드백 받는다": "고객 재방문 유도 전략"
    }
    
    current_stage = st.session_state.current_stage
    mapped_stage = areas_mapping.get(current_stage, current_stage)
    st.title(f"{mapped_stage} 단계 진단")
    
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
    
    # 핵심 정보만 표시
    st.markdown(f"**진단 레벨:** {diagnosis_result['level']['name']}")
    st.markdown(f"**레벨 설명:** {diagnosis_result['level']['description']}")
    
    # 전체 보고서 내용
    full_report = f"""
{report_data.get("current_diagnosis", "")}

{report_data.get("action_plan", "")}

{report_data.get("upgrade_tips", "")}
"""
    
    # 클린 버전 (마크다운 문법 제거)
    clean_full_report = clean_markdown(full_report)
    
    # 전체 복사 버튼 (실제 복사 기능 구현)
    if st.button("📋 전체 보고서 복사하기", key="copy_all", help="클릭하면 전체 보고서 내용이 클립보드에 복사됩니다"):
        st.success("✅ 전체 보고서가 클립보드에 복사되었습니다!")
        
        # 클립보드로 복사하는 JavaScript 코드
        st.components.v1.html(
            f"""
            <textarea id="copy-content" style="position: absolute; left: -9999px;">{clean_full_report}</textarea>
            <script>
                function copyToClipboard() {{
                    const copyText = document.getElementById("copy-content");
                    copyText.select();
                    document.execCommand("copy");
                }}
                // 페이지 로드 시 자동 복사 실행
                window.onload = copyToClipboard;
            </script>
            """,
            height=0
        )
    
    # 진단 내용을 컨테이너에 담아 스크롤 가능하게 표시
    with st.container():
        # 현재 진단
        st.markdown(report_data.get("current_diagnosis", ""))
        
        # 현재 진단 복사 버튼
        if st.button("📋 현재 진단 복사", key="copy_diagnosis"):
            st.success("✅ 현재 진단 내용이 클립보드에 복사되었습니다!")
            clean_diagnosis = clean_markdown(report_data.get("current_diagnosis", ""))
            st.components.v1.html(
                f"""
                <textarea id="copy-diagnosis" style="position: absolute; left: -9999px;">{clean_diagnosis}</textarea>
                <script>
                    function copyDiagnosis() {{
                        const copyText = document.getElementById("copy-diagnosis");
                        copyText.select();
                        document.execCommand("copy");
                    }}
                    window.onload = copyDiagnosis;
                </script>
                """,
                height=0
            )
        
        st.markdown("---")
        
        # 액션 플랜
        st.markdown(report_data.get("action_plan", ""))
        
        # 액션 플랜 복사 버튼
        if st.button("📋 액션 플랜 복사", key="copy_action"):
            st.success("✅ 액션 플랜 내용이 클립보드에 복사되었습니다!")
            clean_plan = clean_markdown(report_data.get("action_plan", ""))
            st.components.v1.html(
                f"""
                <textarea id="copy-action" style="position: absolute; left: -9999px;">{clean_plan}</textarea>
                <script>
                    function copyAction() {{
                        const copyText = document.getElementById("copy-action");
                        copyText.select();
                        document.execCommand("copy");
                    }}
                    window.onload = copyAction;
                </script>
                """,
                height=0
            )
        
        st.markdown("---")
        
        # 업그레이드 팁
        st.markdown(report_data.get("upgrade_tips", ""))
        
        # 업그레이드 팁 복사 버튼
        if st.button("📋 업그레이드 팁 복사", key="copy_tips"):
            st.success("✅ 업그레이드 팁 내용이 클립보드에 복사되었습니다!")
            clean_tips = clean_markdown(report_data.get("upgrade_tips", ""))
            st.components.v1.html(
                f"""
                <textarea id="copy-tips" style="position: absolute; left: -9999px;">{clean_tips}</textarea>
                <script>
                    function copyTips() {{
                        const copyText = document.getElementById("copy-tips");
                        copyText.select();
                        document.execCommand("copy");
                    }}
                    window.onload = copyTips;
                </script>
                """,
                height=0
            )
    
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
    st.title("🔍 AI 마케팅 부스터")
    st.markdown("---")
    
    if st.session_state.page != 'welcome':
        if st.button("처음으로 돌아가기"):
            reset_diagnostic()
    
    if st.session_state.page == 'result':
        st.markdown("### 목차")
        st.markdown("- [📊 현재 진단](#-현재-진단)")
        st.markdown("- [🎯 액션 플랜](#-액션-플랜)")  
        st.markdown("- [💡 업그레이드 팁](#-업그레이드-팁)")
        
        # 사이드바
with st.sidebar:
    st.title("🔍 AI 마케팅 부스터")
    st.markdown("---")
    
    if st.session_state.page != 'welcome':
        if st.button("처음으로 돌아가기"):
            reset_diagnostic()
    
    if st.session_state.page == 'result':
        st.markdown("### 목차")
        st.markdown("- [📊 현재 진단](#-현재-진단)")
        st.markdown("- [🎯 액션 플랜](#-액션-플랜)")  
        st.markdown("- [💡 업그레이드 팁](#-업그레이드-팁)")
        
        # 전체 보고서 복사 버튼 (사이드바에도 추가)
        if st.button("📋 전체 보고서 복사", key="sidebar_copy"):
            # report_data를 세션 상태에서 가져옴
            if "report_data" in st.session_state and st.session_state.report_data:
                report_data = st.session_state.report_data
                
                # 전체 보고서 내용 준비
                current_diagnosis = report_data.get("current_diagnosis", "")
                action_plan = report_data.get("action_plan", "")
                upgrade_tips = report_data.get("upgrade_tips", "")
                
                full_report = f"{current_diagnosis}\n\n{action_plan}\n\n{upgrade_tips}"
                clean_full_report = clean_markdown(full_report)
                
                # 복사 성공 메시지 표시
                st.success("✅ 전체 보고서가 클립보드에 복사되었습니다!")
                
                # JavaScript로 클립보드에 복사
                st.components.v1.html(
                    f"""
                    <textarea id="copy-sidebar" style="position: absolute; left: -9999px;">{clean_full_report}</textarea>
                    <script>
                        function copySidebar() {{
                            const copyText = document.getElementById("copy-sidebar");
                            copyText.select();
                            document.execCommand("copy");
                        }}
                        window.onload = copySidebar;
                    </script>
                    """,
                    height=0
                )
        
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
    if st.session_state.page == 'result':
        # 전체 보고서 내용 (마크다운 문법 제거)
        full_report = f"""
{report_data.get("current_diagnosis", "")}

{report_data.get("action_plan", "")}

{report_data.get("upgrade_tips", "")}
"""
        clean_full_report = clean_markdown(full_report)
        
        # 고정된 위치에 복사 버튼 표시
        st.markdown(
            f"""
            <style>
            .floating-button {{
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
            }}
            .floating-button:hover {{
                background-color: #ff2e2e;
            }}
            .tooltip {{
                display: none;
                position: fixed;
                bottom: 90px;
                right: 20px;
                background-color: #333;
                color: white;
                padding: 5px 10px;
                border-radius: 4px;
                font-size: 12px;
                z-index: 1001;
            }}
            </style>
            
            <div id="floating-copy-button" class="floating-button" onclick="copyFloating()">📋</div>
            <div id="tooltip" class="tooltip">복사 완료!</div>
            
            <script>
            function copyFloating() {{
                // 클립보드에 텍스트 복사
                const el = document.createElement('textarea');
                el.value = `{clean_full_report}`;
                el.setAttribute('readonly', '');
                el.style.position = 'absolute';
                el.style.left = '-9999px';
                document.body.appendChild(el);
                el.select();
                document.execCommand('copy');
                document.body.removeChild(el);
                
                // 툴팁 표시
                const tooltip = document.getElementById('tooltip');
                tooltip.style.display = 'block';
                setTimeout(function() {{
                    tooltip.style.display = 'none';
                }}, 2000);
            }}
            </script>
            """,
            unsafe_allow_html=True
                )

if __name__ == "__main__":
    main()