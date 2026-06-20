from crawler import Crawler

def main():
    # 대상 종목
    code = "005930"
    
    start_nid = "420399053" 
    end_nid = "420399153"   
    
    print("\n==================================================")
    print("🚀 [테스트 가동] 2021년 데이터 일부만 안전하게 크롤링해 봅니다.")
    print(f"📌 설정된 좁은 NID 범위: {start_nid} ~ {end_nid}")
    print("==================================================")
    
    # 크롤러 가동
    crawler = Crawler(n_process=1, start_nid=start_nid, end_nid=end_nid)
    crawler.fetch_one(code)
    
    print("\n==================================================")
    print("🎉 테스트가 종료되었습니다! DB 폴더를 확인해 보세요.")
    print("==================================================")

if __name__ == "__main__":
    main()