import logging
from typing import Dict, Any, List
from models.llama_model import LlamaAnalyzer

logger = logging.getLogger(__name__)

class TextAnalyzer:
    def __init__(self):
        """TextAnalyzer 초기화"""
        self.llama = LlamaAnalyzer()
    
    def analyze_text(self, text: str) -> Dict[str, Any]:
        """텍스트 분석 수행

        Args:
            text: 분석할 텍스트

        Returns:
            Dict containing:
            - keywords: 주요 키워드 리스트
            - summary: 텍스트 요약
            - sentiment: 감정 분석 결과
        """
        try:
            # 키워드 추출
            keywords = self.llama.extract_keywords(text)
            
            # 텍스트 요약
            summary = self.llama.summarize_text(text)
            
            # 감정 분석
            sentiment = self.llama.analyze_sentiment(text)
            
            return {
                "keywords": keywords,
                "summary": summary,
                "sentiment": sentiment
            }
            
        except Exception as e:
            logger.error(f"텍스트 분석 중 에러 발생: {str(e)}")
            return {
                "keywords": [],
                "summary": "텍스트 분석에 실패했습니다.",
                "sentiment": "알 수 없음"
            }
    
    def analyze_content_relevance(self, text: str, image_description: str) -> str:
        """텍스트와 이미지 설명 간의 관련성 분석

        Args:
            text: 텍스트 내용
            image_description: 이미지 설명

        Returns:
            관련성 분석 결과
        """
        try:
            return self.llama.analyze_content_relevance(text, image_description)
        except Exception as e:
            logger.error(f"컨텐츠 관련성 분석 중 에러 발생: {str(e)}")
            return "컨텐츠 관련성 분석에 실패했습니다."
    
    def preprocess_text(self, text: str) -> str:
        """텍스트 전처리

        Args:
            text: 원본 텍스트

        Returns:
            전처리된 텍스트
        """
        # 해시태그 처리
        hashtags = [word for word in text.split() if word.startswith("#")]
        clean_text = " ".join([word for word in text.split() if not word.startswith("#")])
        
        # 해시태그를 문장 끝에 추가
        if hashtags:
            clean_text += "\n\n해시태그: " + " ".join(hashtags)
        
        return clean_text
