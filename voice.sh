#!/bin/bash
# ワークフロー実行用ショートカット

# スクリプトがあるディレクトリに移動
cd "$(dirname "$0")"

# ワークフローを実行
python3 process_voice_memos.py
