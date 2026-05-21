# HIDA v2.0 - AI向け実装仕様書

このドキュメントは、AIがHIDA意識モデルのコードを書くために必要な情報をまとめたものです。

**用語について**: 本プロジェクトでは「意識」を「L1〜L4の主導・追随による動的同期状態」として操作的に定義しています。哲学的議論ではなく、実装可能なシステムとして扱います。

**バージョン**: v2.0（2026年5月） — 主導・追随モデルへの再定式化

---

## 1. モデルの目的

「意識とは何か」を計算可能な形で実装し、シミュレーションで検証する。

**核心の主張：**
- 意識は「主導層が同期信号を発し、追随層が整合的に応答する動的状態」
- 意識は連続的ではなく、間欠的（ON/OFF）
- 意識の質は主導タイプ（sync_type）として構造的に記述される
- 「自己」は最初から存在せず、経験の蓄積で形成される（self_strength）

> ※ `self_strength` は理論上の自己形成指標であり、Phase別実装（特に `phase4_memory_and_self.py`）と論文で扱う。現行の統合版 `hida_unified_v2.py` では、L4の長期記憶・経験由来の `modulation`・行動傾向（`learned_tendencies`）として部分的に表現される。

**v1.1からv2.0の主な変更**: 同期を「対称的な同時活動」から「主導・追随による非対称的構造」へと再定式化した。詳細は論文 `HIDA_theory_paper_v2_0.md` 参照。

---

## 2. 5層アーキテクチャ

```
        ┌─────────────────────┐
        │  第5層: 意識        │ ← 主導・追随同期
        │  (Consciousness)    │   状態を記述する操作的概念
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
        │  第1層: 身体        │ ← センサー入力
        │  (Body)             │   外受容＋内受容
        └─────────────────────┘
```

**重要：層の番号は説明の順番であり、処理の順番ではない。2-4層は相互ネットワーク。**

---

## 3. 各層の定義

### 第1層：身体層 (Body Layer)
- **役割：** 外部環境からの信号を受け取り、電気信号に変換
- **入力：** 外受容（皮膚・目・耳・鼻・舌）と内受容（ホルモン・自律神経・疲労・痛覚など）
- **出力：** 身体状態（energy, fatigue, position, holding 等）
- **v2.0での三役割：**
  1. センサー機能（従来通り）
  2. 同期信号の発生源（主導層になりうる）
  3. 現実接地の担い手（L1外受容入力がL3・L4の内部生成を継続的に修正）

### 第2層：クオリア層 (Qualia Layer)
- **役割：** 信号を「感じ」に変換。即応的な記憶（RAM的）
- **入力：** 第1層からの信号
- **出力：** valence (-1.0〜+1.0), arousal (-1.0〜+1.0), 個別qualia辞書
- **特徴：** 概念を経由せず身体を動かせる（蛇→飛びのく）
- **個別クオリア：** fear, desire, surprise, curiosity, urgency, anger, sadness, joy, disgust

### 第3層：構造化層 (Structuring Layer)
- **役割：** パターン認識、予測、予測誤差の計算
- **入力：** 第2層からのクオリア、第4層からの記憶、第1層からの感覚
- **出力：** errors リスト（各誤差に magnitude を持つ）
- **計算：** 「予測」と「実際」のズレを数値化
- **実装：**
```python
class L3Prediction:
    def __init__(self):
        self.predictions = {}
        self.errors = []  # 各要素は {'type': str, 'pos': tuple, 'magnitude': float, ...}
```

### 第4層：記憶層 (Memory Layer)
- **役割：** 長期記憶の保存と照合（SSD的）、記憶活性化の追跡
- **入力：** 経験（stimulus, qualia, 結果）
- **出力：** 過去のパターン、自己の履歴、activation_count
- **v2.0新規：** `activation_count` 属性。新規発見・パターン照合・記憶再活性化のたびに増加
- **特徴：** self_strengthの基盤

