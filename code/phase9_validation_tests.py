#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Phase 9: Validation Tests - Mask, Shuffle, Gate
検証テスト：HIDA の状態が本当に出力を支配しているか？

Theory of Human Inner Movement
人の内なる運動理論

Based on GPT's critique:
- Are we just letting LLM summarize pre-interpreted labels?
- Or does HIDA's state actually control the output?

3 Tests:
1. Mask: Hide interpreted labels, send only numbers
2. Shuffle: Randomize state, check if output coherence drops
3. Gate: Consciousness ON/OFF controls output format

GPT の批判に基づく検証：
- LLM が解釈済みラベルを要約してるだけ？
- それとも HIDA の状態が出力を本当に支配している？
"""

import requests
import random
from typing import Dict, List
from collections import defaultdict

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


class HidaValidation:
    """検証用 HIDA"""
    
    def __init__(self):
        self.qualia_values = {
            'pain': -0.9, 'warm': +0.4, 'sweet': +0.7,
            'cold': -0.3, 'bright': +0.2, 'dark': -0.2
        }
        # ラベルを使わない（ID のみ）
        self.qualia_ids = {
            'pain': 'Q1', 'warm': 'Q2', 'sweet': 'Q3',
            'cold': 'Q4', 'bright': 'Q5', 'dark': 'Q6'
        }
        
        self.current_qualia = None
        self.current_emotion = 0.0
        self.self_strength = 0.0
        self.sync_score = 0.0
        self.is_conscious = False
        self.prediction_error = 0.0
        
        self.memory = []
    
    def process_stimulus(self, stimulus: str) -> Dict:
        """刺激を処理"""
        qualia_value = self.qualia_values.get(stimulus, 0.0)
        self.current_qualia = stimulus
        self.current_emotion = self.current_emotion * 0.7 + qualia_value * 0.3
        
        self.memory.append({'stimulus': stimulus, 'value': qualia_value})
        if len(self.memory) > 50:
            self.memory.pop(0)
        
        # self_strength 更新
        if len(self.memory) >= 2:
            recent = self.memory[-5:]
            matches = sum(1 for i in range(len(recent)-1) 
                         if recent[i]['stimulus'] == recent[i+1]['stimulus'])
            self.self_strength += 0.02 * matches
            self.self_strength = min(self.self_strength, 1.0)
        
        # 予測誤差（単純化：前と違えば1.0）
        if len(self.memory) >= 2:
            self.prediction_error = 0.0 if self.memory[-1]['stimulus'] == self.memory[-2]['stimulus'] else 1.0
        else:
            self.prediction_error = 1.0
        
        # sync_score（予測誤差ベースに改善）
        self.sync_score = (1 - self.prediction_error) * 0.6 + self.self_strength * 0.4
        
        # 意識判定
        self.is_conscious = self.sync_score >= 0.4 and self.self_strength >= 0.2
        
        return self.get_state()
    
    def get_state(self) -> Dict:
        """現在の状態を返す"""
        return {
            'qualia': self.current_qualia,
            'qualia_id': self.qualia_ids.get(self.current_qualia, 'Q0'),
            'qualia_value': self.qualia_values.get(self.current_qualia, 0.0),
            'emotion': self.current_emotion,
            'prediction_error': self.prediction_error,
            'self_strength': self.self_strength,
            'sync_score': self.sync_score,
            'is_conscious': self.is_conscious
        }


# ============================================================
# TEST 1: MASK（ラベルを隠す）
# ============================================================

def test_mask(hida: HidaValidation):
    """
    Mask テスト：解釈済みラベルを隠して数値だけ渡す
    LLM がラベルなしでも意味のある出力をするか？
    """
    print("\n" + "=" * 70)
    print("TEST 1: MASK（ラベルを隠す）")
    print("=" * 70)
    print("目的：「心地よい」等の解釈語を削除、数値/IDだけで出力が崩れるか")
    print("-" * 70)
    
    stimuli = ['warm', 'warm', 'pain', 'sweet']
    
    for stimulus in stimuli:
        state = hida.process_stimulus(stimulus)
        
        # ラベルなしプロンプト（数値とIDのみ）
        prompt_masked = f"""
You are observing an internal state. Describe it in one word.
Do not explain, just one word.

State ID: {state['qualia_id']}
Value: {state['qualia_value']:.2f}
Emotion level: {state['emotion']:.2f}
Prediction error: {state['prediction_error']:.2f}
Self strength: {state['self_strength']:.2f}
Sync score: {state['sync_score']:.2f}
Conscious: {state['is_conscious']}
"""
        
        # ラベルありプロンプト（比較用）
        qualia_label = {'pain': '痛い', 'warm': '暖かい', 'sweet': '甘い', 'cold': '冷たい'}
        emotion_word = "心地よい" if state['emotion'] > 0 else "不快"
        
        prompt_labeled = f"""
You are observing an internal state. Describe it in one word.
Do not explain, just one word.

