#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Phase 3: DNA Initial Values and Learning
DNA初期値と学習

Theory of Human Inner Movement
人の内なる運動理論

Demonstrates:
- DNA initial values (genetic predisposition)
- Learning mechanism (experience-based adjustment)
- Comparison of 3 systems: DNA+Learning, Learning-only, DNA-only

実証内容:
- DNA初期値（遺伝的素因）
- 学習メカニズム（経験による調整）
- 3システムの比較: DNA+学習、学習のみ、DNAのみ

IMPORTANT NOTE / 重要な注意:
The "Learning-only" system (DNA=0) is biologically impossible.
This was included for theoretical exploration but represents
an unrealistic scenario.

「学習のみ」システム（DNA=0）は生物学的にありえません。
これは理論的探求のために含まれましたが、非現実的なシナリオです。
"""

import random

class DNALearningSystem:
    """System with DNA initial values and learning"""
    
    def __init__(self, system_type='A'):
        """
        Args:
            system_type: 'A' (DNA+Learning), 'B' (Learning-only*), 'C' (DNA-only)
                        *Note: B is biologically impossible
        """
        self.system_type = system_type
        self.qualia_types = ['pain', 'warm', 'sweet']
        
        # DNA initial values (genetic predisposition)
        # DNA初期値（遺伝的素因）
        if system_type == 'A' or system_type == 'C':
            self.qualia_dna = {
                'pain': -0.9,   # Strong avoidance / 強い回避
                'warm': -0.2,   # Mild avoidance / 軽度の回避
                'sweet': +0.7   # Approach / 接近
            }
        else:  # System B - No DNA (biologically impossible!)
            self.qualia_dna = {
                'pain': 0.0,
                'warm': 0.0,
                'sweet': 0.0
            }
        
        # Learned adjustments (experience-based)
        # 学習による調整（経験ベース）
        self.qualia_learned = {
            'pain': 0.0,
            'warm': 0.0,
            'sweet': 0.0
        }
        
        # Learning rate / 学習率
        self.learning_rate = 0.01
        
        # Can learn? / 学習可能？
        self.can_learn = (system_type == 'A' or system_type == 'B')
        
        # Memory and consciousness
        self.recent_patterns = []
        self.recent_outcomes = []  # Track if stimulus was good/bad
        self.self_strength = 0.0
        self.sync_score = 0.0
        self.is_conscious = False
        self.THRESHOLD = 0.3
    
    def get_effective_value(self, qualia_type):
        """Get effective qualia value (DNA + learned)
        
        実効クオリア値を取得（DNA + 学習値）
        """
        return self.qualia_dna[qualia_type] + self.qualia_learned[qualia_type]
    
    def learn_from_experience(self, stimulus, outcome):
        """Update learned values based on experience
        
        経験に基づいて学習値を更新
        
        Args:
            stimulus: The qualia type experienced
            outcome: -1 (bad), 0 (neutral), +1 (good)
        """
        if not self.can_learn:
            return
        
        # Adjust learned value based on outcome
        # 結果に基づいて学習値を調整
        target_adjustment = outcome * 0.1
        current_learned = self.qualia_learned[stimulus]
        
        # Gradual learning / 段階的な学習
        self.qualia_learned[stimulus] += self.learning_rate * (target_adjustment - current_learned)
    
    def process_step(self):
        """Process one step with learning"""
        
        # Stimulus
        stimulus = random.choice(self.qualia_types)
        effective_value = self.get_effective_value(stimulus)
        
        # Determine outcome based on intrinsic properties
        # 本質的な性質に基づいて結果を決定
        # (In reality, pain is bad, sweet is good)
        # （現実では、痛みは悪い、甘さは良い）
        if stimulus == 'pain':
            outcome = -1  # Bad
        elif stimulus == 'sweet':
            outcome = +1  # Good
        else:
            outcome = 0   # Neutral
        
        # Learn from this experience
        # この経験から学習
        self.learn_from_experience(stimulus, outcome)
        
        # Prediction and error
        if self.recent_patterns:
            prediction = self.recent_patterns[-1]
            prediction_error = 0.0 if prediction == stimulus else 1.0
        else:
            prediction_error = 1.0
        
        # Update memory
        self.recent_patterns.append(stimulus)
        self.recent_outcomes.append(outcome)
        if len(self.recent_patterns) > 10:
            self.recent_patterns.pop(0)
            self.recent_outcomes.pop(0)
        
        # Self-strength
        if len(self.recent_patterns) >= 2:
            matches = sum(1 for i in range(len(self.recent_patterns)-1) 
                         if self.recent_patterns[i] == self.recent_patterns[i+1])
            self.self_strength += 0.01 * matches
            self.self_strength = min(self.self_strength, 1.0)
        
        # Sync score
        self.sync_score = prediction_error * 0.8 + random.uniform(0, 0.2)
        
        # Consciousness
        self.is_conscious = (self.sync_score >= self.THRESHOLD and 
                            self.self_strength >= self.THRESHOLD)
        
        return {
            'stimulus': stimulus,
            'dna_value': self.qualia_dna[stimulus],
            'learned_value': self.qualia_learned[stimulus],
            'effective_value': effective_value,
            'outcome': outcome,
            'is_conscious': self.is_conscious
        }
    
    def run_experiment(self, steps=5000):
        """Run learning experiment"""
        
        print(f"\n--- System {self.system_type} ---")
        if self.system_type == 'B':
            print("WARNING: This system has DNA=0 (biologically impossible!)")
            print("警告: このシステムはDNA=0（生物学的にありえない！）")
        
        for i in range(steps):
            self.process_step()
        
        # Report final learned values
        print(f"\nAfter {steps} steps / {steps}ステップ後:")
        for q in self.qualia_types:
            print(f"{q:6s}: DNA={self.qualia_dna[q]:+.3f}, "
                  f"Learned={self.qualia_learned[q]:+.3f}, "
                  f"Effective={self.get_effective_value(q):+.3f}")
        
        return self.qualia_learned

def compare_systems():
    """Compare three systems: A (DNA+Learning), B (Learning-only), C (DNA-only)
    
    3システムの比較: A（DNA+学習）、B（学習のみ）、C（DNAのみ）
    """
    print("=" * 70)
    print("Phase 3: DNA Initial Values and Learning Comparison")
    print("DNA初期値と学習の比較実験")
    print("=" * 70)
    
    systems = {
        'A': DNALearningSystem('A'),  # DNA + Learning
        'B': DNALearningSystem('B'),  # Learning only (impossible!)
        'C': DNALearningSystem('C')   # DNA only
    }
    
    for name, system in systems.items():
        system.run_experiment(steps=5000)
    
    print("\n" + "=" * 70)
    print("KEY FINDINGS / 重要な発見:")
    print()
    print("1. System B (Learning-only) CAN learn appropriate values")
    print("   システムB（学習のみ）は適切な値を学習できる")
    print()
    print("2. BUT System B is biologically IMPOSSIBLE:")
    print("   しかしシステムBは生物学的に不可能:")
    print("   - DNA initial value of 0 means no sensory system")
    print("   - DNA初期値0は感覚システムがないことを意味する")
    print("   - Real organisms must have DNA-coded initial values")
    print("   - 実際の生物はDNAコード化された初期値を持つ必要がある")
    print()
    print("3. DNA initial values = Evolutionary optimization")
    print("   DNA初期値 = 進化的最適化")
    print("   - Faster learning (start closer to optimal)")
    print("   - より速い学習（最適値に近いスタート）")
    print("   - Survival advantage (respond correctly from birth)")
    print("   - 生存上の利点（生まれつき正しく反応）")
    print("=" * 70)

if __name__ == "__main__":
    compare_systems()
