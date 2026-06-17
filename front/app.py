import streamlit as st
import requests

# 페이지 설정 및 CSS
st.set_page_config(page_title="Balance-Pill", page_icon="💊", layout="wide")
st.markdown("""
    <style>
    /* 화면 분할 */
    [data-testid="column"]:nth-of-type(1) {
        border-right: 2px solid #E8F0E9;
        padding-right: 2rem;
    }
    [data-testid="column"]:nth-of-type(2) {
        padding-left: 2rem;
    }
    [data-testid="stWidgetLabel"] p {
        font-size: 18px !important;
        font-weight: 800 !important;
        color: #1F2E24 !important;
    }
    </style>
""", unsafe_allow_html=True)

# 통신 URL
BACKEND_URL = "http://18.207.20.190:8000/analyze"

@st.cache_data
def load_base_data():
    return {
        "symptoms": ["만성피로/수면 질 저하", "수면부족", "안구건조", "관절통증", "근육통", "면역력저하", "소화불량/변비"],
        "supplements": ["종합비타민", "비타민C", "비타민D", "비타민B", "철분", "칼슘", "마그네슘", "오메가3", "유산균", "루테인", "밀크씨슬"]
    }

base_data = load_base_data()

# 화면 분할
left_col, right_col = st.columns([1, 1.2])

# 좌측: 사용자 입력 폼
with left_col:
    st.title("💊 Balance-Pill")
    st.markdown("건강 상태와 복용 중인 영양제를 입력해주세요.")
    st.markdown("---")
    
    lifestyle_input = st.radio(
        "주요 생활 습관",
        ["해당 없음", "☀️ 야외 활동 및 햇빛 노출 부족", "🥤 커피/카페인 과다 섭취", "🍞 탄수화물 및 당류 과다 섭취", "🚬 잦은 흡연", "🍺 잦은 음주", "🏋️ 고강도 운동 취미"]
    )
    
    st.markdown("<br>", unsafe_allow_html=True)
    fatigue_input = st.slider(
        "최근 육체적 피로도 (1~10)", 
        min_value=1, max_value=10, value=5
    )
    
    st.markdown("<br>", unsafe_allow_html=True)
    selected_symptoms = st.multiselect(
        "요즘 가장 고민인 건강 증상", 
        base_data["symptoms"]
    )
    
    st.markdown("<br>", unsafe_allow_html=True)
    selected_supplements = st.pills(
        "현재 복용 중인 영양제", 
        base_data["supplements"], 
        selection_mode="multi"
    )
    
    st.markdown("<br>", unsafe_allow_html=True)
    analyze_button = st.button("분석하기", type="primary", use_container_width=True)

# 우측: 분석 결과 리포트
with right_col:
    st.title("🌿 분석 리포트")
    
    if analyze_button:
        if not selected_supplements:
            st.warning("👈 왼쪽 화면에서 응답을 먼저 진행해주세요.")
        else:
            payload = {
                "symptoms": selected_symptoms,
                "supplements": selected_supplements,
                "fatigue_level": fatigue_input,
                "lifestyle": lifestyle_input
            }
            
            try:
                # 백엔드 API 호출
                with st.spinner('영양제 조합을 분석하고 있습니다...'):
                    response = requests.post(BACKEND_URL, json=payload)
                
                if response.status_code == 200:
                    result = response.json()
                    status = result.get("status")
                    conflicts = result.get("conflicts", [])
                    synergies = result.get("synergies", [])
                    recs = result.get("recommendations", [])
                    
                    # 요약 지표 출력
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric(label="🚨 주의 조합", value=f"{len(conflicts)} 건")
                    with col2:
                        st.metric(label="✨ 시너지 조합", value=f"{len(synergies)} 건")
                    
                    st.markdown("---")
                    
                    # 종합 상태 메시지
                    if status == "danger":
                        st.error("**🚨 주의 필요**\n\n함께 복용 시 효과를 감소시키거나 주의가 필요한 조합이 있습니다.")
                    elif status == "success":
                        st.success("**✨ 완벽해요**\n\n서로의 효과를 극대화하는 훌륭한 시너지 조합이 포함되어 있습니다.")
                        st.balloons()
                    else:
                        st.info("**ℹ️ 특이사항 없음**\n\n현재 선택한 조합 간의 특별한 충돌은 발견되지 않았습니다.")
                    
                    st.markdown("<br>", unsafe_allow_html=True)
                    
                    # 결과 아코디언 메뉴
                    if conflicts:
                        st.markdown("### ❌ 주의 조합 상세")
                        for c in conflicts:
                            with st.expander(f"⚠️ **{c['combination']}**"):
                                st.write(c['reason'])
                                
                    if synergies:
                        st.markdown("### ☀️ 시너지 조합 상세")
                        for s in synergies:
                            with st.expander(f"✨ **{s['combination']}**"):
                                st.write(s['reason'])
                                
                    if recs:
                        st.markdown("### 💡 라이프스타일 맞춤 추천")
                        for r in recs:
                            st.markdown(f"#### **{r['supplement']}**")
                            st.markdown(f"{r['reason']}")
                            st.markdown("<br>", unsafe_allow_html=True)
                else:
                    st.error("백엔드 API 서버로부터 올바른 응답을 받지 못했습니다.")
                    
            except requests.exceptions.ConnectionError:
                st.error("백엔드 서버와 통신을 연결할 수 없습니다. 컨테이너 상태와 통신 IP를 확인하세요.")
    else:
        st.info("👈 왼쪽 패널에 건강 상태를 입력하고 [분석하기] 버튼을 눌러주세요.")