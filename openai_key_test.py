import streamlit as st
import openai
import os

st.set_page_config(page_title="OpenAI API 키 테스트", page_icon="🤖")

st.title("🔑 OpenAI API Key 테스트 페이지")

# 1. API 키 입력 (직접 입력 or 환경변수 사용)
api_key = st.text_input("OpenAI API Key를 입력하세요:", type="password", value=os.getenv("OPENAI_API_KEY", ""))

if st.button("API 키로 테스트"):
    if not api_key or not api_key.startswith("sk-"):
        st.error("유효한 OpenAI API 키를 입력하세요.")
    else:
        openai.api_key = api_key
        try:
            with st.spinner("OpenAI API 키를 테스트 중입니다..."):
                # 최신 openai 패키지에서는 실제 채팅 호출로 테스트
                response = openai.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": "Hello, are you working?"}]
                )
                st.success("✅ API 키가 정상적으로 작동합니다!")
                st.write("모델 응답 예시:", response.choices[0].message.content)
        except Exception as e:
            st.error(f"❌ API 키 오류 또는 네트워크 문제: {e}")

st.markdown("---")
st.info("이 페이지는 OpenAI API 키가 정상적으로 동작하는지 확인하는 테스트용입니다.")