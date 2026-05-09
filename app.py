import streamlit as st
import pandas as pd
import random, os, json
from datetime import date
from io import BytesIO

# ══════════════════════════════════════════════════════════════
# 앱 설정 (반응형 + 다크모드 지원)
# ══════════════════════════════════════════════════════════════
st.set_page_config(page_title="두류 랭킹", page_icon="🎾",
                   layout="wide", initial_sidebar_state="collapsed")

# 반응형 + 다크모드 지원 CSS
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;600;700;800;900&display=swap');

* {
    font-family: 'Noto Sans KR', sans-serif !important;
    box-sizing: border-box;
}

/* 반응형 컨테이너 */
.block-container { 
    padding: 0.5rem 0.8rem 1rem 0.8rem !important; 
    max-width: 100% !important;
}

/* 네비게이션 바 - 터치 최적화 */
section.main [data-testid="stHorizontalBlock"]:first-of-type .stButton > button {
    background: transparent !important;
    color: var(--text-color, rgba(0,0,0,0.7)) !important;
    border: none !important; 
    border-radius: 12px !important;
    font-size: clamp(0.65rem, 3.5vw, 0.85rem) !important;
    font-weight: 600 !important;
    padding: 10px 4px !important;
    line-height: 1.3 !important;
    white-space: pre-line !important;
    box-shadow: none !important;
    min-height: 55px !important;
    transition: all 0.2s ease !important;
}
section.main [data-testid="stHorizontalBlock"]:first-of-type .stButton > button:hover {
    background: rgba(100, 100, 100, 0.1) !important;
}
section.main [data-testid="stHorizontalBlock"]:first-of-type .stButton > button[kind="primary"] {
    background: linear-gradient(135deg,#1D5B2E,#388E3C) !important;
    color: #fff !important;
    box-shadow: 0 2px 8px rgba(29,91,46,0.3) !important;
}

/* 헤더 스타일 */
.main-hdr {
    background: linear-gradient(135deg,#1D5B2E,#388E3C);
    color:#fff; 
    padding: 0.7rem 1rem; 
    border-radius: 14px;
    margin-bottom: 0.8rem; 
    font-size: clamp(1rem, 5vw, 1.3rem);
    font-weight: 800; 
    text-align: center;
    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
}
.sec {
    font-size: 0.95rem; 
    font-weight: 800; 
    color: #1D5B2E;
    border-left: 4px solid #66BB6A; 
    padding-left: 10px; 
    margin: 14px 0 8px;
}

/* 탭 스타일 */
button[data-baseweb="tab"] {
    font-size: 0.75rem !important;
    font-weight: 600 !important;
    padding: 8px 12px !important;
    border-radius: 12px 12px 0 0 !important;
}
button[data-baseweb="tab"][aria-selected="true"] {
    background: linear-gradient(135deg,#1D5B2E,#388E3C) !important;
    color: #fff !important;
}

/* ================================================================
   ★★★ 데이터프레임 완벽 가운데 정렬 + 다크모드 대응 ★★★
   ================================================================ */
div[data-testid="stDataFrame"] {
    overflow-x: auto !important;
}
div[data-testid="stDataFrame"] table,
div[data-testid="stDataEditor"] table {
    width: 100% !important;
    border-collapse: collapse !important;
}
div[data-testid="stDataFrame"] table th,
div[data-testid="stDataFrame"] table td,
div[data-testid="stDataEditor"] table th,
div[data-testid="stDataEditor"] table td {
    text-align: center !important;
    vertical-align: middle !important;
    padding: 8px 6px !important;
    font-size: clamp(0.65rem, 3vw, 0.8rem) !important;
}
/* 다크모드에서도 글자 보이게 */
div[data-testid="stDataFrame"] table td {
    color: var(--text-color, #000000) !important;
}
/* 헤더 스타일 유지 */
div[data-testid="stDataFrame"] table th {
    background-color: rgba(29, 91, 46, 0.1) !important;
    font-weight: 700 !important;
}

/* 숫자 입력 필드 */
input[type="number"] {
    text-align: center !important;
    font-size: 0.9rem !important;
    font-weight: 600 !important;
    min-height: 44px !important;
    border-radius: 10px !important;
}
div[data-testid="stNumberInput"] input {
    text-align: center !important;
    font-weight: 600 !important;
    font-size: 0.9rem !important;
    padding: 8px !important;
    min-height: 44px !important;
    border-radius: 10px !important;
}

/* 팀 도형 - 다크모드 대응 */
.team-box {
    border-radius: 12px;
    padding: 10px 12px !important;
    font-weight: 700 !important;
    font-size: clamp(0.7rem, 3.5vw, 0.85rem) !important;
    text-align: center;
    margin: 4px 0;
    box-shadow: 0 1px 4px rgba(0,0,0,.1);
    line-height: 1.3;
    min-height: 50px;
    display: flex;
    align-items: center;
    justify-content: center;
    width: 100%;
    word-break: keep-all;
    color: #fff !important;
}
.tg{background:linear-gradient(135deg,#66BB6A,#43A047);}
.tb{background:linear-gradient(135deg,#42A5F5,#1E88E5);}
.to{background:linear-gradient(135deg,#FFA726,#FB8C00);}
.tp{background:linear-gradient(135deg,#AB47BC,#8E24AA);}
.tr{background:linear-gradient(135deg,#EF5350,#E53935);}
.tt{background:linear-gradient(135deg,#26A69A,#00897B);}

/* 경기별 색상 */
.match-color-0 { background: linear-gradient(135deg,#66BB6A,#43A047) !important; color:#fff; }
.match-color-1 { background: linear-gradient(135deg,#42A5F5,#1E88E5) !important; color:#fff; }
.match-color-2 { background: linear-gradient(135deg,#FFA726,#FB8C00) !important; color:#fff; }

/* VS 원 */
.vs-circle {
    background:#FFB74D;
    color:#fff;
    border-radius:50%;
    width: 40px !important;
    height: 40px !important;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 800;
    font-size: 0.8rem;
    margin: 0 auto;
    box-shadow: 0 2px 6px rgba(0,0,0,0.2);
}

/* 구분선 */
hr {
    margin: 12px 0;
    border-color: rgba(128,128,128,0.2);
}

/* 참가자 태그 */
.p-tag {
    display: inline-block;
    background: #E8F5E9;
    border: 1px solid #66BB6A;
    border-radius: 25px;
    padding: 5px 12px;
    margin: 3px 5px;
    font-size: 0.75rem;
    font-weight: 600;
    color: #1D5B2E;
}

/* 버튼 - 터치 최적화 */
.stButton > button {
    border-radius: 12px !important;
    font-weight: 600 !important;
    font-size: 0.85rem !important;
    padding: 10px 16px !important;
    min-height: 48px !important;
    transition: all 0.2s ease !important;
}
.stButton > button:hover {
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(0,0,0,0.15);
}

/* 입력 필드 터치 영역 */
.stTextInput > div > div > input,
.stTextArea > div > div > textarea,
.stSelectbox > div > div {
    min-height: 44px !important;
    border-radius: 10px !important;
}

/* 매트릭스 테이블 */
.matrix-table {
    width: 100%;
    border-collapse: collapse;
    font-size: clamp(0.6rem, 3vw, 0.75rem);
    background: var(--background-color, #fff);
}
.matrix-table th, .matrix-table td {
    padding: 8px 5px;
    border: 1px solid rgba(128,128,128,0.3);
    text-align: center;
}
.matrix-table th {
    background-color: rgba(29, 91, 46, 0.15);
    font-weight: 700;
}
.matrix-grey {
    background-color: rgba(200,200,200,0.5);
    color: #999;
}
.matrix-x {
    color: #aaa;
}

/* KDK 대진표 */
.kdk-bracket {
    background: rgba(245,245,245,0.6);
    border-radius: 12px;
    padding: 12px;
    margin: 10px 0;
    font-size: clamp(0.6rem, 3vw, 0.75rem);
    overflow-x: auto;
}
.kdk-bracket table {
    width: 100%;
    border-collapse: collapse;
}
.kdk-bracket th, .kdk-bracket td {
    padding: 8px;
    text-align: center;
    border: 1px solid rgba(128,128,128,0.3);
}
.kdk-bracket th {
    background-color: rgba(29, 91, 46, 0.15);
    font-weight: 700;
}

/* 카드 */
.tour-card, .rank-card {
    padding: 10px 14px;
    margin: 8px 0;
    border-radius: 12px;
    background: var(--background-color, #fff);
    border: 1px solid rgba(128,128,128,0.2);
    box-shadow: 0 2px 6px rgba(0,0,0,0.05);
}

/* 반응형: 모바일에서 컬럼 간격 조정 */
@media (max-width: 640px) {
    .block-container {
        padding: 0.3rem 0.5rem 0.8rem 0.5rem !important;
    }
    .team-box {
        padding: 6px 8px !important;
        min-height: 44px !important;
        font-size: 0.7rem !important;
    }
    .vs-circle {
        width: 32px !important;
        height: 32px !important;
        font-size: 0.7rem;
    }
    .stButton > button {
        padding: 6px 10px !important;
        min-height: 40px !important;
        font-size: 0.75rem !important;
    }
    .matrix-table th, .matrix-table td {
        padding: 5px 3px;
    }
}

/* 다크모드 지원 */
@media (prefers-color-scheme: dark) {
    .matrix-table {
        background: #1e1e1e;
    }
    .matrix-table td {
        color: #e0e0e0;
    }
    .matrix-grey {
        background-color: #3a3a3a;
        color: #666;
    }
    .kdk-bracket {
        background: #2a2a2a;
    }
    .kdk-bracket td {
        color: #e0e0e0;
    }
    .tour-card, .rank-card {
        background: #2a2a2a;
        border-color: #444;
    }
    .p-tag {
        background: #2a4a2a;
        border-color: #66BB6A;
        color: #c8e6c9;
    }
}
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
# 파일 경로 / 상수
# ══════════════════════════════════════════════════════════════
RANK_FILE   = "ranking_master.csv"
MEMBER_FILE = "member_roster.json"
TOUR_FILE   = "tournaments.json"
ADMIN_PW    = "0502"
COLS_RANK   = ["랭킹","이름","현재포인트","3월 포인트","결과","부과점","그룹","비고"]

GCLS = ["tg","tb","to","tp","tr","tt"]
GHEX = ["#66BB6A","#42A5F5","#FFA726","#AB47BC","#EF5350","#26A69A"]
GLBL = ["🟢","🔵","🟠","🟣","🔴","🩵"]

# KDK 대진표 (1인 3게임)
KDK_3G = {
    4: [(1,4,2,3), (1,3,2,4), (1,2,3,4)],
    8: [(1,2,3,4), (5,6,7,8), (1,8,2,7), (3,6,4,5), (1,4,5,8), (2,3,6,7)],
    12: [(1,2,3,4), (5,6,7,8), (9,10,11,12), (1,3,5,7), (2,4,6,8),
         (9,11,1,5), (4,8,9,12), (6,7,10,11), (10,12,2,3)]
}

# KDK 대진표 (1인 4게임)
KDK_4G = {
    5: [(1,2,3,4), (1,3,2,5), (1,4,3,5), (1,5,2,4), (2,3,4,5)],
    6: [(1,3,2,4), (1,5,4,6), (2,3,5,6), (1,4,3,5), (2,6,3,4), (1,6,2,5)],
    7: [(1,2,3,4), (5,6,1,7), (2,3,5,7), (1,4,6,7), (3,5,2,4), (1,6,2,5), (4,6,3,7)],
    8: [(1,2,3,4), (5,6,7,8), (1,3,5,7), (2,4,6,8), (1,5,2,6), (3,7,4,8), (1,6,3,8), (2,5,4,7)],
    9: [(1,2,3,4), (5,6,7,8), (1,9,5,7), (2,3,6,8), (4,9,3,8), (1,5,2,6), (3,6,4,5), (1,7,8,9), (2,4,7,9)],
    10: [(1,2,3,5), (6,7,8,10), (2,3,4,6), (7,8,1,9), (3,4,5,7), (8,9,2,10),
         (4,5,6,8), (1,3,9,10), (5,6,7,9), (1,10,2,4)],
    11: [(1,2,3,5), (6,7,8,10), (4,9,1,11),
