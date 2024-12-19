import logging
import requests
from bs4 import BeautifulSoup
import json

logger = logging.getLogger(__name__)

class InstagramScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

    def scrape(self, url):
        try:
            logger.info("스크래핑 프로세스 시작...")
            
            # Instagram URL 검증
            if not self._is_valid_instagram_url(url):
                raise ValueError("유효하지 않은 Instagram URL입니다.")

            # 페이지 요청
            response = self.session.get(url)
            if response.status_code != 200:
                raise Exception(f"페이지 로드 실패: {response.status_code}")

            logger.info("HTML에서 데이터 추출 시도")
            soup = BeautifulSoup(response.text, 'lxml')
            
            # 메타 데이터 추출
            meta_data = {}
            for meta in soup.find_all('meta'):
                property = meta.get('property', '')
                content = meta.get('content', '')
                if property.startswith('og:'):
                    meta_data[property[3:]] = content

            # 텍스트 컨텐츠 추출
            text_content = ""
            article = soup.find('article')
            if article:
                text_content = article.get_text(strip=True)
            
            return {
                'url': url,
                'title': meta_data.get('title', ''),
                'description': meta_data.get('description', ''),
                'text': text_content,
                'type': meta_data.get('type', ''),
                'image': meta_data.get('image', '')
            }

        except Exception as e:
            logger.error(f"스크래핑 중 오류 발생: {str(e)}")
            return None

    def _is_valid_instagram_url(self, url):
        """Instagram URL 유효성 검사"""
        return 'instagram.com' in url and ('/p/' in url or '/reel/' in url)
