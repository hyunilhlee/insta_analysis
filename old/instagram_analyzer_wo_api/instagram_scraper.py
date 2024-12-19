from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import time
import os
import requests
import logging

class InstagramScraper:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.chrome_options = webdriver.ChromeOptions()
        self.chrome_options.add_argument('--headless')
        self.chrome_options.add_argument('--no-sandbox')
        self.chrome_options.add_argument('--disable-dev-shm-usage')
        self.chrome_options.add_argument('--window-size=1920,1080')
        self.chrome_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')

    def get_post_data(self, post_url):
        driver = None
        try:
            # WebDriver 초기화
            self.logger.info("Chrome WebDriver 초기화 중...")
            driver = webdriver.Chrome(options=self.chrome_options)
            
            # URL 정리 (쿼리 파라미터 제거)
            clean_url = post_url.split('?')[0]
            self.logger.info(f"접속 URL: {clean_url}")
            
            # 페이지 로드
            driver.get(clean_url)
            time.sleep(5)
            
            # 이미지 URL 수집 (중복 제거를 위해 set 사용)
            image_urls = set()
            
            # 메인 이미지 찾기
            try:
                main_images = driver.find_elements(By.CSS_SELECTOR, 'img[class*="_aagt"]')
                for img in main_images:
                    src = img.get_attribute('src')
                    if src and 'scontent' in src and not any(x in src.lower() for x in ['profile', 'avatar']):
                        image_urls.add(src)
                        self.logger.info(f"메인 이미지 URL 발견: {src}")
            except Exception as e:
                self.logger.error(f"메인 이미지 검색 실패: {e}")
            
            # 다중 이미지 처리
            try:
                while True:
                    # 다음 버튼 찾기
                    try:
                        next_button = driver.find_element(By.CSS_SELECTOR, 'button._aahi')
                        if not next_button.is_displayed():
                            break
                            
                        # 다음 버튼 클릭
                        driver.execute_script("arguments[0].click();", next_button)
                        time.sleep(2)
                        
                        # 새 이미지 찾기
                        new_image = driver.find_element(By.CSS_SELECTOR, 'img._aagt')
                        src = new_image.get_attribute('src')
                        if src and 'scontent' in src:
                            image_urls.add(src)
                            self.logger.info(f"추가 이미지 URL 발견: {src}")
                    except:
                        break  # 다음 버튼을 찾지 못하면 종료
            except Exception as e:
                self.logger.info(f"다중 이미지 처리 완료: {e}")
            
            # 캡션 추출
            caption = ""
            try:
                caption_element = driver.find_element(By.CSS_SELECTOR, 'div._a9zs')
                caption = caption_element.text
                self.logger.info(f"캡션 추출 성공: {len(caption)} 글자")
            except Exception as e:
                self.logger.error(f"캡션 추출 실패: {e}")
            
            # 이미지 다운로드
            downloaded_files = []
            self.logger.info(f"\n총 {len(image_urls)}개의 고유한 이미지 URL 발견")
            
            for url in image_urls:
                file_path = self._download_media(url)
                if file_path:
                    downloaded_files.append(file_path)
            
            self.logger.info(f"총 {len(downloaded_files)}개의 이미지 파일 다운로드 완료")
            
            if not downloaded_files:
                self.logger.error("다운로드된 이미지가 없습니다!")
                return {'images': [], 'caption': caption, 'url': clean_url}
            
            return {
                'images': downloaded_files,
                'caption': caption,
                'url': clean_url
            }
            
        except Exception as e:
            self.logger.error(f"데이터 수집 실패: {e}")
            return {'images': [], 'caption': '', 'url': post_url}
            
        finally:
            if driver:
                driver.quit()

    def _download_media(self, url):
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Referer': 'https://www.instagram.com/'
            }
            
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                # 저장 디렉토리 생성
                os.makedirs('temp_downloads', exist_ok=True)
                
                # 파일 저장
                file_path = f"temp_downloads/media_{hash(url)}.jpg"
                with open(file_path, 'wb') as f:
                    f.write(response.content)
                
                self.logger.info(f"미디어 다운로드 성공: {file_path}")
                return file_path
                
        except Exception as e:
            self.logger.error(f"미디어 다운로드 실패: {e}")
        return None