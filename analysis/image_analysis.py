import logging
from typing import List, Optional
from pathlib import Path
import torch
import clip
from PIL import Image
import cv2
import numpy as np

logger = logging.getLogger(__name__)

class ImageAnalyzer:
    def __init__(self):
        """ImageAnalyzer 초기화"""
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model, self.preprocess = clip.load("ViT-B/32", device=self.device)
    
    def analyze_image(self, image_path: Path) -> str:
        """이미지 분석 및 설명 생성

        Args:
            image_path: 이미지 파일 경로

        Returns:
            이미지 설명 텍스트
        """
        try:
            image = Image.open(image_path)
            image_input = self.preprocess(image).unsqueeze(0).to(self.device)
            
            # 미리 정의된 카테고리로 이미지 분류
            categories = [
                "사람", "풍경", "음식", "동물", "제품", "예술작품",
                "실내", "실외", "스포츠", "패션", "여행", "일상"
            ]
            
            text_inputs = torch.cat([
                clip.tokenize(f"이 이미지는 {category}를 보여줍니다") for category in categories
            ]).to(self.device)
            
            with torch.no_grad():
                image_features = self.model.encode_image(image_input)
                text_features = self.model.encode_text(text_inputs)
                
                similarity = (100.0 * image_features @ text_features.T).softmax(dim=-1)
                values, indices = similarity[0].topk(3)
            
            top_categories = [categories[idx] for idx in indices]
            description = f"이 이미지는 {', '.join(top_categories)}와 관련된 내용을 보여줍니다."
            
            return description
            
        except Exception as e:
            logger.error(f"이미지 분석 중 에러 발생: {str(e)}")
            return "이미지 분석에 실패했습니다."
    
    def analyze_video(self, video_path: Path, sample_interval: int = 30) -> List[str]:
        """비디오 분석 및 설명 생성

        Args:
            video_path: 비디오 파일 경로
            sample_interval: 프레임 샘플링 간격 (초)

        Returns:
            프레임별 설명 리스트
        """
        try:
            cap = cv2.VideoCapture(str(video_path))
            fps = cap.get(cv2.CAP_PROP_FPS)
            frame_interval = int(fps * sample_interval)
            
            descriptions = []
            frame_count = 0
            
            while cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    break
                
                if frame_count % frame_interval == 0:
                    # OpenCV BGR을 RGB로 변환
                    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    image = Image.fromarray(frame_rgb)
                    
                    # 임시 파일로 저장
                    temp_path = Path("temp_frame.jpg")
                    image.save(temp_path)
                    
                    # 프레임 분석
                    description = self.analyze_image(temp_path)
                    descriptions.append(description)
                    
                    # 임시 파일 삭제
                    temp_path.unlink()
                
                frame_count += 1
            
            cap.release()
            return descriptions
            
        except Exception as e:
            logger.error(f"비디오 분석 중 에러 발생: {str(e)}")
            return ["비디오 분석에 실패했습니다."]
    
    def get_content_description(self, media_path: Path) -> Optional[str]:
        """미디어 파일 분석 및 설명 생성

        Args:
            media_path: 미디어 파일 경로

        Returns:
            미디어 설명 텍스트
        """
        try:
            if media_path.suffix.lower() in ['.jpg', '.jpeg', '.png', '.gif']:
                return self.analyze_image(media_path)
            elif media_path.suffix.lower() in ['.mp4', '.mov', '.avi']:
                descriptions = self.analyze_video(media_path)
                return " ".join(descriptions)
            else:
                logger.warning(f"지원하지 않는 파일 형식: {media_path.suffix}")
                return None
                
        except Exception as e:
            logger.error(f"미디어 분석 중 에러 발생: {str(e)}")
            return None
