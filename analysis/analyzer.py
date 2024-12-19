import os
import logging
from openai import OpenAI

logger = logging.getLogger(__name__)

class ContentAnalyzer:
    def __init__(self):
        try:
            api_key = os.getenv('OPENAI_API_KEY')
            if not api_key:
                raise ValueError("OpenAI API 키가 환경 변수에 설정되지 않았습니다.")
            
            self.client = OpenAI(api_key=api_key)
            logger.info("OpenAI 클라이언트 초기화 성공")
        except Exception as e:
            logger.error(f"OpenAI 설정 실패: {str(e)}")
            raise

    def analyze_content(self, content):
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Instagram 컨텐츠를 분석하여 주요 내용, 감정, 주제를 추출하는 전문가입니다."},
                    {"role": "user", "content": f"다음 Instagram 컨텐츠를 분석해주세요:\n\n{content}"}
                ]
            )
            
            analysis = response.choices[0].message.content
            return {
                "success": True,
                "analysis": analysis,
                "original_content": content
            }
        except Exception as e:
            logger.error(f"컨텐츠 분석 중 오류: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "original_content": content
            } 