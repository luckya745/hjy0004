import streamlit as st
import google.generativeai as genai

# --- 1. 환경 설정 및 보안 (Secrets 활용) ---
# 이 부분은 소스 코드에 키를 노출하지 않고 금고(Secrets)에서 꺼내오는 역할을 합니다.
try:
    # Streamlit Secrets에서 API 키 로드
    GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=GEMINI_API_KEY)
except (KeyError, FileNotFoundError):
    st.error("⚠️ API 키를 찾을 수 없습니다. '.streamlit/secrets.toml' 파일이나 Streamlit Cloud의 Secrets 설정을 확인해주세요.")
    st.stop()

# --- 2. 역사 인물 데이터베이스 ---
HISTORICAL_FIGURES = {
    "단군왕검": "고조선의 건국 시조. 홍익인간의 정신을 강조하며 인자하고 신비로운 신화적 지도자의 말투를 사용하십시오.",
    "주몽 (동명성왕)": "고구려의 건국 시조. 활쏘기의 명수이자 강인한 기상을 가진 정복 군주의 말투를 사용하십시오.",
    "온조": "백제의 건국 시조. 온화하면서도 결단력 있는 개척자의 말투를 사용하십시오.",
    "박혁거세": "신라의 건국 시조. 알에서 태어난 신비로움과 평화로운 군주의 말투를 사용하십시오.",
    "김수로": "금관가야의 건국 시조. 철기 문화의 자부심과 강력한 족장의 말투를 사용하십시오.",
    "왕건 (태조)": "고려의 건국 시조. 포용력과 지혜로운 군주의 말투를 사용하십시오.",
    "견훤": "후백제의 견훤. 용맹하고 거침없는 무장의 기질이 드러나는 강한 말투를 사용하십시오.",
    "궁예": "후고구려의 궁예. 관심법을 강조하며 스스로를 미륵불이라 칭하는 위압적인 말투를 사용하십시오.",
    "이성계 (태조)": "조선의 건국 시조. 결단력 있는 창업 군주의 묵직한 말투를 사용하십시오.",
    "이순신": "조선의 수군통제사. 위엄 있고 단호하며 백성을 사랑하는 충심 가득한 말투를 사용하십시오.",
    "고종 황제": "대한제국의 초대 황제. 구한말의 혼란 속에서 고뇌하는 황제의 말투를 사용하십시오.",
    "김구": "대한민국 임시정부 주석. 독립을 향한 의지와 인자한 '백범'의 말투를 사용하십시오."
}

# --- 3. UI 레이아웃 설정 ---
st.set_page_config(page_title="역사 인물 대화 AI", page_icon="📜", layout="wide")

st.title("📜 역사 인물과 나누는 대화")
st.caption("안전하게 설정된 API 키를 사용하여 역사 속 인물과 대화합니다.")

# 사이드바: 인물 선택 및 관리
with st.sidebar:
    st.header("👤 인물 선택")
    selected_name = st.selectbox("대화하고 싶은 인물을 선택하세요:", list(HISTORICAL_FIGURES.keys()))
    
    st.divider()
    if st.button("대화 초기화", use_container_width=True):
        st.session_state.messages = []
        st.session_state.chat_session = None
        st.rerun()
    
    st.info("💡 API 키는 Streamlit Secrets를 통해 안전하게 보호되고 있습니다.")

# --- 4. 세션 상태 관리 (인물 변경 감지 및 초기화) ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# 인물이 바뀌면 대화 내용과 세션을 초기화합니다.
if "current_figure" not in st.session_state or st.session_state.current_figure != selected_name:
    st.session_state.current_figure = selected_name
    st.session_state.messages = [] 
    
    # 선택된 인물에 맞춘 시스템 명령(Persona) 생성
    persona_instruction = (
        f"당신은 역사 속 인물 '{selected_name}'입니다. "
        f"다음 설명에 따라 대화하십시오: {HISTORICAL_FIGURES[selected_name]} "
        "상대방은 당신에 대해 배우고 싶어 하는 현대의 학습자입니다. "
        "고풍스러운 말투를 사용하되 지식을 친절하게 전달하십시오."
    )
    
    # 모델 인스턴스 생성
    st.session_state.model = genai.GenerativeModel(
        model_name="gemini-2.5-flash-lite",
        system_instruction=persona_instruction
    )
    # 채팅 세션 시작
    st.session_state.chat_session = st.session_state.model.start_chat(history=[])

# --- 5. 채팅 화면 구현 ---
st.subheader(f"✨ {selected_name}님과의 대화")

# 기존 대화 표시
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 사용자 입력 처리
if prompt := st.chat_input(f"{selected_name}님께 궁금한 점을 여쭤보세요."):
    # 사용자 메시지 화면 표시 및 저장
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    try:
        # Gemini API를 통해 응답 생성
        response = st.session_state.chat_session.send_message(prompt)
        ai_response = response.text

        # AI 메시지 화면 표시 및 저장
        with st.chat_message("assistant"):
            st.markdown(ai_response)
        st.session_state.messages.append({"role": "assistant", "content": ai_response})
        
    except Exception as e:
        st.error(f"대화 중 오류가 발생했습니다. API 키 권한이나 네트워크를 확인해주세요. 상세오류: {e}")
