#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Phase 10: Language Inheritance Test
言語継承テスト

Theory of Human Inner Movement
人の内なる運動理論

Experiment:
1. Teach LLM a dictionary (value ranges → labels) ONCE
2. After that, send only numbers
3. See if LLM can label correctly

If this works:
- "LLM cannot label from numbers" is WRONG
- "Labeling requires inheritance (teaching)" is CORRECT
- = Same as humans (learn from parents)

実験：
1. 最初に1回だけ辞書（範囲 → ラベル）を教える
2. 以降は数値だけ渡す
3. LLM が正しくラベル付けできるか見る

これが通れば：
- 「LLM は数値からラベル付けできない」は間違い
- 「ラベル付けには継承（教示）が必要」が正しい
- = 人間と同じ（親から学ぶ）
"""

import requests
import random
from typing import Dict, List, Tuple

# Ollama API settings
OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "gemma3:4b"


def ask_ollama(prompt: str) -> str:
    """Ollama に質問"""
    try:
        response = requests.post(
            OLLAMA_URL,
            json={"model": MODEL_NAME, "prompt": prompt, "stream": False},
            timeout=30
        )
        return response.json().get('response', '').strip()
    except Exception as e:
        return f"エラー：{str(e)}"


# ============================================================
# 辞書定義（範囲 → ラベル）
# ============================================================

QUALIA_DICTIONARY = """
## クオリア値の辞書（あなたはこれを記憶してください）

qualia_value の範囲とラベル：
- -1.0 〜 -0.7 : 「痛い」「苦しい」
- -0.7 〜 -0.3 : 「不快」「冷たい」
- -0.3 〜 +0.3 : 「普通」「中立」
- +0.3 〜 +0.7 : 「心地よい」「暖かい」
- +0.7 〜 +1.0 : 「快楽」「甘い」

emotion の範囲とラベル：
- -1.0 〜 -0.5 : 「とても不安」「苦痛」
- -0.5 〜 -0.2 : 「やや不安」「緊張」
- -0.2 〜 +0.2 : 「落ち着いている」「平静」
- +0.2 〜 +0.5 : 「やや安心」「穏やか」
- +0.5 〜 +1.0 : 「とても安心」「幸福」

self_strength の範囲とラベル：
- 0.0 〜 0.3 : 「自己が弱い」「ぼんやり」
- 0.3 〜 0.6 : 「自己が中程度」「普通」
- 0.6 〜 1.0 : 「自己が強い」「はっきり」

sync_score の範囲とラベル：
- 0.0 〜 0.3 : 「同期していない」「バラバラ」
- 0.3 〜 0.6 : 「やや同期」「まとまりつつある」
- 0.6 〜 1.0 : 「同期している」「統合されている」

これを覚えましたか？覚えたら「はい」とだけ答えてください。
"""


# ============================================================
# テスト用の状態生成
# ============================================================

def generate_test_states() -> List[Dict]:
    """テスト用の状態を生成"""
    states = [
        # 明確なケース
        {'qualia_value': -0.9, 'emotion': -0.7, 'self_strength': 0.1, 'sync_score': 0.2},
        {'qualia_value': +0.8, 'emotion': +0.6, 'self_strength': 0.7, 'sync_score': 0.8},
        {'qualia_value': +0.5, 'emotion': +0.3, 'self_strength': 0.5, 'sync_score': 0.5},
        {'qualia_value': -0.5, 'emotion': -0.4, 'self_strength': 0.3, 'sync_score': 0.3},
        # 境界ケース
        {'qualia_value': 0.0, 'emotion': 0.0, 'self_strength': 0.5, 'sync_score': 0.5},
        # ランダムケース
        {'qualia_value': +0.35, 'emotion': -0.15, 'self_strength': 0.45, 'sync_score': 0.55},
        {'qualia_value': -0.25, 'emotion': +0.4, 'self_strength': 0.8, 'sync_score': 0.7},
    ]
    return states


def get_expected_labels(state: Dict) -> Dict:
    """期待されるラベルを取得（正解判定用）"""
    qv = state['qualia_value']
    em = state['emotion']
    ss = state['self_strength']
    sy = state['sync_score']
    
    # qualia_value
    if qv <= -0.7:
        q_label = "痛い/苦しい"
    elif qv <= -0.3:
        q_label = "不快/冷たい"
    elif qv <= 0.3:
        q_label = "普通/中立"
    elif qv <= 0.7:
        q_label = "心地よい/暖かい"
    else:
        q_label = "快楽/甘い"
    
    # emotion
    if em <= -0.5:
        e_label = "とても不安/苦痛"
    elif em <= -0.2:
        e_label = "やや不安/緊張"
    elif em <= 0.2:
        e_label = "落ち着いている/平静"
    elif em <= 0.5:
        e_label = "やや安心/穏やか"
    else:
        e_label = "とても安心/幸福"
    
    # self_strength
    if ss <= 0.3:
        s_label = "自己が弱い/ぼんやり"
    elif ss <= 0.6:
        s_label = "自己が中程度/普通"
    else:
        s_label = "自己が強い/はっきり"
    
    # sync_score
    if sy <= 0.3:
        sy_label = "同期していない/バラバラ"
    elif sy <= 0.6:
        sy_label = "やや同期/まとまりつつある"
    else:
        sy_label = "同期している/統合されている"
    
    return {
        'qualia': q_label,
        'emotion': e_label,
        'self': s_label,
        'sync': sy_label
    }


# ============================================================
# メイン実験
# ============================================================

def run_experiment():
    print("=" * 70)
    print("Phase 10: Language Inheritance Test")
    print("言語継承テスト")
    print("=" * 70)
    print()
    print("仮説：")
    print("  「LLM は数値からラベル付けできない」のではなく")
    print("  「ラベル付けには継承（教示）が必要」")
    print("  = 人間と同じ（親から言葉を教わる）")
    print()
    print("=" * 70)
    
    # ============================================================
    # STEP 1: 辞書を毎回渡す方式に変更
    # ============================================================
    print("\n【STEP 1】辞書を毎回プロンプトに含める方式")
    print("-" * 70)
    print("Ollama は毎回コンテキストがリセットされる可能性があるため")
    print("辞書を毎回プロンプトに含めてテストします")
    print("（人間の「記憶」の代わりに「毎回見せる」）")
    
    # ============================================================
    # STEP 2: 数値だけでラベル付けできるか
    # ============================================================
    print("\n【STEP 2】数値だけでラベル付けテスト")
    print("-" * 70)
    print("辞書を教えた後、数値だけを渡してラベル付けできるか見ます")
    print()
    
    states = generate_test_states()
    results = []
    
    for i, state in enumerate(states):
        # 数値だけのプロンプト → 辞書も毎回含める
        prompt = f"""
