import logging
import os
import openai
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)

class ContentAnalyzer:
    def __init__(self, api_key: str = None):
        """ContentAnalyzer 초기화"""
        try:
            if not api_key:
                api_key = os.getenv('OPENAI_API_KEY')
            if not api_key:
                raise ValueError("OpenAI API 키가 필요합니다. api_key 파라미터를 통해 전달하거나 OPENAI_API_KEY 환경 변수를 설정해주세요.")
            
            # OpenAI API 키 설정
            openai.api_key = api_key
            self.model = "gpt-3.5-turbo"
            logger.info("OpenAI API 키가 성공적으로 설정되었습니다.")
        except Exception as e:
            logger.error(f"OpenAI 설정 실패: {str(e)}")
            raise

    def _call_openai(self, prompt: str) -> str:
        """OpenAI API 호출"""
        try:
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "당신은 인스타그램 컨텐츠를 분석하는 전문가입니다."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=500
            )
            return response.choices[0].message['content'].strip()
        except Exception as e:
            logger.error(f"OpenAI API 호출 중 에러 발생: {str(e)}")
            raise

    def analyze_content(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """컨텐츠 분석"""
        try:
            logger.info("컨텐츠 분석 시작...")
            
            # 텍스트 컨텐츠 분석
            text = content.get('text', '')
            logger.info(f"텍스트 분석 시작 (길이: {len(text)}자)")
            
            # 키워드 추출
            keywords = self._extract_keywords(text)
            logger.info(f"키워드 추출 완료: {keywords}")
            
            # 내용 요약
            summary = self._summarize_text(text)
            logger.info("텍스트 요약 완료")
            
            # 감정 분석
            sentiment = self._analyze_sentiment(text)
            logger.info(f"감정 분석 완료: {sentiment}")
            
            # 이미지/비디오 분석
            media_analysis = self._analyze_media(content)
            logger.info("미디어 분석 완료")
            
            # 컨텐츠 일치성 분석
            content_coherence = self._analyze_content_coherence(text, media_analysis)
            logger.info("컨텐츠 일치성 분석 완료")
            
            return {
                "keywords": keywords,
                "summary": summary,
                "sentiment": sentiment,
                "media_analysis": media_analysis,
                "content_coherence": content_coherence,
                "analysis_process": {
                    "text_length": len(text),
                    "image_count": content.get('analysis_summary', {}).get('image_count', 0),
                    "has_video": content.get('analysis_summary', {}).get('has_video', False),
                    "timestamp": content.get('analysis_summary', {}).get('timestamp')
                }
            }
            
        except Exception as e:
            logger.error(f"컨텐츠 분석 중 에러 발생: {str(e)}")
            raise

    def _extract_keywords(self, text: str) -> List[str]:
        """키워드 추출"""
        prompt = f"다음 텍스트에서 가장 중요한 키워드 5개를 추출해주세요. 쉼표(, )로 구분해서 답변해주세요:\n\n{text}"
        response = self._call_openai(prompt)
        return [keyword.strip() for keyword in response.split(',')]
    
    def _summarize_text(self, text: str) -> str:
        """텍스트 요약"""
        prompt = f"다음 텍스트를 2-4문장으로 요약해주세요:\n\n{text}"
        return self._call_openai(prompt)
    
    def _analyze_sentiment(self, text: str) -> str:
        """감정 분석"""
        prompt = f"다음 텍스트의 전반적인 감정을 '긍정', '부정', '중립' 중 하나로 분석해주세요:\n\n{text}"
        return self._call_openai(prompt)
    
    def _analyze_media(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """미디어 분석"""
        return {
            "image_count": content.get('analysis_summary', {}).get('image_count', 0),
            "has_video": content.get('analysis_summary', {}).get('has_video', False),
            "media_types": self._get_media_types(content)
        }
    
    def _get_media_types(self, content: Dict[str, Any]) -> List[str]:
        """미디어 타입 확인"""
        media_types = []
        if content.get('images'):
            media_types.append('image')
        if content.get('video'):
            media_types.append('video')
        return media_types
    
    def _analyze_content_coherence(self, text: str, media_analysis: Dict[str, Any]) -> str:
        """컨텐츠 일치성 분석"""
        prompt = f"""다음 텍스트와 미디어 정보 간의 관련성을 분석해주세요:

텍스트: {text}

미디어 정보:
- 이미지 수: {media_analysis['image_count']}
- 비디오 여부: {'있음' if media_analysis['has_video'] else '없음'}
"""
        return self._call_openai(prompt) 