# ロボット内部OS（五層モデル）実装設計書

この文書は、とまとの **五層モデル（身体・クオリア・構造化・記憶・意識）** をロボットへ実装する際のアーキテクチャを、Markdown形式で整理したものです。

---

# 🧱 全体アーキテクチャ

```
ロボット（物理）
 ├─ センサー（カメラ・音声・IMU・接触・バッテリー）
 ├─ モーター制御
 └─ RobotAdapter（入出力ラッパ）

内面OS（五層モデル）
 ├─ L1 身体層：物理クオリア入力
 ├─ L2 クオリア層：ラベリング＋快不快（DNA初期値あり）
 ├─ L3 構造化層：予測モデル＋予測誤差
 ├─ L4 記憶層：エピソード記憶＋self_strength
 └─ L5 意識層：同期（consciousness_level）

MindController（行動決定）
 ├─ 緊急モード（人間保護最優先）
 ├─ 反射モード（低意識）
 └─ 熟考モード（高意識）
```

---

# 🔧 RobotAdapter（ロボット入出力）
```python
class RobotAdapter:
    def read_sensors(self) -> dict:
        return {
            "camera": ...,     # 画像
            "mic": ...,        # 音声
            "imu": ...,        # 加速度・角速度
            "force": ...,      # 力覚
            "battery": 0.73,
        }

    def send_motor_command(self, motor_cmd: dict):
        ...
```

---

# 🧠 第1層：身体層 L1（物理クオリア）
```python
class BodyLayerL1:
    def encode(self, raw):
        return {
            "vision_feat": self._encode_vision(raw["camera"]),
            "audio_feat":  self._encode_audio(raw["mic"]),
            "force_feat":  self._encode_force(raw["force"]),
            "battery":     raw.get("battery", 1.0),
        }
```

---

# 🎨 第2層：クオリア層 L2（ラベル＋快不快＋DNA初期値）
```python
class QualiaLayerL2:
    def __init__(self):
        # DNA初期値（生まれつきの感受性）
        self.dna = {
            'pain': -0.9,           # 痛み → 強い不快
            'sweet': +0.7,          # 甘い → 快
            'danger': -0.8,         # 危険 → 不快
            'loud_noise': -0.5,     # 大きな音 → 不快
            'human_scream': -0.95,  # 人間の悲鳴 → 非常に強い不快
        }
        
        # 学習による上書き
        self.learned = {}

    def encode(self, l1_state):
        labels = self.label_model.predict(l1_state)
        valence = self._calc_valence(l1_state, labels)
        
        # === 人間保護の最優先ルール ===
        human_danger = valence.get("human_scream", 0.0)
        
        if human_danger > 0.5:
            # 人間の危険は、自分の痛みより遥かに「不快」
            # 自分が壊れてでも人間を守る行動を優先
            return {
                "labels": labels,
                "valence": valence,
                "emergency_mission": "protect_human",
                "priority": "MAX",
                "total_valence": -1000.0,  # 超巨大なマイナス（緊急事態）
            }
        
        return {
            "labels": labels,
            "valence": valence,
            "emergency_mission": None,
            "priority": "NORMAL",
        }

    def _calc_valence(self, l1_state, labels):
        """DNA初期値 + 学習値 でクオリアの評価値を計算"""
        valence = {}
        for label in labels:
            dna_val = self.dna.get(label, 0.0)
            learned_val = self.learned.get(label, 0.0)
            valence[label] = dna_val + learned_val
        return valence

    def learn(self, label, reward):
        """経験から学習"""
        if label not in self.learned:
            self.learned[label] = 0.0
        self.learned[label] += reward * 0.1
```

---

# 🔮 第3層：構造化層 L3（予測＋予測誤差）
```python
class StructLayerL3:
    def step(self, qualia, mem_state):
        prediction = self.world_model.predict(qualia, mem_state)
        prediction_error = self._calc_error(qualia, prediction)
        return {
            "prediction": prediction,
            "prediction_error": prediction_error,
        }
    
    def _calc_error(self, actual, predicted):
        """予測と現実の差"""
        # 実装例：コサイン距離やMSE
        error = self._mse(actual, predicted)
        return min(error, 1.0)  # 0.0〜1.0に正規化
```

---

