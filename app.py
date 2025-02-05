from flask import Flask, render_template, request, jsonify
import requests
import os
import re
import logging

# ロギングの設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

def validate_instagram_url(url):
    """InstagramのURLを検証する"""
    if not url:
        return False, "URLが入力されていません"
    
    instagram_pattern = r'^https?://(?:www\.)?instagram\.com/(?:p|reel)/[\w-]+/?.*$'
    if not re.match(instagram_pattern, url):
        return False, "無効なInstagram URLです"
    
    return True, None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate_hashtags():
    # APIキーの確認
    api_key = os.getenv("REQUSTY_API_KEY")
    if not api_key:
        logger.error("REQUSTY_API_KEY is not set")
        return jsonify({'error': 'API key is not configured'}), 500

    # リクエストデータの取得と検証
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400

    instagram_url = data.get('url')
    is_valid, error_message = validate_instagram_url(instagram_url)
    if not is_valid:
        return jsonify({'error': error_message}), 400

    language = data.get('language', 'ja')
    count = min(max(data.get('count', 10), 1), 30)

    try:
        # Requsty LLM Routing Serviceへのリクエスト
        logger.info(f"Sending request to Requsty API for URL: {instagram_url}")
        # リクエストパラメータの設定
        request_data = {
            'url': instagram_url,
            'language': language,
            'count': count,
            'model': 'anthropic/claude-3-5-sonnet-20241022',  # Anthropic Claude 3.5 Sonnet
            'options': {
                'max_tokens': 1000,
                'temperature': 0.7,
                'hashtag_style': 'instagram'
            }
        }
        
        logger.info(f"Request parameters: {request_data}")
        
        response = requests.post(
            'https://router.requesty.ai/v1',
            headers={
                'Authorization': f'Bearer {api_key}',
                'Content-Type': 'application/json'
            },
            json=request_data
        )
        
        # レスポンスの解析
        response_data = response.json()
        logger.info(f"Requsty API response status: {response.status_code}")
        
        if response.status_code == 200:
            hashtags = response_data.get('hashtags', [])
            if not hashtags:
                logger.warning("No hashtags generated from valid response")
                return jsonify({'error': 'No hashtags were generated'}), 500
            return jsonify({'hashtags': hashtags})
        else:
            error_message = response_data.get('error', 'Unknown error occurred')
            logger.error(f"Requsty API error: {error_message}")
            return jsonify({'error': f"Failed to generate hashtags: {error_message}"}), response.status_code

    except requests.exceptions.RequestException as e:
        logger.error(f"Request error: {str(e)}")
        return jsonify({'error': 'Failed to connect to the API service'}), 500
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return jsonify({'error': 'An unexpected error occurred'}), 500

if __name__ == '__main__':
    app.run(debug=True)