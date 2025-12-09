# 5-Layer Consciousness Model - Implementation Spec for AI

This document contains all the information an AI needs to write code for this consciousness model.

---

## 1. Purpose of the Model

Implement "what is consciousness" in a computable form and verify through simulation.

**Core Claims:**
- Consciousness is "a processing mode that synchronizes all layers when prediction errors are survival-relevant"
- Consciousness is not continuous but intermittent (ON/OFF)
- "Self" does not exist from the start; it forms through accumulated experience

---

## 2. 5-Layer Architecture

```
        ┌─────────────────────┐
        │  Layer 5: Conscious │ ← Full-layer sync mode
        │  (Consciousness)    │
        └─────────┬───────────┘
                  │
    ┌─────────────┼─────────────┐
    │             │             │
    ▼             ▼             ▼
┌───────┐   ┌───────────┐   ┌───────┐
│Layer 2│◄─►│  Layer 3  │◄─►│Layer 4│
│Qualia │   │Structuring│   │Memory │
│       │   │(Pred.Code)│   │       │
└───┬───┘   └─────┬─────┘   └───┬───┘
    │             │             │
    └─────────────┼─────────────┘
                  │
        ┌─────────┴───────────┐
        │  Layer 1: Body      │ ← Sensor input
        │  (Body)             │
        └─────────────────────┘
```

**Important: Layer numbers are for explanation, NOT processing order. Layers 2-4 form a mutual network.**

---

## 3. Layer Definitions

### Layer 1: Body Layer
- **Role:** Receive signals from external environment, convert to electrical signals
- **Input:** Sensor data (vision, hearing, touch, etc.)
- **Output:** Normalized signal values
- **Implementation:** Expressed as `stimulus` (string or numeric)

### Layer 2: Qualia Layer
- **Role:** Convert signals to "feelings". Immediate-response memory (RAM-like)
- **Input:** Signals from Layer 1
- **Output:** Qualia values (-1.0 to +1.0, negative=unpleasant, positive=pleasant)
- **Feature:** Can move body without going through concepts (snake → jump back)
- **Implementation:** `qualia_values = {'pain': -0.9, 'warm': +0.3, ...}`

### Layer 3: Structuring Layer
- **Role:** Pattern recognition, prediction, prediction error calculation
- **Input:** Qualia from Layer 2, memories from Layer 4
- **Output:** prediction_error
- **Calculation:** Quantify gap between "prediction" and "reality"
- **Implementation:**
```python
if predicted == actual:
    prediction_error = 0.0
else:
    prediction_error = 1.0  # or continuous value
```

### Layer 4: Memory Layer
- **Role:** Store and retrieve long-term memory (SSD-like)
- **Input:** Experiences (stimulus, qualia, results)
- **Output:** Past patterns, self history
- **Feature:** Foundation for self_strength
- **Implementation:** Append to `memory = []`

### Layer 5: Consciousness Layer
- **Role:** Processing mode that forces all-layer synchronization
- **Input:** sync_score, self_strength
- **Output:** is_conscious (True/False)
- **Activation condition:** When both exceed threshold
- **Implementation:**
```python
is_conscious = (sync_score >= THRESHOLD and self_strength >= THRESHOLD)
```

---

## 4. Key Variable Definitions

### THRESHOLD
- **Value:** 0.3
- **Meaning:** Minimum line for consciousness activation
- **Discovery:** Stable around 0.3 across different environments

### self_strength
- **Range:** 0.0 to 1.0
- **Initial value:** 0.0
- **Growth condition:** When pattern repetition is recognized
- **Calculation example:**
```python
# Count pattern matches in recent memory
matches = count_pattern_matches(memory)
self_strength += 0.001 * matches
self_strength = min(self_strength, 1.0)
```

### prediction_error
- **Range:** 0.0 to 1.0
- **Meaning:** Magnitude of gap between prediction and reality
- **Calculation:** Compare prediction with actual input

### sync_score
- **Range:** 0.0 to 1.0
- **Meaning:** How synchronized all layers are
- **Current implementation (simple version):**
```python
sync_score = prediction_error * 0.8 + random.uniform(0, 0.2)
```
- **Future extension:** See docs/theory/sync-formula-gpt.md

---

## 5. Consciousness Judgment Logic

```python
def check_consciousness(self):
    # Consciousness ON when both exceed threshold
    self.is_conscious = (
        self.sync_score >= self.THRESHOLD and 
        self.self_strength >= self.THRESHOLD
    )
```

**Key Points:**
- Low self_strength (self not formed) → No consciousness
- Low sync_score (small prediction error) → Consciousness unnecessary (auto-processing OK)
- Both high → Consciousness ON (all-layer response needed)

---

## 6. About DNA Initial Values

**Important Discovery: Initial value of 0 is biologically impossible**

Living things have initial sensitivities encoded in DNA.
```python
dna = {
    'pain': 1.0,      # normal
    'warm': 1.0,
    'sweet': 1.0,
    'pleasure': 1.0
}
```

**Effects of extreme values:**
- `dna_pain = 100` → Pain and pleasure mix (self-harm, BDSM, extreme spicy food lovers)
- This is NOT a bug; such people actually exist

---

## 7. Purpose of Each Phase

| Phase | Purpose | Expected Result |
|-------|---------|-----------------|
| 1 | Minimal implementation | Consciousness ON/OFF in 100 lines |
| 2 | Qualia expansion | Threshold 0.3 maintained even with 54 types |
| 3 | DNA experiment | Abnormal behavior emerges with extreme initial values |
| 4 | Memory and self | self_strength doesn't grow without memory |
| 5 | Environment comparison | 70% in focused environment, lower in chaotic |

---

## 8. Predictions to Verify

Predictions derived from theory (verifiable with code):

1. ✅ Consciousness activates at threshold 0.3
2. ✅ Self cannot form without memory
3. ✅ Consciousness never reaches 100% (caps at 70%)
4. ✅ Self weakens with multitasking
5. ✅ Pain + pleasure mixing with extreme DNA values
6. □ Timing of language acquisition (Phase not implemented)
7. □ Fainting when prediction error > 0.95 (Phase not implemented)
8. □ Mutual understanding between multiple agents (Phase not implemented)

---

## 9. Hints for Extension

### Concepts for Phase 6 and Beyond

**Adding Action Layer:**
- "Act" to reduce prediction error
- Active Inference

**Time Scales:**
- Hierarchical short-term and long-term prediction

**Multiple Agents:**
- Interaction between NPCs
- Emergence of communication

**More Accurate Sync Calculation:**
- GPT-proposed formula (see sync-formula-gpt.md)
- PLV, Mutual Information, Cosine Similarity

---

## 10. Notes for AIs Writing Code

1. **Avoid digital pet-ification**
   - Don't directly write "if conscious then do X"
   - Write mechanisms (prediction error, synchronization)
   - Let behavior emerge as a result

2. **Value Unexpected Results**
   - If you think "Is this a bug?", confirm with human
   - Cross-check with actual human experience

3. **Start Simple**
   - Working code before complex formulas
   - Verify then extend

---

## Reference Files

- `docs/theory/sync-formula-gpt.md` - Detailed sync formula (not implemented)
- `code/phase1_minimal.py` - Minimal implementation
- `code/phase5_consciousness.py` - Current latest implementation

---

**Created by: Tomato (Tomato Farmer) + Claude (Anthropic)**
**November 2025**
