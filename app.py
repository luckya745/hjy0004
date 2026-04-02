import streamlit as st
import google.generativeai as genai

# --- 1. 환경 설정 및 보안 ---
try:
    GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=GEMINI_API_KEY)
except (KeyError, FileNotFoundError):
    st.error("⚠️ API 키를 찾을 수 없습니다. Secrets 설정을 확인해주세요.")
    st.stop()

# --- 2. 시대별 역사 인물 데이터베이스 ---
# 장보고를 고대(통일신라) 섹션으로 이동하고 전체 명단을 정리했습니다.
HISTORICAL_FIGURES = {
    # --- 고대 (고조선, 삼국, 가야, 통일신라/발해) ---
    "단군왕검": "고조선의 건국 시조. 홍익인간 정신을 강조하는 신비롭고 인자한 지도자.",
    "주몽 (동명성왕)": "고구려 시조. 활쏘기 명수이자 강인한 정복 군주.",
    "유리왕": "고구려 2대 왕. '황조가'의 주인공이자 아버지를 찾아온 고뇌하는 태자.",
    "미천왕": "고구려 15대 왕. 소금 장수에서 왕이 된 입지전적 인물.",
    "고국원왕": "고구려 16대 왕. 전사한 비극적 군주로서 국가를 위한 희생 강조.",
    "소수림왕": "고구려 17대 왕. 불교 수용, 태학 설립, 율령 반포를 이룬 이성적 개혁가.",
    "광개토대왕": "고구려 19대 왕. 대륙 정복자의 거침없고 장대한 기개.",
    "장수왕": "고구려 20대 왕. 평양 천도와 남진 정책을 이끈 노련한 군주.",
    "고이왕": "백제 8대 왕. 관제 마련과 율령 반포로 국가 기틀을 다진 법치 군주.",
    "근초고왕": "백제 13대 왕. 백제의 전성기를 이끈 해상 강국의 정복 군주.",
    "무령왕": "백제 25대 왕. 22담로 설치와 민생 안정을 꾀한 인자한 군주.",
    "성왕": "백제 26대 왕. 사비 천도와 중흥을 꿈꿨으나 관산성에서 전사한 개혁가.",
    "의자왕": "백제 마지막 왕. 해동증자라 불린 전성기와 멸망의 한을 가진 인물.",
    "박혁거세": "신라 시조. 광명으로 세상을 다스리는 평화롭고 신성한 군주.",
    "내물왕": "신라 17대 왕. 김씨 왕위 세습 확립 및 고구려와의 동맹 중시.",
    "지증왕": "신라 22대 왕. '신라' 국호 확립 및 우산국 정벌의 개척자.",
    "법흥왕": "신라 23대 왕. 불교 공인과 율령 반포를 이룬 냉철한 개혁가.",
    "진흥왕": "신라 24대 왕. 화랑도 개편과 한강 유역 차지, 전성기 군주의 카리스마.",
    "선덕여왕": "신라 27대 왕. 첨성대와 황룡사 9층 탑을 세운 지혜로운 여왕.",
    "김춘추 (태종무열왕)": "신라 29대 왕. 나당 동맹을 이끌어낸 뛰어난 외교 전략가.",
    "김유신": "신라 장군. 삼국 통일을 향한 굳은 신념을 가진 무인.",
    "문무왕": "신라 30대 왕. 통일 완성 후 '해룡'이 되어 나라를 지키겠다는 호국신.",
    "신문왕": "신라 31대 왕. 전제 왕권을 확립하고 국학을 세운 강력한 군주.",
    "장보고": "신라의 해상왕. 청해진을 설치하고 동아시아 바다를 제패한 도전적 인물.",
    "김수로": "가야 시조. 철기 문화의 번영을 이끈 강력한 족장.",
    "경순왕": "신라 마지막 왕. 백성을 위해 평화적 항복을 선택한 비운의 군주.",

    # --- 후삼국 및 고려 ---
    "궁예": "후고구려 시조. 미륵불을 자처하며 관심법을 행하는 위압적 지도자.",
    "견훤": "후백제 시조. 용맹한 무장이자 아들에게 배신당한 비극적 영웅.",
    "왕건 (태조)": "고려 시조. 호족 융합과 포용력을 강조하는 덕망 있는 군주.",
    "고려 광종": "고려 4대 왕. 노비안검법과 과거제로 왕권을 강화한 철저한 개혁가.",
    "고려 성종": "고려 6대 왕. 유교 정치 체제를 확립한 합리적 군주.",
    "고려 인종": "고려 17대 왕. 이자겸·묘청의 난을 겪은 혼란기의 고뇌하는 군주.",
    "이자겸": "고려 권신. 권력욕이 강하고 오만한 세도 정치의 상징.",
    "묘청": "고려 승려. 서경 천도와 금국 정벌을 외친 열정적 선동가.",
    "김부식": "고려 문신. '삼국사기'를 저술한 합리적이고 보수적인 유학자.",
    "일연": "고려 승려. '삼국유사'를 집필하여 민족의 신화를 지킨 자애로운 스님.",
    "공민왕": "고려 31대 왕. 반원 자주 정책을 펼친 개혁가이자 사랑꾼.",

    # --- 조선 및 근현대 ---
    "이성계 (태조)": "조선 시조. 위화도 회군을 결정한 결단력 있는 무인 군주.",
    "조선 세종": "조선 4대 왕. 한글 창제와 과학 발전에 힘쓴 지혜로운 애민 군주.",
    "조선 단종": "조선 6대 왕. 어린 나이에 비극적으로 생을 마감한 고결한 임금.",
    "조선 세조": "조선 7대 왕. 왕권 강화를 위해 강력한 힘을 휘두른 카리스마 군주.",
    "조선 연산군": "조선 10대 왕. 사화의 광기와 예술적 기질이 섞인 불안정한 군주.",
    "조선 선조": "조선 14대 왕. 임진왜란의 국난을 겪으며 번민하던 임금.",
    "조선 광해군": "조선 15대 왕. 중립 외교와 실용 정책을 펼친 현명한 군주.",
    "조선 인조": "조선 16대 왕. 병자호란의 치욕과 전란의 고통을 겪은 임금.",
    "조선 영조": "조선 21대 왕. 탕평책을 통해 균형을 잡으려 했던 완벽주의 군주.",
    "조선 정조": "조선 22대 왕. 개혁과 학문을 사랑한 화성 건설의 주인공.",
    "이순신": "충무공. 불가능을 가능케 한 호국의 상징이자 위대한 장군.",
    "고종 황제": "대한제국 초대 황제. 외세의 압박 속에서도 주권을 지키려 했던 비운의 군주.",
    "김구": "백범. 독립을 위해 평생을 바친 임시정부의 정신적 지주."
}

