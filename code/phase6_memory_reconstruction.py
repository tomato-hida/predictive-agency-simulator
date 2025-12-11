#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Phase 6: Memory Reconstruction
記憶の再構成

Theory of Human Inner Movement
人の内なる運動理論

Based on: "The cognitive neuroscience of memory representations"
(Neuroscience & Biobehavioral Reviews, 2025)

Demonstrates:
- Memory is NOT fixed storage
- Memory is reconstructed each time it's recalled
- Current state influences reconstruction
- Reconstructed memory is re-stored (gradual change)

実証内容:
- 記憶は固定保存ではない
- 記憶は呼び出すたびに再構成される
- 現在の状態が再構成に影響
- 再構成された記憶が再保存される（徐々に変化）
"""

import random
from typing import Dict, List, Optional

class Memory:
    """Single memory unit with reconstruction capability"""
    
    def __init__(self, pattern: str, qualia_value: float, emotion: float):
        self.original_pattern = pattern      # 元のパターン
        self.current_pattern = pattern       # 現在のパターン（再構成で変わる）
        self.original_qualia = qualia_value  # 元のクオリア値
        self.current_qualia = qualia_value   # 現在のクオリア値
        self.original_emotion = emotion      # 元の感情値
        self.current_emotion = emotion       # 現在の感情値
        self.recall_count = 0                # 呼び出し回数
        self.reconstruction_history = []     # 再構成履歴
        
    def reconstruct(self, current_state: Dict) -> Dict:
        """
        Reconstruct memory based on current state
        現在の状態に基づいて記憶を再構成
        
        This is the key mechanism from the paper:
        記憶は「取り出す」のではなく「再構成する」
        """
        self.recall_count += 1
        
        # Integration weight: how much current state affects memory
        # 統合重み：現在の状態がどれだけ記憶に影響するか
        integration_weight = 0.1  # 10% influence each recall
        
        # Reconstruct qualia value
        # クオリア値の再構成
        old_qualia = self.current_qualia
        self.current_qualia = (
            self.current_qualia * (1 - integration_weight) +
            current_state['qualia'] * integration_weight
        )
        
        # Reconstruct emotion value
        # 感情値の再構成
        old_emotion = self.current_emotion
        self.current_emotion = (
            self.current_emotion * (1 - integration_weight) +
            current_state['emotion'] * integration_weight
        )
        
        # Record reconstruction
        # 再構成を記録
        self.reconstruction_history.append({
            'recall_number': self.recall_count,
            'current_state': current_state.copy(),
            'qualia_change': self.current_qualia - old_qualia,
            'emotion_change': self.current_emotion - old_emotion
        })
        
        return {
            'original_qualia': self.original_qualia,
            'reconstructed_qualia': self.current_qualia,
            'original_emotion': self.original_emotion,
            'reconstructed_emotion': self.current_emotion,
            'drift_qualia': self.current_qualia - self.original_qualia,
            'drift_emotion': self.current_emotion - self.original_emotion,
            'recall_count': self.recall_count
        }


class MemoryReconstructionSystem:
    """System demonstrating memory reconstruction"""
    
    def __init__(self):
        self.qualia_types = ['pain', 'warm', 'sweet', 'red', 'blue', 'green']
        
        # Qualia values
        self.qualia_values = {
            'pain': -0.9, 'warm': +0.3, 'sweet': +0.7,
            'red': +0.3, 'blue': +0.2, 'green': +0.4
        }
        
        # Long-term memory storage
        # 長期記憶ストレージ
        self.memories: Dict[str, Memory] = {}
        
        # Current emotional state (fluctuates)
        # 現在の感情状態（変動する）
        self.current_emotion = 0.0
        
        # Self strength
        self.self_strength = 0.0
        self.THRESHOLD = 0.3
        
    def create_memory(self, pattern: str, emotion: float) -> Memory:
        """Create a new memory"""
        qualia_value = self.qualia_values.get(pattern, 0.0)
        memory = Memory(pattern, qualia_value, emotion)
        memory_id = f"{pattern}_{len(self.memories)}"
        self.memories[memory_id] = memory
        return memory
    
    def recall_memory(self, memory_id: str) -> Optional[Dict]:
        """
        Recall and reconstruct a memory
        記憶を呼び出して再構成
        
        Key insight from paper:
        「記憶は写真やビデオのように保存されてない」
        「思い出すたびに今の状況に合わせて再構成される」
        """
        if memory_id not in self.memories:
            return None
            
        memory = self.memories[memory_id]
        
        # Current state affects reconstruction
        # 現在の状態が再構成に影響
        current_state = {
            'qualia': random.uniform(-0.5, 0.5),  # Current sensory state
            'emotion': self.current_emotion,       # Current emotional state
            'self_strength': self.self_strength
        }
        
        # Reconstruct memory (this is where the magic happens)
        # 記憶を再構成（ここが核心）
        result = memory.reconstruct(current_state)
        
        return result
    
    def update_emotional_state(self, stimulus: str):
        """Update current emotional state based on stimulus"""
        qualia_value = self.qualia_values.get(stimulus, 0.0)
        # Emotional state drifts based on recent stimuli
        self.current_emotion = self.current_emotion * 0.7 + qualia_value * 0.3
        
    def run_experiment(self, steps: int = 100):
        """
        Demonstrate memory reconstruction over time
        時間経過による記憶の再構成を実証
        """
        print("=" * 70)
        print("Phase 6: Memory Reconstruction Experiment")
        print("記憶再構成の実験")
        print("=" * 70)
        print()
        print("Based on: 'The cognitive neuroscience of memory representations'")
        print("(Neuroscience & Biobehavioral Reviews, October 2025)")
        print()
        print("Key insight: Memory is reconstructed each time it's recalled,")
        print("influenced by current emotional state.")
        print("記憶は呼び出すたびに、現在の感情状態の影響を受けて再構成される")
        print("=" * 70)
        
        # Create initial memories with different emotional contexts
        # 異なる感情コンテキストで初期記憶を作成
        print("\n1. CREATING INITIAL MEMORIES")
        print("-" * 50)
        
        # Happy memory of warmth
        self.current_emotion = +0.8  # Happy state
        happy_memory = self.create_memory('warm', self.current_emotion)
        print(f"Memory 'warm_0' created:")
        print(f"  Original qualia: {happy_memory.original_qualia:+.2f}")
        print(f"  Original emotion: {happy_memory.original_emotion:+.2f} (happy)")
        
        # Painful memory
        self.current_emotion = -0.7  # Sad state
        sad_memory = self.create_memory('pain', self.current_emotion)
        print(f"\nMemory 'pain_1' created:")
        print(f"  Original qualia: {sad_memory.original_qualia:+.2f}")
        print(f"  Original emotion: {sad_memory.original_emotion:+.2f} (sad)")
        
        # Now simulate life: emotional states change, memories get recalled
        # 人生をシミュレート：感情状態が変わり、記憶が呼び出される
        print("\n" + "=" * 70)
        print("2. SIMULATING LIFE: RECALLING MEMORIES IN DIFFERENT STATES")
        print("-" * 50)
        
        # Scenario: Recall happy memory while in different emotional states
        print("\n--- Recalling 'warm_0' (originally happy memory) ---")
        
        emotional_states = [
            (+0.8, "very happy / とても幸せ"),
            (+0.3, "slightly happy / やや幸せ"),
            (-0.2, "slightly sad / やや悲しい"),
            (-0.6, "sad / 悲しい"),
            (-0.8, "very sad / とても悲しい"),
        ]
        
        for target_emotion, label in emotional_states:
            # Set emotional state
            self.current_emotion = target_emotion
            
            # Recall memory (this reconstructs it)
            result = self.recall_memory('warm_0')
            
            print(f"\nRecall #{result['recall_count']} in state: {label}")
            print(f"  Current emotion: {target_emotion:+.2f}")
            print(f"  Reconstructed qualia: {result['reconstructed_qualia']:+.3f} "
                  f"(drift: {result['drift_qualia']:+.3f})")
            print(f"  Reconstructed emotion: {result['reconstructed_emotion']:+.3f} "
                  f"(drift: {result['drift_emotion']:+.3f})")
        
        # Show total drift
        print("\n" + "=" * 70)
        print("3. MEMORY DRIFT ANALYSIS")
        print("-" * 50)
        
        warm_memory = self.memories['warm_0']
        print(f"\nMemory 'warm_0' after {warm_memory.recall_count} recalls:")
        print(f"  Original emotion: {warm_memory.original_emotion:+.3f}")
        print(f"  Current emotion:  {warm_memory.current_emotion:+.3f}")
        print(f"  Total drift:      {warm_memory.current_emotion - warm_memory.original_emotion:+.3f}")
        print()
        print("The happy memory has become less happy due to being recalled")
        print("while in sad emotional states!")
        print("悲しい状態で呼び出されたため、幸せな記憶が幸せでなくなった！")
        
        # Key findings
        print("\n" + "=" * 70)
        print("KEY FINDINGS / 重要な発見")
        print("=" * 70)
        print()
        print("1. Memory is NOT fixed storage")
        print("   記憶は固定保存ではない")
        print()
        print("2. Each recall RECONSTRUCTS the memory")
        print("   呼び出すたびに記憶が再構成される")
        print()
        print("3. Current emotional state influences reconstruction")
        print("   現在の感情状態が再構成に影響")
        print()
        print("4. Reconstructed memory is re-stored (gradual change)")
        print("   再構成された記憶が再保存される（徐々に変化）")
        print()
        print("5. This explains:")
        print("   これが説明できること:")
        print("   - Why memories feel different depending on mood")
        print("     なぜ気分で記憶の印象が変わるか")
        print("   - Why memories change over time")
        print("     なぜ時間が経つと記憶が変わるか")
        print("   - Why trauma can be reprocessed")
        print("     なぜトラウマが再処理できるか")
        print("=" * 70)
        
        return {
            'memories': self.memories,
            'warm_drift': warm_memory.current_emotion - warm_memory.original_emotion
        }


def demonstrate_trauma_reprocessing():
    """
    Demonstrate how trauma can be reprocessed through positive recalls
    ポジティブな呼び出しによるトラウマの再処理を実証
    """
    print("\n" + "=" * 70)
    print("BONUS: Trauma Reprocessing Simulation")
    print("トラウマ再処理のシミュレーション")
    print("=" * 70)
    
    system = MemoryReconstructionSystem()
    
    # Create traumatic memory
    system.current_emotion = -0.9  # Traumatic state
    trauma = system.create_memory('pain', system.current_emotion)
    
    print(f"\nTraumatic memory created:")
    print(f"  Emotion: {trauma.original_emotion:+.2f} (traumatic)")
    
    # Therapy: recall in safe, positive states
    print("\n--- Therapy: Recalling in safe, positive states ---")
    print("--- セラピー：安全でポジティブな状態で呼び出す ---")
    
    for i in range(10):
        # Therapist creates safe, positive environment
        system.current_emotion = +0.5 + random.uniform(0, 0.3)
        result = system.recall_memory('pain_0')
        
        if (i + 1) % 2 == 0:
            print(f"Session {i+1}: emotion drift = {result['drift_emotion']:+.3f}")
    
    print(f"\nAfter therapy:")
    print(f"  Original emotion: {trauma.original_emotion:+.3f}")
    print(f"  Current emotion:  {trauma.current_emotion:+.3f}")
    print(f"  Improvement:      {trauma.current_emotion - trauma.original_emotion:+.3f}")
    print()
    print("The traumatic memory has been 'softened' through repeated")
    print("recall in positive emotional states.")
    print("ポジティブな状態での繰り返し呼び出しで")
    print("トラウマ記憶が「軟化」した")


if __name__ == "__main__":
    # Main experiment
    system = MemoryReconstructionSystem()
    system.run_experiment()
    
    # Bonus: trauma reprocessing
    demonstrate_trauma_reprocessing()
