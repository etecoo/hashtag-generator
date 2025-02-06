from flask import Flask, render_template, request, jsonify
import os
import re
import logging
import json
import openai

# ロギングの設定
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# OpenAIクライアントの初期化
def get_requesty_client():
    api_key = os.getenv("REQUESTY_API_KEY")
    if not api_key:
        raise ValueError("REQUESTY_API_KEY is not set")
    
    return openai.OpenAI(
        api_key=api_key,
        base_url="https://router.requesty.ai/v1"
    )

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

    # リクエストの生データを確認
    logger.info("Raw request data:")
    logger.info(f"Content-Type: {request.content_type}")
    logger.info(f"Raw data: {request.get_data(as_text=True)}")

    # リクエストデータの取得と検証
    try:
        raw_data = request.get_data(as_text=True)
        logger.info("Raw request data before parsing:")
        logger.info(f"Raw data: {raw_data}")
        logger.info(f"Raw data type: {type(raw_data)}")
        
        # 文字列が空でないことを確認
        if not raw_data:
            logger.error("Empty request data")
            return jsonify({'error': 'No data provided'}), 400
            
        # JSONデータのパース
        data = json.loads(raw_data)
        logger.info("Parsed JSON data:")
        logger.info(f"Type: {type(data)}")
        logger.info(f"Content: {data}")
        
        # セミコロンチェック
        if ';' in str(data):
            logger.warning("Semicolon found in parsed data")
            # セミコロンを含む場合はエラーとして扱う
            return jsonify({'error': 'Invalid character (semicolon) in request data'}), 400
            
    except json.JSONDecodeError as e:
        logger.error(f"JSON parse error: {str(e)}")
        logger.error(f"Raw data causing error: {raw_data}")
        return jsonify({'error': 'Invalid JSON format'}), 400
    except Exception as e:
        logger.error(f"Unexpected error during request processing: {str(e)}")
        return jsonify({'error': 'Error processing request data'}), 400

    if not data:
        return jsonify({'error': 'No data provided'}), 400

    # URLの存在確認と型チェック
    if 'url' not in data or not isinstance(data['url'], str):
        logger.error(f"Invalid URL in request data: {data.get('url')}")
        return jsonify({'error': 'Invalid URL format'}), 400

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

        # Requesty LLM Routing Serviceへのリクエスト
        logger.info(f"Sending request to Requesty API for URL: {instagram_url}")
        
        client = get_requesty_client()
        
        # プロンプトの構築
        prompt = f"""
        以下のInstagram投稿に関連するハッシュタグを{count}個生成してください。
        URL: {instagram_url}
        言語: {'日本語' if language == 'ja' else '英語'}
        """

        # OpenAIクライアントを使用してリクエスト
        response = client.chat.completions.create(
            model="anthropic/claude-3-5-sonnet-20241022",
            messages=[
                {
                    "role": "system",
                    "content": "あなたはInstagramのハッシュタグ生成の専門家です。"
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            max_tokens=1000,
            temperature=0.7
        )

        # レスポンスからハッシュタグを抽出
        generated_text = response.choices[0].message.content
        hashtags = [tag.strip() for tag in generated_text.split() if tag.startswith('#')]

        if not hashtags:
            logger.warning("No hashtags generated from valid response")
            return jsonify({'error': 'No hashtags were generated'}), 500

        return jsonify({'hashtags': hashtags[:count]})

    except openai.APIError as e:
        logger.error(f"OpenAI API error: {str(e)}")
        return jsonify({'error': f"Failed to generate hashtags: {str(e)}"}), 500
    except openai.APIConnectionError as e:
        logger.error(f"Connection Error: {str(e)}")
        return jsonify({'error': 'Failed to connect to the API service. Please check your network connection.'}), 500
    except openai.APITimeoutError as e:
        logger.error(f"Timeout Error: {str(e)}")
        return jsonify({'error': 'Request timed out'}), 500
    except openai.AuthenticationError as e:
        logger.error(f"Authentication Error: {str(e)}")
        return jsonify({'error': 'API authentication failed'}), 500
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return jsonify({'error': 'An unexpected error occurred'}), 500

if __name__ == '__main__':
    app.run(debug=True)
