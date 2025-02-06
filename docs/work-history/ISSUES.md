# 問題と解決策の記録

## アーカイブ参照
- 初期セットアップと基本機能実装: [ISSUE-001 - ISSUE-007](issues/archive-2025-02-06-part1.md)
- 初期のデバッグと問題解決: [ISSUE-008 - ISSUE-014](issues/archive-2025-02-06-part2.md)

## アクティブな問題

## [ISSUE-015] - 2025-02-06
### フロントエンド・バックエンド間のURL変換問題
#### 問題の発見
1. フロントエンドの動作：
   - 正規表現パターン `(?:\?[^;]*)?$` でセミコロンを含むURLを拒否
   - JSON.stringify で単純にURLを送信
   - 送信時点ではセミコロンは存在しないはず

2. バックエンドの動作：
   - リクエストデータにセミコロンが存在
   - 複数の除去処理を実装するも解決せず

#### 仮説
1. データ転送時の変換問題：
   - フロントエンドからバックエンドへの通信時に何らかの変換が発生
   - Content-Type: application/json の処理過程での問題の可能性

2. フレームワークの動作：
   - FlaskのJSON処理
   - request.get_json()の内部動作

#### 検証計画
1. フロントエンド側の確認：
   - 送信直前のURLの状態をログ出力
   - JSON.stringify後のデータ形式を確認

2. ネットワークレベルの確認：
   - ブラウザの開発者ツールでリクエストの生データを確認
   - 通信途中でのデータ変換の有無を確認

3. バックエンド側の確認：
   - リクエスト受信直後の生データを確認
   - request.get_json()前後のデータ形式を比較

#### 状態
- [ ] 検証開始待ち
- [ ] 原因特定待ち

