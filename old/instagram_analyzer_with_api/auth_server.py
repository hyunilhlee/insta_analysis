from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import socket
import sys

class AuthHandler(BaseHTTPRequestHandler):
    timeout = 60
    
    def do_GET(self):
        try:
            path = self.path.split('?')[0]
            
            if path == '/privacy-policy':
                self.send_response(200)
                self.send_header('Content-type', 'text/html; charset=utf-8')
                self.end_headers()
                
                with open('privacy_policy.html', 'r', encoding='utf-8') as f:
                    content = f.read()
                self.wfile.write(content.encode('utf-8'))
                return
            
            client_ip = self.client_address[0]
            print(f"새로운 요청 받음: {client_ip} - {self.path}")
            query_components = parse_qs(urlparse(self.path).query)
            
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            if 'code' in query_components:
                message = f"인증 코드: {query_components['code'][0]}"
            else:
                message = "인증 코드를 찾을 수 없습니다."
                
            response = f"""
            <html>
                <head>
                    <meta charset="utf-8">
                </head>
                <body>
                    <h1>{message}</h1>
                    <p>이 코드를 복사하여 프로그램에 붙여넣으세요.</p>
                </body>
            </html>
            """
            print(f"응답 전송: {client_ip}")
            self.wfile.write(response.encode('utf-8'))
            
        except Exception as e:
            print(f"요청 처리 중 오류: {e}")
            self.send_error(500, f"Internal Server Error: {str(e)}")

def test_connection(host, port):
    print(f"\n=== 연결 테스트: {host}:{port} ===")
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(5)
    try:
        print(f"연결 시도: {host}:{port}")
        sock.connect((host, port))
        print(f"연결 성공: {host}:{port}")
        return True
    except Exception as e:
        print(f"연결 실패: {host}:{port} - {e}")
        return False
    finally:
        sock.close()

def run_server(host='0.0.0.0', port=8000, public_ip='3.35.105.254'):
    try:
        # 서버 설정
        server_address = (host, port)
        httpd = HTTPServer(server_address, AuthHandler)
        httpd.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        # 바인딩 정보 출력
        bound_addr = httpd.socket.getsockname()
        print(f"\n=== 서버 시작 ===")
        print(f"바인딩 주소: {bound_addr}")
        print(f"외부 접속 URL: http://{public_ip}:{port}/auth")
        
        # 연결 테스트
        if not test_connection('localhost', port):
            print("경고: 로컬 연결 실패")
        if not test_connection(public_ip, port):
            print("경고: 외부 연결 실패")
        
        print("\n서버가 요청을 기다리는 중...")
        httpd.serve_forever()
        
    except Exception as e:
        print(f"\n오류 발생: {e}")
        raise

if __name__ == '__main__':
    try:
        run_server()
    except KeyboardInterrupt:
        print("\n서버를 종료합니다.")
        sys.exit(0)
    except Exception as e:
        print(f"\n치명적 오류: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1) 