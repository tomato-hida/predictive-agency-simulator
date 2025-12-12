#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Phase 8: Learning Qualia - HIDA that learns words for feelings
クオリアを学習する飛騨

Theory of Human Inner Movement
人の内なる運動理論

Demonstrates:
- HIDA learns word-qualia associations from Ollama (like baby learns from parent)
- After enough learning, HIDA can verbalize without asking Ollama
- Qualia = Pattern + Value + Word (learned)
- Language acquisition through experience

実証内容:
- 飛騨が Ollama から言葉とクオリアの関連を学ぶ（赤ちゃんが親から学ぶように）
- 十分学習すると、Ollama に聞かなくても言語化できる
- クオリア = パターン + 値 + 言葉（学習）
- 経験を通じた言語獲得
"""

import requests
import random
from typing import Dict, Optional, List
from collections import defaultdict

# Ollama API settings
OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "gemma3:4b"


def ask_ollama(prompt: str) -> str:
    """Ollama (Gemma) に質問して返答を得る"""
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
        return result.get('response', '').strip()
    except Exception as e:
        return f"エラー：{str(e)}"


class QualiaMemory:
    """
    クオリアと言葉の関連を記憶するシステム
    """
    def __init__(self):
        # {状態キー: {言葉: 出現回数}}
        self.word_associations = defaultdict(lambda: defaultdict(int))
        # 学習閾値：この回数以上なら自分で言える
        self.confidence_threshold = 3
    
    def make_state_key(self, qualia: str, emotion_level: str) -> str:
        """状態をキーに変換"""
        return f"{qualia}_{emotion_level}"
    
    def learn(self, qualia: str, emotion_level: str, word: str):
        """言葉を学習（記憶に追加）"""
        key = self.make_state_key(qualia, emotion_level)
        self.word_associations[key][word] += 1
    
    def can_speak_alone(self, qualia: str, emotion_level: str) -> bool:
        """自分で言えるか（十分学習したか）"""
        key = self.make_state_key(qualia, emotion_level)
        if key not in self.word_associations:
            return False
        # 最も多い言葉の出現回数
        if not self.word_associations[key]:
            return False
        max_count = max(self.word_associations[key].values())
        return max_count >= self.confidence_threshold
    
    def get_learned_word(self, qualia: str, emotion_level: str) -> Optional[str]:
        """学習した言葉を取得"""
        key = self.make_state_key(qualia, emotion_level)
        if key not in self.word_associations:
            return None
        if not self.word_associations[key]:
            return None
        # 最も多い言葉を返す
        return max(self.word_associations[key], 
                   key=self.word_associations[key].get)
    
    def get_stats(self) -> Dict:
        """学習統計を取得"""
        total_associations = len(self.word_associations)
        speakable = sum(1 for key in self.word_associations 
                       if max(self.word_associations[key].values(), default=0) 
                       >= self.confidence_threshold)
        return {
            'total_learned': total_associations,
            'can_speak_alone': speakable,
            'details': dict(self.word_associations)
        }


class HidaLearning:
    """
    学習する飛騨アーキテクチャ
    """
    
    def __init__(self):
        # クオリア定義
        self.qualia_types = ['pain', 'warm', 'sweet', 'cold', 'bright', 'dark']
        self.qualia_values = {
            'pain': -0.9, 'warm': +0.4, 'sweet': +0.7,
            'cold': -0.3, 'bright': +0.2, 'dark': -0.2
        }
        self.qualia_labels = {
            'pain': '痛い', 'warm': '暖かい', 'sweet': '甘い',
            'cold': '冷たい', 'bright': '明るい', 'dark': '暗い'
        }
        
        # クオリア記憶システム（言葉の学習）
        self.qualia_memory = QualiaMemory()
        
        # 経験記憶
        self.experience_memory = []
        self.memory_capacity = 100
        
        # 意識状態
        self.self_strength = 0.0
        self.sync_score = 0.0
        self.is_conscious = False
        self.THRESHOLD = 0.3
        
        # 現在の状態
        self.current_qualia = None
        self.current_emotion = 0.0
        
        # 統計
        self.asked_ollama_count = 0
        self.spoke_alone_count = 0
    
    def get_emotion_level(self, emotion: float) -> str:
        """感情値をレベルに変換"""
        if emotion > 0.5:
            return "very_positive"
        elif emotion > 0.2:
            return "positive"
        elif emotion > -0.2:
            return "neutral"
        elif emotion > -0.5:
            return "negative"
        else:
            return "very_negative"
    
    def process_stimulus(self, stimulus: str) -> Dict:
        """刺激を処理"""
        qualia_value = self.qualia_values.get(stimulus, 0.0)
        self.current_qualia = stimulus
        
        # 感情更新
        self.current_emotion = self.current_emotion * 0.7 + qualia_value * 0.3
        
        # 経験記憶に追加
        self.experience_memory.append({
            'stimulus': stimulus,
            'value': qualia_value,
            'emotion': self.current_emotion
        })
        if len(self.experience_memory) > self.memory_capacity:
            self.experience_memory.pop(0)
        
        # self_strength 更新
        if len(self.experience_memory) >= 2:
            recent = self.experience_memory[-5:]
            matches = sum(1 for i in range(len(recent)-1) 
                         if recent[i]['stimulus'] == recent[i+1]['stimulus'])
            self.self_strength += 0.02 * matches
            self.self_strength = min(self.self_strength, 1.0)
        
        # sync_score
        self.sync_score = 0.3 + random.uniform(0.1, 0.4)
        
        # 意識判定
        self.is_conscious = (self.sync_score >= self.THRESHOLD and 
                            self.self_strength >= self.THRESHOLD)
        
        return {
            'stimulus': stimulus,
            'qualia_value': qualia_value,
            'emotion': self.current_emotion,
            'emotion_level': self.get_emotion_level(self.current_emotion),
            'self_strength': self.self_strength,
            'is_conscious': self.is_conscious
        }
    
    def verbalize(self) -> Dict:
        """
        内部状態を言語化
        - 学習済みなら自分で言う
        - 未学習なら Ollama に聞いて学習
        """
        emotion_level = self.get_emotion_level(self.current_emotion)
        qualia_label = self.qualia_labels.get(self.current_qualia, '不明')
        
        # 自分で言えるか確認
        if self.qualia_memory.can_speak_alone(self.current_qualia, emotion_level):
            # 自分で言える！
            word = self.qualia_memory.get_learned_word(self.current_qualia, emotion_level)
            self.spoke_alone_count += 1
            return {
                'word': word,
                'source': 'self',  # 自分で言った
                'message': f"（自分で言えた）{word}"
            }
        else:
            # Ollama に聞く
            prompt = f"""