## [ISSUE-016] - 2025-02-06
### セミコロン問題の継続調査状況まとめ
#### これまでの経緯
1. 段階的な対応の流れ：
   - [ISSUE-007](issues/archive-2025-02-06-part1.md#issue-007): 末尾のセミコロン除去（rstrip）
   - [ISSUE-012](issues/archive-2025-02-06-part2.md#issue-012): 正規表現によるURL抽出
   - [ISSUE-013](issues/archive-2025-02-06-part2.md#issue-013): JSONデータの検証追加
   - [ISSUE-014](issues/archive-2025-02-06-part2.md#issue-014): 包括的なセミコロン除去
   - ISSUE-015: フロントエンド・バックエンド間の変換問題調査

2. 実装済みの対策：
   - フロントエンド：
     * URLの正規表現バリデーション
     * UIベースのデバッグ情報表示
     * JSON変換過程の監視
   - バックエンド：
     * リクエストの生データログ
     * JSONパース前後の状態確認
     * 多層的なセミコロン除去

#### 現在の課題
1. 技術的な問題：
   - セミコロンが依然として混入
   - 404エラーが継続
   - JSONパースエラーが発生

2. 調査の必要な点：
   - フロントエンド→バックエンド間のデータ変換過程
   - Flaskのリクエスト処理メカニズム
   - Instagram URLの特性（意図的なセミコロン付加の可能性）

#### 次のステップ
1. 検証項目：
   - フロントエンドのUIデバッグ表示の確認
   - バックエンドの詳細ログの分析
   - ネットワークレベルのリクエスト確認

2. 追加調査が必要な点：
   - Instagram URLのコピー時の挙動
   - FlaskのJSON処理の詳細
   - ブラウザ拡張機能の影響

#### 参考情報
- 関連コミット：
  * 9d99a75: UIベースのデバッグ情報表示
  * acb5438: バックエンドログ強化
  * d6bdd9f: URL検証改善

#### 状態
- [ ] 新規タスクでの継続調査待ち

## [ISSUE-017] - 2025-02-06
### JSONパース時のセミコロン混入問題の特定
#### 問題の特定
1. データの流れ：
   ```
   フロントエンド送信データ:
   { "url": "https://www.instagram.com/p/DFkiqqsvq98/", "language": "ja", "count": 10 }

   バックエンド受信時の生データ:
   {"url":"https://www.instagram.com/p/DFkiqqsvq98/","language":"ja","count":10}

   JSONパース後のデータ:
   {'url': 'https://www.instagram.com/p/DFkiqqsvq98/';, 'language': 'ja', 'count': 10}
   ```

2. 重要な発見：
   - フロントエンド送信時：セミコロンなし
   - バックエンド受信時の生データ：セミコロンなし
   - JSONパース後：セミコロンが付加
   - 問題はFlaskのrequest.get_json()の内部処理で発生している可能性が高い

#### 仮説
1. Flask の request.get_json() の内部処理で変換が発生
   - JSONデコード時の文字列処理
   - Pythonオブジェクトへの変換過程

2. 対応方針：
   - request.get_json()を使用せず、生データを直接処理
   - 別のJSONパーサーの使用を検討
   - カスタムデコード処理の実装

#### 検証計画
1. 代替手段の実装：
   ```python
   raw_data = request.get_data(as_text=True)
   data = json.loads(raw_data)
   ```

2. デコード処理の検証：
   - 各段階でのデータ形式を確認
   - セミコロン混入のタイミングを特定
   - 文字エンコーディングの影響を確認

#### 状態
- [x] 問題特定完了
- [x] 修正実装完了
- [ ] 検証待ち

## [ISSUE-018] - 2025-02-06
### request.get_json()の代替実装による問題解決
#### 問題の背景
- ISSUE-017で特定されたFlaskのrequest.get_json()処理に起因する問題
- JSONパース時にセミコロンが混入する現象

#### 実装した修正
1. データ取得方法の変更：
   ```python
   # 変更前
   data = request.get_json()
   
   # 変更後
   raw_data = request.get_data(as_text=True)
   data = json.loads(raw_data)
   ```

2. 詳細なログ出力の追加：
   - パース前の生データの内容と型を記録
   - パース後のデータ構造を確認
   - セミコロンの存在チェックを実装

3. エラーハンドリングの強化：
   - 空データのチェック
   - JSONDecodeErrorの詳細なログ記録
   - セミコロン検出時の明示的なエラー処理

#### 期待される効果
- セミコロン混入問題の解消
- デバッグ情報の充実
- エラー発生時の原因特定の容易化

#### 検証項目
1. リクエストデータの正常なパース
2. セミコロンを含むデータの適切な処理
3. エラー時のログ出力確認

#### 状態
- [x] 実装完了
- [ ] 動作検証待ち

## [ISSUE-019] - 2025-02-06
### フロントエンド・バックエンド間の通信改善
#### 問題の背景
- レスポンスデータの処理が不完全
- デバッグ情報の表示が一時的な実装
- エラーハンドリングの強化が必要

#### 実装した修正
1. レスポンス処理の改善：
   ```javascript
   // 変更前
   if (response.ok) {
       hashtagsContainer.innerHTML = data.hashtags...
   }
   
   // 変更後
   const data = await response.json();
   if (response.ok && data.hashtags && Array.isArray(data.hashtags)) {
       hashtagsContainer.innerHTML = data.hashtags...
   }
   ```

2. デバッグ情報の強化：
   - リクエスト送信前のデータ検証
   - レスポンスステータスとデータの表示
   - セミコロン検出の警告表示

3. エラーハンドリングの改善：
   - レスポンスデータの型チェック
   - より詳細なエラーメッセージ
   - エラー状態の視覚的フィードバック

#### 期待される効果
- データ処理の信頼性向上
- デバッグ作業の効率化
- ユーザーへのフィードバック改善

#### 検証項目
1. レスポンスデータの正常な処理
2. デバッグ情報の適切な表示
3. エラー時の適切なフィードバック

#### 状態
- [x] 実装完了
- [ ] 動作検証待ち

## [ISSUE-020] - 2025-02-06
### リクエストデータ処理の構造的改善
#### 問題の背景
- コードの構造的な問題（インデント、重複したreturn文）
- try-exceptブロックの不適切な入れ子
- セミコロンチェック処理の散在

#### 実装した修正
1. コード構造の改善：
   - インデントの修正
   - 重複したreturn文の削除
   - try-exceptブロックの整理

2. セミコロンチェック処理の統合：
   ```python
   def check_semicolon(obj):
       if isinstance(obj, dict):
           return any(check_semicolon(v) for v in obj.values())
       elif isinstance(obj, list):
           return any(check_semicolon(v) for v in obj)
       elif isinstance(obj, str):
           return ';' in obj
       return False
   ```

3. リクエストデータ検証の強化：
   - JSONシリアライズ/デシリアライズによる検証
   - 階層的なセミコロンチェック
   - 検証済みデータの使用

#### 期待される効果
- コードの可読性向上
- エラー処理の信頼性向上
- データ検証の確実性向上

#### 検証項目
1. リクエストデータの正常な処理
2. エラー時の適切なハンドリング
3. セミコロンチェックの確実な実行

#### 状態
- [x] 実装完了
- [ ] 動作検証待ち

## [ISSUE-021] - 2025-02-06
### Requesty LLM Service接続エラー
#### 問題
- 送信前のURL: https://www.instagram.com/p/DFkiqqsvq98/
- データ内容: { "url": "https://www.instagram.com/p/DFkiqqsvq98/", "language": "ja", "count": 10 }
- レスポンス情報:
  * ステータス: 500
  * データ: { "error": "Failed to connect to the API service" }

#### 仮説
1. API接続の問題：
   - ネットワーク接続の問題
   - APIキーの設定や認証の問題
   - SSLの問題

2. 環境変数の問題：
   - REQUESTY_API_KEYの未設定または無効化
   - 環境変数の読み込みエラー

#### 検証計画
1. 環境変数の確認：
   - REQUESTY_API_KEYの存在確認
   - APIキーの有効性確認

2. ネットワーク接続の確認：
   - Requesty APIへの疎通確認
   - SSLの設定確認
   - タイムアウト設定の確認

3. APIサービスの状態確認：
   - Requesty LLM Serviceのステータス確認
   - サービスの稼働状態確認

#### 状態
- [ ] 環境変数確認待ち
- [ ] ネットワーク接続確認待ち
- [ ] APIサービス状態確認待ち
