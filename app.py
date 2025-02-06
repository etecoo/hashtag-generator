from flask import Flask, render_template, request, jsonify
import requests
import os
import re
import logging
import json

# ロギングの設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

def validate_instagram_url(url):
    """InstagramのURLを検証する"""
    if not url:
        return False, "URLが入力されていません"
    
    # クエリパラメータを含むベースURLのパターン
    instagram_pattern = r'^https?://(?:www\.)?instagram\.com/(?:p|reel)/[\w-]+/?(?:\?[^;]*)?$'
    if not re.match(instagram_pattern, url):
        return False, "無効なInstagram URLです"
    
    return True, None

def clean_url(url):
    """URLをクリーニングする"""
    if not isinstance(url, str):
        return ""
    
    # URLからクエリパラメータを除去し、基本的なパスのみを保持
    base_url_pattern = r'(https?://(?:www\.)?instagram\.com/(?:p|reel)/[\w-]+)/?'
    match = re.match(base_url_pattern, url)
    if not match:
        return ""
    
    cleaned = match.group(1)
    logger.info(f"Original URL: {url}")
    logger.info(f"Cleaned URL: {cleaned}")
    return cleaned

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate_hashtags():
    # APIキーの確認
    api_key = os.getenv("REQUESTY_API_KEY")
    if not api_key:
        logger.error("REQUESTY_API_KEY is not set")
        return jsonify({'error': 'API key is not configured'}), 500

    # リクエストデータの取得と検証
    try:
        data = request.get_json()
    except Exception as e:
        logger.error(f"JSON parse error: {str(e)}")
        return jsonify({'error': 'Invalid JSON format'}), 400

    if not data:
        return jsonify({'error': 'No data provided'}), 400

    # URLの取得と正規化
    instagram_url = clean_url(data.get('url', ''))
    logger.info(f"Cleaned Instagram URL: {instagram_url}")
    is_valid, error_message = validate_instagram_url(instagram_url)
    if not is_valid:
        return jsonify({'error': error_message}), 400

    # 言語パラメータの検証
    language = data.get('language', 'ja')
    if not isinstance(language, str) or language not in ['ja', 'en']:
        logger.warning(f"Invalid language parameter: {language}")
        language = 'ja'  # デフォルト値を設定

    # 生成数の検証と正規化
    try:
        count = int(data.get('count', 10))
        count = min(max(count, 1), 30)
    except (TypeError, ValueError):
        logger.warning(f"Invalid count parameter: {data.get('count')}")
        count = 10  # デフォルト値を設定

    try:
        # Requesty LLM Routing Serviceへのリクエスト
        logger.info(f"Sending request to Requesty API for URL: {instagram_url}")
        
        # URLの厳密な検証とクリーニング
        if ';' in instagram_url:
            logger.warning(f"Semicolon found in URL: {instagram_url}")
            instagram_url = instagram_url.replace(';', '')
            logger.info(f"Removed semicolon from URL: {instagram_url}")

        # リクエストデータの構築前に文字列を検証
        if not isinstance(instagram_url, str):
            logger.error("URL is not a string")
            return jsonify({'error': 'Invalid URL format'}), 400

        if not instagram_url:
            logger.error("Empty URL after cleaning")
            return jsonify({'error': 'Invalid URL format'}), 400

        # リクエストデータの構築
        request_data = {
            'url': instagram_url,  # セミコロンが除去されたURL
            'language': language,
            'count': count,
            'model': 'anthropic/claude-3-5-sonnet-20241022',
            'options': {
                'max_tokens': 1000,
                'temperature': 0.7,
                'hashtag_style': 'instagram'
            }
        }

        # リクエストデータの文字列表現を確認
        request_str = str(request_data)
        if ';' in request_str:
            logger.error(f"Semicolon found in request data: {request_str}")
            return jsonify({'error': 'Invalid character in request'}), 400

        logger.info("Request parameters:")
        logger.info(request_data)
        
        logger.info("Validated request parameters:")
        logger.info(request_data)
        logger.info(f"Request URL: {request_data['url']}")
        logger.info(f"URL length: {len(request_data['url'])}")
        
        response = requests.post(
            'https://router.requesty.ai/v1',
            headers={
                'Authorization': f'Bearer {api_key}',
                'Content-Type': 'application/json'
            },
            json=request_data,
            timeout=30,
            verify=True
        )
        # レスポンス全文ログ出力:
        # APIから返されたレスポンス全文をログに出力することで、
        # JSONパースエラーの原因となる余分な文字列（例：プレフィックスや複数のJSONオブジェクト）を確認できるようにしています。
        logger.info(f"Full Requesty API response text: {response.text}")
        
        # レスポンスの解析: 取得したレスポンスをJSON形式に変換します。
        try:
            response_data = response.json()
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON from Requesty API response: {response.text}")
            import re
            match = re.search(r'({.*})', response.text.strip())
            if match:
                logger.info(f"Regex match extracted JSON string: {match.group(1)}")
                try:
                    response_data = json.loads(match.group(1))
                except json.JSONDecodeError as e2:
                    logger.error(f"JSON extraction failed: {e2}")
                    raise e2
            else:
                raise e
        logger.info(f"Extracted JSON: {response_data}")
        logger.info(f"Requesty API response status: {response.status_code}")
        
        if response.status_code == 200:
            hashtags = response_data.get('hashtags', [])
            if not hashtags:
                logger.warning("No hashtags generated from valid response")
                return jsonify({'error': 'No hashtags were generated'}), 500
            return jsonify({'hashtags': hashtags})
        else:
            error_message = response_data.get('error', 'Unknown error occurred')
            logger.error(f"Requesty API error: {error_message}")
            return jsonify({'error': f"Failed to generate hashtags: {error_message}"}), response.status_code

    except requests.exceptions.Timeout:
        logger.error("Request timed out")
        return jsonify({'error': 'Request timed out after 30 seconds'}), 500
    except requests.exceptions.SSLError as e:
        logger.error(f"SSL Error: {str(e)}")
        return jsonify({'error': 'SSL verification failed'}), 500
    except requests.exceptions.ConnectionError as e:
        logger.error(f"Connection Error: {str(e)}")
        return jsonify({'error': 'Failed to connect to the API service. Please check your network connection.'}), 500
    except requests.exceptions.RequestException as e:
        logger.error(f"Request error: {str(e)}")
        return jsonify({'error': 'Failed to connect to the API service'}), 500
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return jsonify({'error': 'An unexpected error occurred'}), 500

if __name__ == '__main__':
    app.run(debug=True)