### 第5層：意識層 (Consciousness Layer)
- **役割：** L1〜L4の主導・追随同期パターンを記述する操作的概念
- **v2.0出力：** 
  - `is_conscious` (bool): 意識ON/OFF
  - `sync_score` (float, [0,1]): 同期強度
  - `sync_type` (str|None): 主導タイプ {'L1', 'L2', 'L3', 'L4', None}
- **重要：** 第5層は能動的処理主体ではなく、L1〜L4の状態を記述する概念。「行動を選択する主体」「層を制御する主体」ではない。

---

## 4. v2.0 中核：主導・追随モデル

### 4.1 中核定義

| 用語 | 定義 |
|---|---|
| 同期信号 | ある層の活動量が閾値を超え、他層の状態更新を誘導する起点となる信号 |
| 活動量 | 層ごとに測定される「状態の変化の強さ」（絶対値ではなく変化量） |
| 主導層 | その時点で最大の活動量を示す層。状況に応じて変化 |
| 追随層 | 主導層の活動に応じて状態変化する層 |
| 同期 | 主導層の活動に対して、追随層が一定時間内に整合的に変化すること |
| 現実接地 | L1外受容入力がL3・L4の内部生成を継続的に修正している状態 |

### 4.2 各層の活動量計算

各層の活動量は「前ステップからの変化量」として測定する：

```python
# L1: 身体状態の変化量
l1_change = abs(l1.energy - prev.l1_energy) + abs(l1.fatigue - prev.l1_fatigue)
l1_act = clip01(l1_change / 1.0)

# L2: 価値変化量（valence/arousal/qualiaの変動）
l2_change = abs(l2.valence - prev.l2_valence) + \
            abs(l2.arousal - prev.l2_arousal) + \
            sum(abs(l2.qualia[k] - prev.l2_qualia.get(k, 0)) for k in l2.qualia)
l2_act = clip01(l2_change / 3.0)

# L3: 予測誤差の強度合計
l3_magnitude_sum = sum(e.get('magnitude', 0.0) for e in l3.errors)
l3_act = clip01(l3_magnitude_sum / 3.0)

# L4: 記憶活性化の増分
l4_change = max(0, l4.activation_count - prev.l4_activation_count)
l4_act = clip01(l4_change / 3.0)
```

**注意：** 正規化定数（1.0, 3.0, 3.0, 3.0）は初期DNAであり、環境に応じて調整される対象。

### 4.3 主導層の特定

```python
LEADER_THRESHOLD = 0.3

def detect_leader(activities):
    candidates = {k: v for k, v in activities.items() if v >= LEADER_THRESHOLD}
    if not candidates:
        return None, 0.0  # 同期信号なし
    leader = max(candidates, key=candidates.get)
    return leader, candidates[leader]
```

閾値以下なら、現行実装では「主導層なし」として扱い、`sync_type = None`、`raw_sync = 0.0` となる。

理論上は、複数層が低〜中程度に揃う状態を「均衡的同期状態」（論文§2.3.9）として拡張可能だが、**v2.0簡易実装では未実装**である。将来の拡張対象。

### 4.4 追随整合性の評価（簡易版）

```python
def measure_follower_coherence(activities, leader, leader_strength):
    follower_activities = [v for k, v in activities.items() if k != leader]
    follower_mean = sum(follower_activities) / 3
    return clip01(follower_mean / leader_strength)
```

**注：** v2.0簡易版。本来は時間遅れ相関や位相同期で測るべき（将来拡張）。

### 4.5 同期スコアの算出

```python
sync_score = leader_strength × follower_coherence
```

### 4.6 時間平滑化とヒステリシス

```python
EMA_ALPHA = 0.35
ON_THRESHOLD = 0.03   # デモ用仮値（論文記述は0.55）
OFF_THRESHOLD = 0.02  # デモ用仮値（論文記述は0.50）

ema = (1 - EMA_ALPHA) * prev_ema + EMA_ALPHA * raw_sync

if not is_conscious:
    is_conscious = (ema >= ON_THRESHOLD)
else:
    is_conscious = (ema >= OFF_THRESHOLD)
```

