from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import sys

# 프로젝트 루트 디렉토리를 Python 경로에 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from analysis.analyzer import ContentAnalyzer
from scraping.scraper import InstagramScraper

app = Flask(__name__)
CORS(app)

@app.route('/api/analyze', methods=['POST'])
def analyze():
    try:
        data = request.get_json()
        url = data.get('url')
        
        if not url:
            return jsonify({'error': 'URL이 필요합니다'}), 400
            
        # Instagram 스크래핑
        scraper = InstagramScraper()
        content = scraper.scrape(url)
        
        # 컨텐츠 분석
        analyzer = ContentAnalyzer()
        analysis_result = analyzer.analyze_content(content)
        
        return jsonify(analysis_result)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy'}), 200 