import os
import pandas as pd
import matplotlib.pyplot as plt

def create_dual_axis_chart(final_csv, output_img):
    # 1. 파일 존재 여부 확인
    if not os.path.exists(final_csv):
        print(f"❌ '{final_csv}' 파일이 없습니다. 먼저 merge_advanced_v3.py를 실행해주세요.")
        return

    # 2. 데이터 로드 및 날짜 기준 오름차순 정렬
    df = pd.read_csv(final_csv)
    df['Date'] = pd.to_datetime(df['Date'])
    df.sort_values('Date', ascending=True, inplace=True)

    # 3. 한글 깨짐 방지 폰트 설정 (윈도우 환경 기준)
    plt.rcParams['font.family'] = 'Malgun Gothic'  # 맥북을 쓰신다면 'AppleGothic'으로 변경하세요.
    plt.rcParams['axes.unicode_minus'] = False     # 마이너스 기호 깨짐 방지

    # 4. 그래프 틀 생성 (figure 대신 subplots 사용 규격 준수)
    fig, ax1 = plt.subplots(figsize=(14, 7))

    # 🔵 [첫 번째 축: 왼쪽] 실제 주가 종가 (원) - 실선 그래프
    color_stock = '#1f77b4'  # 신뢰감을 주는 블루 계열
    ax1.set_xlabel('날짜 (Date)', fontsize=12, labelpad=10)
    ax1.set_ylabel('주가 종가 (원)', color=color_stock, fontsize=12, labelpad=10)
    ax1.plot(df['Date'], df['Close'], color=color_stock, marker='o', linewidth=2, label='주가 종가')
    ax1.tick_params(axis='y', labelcolor=color_stock)
    ax1.grid(True, linestyle='--', alpha=0.5)  # 배경 점선 추가로 가독성 업

    # 🟠 [두 번째 축: 오른쪽] 정규화 감정 지수 (0~100) - 점선 그래프
    ax2 = ax1.twinx()  # X축(날짜)을 공유하는 새로운 Y축 생성
    color_sentiment = '#ff7f0e'  # 주황색 계열로 블루와 대비 극대화
    ax2.set_ylabel('누적 정규화 감정 지수 (0~100)', color=color_sentiment, fontsize=12, labelpad=10)
    ax2.plot(df['Date'], df['Scaled_Index'], color=color_sentiment, marker='x', linestyle='--', linewidth=2, label='감정 지수')
    ax2.tick_params(axis='y', labelcolor=color_sentiment)

    # 5. 그래프 제목 및 레이아웃 최적화
    plt.title('SK하이닉스 주가 추이 vs 종토방 일일 감정 지수 (2021년 8월 1~31일)', fontsize=15, fontweight='bold', pad=15)
    
    # 텍스트나 레이블이 잘리지 않도록 자동 조절
    fig.tight_layout()
    
    # 6. 고해상도 이미지 파일로 저장 (show를 사용하지 않고 저장)
    plt.savefig(output_img, dpi=300)
    print("=" * 60)
    print(f"🎉 이중 축 시각화 그래프 생성 완료! ➡️ {output_img}")
    print("=" * 60)

if __name__ == '__main__':
    # 공휴일이 완벽 처리된 최종 마스터 파일명을 입력합니다.
    # 만약 파일명이 다르면 실제 파일명에 맞게 수정해주세요.
    create_dual_axis_chart('final_analysis_data_000660_SK하이닉스.csv', 'sentiment_chart_000660_SK하이닉스.png')