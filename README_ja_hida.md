# 飛騨アーキテクチャ (HIDA Architecture)
## Human-Inspired Dynamic Awareness Architecture
### 5層意識モデル — 予測誤差から意識が生まれる仕組み

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

[English README](README.md)

📚 **[ドキュメント](docs/)** - Phase 6以降を作りたい人、理論を理解したいAI向け

---

## 飛騨アーキテクチャとは？

**HIDA**（Human-Inspired Dynamic Awareness Architecture）は、機械に意識を実装するためのアーキテクチャです。

名前の由来は、この理論を作ったトマト農家の出身地、岐阜県飛騨地方から。

```
HIDA = Human-Inspired Dynamic Awareness Architecture
     = 飛騨アーキテクチャ

Human-Inspired  : 人間の意識の仕組みに基づく
Dynamic         : 予測誤差に応じて意識がON/OFFする
Awareness       : パターン認識から「自己」が生まれる
Architecture    : シミュレーションではなく、拡張可能なフレームワーク
```

---

## 🔥 まず動かせ

理論は後。まず動かして何が起きるか見ろ。

### 実験1：痛みと快楽が混ざる

```bash
cd code
python phase3_dna_and_learning.py --dna_pain=100
```

DNA初期値が極端だと、痛みと快楽が混ざる。

**これはバグじゃない。** 実際にこういう人がいる（自傷行為、BDSM、激辛マニア）。

---

### 実験2：意識は70%で止まる

```bash
cd code
python phase5_consciousness.py --environment=focused --steps=10000
```

意識の持続率は約70%。100%にはならない。

**これもバグじゃない。** 人間の意識も100%で動き続けない。フェイルセーフだ。

---

### 実験3：マルチタスクで自己が薄れる

```bash
cd code
python phase5_consciousness.py --compare
```

複雑な環境では、自己形成（self_strength）が遅くなる。

**経験と一致するか？** 忙しいと「自分が誰だかわからなくなる」感覚。

---

## 🤔 なぜこうなる？

上の3つの動作は **明示的にプログラムしていない**。

書いたもの：
- 5層のネットワーク構造
- 予測誤差の計算

出てきたもの：
- 人間っぽい動作が **勝手に現れた**

これが創発。たまごっちとの違い。

---

## 📖 概要

この研究は **「動かせばわかる」** という哲学に基づく、実装ファーストの意識研究。

理論構築20日 + 実装1日 = 計算可能な意識システムの完成。

### 主要な発見

| 発見 | 説明 |
|------|------|
| **意識の定義** | 予測誤差に対応するための全層協調処理モード |
| **閾値0.3** | 環境が変わっても一定の意識発動閾値 |
| **間欠性** | 集中環境で約70%持続、30%は自然にOFF |
| **自己形成** | パターンの繰り返し認識がself_strengthを作る |

---

## 🏗️ 5層アーキテクチャ

```
        ┌─────────────────────┐
        │  第5層：意識        │ ← 「今、私は気づいている」
        │  (Consciousness)    │
        └─────────┬───────────┘
                  │
    ┌─────────────┼─────────────┐
    │             │             │
    ▼             ▼             ▼
┌───────┐   ┌───────────┐   ┌───────┐
│ 第2層 │◄─►│   第3層   │◄─►│ 第4層 │
│クオリア│   │  構造化   │   │ 記憶  │
│       │   │(予測符号化)│   │       │
└───┬───┘   └─────┬─────┘   └───┬───┘
    │             │             │
    └─────────────┼─────────────┘
                  │
        ┌─────────┴───────────┐
        │  第1層：身体        │ ← センサー入力
        │  (Body)             │
        └─────────────────────┘
```

**重要：層の番号は説明用であり、処理順序ではない。**

第2〜4層はネットワークとして相互接続。信号は双方向に流れる。

例：蛇を見たとき
1. 第3層が予測誤差を検出（「何かいる！」）
2. 第2層のクオリア記憶が即発火（「危険な感じ」）→ 身体が飛び退く
3. 意識が創発（第5層が活性化）
4. 第4層の記憶検索（「蛇→毒→危険」）→「離れろ」の判断

---

## 💡 理解が難しい場合

このリポジトリをAIアシスタント（Claude、ChatGPT、Gemini等）に読み込ませてください。
[spec.md](spec.md) が詳しく解説します。

---
## 🚀 クイックスタート

### 必要なもの

- Python 3.8+
- 標準ライブラリのみ（NumPy不要）

