import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta
import plotly.express as px

# 페이지 설정
st.set_page_config(
    page_title="나스닥 100 시총 Top 10 기업 주가 현황",
    page_icon="📈",
    layout="wide"
)

# NASDAQ 100 시총 Top 10 기업 (현재 기준, 변동 가능)
# 실제 시총 Top 10은 변동이 있으므로, 자주 업데이트되는 리스트를 참고하여 수동으로 최신화 필요
# 2025년 7월 현재 기준 NASDAQ 100 시총 상위 기업들 (예시)
NASDAQ_TOP_10_COMPANIES = {
    "Microsoft": "MSFT",        # 소프트웨어 및 클라우드 서비스 제공. 윈도우, 오피스, 애저 클라우드 등.
    "Apple": "AAPL",            # 아이폰, 맥, 아이패드 등 혁신적인 가전제품과 서비스 제공. 전 세계적인 브랜드 인지도.
    "NVIDIA": "NVDA",           # 인공지능 및 그래픽 처리 장치(GPU) 시장 선도. 데이터 센터 및 게임 분야 핵심 기술.
    "Amazon": "AMZN",           # 세계 최대 온라인 소매업체. 클라우드 컴퓨팅(AWS) 및 디지털 콘텐츠 서비스 제공.
    "Alphabet (Class A)": "GOOGL", # 구글 검색 엔진, 유튜브, 안드로이드 등 다양한 인터넷 기반 서비스 제공.
    "Meta Platforms": "META",   # 페이스북, 인스타그램, 왓츠앱 등 소셜 미디어 플랫폼 운영. 메타버스 기술 투자.
    "Tesla": "TSLA",            # 전기 자동차 및 에너지 저장 시스템 제조. 자율주행 기술 개발 선도.
    "Broadcom": "AVGO",         # 반도체 및 인프라 소프트웨어 솔루션 제공. 광범위한 네트워킹 기술.
    "Costco Wholesale": "COST", # 회원제 창고형 할인점 운영. 다양한 고품질 상품을 저렴하게 판매.
    "PepsiCo": "PEP"            # 음료 및 스낵류 제조. 펩시, 게토레이, 트로피카나 등 세계적인 브랜드 보유.
}

@st.cache_data
def get_stock_data(ticker, start_date, end_date):
    """주식 데이터를 지정된 기간으로 가져오는 함수"""
    try:
        stock = yf.Ticker(ticker)
        data = stock.history(start=start_date, end=end_date)
        return data
    except Exception as e:
        st.error(f"{ticker} 데이터를 가져오는 중 오류 발생: {e}")
        return None

@st.cache_data
def get_company_info(ticker):
    """회사 정보를 가져오는 함수"""
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        return {
            'name': info.get('longName', 'N/A'),
            'sector': info.get('sector', 'N/A'),
            'industry': info.get('industry', 'N/A'), # 산업 추가
            'marketCap': info.get('marketCap', 0),
            'currentPrice': info.get('currentPrice', 0),
            'summary': info.get('longBusinessSummary', 'N/A') # 기업 개요 추가
        }
    except Exception as e:
        # st.warning(f"{ticker} 회사 정보 가져오기 실패: {e}") # 디버깅용
        return {'name': 'N/A', 'sector': 'N/A', 'industry': 'N/A', 'marketCap': 0, 'currentPrice': 0, 'summary': 'N/A'}

def format_market_cap(market_cap):
    """시가총액을 읽기 쉬운 형태로 변환"""
    if market_cap >= 1e12:
        return f"${market_cap/1e12:.2f}T"
    elif market_cap >= 1e9:
        return f"${market_cap/1e9:.2f}B"
    elif market_cap >= 1e6:
        return f"${market_cap/1e6:.2f}M"
    else:
        return f"${market_cap:,.0f}"

def truncate_summary(summary, max_lines=2):
    """기업 개요를 2줄로 자르는 함수"""
    sentences = summary.replace('\n', ' ').split('.')
    truncated = []
    line_count = 0
    for sentence in sentences:
        if sentence.strip():
            truncated.append(sentence.strip() + '.')
            line_count += 1
            if line_count >= max_lines:
                break
    return " ".join(truncated).replace("..", ".").strip() # 중복 마침표 제거 및 정리

