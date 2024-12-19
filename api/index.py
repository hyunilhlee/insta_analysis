from flask import Flask, request, jsonify, render_template, Response
from flask_cors import CORS
import os
import sys
from http.server import BaseHTTPRequestHandler
import json

# 프로젝트 루트 디렉토리를 Python 경로에 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from analysis.analyzer import ContentAnalyzer
from scraping.scraper import InstagramScraper

def handle_request(request):
    if request.get('method') == 'POST' and request.get('path').startswith('/api/analyze'):
        try:
            body = json.loads(request.get('body', '{}'))
            url = body.get('url')
            
            if not url:
                return {
                    'statusCode': 400,
                    'body': json.dumps({'error': 'URL이 필요합니다'})
                }
                
            # Instagram 스크래핑
            scraper = InstagramScraper()
            content = scraper.scrape(url)
            
            # 컨텐츠 분석
            analyzer = ContentAnalyzer()
            analysis_result = analyzer.analyze_content(content)
            
            return {
                'statusCode': 200,
                'body': json.dumps(analysis_result)
            }
            
        except Exception as e:
            return {
                'statusCode': 500,
                'body': json.dumps({'error': str(e)})
            }
    
    elif request.get('method') == 'GET' and request.get('path') == '/api/health':
        return {
            'statusCode': 200,
            'body': json.dumps({'status': 'healthy'})
        }
    
    elif request.get('method') == 'GET' and request.get('path') == '/':
        try:
            with open('templates/index.html', 'r') as f:
                html_content = f.read()
            return {
                'statusCode': 200,
                'headers': {'Content-Type': 'text/html'},
                'body': html_content
            }
        except Exception as e:
            return {
                'statusCode': 500,
                'body': json.dumps({'error': str(e)})
            }
    
    return {
        'statusCode': 404,
        'body': json.dumps({'error': 'Not Found'})
    }

def handler(event, context):
    return handle_request({
        'method': event.get('httpMethod', 'GET'),
        'path': event.get('path', '/'),
        'body': event.get('body', '{}'),
        'headers': event.get('headers', {})
    })