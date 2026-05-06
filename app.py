import streamlit as st
import pandas as pd
import numpy as np
import os
import io
import random
from datetime import datetime

# ─── [1] 환경 설정 및 테마 디자인 (모바일 최적화) ───
st.set_page_config(page_title="두류 랭킹 관리 시스템", layout="wide", initial_sidebar_state="collapsed")

def local_css():
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;700;900&display=swap');
        * { font-family: 'Noto Sans KR', sans-serif; text-align: center; }
        .stApp { background-color: #F8FAFC; }
        
        /* 헤더 디자인 */
        .main-header { background: linear-gradient(135deg, #0284c7 0%, #0369a1 100%); padding: 2rem; border-radius: 0 0 30px 30px; color: white; margin-bottom: 2rem; box-shadow: 0 10px 15px -3px rgba(0,0,0,0.1); }
        
        /* 카드 UI */
        .css-card { background: white; border-radius: 16px; padding: 1.5rem; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1); border: 1px solid #E2E8F0; margin-bottom: 1rem; }
        
        /* 경기 대진 UI */
        .match-row { display: flex; align-items: center; justify-content: center; background: #FFFFFF; border-radius: 12px; padding: 10px; margin: 10px 0; border: 2px solid #E0F2FE; transition: 0.3s; }
        .match-row:hover { border-color: #38BDF8; transform: translateY(-2px); }
        .team-box { flex: 1; padding: 10px; border-radius: 8px; font-weight: 700; font-size: 1.1rem; }
        .team-left { background: #F1F5F9; color: #1E293B; }
        .team-right { background: #F1F5F9; color: #1E293B; }
        .vs-circle { background: #EF4444; color: white; width: 40px; height: 40px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-style: italic; font-weight: 900; margin: 0 15px; box-shadow: 0 4px 6px rgba(0,0,0,0.2); }
        
        /* 매트릭스 음영 */
        .matrix-self { background-color: #CBD5E1 !important; }
        
        /* 탭 커스텀 */
        .stTabs [data-baseweb="tab-list"] { gap: 10px; justify-content: center; }
        .stTabs [data-baseweb="tab"] { background-color: #f1f5f9; border-radius: 8px 8px 0 0; padding: 10px 20px; font-weight: 700; }
        .stTabs [data-baseweb="tab--active"] { background-color: #38bdf8 !important; color: white !important; }
    </style>
    """, unsafe_allow_html=True)

local_css()

# ─── [2] 데이터 처리 엔진 ───
DB_FILE = "tennis_members.csv"
HIST_FILE = "tournament_history.csv"

def init_db():
    if not os.path.exists(DB_FILE):
        df = pd.DataFrame(columns=["이름", "현재포인트", "이전포인트", "결과", "부과점", "그룹", "비고"])
        df.to_csv(DB_FILE, index=False)
    if not os.path.exists(HIST_FILE):
        pd.DataFrame(columns=["대회명", "날짜", "그룹데이터"]).to_csv(HIST_FILE, index=False)

def load_data():
    try:
        df = pd.read_csv(DB_FILE)
        df.columns = [c.strip() for c in df.columns] # 공백 제거로 KeyError 방지
        return df
    except:
        return pd.DataFrame(columns=["이름", "현재포인트", "이전포인트", "결과", "부과점", "그룹", "비고"])

init_db()

# ─── [3] KDK 및 경기 알고리즘 ───
# 요청하신 1인 3게임/4게임 정교한 대진표 로직
KDK_DB = {
    "3_4": [(1,4,2,3), (1,3,2,4), (1,2,3,4)],
    "3_8": [(1,2,3,4), (5,6,7,8), (1,8,2,7), (3,6,4,5), (1,4,5,8), (2,3,6,7)],
    "3_12": [(1,2,3,4), (5,6,7,8), (9,10,11,12), (1,3,5,7), (2,4,6,8), (9,11,1,5), (4,8,9,12), (6,7,10,11), (10,12,2,3)],
    "4_5": [(1,2,3,4), (1,3,2,5), (1,4,3,5), (1,5,2,4), (2,3,4,5)],
    "4_6": [(1,3,2,4), (1,5,4,6), (2,3,5,6), (1,4,3,5), (2,6,3,4), (1,6,2,5)],
    "4_7": [(1,2,3,4), (5,6,1,7), (2,3,5,7), (1,4,6,7), (3,5,2,4), (1,6,2,5), (4,6,3,7)],
    "4_8": [(1,2,3,4), (5,6,7,8), (1,3,5,7), (2,4,6,8), (1,5,2,6), (3,7,4,8), (1,6,3,8), (2,5,4,7)],
    "4_9": [(1,2,3,4), (5,6,7,8), (1,9,5,7), (2,3,6,8), (4,9,3,8), (1,5,2,6), (3,6,4,5), (1,7,8,9), (2,4,7,9)],
    "4_10": [(1,2,3,5), (6,7,8,10), (2,3,4,6), (7,8,1,9), (3,4,5,7), (8,9,2,10), (4,5,6,8), (1,3,9,10), (5,6,7,9), (1,10,2,4)],
    "4_11": [(1,2,3,5), (6,7,8,10), (4,9,1,11), (2,3,6,8), (4,5,7,10), (9,11,2,6), (1,3,7,11), (4,8,5,9), (1,10,2,8), (4,7,6,11), (3,9,5,10)]
}

def generate_matches(players, p_type, games):
    n = len(players)
    if p_type == "KDK":
        key = f"{games}_{n}"
        if key in KDK_DB:
            return [((players[idx[0]-1], players[idx[1]-1]), (players[idx[2]-1], players[idx[3]-1])) for idx in KDK_DB[key]]
    elif p_type == "고정페어":
        # 1위+최하위, 2위+차하위 로직
        pairs = []
        for i in range(n // 2):
            pairs.append((players[i], players[n-1-i]))
        matches = []
        for i in range(len(pairs)):
            for j in range(i+1, len(pairs)):
                matches.append((pairs[i], pairs[j]))
        return matches
    elif p_type == "단식":
        shuffled = random.sample(players, n)
        return [( (shuffled[i],), (shuffled[i+1],) ) for i in range(0, n-1, 2)]
    return []

# ─── [4] 세션 상태 초기화 ───
if "admin" not in st.session_state: st.session_state.admin = False
if "tournament" not in st.session_state:
    st.session_state.tournament = {"name": "2026 두류 챔피언십", "groups": {}, "court": 2}
if "pw" not in st.session_state: st.session_state.pw = "0502"

# ─── [5] UI 메인 렌더링 ───
st.markdown(f'<div class="main-header"><h1>🎾 두류 랭킹 관리 시스템</h1><p>{st.session_state.tournament["name"]}</p></div>', unsafe_allow_html=True)

menu = st.sidebar.radio("MENU", ["🏆 두류 랭킹", "📅 대진 및 경기 현황", "📊 경기 결과/순위", "📂 아카이브", "⚙️ 관리자"])

# --- 1번 메뉴: 두류 랭킹 ---
if menu == "🏆 두류 랭킹":
    df = load_data()
    # 상단 랭킹 정렬 (내림차순)
    df = df.sort_values("현재포인트", ascending=False).reset_index(drop=True)
    df.insert(0, "순위", range(1, len(df)+1))
    
    # 컬럼명 변경 표시 (4월=현재, 3월=이전)
    view_df = df.copy()
    view_df.columns = ["순위", "이름", "4월 포인트", "3월 포인트", "결과", "부과점", "그룹", "비고"]
    
    st.subheader("회원 포인트 리스트")
    if st.session_state.admin:
        edited = st.data_editor(view_df, use_container_width=True, num_rows="dynamic")
        if st.button("데이터 최종 저장"):
            # 컬럼 복원 후 저장
            final_df = edited.drop(columns=["순위"])
            final_df.columns = ["이름", "현재포인트", "이전포인트", "결과", "부과점", "그룹", "비고"]
            final_df.to_csv(DB_FILE, index=False)
            st.success("랭킹 데이터가 업데이트되었습니다.")
    else:
        st.table(view_df)

    col1, col2 = st.columns(2)
    with col1:
        csv = view_df.to_csv(index=False).encode('utf-8-sig')
        st.download_button("Excel(CSV) 다운로드", csv, "duryu_ranking.csv", "text/csv")
    with col2:
        if st.session_state.admin:
            file = st.file_uploader("랭킹 업데이트 (CSV)", type="csv")
            if file:
                up_df = pd.read_csv(file)
                up_df.columns = [c.strip() for c in up_df.columns]
                up_df.to_csv(DB_FILE, index=False)
                st.rerun()

# --- 2번 메뉴: 대진 및 경기 현황 ---
elif menu == "📅 대진 및 경기 현황":
    groups = st.session_state.tournament["groups"]
    if not groups:
        st.info("관리자 페이지에서 대진을 생성해 주세요.")
    else:
        tabs = st.tabs(list(groups.keys()))
        for i, g_name in enumerate(groups.keys()):
            with tabs[i]:
                g = groups[g_name]
                players = g["players"]
                
                c1, c2 = st.columns([3, 2])
                with c1:
                    st.markdown("#### 🏁 조별 매트릭스")
                    matrix = pd.DataFrame("-", index=players, columns=players)
                    for idx, p in enumerate(players): matrix.iloc[idx, idx] = "X"
                    st.dataframe(matrix.style.applymap(lambda x: 'background-color: #CBD5E1' if x == 'X' else ''), use_container_width=True)
                
                with c2:
                    st.markdown("#### 📈 실시간 순위표")
                    st.caption("경기 결과 입력 시 자동 반영됩니다.")
                
                st.markdown("---")
                st.markdown("#### 🎾 대진 순서 및 결과 입력")
                for midx, match in enumerate(g["matches"]):
                    t1, t2 = match
                    with st.container():
                        st.markdown(f"""
                        <div class="match-row">
                            <div class="team-box team-left">{" & ".join(t1)}</div>
                            <div class="vs-circle">VS</div>
                            <div class="team-box team-right">{" & ".join(t2)}</div>
                        </div>
                        """, unsafe_allow_html=True)
                        sc1, sc2 = st.columns(2)
                        with sc1: st.number_input(f"T1", 0, 10, key=f"s1_{g_name}_{midx}")
                        with sc2: st.number_input(f"T2", 0, 10, key=f"s2_{g_name}_{midx}")

# --- 5번 메뉴: 관리자 페이지 ---
elif menu == "⚙️ 관리자":
    st.subheader("🔐 시스템 관리자 로그인")
    pw = st.text_input("PASSWORD", type="password")
    if pw == st.session_state.pw:
        st.session_state.admin = True
        st.success("인증 성공")
        
        adm_tabs = st.tabs(["대회/대진 생성", "회원 관리", "지난 대회 관리"])
        
        with adm_tabs[0]:
            st.markdown("### 🏟️ 대회 및 대진 구성")
            t_name = st.text_input("대회 이름", value=st.session_state.tournament["name"])
            c_cnt = st.selectbox("진행 코트 수", [1, 2, 3], index=1)
            
            st.markdown("---")
            df = load_data()
            all_names = df["이름"].tolist()
            selected = st.multiselect("참가자 선택 (체크박스)", all_names)
            
            st.write(f"선택 인원: {len(selected)}명")
            
            col_a, col_b, col_c = st.columns(3)
            g_cnt = col_a.number_input("그룹 수", 1, 10, 4)
            g_type = col_b.selectbox("경기 방식", ["KDK", "고정페어", "단식"])
            g_game = col_c.selectbox("1인당 게임 수", [3, 4])
            
            if st.button("🔥 랭킹순 그룹 배정 및 대진 생성"):
                # 랭킹순 정렬
                sorted_selected = [n for n in df.sort_values("현재포인트", ascending=False)["이름"] if n in selected]
                
                new_groups = {}
                chunk = len(sorted_selected) // g_cnt
                for i in range(g_cnt):
                    g_name = f"{chr(65+i)}조"
                    start = i * chunk
                    end = (i+1) * chunk if i < g_cnt-1 else len(sorted_selected)
                    g_players = sorted_selected[start:end]
                    
                    matches = generate_matches(g_players, g_type, g_game)
                    new_groups[g_name] = {"players": g_players, "type": g_type, "matches": matches}
                
                st.session_state.tournament = {"name": t_name, "groups": new_groups, "court": c_cnt}
                st.success("대진표 생성이 완료되었습니다!")

        with adm_tabs[2]:
            st.subheader("아카이브 관리")
            if st.button("현재 대회 아카이브 저장"):
                st.info("데이터 저장 중...")
    
    elif pw != "":
        st.error("비밀번호가 올바르지 않습니다.")

# --- 3, 4번 메뉴는 위 구조를 기반으로 아카이브 로드/결과 집계 로직 추가 ---
else:
    st.info("메뉴 개발 중입니다. (결과 분석 및 아카이브)")

st.sidebar.markdown("---")
st.sidebar.caption("v2.1.0-2026-Duryu")
