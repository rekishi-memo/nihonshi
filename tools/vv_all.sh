#!/bin/bash
# 全セットの音声を、セットごとに作ってコミット・push する（途中で止まっても、もう一度動かせば続きから）。2026-11-14。
#   bash vv_all.sh <VOICEVOX のフォルダ> <VOICEVOX の venv の python> <声のID...>
#   例：bash vv_all.sh ~/vv ~/vv/venv/bin/python 3 14 46
set -u
VV=$1; PY=$2; shift 2; IDS="$*"
cd "$(dirname "$0")"
T=$(mktemp -d)
PACKS=$(node -e "
const {chromium}=require('playwright');(async()=>{const b=await chromium.launch();const p=await b.newPage();
await p.goto('file://'+require('path').resolve('../index.html'));await p.waitForTimeout(900);
console.log((await p.evaluate(()=>packOrder.filter(id=>packsById[id].lessons.length&&id!=='seiri').map(id=>id+'\t'+packsById[id].title))).join('\n'));await b.close();})();")
echo "$PACKS" | while IFS=$'\t' read -r pid title; do
  [ -z "$pid" ] && continue
  echo "== $pid $title"
  node vv_dump.js "$T/in.json" "$pid:*" || { echo "dump failed $pid"; continue; }
  "$PY" vv_make.py "$VV" "$T/in.json" $IDS 2>&1 | grep -v WARNING
  cd ..
  git add audio
  if ! git diff --cached --quiet; then
    git commit -q -m "音声：${title}（VOICEVOX）

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01Kwmj5WmmBFJYUqiGsjExiy"
    for i in 1 2 3 4; do git push -q origin main 2>/dev/null && { echo "pushed $pid"; break; }; sleep $((i*10)); done
  fi
  cd tools
done
echo "ALL DONE"
