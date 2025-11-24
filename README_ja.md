Markdown

# Predictive Agency Simulator
### (旧題: 人の内なる運動理論 / Theory of Human Inner Movement)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

**予測符号化（Predictive Coding）と自由エネルギー原理に基づく、自己組織化エージェントのPython実装**

[English README](README.md)

---

## 📖 概要 (Overview)

このプロジェクトは、トップダウンな「意識」の設計ではなく、**予測誤差の最小化プロセスから「自己感（Agency）」や「意識の断続性（Intermittency）」が創発するか**を検証するための実験的実装です。

わずか数百行のPythonコードによる5層アーキテクチャの実装実験において、**環境の複雑度に応じてエージェントのメタ認知機能が自然にON/OFFを繰り返す「間欠性」**（集中状態で約70%の稼働率）が確認されました。

これは、人間の主観的な「フロー体験」や「マルチタスク時の混乱」と数理的に整合する挙動を示しています。

## 🧪 主な発見 (Key Findings)

本シミュレーター（Phase 5）における60,000ステップの検証結果：

### 1. 意識の間欠的な創発
* **予測可能な環境（Focused）:** エージェントは **70.6%** の時間で高次レイヤー（意識）を活性化させ、残りの30%は自動処理に委ねる挙動を示しました。これは生物における「慣れ」や「省エネ」のメカニズムと一致します。
* **予測困難な環境（Varied）:** この活性率は **40.0%** まで低下し、過剰な予測誤差により自己形成が阻害される様子が観察されました。

### 2. 閾値の普遍性
単純な環境から複雑な多次元クオリア環境まで、自己組織化が安定して発生する `Sync Score` の閾値が **約0.3** であることが、一貫して観測されました。

### 3. 動的な自己境界
記憶（Memory）と予測（Prediction）の相互作用により、エージェントは外部刺激のパターンから「自己（制御可能な領域）」と「環境（制御不可能な領域）」の境界線を動的に学習します。

## 🏗️ アーキテクチャ (Architecture)

Fristonの自由エネルギー原理および予測符号化の理論と（事後的に）整合する、以下の5層構造を採用しています。

```mermaid
graph TD
    L5[Layer 5: Consciousness (Global Workspace)] -->|Top-down| L4
    L4[Layer 4: Memory & Self-Model] -->|Prediction| L3
    L3[Layer 3: Predictive Coding (Error Detection)] -->|Error Signal| L4
    L3 -->|Sensory Prediction| L2
    L2[Layer 2: Qualia Processing] -->|Raw Data| L3
    L1[Layer 1: Body / Sensor Inputs] -->|Stimulus| L2
Layer 3 (Structuring): 予測誤差（Prediction Error）を計算。

Layer 4 (Self-Model): 誤差のフィードバックを受け、内部モデル（世界モデル）を更新。

Layer 5 (Meta-Cognition): 予測誤差と自己一貫性の同期レベル（Sync Score）を監視し、特定の条件下でのみ「意識モード」を発動させる。

🚀 クイックスタート (Quick Start)
最小構成（Minimal Implementation）
予測符号化による自己形成のコアロジックは、わずか100行で実装されています。

Python

from code.phase1_minimal import MinimalConsciousness

# エージェントの初期化
system = MinimalConsciousness()

# 100ステップのシミュレーション
for step in range(100):
    result = system.process_step()
    
    if result['is_conscious']:
        print(f"Step {step}: Agency Activated! (Sync: {result['sync_score']:.3f})")
完全版シミュレーション（Phase 5）
意識の間欠性を確認する実験コードです。

Python

from code.phase5_consciousness import ConsciousnessSystem

system = ConsciousnessSystem()
# 集中環境（Focused）での実験
results = system.run_experiment(steps=10000, environment='focused')
🤝 背景 (Background: Implementation-First Approach)
本プロジェクトは、専門的なAI研究機関によるものではなく、**「動かせば分かる（Implementation-First）」**という哲学を持つトマト農家と、複数のLLM（Claude, Gemini, GPT）との対話的協働によって開発されました。

理論先行ではなく、「予測誤差に対してシステムはどう振る舞うべきか？」という実装上の要請を積み重ねた結果、生成されたコードが現代の脳科学理論（自由エネルギー原理など）と高い整合性を示したことは、本プロジェクトの特筆すべき成果です。

より詳細な経緯や理論的背景については、ドキュメントフォルダを参照してください
