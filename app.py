import streamlit as st
import pandas as pd
import os
import json
import random
from datetime import datetime
from io import BytesIO

# --- [1. 스타일 및 시각화 설정] ---
st.set_page_config(page_title="두류 테니스 운영 시스템", layout="wide", initial_sidebar_state="expanded")

def apply_design():
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;700;900&display=swap');
        * { font-family: 'Noto Sans KR', sans-serif; text-align: center; }
        .stApp { background-color: #F7FAF7; }
        
        /* 메인 헤더 */
        .main-header { 
            background: linear-gradient(135deg, #1D5B2E 0%, #388E3C 100%); 
            color: white; padding: 2.5rem; border-radius: 25px; 
            margin-bottom: 35px; box-shadow: 0 12px 24px rgba(0,0,0,0.15);
        }
        
        /* 매치 카드 */
        .match-card { 
            background: white; border-radius: 18px; padding: 25px; 
            border: 1px solid #E0E0E0; margin-bottom: 20px; 
            box-shadow: 0 6px 15px rgba(0,0,0,0.06);
            display: flex; align-items: center; justify-content: space-around;
        }
        .team-unit { 
            width: 42%; background: #F1F8E9; padding: 18px; 
            border-radius: 15px; border: 2px solid #C8E6C9;
        }
        .player-text { font-weight: 700; color: #2E7D32; font-size: 1.25rem; }
        .vs-badge { 
            background: #FF5252; color: white; width: 50px; height: 50px; 
            border-radius: 50%; display: flex; align-items: center; 
            justify-content: center; font-weight: 900;
        }
        
        /* 그룹 구분선 */
        .group-header {
            background: #FFD600; color: #333; padding: 8px 20px;
            border-radius: 50px; font-weight: 800; font-size: 1rem;
            margin: 20px 0; display: inline-block;
        }
    </style>
    """, unsafe_allow_html=True)

# --- [2. 데이터 매니지먼트 클래스] ---
class DuryuDataHandler:
    MEMBER_FILE = "duryu_members.csv"
    HISTORY_FILE = "tournament_history.json"

    @staticmethod
    def load_members():
        if os.path.exists(DuryuDataHandler.MEMBER_FILE):
            df = pd.read_csv(DuryuDataHandler.MEMBER_FILE)
            df.columns = [c.strip() for c in df.columns]
            return df.sort_values(by="랭킹").reset_index(drop=True)
        # 초기 기본 데이터
        return pd.DataFrame({"랭킹": range(1, 21), "이름": [f"회원{i}" for i in range(1, 21)], "급수": ["A"]*20})

    @staticmethod
    def save_members(df):
        df.to_csv(DuryuDataHandler.MEMBER_FILE, index=False)

    @staticmethod
    def load_history():
        if os.path.exists(DuryuDataHandler.HISTORY_FILE):
            try:
                with open(DuryuDataHandler.HISTORY_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
            except: return {}
        return {}

    @staticmethod
    def save_history(history):
        with open(DuryuDataHandler.HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(history, f, ensure_ascii=False, indent=4)

# --- [3. 대진 생성 엔진] ---
class TournamentEngine:
    @staticmethod
    def get_kdk_blueprint(n, games):
        # 1인 3게임 기준
        if games == 3:
            if n == 4: return [(1,4,2,3), (1,3,2,4), (1,2,3,4)]
            if n == 8: return [(1,2,3,4), (5,6,7,8), (1,8,2,7), (3,6,4,5), (1,4,5,8), (2,3,6,7)]
            if n == 12: return [(1,2,3,4), (5,6,7,8), (9,10,11,12), (1,3,5,7), (2,4,6,8), (9,11,1,5), (4,8,9,12), (6,7,10,11), (10,12,2,3)]
        # 1인 4게임 기준
        elif games == 4:
            if n == 5: return [(1,2,3,4), (1,3,2,5), (1,4,3,5), (1,5,2,4), (2,3,4,5)]
            if n == 6: return [(1,3,2,4), (1,5,4,6), (2,3,5,6), (1,4,3,5), (2,6,3,4), (1,6,2,5)]
            if n == 7: return [(1,2,3,4), (5,6,1,7), (2,3,5,7), (1,4,6,7), (3,5,2,4), (1,6,2,5), (4,6,3,7)]
            if n == 8: return [(1,2,3,4), (5,6,7,8), (1,3,5,7), (2,4,6,8), (1,5,2,6), (3,7,4,8), (1,6,3,8), (2,5,4,7)]
            if n == 10: return [(1,2,3,5), (6,7,8,10), (2,3,4,6), (7,8,1,9), (3,4,5,7), (8,9,2,10), (4,5,6,8), (1,3,9,10), (5,6,7,9), (1,10,2,4)]
        return []

    @staticmethod
    def build_matches(players, mode, games):
        n = len(players)
        if mode == "고정페어":
            # 1위-최하위, 2위-차하위 밸런스 페어링
            pairs = [(players[i], players[n-1-i]) for i in range(n // 2)]
            matches = []
            for _ in range(games):
                random.shuffle(pairs)
                for j in range(0, len(pairs)-1, 2):
                    matches.append((pairs[j], pairs[j+1]))
            return matches
        elif mode == "KDK":
            blueprint = TournamentEngine.get_kdk_blueprint(n, games)
            return [((players[i[0]-1], players[i[1]-1]), (players[i[2]-1], players[i[3]-1])) for i in blueprint]
        return []

# --- [4. 메인 어플리케이션] ---
def main():
    apply_design()
    handler = DuryuDataHandler()
    engine = TournamentEngine()
    
    # 세션 상태 초기화 (전체 선택용)
    if 'select_all' not in st.session_state: st.session_state.select_all = False

    st.sidebar.title("🎾 Duryu Admin")
    admin_code = st.sidebar.text_input("관리자 코드", type="password")
    is_admin = (admin_code == "0502")

    menu = st.sidebar.radio("메뉴 이동", ["📊 회원 랭킹 관리", "📝 대회 참가 신청", "⚙️ 대진 생성 및 운영", "📅 경기 현황판"])

    # --- 메뉴 1: 회원 랭킹 관리 ---
    if menu == "📊 회원 랭킹 관리":
        st.markdown("<div class='main-header'>📊 두류 테니스 클럽 회원 DB</div>", unsafe_allow_html=True)
        df_members = handler.load_members()
        
        if is_admin:
            st.subheader("📤 전체 명단 엑셀 업로드")
            excel_file = st.file_uploader("랭킹 엑셀 파일을 선택하세요", type=['xlsx'])
            if excel_file:
                new_df = pd.read_excel(excel_file)
                handler.save_members(new_df)
                st.success("회원 명단이 성공적으로 저장되었습니다.")
                st.rerun()

        st.dataframe(df_members, use_container_width=True, hide_index=True)
        
        # 엑셀 다운로드 기능
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df_members.to_excel(writer, index=False)
        st.download_button("📥 현재 명단 엑셀 다운로드", output.getvalue(), "duryu_members_list.xlsx")

    # --- 메뉴 2: 대회 참가 신청 (텍스트 입력 및 체크박스) ---
    elif menu == "📝 대회 참가 신청":
        st.markdown("<div class='main-header'>📝 당일 대회 참가자 접수</div>", unsafe_allow_html=True)
        df_all = handler.load_members()
        
        col_text, col_check = st.columns([1, 1.5])
        
        with col_text:
            st.subheader("1️⃣ 텍스트로 일괄 입력")
            st.caption("카톡 명단을 복사해서 붙여넣으세요. (이름 사이 쉼표나 줄바꿈)")
            input_text = st.text_area("참가자 명단 입력", height=300)
            text_names = [n.strip() for n in input_text.replace('\n', ',').split(',') if n.strip()]
            
        with col_check:
            st.subheader("2️⃣ 명단에서 선택")
            # 전체 선택 기능
            if st.checkbox("🔄 전체 선택 / 해제", value=st.session_state.select_all):
                st.session_state.select_all = True
            else:
                st.session_state.select_all = False
            
            selected_names = []
            chk_cols = st.columns(3)
            for i, row in df_all.iterrows():
                is_checked = st.session_state.select_all or (row['이름'] in text_names)
                if chk_cols[i%3].checkbox(f"{row['이름']} ({row['랭킹']}위)", value=is_checked, key=f"att_{row['이름']}"):
                    selected_names.append(row['이름'])
        
        # 중복 제거 및 랭킹 정렬
        final_list = sorted(list(set(selected_names)), key=lambda x: df_all[df_all['이름'] == x]['랭킹'].values[0] if x in df_all['이름'].values else 999)
        st.session_state.current_attendees = final_list
        
        st.info(f"✅ 현재 접수된 인원: {len(final_list)}명")
        st.write(", ".join(final_list))

    # --- 메뉴 3: 대진 생성 및 운영 ---
    elif menu == "⚙️ 대진 생성 및 운영":
        if not is_admin:
            st.error("관리자 권한이 필요합니다."); return
        
        st.markdown("<div class='main-header'>⚙️ 그룹 배정 및 대진 생성</div>", unsafe_allow_html=True)
        
        attendees = st.session_state.get('current_attendees', [])
        if not attendees:
            st.warning("먼저 참가 신청 메뉴에서 인원을 선택해주세요."); return
            
        df_all = handler.load_members()
        
        # 그룹 설정
        g_count = st.number_input("나눌 그룹 수", 1, 6, 2)
        final_tournament = {}
        ptr = 0
        
        for i in range(g_count):
            with st.expander(f"📍 그룹 {i+1} 세부 설정", expanded=True):
                c1, c2, c3, c4 = st.columns([2, 1, 1, 1])
                g_name = c1.text_input("그룹명", f"{chr(65+i)}그룹", key=f"gn_{i}")
                g_size = c2.number_input("인원수", 4, 30, 8, key=f"gs_{i}")
                g_mode = c3.selectbox("방식", ["고정페어", "KDK"], index=1, key=f"gm_{i}")
                g_games = c4.selectbox("게임수", [3, 4], index=1, key=f"gg_{i}")
                
                # 랭킹순 자동 슬라이싱
                assigned = attendees[ptr : ptr + int(g_size)]
                st.markdown(f"**배정된 명단:** {', '.join(assigned)}")
                
                if assigned:
                    final_tournament[g_name] = {
                        "mode": g_mode, "games": g_games, "players": assigned,
                        "matches": engine.build_matches(assigned, g_mode, g_games)
                    }
                    ptr += int(g_size)

        if st.button("🚀 대진표 최종 확정 및 저장"):
            history = handler.load_history()
            tid = datetime.now().strftime("%Y-%m-%d %H:%M")
            history[tid] = {
                "title": f"{datetime.now().strftime('%m월 %d일')} 두류 정기전",
                "groups": final_tournament
            }
            handler.save_history(history)
            st.success("대진표가 생성되었습니다! '경기 현황판' 메뉴를 확인하세요.")

    # --- 메뉴 4: 경기 현황판 ---
    elif menu == "📅 경기 현황판":
        history = handler.load_history()
        if not history:
            st.info("진행 중인 대회가 없습니다.")
        else:
            latest_id = list(history.keys())[-1]
            data = history[latest_id]
            st.markdown(f"<div class='main-header'>📅 {data['title']}</div>", unsafe_allow_html=True)
            
            for g_name, g_info in data['groups'].items():
                st.markdown(f"<div class='group-header'>{g_name} ({g_info['mode']})</div>", unsafe_allow_html=True)
                cols = st.columns(2)
                for idx, m in enumerate(g_info['matches']):
                    with cols[idx % 2]:
                        st.markdown(f"""
                        <div class='match-card'>
                            <div class='team-unit'><div class='player-text'>{m[0][0]}</div><div style='font-size:0.8rem;'>{m[0][1]}</div></div>
                            <div class='vs-badge'>VS</div>
                            <div class='team-unit'><div class='player-text'>{m[1][0]}</div><div style='font-size:0.8rem;'>{m[1][1]}</div></div>
                        </div>
                        """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
