#!/usr/bin/env python3
"""
OpenAI Whisper APIを使用して音声ファイルを文字起こしするスクリプト
"""
import os
import sys
from pathlib import Path

def transcribe_with_openai(audio_file_path):
    """OpenAI Whisper APIを使用して音声を文字起こし"""
    try:
        from openai import OpenAI
        from dotenv import load_dotenv
        
        # .envファイルを読み込む
        env_path = Path(__file__).parent / '.env'
        load_dotenv(dotenv_path=env_path)
        
        # APIキーを環境変数から取得
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key or api_key == "your-api-key-here":
            print("エラー: OPENAI_API_KEYが設定されていません")
            print("\n以下の手順で設定してください:")
            print("1. .env.example を .env にコピー")
            print("   cp .env.example .env")
            print("2. .env ファイルを編集してAPIキーを設定")
            print("   OPENAI_API_KEY=sk-...")
            return None
        
        client = OpenAI(api_key=api_key)
        
        print(f"音声ファイルを文字起こし中: {audio_file_path}")
        print("OpenAI Whisper APIに送信しています...")
        
        with open(audio_file_path, "rb") as audio_file:
            transcript = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                language="ja"
            )
        
        return transcript.text
        
    except ImportError:
        print("openaiライブラリがインストールされていません")
        print("以下のコマンドでインストールしてください:")
        print("pip install openai")
        return None
    except Exception as e:
        print(f"エラーが発生しました: {e}")
        return None

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("使用方法: python transcribe_openai.py <音声ファイルパス>")
        sys.exit(1)
    
    audio_file = sys.argv[1]
    
    if not os.path.exists(audio_file):
        print(f"ファイルが見つかりません: {audio_file}")
        sys.exit(1)
    
    result = transcribe_with_openai(audio_file)
    
    if result:
        print("\n=== 文字起こし結果 ===")
        print(result)
        print("\n=== 完了 ===")
        
        # 結果をファイルに保存
        output_file = audio_file.replace(".m4a", "_文字起こし.txt")
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(result)
        print(f"\n結果を保存しました: {output_file}")
    else:
        print("文字起こしに失敗しました")
        sys.exit(1)
