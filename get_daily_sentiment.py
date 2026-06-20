import os
import pandas as pd
import torch
from transformers import pipeline

def calculate_daily_sentiment_index(csv_path, output_csv_path):
    if not os.path.exists(csv_path):
        print(f"❌ '{csv_path}' 파일이 없습니다. 경로를 확인해주세요.")
        return

    print("📡 한국어 금융/감정 특화 BERT AI 모델 로드 중 (최초 1회 다운로드)...")
    # 🎯 한국어 뉴스 및 금융 텍스트 감정에 강한 오픈소스 BERT 모델 파이프라인 호출
    # 모델은 기본 3단계(부정:0, 중립:1, 긍정:2)로 작동하며, 이를 가중치와 결합해 5단계 효과를 냅니다.
    sentiment_analyzer = pipeline(
        "text-classification", 
        model="DataWizardd/finbert-sentiment-ko",
        device=0 if torch.cuda.is_available() else -1 # GPU가 있으면 GPU 사용, 없으면 CPU
    )
    print("✅ AI 모델 로드 완료!")

    # 1. 데이터 읽기
    df = pd.read_csv(csv_path)
    
    # 날짜 포맷을 'YYYY-MM-DD' 하루 단위로 깔끔하게 통일
    df['date'] = pd.to_datetime(df['date']).dt.date
    
    # 숫자형 변환 및 결측치 방어
    df['agree'] = pd.to_numeric(df['agree'], errors='coerce').fillna(0).astype(int)
    df['disagree'] = pd.to_numeric(df['disagree'], errors='coerce').fillna(0).astype(int)

    print(f"📊 총 {len(df):,}개의 게시글 문맥 분석 및 주주 가중치 계산 시작...")
    
    final_post_scores = []

    # 2. 게시글별 루프 수행
    for idx, row in df.iterrows():
        text = str(row['title']) + " " + str(row['content'])
        # BERT 모델 텍스트 길이 제한(512자) 방어
        text = text[:400] 
        
        try:
            # 🎯 [1단계] 순수 텍스트 문맥 점수 추출
            result = sentiment_analyzer(text)[0]
            label = result['label'] # '부정', '중립', '긍정' 중 하나 출력
            
            # 텍스트 감정 기본 점수화 (부정=1점, 중립=2점, 긍정=3점)
            if label == '부정':
                base_score = 1.0
            elif label == '긍정':
                base_score = 3.0
            else:
                base_score = 2.0
                
            # 🎯 [2단계] 좋아요 / 싫어요 수 기반 주주 공감도 가중치($W$) 계산 (질문자님 아이디어 💡)
            agree = row['agree']
            disagree = row['disagree']
            total = agree + disagree
            
            if total >= 3:  # 최소 3명 이상 반응한 글에만 가중치 유효 적용
                pos_ratio = agree / total
                if pos_ratio >= 0.75:    # 좋아요가 압도적이면 긍정 방향으로 점수 증폭
                    weight = 1.2 if base_score >= 2.0 else 0.8
                elif pos_ratio <= 0.25:  # 싫어요가 압도적이면 부정 방향으로 점수 증폭
                    weight = 1.2 if base_score <= 2.0 else 0.8
                else:
                    weight = 1.0         # 찬반 팽팽하면 기본값
            else:
                weight = 1.0             # 반응이 없거나 적으면 기본값

            # 최종 가중치 점수 산출 및 5단계 스케일(0~4) 제한 안전장치
            final_score = base_score * weight
            final_score = max(0.0, min(4.0, final_score))
            
            final_post_scores.append(final_score)
            
        except Exception as e:
            final_post_scores.append(2.0) # 에러 발생 시 중립 처리
            continue

    df['post_sentiment_score'] = final_post_scores

    print("📈 [3단계] 날짜별(Daily) 그룹화 및 일일 감정 지수 산출 중...")
    # 🎯 같은 날짜로 묶어서 그날 주주들의 평균 심리 점수를 계산 (하루에 딱 하나의 행으로 압축)
    daily_summary = df.groupby('date')['post_sentiment_score'].mean().reset_index()
    daily_summary.columns = ['Date', 'Sentiment_Index']
    
    # 날짜순 오름차순 정렬 (시계열 분석을 위해)
    daily_summary.sort_values(by='Date', ascending=True, inplace=True)

    # 3. 최종 시계열 데이터 저장
    daily_summary.to_csv(output_csv_path, index=False, encoding='utf-8-sig')
    print("=" * 60)
    print(f"🎉 시계열 감정 지수 파일 생성 완료! ➡️ {output_csv_path}")
    print(f"📊 수집된 총 일수(데이터 행 수): {len(daily_summary)}일")
    print("=" * 60)
    print(daily_summary.head(10)) # 상위 10일치 미리보기 출력

if __name__ == '__main__':
    # 💡 하이닉스 CSV 파일을 넣어서 돌리면 하루에 1행짜리 '일일 지수 데이터'가 뚝딱 만들어집니다.
    calculate_daily_sentiment_index('naver_board_005380_현대차.csv', 'daily_sentiment_005380_현대차.csv')