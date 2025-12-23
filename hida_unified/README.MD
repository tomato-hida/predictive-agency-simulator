# HIDA Unified - 5層意識モデル統合版

## 概要

「人間の内面運動理論」に基づく5層意識モデルを1ファイルに統合した実装。
**脚本なし、数値の力学だけで行動と性格が決まる。**

## アーキテクチャ

```
L1（身体）→ position, energy, fatigue
    ↓
L2（クオリア）→ valence, arousal, fear, desire, urgency
    ↓
L3（予測）→ 予測誤差検出
    ↓
L4（記憶）→ 内部マップ、LTM、変調値
    ↓
L5（意識）→ 同期検知、自認、言語化
    ↓
LLM → 自然言語での自己表現
```

## 核心的発見

### 1. L5（意識）は判断しない

```
❌ L5が判断する主体
✅ L5は同期検知 + 言語系への橋渡し

行動決定: L2/L3/L4の数値計算から自然に決まる
言語化: LLMが状態を言葉に変換するだけ
```

### 2. 記憶 → 数値変調 → 行動変化

```
経験の蓄積（LTM）
    ↓
変調値（hida_modulation.json）
  - fear_weight: 恐怖感度
  - safe_preference: 安全志向度
  - energy_caution: エネルギー慎重さ
    ↓
L2クオリアに適用
    ↓
スコア計算が変わる
    ↓
行動が変わる
```

**脚本テキストなし。数値だけで性格が決まる。**

### 3. 2種類のダメージ（痛みと疲労の分離）

危険ゾーンで2種類の影響を受ける：

```
⚡ 痛い（danger_pain）33%
    → fear上昇（その場で行動変化）
    → 記憶に保存
    → 次回fear_weight上昇
    → 危険を避けるようになる

💦 疲れた（danger_fatigue）33%
    → energy減少
    → 遠いものを避ける
    → 近いものを選ぶようになる
```

**別のメカニズムで行動に影響：**
```
痛い目に遭う → 次から怖い → 危険を避ける（恐怖記憶）
疲れる → 遠くまで行けない → 近いの選ぶ（体力消耗）
```

### 4. 環境が変われば性格も変わる

```
低エネルギー続き → 緑（安全）を選ぶ → safe_pref上昇
高エネルギー続き → 赤（好き）を選ぶ → safe_pref低下

痛い目に遭い続ける → fear_weight上昇 → 慎重になる
成功体験を積む → fear_weight低下 → 冒険的になる

環境 → 行動 → 記憶 → 変調値 → 行動（ループ）
```

## 使い方

```bash
# 通常テスト（高E→低Eの2回）
python hida_unified.py

# 低エネルギー5回（慎重になる）
python hida_unified.py loop

# 高エネルギー5回（冒険的になる）
python hida_unified.py loop_high

# 記憶と変調値をリセット
python hida_unified.py reset
```

### ollama使用

```bash
ollama pull gemma3:4b
python hida_unified.py
```

### Claude API使用

```bash
# Windows
set ANTHROPIC_API_KEY=sk-ant-...

# Mac/Linux
export ANTHROPIC_API_KEY=sk-ant-...

python hida_unified.py
```

## テスト結果例

### 痛い目に遭って慎重になる

```
セッション1: fear_weight=1.00 → 赤を取る
    ⚡ 痛い！ fear=0.55
セッション2: fear_weight=1.10 → 赤を取る
    ⚡ 痛い！ fear=0.40
    💦 疲れた！ E=0.68
セッション3: fear_weight=1.20 → まだ赤
    ...
セッション5: fear_weight=1.80 → 緑を選ぶ！
```

### 途中で行動が変わる

```
Step 5: go_to_red（赤に向かう）
Step 6: ⚡ 痛い！ fear=0.40
Step 7: ⚡ 痛い！ fear=0.99
Step 8: go_to_blue（青に切り替え！）
```

痛い目に遭った瞬間、行動が変わる。

### スコア計算式

```python
score = preference × 10 
      - distance × (0.5 + urgency)
      - danger_penalty × fear_weight   # 痛い経験で増加
      + safe_bonus × safe_preference   # 安全経験で増加
      - energy_penalty × (1 + energy_caution)
```

## ファイル構成

| ファイル | 説明 |
|---------|------|
| `hida_unified.py` | 全層統合コード（L1〜L5 + LLM） |
| `hida_ltm.json` | 長期記憶（自動生成） |
| `hida_modulation.json` | 変調値（自動生成） |

## 理論的意義

### 意識の役割

```
L5（意識）= L1〜L4の状態を自認 + 言語化 + コミュニケーション
         = 内部状態の「外部出力インターフェース」
         ≠ 判断する主体
```

### 性格形成のメカニズム

```
DNA由来: color_preference（好み）
身体: energy, fatigue
記憶: LTM → 変調値

これらの数値の力学で行動が決まる
LLMは数値を見て言語化するだけ
```

### 痛みと疲労の分離

```
痛み = 恐怖の記憶（fear経由）
疲労 = 身体の消耗（energy経由）

同じ「危険」でも別のメカニズムで行動に影響
人間と同じ
```

## ライセンス

MIT License

## 現状の課題と将来の拡張

### 忘却システム（実装済み）

```
fear_weight: 毎セッション5%減衰（最低1.0）
safe_preference: 毎セッション2%減衰（最低0.0）

→ トラウマも安全志向も時間で薄れる
→ ダイナミックなループが続く
→ 「たまに赤が復権」して葛藤が生まれる
```

```python
# fear忘却
if fear_weight > 1.0:
    fear_weight *= 0.95

# safe忘却  
if safe_preference > 0.0:
    safe_preference *= 0.98
```

**調整ポイント：** 0.95, 0.98の値を変えると忘却速度が変わる

### エネルギー回復

```
現状: 回復しない（バッテリー的）

拡張案:
- 充電スポット → energy回復
- 休憩アクション → fatigue回復  
- 食事オブジェクト → 両方回復
```

### その他の拡張可能性

```
- 複数エージェントの相互作用
- より複雑な環境（複数の危険ゾーン）
- 報酬の種類を増やす
- 感情の種類を増やす（怒り、悲しみなど）
```

## 関連

- [人間の内面運動理論](https://github.com/tomato-and-mozzarella/human-inner-movement-theory)