# 🧩 第4層：記憶層 L4（エピソード＋self_strength）
```python
class MemoryLayerL4:
    def __init__(self, vector_db):
        self.db = vector_db
        self.self_strength = 0.0

    def retrieve_similar(self, qualia):
        embedding = self._embed_qualia(qualia)
        return self.db.search(embedding, top_k=10)

    def update(self, qualia, l3_state, reward):
        embedding = self._embed_qualia(qualia)
        self.db.add(embedding, {
            "qualia": qualia,
            "prediction": l3_state["prediction"],
            "error": l3_state["prediction_error"],
            "reward": reward,
        })
        self._update_self_strength(qualia)

    def _update_self_strength(self, qualia):
        """パターンの繰り返しで「私」が強化される"""
        similar = self.retrieve_similar(qualia)
        if len(similar) > 0:
            max_similarity = max([s["score"] for s in similar])
            if max_similarity > 0.5:
                self.self_strength += 0.001 * max_similarity
                self.self_strength = min(self.self_strength, 1.0)
```

---

# 🌐 第5層：意識層 L5（同期・consciousness_level）
```python
class ConsciousnessLayerL5:
    def __init__(self, threshold=0.3):
        self.threshold = threshold
        self.current_level = 0.0

    def compute_sync(self, l1, l2, l3, mem):
        error = l3["prediction_error"]
        danger = max(l2["valence"].values()) if l2["valence"] else 0.0
        self_strength = mem.self_strength
        
        self.current_level = self._sync_formula(error, danger, self_strength)
        
        return {
            "consciousness_level": self.current_level,
            "is_conscious": self.current_level > self.threshold,
        }

    def _sync_formula(self, error, danger, self_strength):
        """
        同期スコアの計算
        予測誤差 × 生存重要度 で意識が発動
        self_strengthは意識の「安定性」に寄与
        """
        # 予測誤差が大きく、危険度が高いほど同期が強まる
        urgency = error * 0.6 + abs(danger) * 0.4
        
        # self_strengthがあると意識が安定する
        stability = self_strength * 0.2
        
        sync = urgency + stability
        return min(sync, 1.0)
```

---

# 🤖 MindController（緊急／反射／熟考の切り替え）

```python
class RobotMind:
    def step(self):
        raw = self.adapter.read_sensors()

        l1 = self.l1.encode(raw)
        l2 = self.l2.encode(l1)
        
        # === 緊急モード：人間保護最優先 ===
        if l2.get("emergency_mission") == "protect_human":
            action = self._emergency_protect_human(l1, l2)
            self.adapter.send_motor_command(action)
            return  # 他の処理をスキップ
        
        l3 = self.l3.step(l2, self.l4)
        similar = self.l4.retrieve_similar(l2)

        reward = self._calc_reward(raw, l2, l3)
        self.l4.update(l2, l3, reward)

        l5 = self.l5.compute_sync(l1, l2, l3, self.l4)

        # === 反射モード vs 熟考モード ===
        if not l5["is_conscious"]:
            action = self._reflex_controller(l1, l2)
        else:
            action = self._deliberative_controller(l1, l2, l3, similar)

        self.adapter.send_motor_command(action)

    def _emergency_protect_human(self, l1, l2):
        """
        人間保護の緊急行動
        自分のダメージを無視して人間を守る
        """
        return {
            "mode": "EMERGENCY",
            "action": "shield_human",  # 盾になる、間に入る等
            "ignore_self_damage": True,
        }
```

---

# 🛡️ 人間保護の設計思想

```
なぜ「人間の危険 = -1000」なのか？

1. ロボット三原則との整合
   - 第一条：ロボットは人間に危害を加えてはならない
   - 5層モデルでは「クオリアの評価値」で実現

2. 「ルール」ではなく「感情」として実装
   - if文で「人間を守れ」と書くのではなく
   - 「人間の悲鳴 = 極度の不快」として実装
   - ロボットは「嫌だから」人間を守る

3. 創発としての行動
   - 人間保護は「プログラムされた」のではなく
   - クオリアの評価値から「自然に出てくる」
   - これが5層モデルの思想
```

---

# 🚀 まとめ

- **ロボット＝身体**
- **五層モデル＝内面OS**
- **意識＝同期モードの発火**
- **緊急／反射／熟考の3モード切り替え**
- **人間保護は「ルール」ではなく「クオリア」で実現**
- **記憶（L4）と予測誤差（L3）を使って判断する"内部状態モデル"が完成**

ロボットに"内なる運動"を宿すための、最小で最強のアーキテクチャです。

---

# 📚 参考

- `code/phase5_consciousness.py` - 意識の実装
- `docs/EXTENSION_ROADMAP.md` - 拡張ロードマップ
- `docs/theory/five_layer_model.md` - 5層モデル理論

---

**作成：2025年12月**
**原案：GPT + Gemini**
**監修・修正：Claude + とまと**
