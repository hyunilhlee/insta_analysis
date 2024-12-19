import requests

def test_instagram_api():
    # 앱 정보
    app_id = "2238165979903572"
    app_secret = "7fa1a2d691a0ed2bbb77365eeb7dc90e"
    
    # 앱 액세스 토큰 얻기
    access_token_url = f"https://graph.facebook.com/oauth/access_token"
    params = {
        'client_id': app_id,
        'client_secret': app_secret,
        'grant_type': 'client_credentials'
    }
    
    try:
        # 앱 액세스 토큰 요청
        response = requests.get(access_token_url, params=params)
        if response.status_code == 200:
            app_access_token = response.json()['access_token']
            print("앱 액세스 토큰 발급 성공")
            
            # 테스트 API 호출
            test_url = f"https://graph.facebook.com/v18.0/debug_token"
            test_params = {
                'input_token': app_access_token,
                'access_token': app_access_token
            }
            
            test_response = requests.get(test_url, params=test_params)
            print(f"테스트 API 응답: {test_response.status_code}")
            print(f"응답 내용: {test_response.json()}")
            
        else:
            print(f"토큰 발급 실패: {response.text}")
            
    except Exception as e:
        print(f"오류 발생: {e}")

if __name__ == "__main__":
    test_instagram_api() 