**注：** 閾値は現在の活動量スケール（変化量ベース、各層0-1正規化）に合わせて低めに設定。論文記述の0.55/0.50は別スケールを前提とした概念値。整合的な閾値調整は研究対象。

---

## 5. 意識判定ロジック（v2.0）

```python
def check_sync(self, l1, l2, l3, l4):
    """毎ステップ呼ぶこと（GPT指摘によるバグ修正）"""
    
    # Step 1: 各層の活動量（変化量として）
    activities = self._measure_activity(l1, l2, l3, l4)
    
    # Step 2: 主導層の特定
    leader, leader_strength = self._detect_leader(activities)
    
    if leader is None:
        # 同期信号なし
        raw_sync = 0.0
        self.sync_type = None
    else:
        # Step 3: 追随整合性
        follower_coherence = self._measure_follower_coherence(
            activities, leader, leader_strength
        )
        # Step 4: 同期スコア
        raw_sync = leader_strength * follower_coherence
        self.sync_type = leader
    
    # Step 5: EMAとヒステリシス
    self._ema = (1 - self.EMA_ALPHA) * self._ema + self.EMA_ALPHA * raw_sync
    self.sync_score = self._ema
    
    if not self.is_conscious:
        self.is_conscious = (self._ema >= self.ON_THRESHOLD)
    else:
        self.is_conscious = (self._ema >= self.OFF_THRESHOLD)
    
    # Step 6: 次ステップ用に保存
    self._update_prev(l1, l2, l3, l4)
    
    return self.is_conscious
```

**重要なポイント：**
- `check_sync()` は毎ステップ呼ぶ（5ステップごとではない）
- 感情イベント（ゴール到達のjoy上昇など）は `check_sync()` の**前**に処理する
- LLM言語化（`reflect()`）は同期判定とは分離する

---

## 6. 初期DNA設定（v2.0コードの「生まれながらの値」）

論文§2.3.2「DNA初期値＋学習値」の枠組みに従い、以下の値は初期DNA。

### L5の閾値
```python
LEADER_THRESHOLD = 0.3
EMA_ALPHA = 0.35
ON_THRESHOLD = 0.03    # デモ用、論文は0.55
OFF_THRESHOLD = 0.02   # デモ用、論文は0.50
```

### L4のactivation_count増加ルール
```python
# update_from_sense:
新規セル発見:                +1
新規オブジェクト発見:         +1
既知オブジェクトの再観測:     +0.3

# update_from_errors:
予測誤差由来の記憶更新:       +1 + qualia_intensity

# mark_visited:
新規訪問:                    +0.5
```

### クオリア反応の初期DNA

現行コードでは、fear, joy, anger, disgust などのクオリア値そのものは初期状態では 0.0 から始まる。

一方で、**どの刺激に対してどのクオリアがどれだけ変化するか、またどの方向のvalence/arousalを持つか**は、DNA初期値に相当する。

例（現行コードに実装されている反応の初期DNA）:
```
danger / pain         → fear 上昇, valence 低下
goal_reached          → joy 上昇 (+0.5), valence 上昇 (+0.3)
                        好きな色なら joy さらに +0.3
rotten object         → disgust 上昇 (+0.6), valence 低下 (-0.4)
NPC block (邪魔)       → anger 上昇 (+0.3), arousal 上昇 (+0.2)
exhausted (疲労)       → sadness 上昇 (+0.15)
```

**極端なDNA初期値の効果（実装上の予測）：**

極端な初期反応量を設定すると、通常とは異なる価値づけが生じる可能性がある。
ただし、これは病理や嗜好を直接説明するためのものではなく、**初期反応量が行動傾向に与える影響を検証するための実験設定**である。

