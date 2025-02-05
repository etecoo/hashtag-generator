from flask import Flask, render_template, request, jsonify
import requests
import os

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate_hashtags():
    data = request.get_json()
    instagram_url = data.get('url')
    language = data.get('language', 'ja')
    count = min(max(data.get('count', 10), 1), 30)

    try:
        # Requsty LLM Routing Serviceへのリクエスト
        # 実際のエンドポイントとパラメータは、Requstyのドキュメントに従って設定
        response = requests.post(
            'https://api.requsty.com/analyze',
            headers={
                'Authorization': f'Bearer {os.getenv("REQUSTY_API_KEY")}'
            },
            json={
                'url': instagram_url,
                'language': language,
                'count': count
            }
        )
        
        if response.status_code == 200:
            hashtags = response.json().get('hashtags', [])
            return jsonify({'hashtags': hashtags})
        else:
            return jsonify({'error': 'Failed to generate hashtags'}), 500

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)