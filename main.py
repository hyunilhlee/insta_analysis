import logging
import os
from scraping.scraper import InstagramScraper
from analysis.analyzer import ContentAnalyzer
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    try:
        # OpenAI API 키를 환경 변수에서 가져오기
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("OPENAI_API_KEY 환경 변수가 설정되지 않았습니다.")
        
        # 인스타그램 스크래퍼 초기화
        scraper = InstagramScraper()
        
        # 컨텐츠 분석기 초기화
        analyzer = ContentAnalyzer(api_key=api_key)
        
        # 사용자로부터 URL 입력 받기
        url = input("인스타그램 포스트 URL을 입력하세요: ")
        
        # 포스트 스크래핑
        content = scraper.scrape_post(url)
        
        # 컨텐츠 분석
        analysis_result = analyzer.analyze_content(content)
        
        # 분석 결과 출력
        print("\n=== 분석 결과 ===\n")
        print("주요 키워드:")
        print(", ".join(f"[{keyword}]" for keyword in analysis_result["keywords"]))
        print("\n내용 요약:")
        print(analysis_result["summary"])
        print("\n감정 분석:")
        print(f"- {analysis_result['sentiment']}")
        print("\n컨텐츠 일치성:")
        print(f"- {analysis_result['content_coherence']}")
        
    except Exception as e:
        logger.error(f"프로그램 실행 중 에러 발생: {str(e)}")
        raise

if __name__ == "__main__":
    main()
