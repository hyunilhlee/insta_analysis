import requests
import json

class ContentAnalyzer:
    def __init__(self):
        self.api_url = "http://localhost:11434/api/generate"
    
    def analyze_content(self, text_from_images, caption, video_frames=None):
        try:
            # 모든 텍스트 컨텐츠 결합
            all_content = f"캡션: {caption}\n이미지 텍스트: {text_from_images}"
            
            # Llama 모델에 분석 요청
            prompt = f"""
다음 인스타그램 콘텐츠를 분석해주세요. 캡션과 이미지에서 추출된 텍스트를 기반으로 분석해주세요:

{all_content}

다음 형식으로 한글로 응답해주세요:
1. 주요 키워드 (최대 5개, 쉼표로 구분)
2. 콘텐츠 요약 (2-3문장)
3. 전반적인 감정 분석 (긍정/중립/부정)
"""
            
            payload = {
                "model": "llama2",
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.7,
                    "top_p": 0.9,
                    "num_predict": 500
                }
            }
            
            response = requests.post(self.api_url, json=payload, timeout=180)
            if response.status_code != 200:
                print(f"분석 API 오류: {response.status_code}")
                print(f"오류 내용: {response.text}")
                return self._get_default_response("API 오류")
            
            result = response.json()
            if 'response' not in result:
                print(f"예상치 못한 응답 형식: {result}")
                return self._get_default_response("응답 형식 오류")
            
            analysis = result['response']
            print(f"원본 분석 결과: {analysis}")  # 디버깅용
            
            try:
                return {
                    'keywords': self._extract_keywords(analysis),
                    'summary': self._extract_summary(analysis),
                    'sentiment': self._extract_sentiment(analysis)
                }
            except Exception as e:
                print(f"분석 결과 파싱 오류: {e}")
                return self._get_default_response("파싱 오류")
            
        except Exception as e:
            print(f"콘텐츠 분석 중 오류 발생: {e}")
            return self._get_default_response(str(e))
    
    def _get_default_response(self, error_msg="알 수 없는 오류"):
        return {
            'keywords': [f'분석 실패: {error_msg}'],
            'summary': f'콘텐츠 분석에 실패했습니다. 사유: {error_msg}',
            'sentiment': '알 수 없음'
        }
    
    def _extract_keywords(self, analysis):
        try:
            # 키워드 부분 찾기
            if '키워드' in analysis:
                keywords_text = analysis.split('키워드')[1].split('\n')[0]
                # 쉼표나 공백으로 구분된 키워드 추출
                keywords = [k.strip() for k in keywords_text.replace(':', '').split(',')]
                return [k for k in keywords if k]  # 빈 문자열 제거
            return ['키워드 추출 실패']
        except Exception as e:
            print(f"키워드 추출 오류: {e}")
            return ['키워드 추출 오류']
    
    def _extract_summary(self, analysis):
        try:
            if '요약' in analysis:
                return analysis.split('요약')[1].split('\n')[0].strip().replace(':', '').strip()
            return '요약 추출 실패'
        except Exception as e:
            print(f"요약 추출 오류: {e}")
            return '요약 추출 오류'
    
    def _extract_sentiment(self, analysis):
        try:
            if '감정' in analysis:
                sentiment = analysis.split('감정')[1].split('\n')[0].strip().replace(':', '').strip()
                return sentiment if sentiment in ['긍정', '중립', '부정'] else '감정 분석 실패'
            return '감정 분석 실패'
        except Exception as e:
            print(f"감정 분석 오류: {e}")
            return '감정 분석 오류' 