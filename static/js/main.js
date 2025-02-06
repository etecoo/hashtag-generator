document.addEventListener('DOMContentLoaded', function() {
    // 生成数のプルダウンを初期化
    const hashtagCount = document.getElementById('hashtagCount');
    for (let i = 1; i <= 30; i++) {
        const option = document.createElement('option');
        option.value = i;
        option.textContent = i;
        if (i === 10) option.selected = true;
        hashtagCount.appendChild(option);
    }

    // DOM要素の取得
    const form = document.getElementById('hashtagForm');
    const result = document.getElementById('result');
    const hashtagsContainer = document.getElementById('hashtags');
    const errorContainer = document.getElementById('error');
    const copyButton = document.getElementById('copyButton');

    // 【変更の目的】
    // 以下の関数 generateHashtags は、フォーム送信時にInstagram URLの検証、バックエンドへのリクエスト、
    // 及びレスポンスに基づくUI更新を実施するために定義されています。
    // 名前付き関数として定義することで、外部からも参照可能になり、エラー発生のリスクを低減するとともに、
    // コードの可読性と再利用性を向上させます。
    async function generateHashtags(e) {
        // フォーム送信のデフォルト動作を無効化
        e.preventDefault();

        // UI状態の初期化：結果・エラー表示の非表示
        result.classList.add('hidden');
        errorContainer.classList.add('hidden');

        // フォームデータの取得
        const url = document.getElementById('instagramUrl').value.trim();
        const language = document.querySelector('input[name="language"]:checked').value;
        const count = parseInt(hashtagCount.value);

        // Instagram URLの基本的なバリデーション
        const instagramPattern = /^https?:\/\/(?:www\.)?instagram\.com\/(?:p|reel)\/[\w-]+\/?(?:\?[^;]*)?$/;
        if (!instagramPattern.test(url)) {
            errorContainer.querySelector('div').textContent = '無効なInstagram URLです';
            errorContainer.classList.remove('hidden');
            return;
        }

        // バックエンド API (/generate) へのリクエスト処理
        try {
            const response = await fetch('/generate', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ url, language, count })
            });
            const data = await response.json();
            if (response.ok) {
                // 生成されたハッシュタグの表示
                hashtagsContainer.innerHTML = data.hashtags
                    .map(tag => `<span class="inline-block bg-blue-100 text-blue-800 px-2 py-1 rounded mr-2 mb-2">${tag}</span>`)
                    .join('');
                result.classList.remove('hidden');
            } else {
                errorContainer.querySelector('div').textContent = data.error;
                errorContainer.classList.remove('hidden');
            }
        } catch (error) {
            errorContainer.querySelector('div').textContent = 'エラーが発生しました。もう一度お試しください。';
            errorContainer.classList.remove('hidden');
        }
    }

    // フォーム送信イベントに対して generateHashtags 関数を登録
    form.addEventListener('submit', generateHashtags);

    // クリップボードへのコピー機能の設定
    copyButton.addEventListener('click', function() {
        const hashtags = Array.from(hashtagsContainer.querySelectorAll('span'))
            .map(span => span.textContent)
            .join(' ');
        navigator.clipboard.writeText(hashtags).then(function() {
            const originalText = copyButton.textContent;
            copyButton.textContent = 'コピーしました！';
            setTimeout(() => {
                copyButton.textContent = originalText;
            }, 2000);
        });
    });
});