私は今「{qualia_label}」という感覚を感じていて、
気分は「{emotion_level}」です。
この状態を一言（単語か短いフレーズ）で表現してください。
表現だけを答えてください。
"""
            word = ask_ollama(prompt)
            # 短くする（最初の単語だけ）
            word = word.split('\n')[0].split('。')[0].strip()
            if len(word) > 20:
                word = word[:20]
            
            # 学習！
            self.qualia_memory.learn(self.current_qualia, emotion_level, word)
            self.asked_ollama_count += 1
            
            return {
                'word': word,
                'source': 'ollama',  # Ollama に教えてもらった
                'message': f"（Ollamaに聞いた）{word}"
            }
    
    def get_learning_stats(self) -> Dict:
        """学習統計"""
        memory_stats = self.qualia_memory.get_stats()
        return {
            'asked_ollama': self.asked_ollama_count,
            'spoke_alone': self.spoke_alone_count,
            'independence_rate': (self.spoke_alone_count / 
                                  max(1, self.asked_ollama_count + self.spoke_alone_count) * 100),
            'memory': memory_stats
        }


def run_experiment():
    """学習実験"""
    print("=" * 70)
    print("Phase 8: Learning Qualia - クオリアを学習する飛騨")
    print("=" * 70)
    print()
    print("実験：飛騨が Ollama から言葉を学び、やがて自分で言えるようになるか？")
    print("（赤ちゃんが親から言葉を学ぶように）")
    print()
    print("=" * 70)
    
    hida = HidaLearning()
    
    # たくさんの刺激を与える（学習フェーズ）
    stimuli_sequence = []
    for _ in range(5):  # 5ラウンド
        stimuli_sequence.extend(['warm', 'warm', 'pain', 'sweet', 'sweet', 'cold'])
    
    print(f"\n【学習フェーズ】{len(stimuli_sequence)} 回の刺激")
    print("-" * 70)
    
    for i, stimulus in enumerate(stimuli_sequence):
        result = hida.process_stimulus(stimulus)
        verb = hida.verbalize()
        
        # 10回ごとに表示
        if (i + 1) % 6 == 0:
            print(f"  {i+1}回目: {hida.qualia_labels[stimulus]} → {verb['message']}")
    
    print("-" * 70)
    
    # 統計
    stats = hida.get_learning_stats()
    print(f"\n【学習結果】")
    print(f"  Ollama に聞いた回数: {stats['asked_ollama']}")
    print(f"  自分で言えた回数: {stats['spoke_alone']}")
    print(f"  自立率: {stats['independence_rate']:.1f}%")
    
    print(f"\n【学習した言葉】")
    for key, words in stats['memory']['details'].items():
        print(f"  {key}: {dict(words)}")
    
    # テストフェーズ
    print("\n" + "=" * 70)
    print("【テストフェーズ】学習後、自分で言えるか？")
    print("-" * 70)
    
    test_stimuli = ['warm', 'pain', 'sweet', 'cold', 'warm', 'sweet']
    
    for stimulus in test_stimuli:
        result = hida.process_stimulus(stimulus)
        verb = hida.verbalize()
        
        qualia_label = hida.qualia_labels[stimulus]
        source_mark = "★自力" if verb['source'] == 'self' else "→Ollama"
        print(f"  {qualia_label} ({result['emotion_level']}) : {verb['word']} [{source_mark}]")
    
    # 最終統計
    final_stats = hida.get_learning_stats()
    print("\n" + "=" * 70)
    print("【最終結果】")
    print(f"  総発話: {final_stats['asked_ollama'] + final_stats['spoke_alone']} 回")
    print(f"  Ollama 依存: {final_stats['asked_ollama']} 回")
    print(f"  自立発話: {final_stats['spoke_alone']} 回")
    print(f"  自立率: {final_stats['independence_rate']:.1f}%")
    print("=" * 70)
    
    if final_stats['independence_rate'] > 50:
        print("\n🎉 飛騨は言葉を学習し、自分で言えるようになった！")
        print("   = 言語獲得の再現")
    else:
        print("\n📚 まだ学習中... もっと経験が必要")
    
    print()


if __name__ == "__main__":
    run_experiment()
