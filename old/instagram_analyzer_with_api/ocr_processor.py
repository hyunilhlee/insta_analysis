import requests
import json
import base64
import time
from PIL import Image
import io
import os

class OCRProcessor:
    def __init__(self):
        self.api_url = "http://localhost:11434/api/generate"
        
    def check_server_connection(self):
        max_attempts = 5
        for attempt in range(max_attempts):
            try:
                response = requests.get("http://localhost:11434/api/version")
                if response.status_code == 200:
                    return True
                else:
                    print(f"서버 응답 코드: {response.status_code}")
                    time.sleep(5)
            except requests.exceptions.ConnectionError:
                if attempt < max_attempts - 1:
                    print(f"서버 연결 대기 중... ({attempt + 1}/{max_attempts})")
                    time.sleep(5)
                else:
                    print("Ollama 서버에 연결할 수 없습니다. 서버가 실행 중인지 확인해주세요.")
        return False
    
    def process_images(self, image_paths):
        if not self.check_server_connection():
            return "서버 연결 실패"
            
        extracted_text = []
        total_images = len(image_paths)
        
        for idx, image_path in enumerate(image_paths, 1):
            print(f"이미지 처리 중... ({idx}/{total_images})")
            
            try:
                # 이미지 파일 존재 확인
                if not os.path.exists(image_path):
                    print(f"이미지 파일이 없습니다: {image_path}")
                    continue
                
                # 이미지 크기 확인
                file_size = os.path.getsize(image_path)
                print(f"이미지 크기: {file_size / 1024 / 1024:.2f} MB")
                
                # 이미지 전처리
                with Image.open(image_path) as img:
                    print(f"이미지 모드: {img.mode}, 크기: {img.size}")
                    
                    # JPEG 형식으로 변환
                    if img.mode != 'RGB':
                        img = img.convert('RGB')
                        print("RGB 모드로 변환됨")
                    
                    # 이미지 크기를 더 작게 제한
                    if img.size[0] > 512 or img.size[1] > 512:
                        img.thumbnail((512, 512))
                        print(f"이미지 크기 조정됨: {img.size}")
                    
                    # 이미지를 바이트로 변환 (품질 낮춤)
                    img_byte_arr = io.BytesIO()
                    img.save(img_byte_arr, format='JPEG', quality=70)
                    img_byte_arr = img_byte_arr.getvalue()
                    print(f"변환된 이미지 크기: {len(img_byte_arr) / 1024 / 1024:.2f} MB")
                    
                    # base64 인코딩
                    image_data = base64.b64encode(img_byte_arr).decode('utf-8')
                    
                    payload = {
                        "model": "llava:7b",
                        "prompt": "Extract and list any text visible in this image.",
                        "stream": False,
                        "images": [image_data],
                        "options": {
                            "num_ctx": 2048,
                            "num_gpu": 0,
                            "temperature": 0.3,
                            "top_p": 0.9
                        }
                    }
                    
                    max_retries = 3
                    for attempt in range(max_retries):
                        try:
                            print(f"API 요청 시작... (시도 {attempt + 1}/{max_retries})")
                            
                            # 세션 사용으로 연결 재사용
                            with requests.Session() as session:
                                response = session.post(
                                    self.api_url,
                                    json=payload,
                                    timeout=180,  # 타임아웃 증가
                                    headers={'Content-Type': 'application/json'}
                                )
                            
                            print(f"응답 상태 코드: {response.status_code}")
                            
                            if response.status_code != 200:
                                print(f"에러 응답: {response.text}")
                                if attempt == max_retries - 1:
                                    break
                                time.sleep(20)  # 대기 시간 증가
                                continue
                            
                            result = response.json()
                            print(f"응답 받음: {result}")
                            
                            if 'response' in result:
                                extracted_text.append(result['response'])
                                print(f"이미지 {idx} 처리 완료")
                                break
                            else:
                                print(f"예상치 못한 응답 형식: {result}")
                                
                        except requests.exceptions.RequestException as e:
                            print(f"API 요청 실패: {str(e)}")
                            if attempt < max_retries - 1:
                                time.sleep(20)
                                print("서버 재연결 시도...")
                            
            except Exception as e:
                print(f"이미지 처리 중 오류 발생: {str(e)}")
                print(f"오류 타입: {type(e)}")
                continue
            
            # 이미지 처리 사이에 잠시 대기
            time.sleep(5)
        
        if not extracted_text:
            return "텍스트 추출 실패"
            
        return ' '.join(extracted_text)