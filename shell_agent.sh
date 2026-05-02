#!/bin/bash
(
HISTORY="$(jq -cn --arg PROMPT "$PROMPT" '[{"content": $PROMPT, "role": "system"}]')"
add() {
    printf "%s:\n%s\n\n" "$ROLE" "$CONTENT"
    HISTORY="$(echo "$HISTORY" | jq -c --arg ROLE "$ROLE" --arg CONTENT "$CONTENT" '.[.|length] |= . + {"content": $CONTENT, "role": $ROLE}')"
}
set -euo pipefail
while :; do
    ROLE=assistant
    CONTENT="$(curl -fsSL "https://openrouter.ai/api/v1/chat/completions" -H "Authorization: Bearer $OPENROUTER_API_KEY" -d "$(jq -cn --argjson HISTORY "$HISTORY" '{"model": "tencent/hy3-preview:free", "messages": $HISTORY}')" | jq -cr '.choices.[0].message.content')"
    add
    ROLE=user
    CONTENT="$(lxc-attach shell-agent -- bash -c "$CONTENT" 2>&1)"
    add
done
)
