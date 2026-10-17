# app.py
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import streamlit.components.v1 as components

st.set_page_config(
    page_title="서울 연평균 기온",
    page_icon="🌡️",
    layout="wide",
)

# ============ 테마 토글 (다크 모드) ============
dark = st.sidebar.toggle("🌓 다크 모드", value=False)

st.markdown(
    f"""
    <script>
    (function() {{
        function applyTheme(dark) {{
            var root = document.querySelector('.stApp');
            if (root) root.classList.toggle('dark-mode', !!dark);
        }}
        applyTheme({str(dark).lower()});
        var ready = document.readyState;
        if (ready === 'complete' || ready === 'interactive') {{
            applyTheme({str(dark).lower()});
        }} else {{
            document.addEventListener('DOMContentLoaded', function() {{
                applyTheme({str(dark).lower()});
            }});
        }}
    }})();
    </script>
    """,
    unsafe_allow_html=True,
)

# ============ 커스텀 CSS ============
st.markdown(
    """
    <style>
    .stApp {
        font-family: "Pretendard", "Noto Sans KR", "Apple SD Gothic Neo", sans-serif;
    }
    .stApp .stMarkdown h1 {
        font-weight: 800;
        letter-spacing: -0.03em;
    }
    .stApp .stMarkdown h2 {
        font-weight: 700;
    }
    .card {
        background: #f8fafc;
        border: 1px solid #e5e7eb;
        border-radius: 12px;
        padding: 16px;
    }
    .stApp.dark-mode {
        --card-bg: #161b22;
        --border: #30363d;
        --bg: #0f1115;
        --text: #e5e7eb;
        --muted: #9ca3af;
        background-color: var(--bg) !important;
        color: var(--text) !important;
    }
    .stApp.dark-mode .stSidebar {
        background: #111318 !important;
    }
    .stApp.dark-mode .stSidebar .stMetricValue {
        color: var(--text) !important;
    }
    .stApp.dark-mode .stMetricLabel {
        color: var(--muted) !important;
    }
    .stApp.dark-mode .stSlider > div {
        color: var(--text) !important;
    }
    .stApp.dark-mode .stDataFrame {
        background: var(--card-bg) !important;
        color: var(--text) !important;
    }
    .stApp.dark-mode .stDataFrame td,
    .stApp.dark-mode .stDataFrame th {
        border-color: var(--border) !important;
    }
    .stApp.dark-mode .stTable th,
    .stApp.dark-mode .stTable td {
        color: var(--text) !important;
        border-color: var(--border) !important;
    }
    .stApp.dark-mode .stSelectbox label,
    .stApp.dark-mode .stTextInput label,
    .stApp.dark-mode .stTextArea label,
    .stApp.dark-mode .stNumberInput label {
        color: #d1d5db !important;
    }
    .stApp.dark-mode .stButton > button {
        color: var(--text) !important;
        background-color: #374151 !important;
        border-color: #4b5563 !important;
    }
    .stApp.dark-mode .stDownloadButton > button {
        color: var(--text) !important;
        background-color: #374151 !important;
        border-color: #4b5563 !important;
    }
    .stApp.dark-mode .stSuccess,
    .stApp.dark-mode .stWarning,
    .stApp.dark-mode .stException {
        color: var(--text) !important;
    }
    .stApp.dark-mode .stCaption {
        color: var(--muted) !important;
    }
    .stApp.dark-mode .stProgress .stProgressBar {
        background-color: #4b5563 !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ============ 데이터 로드 ============
@st.cache_data
def load_data(path: str = "seoul_temperature.csv") -> pd.DataFrame:
    df = pd.read_csv(path, encoding="utf-8-sig")
    df["날짜"] = df["날짜"].str.strip("\t")
    df["날짜"] = pd.to_datetime(df["날짜"])
    df = df.groupby("날짜", as_index=False).mean(numeric_only=True)
    return df


df = load_data()

# 일교차 컬럼 추가
df["일교차"] = df["최고기온(℃)"] - df["최저기온(℃)"]

# 연도별 평균기온
yearly = df.groupby(df["날짜"].dt.year)["평균기온(℃)"].mean().sort_index()
ma5 = yearly.rolling(window=5, min_periods=1).mean()
years = yearly.index.astype(int)

# 월별 히트맵 데이터 (가로축: 월 1~12, 세로축: 연도)
monthly = df.groupby([df["날짜"].dt.year, df["날짜"].dt.month])["평균기온(℃)"].mean().unstack()

# ============ 사이드바 ============
with st.sidebar:
    st.header("🔍 옵션")
    min_year, max_year = st.slider(
        "연도 범위",
        min_value=int(yearly.index.min()),
        max_value=int(yearly.index.max()),
        value=(int(yearly.index.min()), int(yearly.index.max())),
    )
    st.markdown("---")
    st.caption("데이터: seoul_temperature.csv")

# ============ 메인 ============
st.title("🌡️ 서울 연평균 기온")
st.caption("연도별 평균기온 추이 + 월별 히트맵 + 평균 일교차")

# --- 차트 1: 연평균 + 5년 이동평균 ---
st.subheader("연도별 평균기온과 5년 이동평균")
fig = go.Figure()
fig.add_trace(
    go.Scatter(
        x=years,
        y=yearly.values,
        mode="lines+markers",
        name="연평균기온",
        line=dict(color="#1f77b4", width=2),
        marker=dict(size=5),
    )
)
fig.add_trace(
    go.Scatter(
        x=ma5.index.astype(int),
        y=ma5.values,
        mode="lines",
        name="5년 이동평균",
        line=dict(color="#d62728", width=2, dash="dash"),
    )
)
fig.update_layout(
    hovermode="x unified",
    margin=dict(l=40, r=20, t=40, b=30),
)
st.plotly_chart(fig, use_container_width=True)

# --- 차트 2: 월별 히트맵 ---
st.subheader("월별 평균기온 히트맵")
fig_heat = go.Figure(
    go.Heatmap(
        z=monthly.values,
        x=monthly.columns,
        y=monthly.index.astype(int),
        colorscale="purp",
        colorbar_title="평균기온 (℃)",
    )
)
fig_heat.update_layout(
    margin=dict(l=40, r=20, t=40, b=30),
    xaxis_title="월",
    yaxis_title="연도",
)
st.plotly_chart(fig_heat, use_container_width=True)

# --- 차트 3: 연도별 평균 일교차 ---
st.subheader("연도별 평균 일교차")
daily_range_by_year = df.groupby(df["날짜"].dt.year)["일교차"].mean().sort_index()
fig_range = go.Figure(
    go.Scatter(
        x=daily_range_by_year.index.astype(int),
        y=daily_range_by_year.values,
        mode="lines+markers",
        name="평균 일교차",
        line=dict(color="#9467bd", width=2),
        marker=dict(size=5),
    )
)
fig_range.update_layout(
    margin=dict(l=40, r=20, t=40, b=30),
    xaxis_title="연도",
    yaxis_title="일교차 (℃)",
)
st.plotly_chart(fig_range, use_container_width=True)

# --- 선택 구간 요약 카드 ---
with st.container():
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("### 📊 선택 구간 요약")
    min_year, max_year = st.sidebar.slider(
        "연도 범위",
        min_value=int(yearly.index.min()),
        max_value=int(yearly.index.max()),
        value=(int(yearly.index.min()), int(yearly.index.max())),
    )
    sel_mask = (df["날짜"].dt.year >= min_year) & (df["날짜"].dt.year <= max_year)
    sel_df = df[sel_mask]

    avg_temp = sel_df["평균기온(℃)"].mean()
    avg_max = sel_df["최고기온(℃)"].mean()
    avg_min = sel_df["최저기온(℃)"].mean()
    n_days = len(sel_df)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("연도 범위", f"{min_year}년 ~ {max_year}년")
    c2.metric("평균기온", f"{avg_temp:.2f} ℃")
    c3.metric("평균 최고기온", f"{avg_max:.2f} ℃")
    c4.metric("평균 최저기온", f"{avg_min:.2f} ℃")
    st.caption(f"선택 구간 데이터 수: {n_days}일")
    st.markdown('</div>', unsafe_allow_html=True)

# --- 선택 구간 상세 표 ---
st.subheader("선택 구간 상세")
st.dataframe(
    sel_df,
    column_config={
        "날짜": st.column_config.DateColumn("날짜", format="YYYY-MM-DD"),
        "평균기온(℃)": st.column_config.NumberColumn("평균기온", format="%.1f ℃"),
        "최저기온(℃)": st.column_config.NumberColumn("최저기온", format="%.1f ℃"),
        "최고기온(℃)": st.column_config.NumberColumn("최고기온", format="%.1f ℃"),
        "일교차": st.column_config.NumberColumn("일교차", format="%.1f ℃"),
    },
    use_container_width=True,
    height=320,
)

# --- 데이터 다운로드 ---
csv = sel_df.to_csv(index=False).encode("utf-8-sig")
st.download_button(
    "선택 구간 데이터 다운로드 (CSV)",
    data=csv,
    file_name="seoul_selected.csv",
    mime="text/csv",
)

# --- 최고/최저 10일 표 ---
st.subheader("최고기온 상위 10일 / 최저기온 하위 10일")
hot_df = (
    sel_df.nlargest(10, "평균기온(℃)")[
        ["날짜", "평균기온(℃)", "최저기온(℃)", "최고기온(℃)"]
    ]
    .assign(날짜=lambda d: d["날짜"].dt.strftime("%Y-%m-%d"))
)
cold_df = (
    sel_df.nsmallest(10, "평균기온(℃)")[
        ["날짜", "평균기온(℃)", "최저기온(℃)", "최고기온(℃)"]
    ]
    .assign(날짜=lambda d: d["날짜"].dt.strftime("%Y-%m-%d"))
)
c1, c2 = st.columns(2)
with c1:
    st.markdown("### 🔥 최고기온 상위 10일")
    st.dataframe(hot_df, use_container_width=True)
with c2:
    st.markdown("### ❄️ 최저기온 하위 10일")
    st.dataframe(cold_df, use_container_width=True)
