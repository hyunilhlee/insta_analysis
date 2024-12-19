from http.server import BaseHTTPRequestHandler
from urllib.parse import parse_qs
import json
import os
import sys
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

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path.endswith('.js'):
            self._serve_static_file(self.path[1:], 'application/javascript')
        elif self.path.endswith('.css'):
            self._serve_static_file(self.path[1:], 'text/css')
        else:
            self._set_headers()
            self.wfile.write(read_template().encode())

    def _serve_static_file(self, file_path, content_type):
        try:
            with open(os.path.join(root_dir, file_path), 'rb') as f:
                self.send_response(200)
                self.send_header('Content-type', content_type)
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(f.read())
        except FileNotFoundError:
            self.send_error(404, f'File not found: {file_path}')
        except Exception as e:
            logger.error(f"파일 제공 중 오류: {str(e)}")
            self.send_error(500, f'Internal server error: {str(e)}')

    def do_POST(self):
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            
            body = json.loads(post_data.decode())
            url = body.get('url')
            
            if not url:
                self._json_response({'error': 'URL이 필요합니다'}, 400)
                return
            
            logger.info(f"분석 시작: {url}")
            
            # Instagram 스크래핑
            scraper = InstagramScraper()
            content = scraper.scrape(url)
            
            if not content:
                self._json_response({'error': '컨텐츠를 가져오지 못했습니다'}, 400)
                return
            
            logger.info("스크래핑 완료, 분석 시작")
            
            # 컨텐츠 분석
            analyzer = ContentAnalyzer()
            analysis_result = analyzer.analyze_content(content)
            
            logger.info("분석 완료")
            self._json_response(analysis_result)
            
        except json.JSONDecodeError as e:
            logger.error(f"JSON 디코딩 오류: {str(e)}")
            self._json_response({'error': 'Invalid JSON format'}, 400)
        except Exception as e:
            logger.error(f"분석 중 오류: {str(e)}\n{traceback.format_exc()}")
            self._json_response({'error': f'분석 중 오류가 발생했습니다: {str(e)}'}, 500)

    def _set_headers(self, content_type='text/html'):
        self.send_response(200)
        self.send_header('Content-type', content_type)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def _json_response(self, data, status=200):
        self.send_response(status)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

    def do_OPTIONS(self):
        self._set_headers()