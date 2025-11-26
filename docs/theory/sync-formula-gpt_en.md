# Four-Layer Synchronization Quantification: Detailed Formula (GPT Proposal)

**Status: Not Implemented (Proposal Stage)**

Current Phase 5 uses a simple formula.
This document is a reference for those who want to implement more accurate sync calculation.

---

## Current Implementation (Simple Version)

```python
sync_score = prediction_error * 0.8 + random.uniform(0, 0.2)
```

Emergent behaviors like 70% intermittency have been confirmed with this simple formula.

---

## GPT Proposal: Four-Layer Sync Score S

### Basic Formula

```
S = w1 * PLV + w2 * MI + w3 * Corr
```

### Three Components

#### 1. PLV (Phase Locking Value) - Timing Synchronization
Whether signals from four layers respond within the same time window Δt.

- **1:** Perfect sync
- **0:** Unrelated
- **Time window:** 20-50ms (biological), arbitrary (AI)

#### 2. MI (Mutual Information) - Information Sharing
How much information content is shared among body signals, qualia vectors, structuring vectors, and memory matching.

- **High MI:** Same event interpreted in the same direction
- **Low MI:** Each layer's "world" is misaligned

#### 3. Corr (Correlation) - Directionality
Alignment of vector directions across Qualia → Structuring → Memory.
Use Pearson correlation coefficient or cosine similarity.

- **High correlation:** Four layers heading toward same judgment
- **Low correlation:** Conflict, confusion, automatic processing

### Recommended Weights

```python
w1 = 0.4  # Timing
w2 = 0.3  # Information
w3 = 0.3  # Directionality
```

---

## Threshold Interpretation

| Score | State |
|-------|-------|
| S > 0.85 | Strong consciousness ("I am doing this") |
| S > 0.70 | Consciousness frame established |
| S 0.5–0.7 | Semi-sync (attention lowered) |
| S < 0.5 | Unconscious / automatic processing |

---

## Requirements for Implementation

To implement this formula, each layer's output must be clearly defined:

```python
class Layer1_Body:
    def get_signal(self) -> float:
        pass

class Layer2_Qualia:
    def get_vector(self) -> np.array:
        pass

class Layer3_Structure:
    def get_vector(self) -> np.array:
        pass

class Layer4_Memory:
    def get_vector(self) -> np.array:
        pass
```

### PLV Calculation Example (Conceptual)

```python
import numpy as np

def calculate_plv(signals, time_window=0.05):
    """
    signals: Time series signals from each layer [layer1, layer2, layer3, layer4]
    time_window: Time window for sync judgment (seconds)
    """
    # Calculate phase of each signal (e.g., Hilbert transform)
    phases = [hilbert_phase(s) for s in signals]
    
    # Calculate phase difference consistency
    phase_diffs = []
    for i in range(len(phases)):
        for j in range(i+1, len(phases)):
            diff = phases[i] - phases[j]
            phase_diffs.append(np.exp(1j * diff))
    
    # PLV = absolute value of mean phase difference vector
    plv = np.abs(np.mean(phase_diffs))
    return plv
```

### Mutual Information Calculation Example (Conceptual)

```python
from sklearn.metrics import mutual_info_score

def calculate_mi(vector1, vector2):
    """
    Mutual information between two vectors
    """
    # Discretization required
    v1_discrete = discretize(vector1)
    v2_discrete = discretize(vector2)
    return mutual_info_score(v1_discrete, v2_discrete)
```

### Cosine Similarity Calculation Example

```python
def cosine_similarity(v1, v2):
    dot = np.dot(v1, v2)
    norm = np.linalg.norm(v1) * np.linalg.norm(v2)
    return dot / norm if norm > 0 else 0
```

---

## Conditions Satisfied by This Model

- Reproduces consciousness = momentary blinking coherence
- Clearly determines whether four layers handle same information
- Measurable judgment unification
- Implementable (signal processing, statistics, vector calculation only)
- Connectable to self_strength and action loops

---

## Caution

This formula may be more "accurate" but increases complexity.

Major emergent phenomena (70% intermittency, etc.) have been confirmed with the simple version.

**Recommendation:**
1. First run with simple version
2. Replace with this formula if needed
3. Verify if results change

---

**Proposed by:** GPT
**Documented by:** Claude
**November 2025**
