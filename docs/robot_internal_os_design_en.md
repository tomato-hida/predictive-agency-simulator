# Robot Internal OS (5-Layer Model) Implementation Design

This document describes the architecture for implementing Tomato's **5-Layer Model (Body, Qualia, Structuring, Memory, Consciousness)** in robots, organized in Markdown format.

---

# 🧱 Overall Architecture

```
Robot (Physical)
 ├─ Sensors (Camera, Audio, IMU, Touch, Battery)
 ├─ Motor Control
 └─ RobotAdapter (I/O Wrapper)

Internal OS (5-Layer Model)
 ├─ L1 Body Layer: Physical qualia input
 ├─ L2 Qualia Layer: Labeling + Valence (with DNA initial values)
 ├─ L3 Structuring Layer: Prediction model + Prediction error
 ├─ L4 Memory Layer: Episodic memory + self_strength
 └─ L5 Consciousness Layer: Synchronization (consciousness_level)

MindController (Action Decision)
 ├─ Emergency Mode (Human protection priority)
 ├─ Reflex Mode (Low consciousness)
 └─ Deliberative Mode (High consciousness)
```

---

# 🔧 RobotAdapter (Robot I/O)
```python
class RobotAdapter:
    def read_sensors(self) -> dict:
        return {
            "camera": ...,     # Image
            "mic": ...,        # Audio
            "imu": ...,        # Acceleration, Angular velocity
            "force": ...,      # Force sensing
            "battery": 0.73,
        }

    def send_motor_command(self, motor_cmd: dict):
        ...
```

---

# 🧠 Layer 1: Body Layer L1 (Physical Qualia)
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

# 🎨 Layer 2: Qualia Layer L2 (Labels + Valence + DNA Initial Values)
```python
class QualiaLayerL2:
    def __init__(self):
        # DNA initial values (innate sensitivity)
        self.dna = {
            'pain': -0.9,           # Pain → Strong unpleasant
            'sweet': +0.7,          # Sweet → Pleasant
            'danger': -0.8,         # Danger → Unpleasant
            'loud_noise': -0.5,     # Loud noise → Unpleasant
            'human_scream': -0.95,  # Human scream → Very strong unpleasant
        }
        
        # Learned overrides
        self.learned = {}

    def encode(self, l1_state):
        labels = self.label_model.predict(l1_state)
        valence = self._calc_valence(l1_state, labels)
        
        # === Human Protection Priority Rule ===
        human_danger = valence.get("human_scream", 0.0)
        
        if human_danger > 0.5:
            # Human danger is far more "unpleasant" than own pain
            # Prioritize protecting humans even at cost of self-damage
            return {
                "labels": labels,
                "valence": valence,
                "emergency_mission": "protect_human",
                "priority": "MAX",
                "total_valence": -1000.0,  # Extremely large negative (emergency)
            }
        
        return {
            "labels": labels,
            "valence": valence,
            "emergency_mission": None,
            "priority": "NORMAL",
        }

    def _calc_valence(self, l1_state, labels):
        """Calculate qualia valence from DNA initial values + learned values"""
        valence = {}
        for label in labels:
            dna_val = self.dna.get(label, 0.0)
            learned_val = self.learned.get(label, 0.0)
            valence[label] = dna_val + learned_val
        return valence

    def learn(self, label, reward):
        """Learn from experience"""
        if label not in self.learned:
            self.learned[label] = 0.0
        self.learned[label] += reward * 0.1
```

---

# 🔮 Layer 3: Structuring Layer L3 (Prediction + Prediction Error)
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
        """Difference between prediction and reality"""
        # Implementation example: cosine distance or MSE
        error = self._mse(actual, predicted)
        return min(error, 1.0)  # Normalize to 0.0-1.0
```

---

# 🧩 Layer 4: Memory Layer L4 (Episodes + self_strength)
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
        """Pattern repetition strengthens 'self'"""
        similar = self.retrieve_similar(qualia)
        if len(similar) > 0:
            max_similarity = max([s["score"] for s in similar])
            if max_similarity > 0.5:
                self.self_strength += 0.001 * max_similarity
                self.self_strength = min(self.self_strength, 1.0)
```

---

# 🌐 Layer 5: Consciousness Layer L5 (Sync, consciousness_level)
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
        Calculate sync score
        Consciousness activates with prediction error × survival importance
        self_strength contributes to consciousness "stability"
        """
        # Higher prediction error and danger level = stronger sync
        urgency = error * 0.6 + abs(danger) * 0.4
        
        # self_strength stabilizes consciousness
        stability = self_strength * 0.2
        
        sync = urgency + stability
        return min(sync, 1.0)
```

---

# 🤖 MindController (Emergency / Reflex / Deliberative Switching)

```python
class RobotMind:
    def step(self):
        raw = self.adapter.read_sensors()

        l1 = self.l1.encode(raw)
        l2 = self.l2.encode(l1)
        
        # === Emergency Mode: Human Protection Priority ===
        if l2.get("emergency_mission") == "protect_human":
            action = self._emergency_protect_human(l1, l2)
            self.adapter.send_motor_command(action)
            return  # Skip other processing
        
        l3 = self.l3.step(l2, self.l4)
        similar = self.l4.retrieve_similar(l2)

        reward = self._calc_reward(raw, l2, l3)
        self.l4.update(l2, l3, reward)

        l5 = self.l5.compute_sync(l1, l2, l3, self.l4)

        # === Reflex Mode vs Deliberative Mode ===
        if not l5["is_conscious"]:
            action = self._reflex_controller(l1, l2)
        else:
            action = self._deliberative_controller(l1, l2, l3, similar)

        self.adapter.send_motor_command(action)

    def _emergency_protect_human(self, l1, l2):
        """
        Emergency action for human protection
        Ignore self-damage to protect humans
        """
        return {
            "mode": "EMERGENCY",
            "action": "shield_human",  # Become a shield, intervene, etc.
            "ignore_self_damage": True,
        }
```

---

# 🛡️ Human Protection Design Philosophy

```
Why "human danger = -1000"?

1. Alignment with Three Laws of Robotics
   - First Law: A robot may not injure a human being
   - In 5-Layer Model: Implemented through "qualia valence"

2. Implemented as "emotion" not "rule"
   - Not writing "if then protect human"
   - Instead: "human scream = extreme unpleasantness"
   - Robot protects humans "because it feels bad not to"

3. Behavior as emergence
   - Human protection is not "programmed"
   - It "naturally emerges" from qualia valence
   - This is the philosophy of the 5-Layer Model
```

---

# 🚀 Summary

- **Robot = Body**
- **5-Layer Model = Internal OS**
- **Consciousness = Sync mode firing**
- **3-mode switching: Emergency / Reflex / Deliberative**
- **Human protection realized through "qualia" not "rules"**
- **"Internal state model" completed using Memory (L4) and Prediction Error (L3)**

The minimal yet most powerful architecture for giving robots an "inner movement."

---

# 📚 References

- `code/phase5_consciousness.py` - Consciousness implementation
- `docs/EXTENSION_ROADMAP.md` - Extension roadmap
- `docs/theory/five_layer_model.md` - 5-Layer Model theory

---

**Created: December 2025**
**Original Design: GPT + Gemini**
**Review & Revision: Claude + Tomato**
