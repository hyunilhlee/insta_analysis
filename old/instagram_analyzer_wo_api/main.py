import os
from instagram_scraper import InstagramScraper
from ocr_processor import OCRProcessor
from content_analyzer import ContentAnalyzer

def main():
    # 인스타그램 링크 입력 받기
    post_url = input("인스타그램 포스트 URL을 입력하세요: ")
    
    # 인스타그램 스크래퍼 초기화
    scraper = InstagramScraper()
    
    # 포스트 데이터 수집
    post_data = scraper.get_post_data(post_url)
    
    if not post_data['images']:
        print("이미지를 가져오는데 실패했습니다.")
        return
    
    # OCR 처리
    ocr_processor = OCRProcessor()
    text_from_images = ocr_processor.process_images(post_data['images'])
    
    # 콘텐츠 분석
    analyzer = ContentAnalyzer()
    analysis_result = analyzer.analyze_content(
        text_from_images=text_from_images,
        caption=post_data['caption']
    )
    
    # 결과 출력
    print("\n=== 분석 결과 ===")
    print(f"주요 키워드: {', '.join(analysis_result['keywords'])}")
    print(f"\n콘텐츠 요약: {analysis_result['summary']}")
    print(f"\n감정 분석: {analysis_result['sentiment']}")

if __name__ == "__main__":
    main() 