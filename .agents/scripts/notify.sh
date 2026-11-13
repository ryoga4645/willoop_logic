#!/bin/bash
# MacOS desktop notification script for Antigravity

MESSAGE="${1:-ユーザーの承認待ち・もしくは作業が完了しました}"
TITLE="Antigravity Notification"

# 1. セキュリティ対策: osascriptに引数を安全に渡すため、AppleScriptの変数として標準入力から渡す
osascript -e 'on run argv' \
          -e 'display notification (item 1 of argv) with title (item 2 of argv)' \
          -e 'end run' "$MESSAGE" "$TITLE"

# 2. エラーハンドリングとパフォーマンス改善: ファイルの存在確認をしつつ、バックグラウンド(&)で再生する
SOUND_FILE="/System/Library/Sounds/Glass.aiff"
if [ -f "$SOUND_FILE" ]; then
    afplay "$SOUND_FILE" >/dev/null 2>&1 &
fi
