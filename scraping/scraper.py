import logging
from typing import Dict, Any, Optional, List
from pathlib import Path
import requests
from bs4 import BeautifulSoup
import json
import re

logger = logging.getLogger(__name__)

class InstagramScraper:
    def __init__(self):
        """InstagramScraper 초기화"""
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })
    
    def scrape(self, url: str) -> Dict[str, Any]:
        """인스타그램 포스트 스크래핑"""
        try:
            logger.info("스크래핑 프로세스 시작...")
            
            # Instagram API 엔드포인트 URL 생성
            post_id = self._extract_post_id(url)
            if not post_id:
                raise ValueError("올바른 Instagram URL이 아닙니다")
                
            api_url = f"https://www.instagram.com/p/{post_id}/?__a=1&__d=dis"
            
            # 데이터 가져오기
            response = self.session.get(api_url)
            response.raise_for_status()
            
            # HTML 파싱
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # JSON 데이터 추출 시도
            try:
                json_data = json.loads(response.text)
                logger.info("JSON 데이터 추출 성공")
            except json.JSONDecodeError:
                # JSON 추출 실패 시 HTML에서 데이터 추출
                logger.info("HTML에서 데이터 추출 시도")
                json_data = self._extract_from_html(soup)
            
            # 데이터 파싱
            text_content = self._extract_text(json_data)
            image_urls = self._extract_images(json_data)
            video_url = self._extract_video(json_data)
            timestamp = self._extract_timestamp(json_data)
            
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
            # 대체 방법으로 HTML 직접 파싱 시도
            try:
                response = self.session.get(url)
                soup = BeautifulSoup(response.text, 'html.parser')
                
                text_content = soup.select_one('div._a9zs')
                text_content = text_content.text if text_content else ""
                
                image_urls = [img['src'] for img in soup.select('img._aagt') if 'src' in img.attrs]
                
                return {
                    "text": text_content,
                    "images": image_urls,
                    "video": None,
                    "timestamp": None,
                    "analysis_summary": {
                        "text_length": len(text_content),
                        "image_count": len(image_urls),
                        "has_video": False,
                        "timestamp": None
                    }
                }
            except Exception as e2:
                logger.error(f"대체 스크래핑 방법도 실패: {str(e2)}")
                raise
    
    def _extract_post_id(self, url: str) -> Optional[str]:
        """URL에서 포스트 ID 추출"""
        match = re.search(r'/p/([^/]+)/', url)
        return match.group(1) if match else None
    
    def _extract_from_html(self, soup: BeautifulSoup) -> Dict:
        """HTML에서 데이터 추출"""
        script_tag = soup.find('script', string=re.compile('window._sharedData'))
        if script_tag:
            json_text = re.search(r'window._sharedData = ({.*});', script_tag.string).group(1)
            return json.loads(json_text)
        return {}
    
    def _extract_text(self, data: Dict) -> str:
        """JSON 데이터에서 텍스트 추출"""
        try:
            if 'caption' in data:
                return data['caption']
            return ""
        except:
            return ""
    
    def _extract_images(self, data: Dict) -> List[str]:
        """JSON 데이터에서 이미지 URL 추출"""
        try:
            if 'display_url' in data:
                return [data['display_url']]
            return []
        except:
            return []
    
    def _extract_video(self, data: Dict) -> Optional[str]:
        """JSON 데이터에서 비디오 URL 추출"""
        try:
            if 'video_url' in data:
                return data['video_url']
            return None
        except:
            return None
    
    def _extract_timestamp(self, data: Dict) -> Optional[str]:
        """JSON 데이터에서 타임스탬프 추출"""
        try:
            if 'taken_at_timestamp' in data:
                return data['taken_at_timestamp']
            return None
        except:
            return None
