from flask import Flask, request, jsonify, render_template, Response, send_from_directory
from flask_cors import CORS
import os
import sys
import logging
import traceback
from http.server import BaseHTTPRequestHandler
import json

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 프로젝트 루트 디렉토리를 Python 경로에 추가
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(root_dir)

from analysis.analyzer import ContentAnalyzer
from scraping.scraper import InstagramScraper

def handle_request(request):
    logger.info(f"요청 받음: {request.get('method')} {request.get('path')}")
    
    if request.get('method') == 'POST' and request.get('path').startswith('/api/analyze'):
        try:
            logger.info("분석 요청 시작")
            body = json.loads(request.get('body', '{}'))
            url = body.get('url')
            
            if not url:
                logger.error("URL이 제공되지 않았습니다")
                return {
                    'statusCode': 400,
                    'body': json.dumps({'error': 'URL이 필요합니다'})
                }
            
            logger.info(f"URL 분석 시작: {url}")
                
            # Instagram 스크래핑
            scraper = InstagramScraper()
            logger.info("스크래핑 시작")
            content = scraper.scrape(url)
            logger.info("스크래핑 완료")
            
            if not content:
                logger.error("컨텐츠를 가져오지 못했습니다")
                return {
                    'statusCode': 400,
                    'body': json.dumps({'error': '컨텐츠를 가져오지 못했습니다'})
                }
            
            # 컨텐츠 분석
            logger.info("컨텐츠 분석 시작")
            analyzer = ContentAnalyzer()
            analysis_result = analyzer.analyze_content(content)
            logger.info("컨텐츠 분석 완료")
            
            return {
                'statusCode': 200,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Methods': 'POST, OPTIONS',
                    'Access-Control-Allow-Headers': 'Content-Type'
                },
                'body': json.dumps(analysis_result)
            }
            
        except Exception as e:
            error_trace = traceback.format_exc()
            logger.error(f"분석 중 오류 발생: {str(e)}\n{error_trace}")
            return {
                'statusCode': 500,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({
                    'error': f"분석 중 오류가 발생했습니다: {str(e)}",
                    'details': error_trace
                })
            }
    
    elif request.get('method') == 'GET' and request.get('path') == '/api/health':
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({'status': 'healthy'})
        }
    
    elif request.get('method') == 'GET':
        try:
            path = request.get('path', '/')
            
            # 정적 파일 요청 처리
            if path.startswith('/static/'):
                file_path = os.path.join(root_dir, path[1:])  # /static/을 제거하고 경로 생성
                try:
                    with open(file_path, 'rb') as f:
                        content = f.read()
                    content_type = 'text/css' if path.endswith('.css') else 'application/javascript' if path.endswith('.js') else 'text/plain'
                    return {
                        'statusCode': 200,
                        'headers': {
                            'Content-Type': content_type,
                            'Access-Control-Allow-Origin': '*'
                        },
                        'body': content.decode('utf-8')
                    }
                except:
                    logger.error(f"정적 파일을 찾을 수 없음: {file_path}")
            
            # 메인 페이지 요청 처리
            template_path = os.path.join(root_dir, 'templates', 'index.html')
            try:
                with open(template_path, 'r', encoding='utf-8') as f:
                    html_content = f.read()
                return {
                    'statusCode': 200,
                    'headers': {
                        'Content-Type': 'text/html',
                        'Access-Control-Allow-Origin': '*'
                    },
                    'body': html_content
                }
            except Exception as e:
                error_trace = traceback.format_exc()
                logger.error(f"HTML 파일 읽기 오류: {str(e)}\n{error_trace}")
                return {
                    'statusCode': 500,
                    'body': json.dumps({'error': str(e), 'details': error_trace})
                }
        except Exception as e:
            error_trace = traceback.format_exc()
            logger.error(f"요청 처리 중 오류 발생: {str(e)}\n{error_trace}")
            return {
                'statusCode': 500,
                'body': json.dumps({'error': str(e), 'details': error_trace})
            }
    
    return {
        'statusCode': 404,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        },
        'body': json.dumps({'error': 'Not Found'})
    }

def handler(event, context):
    try:
        logger.info(f"요청 받음: {event}")
        response = handle_request({
            'method': event.get('httpMethod', 'GET'),
            'path': event.get('path', '/'),
            'body': event.get('body', '{}'),
            'headers': event.get('headers', {})
        })
        logger.info(f"응답 전송: {response.get('statusCode')}")
        return response
    except Exception as e:
        error_trace = traceback.format_exc()
        logger.error(f"처리 중 오류 발생: {str(e)}\n{error_trace}")
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'error': '서버 오류가 발생했습니다',
                'details': str(e),
                'trace': error_trace
            })
        }