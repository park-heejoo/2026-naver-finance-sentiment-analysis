import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# 한글 깨짐 방지 설정
plt.rcParams['font.family'] = 'Malgun Gothic'
plt.rcParams['axes.unicode_minus'] = False

def plot_shock_wave(hynix_csv, hanmi_csv, dongjin_csv, event_date, window_days=6):
    # 1. 데이터 불러오기 및 정렬
    df_hynix = pd.read_csv(hynix_csv).sort_values('Date')
    df_hanmi = pd.read_csv(hanmi_csv).sort_values('Date')
    df_dongjin = pd.read_csv(dongjin_csv).sort_values('Date')
    
    # 데이터 병합
    df_m = pd.merge(df_hynix[['Date', 'Change', 'Sentiment_Index']], 
                    df_hanmi[['Date', 'Change', 'Sentiment_Index']], on='Date', suffixes=('_hynix', '_hanmi'))
    df_m = pd.merge(df_m, df_dongjin[['Date', 'Change', 'Sentiment_Index']], on='Date')
    df_m.rename(columns={'Change': 'Change_dongjin', 'Sentiment_Index': 'Sentiment_Index_dongjin'}, inplace=True)
    
    df_m['Date'] = pd.to_datetime(df_m['Date'])
    target_date = pd.to_datetime(event_date)
    target_idx = df_m[df_m['Date'] == target_date].index[0]
    
    # 전후 window_days만큼 슬라이싱
    df_event = df_m.iloc[target_idx - window_days : target_idx + window_days + 1].copy()
    
    x = np.arange(len(df_event))
    dates_str = df_event['Date'].dt.strftime('%m-%d').values # 가독성을 위해 월-일로 표현
    
    # 2. 그래프 그리기 (상단: 주가 변동률 / 하단: 심리 점수)
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(13, 10), sharex=True)
    
    # 📈 상단 그래프: 주가 등락률 추이 (시차 증명용)
    ax1.plot(x, df_event['Change_hynix'], marker='o', color='#ff7f0e', linewidth=2.5, label='SK하이닉스 주가')
    ax1.plot(x, df_event['Change_hanmi'], marker='s', color='#1f77b4', linewidth=2, label='한미반도체 주가')
    ax1.plot(x, df_event['Change_dongjin'], marker='^', color='#2ca02c', linewidth=2, label='동진쎄미켐 주가')
    
    # 🌟 기준 사건일(8월 12일) 세로 점선 표시
    target_loc = window_days
    ax1.axvline(x=target_loc, color='red', linestyle='--', linewidth=1.5, label=f'모건스탠리 쇼크일 ({event_date})')
    ax1.set_title('모건스탠리 쇼크 전후 반도체 밸류체인 주가 및 심리 충격파 (시차 분석)', fontsize=14, fontweight='bold', pad=15)
    ax1.set_ylabel('주가 등락률 (%)', fontsize=11)
    ax1.grid(True, linestyle=':', alpha=0.6)
    ax1.legend(loc='upper right', fontsize=10)
    
    # 📊 하단 그래프: 종토방 심리 점수 추이 (지속성 증명용)
    ax2.plot(x, df_event['Sentiment_Index_hynix'], marker='o', color='#ff7f0e', linestyle=':', linewidth=2, label='SK하이닉스 심리')
    ax2.plot(x, df_event['Sentiment_Index_hanmi'], marker='s', color='#1f77b4', linestyle=':', linewidth=2, label='한미반도체 심리')
    ax2.plot(x, df_event['Sentiment_Index_dongjin'], marker='^', color='#2ca02c', linestyle=':', linewidth=2, label='동진쎄미켐 심리')
    
    ax2.axvline(x=target_loc, color='red', linestyle='--', linewidth=1.5)
    ax2.set_xlabel('날짜 (월-일)', fontsize=11, labelpad=10)
    ax2.set_ylabel('종토방 감정 점수 (KOBERT 원본)', fontsize=11)
    ax2.set_xticks(x)
    ax2.set_xticklabels(dates_str, rotation=0)
    ax2.grid(True, linestyle=':', alpha=0.6)
    ax2.legend(loc='upper right', fontsize=10)
    
    plt.tight_layout()
    plt.savefig('sector_shock_wave.png', dpi=300)
    plt.close()
    
    print("🎯 [완료] 8월 12일 쇼크 정밀 시차 분석 그래프가 저장되었습니다! (sector_shock_wave.png)")

if __name__ == '__main__':
    plot_shock_wave(
        hynix_csv='final_analysis_data_000660_SK하이닉스.csv',
        hanmi_csv='final_analysis_data_042700_한미반도체.csv',
        dongjin_csv='final_analysis_data_005290_동진쎄미켐.csv',
        event_date='2021-08-12'
    )