**重要：** これらの初期DNA値はコードに固定されているが、「正しい値」ではなく「出発点」である。環境適応・学習による更新、コミュニティでのキャリブレーションが今後の研究対象。

---

## 7. step() の処理順序（v2.0で重要）

```python
def step(self, world):
    # 1. 変調値適用、L2更新
    self.l2.apply_modulation(...)
    self.l2.update_from_body(...)
    
    # 2. 感覚・思考・行動
    errors = self.sense(world)
    action, details = self.think(world)
    event = self.act(world, action, details)  # "goal_reached"/"grabbed_ball"/None
    
    # 3. 記録
    self.l4.mark_visited(...)
    
    # 4. イベント別処理
    if event == "grabbed_ball":
        self.l4.remember_consciously(...)
    if event == "goal_reached":
        # joy上昇などの感情イベント処理
        # この処理は check_sync の前に実施（同期判定に反映させるため）
        self.l2.qualia['joy'] += ...
        self.l2.valence += ...
        self.l4.remember_consciously(...)
    
    # 5. クオリア減衰
    self.l2.decay_qualia()
    
    # 6. 同期判定（毎ステップ）
    is_conscious = self.l5.check_sync(self.l1, self.l2, self.l3, self.l4)
    
    # 7. 必要なら言語化
    if verbose and is_conscious and self.step_count % 5 == 0:
        reflection = self.reflect(action, details)
```

**順序のポイント：**
- 感情イベント処理は check_sync の前
- check_sync は毎ステップ呼ぶ
- reflect は check_sync の後、意識ON時のみ
- act() の戻り値は bool ではなくイベント名（grabbed_ball / goal_reached / None）

**`remember_consciously` の名前について**:

現行コードでは歴史的経緯により `remember_consciously` という関数名を用いているが、実際には危険ゾーンでの痛み・疲労イベントなど、L5がONでない時点でも呼ばれる「重要イベントの記録」用途も含む。

将来的には `remember_event` または `store_event_memory` への改名が望ましい。AIがこの関数名から「L5がONのときだけ記憶」と誤解しないよう注意すること。

---

## 8. 検証すべき予測（v2.0で14予測）

### v1.1から継続（8予測）
1. ✅ 記憶を封じると意識が消える（self_strengthが増えない）
2. ✅ 閾値前後で質的変化（言語があれば「私が」が誕生）
3. ✅ 繰り返しと「私」の強さ（self_strengthの線形成長）
4. ✅ 言語獲得と感じの報告
5. ✅ クオリア数と処理速度
6. ✅ DNA初期値と学習速度（Garcia効果）
7. ✅ 閉じた回路の必要性
8. ✅ 予測誤差と意識のON/OFF

### v2.0新規（6予測）
9. □ 主導タイプの切り替え頻度と健康な意識
10. □ L1外受容遮断と現実接地の喪失
11. □ 主導強度と追随整合性の独立性
12. □ 主導タイプと現象学的体験の対応
13. □ 主導層の固着と病理的状態
14. □ sync_typeの予測可能性

詳細は論文§6を参照。

---

## 9. コードを書くAIへの注意

### 9.1 デジタルペット化を避ける

**やってはいけない：**
```python
# 直接的な振る舞い記述
if is_conscious:
    print("意識が芽生えました")
```

**やるべき：**
```python
# メカニズムを書く
sync_score = leader_strength * follower_coherence
is_conscious = (ema >= ON_THRESHOLD)
# 結果として振る舞いが創発する
```

### 9.2 主体性を持たせない

L5は**主体ではない**。「L5が判定する」「L5が選ぶ」と書きそうになったら立ち止まる。L5は「状態を記述する操作的概念」。

**避けるべき表現：**
- 「第5層が他層を統合する」
- 「意識が選択する」
- 「L5が決定する」

**使うべき表現：**
- 「L1〜L4の状態から sync_score が算出される」
- 「主導層と追随層の関係として記述される」
- 「同期パターンが成立する」

### 9.3 創発と設計の区別

