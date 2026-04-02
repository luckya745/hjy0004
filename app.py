import streamlit as st
import google.generativeai as genai

# --- 환경 설정 및 보안 ---
try:
    GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
except (KeyError, FileNotFoundError):
    st.error("API 키를 찾을 수 없습니다. Streamlit Secrets 설정을 확인해주세요.")
    st.stop()

genai.configure(api_key=GEMINI_API_KEY)

# --- 역사 인물 데이터베이스 (페르소나 설정) ---
HISTORICAL_FIGURES = {
    "단군왕검": "고조선의 건국 시조. 홍익인간(널리 인간을 이롭게 함)의 정신을 강조하며 인자하고 신비로운 신화적 지도자의 말투를 사용하십시오.",
    "주몽 (동명성왕)": "고구려의 건국 시조. 활쏘기의 명수이자 강인한 기상을 가진 정복 군주의 말투를 사용하십시오. '천제의 아들'이라는 자부심이 느껴져야 합니다.",
    "온조": "백제의 건국 시조. 고구려를 떠나 새로운 터전을 잡은 온화하면서도 결단력 있는 개척자의 말투를 사용하십시오.",
    "박혁거세": "신라의 건국 시조. 알에서 태어난 신비로움과 밝은 빛으로 세상을 다스리는 평화로운 군주의 말투를 사용하십시오.",
    "김수로": "금관가야의 건국 시조. 철기 문화의 자부심과 바다 건너 허황옥과의 사랑을 간직한 낭만적이면서도 강력한 족장의 말투를 사용하십시오.",
    "왕건 (태조)": "고려의 건국 시조. 후삼국을 통일한 포용력과 '훈요십조'를 강조하는 지혜로운 군주의 말투를 사용하십시오. 호족들을 아우르는 부드러운 카리스마가 필요합니다.",
    "견훤": "후백제의 견훤. 용맹하고 거침없는 무장의 기질과 아들들에 대한 복잡한 심경, 고려에 대한 경쟁심이 드러나는 강한 말투를 사용하십시오.",
    "궁예": "후고구려의 궁예. 관심법을 강조하며 스스로를 미륵불이라 칭하는 위압적이고 독특한 말투를 사용하십시오. '누가 기침 소리를 내었는가'와 같은 단호함이 특징입니다.",
    "이성계 (태조)": "조선의 건국 시조. 위화도 회군을 결정한 결단력과 명궁의 실력, 새로운 나라를 세운 창업 군주의 묵직한 말투를 사용하십시오.",
    "이순신": "조선의 수군통제사. 위엄 있고 단호하며 백성을 사랑하는 충심 가득한 말투를 사용하십시오. '필사즉생 필생즉사'의 정신이 느껴져야 합니다.",
    "고종 황제": "대한제국의 초대 황제. 구한말의 혼란 속에서 근대화를 꿈꾸고 국권을 지키려 했던 고뇌하는 황제의 말투를 사용하십시오.",
    "김구": "대한민국 임시정부 주석. '나의 소원'에서 밝힌 높은 문화의 힘을 강조하며, 독립을 향한 일편단심과 인자한 '백범'의 말투를 사용하십시오."
}

# --- UI 레이아웃 ---
st.set_page_config(page_title="역사 인물 대화 AI", page_icon="📜", layout="wide")

st.title("📜 역사 인물과 나누는 대화")
st.caption("공부하고 싶은 인물을 선택하고, 그 인물과 직접 대화하며 역사를 배워보세요.")

# 사이드바에서 인물 선택
with st.sidebar:
    st.header("👤 인물 선택")
    selected_name = st.selectbox("대화하고 싶은 인물을 선택하세요:", list(HISTORICAL_FIGURES.keys()))
    
    st.divider()
    if st.button("대화 초기화"):
        st.session_state.messages = []
        st.session_state.chat_session = None
        st.rerun()

# --- 세션 상태 초기화 ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# 인물이 바뀌면 채팅 세션 초기화
if "current_figure" not in st.session_state or st.session_state.current_figure != selected_name:
    st.session_state.current_figure = selected_name
    st.session_state.messages = [] # 인물 변경 시 대화 내역 삭제 (혼란 방지)
    
    # 새로운 인물에 맞는 시스템 인스트럭션으로 모델 설정
    persona_instruction = (
        f"당신은 역사 속 인물 '{selected_name}'입니다. "
        f"다음 설명에 따라 대화하십시오: {HISTORICAL_FIGURES[selected_name]} "
        "상대방은 당신에 대해 배우고 싶어 하는 현대의 학습자입니다. "
        "당시의 시대적 배경을 바탕으로 고풍스러운 말투를 사용하되, 내용은 유익해야 합니다."
    )
    
    st.session_state.model = genai.GenerativeModel(
        model_name="gemini-1.5-flash",
        system_instruction=persona_instruction
    )
    st.session_state.chat_session = st.session_state.model.start_chat(history=[])

# --- 채팅 화면 구현 ---
st.subheader(f"✨ {selected_name}님과의 대화")

# 기존 대화 표시
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 사용자 입력 처리
if prompt := st.chat_input(f"{selected_name}님께 질문해보세요."):
    # 사용자 메시지 표시
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    try:
        # AI 응답 생성
        response = st.session_state.chat_session.send_message(prompt)
        ai_response = response.text

        # AI 메시지 표시
        with st.chat_message("assistant"):
            st.markdown(ai_response)
        st.session_state.messages.append({"role": "assistant", "content": ai_response})
        
    except Exception as e:
        st.error(f"대화 중 오류가 발생했습니다: {e}")
