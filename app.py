import streamlit as st
import pandas as pd
import os
import json
import random
from datetime import datetime
from io import BytesIO

# --- 1. 환경 설정 및 스타일 ---
st.set_page_config(page_title="두류 랭킹 시스템", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;700;900&display=swap');
    * { font-family: 'Noto Sans KR', sans-serif; text-align: center; }
    .stApp { background-color: #F8FDF9; }
    .main-header { background: linear-gradient(135deg, #1D5B2E, #388E3C); color: white; padding: 1.5rem; border-radius: 15px; margin-bottom: 25px; box-shadow: 0 4px 15px rgba(0,0,0,0.1); }
    .match-card { background: white; border-radius: 15px; padding: 20px; border: 1px solid #C8E6C9; margin-bottom: 15px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); display: flex; align-items: center; justify-content: center; }
    .team-box { width: 42%; background: #E8F5E9; padding: 12px; border-radius: 10px; font-weight: 700; color: #1B5E20; font-size: 1.1rem; border: 1px solid #A5D6A7; }
    .vs-badge { width: 12%; color: #D32F2F; font-weight: 900; font-size: 1.2rem; }
    .group-tag { background: #FFEB3B; padding: 5px 15px; border-radius: 20px; font-weight: bold; font-size: 0.9rem; margin-bottom: 10px; display: inline-block; }
</style>
""", unsafe_allow_html=True)

# --- 2. 데이터 유틸리티 ---
DB_FILE = "tennis_members.csv"
HISTORY_FILE = "tournament_history.json"

def load_members():
    if os.path.exists(DB_FILE):
        return pd.read_csv(DB_FILE).sort_values(by="랭킹")
    return pd.DataFrame({"랭킹": range(1, 21), "이름": [f"회원{i}" for i in range(1, 21)], "포인트": [100]*20})

def load_history():
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r", encoding="utf-8") as f: return json.load(f)
    return {}

def save_history(history):
    with open(HISTORY_FILE, "w", encoding="utf-8") as f: json.dump(history, f, ensure_ascii=False, indent=4)

# --- 3. 대진 생성 엔진 ---
def get_kdk_table(n, games):
    if games == 3:
        if n == 4: return [(1,4,2,3), (1,3,2,4), (1,2,3,4)]
        if n == 8: return [(1,2,3,4), (5,6,7,8), (1,8,2,7), (3,6,4,5), (1,4,5,8), (2,3,6,7)]
        if n == 12: return [(1,2,3,4), (5,6,7,8), (9,10,11,12), (1,3,5,7), (2,4,6,8), (9,11,1,5), (4,8,9,12), (6,7,10,11), (10,12,2,3)]
    elif games == 4:
        if n == 5: return [(1,2,3,4), (1,3,2,5), (1,4,3,5), (1,5,2,4), (2,3,4,5)]
        if n == 6: return [(1,3,2,4), (1,5,4,6), (2,3,5,6), (1,4,3,5), (2,6,3,4), (1,6,2,5)]
        if n == 7: return [(1,2,3,4), (5,6,1,7), (2,3,5,7), (1,4,6,7), (3,5,2,4), (1,6,2,5), (4,6,3,7)]
        if n == 8: return [(1,2,3,4), (5,6,7,8), (1,3,5,7), (2,4,6,8), (1,5,2,6), (3,7,4,8), (1,6,3,8), (2,5,4,7)]
        if n == 9: return [(1,2,3,4), (5,6,7,8), (1,9,5,7), (2,3,6,8), (4,9,3,8), (1,5,2,6), (3,6,4,5), (1,7,8,9), (2,4,7,9)]
        if n == 10: return [(1,2,3,5), (6,7,8,10), (2,3,4,6), (7,8,1,9), (3,4,5,7), (8,9,2,10), (4,5,6,8), (1,3,9,10), (5,6,7,9), (1,10,2,4)]
        if n == 11: return [(1,2,3,5), (6,7,8,10), (4,9,1,11), (2,3,6,8), (4,5,7,10), (9,11,2,6), (1,3,7,11), (4,8,5,9), (1,10,2,8), (4,7,6,11), (3,9,5,10)]
    return []

def generate_matches(players, mode, games):
    n = len(players)
    if mode == "고정페어":
        pairs = [(players[i], players[n-1-i]) for i in range(n // 2)]
        matches = []
        for _ in range(games):
            random.shuffle(pairs)
            for j in range(0, len(pairs)-1, 2):
                matches.append((pairs[j], pairs[j+1]))
        return matches
    elif mode == "KDK":
        logic = get_kdk_table(n, games)
        return [((players[i[0]-1], players[i[1]-1]), (players[i[2]-1], players[i[3]-1])) for i in logic]
    elif mode == "단식":
        res = []
        for _ in range(games):
            pool = list(players)
            random.shuffle(pool)
            for j in range(0, len(pool)-1, 2):
                res.append(((pool[j], ""), (pool[j+1], "")))
        return res
    return []

# --- 4. 메뉴 시스템 ---
menu = st.sidebar.radio("메뉴 이동", ["🏆 실시간 랭킹", "📅 당일 대진표", "📂 지난 대회 기록", "⚙️ 대회 관리자"])

# [1. 실시간 랭킹]
if menu == "🏆 실시간 랭킹":
    st.markdown("<div class='main-header'>🏆 두류 테니스 클럽 실시간 랭킹</div>", unsafe_allow_html=True)
    df = load_members()
    st.dataframe(df, use_container_width=True, hide_index=True)
    
    col1, col2 = st.columns(2)
    with col1:
        output = BytesIO()
        df.to_excel(output, index=False)
        st.download_button("📥 랭킹 엑셀 다운로드", output.getvalue(), "duryu_ranking.xlsx")
    with col2:
        up_file = st.file_uploader("📤 랭킹 엑셀 업로드 (전체 회원용)", type=['xlsx'])
        if up_file:
            pd.read_excel(up_file).to_csv(DB_FILE, index=False)
            st.success("전체 랭킹이 업데이트되었습니다!")
            st.rerun()

# [2. 당일 대진표]
elif menu == "📅 당일 대진표":
    history = load_history()
    if not history:
        st.info("현재 생성된 대진표가 없습니다. 관리자 페이지에서 대진을 확정해주세요.")
    else:
        latest = list(history.values())[-1]
        st.markdown(f"<div class='main-header'>📅 {latest['title']}</div>", unsafe_allow_html=True)
        
        for g_name, g_data in latest['groups'].items():
            st.markdown(f"<div class='group-tag'>{g_name} - {g_data['mode']} ({g_data['games']}게임)</div>", unsafe_allow_html=True)
            for m in g_data['matches']:
                st.markdown(f"""<div class='match-card'><div class='team-box'>{m[0][0]} {f'& {m[0][1]}' if m[0][1] else ''}</div><div class='vs-badge'>VS</div><div class='team-box'>{m[1][0]} {f'& {m[1][1]}' if m[1][1] else ''}</div></div>""", unsafe_allow_html=True)

# [4. 관리자 페이지]
elif menu == "⚙️ 대회 관리자":
    st.markdown("<div class='main-header'>⚙️ 대회 운영 및 대진 관리</div>", unsafe_allow_html=True)
    if st.sidebar.text_input("관리자 암호", type="password") == "0502":
        
        # 1. 참여자 명단 필터링 (랭킹순)
        st.subheader("✅ 오늘 대회 참여자 체크")
        df_all = load_members()
        
        # 텍스트로 이름 수정 기능
        col_txt, col_chk = st.columns([1, 2])
        with col_txt:
            st.caption("이름 오타 수정 시 사용")
            edited_df = st.data_editor(df_all[['랭킹', '이름']], hide_index=True)
            if st.button("회원 이름 수정 저장"):
                df_all['이름'] = edited_df['이름']
                df_all.to_csv(DB_FILE, index=False)
                st.rerun()

        with col_chk:
            st.caption("오늘 출석한 회원만 체크하세요.")
            cols = st.columns(3)
            active_p = []
            for i, (idx, row) in enumerate(df_all.iterrows()):
                if cols[i%3].checkbox(f"{row['이름']} ({row['랭킹']}위)", value=False, key=f"p_{row['이름']}"):
                    active_p.append(row['이름'])
        
        st.divider()
        
        # 2. 그룹 배정 (랭킹순 자동 슬라이싱)
        if active_p:
            st.subheader("📝 그룹별 대진 세부 설정")
            g_count = st.number_input("오늘 운영할 그룹 수", 1, 6, 2)
            court_count = st.selectbox("코트 수 (참고용)", [1, 2, 3], index=1)
            
            group_results = {}
            current_ptr = 0
            for i in range(g_count):
                with st.expander(f"📍 그룹 {i+1} 설정 (현재까지 {len(active_p)}명 중 {current_ptr}명 배정됨)", expanded=True):
                    c1, c2, c3, c4 = st.columns([2,1,1,1])
                    g_name = c1.text_input(f"그룹 이름", f"{chr(65+i)}그룹", key=f"gn_{i}")
                    g_num = c2.number_input(f"참여 인원", 4, 20, 8, key=f"gnum_{i}")
                    g_mode = c3.selectbox(f"방식", ["고정페어", "KDK", "단식"], index=1, key=f"gm_{i}")
                    g_games = c4.selectbox(f"게임수", [3, 4], index=1, key=f"gg_{i}")
                    
                    # 핵심: 체크된 참여자 중 랭킹순으로 자동 배정
                    g_players = active_p[current_ptr : current_ptr + int(g_num)]
                    st.info(f"배정 회원: {', '.join(g_players) if g_players else '없음'}")
                    
                    if g_players:
                        group_results[g_name] = {
                            "mode": g_mode, "games": g_games, 
                            "players": g_players, "matches": generate_matches(g_players, g_mode, g_games)
                        }
                        current_ptr += int(g_num)
            
            if st.button("🎲 최종 대진표 확정 및 저장"):
                history = load_history()
                new_id = datetime.now().strftime("%Y%m%d_%H%M")
                history[new_id] = {
                    "title": f"{datetime.now().strftime('%m월 %d일')} 두류 대회",
                    "groups": group_results
                }
                save_history(history)
                st.success("대진표가 생성되었습니다! '당일 대진표' 메뉴에서 확인하세요.")
                st.rerun()

# [3. 지난 대회 기록]
elif menu == "📂 지난 대회 기록":
    st.markdown("<div class='main-header'>📂 지난 대회 아카이브</div>", unsafe_allow_html=True)
    history = load_history()
    for tid in reversed(list(history.keys())):
        with st.expander(f"📌 {history[tid]['title']}"):
            st.json(history[tid]['groups'])
            if st.button(f"이 대회 삭제", key=f"del_{tid}"):
                del history[tid]
                save_history(history)
                st.rerun()