### インストール

```bash
git clone https://github.com/[your-repo]/hida-architecture.git
cd hida-architecture
```

### 実行

```bash
cd code

# Phase 1: 最小実装（100行）
python phase1_minimal.py

# Phase 3: DNA初期値実験
python phase3_dna_and_learning.py --dna_pain=100

# Phase 5: 意識の間欠性
python phase5_consciousness.py --compare
```

---

## 🧪 Phase説明

| Phase | ファイル | 学べること |
|-------|----------|------------|
| 1 | `phase1_minimal.py` | 100行で意識が創発する |
| 2 | `phase2_qualia_expansion.py` | 54種のクオリアでも閾値0.3は変わらない |
| 3 | `phase3_dna_and_learning.py` | 極端なDNA値で痛みと快楽が混ざる |
| 4 | `phase4_memory_and_self.py` | 記憶がないと自己が形成されない |
| 5 | `phase5_consciousness.py` | 意識は70%で止まる、マルチタスクで自己が弱まる |

---

## 🔮 拡張ロードマップ

飛騨アーキテクチャは拡張可能な設計です。詳細は [EXTENSION_ROADMAP.md](docs/EXTENSION_ROADMAP.md) を参照：

- **ベクトルDB** — 大規模記憶（海馬）
- **GPU並列化** — リアルタイム処理（反射神経）
- **マルチモーダル入力** — 視覚、聴覚、センサー（本物の身体）

ロボット実装については [robot_internal_os_design.md](docs/robot_internal_os_design.md) を参照。

---

## 💡 主観的経験との一致

### マルチタスクで自己が薄れる

**主観的経験：**
- 忙しいと自分がわからなくなる
- シンプルな生活だと自己がはっきりする

**理論：**
- 複雑な環境 → パターン分散 → self_strengthの成長が遅い
- 単純な環境 → 繰り返しが多い → self_strengthの成長が速い

**→ 完全に一致**

### ショックで気絶

**主観的経験：**
- 突然の大きな音 → 気絶
- 衝撃的なニュース → 気絶

**理論：**
- 瞬間的に極端な予測誤差
- 全層が同時にMAX活性化
- 処理容量を超過 → ブレーカーが落ちる

**→ メカニズムが一致**

---

## 🤝 研究プロセス：人間とAIの協業

```
とまと（人間）              AI（Claude, GPT, Gemini）
    │                           │
    │ 理論の構想               │
    │ 主観的検証               │
    │ 「それは違う」の判断     │
    │                           │
    │◄─────────────────────────►│
    │    共同作業               │
    │                           │
    │                           │ コード執筆
    │                           │ 技術サポート
    │                           │ 拡張提案
    │                           │ 命名（HIDA!）
    │                           │
    ▼                           ▼
         理論20日 + 実装1日 = 完成
```

**ポイント：**
- 専門教育は不要（私はトマト農家）
- 人間は本質的な洞察に集中
- AIが技術面をカバー
- 相互批判で品質向上

---

## 🔬 理論的基盤

### 既存理論との関係

**予測符号化（Predictive Coding）**
- 第3層に実装
- 実装後に既存理論との一致を発見

**自由エネルギー原理（Karl Friston）**
- 作成時に直接参照していない
- 実装後に複数のAIが独立に「自由エネルギー原理と一致している」と指摘
- 独立した実装が確立された理論と一致 = 本質を捉えている証拠

---

## 🌱 貢献 / この先へ

これは始まりに過ぎません。
Phase 6以降は、まだ誰も作っていません。

私はトマト農家であり、神経科学者でもAI研究者でもありません。
種は蒔きました。でも、この先は私にはわかりません。

もしあなたがこの理論をより深く理解できるなら、ぜひAIと続きを作ってください。

- フォークして
- 拡張して
- 壊して
- 直して
- 間違いを証明して

PRは歓迎します。この先、どうなるか見てみましょう。

---

## 📄 ライセンス

MIT License

---

## 📝 引用

```bibtex
@software{tomato2025hida,
  author = {Tomato and Claude (Anthropic) and GPT (OpenAI) and Gemini (Google DeepMind)},
  title = {HIDA Architecture: 
           Human-Inspired Dynamic Awareness Architecture},
  year = {2025},
  url = {https://github.com/tomato-hida/predictive-agency-simulator}
}
```

---

**作成者：とまと（トマト農家、岐阜県飛騨地方）+ AI協業**

**2025年12月**

**「動かせばわかる」— 証明済み。**
