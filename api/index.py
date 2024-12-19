import os
import sys
import json
import logging
import traceback

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 프로젝트 루트 디렉토리를 Python 경로에 추가
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(current_dir)
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

try:
    from analysis.analyzer import ContentAnalyzer
    from scraping.scraper import InstagramScraper
except ImportError as e:
    logger.error(f"Import 오류: {str(e)}")
    logger.error(f"현재 Python 경로: {sys.path}")
    raise

def read_template():
    try:
        template_path = os.path.join(root_dir, 'templates', 'index.html')
        with open(template_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        logger.error(f"템플릿 읽기 오류: {str(e)}")
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Instagram 컨텐츠 분석</title>
        </head>
        <body>
            <h1>Instagram 컨텐츠 분석</h1>
            <div id="app">
                <input type="text" id="url" placeholder="Instagram URL을 입력하세요">
                <button onclick="analyze()">분석하기</button>
                <div id="result"></div>
            </div>
            <script>
                async function analyze() {
                    const url = document.getElementById('url').value;
                    const result = document.getElementById('result');
                    result.innerHTML = '분석 중...';
                    try {
                        const response = await fetch('/api/analyze', {
                            method: 'POST',
                            headers: {'Content-Type': 'application/json'},
                            body: JSON.stringify({url})
                        });
                        const data = await response.json();
                        result.innerHTML = `<pre>${JSON.stringify(data, null, 2)}</pre>`;
                    } catch (error) {
                        result.innerHTML = `오류: ${error.message}`;
                    }
                }
            </script>
        </body>
        </html>
        """

def handler(event, context):
    try:
        logger.info(f"요청 받음: {event}")
        
        method = event.get('httpMethod', 'GET')
        path = event.get('path', '/')
        
        # CORS 헤더
        headers = {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type'
        }
        
        # OPTIONS 요청 처리
        if method == 'OPTIONS':
            return {
                'statusCode': 200,
                'headers': headers,
                'body': ''
            }
        
        # API 엔드포인트 처리
        if method == 'POST' and path.startswith('/api/analyze'):
            try:
                body = json.loads(event.get('body', '{}'))
                url = body.get('url')
                
                if not url:
                    return {
                        'statusCode': 400,
                        'headers': {**headers, 'Content-Type': 'application/json'},
                        'body': json.dumps({'error': 'URL이 필요합니다'})
                    }
                
                # Instagram 스크래핑
                scraper = InstagramScraper()
                content = scraper.scrape(url)
                
                if not content:
                    return {
                        'statusCode': 400,
                        'headers': {**headers, 'Content-Type': 'application/json'},
                        'body': json.dumps({'error': '컨텐츠를 가져오지 못했습니다'})
                    }
                
                # 컨텐츠 분석
                analyzer = ContentAnalyzer()
                analysis_result = analyzer.analyze_content(content)
                
                return {
                    'statusCode': 200,
                    'headers': {**headers, 'Content-Type': 'application/json'},
                    'body': json.dumps(analysis_result)
                }
                
            except Exception as e:
                logger.error(f"분석 중 오류: {str(e)}\n{traceback.format_exc()}")
                return {
                    'statusCode': 500,
                    'headers': {**headers, 'Content-Type': 'application/json'},
                    'body': json.dumps({'error': str(e)})
                }
        
        # 메인 페이지 처리
        if method == 'GET' and (path == '/' or path == '/index.html'):
            return {
                'statusCode': 200,
                'headers': {**headers, 'Content-Type': 'text/html'},
                'body': read_template()
            }
        
        # 404 처리
        return {
            'statusCode': 404,
            'headers': {**headers, 'Content-Type': 'application/json'},
            'body': json.dumps({'error': 'Not Found'})
        }
        
    except Exception as e:
        logger.error(f"처리 중 오류 발생: {str(e)}\n{traceback.format_exc()}")
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'error': str(e)})
        }