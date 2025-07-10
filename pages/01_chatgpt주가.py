import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objs as go
from datetime import datetime, timedelta

# 1. 시가총액 Top 10 기업 목록 (2025 기준)
top10_companies = {
    'Apple (AAPL)': 'AAPL',
    'Microsoft (MSFT)': 'MSFT',
    'Alphabet (GOOGL)': 'GOOGL',
    'Amazon (AMZN)': 'AMZN',
    'NVIDIA (NVDA)': 'NVDA',
    'Meta (META)': 'META',
    'Berkshire Hathaway (BRK-B)': 'BRK-B',
    'Eli Lilly (LLY)': 'LLY',
    'Visa (V)': 'V',
    'TSMC (TSM)': 'TSM'
}

# 2. Streamlit UI
st.title("📊 시가총액 Top 10 기업 - 최근 3년 주가 (Plotly 그래프)")

selected = st.multiselect("기업을 선택하세요 (복수 선택 가능)", options=list(top10_companies.keys()), default=['Apple (AAPL)', 'Microsoft (MSFT)'])

if selected:
    # 3. 기간 설정
    end_date = datetime.today()
    start_date = end_date - timedelta(days=3*365)

    # 4. Plotly 그래프 객체 생성
    fig = go.Figure()
    
    for name in selected:
        ticker = top10_companies[name]
        df = yf.download(ticker, start=start_date, end=end_date)
        if not df.empty:
            fig.add_trace(go.Scatter(
                x=df.index,
                y=df['Close'],
                mode='lines',
                name=name
            ))
        else:
            st.warning(f"{name}의 데이터를 불러올 수 없습니다.")

    # 5. 그래프 레이아웃 설정
    fig.update_layout(
        title="최근 3년간 주가 비교 (종가 기준)",
        xaxis_title="날짜",
        yaxis_title="주가 ($)",
        hovermode="x unified",
        template="plotly_white"
    )

    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("기업을 하나 이상 선택해주세요.")
