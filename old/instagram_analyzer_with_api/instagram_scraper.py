# -*- coding: utf-8 -*-
import os
import requests
from urllib.parse import urlparse
import time
import json
import webbrowser

class InstagramScraper:
    def __init__(self):
        # Instagram Graph API 설정 업데이트
        self.client_id = "2238165979903572"  # 새 앱 ID
        self.client_secret = "7fa1a2d691a0ed2bbb77365eeb7dc90e"  # 새 앱 시크릿
        self.redirect_uri = "http://3.35.105.254:8000/auth"  # 새로운 IP 주소로 업데이트
        
        # 토큰 파일 경로
        self.token_file = "instagram_token.json"
        self.access_token = self.load_or_get_token()
    
    def load_or_get_token(self):
        """토큰을 로드하거나 새로 발급받습니다"""
        if os.path.exists(self.token_file):
            with open(self.token_file, 'r') as f:
                data = json.load(f)
                if data.get('expires_at', 0) > time.time():
                    return data['access_token']
        
        return self.get_new_token()
    
    def get_new_token(self):
        """Facebook OAuth를 통해 새 토큰을 발급받습니다"""
        # Facebook 로그인 URL
        auth_url = f"https://www.facebook.com/v18.0/dialog/oauth?client_id={self.client_id}&redirect_uri={self.redirect_uri}&scope=instagram_basic,instagram_content_publish,pages_show_list,pages_read_engagement,instagram_manage_insights"
        
        print("브라우저에서 Facebook 로그인 페이지가 열립니다...")
        print("로그인 후 받은 코드를 입력해주세요.")
        webbrowser.open(auth_url)
        
        # 한글 인코딩 수정
        code = input("인증 코드를 입력하세요: ").strip()  # 깨진 한글 수정
        
        # 액세스 토큰 교환
        token_url = "https://graph.facebook.com/v18.0/oauth/access_token"
        params = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'redirect_uri': self.redirect_uri,
            'code': code
        }
        
        response = requests.get(token_url, params=params)
        if response.status_code == 200:
            token_data = response.json()
            
            # 토큰 저장
            with open(self.token_file, 'w') as f:
                json.dump({
                    'access_token': token_data['access_token'],
                    'expires_at': time.time() + token_data.get('expires_in', 0)
                }, f)
            
            return token_data['access_token']
        
        raise Exception(f"토큰 발급 실패: {response.text}")

    def get_post_data(self, post_url):
        try:
            path = urlparse(post_url).path
            shortcode = path.split('/')[-2]
            print(f"포스트 ID: {shortcode}")
            
            # 먼저 연결된 Instagram 비즈니스 계정 ID 가져오기
            accounts_url = "https://graph.facebook.com/v18.0/me/accounts"
            response = requests.get(accounts_url, params={'access_token': self.access_token})
            
            if response.status_code != 200:
                raise Exception(f"페이지 정보 가져오기 실패: {response.text}")
            
            page_id = response.json()['data'][0]['id']
            
            # Instagram 비즈니스 계정 ID 가져오기
            instagram_account_url = f"https://graph.facebook.com/v18.0/{page_id}?fields=instagram_business_account"
            response = requests.get(instagram_account_url, params={'access_token': self.access_token})
            
            if response.status_code != 200:
                raise Exception(f"Instagram 계정 정보 가져오기 실패: {response.text}")
            
            instagram_account_id = response.json()['instagram_business_account']['id']
            
            # 미디어 목록 가져오기
            media_url = f"https://graph.facebook.com/v18.0/{instagram_account_id}/media"
            response = requests.get(media_url, params={
                'access_token': self.access_token,
                'fields': 'id,caption,media_type,media_url,permalink,timestamp,like_count,comments_count'
            })
            
            if response.status_code == 200:
                data = response.json()
                media_files = []
                
                for item in data.get('data', []):
                    if shortcode in item.get('permalink', ''):
                        media_url = item.get('media_url')
                        if media_url:
                            temp_dir = "temp_downloads"
                            os.makedirs(temp_dir, exist_ok=True)
                            
                            filename = f"{shortcode}.jpg"
                            image_path = os.path.join(temp_dir, filename)
                            
                            if not os.path.exists(image_path):
                                img_response = requests.get(media_url)
                                if img_response.status_code == 200:
                                    with open(image_path, 'wb') as f:
                                        f.write(img_response.content)
                                    print(f"이미지 저장됨: {image_path}")
                                    media_files.append(image_path)
                            else:
                                media_files.append(image_path)
                                print(f"이미지가 이미 존재함: {image_path}")
                        
                        return {
                            'images': media_files,
                            'caption': item.get('caption', ''),
                            'timestamp': item.get('timestamp'),
                            'likes': item.get('like_count', 0),
                            'comments': item.get('comments_count', 0)
                        }
                
                print("포스트를 찾을 수 없습니다.")
            else:
                print(f"API 요청 실패: {response.text}")
            
            return {
                'images': [],
                'caption': '',
                'timestamp': None,
                'likes': 0,
                'comments': 0
            }
            
        except Exception as e:
            print(f"포스트 데이터 가져오기 실패: {e}")
            print(f"오류 타입: {type(e)}")
            return {
                'images': [],
                'caption': '',
                'timestamp': None,
                'likes': 0,
                'comments': 0
            } 