import os
import sys
import json
import logging
import traceback

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 프로젝트 루트 디렉토리를 Python 경로에 추가
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(root_dir)

from analysis.analyzer import ContentAnalyzer
from scraping.scraper import InstagramScraper

def read_file(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        logger.error(f"파일 읽기 오류 ({file_path}): {str(e)}")
        return None

def handler(event, context):
    try:
        logger.info(f"요청 받음: {event}")
        
        method = event.get('httpMethod', 'GET')
        path = event.get('path', '/')
        
        # API 엔드포인트 처리
        if method == 'POST' and path.startswith('/api/analyze'):
            try:
                body = json.loads(event.get('body', '{}'))
                url = body.get('url')
                
                if not url:
                    return {
                        'statusCode': 400,
                        'headers': {'Content-Type': 'application/json'},
                        'body': json.dumps({'error': 'URL이 필요합니다'})
                    }
                
                # Instagram 스크래핑
                scraper = InstagramScraper()
                content = scraper.scrape(url)
                
                if not content:
                    return {
                        'statusCode': 400,
                        'headers': {'Content-Type': 'application/json'},
                        'body': json.dumps({'error': '컨텐츠를 가져오지 못했습니다'})
                    }
                
                # 컨텐츠 분석
                analyzer = ContentAnalyzer()
                analysis_result = analyzer.analyze_content(content)
                
                return {
                    'statusCode': 200,
                    'headers': {
                        'Content-Type': 'application/json',
                        'Access-Control-Allow-Origin': '*'
                    },
                    'body': json.dumps(analysis_result)
                }
                
            except Exception as e:
                logger.error(f"분석 중 오류: {str(e)}")
                return {
                    'statusCode': 500,
                    'headers': {'Content-Type': 'application/json'},
                    'body': json.dumps({'error': str(e)})
                }
        
        # 정적 파일 처리
        if path.startswith('/static/'):
            file_path = os.path.join(root_dir, path[1:])
            content = read_file(file_path)
            if content:
                content_type = 'text/css' if path.endswith('.css') else 'application/javascript'
                return {
                    'statusCode': 200,
                    'headers': {'Content-Type': content_type},
                    'body': content
                }
        
        # 메인 페이지 처리
        if method == 'GET' and (path == '/' or path == '/index.html'):
            content = read_file(os.path.join(root_dir, 'templates', 'index.html'))
            if content:
                return {
                    'statusCode': 200,
                    'headers': {'Content-Type': 'text/html'},
                    'body': content
                }
        
        # 404 처리
        return {
            'statusCode': 404,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'error': 'Not Found'})
        }
        
    except Exception as e:
        logger.error(f"처리 중 오류 발생: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'error': str(e)})
        }