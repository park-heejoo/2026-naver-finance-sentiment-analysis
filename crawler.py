import io
import time
import random
from datetime import datetime
import requests
import pandas as pd
from db_manager import DB_manager

API_URL = 'https://m.stock.naver.com/front-api/discussion/list'


class Crawler:
    def __init__(self, n_process, start_nid=None, end_nid=None):
        self.n_process = n_process
        self.start_nid = int(start_nid) if start_nid else None
        self.end_nid = int(end_nid) if end_nid else None
        self.db = DB_manager()

    def fetch_by_code(self, code):
        headers = {
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Mobile/15E148 Safari/604.1',
            'Referer': f'https://m.stock.naver.com/domestic/stock/{code}/discussion',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7'
        }

        print(f"\n🚀 [안전한 배치 필터 모드] {code} 종목 데이터 수집을 가동합니다.")
        print(f"🎯 목표 NID 범위: {self.start_nid} ~ {self.end_nid}")
        print("=" * 60)
        
        # 주주방 점프 오프셋 설정
        current_offset = f"-{self.end_nid}" if self.end_nid else ""
        batch_count = 1
        
        while True:
            current_hour = datetime.now().hour
            if 9 <= current_hour <= 18:
                delay = random.uniform(3.5, 6.0)
            else:
                delay = random.uniform(1.2, 2.5)
                
            print(f"📡 [Batch {batch_count}] 데이터 요청 중... (오프셋: {current_offset} | 대기: {delay:.2f}초)")
            time.sleep(delay)
            
            params = {
                'discussionType': 'domesticStock',
                'itemCode': code,
                'pageSize': 50, 
                'isHolderOnly': 'false',
                'excludesItemNews': 'false',
                'isItemNewsOnly': 'false',
                'offset': current_offset
            }
            
            try:
                req = requests.get(API_URL, headers=headers, params=params, timeout=10)
                if req.status_code != 200:
                    print(f"⚠️ 서버 통신 지연 (상태코드: {req.status_code}). 3초 후 다시 시도합니다.")
                    time.sleep(3)
                    continue
                    
                res_json = req.json()
                result_data = res_json.get('result', {})
                posts = result_data.get('posts', [])
                
                if not posts:
                    print("🏁 해당 구역에 더 이상 가져올 글이 없습니다.")
                    break
                
                valid_posts = [] 
                reached_start_nid = False
                
                for post in posts:
                    nid = int(post.get('id'))
                    
                    # 🔍 [수정] 오프셋 계산 유연성 확보
                    # 네이버가 오프셋 기점으로 준 리스트는 상한선 검사를 너무 칼같이 하면 첫 글이 날아갑니다.
                    # 내가 설정한 하한선(start_nid)보다 훨씬 뒤의 과거 글로 내려갔을 때만 멈추도록 교정합니다.
                    if self.start_nid and nid < (self.start_nid - 5):
                        reached_start_nid = True
                        break
                    
                    print(f"   🎯 [적중!] {code}의 진짜 게시글을 확보했습니다. (NID: {nid})")
                        
                    date = post.get('writtenAt', '')
                    if 'T' in date:
                        date = date.replace('T', ' ')[:16]
                        
                    title = post.get('title', '')
                    agree = str(post.get('recommendCount', '0'))
                    disagree = str(post.get('notRecommendCount', '0'))
                    
                    posts_dict = {
                        'title': title,
                        'nid': nid,
                        'date': date,
                        'view': '0',        
                        'agree': agree,
                        'disagree': disagree,
                        'opinion': '0',
                        'content': '' 
                    }
                    valid_posts.append(posts_dict)
                
                # 💾 뭉텅이 데이터를 DB에 즉시 기록 (여기서 무조건 파일이 생성됩니다)
                if valid_posts:
                    df_batch = pd.DataFrame(valid_posts)
                    df_batch.date = pd.to_datetime(df_batch.date)
                    df_batch.set_index('nid', inplace=True)
                    
                    self.db.write(code, df_batch)
                    print(f"💾 [실시간 저장 완료] Batch {batch_count} 에서 {len(valid_posts)}개의 글을 DB에 누적했습니다!")
                
                if reached_start_nid:
                    print(f"🏁 설정한 범위 경계면에 도달하여 안전하게 수집을 종료합니다.")
                    break
                    
                last_offset = result_data.get('lastOffset')
                if not last_offset or str(last_offset) == str(current_offset):
                    break
                    
                current_offset = last_offset
                batch_count += 1
                
            except Exception as e:
                print(f"❌ 에러 발생: {e}. 잠시 대기 후 자동으로 이어서 시도합니다.")
                time.sleep(3)
                
        print('\n' + code + ': 수집 완료.', end=' ')
        return None

    def is_up_to_date(self, code):
        return False

    def fetch_one(self, code):
        t = time.time()
        self.fetch_by_code(code)
        print('({:.2f}sec)'.format(time.time() - t))