import streamlit as st
import pandas as pd
import os
from io import BytesIO

# --- 1. 초기 설정 및 모바일 최적화 스타일 ---
st.set_page_config(page_title="두류 랭킹 관리 시스템", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;700;900&display=swap');
    * { font-family: 'Noto Sans KR', sans-serif; text-align: center; }
    .stApp { background-color: #F8FDF9; }
    .main-header { background: linear-gradient(135deg, #007A33, #00A343); color: white; padding: 1.2rem; border-radius: 15px; margin-bottom: 1.5rem; font-weight: 900; }
    /* 카드 UI */
    .match-card { background: white; border-radius: 15px; padding: 15px; border: 1px solid #E0E0E0; box-shadow: 0 4px 6px rgba(0,0,0,0.05); margin-bottom: 10px; }
    .team-box { display: inline-block; width: 42%; vertical-align: middle; padding: 8px; background: #F1F8E9; border-radius: 8px; font-weight: 700; color: #2E7D32; font-size: 0.9rem; }
    .vs-badge { display: inline-block; width: 12%; color: #FF5252; font-weight: 900; font-size: 1rem; }
    /* 매트릭스 셀 */
    .matrix-self { background-color: #EEEEEE !important; }
</style>
""", unsafe_allow_html=True)

# --- 2. 안전한 데이터 로드 로직 (KeyError 방지) ---
DB_FILE = "tennis_members.csv"

def load_data():
    if os.path.exists(DB_FILE):
        try:
            df = pd.read_csv(DB_FILE)
            if '이름' not in df.columns: return create_default_df()[cite: 1]
            return df
        except: return create_default_df()
    return create_default_df()

def create_default_df():
    return pd.DataFrame({
        "랭킹": range(1, 9), "이름": [f"회원{i}" for i in range(1, 9)],
        "현재포인트": [100]*8, "이전포인트": [100]*8,
        "결과": ["-"]*8, "부과점": [0]*8, "그룹": ["A"]*8, "비고": [""]*8
    })[cite: 1]

# --- 3. 세션 상태 관리 ---
if 'admin_mode' not in st.session_state: st.session_state.admin_mode = False
if 'tour_name' not in st.session_state: st.session_state.tour_name = "두류 정기전"
if 'groups_config' not in st.session_state:
    st.session_state.groups_config = [{"name": "A그룹", "type": "KDK", "games": 4, "players": [f"회원{i}" for i in range(1, 9)]}]

# --- 4. 메뉴 구성 (요청하신 5개 메뉴) ---
menu = st.sidebar.radio("메뉴 선택", ["1. 두류 랭킹", "2. 대진 및 경기 현황", "3. 경기 결과 및 점수 확인", "4. 지난 대회 아카이브", "5. 관리자 페이지"])

# --- [1번 메뉴: 두류 랭킹] ---
if menu == "1. 두류 랭킹":
    st.markdown("<div class='main-header'>🏆 두류 랭킹</div>", unsafe_allow_html=True)
    df = load_data()
    st.dataframe(df, use_container_width=True, hide_index=True)[cite: 1]
    
    col1, col2 = st.columns(2)
    with col1:
        output = BytesIO()
        df.to_excel(output, index=False)
        st.download_button("📥 랭킹 엑셀 다운로드", output.getvalue(), "duryu_ranking.xlsx")
    with col2:
        st.file_uploader("📤 엑셀 업로드 (랭킹 갱신)", type=['xlsx'])

# --- [2번 메뉴: 대진 및 경기 현황] ---
elif menu == "2. 대진 및 경기 현황":
    st.markdown(f"<div class='main-header'>{st.session_state.tour_name}</div>", unsafe_allow_html=True)
    
    tabs = st.tabs([g['name'] for g in st.session_state.groups_config])
    for idx, tab in enumerate(tabs):
        conf = st.session_state.groups_config[idx]
        with tab:
            # 상단: 매트릭스 & 결과표 배치
            m1, m2 = st.columns([1, 1])
            with m1:
                st.caption("📊 조별 매트릭스")
                names = conf['players']
                if names:
                    m_df = pd.DataFrame("-", index=names, columns=names)
                    for n in names: m_df.loc[n, n] = "X"
                    st.table(m_df.style.applymap(lambda v: 'background-color: #EEEEEE; color: #EEEEEE' if v == 'X' else ''))
            with m2:
                st.caption("🏆 현재 순위")
                st.table(pd.DataFrame({"이름": names, "승점": [0]*len(names)}))
            
            st.divider()
            
            # 하단: 카드 UI 대진표
            st.subheader(f"🎾 {conf['name']} 경기 대진")
            # 샘플 대진 (8명 KDK 기준 일부)
            sample_matches = [((names[0], names[1]), (names[2], names[3])), ((names[4], names[5]), (names[6], names[7]))]
            for m_idx, (t1, t2) in enumerate(sample_matches):
                st.markdown(f"""
                <div class='match-card'>
                    <div style='color: #888; font-size: 0.7rem;'>ROUND {m_idx+1}</div>
                    <div class='team-box'>{t1[0]} / {t1[1]}</div>
                    <div class='vs-badge'>VS</div>
                    <div class='team-box'>{t2[0]} / {t2[1]}</div>
                </div>
                """, unsafe_allow_html=True)
                c1, c2 = st.columns(2)
                c1.number_input("점수", 0, 10, key=f"s1_{idx}_{m_idx}", label_visibility="collapsed")
                c2.number_input("점수", 0, 10, key=f"s2_{idx}_{m_idx}", label_visibility="collapsed")

# --- [3번 메뉴: 경기 결과 및 점수 확인] ---
elif menu == "3. 경기 결과 및 점수 확인":
    st.markdown("<div class='main-header'>🏁 경기 결과 및 부과점</div>", unsafe_allow_html=True)
    st.write("그룹별 순위에 따른 부과점(7, 5, 3, 1점)이 자동 계산됩니다.")[cite: 1]

# --- [4번 메뉴: 지난 대회 아카이브] ---
elif menu == "4. 지난 대회 아카이브":
    st.markdown("<div class='main-header'>📂 대회 기록 보관소</div>", unsafe_allow_html=True)
    st.selectbox("과거 대회 선택", ["2026-04 정기전", "2026-03 챌린지"])

# --- [5번 메뉴: 관리자 페이지] ---
elif menu == "5. 관리자 페이지":
    st.markdown("<div class='main-header'>⚙️ 대회 운영 관리</div>", unsafe_allow_html=True)
    pw = st.text_input("관리자 비밀번호", type="password")
    if pw == "0502":[cite: 1]
        st.session_state.admin_mode = True
        
        # 대회 기본 설정
        st.session_state.tour_name = st.text_input("대회 이름 수정", st.session_state.tour_name)
        
        # 참여자 관리
        st.subheader("👥 참여자 명단 수정 및 체크")
        df = load_data()
        all_names = df['이름'].tolist()[cite: 1]
        
        new_names = st.text_area("회원 이름 수정 (쉼표 구분)", ", ".join(all_names))
        
        st.write("✅ 오늘 참가자 선택 (체크박스)")
        cols = st.columns(4)
        active_p = [name for i, name in enumerate(all_names) if cols[i%4].checkbox(name, value=True, key=f"p_{name}")]
        
        st.divider()
        
        # 그룹 자유 설정
        st.subheader("📝 그룹별 대진 설정")
        g_num = st.number_input("그룹 수", 1, 10, 1)
        new_groups = []
        for i in range(int(g_num)):
            with st.expander(f"📍 그룹 {i+1} 상세 설정"):
                gn = st.text_input("그룹명", f"{chr(65+i)}그룹", key=f"gn_{i}")
                gt = st.selectbox("방식", ["고정페어", "KDK", "단식"], key=f"gt_{i}")
                gg = st.selectbox("1인당 게임 수", [3, 4], key=f"gg_{i}")
                gp = st.multiselect("참가자 배정", active_p, key=f"gp_{i}")
                new_groups.append({"name": gn, "type": gt, "games": gg, "players": gp})
        
        if st.button("🎲 대진표 최종 생성"):
            st.session_state.groups_config = new_groups
            st.success("대진표 생성이 완료되었습니다!")
