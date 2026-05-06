import streamlit as st
import pandas as pd
import os
import json
import random
from datetime import datetime
from io import BytesIO

# --- [1. 스타일 및 테마 설정] ---
st.set_page_config(page_title="두류 랭킹 시스템", layout="wide", initial_sidebar_state="expanded")

def apply_custom_style():
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;700;900&display=swap');
        * { font-family: 'Noto Sans KR', sans-serif; text-align: center; }
        .stApp { background-color: #F4F9F4; }
        .main-header { 
            background: linear-gradient(135deg, #1D5B2E 0%, #388E3C 100%); 
            color: white; padding: 2rem; border-radius: 20px; 
            margin-bottom: 30px; box-shadow: 0 10px 20px rgba(0,0,0,0.1);
        }
        .match-card { 
            background: white; border-radius: 15px; padding: 25px; 
            border: 1px solid #E0E0E0; margin-bottom: 20px; 
            box-shadow: 0 4px 12px rgba(0,0,0,0.05);
            display: flex; align-items: center; justify-content: space-around;
        }
        .team-container { 
            width: 40%; background: #F1F8E9; padding: 15px; 
            border-radius: 12px; border: 2px solid #C8E6C9;
        }
        .player-name { font-weight: 700; color: #2E7D32; font-size: 1.2rem; }
        .vs-circle { 
            background: #FF5252; color: white; width: 45px; height: 45px; 
            border-radius: 50%; display: flex; align-items: center; 
            justify-content: center; font-weight: 900; font-size: 0.9rem;
        }
        .group-badge {
            background: #FFD600; color: #000; padding: 6px 18px;
            border-radius: 30px; font-weight: 800; font-size: 0.85rem;
            margin-bottom: 15px; display: inline-block;
        }
    </style>
    """, unsafe_allow_html=True)

# --- [2. 데이터 관리 클래스] ---
class DuryuDB:
    DB_FILE = "tennis_members.csv"
    HISTORY_FILE = "tournament_history.json"

    @staticmethod
    def load_members():
        if os.path.exists(DuryuDB.DB_FILE):
            df = pd.read_csv(DuryuDB.DB_FILE)
            # 컬럼명 공백 제거 처리
            df.columns = [c.strip() for c in df.columns]
            return df.sort_values(by="랭킹").reset_index(drop=True)
        return pd.DataFrame({"랭킹": range(1, 21), "이름": [f"회원{i}" for i in range(1, 21)], "포인트": [1000]*20})

    @staticmethod
    def save_members(df):
        df.to_csv(DuryuDB.DB_FILE, index=False)

    @staticmethod
    def load_history():
        if os.path.exists(DuryuDB.HISTORY_FILE):
            try:
                with open(DuryuDB.HISTORY_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
            except: return {}
        return {}

    @staticmethod
    def save_history(history):
        with open(DuryuDB.HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(history, f, ensure_ascii=False, indent=4)

# --- [3. 대진 엔진] ---
class TennisEngine:
    @staticmethod
    def get_kdk_logic(n, games):
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

    @staticmethod
    def create_matches(players, mode, games):
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
            logic = TennisEngine.get_kdk_logic(n, games)
            return [((players[i[0]-1], players[i[1]-1]), (players[i[2]-1], players[i[3]-1])) for i in logic]
        elif mode == "단식":
            matches = []
            for _ in range(games):
                pool = list(players)
                random.shuffle(pool)
                for j in range(0, len(pool)-1, 2):
                    matches.append(((pool[j], ""), (pool[j+1], "")))
            return matches
        return []

# --- [4. 메인 화면 로직] ---
def main():
    apply_custom_style()
    db = DuryuDB()
    
    st.sidebar.title("🏸 두류 테니스 클럽")
    pw = st.sidebar.text_input("관리자 암호", type="password")
    is_admin = (pw == "0502")

    menu = st.sidebar.radio("메뉴", ["🏆 전체 랭킹", "📅 당일 대진표", "📂 아카이브", "⚙️ 대회 관리"])

    # --- 메뉴 1: 전체 랭킹 ---
    if menu == "🏆 전체 랭킹":
        st.markdown("<div class='main-header'>🏆 실시간 클럽 랭킹</div>", unsafe_allow_html=True)
        df = db.load_members()
        st.dataframe(df, use_container_width=True, hide_index=True)
        if is_admin:
            up_file = st.file_uploader("엑셀 업로드", type=['xlsx'])
            if up_file:
                db.save_members(pd.read_excel(up_file))
                st.rerun()

    # --- 메뉴 2: 당일 대진표 ---
    elif menu == "📅 당일 대진표":
        history = db.load_history()
        if not history: st.info("대진표를 생성해주세요.")
        else:
            latest = list(history.values())[-1]
            st.markdown(f"<div class='main-header'>{latest['title']}</div>", unsafe_allow_html=True)
            for g_name, g_info in latest['groups'].items():
                st.markdown(f"<div class='group-badge'>{g_name} ({g_info['mode']})</div>", unsafe_allow_html=True)
                cols = st.columns(2)
                for idx, m in enumerate(g_info['matches']):
                    with cols[idx%2]:
                        st.markdown(f"""<div class='match-card'><div class='team-container'>{m[0][0]} {m[0][1]}</div><div class='vs-circle'>VS</div><div class='team-container'>{m[1][0]} {m[1][1]}</div></div>""", unsafe_allow_html=True)

    # --- 메뉴 4: 대회 관리 (KeyError 방지 로직 포함) ---
    elif menu == "⚙️ 대회 관리":
        if not is_admin: 
            st.warning("암호를 입력하세요."); return
            
        st.markdown("<div class='main-header'>⚙️ 대회 자동 배정 설정</div>", unsafe_allow_html=True)
        df_all = db.load_members()
        
        # 이름/랭킹 컬럼 존재 여부 확인 및 공백 제거
        df_all.columns = [c.strip() for c in df_all.columns]
        
        # STEP 1. 명단 수정 및 참여자 체크
        st.subheader("STEP 1. 명단 확인 및 참여자 선택")
        edited_df = st.data_editor(df_all, use_container_width=True, hide_index=True)
        if st.button("수정 내용 DB 저장"):
            db.save_members(edited_df); st.success("저장 완료")

        active_indices = []
        cols = st.columns(4)
        # KeyError 방지를 위해 index와 loc를 사용하여 안전하게 접근
        for i, idx in enumerate(edited_df.index):
            row = edited_df.loc[idx]
            name = row.get('이름', f"회원{idx}")
            rank = row.get('랭킹', 0)
            if cols[i%4].checkbox(f"{name} ({rank}위)", value=False, key=f"chk_{idx}"):
                active_indices.append(idx)
        
        # 체크된 참여자를 랭킹순으로 추출
        selected_players = edited_df.loc[active_indices].sort_values(by="랭킹")['이름'].tolist()
        
        if selected_players:
            st.success(f"참여자 {len(selected_players)}명: {', '.join(selected_players)}")
            st.divider()
            
            # STEP 2. 그룹별 배정
            st.subheader("STEP 2. 그룹별 랭킹순 자동 슬라이싱")
            g_count = st.number_input("그룹 수", 1, 6, 2)
            final_groups = {}
            current_ptr = 0
            
            for i in range(g_count):
                st.markdown(f"**📍 {i+1}번 그룹**")
                c1, c2, c3, c4 = st.columns([2,1,1,1])
                gn = c1.text_input("이름", f"{chr(65+i)}그룹", key=f"gn_{i}")
                gs = c2.number_input("인원", 4, 20, 8, key=f"gs_{i}")
                gm = c3.selectbox("방식", ["고정페어", "KDK", "단식"], index=1, key=f"gm_{i}")
                gg = c4.selectbox("게임", [3, 4], index=1, key=f"gg_{i}")
                
                # 랭킹순 자동 슬라이싱
                assigned = selected_players[current_ptr : current_ptr + int(gs)]
                st.caption(f"배정 명단: {', '.join(assigned)}")
                
                if assigned:
                    final_groups[gn] = {
                        "mode": gm, "games": gg, "players": assigned,
                        "matches": TennisEngine.create_matches(assigned, gm, gg)
                    }
                    current_ptr += int(gs)
                st.divider()

            if st.button("🚀 대진표 확정"):
                history = db.load_history()
                tid = datetime.now().strftime("%Y%m%d_%H%M")
                history[tid] = {"title": f"{datetime.now().strftime('%m/%d')} 대회", "groups": final_groups}
                db.save_history(history)
                st.rerun()

    # --- 메뉴 3: 아카이브 ---
    elif menu == "📂 아카이브":
        st.markdown("<div class='main-header'>📂 지난 기록 관리</div>", unsafe_allow_html=True)
        history = db.load_history()
        for tid in reversed(list(history.keys())):
            with st.expander(f"📌 {history[tid]['title']} ({tid})"):
                if st.button("삭제", key=f"del_{tid}"):
                    del history[tid]; db.save_history(history); st.rerun()

if __name__ == "__main__":
    main()
