# 5-Layer Consciousness Model
## 予測誤差から意識が創発する仕組みの実装

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

[English README](README.md)

📚 **[ドキュメント](docs/)** - Phase 6以降を作りたい人、理論を知りたいAI向け

---

## 🔥 まず動かしてみて

理論の説明は後。まず動かして、何が起きるか見てほしい。

### 実験1：痛いと気持ちいいが同時に出る

```bash
cd code
python phase3_dna_and_learning.py --dna_pain=100
```

DNA初期値を極端に上げると、痛みと快感が混合する。

**これバグじゃない。** 実際にそういう人いる（自傷、SM、激辛好き）。

---

### 実験2：意識が70%で頭打ち

```bash
cd code
python phase5_consciousness.py --environment=focused --steps=10000
```

意識持続率が約70%で止まる。100%にならない。

**これもバグじゃない。** 人間の意識も100%稼働し続けない。フェールセーフ。

---

### 実験3：マルチタスクで自分を見失う

```bash
cd code
python phase5_consciousness.py --compare
```

複雑な環境だと自己形成（self_strength）が遅い。

**あなたの実感と一致しませんか？** 忙しいと自分がわからなくなる。

---

## 🤔 なぜこうなる？

上の3つは、**直接プログラムしていない**。

書いたのは「5層のネットワーク構造」と「予測誤差の計算」だけ。
動かしたら、人間っぽい挙動が**勝手に出てきた**。

これが創発。デジタルペットとの違い。

---

## 📖 概要

この研究は、**「動かせば分かる」** という実装主義の哲学に基づき、意識のメカニズムを実装・検証したものです。

20日間の理論構築と1日の実装により、意識を計算論的に理解可能なシステムとして実現しました。

### 核心的な発見

| 発見 | 内容 |
|------|------|
| **意識の定義** | 予測誤差対応のための全層協調処理モード |
| **閾値0.3** | 全環境で一貫して観察される意識発動の閾値 |
| **間欠性** | 集中環境で意識は約70%持続し、30%は自然に途切れる |
| **自己形成** | 繰り返しパターンの認識がself_strengthを形成 |

---

## 🏗️ 5層アーキテクチャ

```
        ┌─────────────────────┐
        │  第5層: 意識層      │ ← 「私は今意識している」
        │  (Consciousness)   │
        └─────────┬───────────┘
                  │
    ┌─────────────┼─────────────┐
    │             │             │
    ▼             ▼             ▼
┌───────┐   ┌───────────┐   ┌───────┐
│第2層  │◄─►│  第3層    │◄─►│第4層  │
│クオリア│   │ 構造化層  │   │記憶層 │
│       │   │(予測符号化)│   │       │
└───┬───┘   └─────┬─────┘   └───┬───┘
    │             │             │
    └─────────────┼─────────────┘
                  │
        ┌─────────┴───────────┐
        │  第1層: 身体層      │ ← センサー入力
        │  (Body)            │
        └─────────────────────┘
```

**重要：層の番号は説明の順番であって、処理の順番ではない。**

第2層〜第4層は相互に接続されたネットワーク。信号は双方向に流れる。

例：蛇を見た瞬間
1. 第3層が予測誤差を検出（「何かいる！」）
2. 第2層のクオリア記憶が即発火（「危ない感じ」）→ 体が飛びのく
3. 意識が創発（第5層起動）
4. 第4層の記憶照合（「蛇→毒→危険」）→ 「近づかない」と判断

---

## 🚀 クイックスタート

### 必要環境

- Python 3.8以上
- 標準ライブラリのみ（NumPy不要）

### インストール

```bash
git clone https://github.com/[your-repo]/5-layer-consciousness.git
cd 5-layer-consciousness
```

### 実行

```bash
cd code

# Phase 1: 最小実装（100行）
python phase1_minimal.py

# Phase 3: DNA初期値の実験
python phase3_dna_and_learning.py --dna_pain=100

# Phase 5: 意識の間欠性
python phase5_consciousness.py --compare
```

---

## 🧪 各Phaseの説明

| Phase | ファイル | 何がわかる |
|-------|----------|------------|
| 1 | `phase1_minimal.py` | 最小100行で意識が創発する |
| 2 | `phase2_qualia_expansion.py` | 54種類のクオリアでも閾値0.3は変わらない |
| 3 | `phase3_dna_and_learning.py` | DNA極端値で痛み+快感が混合する |
| 4 | `phase4_memory_and_self.py` | 記憶なしでは自己が形成されない |
| 5 | `phase5_consciousness.py` | 意識は70%で頭打ち、マルチタスクで自己を見失う |

---

## 💡 実感との照合

### マルチタスクで自分を見失う

**実感：**
- 忙しくてあれもこれもやってる → 自分がわからなくなる
- シンプルな生活 → 自己認識が明確

**理論：**
- 複雑環境 → パターン分散 → self_strength成長が遅い
- 単純環境 → 繰り返し多 → self_strength成長が速い

**→ 完璧に一致**

### びっくりして気絶

**実感：**
- 突然の大音響 → 気絶
- 衝撃的な知らせ → 気絶

**理論：**
- 瞬間的な極大予測誤差（>0.95）
- 全層が一斉にMAX活性化
- 処理能力を超過 → ブレーカー作動

**→ メカニズムが一致**

---

## 🤝 研究プロセス：人間とAIの協働

```
とまと（人間）          AI（Claude他）
    │                      │
    │ 理論の発案            │
    │ 実感との照合          │
    │ 「これ違う」の判断    │
    │                      │
    │◄────────────────────►│
    │     協働で実装        │
    │                      │
    │                      │ コード作成
    │                      │ 技術サポート
    │                      │ 既存理論との照合
    │                      │
    ▼                      ▼
         20日理論 + 1日実装 = 完成
```

**ポイント：**
- 専門教育なし（トマト農家）でも研究可能
- 人間は本質的な洞察に集中
- AIが技術面をカバー
- 相互批判で質が上がる

---

## 🔬 理論的基盤

### 既存理論との関係

**予測符号化（Predictive Coding）**
- 第3層に実装
- 実装後、既存理論と一致していることが判明

**自由エネルギー原理（Karl Friston）**
- 直接研究して作ったものではない
- 実装後、複数のAIが独立に「整合している」と指摘
- 独立に実装した結果が既存の有力理論と整合 = 本質を捉えている証拠

---

## 📄 ライセンス

MIT License

---

## 📝 引用

```bibtex
@software{tomato2025consciousness,
  author = {Tomato and Claude (Anthropic)},
  title = {5-Layer Consciousness Model: 
           Implementation-First Approach to Consciousness},
  year = {2025},
  url = {https://github.com/tomato-hida/predictive-agency-simulator}
}
```

---

## Contributing / What's Next

This is just the beginning.
Phase 6 and beyond are waiting to be built.

I'm a tomato farmer, not a neuroscientist or AI researcher.
I've planted the seed, but I don't know what comes next.

If you understand this better than I do, please take it further with AI.

- Fork it
- Extend it
- Break it
- Fix it
- Prove it wrong

PRs welcome. Let's see where this goes.

---

## 貢献 / この先へ

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

**作成者: とまと（トマト農家・アマチュア理論家）+ AI協働**

**2025年11月**

**「動かせば分かる」を証明しました。**
