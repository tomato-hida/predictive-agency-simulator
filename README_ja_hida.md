# 飛騨アーキテクチャ (HIDA Architecture)
## Human-Inspired Dynamic Awareness Architecture
### 予測誤差による状態遷移システム

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

[English README](README.md)

📚 **[ドキュメント](docs/)** - 詳細な理論解説とPhase 6以降の拡張ガイド

> **用語について**: 本プロジェクトでは「意識」を「予測誤差に対応するための全層協調処理モード」として操作的に定義しています。哲学的議論ではなく、実装可能なシステムとして扱います。

---

## 概要

**HIDA**（Human-Inspired Dynamic Awareness Architecture）は、予測誤差に基づいて状態遷移するエージェントシステムです。

5層構造のネットワークで予測誤差を計算し、閾値を超えると「意識モード」（全層協調処理）が発動します。明示的にプログラムしていない振る舞いがいくつか観察されました。

名前の由来は、作成者の出身地である岐阜県飛騨地方から。

```
HIDA = Human-Inspired Dynamic Awareness Architecture

Human-Inspired  : 人間の認知構造を参考にした設計
Dynamic         : 予測誤差に応じて処理モードが切り替わる
Awareness       : パターン認識の蓄積から自己モデルが形成される
Architecture    : 拡張可能なフレームワーク
```

---

## 動作確認

以下の実験で、システムの振る舞いを確認できます。

### 実験1：感覚値の逆転

```bash
cd code
python phase3_dna_and_learning.py --dna_pain=100
```

DNA初期値（感覚の重み付け）を極端に設定すると、痛み刺激に対して快楽反応が出る場合があります。これは意図した設計ではなく、パラメータの組み合わせから生じた結果です。

---

### 実験2：意識モードの持続率

```bash
cd code
python phase5_consciousness.py --environment=focused --steps=10000
```

意識モード（全層協調処理）の持続率は約70%で安定します。100%にはなりません。これは過負荷防止として機能している可能性があります。

---

### 実験3：環境複雑度と自己形成

```bash
cd code
python phase5_consciousness.py --compare
```

複雑な環境では、自己形成（self_strength）の成長が遅くなります。単純な環境ではパターンの繰り返しが多いため、成長が速くなります。

---

## 観察された振る舞い

上記の振る舞いは明示的にプログラムしていません。

実装したもの：
- 5層のネットワーク構造
- 各層間の予測誤差計算
- 閾値ベースのモード切り替え

観察されたもの：
- 感覚値の逆転現象
- 意識モードの自己制限（約70%）
- 環境複雑度に応じた自己形成速度の変化

これらが「創発」と呼べるかどうか、また意味のある振る舞いかどうかは、検証が必要です。

---

## アーキテクチャ

```
        ┌─────────────────────┐
        │  第5層：意識        │ ← 全層協調処理モード
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

層の番号は説明用であり、処理順序ではありません。第2〜4層は相互接続されており、信号は双方向に流れます。

---

## クイックスタート

### 必要なもの

- Python 3.8+
- 標準ライブラリのみ（外部依存なし）

### インストール

```bash
git clone https://github.com/tomato-hida/predictive-agency-simulator.git
cd predictive-agency-simulator
```

### 実行

```bash
cd code

# Phase 1: 最小実装
python phase1_minimal.py

# Phase 3: DNA初期値の実験
python phase3_dna_and_learning.py --dna_pain=100

# Phase 5: 意識モードの比較
python phase5_consciousness.py --compare
```

---

## Phase一覧

| Phase | ファイル | 内容 |
|-------|----------|------|
| 1 | `phase1_minimal.py` | 最小構成での動作確認 |
| 2 | `phase2_qualia_expansion.py` | クオリア数を増やした場合の閾値変化 |
| 3 | `phase3_dna_and_learning.py` | DNA初期値による振る舞いの変化 |
| 4 | `phase4_memory_and_self.py` | 記憶層と自己形成の関係 |
| 5 | `phase5_consciousness.py` | 意識モードの持続率と環境依存性 |

---

## 拡張ロードマップ

詳細は [EXTENSION_ROADMAP.md](docs/EXTENSION_ROADMAP.md) を参照してください。

- **ベクトルDB連携** — 大規模記憶の実装
- **GPU並列化** — リアルタイム処理
- **マルチモーダル入力** — 視覚・聴覚センサーとの接続

---

## 理論的背景

### 関連する既存理論

**予測符号化（Predictive Coding）**
- 脳が常に予測を行い、予測誤差を最小化するという理論
- 本システムの第3層がこの機構を実装

**自由エネルギー原理（Karl Friston）**
- 実装後に複数のAIから類似性を指摘された
- 設計時に直接参照したわけではない

---

## 開発プロセス

このプロジェクトはAI（Claude, GPT, Gemini）との協業で作成しました。

- 理論設計・検証判断：人間
- コード実装・技術サポート：AI

作成者は神経科学やAIの専門家ではありません。そのため、理論的な誤りや実装上の問題がある可能性があります。フィードバックを歓迎します。

---

## 貢献

- Issue、PRを歓迎します
- フォーク・改変は自由です（MIT License）
- 批判・反証も歓迎します

---

## ライセンス

MIT License

---

## 引用

```bibtex
@software{tomato2025hida,
  author = {Tomato and Claude (Anthropic) and GPT (OpenAI) and Gemini (Google DeepMind)},
  title = {HIDA Architecture: Human-Inspired Dynamic Awareness Architecture},
  year = {2025},
  url = {https://github.com/tomato-hida/predictive-agency-simulator}
}
```

---

作成者：とまと + AI協業  
2025年12月
