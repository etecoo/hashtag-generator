# 変更履歴

## [0.1.1] - 2025-02-05

### 更新
- Requsty API設定の更新
  - エンドポイントを実際のURLに更新（https://router.requesty.ai/v1）
  - 環境変数`REQUSTY_API_KEY`の設定をRailway用に準備

### 追加
- Railway用のデプロイ設定
  - Procfileの作成
  - gunicornによるプロダクション用サーバー設定

### Railway設定情報
- ビルドコマンド: `pip install -r requirements.txt`
- スタートコマンド: Procfileに定義（`gunicorn app:app`）
- 環境変数:
  - REQUSTY_API_KEY: Requsty APIキー

## [0.1.0] - 2025-02-05

### 追加
- プロジェクトの初期設定
  - Flaskアプリケーションの基本構造
  - 仮想環境の設定（/Users/ete/venvs/hashtag_generator）
  - 依存パッケージの設定（requirements.txt）

- フロントエンド実装
  - メインページのHTML実装（templates/index.html）
  - TailwindCSSの導入
  - JavaScriptによるフォーム処理（static/js/main.js）
  - カスタムスタイルの追加（static/css/style.css）

- バックエンド実装
  - Flaskルーティングの設定
  - Requsty LLM Service統合の準備
  - エラーハンドリングの実装

- ドキュメント作成
  - プロジェクト構造の文書化（00-CORE.md）
  - アーキテクチャ決定の記録（ADR.md）
  - システム設計の文書化（DESIGN.md）
  - 変更履歴の開始（CHANGELOG.md）

### 技術的変更
- Flask 3.0.2を採用
- TailwindCSSをCDN経由で導入
- RESTful APIエンドポイントの設計
- フォームバリデーションの実装
- クリップボード機能の実装

### セキュリティ
- 環境変数による設定管理の準備
- APIキーのセキュア管理の設定
- 入力値のバリデーション実装

### インフラ
- Railway用の設定準備
- 開発環境の構築