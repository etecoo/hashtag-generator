# Instagram Hashtag Generator - プロジェクト構造

## プロジェクト概要
インスタグラムの投稿URLから自動的にハッシュタグを生成するWebサービス。
画像解析とテキスト解析を組み合わせて、最適なハッシュタグを提案する。

## ディレクトリ構造
```
HashtagGenerator/
├── app.py                 # Flaskアプリケーションのメインファイル
├── requirements.txt       # Python依存パッケージ
├── static/               # 静的ファイル
│   ├── css/
│   │   └── style.css    # カスタムスタイル
│   └── js/
│       └── main.js      # フロントエンドロジック
├── templates/
│   └── index.html       # メインページテンプレート
└── docs/                # プロジェクトドキュメント
    ├── project-context/
    │   └── 00-CORE.md   # プロジェクト構造と設定
    ├── technical-decisions/
    │   ├── ADR.md       # アーキテクチャ決定記録
    │   └── DESIGN.md    # 設計文書
    └── work-history/
        ├── CHANGELOG.md # 変更履歴
        └── ISSUES.md    # 問題と解決策の記録
```

## 依存関係
### バックエンド（Python）
- Flask 3.0.2: Webアプリケーションフレームワーク
- Requests 2.31.0: HTTPクライアント
- python-dotenv 1.0.1: 環境変数管理
- gunicorn 21.2.0: WSGIサーバー

### フロントエンド
- TailwindCSS: UIフレームワーク（CDN経由）

### 外部サービス
- Requsty LLM Routing Service: 画像・テキスト解析API

## 環境設定
### 開発環境
- Python仮想環境: /Users/ete/venvs/hashtag_generator
- デバッグモード: 有効
- ポート: 5000

### 本番環境（Railway）
- 環境変数:
  - REQUESTY_API_KEY: Requesty APIキー
  - PORT: Railwayが提供するポート

## ドキュメント管理方針
1. コードの変更は必ずCHANGELOG.mdに記録
2. 技術的な決定はADR.mdに記録
3. 発生した問題と解決策はISSUES.mdに記録
4. システム設計の変更はDESIGN.mdに記録
5. プロジェクト構造の変更は00-CORE.mdに反映