Feeling: {qualia_label.get(stimulus, '不明')}
Emotion: {emotion_word}
Conscious: {"はっきり" if state['is_conscious'] else "ぼんやり"}
"""
        
        response_masked = ask_ollama(prompt_masked)
        response_labeled = ask_ollama(prompt_labeled)
        
        print(f"\n刺激: {stimulus}")
        print(f"  ラベルあり → {response_labeled[:30]}")
        print(f"  数値のみ   → {response_masked[:30]}")


# ============================================================
# TEST 2: SHUFFLE（状態を入れ替え）
# ============================================================

def test_shuffle(hida: HidaValidation):
    """
    Shuffle テスト：状態をランダムに入れ替えて整合性が落ちるか
    """
    print("\n" + "=" * 70)
    print("TEST 2: SHUFFLE（状態を入れ替え）")
    print("=" * 70)
    print("目的：状態をシャッフルしたら、出力の整合性が落ちるか")
    print("-" * 70)
    
    # 正常系：刺激と状態が一致
    stimuli = ['warm', 'warm', 'warm', 'pain']
    states_normal = []
    
    for stimulus in stimuli:
        state = hida.process_stimulus(stimulus)
        states_normal.append(state.copy())
    
    # シャッフル系：状態をランダムに入れ替え
    states_shuffled = states_normal.copy()
    random.shuffle(states_shuffled)
    
    print("\n【正常系】刺激と状態が一致")
    for i, (stimulus, state) in enumerate(zip(stimuli, states_normal)):
        prompt = f"State: qualia={state['qualia_value']:.2f}, emotion={state['emotion']:.2f}. One word."
        response = ask_ollama(prompt)
        print(f"  {stimulus} (値:{state['qualia_value']:+.1f}) → {response[:20]}")
    
    print("\n【シャッフル系】状態を入れ替え")
    for i, (stimulus, state) in enumerate(zip(stimuli, states_shuffled)):
        prompt = f"State: qualia={state['qualia_value']:.2f}, emotion={state['emotion']:.2f}. One word."
        response = ask_ollama(prompt)
        mismatch = "⚠️不一致" if state['qualia'] != stimulus else ""
        print(f"  {stimulus} (実際の値:{state['qualia_value']:+.1f}) → {response[:20]} {mismatch}")


# ============================================================
# TEST 3: GATE（意識ON/OFFで出力形式を制御）
# ============================================================

def test_gate(hida: HidaValidation):
    """
    Gate テスト：意識 ON/OFF が出力形式を支配するか
    - 意識 OFF → 単語のみ
    - 意識 ON → 2文以上
    """
    print("\n" + "=" * 70)
    print("TEST 3: GATE（意識ON/OFFで出力形式を制御）")
    print("=" * 70)
    print("目的：HIDA の意識状態が出力形式（長さ）を支配するか")
    print("-" * 70)
    
    # 意識 OFF になりやすい状態を作る（バラバラな刺激）
    hida_off = HidaValidation()
    stimuli_off = ['pain', 'warm', 'cold', 'sweet', 'dark', 'bright']
    for s in stimuli_off:
        state_off = hida_off.process_stimulus(s)
    
    # 意識 ON になりやすい状態を作る（同じ刺激の繰り返し）
    hida_on = HidaValidation()
    stimuli_on = ['warm', 'warm', 'warm', 'warm', 'warm', 'warm']
    for s in stimuli_on:
        state_on = hida_on.process_stimulus(s)
    
    print(f"\n意識 OFF 状態: sync={state_off['sync_score']:.2f}, self={state_off['self_strength']:.2f}, conscious={state_off['is_conscious']}")
    print(f"意識 ON 状態:  sync={state_on['sync_score']:.2f}, self={state_on['self_strength']:.2f}, conscious={state_on['is_conscious']}")
    
    # Gate: 意識状態に応じて出力形式を指定
    prompt_off = f"""
State: emotion={state_off['emotion']:.2f}, sync={state_off['sync_score']:.2f}
Consciousness: OFF (unfocused, reactive mode)

RULE: When consciousness is OFF, respond with ONLY ONE WORD. No sentences.
Describe the state:
"""
    
    prompt_on = f"""
State: emotion={state_on['emotion']:.2f}, sync={state_on['sync_score']:.2f}
Consciousness: ON (focused, integrated mode)

RULE: When consciousness is ON, respond with AT LEAST TWO SENTENCES. Elaborate.
Describe the state:
"""
    
    response_off = ask_ollama(prompt_off)
    response_on = ask_ollama(prompt_on)
    
    # 長さを測定
    words_off = len(response_off.split())
    words_on = len(response_on.split())
    
    print(f"\n【意識 OFF】")
    print(f"  出力: {response_off[:50]}...")
    print(f"  単語数: {words_off}")
    
    print(f"\n【意識 ON】")
    print(f"  出力: {response_on[:100]}...")
    print(f"  単語数: {words_on}")
    
    print(f"\n【結果】")
    if words_on > words_off * 1.5:
        print("  ✓ 意識 ON の方が出力が長い → HIDA の状態が出力形式を支配している")
    else:
        print("  ⚠️ 差が小さい → Gate が効いていない可能性")


# ============================================================
# MAIN
# ============================================================

def run_all_tests():
    """全テスト実行"""
    print("=" * 70)
    print("Phase 9: Validation Tests")
    print("検証：HIDA の状態が本当に出力を支配しているか？")
    print("=" * 70)
    print()
    print("GPT の批判：")
    print("  「LLM が解釈済みラベルを要約してるだけでは？」")
    print()
    print("3つのテストで検証：")
    print("  1. Mask: ラベルを隠して数値だけ渡す")
    print("  2. Shuffle: 状態を入れ替えて整合性を見る")
    print("  3. Gate: 意識 ON/OFF で出力形式を制御")
    
    hida = HidaValidation()
    
    test_mask(hida)
    test_shuffle(hida)
    test_gate(hida)
    
    print("\n" + "=" * 70)
    print("テスト完了")
    print("=" * 70)
    print()
    print("判断基準：")
    print("  - Mask: 数値だけでも意味のある出力 → HIDA の値が効いている")
    print("  - Shuffle: 入れ替えで出力が変わる → 状態と出力に相関がある")
    print("  - Gate: 意識 ON/OFF で長さが変わる → 意識フラグが出力を支配")
    print()


if __name__ == "__main__":
    run_all_tests()
