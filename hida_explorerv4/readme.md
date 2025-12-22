# HIDA Explorer - L2クオリア層実装

5層意識モデルにおけるL2（クオリア層）の実装と検証

## 概要

「人間の内面運動理論」に基づき、クオリア（感情的評価）が行動決定に与える影響を実装・検証するプロジェクト。

## 主要な発見

### 1. L5は判断しない

```
❌ L5が判断する主体
✅ L5は同期検知 + 言語系への橋渡し

行動決定: L2/L3/L4の数値計算から自然に決まる
言語化: LLMが状態を言葉に変換
```

### 2. Confabulation（作話）の発生

同じ情報を渡しても、LLMによって自己認識の精度が異なる：

```
【テスト: エネルギー不足で緑ボールを選択】

ollama (gemma3:4b):
「緑のボールは、私の好みにあっていた」
→ Confabulation！（緑の好感度は0.3で低い）

Claude:
「苦手な色だと分かっていても、確実に取れる選択肢に手を伸ばしてしまった」
→ 正確な自己認識
```

### 3. ヒダアーキテクチャの構造

```
L2/L3/L4 ──→ 行動（ルールベース、数値計算）
    │
    └──→ L5（同期検知）──→ LLM（言語化）
```

行動と言葉は分離しているが、同じ情報を見ている。

## ファイル構成

| ファイル | 説明 |
|---------|------|
| `world.py` | グリッドワールド環境 |
| `hida.py` | HIDAエージェント本体 |
| `qualia.py` | L2クオリア層（fear, desire, urgency, color_preference） |
| `l5_sync.py` | L5同期検知 + 言語系への橋渡し |
| `verbalizer.py` | ollama/Claude連携の言語化 |

### テストファイル

| ファイル | 説明 |
|---------|------|
| `test_fear_control.py` | fear閾値による行動変化（100%再現性） |
| `test_multi_qualia.py` | fear × urgency 2×2マトリクス |
| `test_color_preference.py` | 4色ボールの選好テスト |
| `test_confabulation.py` | 行動の本当の理由 vs 言語化された理由 |
| `test_complex_task.py` | エネルギー × 時間 × 好み × 危険の複合タスク |

## 検証結果

### Fear閾値テスト（100回×6条件）

```
fear=0.0: red=100, blue=0
fear=0.2: red=100, blue=0
fear=0.4: red=100, blue=0
----- threshold 0.5 -----
fear=0.6: red=0, blue=100
fear=0.8: red=0, blue=100
fear=1.0: red=0, blue=100
```

→ 閾値0.5で行動が完全に切り替わる

### 2×2マトリクステスト（fear × urgency）

```
            | urgency低(好み優先) | urgency高(近さ優先)
------------------------------------------------------------
fear低(危険) | yellow  (50)      | red     (50)
fear高(安全) | green   (50)      | blue    (50)
```

→ 2つのクオリアで4パターンの行動が創発

### 複合タスク（エネルギー × 時間 × 好み × 危険）

| 条件 | 選択 | 理由 |
|------|------|------|
| 通常 | 赤（好き） | 好みスコアが最高 |
| 低エネルギー | 緑（近い） | エネルギーペナルティで赤が下がる |
| 時間制限 | 赤（好き） | 間に合った |

## スコア計算式

```python
score = preference × 10 
      - distance × (0.5 + urgency)
      - fear × danger_cost
      - energy_penalty
```

行動は最高スコアの選択肢に決まる（L5は判断しない）

## 使い方

### 基本テスト

```bash
cd hida_explorer
python test_fear_control.py
python test_multi_qualia.py
```

### Confabulation検証（ollama必要）

```bash
ollama pull gemma3:4b
python test_confabulation.py
```

### Claude比較（APIキー必要）

```bash
# Windows
set ANTHROPIC_API_KEY=sk-ant-...
python test_complex_task.py

# Mac/Linux
export ANTHROPIC_API_KEY=sk-ant-...
python test_complex_task.py
```

## 理論的意義

### クオリアの組み合わせ爆発 = 個性

```
1クオリア × 2閾値 = 2パターン
2クオリア × 2閾値 = 4パターン
3クオリア × 2閾値 = 8パターン
4クオリア × 3閾値 = 81パターン
```

### Confabulationの原因

1. **語彙不足**: 「エネルギー不足」を知らない → 「好き」で説明
2. **言葉と内部状態の結びつきが弱い**: パターンはあるがラベルがない
3. **情報の欠落**: 本当の理由が見えない → 推測で埋める
4. **説明の楽さ**: 「好きだから」は説明しやすい

### 次のステップ: L2の圧縮

現在の個別クオリア（fear, desire, ...）を基本軸に圧縮：

```python
# Russellの感情円環モデル
valence: float   # 快-不快 (-1 to 1)
arousal: float   # 覚醒-沈静 (-1 to 1)

# L4でラベル辞書を学習
{"ワクワク": (v>0.3, a>0.6), "へとへと": (v<-0.3, a<-0.5), ...}
```

## ライセンス

MIT License


