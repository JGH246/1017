# app.py
import streamlit as st
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(page_title="서울 연도별 기온", page_icon="🌡️", layout="wide")


@st.cache_data
def load_data(path: str = "seoul_temperature.csv") -> pd.DataFrame:
    df = pd.read_csv(path)

    # 1) 날짜 값 앞의 탭 문자 제거 (예: "\t2024-01-01" → "2024-01-01")
    df["날짜"] = df["날짜"].str.strip("\t")
    df["날짜"] = pd.to_datetime(df["날짜"])

    # 2) 날짜별 중복 행이 있으면 평균으로 통합
    df = df.groupby("날짜", as_index=False).mean(numeric_only=True)
    return df


df = load_data()

# 연도별 평균기온
yearly = df.groupby(df["날짜"].dt.year)["평균기온(℃)"].mean().sort_index()
# 5년 이동평균
ma5 = yearly.rolling(window=5, min_periods=1).mean()
years = yearly.index.astype(int)

# --- 사이드바: 연도 범위 슬라이더 ---
min_year, max_year = st.sidebar.slider(
    "연도 범위",
    min_value=int(yearly.index.min()),
    max_value=int(yearly.index.max()),
    value=(int(yearly.index.min()), int(yearly.index.max())),
)

# 선택 구간 필터링
sel_mask = (df["날짜"].dt.year >= min_year) & (df["날짜"].dt.year <= max_year)
sel_df = df[sel_mask]

# 선택 구간 기상 요약
avg_temp = sel_df["평균기온(℃)"].mean()
avg_max = sel_df["최고기온(℃)"].mean()
avg_min = sel_df["최저기온(℃)"].mean()
n_days = len(sel_df)

# --- 그래프 (연도별 평균 + 5년 이동평균) ---
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
    title="서울 연평균기온과 5년 이동평균 (℃)",
    xaxis_title="연도",
    yaxis_title="기온 (℃)",
    hovermode="x unified",
    margin=dict(l=40, r=20, t=40, b=30),
)
st.plotly_chart(fig, use_container_width=True)

# --- 선택 구간 요약 ---
st.subheader("선택 구간 요약")
c1, c2, c3, c4 = st.columns(4)
c1.metric("연도 범위", f"{min_year}년 ~ {max_year}년")
c2.metric("평균기온", f"{avg_temp:.2f} ℃")
c3.metric("평균 최고기온", f"{avg_max:.2f} ℃")
c4.metric("평균 최저기온", f"{avg_min:.2f} ℃")
st.caption(f"선택 구간 데이터 수: {n_days}일")
