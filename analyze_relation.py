import os
import re
import pandas as pd
from collections import Counter

# 🎯 1. 네이버 토론방에서 흔히 언급되는 주요 비교 후보 종목들 정의 (키워드 맵)
# 과제 스케일에 맞게 주주들이 자주 쓰는 줄임말이나 영문명도 매칭되도록 구성했습니다.
STOCK_KEYWORDS = {
    '한미반도체': [
        '한미반도체', '한미', 'hanmi', '한미반', 'gksalvqsehcl',
        'tc본더', '본더' # 하이닉스 HBM 패키징의 핵심 장비인 TC 본더 관련 키워드
    ],
    '리노공업': [
        '리노공업', '리노', 'leeno', 'flshrhddjq',
        '리노핀', '테스트소켓', '소켓' # 반도체 테스트 핵심 부품
    ],
    '이오테크닉스': [
        '이오테크닉스', '이오', 'eotechnics', 'dldhxorzlsmdtm',
        '레이저그루빙', '스텔스다이싱' # HBM 커팅 및 레이저 장비 
    ],
    'HPSP': [
        'hpsp', '에이치피에스피', '고압수소', '수소어닐링', 'gxtv' # 전공정 고압 수소 어닐링 독점 장비사
    ],
    '하나마이크론': [
        '하나마이크론', '하나마이', '하나마', 'hanamicron', 'gksakdlzshshs',
        'osat', '후공정' # 하이닉스의 핵심 후공정(OSAT) 외주 파트너사
    ],
    '주성엔지니어링': [
        '주성엔지니어링', '주성', 'jusung', 'wntjdgldwslgfld',
        'ald', '증착' # 하이닉스 전공정 원자층증착(ALD) 장비 주요 공급사
    ],
    '동진쎄미켐': [
        '동진쎄미켐', '동진', 'dongjin', 'ehdwlsxlalzkq',
        '감광액', 'pr', '포토레지스트' # 전공정 핵심 소재(감광액) 공급사
    ],
    '솔브레인': [
        '솔브레인', 'soulbrain', 'thfqvofpdlsh',
        '식각액', '에천트' # 반도체 공정용 화학 소재(식각액) 공급사
    ]
}

def analyze_related_stocks(csv_path, target_code, target_name):
    if not os.path.exists(csv_path):
        print(f"❌ '{csv_path}' 파일을 찾을 수 없습니다. 크롤링을 먼저 완료해주세요.")
        return
    
    print(f"\n🔍 [{target_name} ({target_code})] 연관 종목 분석 시작...")
    
    # CSV 읽기
    df = pd.read_csv(csv_path)
    
    # 제목과 본문을 하나의 텍스트로 합치고 결측치 제거
    text_data = (df['title'].fillna('') + ' ' + df['content'].fillna('')).tolist()
    
    mentioned_stocks = []
    
    # 텍스트 전체를 돌며 다른 종목이 언급되었는지 카운트
    for text in text_data:
        for stock_name, keywords in STOCK_KEYWORDS.items():
            # 자기 자신 종목은 연관 종목에서 제외
            if stock_name == target_name or (target_name == 'SK하이닉스' and stock_name == 'SK하이닉스'):
                continue
                
            # 키워드 중 하나라도 텍스트에 포함되어 있는지 검사 (정규식 활용으로 정확도 업)
            for kw in keywords:
                if re.search(re.escape(kw), text, re.IGNORECASE):
                    mentioned_stocks.append(stock_name)
                    break # 한 글에 같은 종목이 여러번 언급되어도 1회만 카운트
                    
    # 빈도수 계산
    counts = Counter(mentioned_stocks)
    common_top2 = counts.most_common(2)
    
    print("-" * 50)
    print(f"🎯 {target_name} 방에서 가장 많이 언급된 연관 종목 TOP 2:")
    if not common_top2:
        print("   이 구간 내에서는 언급된 연관 종목이 없습니다. 수집 범위를 넓혀보세요!")
    else:
        for i, (stock, count) in enumerate(common_top2, 1):
            print(f"   {i}위: {stock} (총 {count}회 동시 언급)")
    print("=" * 50)

if __name__ == '__main__':
    # 💡 본인이 긁은 CSV 파일명과 종목명에 맞게 매칭해서 돌려보세요!
    # 예시: SK하이닉스 파일 분석
    analyze_related_stocks('naver_board_000660.csv', '000660', 'SK하이닉스')
    
    # 현대차, 네이버 파일도 있다면 아래 주석을 풀고 경로를 맞춰서 돌리시면 됩니다.
    # analyze_related_stocks('naver_board_005380.csv', '005380', '현대차')
    # analyze_related_stocks('naver_board_035420.csv', '035420', '네이버')