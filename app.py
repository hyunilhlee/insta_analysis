from flask import Flask, request, jsonify, render_template
from scraping.scraper import InstagramScraper
from analysis.analyzer import ContentAnalyzer
import logging
import os
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# OpenAI API 키 가져오기
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY 환경 변수가 설정되지 않았습니다.")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/analyze', methods=['POST'])
def analyze():
    try:
        data = request.get_json()
        url = data.get('url')
        
        if not url:
            return jsonify({'error': 'URL이 제공되지 않았습니다.'}), 400
        
        # 스크래퍼 및 분석기 초기화
        scraper = InstagramScraper()
        analyzer = ContentAnalyzer(api_key=OPENAI_API_KEY)
        
        # 컨텐츠 스크래핑
        content = scraper.scrape_post(url)
        
        # 컨텐츠 분석
        analysis_result = analyzer.analyze_content(content)
        
        return jsonify(analysis_result)
        
    except Exception as e:
        logger.error(f"분석 중 오류 발생: {str(e)}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True) 