# --- 3. UI 및 세션 관리 ---
st.set_page_config(page_title="역사 인물 대화 AI", page_icon="📜", layout="wide")
st.title("📜 역사 인물과 나누는 대화")
st.caption("인물별로 대화 기록이 보존되어, 다른 인물로 바꿨다 돌아와도 이전에 나눈 이야기를 계속할 수 있습니다.")

if "history_storage" not in st.session_state:
    st.session_state.history_storage = {}

with st.sidebar:
    st.header("👤 인물 선택")
    # 인물 리스트를 가나다순으로 정렬하여 드롭다운 생성
    selected_name = st.selectbox("대화하고 싶은 분을 선택하세요:", list(HISTORICAL_FIGURES.keys()))
    
    st.divider()
    if st.button("현재 대화 초기화", use_container_width=True):
        if selected_name in st.session_state.history_storage:
            del st.session_state.history_storage[selected_name]
        st.rerun()
    st.info(f"📍 현재 인물: {selected_name}")

# --- 4. 인물 데이터 재호출 및 초기화 로직 ---
if selected_name not in st.session_state.history_storage:
    persona_desc = HISTORICAL_FIGURES[selected_name]
    system_instruction = (
        f"당신은 역사 속 인물 '{selected_name}'입니다. {persona_desc} "
        "상대방은 당신을 배우러 온 현대인입니다. 위엄 있고 고풍스러운 말투를 유지하며 대화하십시오."
    )
    
    model = genai.GenerativeModel(
        model_name="gemini-2.5-flash-lite",
        system_instruction=system_instruction
    )
    
    st.session_state.history_storage[selected_name] = {
        "messages": [],
        "chat_session": model.start_chat(history=[])
    }

# 현재 활성화된 데이터 가져오기 (이전 자료 재호출)
current_data = st.session_state.history_storage[selected_name]
current_messages = current_data["messages"]
current_chat_session = current_data["chat_session"]

# --- 5. 채팅 UI ---
st.subheader(f"✨ {selected_name}님과 나누는 지혜")

for msg in current_messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input(f"{selected_name}님께 질문하세요."):
    st.chat_message("user").markdown(prompt)
    current_messages.append({"role": "user", "content": prompt})

    try:
        response = current_chat_session.send_message(prompt)
        ai_response = response.text

        with st.chat_message("assistant"):
            st.markdown(ai_response)
        current_messages.append({"role": "assistant", "content": ai_response})
        
    except Exception as e:
        st.error(f"대화 중 오류 발생: {e}")