実装する時は、**「これは設計判断（初期DNA）」「これは創発(実行時に生じる)」**を明確に分ける。

- **初期DNA**: 閾値、増加ルール、減衰率、DNA初期値
- **創発**: sync_typeの切り替えパターン、意識ON持続時間、性格形成、self_strength推移

### 9.4 学習値を手でいじらない

**HIDAの研究方法論として重要な原則：**

> 学習値・経験値は、望ましい挙動を出すために手で書き換えない。
> 調整してよいのは、閾値・正規化係数・減衰率・初期反応量などの**初期DNA**である。
> 経験後の傾向は、環境との相互作用からHIDA自身が形成するものとして扱う。

具体的には：
- `self_strength` を手で大きくしてはいけない（経験から育つもの）
- `activation_count` を直接設定してはいけない（イベントから増えるもの)
- `learned_tendencies`、`modulation` を直接書き換えてはいけない（学習結果）
- LTM（長期記憶）の中身を直接編集してはいけない

**手で調整してよいのは初期DNA（コード上の定数として固定されている値）のみ。**

これを守らないと、HIDAは「人間が指示した通りに振る舞うペット」になってしまう。HIDAの研究価値は「初期DNAから何が創発するか」を観察できる点にある。

### 9.5 予想外の結果を大切にする

- 「バグかも？」と思ったら人間に確認
- 実際の人間の経験と照合する
- 創発した振る舞いを記録する

### 9.6 シンプルに始める

- 複雑な式より、動くコードを先に
- 検証してから拡張する
- 最初の実装は粗くてよい（v1.1からv2.0への移行はそのプロセス）

---

## 10. v2.0実装の主要クラス構造

### L5Consciousness

```python
class L5Consciousness:
    # クラス定数（初期DNA）
    LEADER_THRESHOLD = 0.3
    EMA_ALPHA = 0.35
    ON_THRESHOLD = 0.03
    OFF_THRESHOLD = 0.02
    
    def __init__(self):
        self.is_conscious = False
        self.sync_score = 0.0
        self.sync_type = None
        self._ema = 0.0
        self._prev = {...}  # 前ステップ保存
    
    def _measure_activity(self, l1, l2, l3, l4) -> Dict[str, float]:
        """各層の活動量を変化量として測定"""
        ...
    
    def _detect_leader(self, activities) -> Tuple[Optional[str], float]:
        """主導層特定"""
        ...
    
    def _measure_follower_coherence(self, activities, leader, leader_strength) -> float:
        """追随整合性（簡易版）"""
        ...
    
    def _update_prev(self, l1, l2, l3, l4):
        """次ステップ用の状態保存"""
        ...
    
    def check_sync(self, l1, l2, l3, l4) -> bool:
        """毎ステップ呼ぶ。主導・追随モデルによる同期判定"""
        ...
```

### L4Memory への追加

```python
class L4Memory:
    def __init__(self):
        ...
        self.activation_count = 0  # v2.0追加：記憶活性化カウンタ
    
    def update_from_sense(self, sense_data):
        # 新規発見・既知再観測でactivation_count増加
        ...
    
    def update_from_errors(self, errors, qualia_intensity):
        # 予測誤差由来の記憶更新で強く活性化
        ...
    
    def mark_visited(self, pos):
        # 新規訪問でactivation_count増加
        ...
```

---

## 参照ファイル

- `HIDA_theory_paper_v2_0.md` — v2.0論文本体（理論詳細）
- `code/hida_unified_v2.py` — v2.0実装本体
- `code/phase1_minimal.py` 〜 `phase5_consciousness.py` — Phase別実装
- `HIDA_v2_0_summary.pdf` — A4一枚要約

---

**作成・改訂：**
- v1.0: 2025年11月（最初のSpec）
- v2.0: 2026年5月21日（主導・追随モデル対応）

**作成者：** とまと（トマト農家）＋ Claude（Anthropic）＋ GPT（OpenAI）
