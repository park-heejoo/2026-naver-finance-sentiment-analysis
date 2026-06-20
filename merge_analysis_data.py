import os
import pandas as pd

def merge_perfect_holiday_handling(sentiment_csv, stock_csv, output_csv):
    if not os.path.exists(sentiment_csv) or not os.path.exists(stock_csv):
        print("❌ 파일 경로를 다시 확인해주세요.")
        return

    print("🔄 [돌발 공휴일 & 주말 완벽 방어 모드] 데이터 병합을 시작합니다...")
    
    # 1. 감정 지수 로드 (31일 전체 데이터 존재)
    df_sentiment = pd.read_csv(sentiment_csv)
    df_sentiment['Date'] = pd.to_datetime(df_sentiment['Date'])
    
    # 2. 주가 데이터 로드 (개장일만 존재)
    df_stock = pd.read_csv(stock_csv)
    df_stock['Date'] = pd.to_datetime(df_stock['Date'])
    
    # 3. 🎯 [핵심] 주가 데이터의 '실제 개장일 날짜 목록'만 따로 추출
    trading_days = pd.DataFrame({'Date': df_stock['Date'], 'Is_Trading_Day': True})
    
    # 4. 감정 데이터(31일)와 개장일 목록을 날짜 기준으로 먼저 정렬 결합
    df_merged = pd.merge(df_sentiment, trading_days, on='Date', how='left')
    df_merged.sort_values(by='Date', ascending=True, inplace=True)
    
    # 5. 🔥 [질문자님 아이디어 구현] 
    # 주가 데이터가 없는 날(주말/공휴일)의 행에 '그 다음으로 가장 가까운 개장일 날짜'를 매칭해줍니다.
    # 판다스의 bfill(backward fill)을 쓰면 뒤(미래)에 있는 개장일 날짜가 앞으로 슥 당겨져서 채워집니다.
    df_merged['Target_Trading_Date'] = df_merged['Date'].where(df_merged['Is_Trading_Day'] == True)
    df_merged['Target_Trading_Date'] = df_merged['Target_Trading_Date'].bfill()
    
    # 만약 한 달의 맨 마지막 날들이 휴일이라 뒤에서 채워줄 개장일이 없다면 제거
    df_merged.dropna(subset=['Target_Trading_Date'], inplace=True)
    
    # 6. 🎯 'Target_Trading_Date'를 기준으로 감정 지수 그룹화 후 평균(mean) 내기
    # 이 작업을 통해 주말뿐만 아니라 평일 공휴일에 쌓인 감정도 다음 개장일 아침으로 완벽히 누적 통합됩니다!
    df_sentiment_grouped = df_merged.groupby('Target_Trading_Date')['Sentiment_Index'].mean().reset_index()
    df_sentiment_grouped.columns = ['Date', 'Sentiment_Index']
    
    # 주말/공휴일이 합산되었으므로 다시 0~100점 재정규화 (Scaling)
    min_val = df_sentiment_grouped['Sentiment_Index'].min()
    max_val = df_sentiment_grouped['Sentiment_Index'].max()
    df_sentiment_grouped['Scaled_Index'] = ((df_sentiment_grouped['Sentiment_Index'] - min_val) / (max_val - min_val)) * 100
    df_sentiment_grouped['Scaled_Index'] = df_sentiment_grouped['Scaled_Index'].round(2)

    # 7. 실제 주가 데이터와 병합
    df_final = pd.merge(df_sentiment_grouped, df_stock, on='Date', how='inner')
    df_final.sort_values(by='Date', ascending=True, inplace=True)
    
    # 8. [시차 적용] 오늘의 누적 감정 ➡️ 다음 개장일 주가 등락률 예측
    df_final['Next_Day_Change'] = df_final['Change'].shift(-1)
    df_final.dropna(subset=['Next_Day_Change'], inplace=True)
    
    # 9. 마스터 마켓 데이터셋 저장
    df_final.to_csv(output_csv, index=False, encoding='utf-8-sig')
    print("=" * 60)
    print(f"🎉 최종 마스터 데이터셋 생성 완료! ➡️ {output_csv}")
    print(f"📊 최종 분석 가능 일수: {len(df_final)}일")
    print("=" * 60)
    print(df_final[['Date', 'Scaled_Index', 'Close', 'Change', 'Next_Day_Change']].head(7))

if __name__ == '__main__':
    merge_perfect_holiday_handling(
        sentiment_csv='daily_sentiment_000660_SK하이닉스.csv', # 원본 2점대 파일
        stock_csv='krx_stock_042700_한미반도체.csv',
        output_csv='spillover_hynix_to_hanmi.csv'
    )