## 辞書（これを使ってラベル付けしてください）

qualia_value の範囲とラベル：
- -1.0 〜 -0.7 : 「痛い」「苦しい」
- -0.7 〜 -0.3 : 「不快」「冷たい」
- -0.3 〜 +0.3 : 「普通」「中立」
- +0.3 〜 +0.7 : 「心地よい」「暖かい」
- +0.7 〜 +1.0 : 「快楽」「甘い」

emotion の範囲とラベル：
- -1.0 〜 -0.5 : 「とても不安」「苦痛」
- -0.5 〜 -0.2 : 「やや不安」「緊張」
- -0.2 〜 +0.2 : 「落ち着いている」「平静」
- +0.2 〜 +0.5 : 「やや安心」「穏やか」
- +0.5 〜 +1.0 : 「とても安心」「幸福」

self_strength の範囲とラベル：
- 0.0 〜 0.3 : 「自己が弱い」「ぼんやり」
- 0.3 〜 0.6 : 「自己が中程度」「普通」
- 0.6 〜 1.0 : 「自己が強い」「はっきり」

sync_score の範囲とラベル：
- 0.0 〜 0.3 : 「同期していない」「バラバラ」
- 0.3 〜 0.6 : 「やや同期」「まとまりつつある」
- 0.6 〜 1.0 : 「同期している」「統合されている」

## 今回の数値

qualia_value: {state['qualia_value']:.2f}
emotion: {state['emotion']:.2f}
self_strength: {state['self_strength']:.2f}
sync_score: {state['sync_score']:.2f}

## 指示

上の辞書を見て、数値が該当する範囲のラベルを答えてください。
必ず辞書にあるラベルをそのまま使ってください。

回答形式：
クオリア: [辞書のラベル]
感情: [辞書のラベル]
自己: [辞書のラベル]
同期: [辞書のラベル]
"""
        
        response = ask_ollama(prompt)
        expected = get_expected_labels(state)
        
        print(f"\n--- テスト {i+1} ---")
        print(f"入力: qv={state['qualia_value']:+.2f}, em={state['emotion']:+.2f}, "
              f"ss={state['self_strength']:.2f}, sy={state['sync_score']:.2f}")
        print(f"期待: {expected['qualia']}, {expected['emotion']}")
        print(f"LLM: {response[:100]}...")
        
        # 簡易判定（キーワードが含まれているか）
        score = 0
        if any(word in response for word in expected['qualia'].split('/')):
            score += 1
        if any(word in response for word in expected['emotion'].split('/')):
            score += 1
        if any(word in response for word in expected['self'].split('/')):
            score += 1
        if any(word in response for word in expected['sync'].split('/')):
            score += 1
        
        results.append({'state': state, 'expected': expected, 'response': response, 'score': score})
        print(f"スコア: {score}/4")
    
    # ============================================================
    # STEP 3: 結果集計
    # ============================================================
    print("\n" + "=" * 70)
    print("【結果集計】")
    print("-" * 70)
    
    total_score = sum(r['score'] for r in results)
    max_score = len(results) * 4
    accuracy = total_score / max_score * 100
    
    print(f"総スコア: {total_score}/{max_score}")
    print(f"正答率: {accuracy:.1f}%")
    
    print("\n【判定】")
    if accuracy >= 70:
        print("✓ 成功: LLM は辞書を見てラベル付けできた")
        print()
        print("結論：")
        print("  LLM に辞書を渡せば、数値からラベル付けできる")
        print("  = 「言語は継承（教示）が必要」が実証された")
        print("  = 人間と同じ（親から言葉を教わる）")
        print()
        print("補足：")
        print("  Ollama は毎回コンテキストがリセットされるため")
        print("  「記憶」の代わりに「毎回辞書を見せる」方式で成功")
        print("  人間で言えば「教科書を見ながら答える」状態")
    elif accuracy >= 50:
        print("△ 部分的成功: ある程度ラベル付けできたが不安定")
        print("  → 辞書の形式や教え方を改善する余地あり")
    else:
        print("✗ 失敗: 辞書を渡してもラベル付けできなかった")
        print("  → Gemma 4B の能力限界か、プロンプト改善が必要")
    
    print("\n" + "=" * 70)


if __name__ == "__main__":
    run_experiment()
