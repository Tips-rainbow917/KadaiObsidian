#!/usr/bin/env python3
"""
音声ファイルを文字起こしするスクリプト
OpenAI Whisper APIを使用
"""
import os
import sys

def transcribe_audio(audio_file_path):
    """音声ファイルを文字起こし"""
    try:
        # speech_recognitionを使用してローカルで処理
        import speech_recognition as sr
        
        # 音声ファイルを読み込む
        recognizer = sr.Recognizer()
        
        # m4aをサポートするためにpydubを使用
        from pydub import AudioSegment
        
        print(f"音声ファイルを読み込んでいます: {audio_file_path}")
        
        # m4aをwavに変換
        audio = AudioSegment.from_file(audio_file_path, format="m4a")
        wav_path = audio_file_path.replace(".m4a", "_temp.wav")
        audio.export(wav_path, format="wav")
        
        print("音声を認識中...")
        with sr.AudioFile(wav_path) as source:
            audio_data = recognizer.record(source)
            
        # Google Speech Recognitionを使用（無料）
        text = recognizer.recognize_google(audio_data, language='ja-JP')
        
        # 一時ファイルを削除
        if os.path.exists(wav_path):
            os.remove(wav_path)
            
        return text
        
    except ImportError as e:
        print(f"必要なライブラリがインストールされていません: {e}")
        print("以下のコマンドでインストールしてください:")
        print("pip install SpeechRecognition pydub")
        return None
    except Exception as e:
        print(f"エラーが発生しました: {e}")
        return None

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("使用方法: python transcribe_audio.py <音声ファイルパス>")
        sys.exit(1)
    
    audio_file = sys.argv[1]
    
    if not os.path.exists(audio_file):
        print(f"ファイルが見つかりません: {audio_file}")
        sys.exit(1)
    
    result = transcribe_audio(audio_file)
    
    if result:
        print("\n=== 文字起こし結果 ===")
        print(result)
        print("\n=== 完了 ===")
        
        # 結果をファイルに保存
        output_file = audio_file.replace(".m4a", "_transcript.txt")
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(result)
        print(f"\n結果を保存しました: {output_file}")
    else:
        print("文字起こしに失敗しました")
        sys.exit(1)
