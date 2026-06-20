import os
import pandas as pd

def analyze_correlation(final_csv):
    if not os.path.exists(final_csv):
        print(f"❌ '{final_csv}' 파일이 없습니다. merge_advanced_v3.py를 먼저 실행해주세요.")
        return

    # 1. 완벽 방어 버전 마스터 데이터셋 로드
    df = pd.read_csv(final_csv)
    
    print("=" * 60)
    print(f"📈 [{df['Date'].min()} ~ {df['Date'].max()}] 기간 통계 및 상관관계 분석")
    print(f"📊 분석에 사용된 총 거래일수: {len(df)}일")
    print("=" * 60)

    # 2. 🎯 핵심 상관관계 계산 (피어슨 상관계수)
    # 오늘 감정(Scaled_Index) vs 오늘 주가 등락률(Change)
    corr_same_day = df['Scaled_Index'].corr(df['Change'])
    
    # 오늘 감정(Scaled_Index) vs 내일 주가 등락률(Next_Day_Change) -> 🔥 우리 가설의 핵심!
    corr_next_day = df['Scaled_Index'].corr(df['Next_Day_Change'])

    # 3. 결과 출력
    print(f"💡 [분석 결과 1] 당일 종토방 감정지수 ↔ 당일 주가 등락률 상관계수: {corr_same_day:.4f}")
    print(f"💡 [분석 결과 2] 당일 종토방 감정지수 ↔ 내일 주가 등락률 상관계수: {corr_next_day:.4f}")
    print("-" * 60)
    
    # 4. 추가 인사이트 (감정이 최악/최고일 때 다음 날 실제 주가 움직임 요약)
    worst_day = df.loc[df['Scaled_Index'].idxmin()]
    best_day = df.loc[df['Scaled_Index'].idxmax()]
    
    print(f"🚨 [공포 모멘텀] 한 달 중 감정이 가장 낮았던 날 ({worst_day['Date']}):")
    print(f"   - 당일 감정지수: {worst_day['Scaled_Index']}점 (최악)")
    print(f"   - 당일 주가등락: {worst_day['Change']:.2f}%")
    print(f"   - 다음날 주가등락: {worst_day['Next_Day_Change']:.2f}%")
    print("-" * 60)
    
    print(f"🚀 [환호 모멘텀] 한 달 중 감정이 가장 높았던 날 ({best_day['Date']}):")
    print(f"   - 당일 감정지수: {best_day['Scaled_Index']}점 (최고)")
    print(f"   - 당일 주가등락: {best_day['Change']:.2f}%")
    print(f"   - 다음날 주가등락: {best_day['Next_Day_Change']:.2f}%")
    print("=" * 60)

if __name__ == '__main__':
    # merge_advanced_v3.py가 뱉어낸 최종 파일명을 입력합니다.
    analyze_correlation('spillover_hynix_to_hanmi.csv')