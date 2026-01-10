#!/usr/bin/env python3
"""
音声ファイル自動文字起こしワークフロー

00ボイスメモ内の音声ファイルを自動的に文字起こしし、
AI分析で構造化・要約して、Obsidianノートとして保存します。
"""
import os
import sys
from pathlib import Path
from datetime import datetime
import shutil
import json

def load_env():
    """環境変数を読み込む"""
    try:
        from dotenv import load_dotenv
        env_path = Path(__file__).parent / '.env'
        load_dotenv(dotenv_path=env_path)
    except ImportError:
        print("警告: python-dotenvがインストールされていません")
        print("pip install python-dotenv")

def get_openai_client():
    """OpenAIクライアントを取得"""
    try:
        from openai import OpenAI
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key or api_key == "your-api-key-here":
            print("エラー: OPENAI_API_KEYが設定されていません")
            print(".envファイルを確認してください")
            return None
        return OpenAI(api_key=api_key)
    except ImportError:
        print("エラー: openaiライブラリがインストールされていません")
        print("pip install openai")
        return None

def find_audio_files(voice_memo_dir):
    """音声ファイルを検出"""
    audio_extensions = ['.m4a', '.mp3', '.wav', '.mp4']
    audio_files = []
    
    for file in Path(voice_memo_dir).iterdir():
        if file.is_file() and file.suffix.lower() in audio_extensions:
            audio_files.append(file)
    
    return audio_files

def find_existing_transcript(audio_file, voice_memo_dir, processed_dir):
    """既存の文字起こし.txtファイルを検索"""
    base_name = audio_file.stem
    
    # 00ボイスメモ内を検索
    txt_path = Path(voice_memo_dir) / f"{base_name}.txt"
    if txt_path.exists():
        print(f"✓ 既存の文字起こしファイルを発見: {txt_path}")
        return txt_path
    
    # processed内を検索
    txt_path_processed = Path(processed_dir) / f"{base_name}.txt"
    if txt_path_processed.exists():
        print(f"✓ 既存の文字起こしファイルを発見（processed内）: {txt_path_processed}")
        return txt_path_processed
    
    # _文字起こし.txt形式も検索
    txt_path_alt = Path(voice_memo_dir) / f"{base_name}_文字起こし.txt"
    if txt_path_alt.exists():
        print(f"✓ 既存の文字起こしファイルを発見: {txt_path_alt}")
        return txt_path_alt
    
    return None

def transcribe_audio(audio_file, client):
    """OpenAI Whisper APIで音声を文字起こし"""
    print(f"🎤 音声ファイルを文字起こし中: {audio_file.name}")
    print("   OpenAI Whisper APIに送信しています...")
    
    try:
        with open(audio_file, "rb") as f:
            transcript = client.audio.transcriptions.create(
                model="whisper-1",
                file=f,
                language="ja"
            )
        
        text = transcript.text
        print(f"✓ 文字起こし完了（{len(text)}文字）")
        
        # .txtファイルとして保存
        txt_path = audio_file.parent / f"{audio_file.stem}.txt"
        with open(txt_path, "w", encoding="utf-8") as f:
            f.write(text)
        print(f"✓ 文字起こしを保存: {txt_path}")
        
        return text
    except Exception as e:
        print(f"✗ 文字起こしエラー: {e}")
        return None

def analyze_and_structure(transcript_text, client):
    """AIで文字起こしを分析・構造化"""
    print("🤖 AIで分析・構造化中...")
    
    prompt = f"""以下の音声文字起こしテキストを分析し、以下の形式でJSON形式で返してください：

{{
  "title": "内容を表す簡潔なタイトル（20文字以内）",
  "summary": "3-5行程度の要約",
  "tags": ["タグ1", "タグ2", "タグ3"],
  "sections": [
    {{"heading": "見出し1", "content": "この見出しに関連する内容の要約"}},
    {{"heading": "見出し2", "content": "この見出しに関連する内容の要約"}}
  ]
}}

文字起こしテキスト:
{transcript_text}
"""
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "あなたは音声メモを分析し、構造化するアシスタントです。必ずJSON形式で返してください。"},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"}
        )
        
        result = json.loads(response.choices[0].message.content)
        print("✓ AI分析完了")
        return result
    except Exception as e:
        print(f"✗ AI分析エラー: {e}")
        # フォールバック: 基本的な構造を返す
        return {
            "title": "音声メモ",
            "summary": transcript_text[:200] + "...",
            "tags": ["音声メモ", "文字起こし"],
            "sections": []
        }

