# 変更履歴

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
  - Requesty LLM Service統合の準備
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

## [0.1.2] - 2025-02-05

### 改善
- エラーハンドリングの強化
  - APIキーの存在チェックを追加
  - Instagram URLのバリデーション実装
  - Requstyからのエラーメッセージの詳細取得
- ロギング機能の実装
  - リクエスト情報のログ記録
  - レスポンスステータスのログ記録
  - エラー詳細のログ記録

### セキュリティ
- URLバリデーションの追加
  - Instagram投稿URLの形式チェック
  - 必須パラメータの検証

## [0.1.3] - 2025-02-05

### 追加
- Requsty APIのAIモデル設定
  - Anthropic Claude 3.5 Sonnetモデル（anthropic/claude-3-5-sonnet-20241022）を指定
  - 最適なパラメータを設定：
    * max_tokens: 1000
    * temperature: 0.7
    * hashtag_style: instagram

### 技術的変更
- リクエストパラメータの最適化
- ログ出力の詳細化

## [0.1.4] - 2025-02-05

### 修正
- 環境変数名の修正
  - REQUSTY_API_KEY → REQUESTY_API_KEY（スペルミス修正）

### 改善
- APIリクエストのエラーハンドリング強化
  - タイムアウト設定（30秒）の追加
  - SSL証明書検証の明示的な有効化
  - 詳細なエラーメッセージの実装
  - ネットワークエラーの詳細なログ記録

  [0.1.5] - 2025-02-06
### 改善
- フォーム送信処理のリファクタリングを実施
  - 匿名関数から明示的な名前付き関数 `generateHashtags` に変更
  - これにより、外部から `generateHashtags` 関数が参照可能となり、「ReferenceError: generateHashtags is not defined」エラーを解消
  - コードの可読性と再利用性が向上し、単体テスト等の将来的な拡張にも有利になる

## [0.1.6] - 2025-02-06
### 改善
- URLクリーニング処理の強化
  - 正規表現を使用してInstagramの基本URLのみを抽出するように改善
  - クエリパラメータを完全に除去する処理を追加
  - ログ出力の改善により、URL処理の追跡を容易に

- リクエストパラメータのログ出力を改善
  - JSON文字列化による問題を解消
  - より詳細で明確なログ形式を実装
  - デバッグ情報の可視性を向上