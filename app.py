import streamlit as st
import pandas as pd
import random, os, json
from datetime import date
from io import BytesIO

# ══════════════════════════════════════════════════════════════
# 앱 설정
# ══════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="두류 랭킹 관리 시스템",
    page_icon="🎾",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ══════════════════════════════════════════════════════════════
# CSS
# ══════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;600;700;900&display=swap');

html, body, [class*="css"], button, input, select, textarea {
    font-family: 'Noto Sans KR', sans-serif !important;
}

.block-container{
    padding:0.5rem 0.7rem 2rem !important;
    max-width:100% !important;
}

/* 상단 */
.main-hdr{
    background:linear-gradient(135deg,#1D5B2E,#388E3C);
    color:#fff;
    padding:1rem 1.4rem;
    border-radius:16px;
    margin-bottom:1rem;
    font-size:clamp(1.2rem,4vw,2rem);
    font-weight:900;
    text-align:center;
    box-shadow:0 6px 18px rgba(0,0,0,0.15);
}

.sec{
    font-size:1.05rem;
    font-weight:900;
    color:#1D5B2E;
    border-left:5px solid #43A047;
    padding-left:10px;
    margin:16px 0 10px;
}

/* 네비 */
.nav-wrap{
    background:#1D5B2E;
    padding:14px 14px 8px 14px;
    border-radius:0 0 18px 18px;
    margin:-1rem -0.7rem 1rem -0.7rem;
    box-shadow:0 5px 16px rgba(0,0,0,0.22);
}

section.main [data-testid="stHorizontalBlock"]:first-of-type .stButton > button{
    background:transparent !important;
    color:rgba(255,255,255,0.72) !important;
    border:none !important;
    border-radius:0 !important;
    font-size:0.95rem !important;
    font-weight:800 !important;
    min-height:64px !important;
    white-space:pre-line !important;
    border-bottom:4px solid transparent !important;
}

section.main [data-testid="stHorizontalBlock"]:first-of-type .stButton > button:hover{
    background:rgba(255,255,255,0.12)!important;
    color:#fff!important;
}

section.main [data-testid="stHorizontalBlock"]:first-of-type .stButton > button[kind="primary"]{
    background:rgba(255,255,255,0.18)!important;
    color:#fff!important;
    border-bottom:4px solid #A5D6A7!important;
}

/* 버튼 */
.stButton > button{
    width:100%;
    border-radius:10px !important;
    font-weight:800 !important;
    transition:0.15s;
}

.stButton > button:hover{
    transform:translateY(-1px);
}

/* 테이블 */
table{
    width:100% !important;
}

th{
    text-align:center !important;
    font-weight:900 !important;
}

td{
    text-align:center !important;
    vertical-align:middle !important;
}

/* dataframe */
[data-testid="stDataFrame"] div{
    text-align:center !important;
}

/* editor */
[data-testid="stDataEditor"] table{
    text-align:center !important;
}

/* 참가자 태그 */
.p-tag{
    display:inline-block;
    background:#E8F5E9;
    border:1.5px solid #66BB6A;
    border-radius:20px;
    padding:4px 12px;
    margin:3px 4px;
    font-size:.92rem;
    font-weight:700;
    color:#1D5B2E;
}

/* 카드 */
.info-card{
    background:#F9FBF9;
    border:1.5px solid #C8E6C9;
    border-radius:14px;
    padding:12px 16px;
    margin:8px 0;
}

/* 양쪽 균일 */
.equal-box{
    background:#fff;
    border:1px solid #E0E0E0;
    border-radius:14px;
    padding:14px;
    height:100%;
}

/* 모바일 */
@media(max-width:640px){
    .block-container{
        padding:0.3rem 0.25rem 2rem !important;
    }
}
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
# 파일
# ══════════════════════════════════════════════════════════════
RANK_FILE   = "ranking_master.csv"
MEMBER_FILE = "member_roster.json"
TOUR_FILE   = "tournaments.json"

ADMIN_PW = "0502"

COLS_RANK = [
    "랭킹","이름","현재포인트","3월 포인트",
    "결과","부과점","그룹","비고"
]

# ══════════════════════════════════════════════════════════════
# 데이터 함수
# ══════════════════════════════════════════════════════════════
def load_rank():
    if not os.path.exists(RANK_FILE):
        return pd.DataFrame(columns=COLS_RANK)

    df = pd.read_csv(RANK_FILE)

    for c in ["현재포인트","3월 포인트","부과점"]:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce").fillna(0)

    if "현재포인트" in df.columns:
        df = df.sort_values("현재포인트", ascending=False).reset_index(drop=True)
        df["랭킹"] = df.index + 1

    return df.fillna("")


def save_rank(df):
    if "현재포인트" in df.columns:
        df["현재포인트"] = pd.to_numeric(
            df["현재포인트"], errors="coerce"
        ).fillna(0)

        df = df.sort_values(
            "현재포인트",
            ascending=False
        ).reset_index(drop=True)

        df["랭킹"] = df.index + 1

    df.to_csv(RANK_FILE, index=False)


def load_members():
    if os.path.exists(MEMBER_FILE):
        with open(MEMBER_FILE, "r", encoding="utf-8") as f:
            return json.load(f)

    df = load_rank()

    if "이름" in df.columns:
        return df["이름"].tolist()

    return []


def save_members(names):
    with open(MEMBER_FILE, "w", encoding="utf-8") as f:
        json.dump(names, f, ensure_ascii=False, indent=2)


def to_excel(df):
    bio = BytesIO()
    with pd.ExcelWriter(bio, engine="openpyxl") as writer:
        df.to_excel(writer, index=False)
    return bio.getvalue()


# ══════════════════════════════════════════════════════════════
# 세션
# ══════════════════════════════════════════════════════════════
if "menu" not in st.session_state:
    st.session_state.menu = "ranking"

if "is_admin" not in st.session_state:
    st.session_state.is_admin = False


# ══════════════════════════════════════════════════════════════
# 네비
# ══════════════════════════════════════════════════════════════
st.markdown('<div class="nav-wrap">', unsafe_allow_html=True)

menus = [
    ("ranking","🏆\n두류 랭킹"),
    ("admin","⚙️\n관리자")
]

cols = st.columns(len(menus))

for col, (key, label) in zip(cols, menus):

    active = st.session_state.menu == key

    with col:
        if st.button(
            label,
            key=f"menu_{key}",
            type="primary" if active else "secondary",
            use_container_width=True
        ):
            st.session_state.menu = key
            st.rerun()

st.markdown("</div>", unsafe_allow_html=True)

M = st.session_state.menu

# ══════════════════════════════════════════════════════════════
# 1. 랭킹
# ══════════════════════════════════════════════════════════════
if M == "ranking":

    st.markdown(
        "<div class='main-hdr'>🏆 두류 랭킹</div>",
        unsafe_allow_html=True
    )

    df = load_rank()

    if df.empty:
        st.warning("등록된 랭킹 데이터가 없습니다.")
    else:

        icons = ["🥇","🥈","🥉"]

        show_df = df.copy()

        show_df.insert(
            0,
            "순위",
            [icons[i] if i < 3 else str(i+1)
             for i in range(len(show_df))]
        )

        st.dataframe(
            show_df,
            use_container_width=True,
            hide_index=True
        )

        st.download_button(
            "📥 랭킹 엑셀 다운로드",
            data=to_excel(df),
            file_name=f"두류랭킹_{date.today()}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )

# ══════════════════════════════════════════════════════════════
# 2. 관리자
# ══════════════════════════════════════════════════════════════
elif M == "admin":

    st.markdown(
        "<div class='main-hdr'>⚙️ 관리자 센터</div>",
        unsafe_allow_html=True
    )

    pw = st.text_input(
        "🔒 관리자 비밀번호",
        type="password"
    )

    if pw == ADMIN_PW:
        st.session_state.is_admin = True

    if not st.session_state.is_admin:

        if pw and pw != ADMIN_PW:
            st.error("❌ 비밀번호가 틀렸습니다.")

        st.stop()

    st.success("✅ 관리자 모드 활성화")

    tabs = st.tabs([
        "📋 랭킹 관리",
        "👥 회원명부"
    ])

    # ══════════════════════════════════════════════════════════
    # 랭킹 관리
    # ══════════════════════════════════════════════════════════
    with tabs[0]:

        left, right = st.columns(2)

        # ─────────────────────────────────────
        # 업로드
        # ─────────────────────────────────────
        with left:

            st.markdown(
                "<div class='equal-box'>",
                unsafe_allow_html=True
            )

            st.markdown(
                "<div class='sec'>📥 엑셀 업로드</div>",
                unsafe_allow_html=True
            )

            st.caption("""
            업로드 가능 형식:
            XLSX / CSV
            """)

            up = st.file_uploader(
                "랭킹 파일 선택",
                type=["xlsx","csv"]
            )

            if up:

                try:

                    if up.name.endswith(".xlsx"):
                        df_up = pd.read_excel(up)
                    else:
                        df_up = pd.read_csv(
                            up,
                            encoding_errors="replace"
                        )

                    df_up.columns = [
                        str(c).strip()
                        for c in df_up.columns
                    ]

                    if "현재포인트" in df_up.columns:

                        df_up["현재포인트"] = pd.to_numeric(
                            df_up["현재포인트"],
                            errors="coerce"
                        ).fillna(0)

                        df_up = df_up.sort_values(
                            "현재포인트",
                            ascending=False
                        ).reset_index(drop=True)

                        df_up["랭킹"] = df_up.index + 1

                    st.dataframe(
                        df_up,
                        use_container_width=True,
                        hide_index=True
                    )

                    if st.button(
                        "💾 랭킹 저장",
                        type="primary"
                    ):

                        save_rank(df_up)

                        if "이름" in df_up.columns:
                            save_members(
                                df_up["이름"]
                                .astype(str)
                                .str.strip()
                                .tolist()
                            )

                        st.success(
                            "✅ 랭킹 저장 완료!"
                        )

                        st.rerun()

                except Exception as e:
                    st.error(f"파일 오류: {e}")

            st.markdown("</div>", unsafe_allow_html=True)

        # ─────────────────────────────────────
        # 다운로드
        # ─────────────────────────────────────
        with right:

            st.markdown(
                "<div class='equal-box'>",
                unsafe_allow_html=True
            )

            st.markdown(
                "<div class='sec'>📥 랭킹 다운로드</div>",
                unsafe_allow_html=True
            )

            current_df = load_rank()

            if current_df.empty:
                st.info("다운로드할 랭킹 데이터가 없습니다.")
            else:

                st.dataframe(
                    current_df.head(10),
                    use_container_width=True,
                    hide_index=True
                )

                st.download_button(
                    "⬇️ 엑셀 다운로드",
                    data=to_excel(current_df),
                    file_name=f"두류랭킹_{date.today()}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True
                )

            st.markdown("</div>", unsafe_allow_html=True)

        st.divider()

        # ─────────────────────────────────────
        # 수정
        # ─────────────────────────────────────
        st.markdown(
            "<div class='sec'>✏️ 랭킹 직접 수정</div>",
            unsafe_allow_html=True
        )

        df_edit = load_rank()

        if df_edit.empty:
            st.info("수정할 데이터가 없습니다.")
        else:

            edited = st.data_editor(
                df_edit,
                use_container_width=True,
                hide_index=True,
                num_rows="dynamic",
                key="rank_editor"
            )

            c1, c2 = st.columns(2)

            with c1:
                if st.button(
                    "💾 수정 저장",
                    type="primary",
                    use_container_width=True
                ):

                    save_rank(edited)

                    if "이름" in edited.columns:
                        save_members(
                            edited["이름"]
                            .astype(str)
                            .str.strip()
                            .tolist()
                        )

                    st.success("✅ 수정 저장 완료!")
                    st.rerun()

            with c2:
                st.download_button(
                    "📥 수정본 다운로드",
                    data=to_excel(edited),
                    file_name=f"두류랭킹_수정본_{date.today()}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True
                )

    # ══════════════════════════════════════════════════════════
    # 회원명부
    # ══════════════════════════════════════════════════════════
    with tabs[1]:

        st.markdown(
            "<div class='sec'>👥 현재 회원명부</div>",
            unsafe_allow_html=True
        )

        roster = load_members()

        if not roster:
            st.info("등록된 회원명부가 없습니다.")
        else:

            st.success(f"총 {len(roster)}명")

            tags = "".join([
                f'<span class="p-tag">{n}</span>'
                for n in roster
            ])

            st.markdown(
                f"<div style='line-height:2.3'>{tags}</div>",
                unsafe_allow_html=True
            )
