# Instagram Hashtag Generator

インスタグラムの投稿から自動的にハッシュタグを生成するWebサービス

## 機能概要

- インスタグラム投稿URLからの画像・テキスト解析
- 日本語・英語ハッシュタグの自動生成
- 言語選択機能（日本語/英語）
- 生成ハッシュタグ数の選択（1-30個）

## 技術スタック

- フロントエンド
  - HTML/CSS/JavaScript
  - TailwindCSS（スタイリング）
  
- バックエンド
  - Python/Flask
  - Requesty LLM Routing Service（画像解析・テキスト生成）

- インフラ
  - Railway（ホスティング）

## プロジェクト構造

```
HashtagGenerator/
├── README.md
├── requirements.txt
├── app.py
├── static/
│   ├── css/
│   │   └── style.css
│   └── js/
│       └── main.js
└── templates/
    └── index.html
```

## セットアップ手順

1. 仮想環境の作成とアクティベート
```bash
python -m venv /Users/ete/venvs/hashtag_generator
source /Users/ete/venvs/hashtag_generator/bin/activate
```

2. 依存パッケージのインストール
```bash
pip install -r requirements.txt
```

3. アプリケーションの起動
```bash
python app.py
```

## デプロイ手順

1. Railwayにプロジェクトを作成
2. GitHubリポジトリと連携
3. 環境変数の設定
   - REQUESTY_API_KEY
4. デプロイの実行

## API仕様

### ハッシュタグ生成エンドポイント

- エンドポイント: `/generate`
- メソッド: POST
- リクエストボディ:
```json
{
  "url": "Instagram投稿URL",
  "language": "ja|en",
  "count": 1-30
}
```
- レスポンス:
```json
{
  "hashtags": [
    "#example",
    "#サンプル"
  ]
}