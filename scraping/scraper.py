import logging
import requests
from bs4 import BeautifulSoup
import json
import time

logger = logging.getLogger(__name__)

class InstagramScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Cache-Control': 'max-age=0'
        }

    def scrape(self, url):
        try:
            logger.info("스크래핑 프로세스 시작...")
            
            # Instagram URL 검증
            if not self._is_valid_instagram_url(url):
                raise ValueError("유효하지 않은 Instagram URL입니다.")

            # URL 정규화
            if '?' in url:
                url = url.split('?')[0]

            # 페이지 요청 (여러 번 시도)
            content = None
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    response = self.session.get(url, timeout=10)
                    if response.status_code == 200:
                        content = response.text
                        break
                    elif response.status_code == 429:
                        logger.warning(f"Rate limit 감지됨 (시도 {attempt + 1}/{max_retries})")
                        time.sleep(2 ** attempt)  # 지수 백오프
                    else:
                        logger.warning(f"HTTP {response.status_code} 수신됨 (시도 {attempt + 1}/{max_retries})")
                except requests.RequestException as e:
                    logger.warning(f"요청 실패 (시도 {attempt + 1}/{max_retries}): {str(e)}")
                    if attempt < max_retries - 1:
                        time.sleep(2 ** attempt)

            if not content:
                raise Exception("페이지 로드 실패")

            logger.info("HTML에서 데이터 추출 시도")
            soup = BeautifulSoup(content, 'lxml')
            
            # 메타 데이터 추출
            meta_data = {}
            for meta in soup.find_all('meta'):
                property = meta.get('property', '')
                content = meta.get('content', '')
                if property.startswith('og:'):
                    meta_data[property[3:]] = content

            # 텍스트 컨텐츠 추출 (여러 방법 시도)
            text_content = []
            
            # 1. article 태그에서 추출
            article = soup.find('article')
            if article:
                text_content.append(article.get_text(strip=True))
            
            # 2. 특정 클래스를 가진 div에서 추출
            content_divs = soup.find_all('div', class_=['_a9zs', 'C4VMK'])
            for div in content_divs:
                text_content.append(div.get_text(strip=True))
            
            # 3. span 태그에서 추출
            spans = soup.find_all('span')
            for span in spans:
                if len(span.get_text(strip=True)) > 50:  # 의미 있는 텍스트만 추출
                    text_content.append(span.get_text(strip=True))

            # 결과 조합
            result = {
                'url': url,
                'title': meta_data.get('title', ''),
                'description': meta_data.get('description', ''),
                'text': ' '.join(text_content),
                'type': meta_data.get('type', ''),
                'image': meta_data.get('image', '')
            }

            # 컨텐츠 유효성 검사
            if not any([result['text'], result['description']]):
                logger.error("텍스트 컨텐츠를 찾을 수 없습니다")
                return None

            return result

        except Exception as e:
            logger.error(f"스크래핑 중 오류 발생: {str(e)}")
            return None

    def _is_valid_instagram_url(self, url):
        """Instagram URL 유효성 검사"""
        return 'instagram.com' in url and ('/p/' in url or '/reel/' in url)