def create_obsidian_note(audio_file, transcript_text, analysis, output_dir):
    """Obsidianノートを生成"""
    print("📝 Obsidianノートを生成中...")
    
    # ファイル名（日付_タイトル形式）
    today = datetime.now().strftime("%Y-%m-%d")
    safe_title = analysis['title'].replace('/', '_').replace('\\', '_')
    output_filename = f"{today}_{safe_title}.md"
    output_path = Path(output_dir) / output_filename
    
    # YAMLフロントマター
    tags_yaml = "\n  - ".join(["文字起こし", "音声"] + analysis.get('tags', []))
    frontmatter = f"""---
タイトル: {analysis['title']}
作成日: {today}
元ファイル: {audio_file.name}
タグ:
  - {tags_yaml}
カテゴリ: 音声メモ
---

"""
    
    # 音声埋め込みリンク
    audio_embed = f"![[{audio_file.name}]]\n\n"
    
    # 要約セクション
    summary_section = f"""## 📝 要約

{analysis['summary']}

"""
    
    # 構造化セクション
    structured_section = ""
    if analysis.get('sections'):
        structured_section = "## 🗂️ 内容\n\n"
        for section in analysis['sections']:
            structured_section += f"### {section['heading']}\n\n{section['content']}\n\n"
    
    # 全文文字起こし
    transcript_section = f"""## 📄 全文文字起こし

{transcript_text}

---

*文字起こし日時: {today}*  
*使用ツール: OpenAI Whisper API*
"""
    
    # 結合
    content = frontmatter + audio_embed + summary_section + structured_section + transcript_section
    
    # 保存
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(content)
    
    print(f"✓ Obsidianノートを保存: {output_path}")
    return output_path

def move_to_processed(audio_file, processed_dir):
    """処理済みファイルをアーカイブ"""
    print(f"📦 処理済みファイルを移動中...")
    
    processed_path = Path(processed_dir)
    processed_path.mkdir(parents=True, exist_ok=True)
    
    destination = processed_path / audio_file.name
    
    # 同名ファイルが存在する場合はタイムスタンプを付ける
    if destination.exists():
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        destination = processed_path / f"{audio_file.stem}_{timestamp}{audio_file.suffix}"
    
    shutil.move(str(audio_file), str(destination))
    print(f"✓ 移動完了: {destination}")

def process_single_file(audio_file, voice_memo_dir, processed_dir, output_dir, client):
    """1つの音声ファイルを処理"""
    print(f"\n{'='*60}")
    print(f"処理開始: {audio_file.name}")
    print(f"{'='*60}")
    
    # 1. 既存の文字起こしを検索
    existing_txt = find_existing_transcript(audio_file, voice_memo_dir, processed_dir)
    
    if existing_txt:
        # 既存の.txtファイルを使用
        with open(existing_txt, "r", encoding="utf-8") as f:
            transcript_text = f.read()
        print(f"✓ 既存の文字起こしを使用（{len(transcript_text)}文字）")
    else:
        # 新規文字起こし
        transcript_text = transcribe_audio(audio_file, client)
        if not transcript_text:
            print("✗ 文字起こしに失敗しました。スキップします。")
            return False
    
    # 2. AI分析
    analysis = analyze_and_structure(transcript_text, client)
    
    # 3. Obsidianノート生成
    note_path = create_obsidian_note(audio_file, transcript_text, analysis, output_dir)
    
    # 4. 処理済みファイルを移動
    move_to_processed(audio_file, processed_dir)
    
    print(f"✓ 処理完了: {audio_file.name}")
    return True

def main():
    """メイン処理"""
    print("🎵 音声ファイル自動文字起こしワークフロー")
    print("="*60)
    
    # 環境変数読み込み
    load_env()
    
    # OpenAIクライアント取得
    client = get_openai_client()
    if not client:
        sys.exit(1)
    
    # ディレクトリ設定
    base_dir = Path(__file__).parent
    voice_memo_dir = base_dir / "00ボイスメモ"
    output_dir = base_dir / "01文字起こし"
    processed_dir = voice_memo_dir / "processed"
    
    # ディレクトリ確認
    if not voice_memo_dir.exists():
        print(f"エラー: {voice_memo_dir} が存在しません")
        sys.exit(1)
    
    # 出力ディレクトリ作成
    output_dir.mkdir(exist_ok=True)
    processed_dir.mkdir(exist_ok=True)
    
    # 音声ファイル検出
    audio_files = find_audio_files(voice_memo_dir)
    
    if not audio_files:
        print(f"\n音声ファイルが見つかりませんでした: {voice_memo_dir}")
        print("処理を終了します。")
        return
    
    print(f"\n検出した音声ファイル: {len(audio_files)}件")
    for f in audio_files:
        print(f"  - {f.name}")
    
    # バッチ処理
    success_count = 0
    fail_count = 0
    
    for audio_file in audio_files:
        try:
            if process_single_file(audio_file, voice_memo_dir, processed_dir, output_dir, client):
                success_count += 1
            else:
                fail_count += 1
        except Exception as e:
            print(f"✗ エラーが発生しました: {e}")
            fail_count += 1
    
    # 結果サマリー
    print(f"\n{'='*60}")
    print("処理完了")
    print(f"{'='*60}")
    print(f"成功: {success_count}件")
    print(f"失敗: {fail_count}件")
    print(f"出力先: {output_dir}")

if __name__ == "__main__":
    main()
