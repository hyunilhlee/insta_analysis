import os
import logging
import openai
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()

logger = logging.getLogger(__name__)

class ContentAnalyzer:
    def __init__(self):
        try:
            # 환경 변수에서 API 키 가져오기
            api_key = os.getenv('OPENAI_API_KEY')
            
            # Vercel 환경 변수에서 API 키 가져오기 시도
            if not api_key:
                api_key = os.environ.get('OPENAI_API_KEY')
            
            if not api_key:
                logger.error("OpenAI API 키를 찾을 수 없습니다.")
                raise ValueError("OpenAI API 키가 환경 변수에 설정되지 않았습니다. OPENAI_API_KEY를 설정해주세요.")
            
            openai.api_key = api_key
            logger.info("OpenAI API 키 설정 성공")
        except Exception as e:
            logger.error(f"OpenAI 설정 실패: {str(e)}")
            raise

    def analyze_content(self, content):
        try:
            if not content:
                raise ValueError("분석할 컨텐츠가 없습니다.")
                
            logger.info("컨텐츠 분석 시작")
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Instagram 컨텐츠를 분석하여 주요 내용, 감정, 주제를 추출하는 전문가입니다."},
                    {"role": "user", "content": f"다음 Instagram 컨텐츠를 분석해주세요:\n\n{content}"}
                ]
            )
            
            analysis = response.choices[0].message['content']
            logger.info("컨텐츠 분석 완료")
            
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