def main():
    st.title("📈 나스닥 100 시총 Top 10 기업 주가 현황")
    st.markdown("올해 1월 1일 기준 비교 상승률과 함께 주요 기업들의 정보를 확인해보세요.")
    
    # 사이드바에서 기업 선택
    st.sidebar.header("기업 선택")
    selected_companies = st.sidebar.multiselect(
        "분석할 기업을 선택하세요:",
        options=list(NASDAQ_TOP_10_COMPANIES.keys()),
        default=list(NASDAQ_TOP_10_COMPANIES.keys())[:3]  # 기본으로 3개 선택
    )
    
    if not selected_companies:
        st.warning("최소 하나의 기업을 선택해주세요.")
        return
    
    # 날짜 범위 설정 (올해 1월 1일부터 현재까지)
    current_year = datetime.now().year
    start_date = datetime(current_year, 1, 1)
    end_date = datetime.now()
    
    # 데이터 로딩
    with st.spinner("데이터를 불러오는 중..."):
        stock_data = {}
        company_info = {}
        
        for company in selected_companies:
            ticker = NASDAQ_TOP_10_COMPANIES[company]
            data = get_stock_data(ticker, start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d'))
            info = get_company_info(ticker)
            
            if data is not None and not data.empty:
                stock_data[company] = data
                company_info[company] = info
    
    if not stock_data:
        st.error("선택한 기업의 데이터를 불러올 수 없습니다. 기간 내 주식 데이터가 없거나, 야후 파이낸스 API 문제일 수 있습니다.")
        return
    
    # 회사 정보 표시 및 기업 개요
    st.header("📊 선택된 기업 정보")
    
    for company in selected_companies:
        if company in company_info:
            info = company_info[company]
            st.subheader(f"**{company} ({NASDAQ_TOP_10_COMPANIES[company]})**")
            cols = st.columns(3)
            with cols[0]:
                st.metric(label="현재 가격", value=f"${info['currentPrice']:.2f}")
            with cols[1]:
                st.metric(label="시가총액", value=f"{format_market_cap(info['marketCap'])}")
            with cols[2]:
                st.metric(label="섹터", value=info['sector'])
            
            summary_text = truncate_summary(info['summary'])
            st.markdown(f"**기업 개요**: {summary_text if summary_text != 'N/A' else '정보 없음'}")
            st.markdown("---") # 구분선
    
    # 비교 상승률 차트
    st.header("📈 올해 (1월 1일 기준) 비교 상승률 차트")
    
    fig_growth = go.Figure()
    colors = px.colors.qualitative.Set1[:len(selected_companies)]
    
    for i, (company, data) in enumerate(stock_data.items()):
        if not data.empty and data['Close'].iloc[0] != 0: # 0으로 나누는 오류 방지
            # 첫 날 종가를 기준으로 정규화
            normalized_data = (data['Close'] / data['Close'].iloc[0] - 1) * 100
            
            fig_growth.add_trace(go.Scatter(
                x=data.index,
                y=normalized_data,
                mode='lines',
                name=company,
                line=dict(color=colors[i], width=2),
                hovertemplate=f'<b>{company}</b><br>' +
                                'Date: %{x}<br>' +
                                '상승률: %{y:.2f}%<br>' +
                                '<extra></extra>'
            ))
    
    fig_growth.update_layout(
        title=f"올해 ({current_year}년 1월 1일 기준) 주가 상승률 비교",
        xaxis_title="날짜",
        yaxis_title="상승률 (%)",
        hovermode='x unified',
        height=600,
        template='plotly_white'
    )
    
    st.plotly_chart(fig_growth, use_container_width=True)
    
    # 거래량 차트
    st.header("📊 거래량 분석")
    
    fig_volume = go.Figure()
    
    for i, (company, data) in enumerate(stock_data.items()):
        fig_volume.add_trace(go.Scatter(
            x=data.index,
            y=data['Volume'],
            mode='lines',
            name=company,
            line=dict(color=colors[i % len(colors)], width=2),
            hovertemplate=f'<b>{company}</b><br>' +
                            'Date: %{x}<br>' +
                            'Volume: %{y:,.0f}<br>' +
                            '<extra></extra>'
        ))
    
    fig_volume.update_layout(
        title=f"거래량 추이 - {start_date.strftime('%Y.%m.%d')} ~ {end_date.strftime('%Y.%m.%d')}",
        xaxis_title="날짜",
        yaxis_title="거래량",
        hovermode='x unified',
        height=400,
        template='plotly_white'
    )
    
    st.plotly_chart(fig_volume, use_container_width=True)
    
    # 추가 정보
    st.header("ℹ️ 추가 정보")
    st.info("""
    **데이터 소스**: Yahoo Finance
    
    **주의사항**: 
    - 이 데이터는 투자 조언이 아닙니다.
    - 실제 투자 전에 전문가와 상담하세요.
    - 과거 성과가 미래 성과를 보장하지 않습니다.
    """)

if __name__ == "__main__":
    main()
