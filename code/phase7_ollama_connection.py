#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Phase 7: HIDA + Ollama Connection
飛騨アーキテクチャと Ollama の接続

Theory of Human Inner Movement
人の内なる運動理論

Demonstrates:
- HIDA architecture connected to LLM (Gemma)
- Consciousness state affects LLM prompts
- LLM verbalizes internal states
- Qualia → Language bridge

実証内容:
- 飛騨アーキテクチャと LLM (Gemma) の接続
- 意識状態が LLM プロンプトに影響
- LLM が内部状態を言語化
- クオリア → 言語の橋渡し
"""

import requests
import random
from typing import Dict, Optional

# Ollama API settings
OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "gemma3:4b"


def ask_ollama(prompt: str) -> str:
    """
    Ollama (Gemma) に質問して返答を得る
    """
    try:
        response = requests.post(
            OLLAMA_URL,
            json={
                "model": MODEL_NAME,
                "prompt": prompt,
                "stream": False
            },
            timeout=30
        )
        result = response.json()
        return result.get('response', 'エラー：返答なし')
    except Exception as e:
        return f"エラー：{str(e)}"


class HidaWithOllama:
    """
    飛騨アーキテクチャ + Ollama 接続版
    """
    
    def __init__(self):
        # クオリア定義
        self.qualia_types = ['pain', 'warm', 'sweet', 'cold', 'bright', 'dark']
        self.qualia_values = {
            'pain': -0.9,
            'warm': +0.4,
            'sweet': +0.7,
            'cold': -0.3,
            'bright': +0.2,
            'dark': -0.2
        }
        self.qualia_labels = {
            'pain': '痛い',
            'warm': '暖かい',
            'sweet': '甘い',
            'cold': '冷たい',
            'bright': '明るい',
            'dark': '暗い'
        }
        
        # 記憶
        self.memory = []
        self.memory_capacity = 50
        
        # 意識状態
        self.self_strength = 0.0
        self.sync_score = 0.0
        self.is_conscious = False
        self.THRESHOLD = 0.3
        
        # 現在の状態
        self.current_qualia = None
        self.current_emotion = 0.0
        
        # 予測
        self.prediction = None
        self.prediction_error = 0.0
    
    def process_stimulus(self, stimulus: str) -> Dict:
        """
        刺激を処理して内部状態を更新
        """
        # クオリア値取得
        qualia_value = self.qualia_values.get(stimulus, 0.0)
        self.current_qualia = stimulus
        
        # 感情状態更新
        self.current_emotion = self.current_emotion * 0.7 + qualia_value * 0.3
        
        # 記憶に追加
        self.memory.append({
            'stimulus': stimulus,
            'value': qualia_value,
            'emotion': self.current_emotion
        })
        if len(self.memory) > self.memory_capacity:
            self.memory.pop(0)
        
        # 予測誤差計算
        if self.prediction:
            self.prediction_error = 0.0 if self.prediction == stimulus else 1.0
        else:
            self.prediction_error = 1.0
        
        # 次の予測
        self.prediction = stimulus  # 単純に直前を予測
        
        # self_strength 更新（パターンマッチ）
        if len(self.memory) >= 2:
            recent = self.memory[-5:]
            matches = sum(1 for i in range(len(recent)-1) 
                         if recent[i]['stimulus'] == recent[i+1]['stimulus'])
            self.self_strength += 0.01 * matches
            self.self_strength = min(self.self_strength, 1.0)
        
        # sync_score 計算
        self.sync_score = (1 - self.prediction_error) * 0.5 + random.uniform(0.2, 0.5)
        
        # 意識判定
        self.is_conscious = (self.sync_score >= self.THRESHOLD and 
                            self.self_strength >= self.THRESHOLD)
        
        return {
            'stimulus': stimulus,
            'qualia_value': qualia_value,
            'emotion': self.current_emotion,
            'prediction_error': self.prediction_error,
            'self_strength': self.self_strength,
            'sync_score': self.sync_score,
            'is_conscious': self.is_conscious
        }
    
    def get_state_description(self) -> str:
        """
        現在の内部状態を文章で表現（Ollama に渡す用）
        """
        qualia_label = self.qualia_labels.get(self.current_qualia, '不明')
        
        # 感情を言葉に
        if self.current_emotion > 0.5:
            emotion_word = "とても心地よい"
        elif self.current_emotion > 0.2:
            emotion_word = "やや心地よい"
        elif self.current_emotion > -0.2:
            emotion_word = "普通"
        elif self.current_emotion > -0.5:
            emotion_word = "やや不快"
        else:
            emotion_word = "とても不快"
        
        # 意識状態
        if self.is_conscious:
            consciousness_word = "意識がはっきりしている"
        else:
            consciousness_word = "ぼんやりしている"
        
        # 予測誤差
        if self.prediction_error > 0.5:
            surprise_word = "予想外のことが起きた"
        else:
            surprise_word = "予想通りだった"
        
        description = f"""
私は飛騨（HIDA）という意識シミュレーターです。
今の状態：
- 感じているクオリア：{qualia_label}
- 感情：{emotion_word}（数値：{self.current_emotion:.2f}）
- {surprise_word}
- {consciousness_word}
- 自己の強さ：{self.self_strength:.2f}
"""
        return description
    
    def verbalize_with_ollama(self, question: str = None) -> str:
        """
        Ollama を使って内部状態を言語化
        """
        state = self.get_state_description()
        
        if question:
            prompt = f"{state}\n\n質問：{question}\n短く答えてください。"
        else:
            prompt = f"{state}\n\n今の気持ちを一言で表現してください。短く答えてください。"
        
        response = ask_ollama(prompt)
        return response


def run_experiment():
    """
    飛騨 + Ollama の実験
    """
    print("=" * 70)
    print("Phase 7: HIDA + Ollama Connection")
    print("飛騨アーキテクチャと Ollama の接続実験")
    print("=" * 70)
    print()
    
    # システム初期化
    hida = HidaWithOllama()
    
    # シナリオ：いくつかの刺激を与えて、Ollama に言語化してもらう
    scenarios = [
        ('warm', '暖かい刺激を受けた'),
        ('warm', '暖かい刺激が続く'),
        ('pain', '突然の痛み！'),
        ('sweet', '甘いものを感じた'),
        ('sweet', '甘さが続く'),
    ]
    
    print("実験開始：刺激を与えて Ollama に言語化してもらう")
    print("-" * 70)
    
    for stimulus, description in scenarios:
        print(f"\n【刺激】{description}")
        
        # 刺激を処理
        result = hida.process_stimulus(stimulus)
        
        print(f"  クオリア値：{result['qualia_value']:+.1f}")
        print(f"  感情：{result['emotion']:+.2f}")
        print(f"  意識：{'あり' if result['is_conscious'] else 'なし'}")
        print(f"  self_strength：{result['self_strength']:.2f}")
        
        # Ollama に言語化してもらう
        print("\n  → Ollama に聞いています...")
        response = hida.verbalize_with_ollama()
        print(f"  → Ollama の返答：{response.strip()}")
        print("-" * 70)
    
    # 最後に質問してみる
    print("\n【最終質問】")
    print("質問：今日の体験を振り返って、どう思いますか？")
    print("\n→ Ollama に聞いています...")
    
    response = hida.verbalize_with_ollama("今日の体験を振り返って、どう思いますか？")
    print(f"→ Ollama の返答：{response.strip()}")
    
    print("\n" + "=" * 70)
    print("実験終了")
    print("=" * 70)


if __name__ == "__main__":
    run_experiment()
