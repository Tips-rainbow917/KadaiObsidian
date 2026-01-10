# 音声文字起こしツール

このツールは、OpenAI Whisper APIを使用して音声ファイルを日本語で文字起こしします。

## セットアップ

### 1. 必要なライブラリのインストール

```bash
pip install openai python-dotenv
```

### 2. APIキーの設定

1. `.env.example`を`.env`にコピー:
   ```bash
   cp .env.example .env
   ```

2. `.env`ファイルを編集してOpenAI APIキーを設定:
   ```
   OPENAI_API_KEY=sk-your-actual-api-key-here
   ```

3. APIキーは [OpenAI Platform](https://platform.openai.com/api-keys) で取得できます

## 使用方法

```bash
python3 transcribe_openai.py "音声ファイル.m4a"
```

実行すると、以下のファイルが生成されます:
- `音声ファイル_文字起こし.txt` - 文字起こし結果

## サポートされている音声形式

- m4a
- mp3
- wav
- その他OpenAI Whisper APIがサポートする形式

## 注意事項

- `.env`ファイルはGit管理から除外されています（機密情報保護のため）
- APIの使用には料金が発生します
- 音声ファイルのサイズ制限: 25MB以下
