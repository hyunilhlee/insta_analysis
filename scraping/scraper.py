import logging
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

class InstagramScraper:
    def __init__(self):
        self.driver = None
        self.setup_driver()

    def setup_driver(self):
        try:
            chrome_options = Options()
            chrome_options.add_argument('--headless')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--window-size=1920x1080')
            chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')

            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            logger.info("Chrome 드라이버 초기화 성공")
        except Exception as e:
            logger.error(f"드라이버 설정 실패: {str(e)}")
            raise

    def scrape(self, url):
        try:
            logger.info("스크래핑 프로세스 시작...")
            
            if not self._is_valid_instagram_url(url):
                raise ValueError("유효하지 않은 Instagram URL입니다.")

            # URL 정규화
            if '?' in url:
                url = url.split('?')[0]

            # 페이지 로드
            self.driver.get(url)
            time.sleep(3)  # 페이지 로드 대기

            # 컨텐츠 로드 대기
            try:
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.TAG_NAME, "article"))
                )
            except TimeoutException:
                logger.warning("페이지 로드 타임아웃")

            # HTML 파싱
            soup = BeautifulSoup(self.driver.page_source, 'lxml')
            
            # 텍스트 컨텐츠 추출
            text_content = []
            
            # 1. article 내용 추출
            article = soup.find('article')
            if article:
                # 게시물 텍스트
                text_elements = article.find_all(['span', 'h1', 'p'])
                for elem in text_elements:
                    text = elem.get_text(strip=True)
                    if len(text) > 10:  # 의미 있는 텍스트만 추출
                        text_content.append(text)

            # 2. 이미지 alt 텍스트 추출
            images = soup.find_all('img')
            for img in images:
                alt_text = img.get('alt', '')
                if alt_text and len(alt_text) > 10:
                    text_content.append(alt_text)

            # 결과 생성
            result = {
                'url': url,
                'text': ' '.join(text_content),
                'image_count': len(images),
                'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
            }

            # 컨텐츠 유효성 검사
            if not result['text']:
                logger.error("텍스트 컨텐츠를 찾을 수 없습니다")
                return None

            logger.info(f"컨텐츠 추출 성공: {len(result['text'])} 글자")
            return result

        except Exception as e:
            logger.error(f"스크래핑 중 오류 발생: {str(e)}")
            return None
        finally:
            if self.driver:
                self.driver.quit()

    def _is_valid_instagram_url(self, url):
        """Instagram URL 유효성 검사"""
        return 'instagram.com' in url and ('/p/' in url or '/reel/' in url)
