import streamlit as st
import requests
import pandas as pd
import google.generativeai as genai

# --- 환경 설정 및 보안 ---
# Streamlit Cloud 배포 시 설정 메뉴의 Secrets에 키를 입력해야 합니다.
# 로컬 실행 시에는 .streamlit/secrets.toml 파일을 생성하세요.
try:
    SCHOOL_API_KEY = st.secrets["SCHOOL_API_KEY"]
    GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
except (KeyError, FileNotFoundError):
    st.error("API 키를 찾을 수 없습니다. Secrets 설정을 확인해주세요.")
    st.stop()

# Gemini 설정 (최신 안정화 모델 사용)
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-2.5-flash') # 2.5 대신 현재 안정 버전인 1.5 사용 권장

# 세션 상태 초기화
if 'school_data' not in st.session_state:
    st.session_state.school_data = None
if 'analysis_report' not in st.session_state:
    st.session_state.analysis_report = None

# --- 함수 정의 ---
def get_school_info(school_name):
    """학교알리미 API를 호출하여 학교 기본 정보를 가져옵니다."""
    url = "https://www.schoolinfo.go.kr/openApi/api/school/baseInfo.do"
    params = {
        'apiKey': SCHOOL_API_KEY,
        's_schul_nm': school_name,
        'format': 'json'
    }

    try:
        response = requests.get(url, params=params, timeout=10)
        res_data = response.json()
        
        # 실제 데이터 구조에 맞게 파싱 (예시: 첫 번째 검색 결과 반환)
        if 'list' in res_data and len(res_data['list']) > 0:
            info = res_data['list'][0]
            # API 반환 필드명에 맞춰 수정이 필요할 수 있습니다.
            return {
                "name": info.get("SCHUL_NM", school_name),
                "address": info.get("ADRES", "정보 없음"),
                "total_students": info.get("USER_CON_3", "0"), # 예시 필드명
                "teacher_count": info.get("USER_CON_5", "0"),
                "found_date": info.get("FOND_DE", "정보 없음"),
                "raw_data": info # AI 분석용 전체 데이터
            }
        else:
            st.warning("검색된 학교가 없습니다.")
            return None
    except Exception as e:
        st.error(f"데이터 수집 중 오류 발생: {e}")
        return None

def analyze_school(data):
    """Gemini를 이용한 SWOT 분석 및 컨설팅 전략 생성"""
    prompt = f"""
    당신은 교육 행정 전문가이자 학교 컨설턴트입니다. 
    다음 학교 데이터를 바탕으로 상세한 SWOT 분석과 학교 발전 전략을 제안하세요.
    
    [학교 데이터]
    {data}
    
    [요구사항]
    1. 강점(S), 약점(W), 기회(O), 위협(T)을 구체적으로 분석할 것.
    2. 데이터 기반의 실무적인 교육과정 개선안을 제안할 것.
    3. 가독성을 위해 마크다운 형식으로 작성할 것.
    """
    response = model.generate_content(prompt)
    return response.text

# --- UI 레이아웃 ---
st.set_page_config(page_title="스쿨 인사이트 AI", layout="wide", page_icon="🏫")

st.title("🏫 스쿨 인사이트 AI")
st.caption("학교 알리미 데이터 기반 AI 심층 컨설팅 리포트")

# 사이드바: 검색 및 설정
with st.sidebar:
    st.header("🔍 학교 검색")
    target = st.text_input("분석할 학교명을 입력하세요", placeholder="예: 신광중학교")
    
    if st.button("데이터 수집 시작", use_container_width=True):
        if target:
            with st.spinner("학교 정보를 불러오는 중..."):
                result = get_school_info(target)
                if result:
                    st.session_state.school_data = result
                    st.session_state.analysis_report = None # 새로운 검색 시 이전 분석 삭제
                    st.success("데이터 로드 완료!")
        else:
            st.warning("학교명을 입력해 주세요.")

# 메인 화면: 데이터 표시 및 분석
if st.session_state.school_data:
    data = st.session_state.school_data
    
    # 1. 학교 기본 정보 대시보드
    st.subheader(f"📊 {data['name']} 핵심 지표")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("설립일", data['found_date'])
    with col2:
        st.metric("주소", data['address'][:15] + "...")
    with col3:
        st.info(f"💡 학교 기본 정보를 성공적으로 수집했습니다.")

    st.divider()

    # 2. AI 분석 실행 섹션
    if st.button("🚀 AI 전문가 심층 분석 실행", type="primary"):
        with st.spinner("전문가 AI가 데이터를 분석하고 있습니다..."):
            report = analyze_school(data['raw_data'])
            st.session_state.analysis_report = report

    # 3. 분석 결과 출력
    if st.session_state.analysis_report:
        st.markdown("---")
        st.markdown("### 📝 AI 컨설팅 리포트")
        st.markdown(st.session_state.analysis_report)
        
        # 리포트 다운로드 기능
        st.download_button(
            label="📄 리포트 파일로 저장 (TXT)",
            data=st.session_state.analysis_report,
            file_name=f"{data['name']}_컨설팅_리포트.txt",
            mime="text/plain"
        )
else:
    st.info("왼쪽 사이드바에서 학교명을 입력하고 '데이터 수집 시작'을 눌러주세요.")
