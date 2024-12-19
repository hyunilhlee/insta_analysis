import logging
from typing import Dict, Any, Optional
from pathlib import Path
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import subprocess
import time
import re
from selenium.common.exceptions import WebDriverException, TimeoutException, NoSuchElementException

logger = logging.getLogger(__name__)

class InstagramScraper:
    def __init__(self):
        """InstagramScraper 초기화"""
        self.setup_driver()
    
    def setup_driver(self):
        """Selenium 웹드라이버 설정"""
        chrome_options = Options()
        chrome_options.add_argument("--headless=new")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--remote-debugging-port=0")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_argument("--lang=ko-KR")
        chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        
        try:
            # Chrome 실행 파일 경로 자동 감지
            chrome_paths = [
                "/usr/bin/chromium-browser",
                "/usr/bin/chromium",
                "/snap/bin/chromium",
                "/usr/bin/google-chrome",
                "/usr/bin/google-chrome-stable"
            ]
            
            chrome_path = None
            for path in chrome_paths:
                if Path(path).exists():
                    chrome_path = path
                    break
            
            if chrome_path:
                chrome_options.binary_location = chrome_path
                logger.info(f"Chrome 실행 파일 경로: {chrome_path}")
            
            service = Service()
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            self.driver.set_page_load_timeout(30)
            logger.info("Chrome 웹드라이버가 성공적으로 초기화되었습니다.")
            
        except WebDriverException as e:
            if "This version of ChromeDriver only supports Chrome version" in str(e):
                logger.error("ChromeDriver 버전 불일치. 수동 설치가 필요할 수 있습니다.")
                logger.error("다음 명령어로 Chrome과 ChromeDriver를 설치해주세요:")
                logger.error("sudo apt update && sudo apt install -y chromium-browser chromium-chromedriver")
            raise
        except Exception as e:
            logger.error(f"웹드라이버 설정 실패: {str(e)}")
            raise
        
        self.wait = WebDriverWait(self.driver, 20)
    
    def wait_for_element(self, by, selector, timeout=20):
        """요소가 나타날 때까지 대기"""
        try:
            return self.wait.until(
                EC.presence_of_element_located((by, selector))
            )
        except TimeoutException:
            logger.error(f"요소를 찾을 수 없음: {selector}")
            raise
    
    def scrape_post(self, url: str) -> Dict[str, Any]:
        """인스타그램 포스트 스크래핑"""
        try:
            logger.info("스크래핑 프로세스 시작...")
            self.driver.get(url)
            time.sleep(10)  # 초기 페이지 로딩 대기
            
            logger.info("페이지 로딩 완료, 컨텐츠 분석 시작...")
            
            # 페이지가 완전히 로드될 때까지 대기
            self.wait.until(
                lambda driver: driver.execute_script("return document.readyState") == "complete"
            )
            
            # 텍스트 컨텐츠 추출 시도
            text_content = ""
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    text_element = self.wait_for_element(By.CSS_SELECTOR, "div._a9zs")
                    text_content = text_element.text
                    if text_content:
                        logger.info(f"텍스트 컨텐츠 추출 성공 (길이: {len(text_content)}자)")
                        break
                    time.sleep(5)
                except (TimeoutException, NoSuchElementException):
                    if attempt == max_retries - 1:
                        logger.warning("텍스트 컨텐츠를 찾을 수 없음")
                        raise
                    time.sleep(5)
            
            # 이미지/비디오 URL 추출
            logger.info("미디어 컨텐츠 분석 시작...")
            
            # 이미지 분석 (여러 선택자 시도)
            image_urls = set()  # 중복 방지를 위해 set 사용
            image_selectors = [
                "img._aagt",  # 기존 선택자
                "img._aa8j",  # 추가 선택자
                "img[class*='x5yr21d']",  # 동적 클래스 패턴
                "article img",  # 일반적인 이미지
            ]
            
            for selector in image_selectors:
                try:
                    media_elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    for elem in media_elements:
                        src = elem.get_attribute("src")
                        if src and not src.endswith(('profile.jpg', 'avatar.jpg')):  # 프로필 이미지 제외
                            image_urls.add(src)
                    if image_urls:
                        logger.info(f"{selector} 선택자로 새로운 이미지 발견")
                except Exception as e:
                    logger.debug(f"{selector} 선택자로 이미지 검색 실패: {str(e)}")
            
            image_urls = list(image_urls)  # set을 list로 변환
            logger.info(f"중복 제거 후 실제 이미지 개수: {len(image_urls)}")
            
            # 디버그를 위한 이미지 URL 출력
            for i, url in enumerate(image_urls, 1):
                logger.debug(f"이미지 {i}: {url}")
            
            # 비디오 분석
            video_url = None
            try:
                video_element = self.driver.find_element(By.TAG_NAME, "video")
                video_url = video_element.get_attribute("src")
                if video_url:
                    logger.info("비디오 컨텐츠 발견")
            except NoSuchElementException:
                logger.info("비디오 컨텐츠 없음")
            
            # 추가 메타데이터 수집
            try:
                timestamp = self.wait_for_element(By.CSS_SELECTOR, "time._aaqe").get_attribute("datetime")
                logger.info(f"게시물 작성 시간: {timestamp}")
            except:
                timestamp = None
                logger.warning("게시물 작성 시간을 찾을 수 없음")
            
            return {
                "text": text_content,
                "images": image_urls,
                "video": video_url,
                "timestamp": timestamp,
                "analysis_summary": {
                    "text_length": len(text_content) if text_content else 0,
                    "image_count": len(image_urls),
                    "has_video": video_url is not None,
                    "timestamp": timestamp
                }
            }
            
        except Exception as e:
            logger.error(f"스크래핑 중 에러 발생: {str(e)}")
            raise
        
    def download_media(self, url: str, save_path: Path) -> Optional[Path]:
        """미디어 파일 다운로드"""
        try:
            response = requests.get(url, stream=True)
            response.raise_for_status()
            
            save_path.parent.mkdir(parents=True, exist_ok=True)
            with open(save_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            return save_path
        except Exception as e:
            logger.error(f"미디어 다운로드 중 에러 발생: {str(e)}")
            return None
    
    def __del__(self):
        """드라이버 정리"""
        if hasattr(self, 'driver'):
            try:
                self.driver.quit()
            except:
                pass
