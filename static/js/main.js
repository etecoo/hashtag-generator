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

    // フォームの送信処理
    const form = document.getElementById('hashtagForm');
    const result = document.getElementById('result');
    const hashtagsContainer = document.getElementById('hashtags');
    const errorContainer = document.getElementById('error');
    const copyButton = document.getElementById('copyButton');

    form.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        // UI状態の初期化
        result.classList.add('hidden');
        errorContainer.classList.add('hidden');
        
        // フォームデータの取得と前処理
        const url = document.getElementById('instagramUrl').value.trim();
        const language = document.querySelector('input[name="language"]:checked').value;
        const count = parseInt(hashtagCount.value);

        // URLの基本的なバリデーション
        const instagram_pattern = /^https?:\/\/(?:www\.)?instagram\.com\/(?:p|reel)\/[\w-]+\/?(?:\?[^;]*)?$/;
        if (!instagram_pattern.test(url)) {
            errorContainer.querySelector('div').textContent = '無効なInstagram URLです';
            errorContainer.classList.remove('hidden');
            return;
        }

        try {
            const response = await fetch('/generate', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ url, language, count })
            });

            const data = await response.json();

            if (response.ok) {
                // ハッシュタグの表示
                hashtagsContainer.innerHTML = data.hashtags
                    .map(tag => `<span class="inline-block bg-blue-100 text-blue-800 px-2 py-1 rounded mr-2 mb-2">${tag}</span>`)
                    .join('');
                result.classList.remove('hidden');
            } else {
                // エラーメッセージの表示
                errorContainer.querySelector('div').textContent = data.error;
                errorContainer.classList.remove('hidden');
            }
        } catch (error) {
            errorContainer.querySelector('div').textContent = 'エラーが発生しました。もう一度お試しください。';
            errorContainer.classList.remove('hidden');
        }
    });

    // クリップボードへのコピー機能
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