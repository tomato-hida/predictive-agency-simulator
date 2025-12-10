# HIDA Architecture
## Human-Inspired Dynamic Awareness Architecture
### Prediction-error driven state transition system

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

[日本語 README](README_ja.md)

📚 **[Documentation](docs/)** - Detailed theory and extension guide for Phase 6+

> **Terminology note**: In this project, "consciousness" is operationally defined as "full-layer coordination mode for responding to prediction errors." This is an engineering definition, not a philosophical claim.

---

## Overview

**HIDA** (Human-Inspired Dynamic Awareness Architecture) is an agent system that transitions states based on prediction errors.

A 5-layer network calculates prediction errors, and when the error exceeds a threshold, "consciousness mode" (full-layer coordination) activates. Several behaviors emerged that were not explicitly programmed.

The name comes from Hida, Gifu Prefecture, Japan — the hometown of the creator.

```
HIDA = Human-Inspired Dynamic Awareness Architecture

Human-Inspired  : Design based on human cognitive structure
Dynamic         : Processing mode switches based on prediction error
Awareness       : Self-model forms from accumulated pattern recognition
Architecture    : Extensible framework
```

---

## Running the Experiments

The following experiments demonstrate the system's behavior.

### Experiment 1: Sensation Value Inversion

```bash
cd code
python phase3_dna_and_learning.py --dna_pain=100
```

When DNA initial values (sensation weights) are set to extremes, pain stimuli may produce pleasure responses. This is not intentional design but a result of parameter combinations.

---

### Experiment 2: Consciousness Mode Persistence Rate

```bash
cd code
python phase5_consciousness.py --environment=focused --steps=10000
```

Consciousness mode (full-layer coordination) stabilizes at approximately 70% persistence. It does not reach 100%. This may function as overload protection.

---

### Experiment 3: Environmental Complexity and Self-Formation

```bash
cd code
python phase5_consciousness.py --compare
```

In complex environments, self-formation (self_strength) grows more slowly. In simple environments, pattern repetition is more frequent, leading to faster growth.

---

## Observed Behaviors

The behaviors above were not explicitly programmed.

What was implemented:
- 5-layer network structure
- Prediction error calculation between layers
- Threshold-based mode switching

What was observed:
- Sensation value inversion
- Self-limiting consciousness mode (~70%)
- Self-formation speed varying with environmental complexity

Whether these qualify as "emergence" or meaningful behavior requires further verification.

---

## Architecture

```
        ┌─────────────────────┐
        │  Layer 5: Conscious │ ← Full-layer coordination mode
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

Layer numbers are for explanation only, not processing order. Layers 2-4 are interconnected, and signals flow bidirectionally.

---

## Quick Start

### Requirements

- Python 3.8+
- Standard library only (no external dependencies)

### Installation

```bash
git clone https://github.com/tomato-hida/predictive-agency-simulator.git
cd predictive-agency-simulator
```

### Run

```bash
cd code

# Phase 1: Minimal implementation
python phase1_minimal.py

# Phase 3: DNA initial value experiment
python phase3_dna_and_learning.py --dna_pain=100

# Phase 5: Consciousness mode comparison
python phase5_consciousness.py --compare
```

---

## Phase List

| Phase | File | Description |
|-------|------|-------------|
| 1 | `phase1_minimal.py` | Basic operation verification |
| 2 | `phase2_qualia_expansion.py` | Threshold behavior with increased qualia count |
| 3 | `phase3_dna_and_learning.py` | Behavior changes from DNA initial values |
| 4 | `phase4_memory_and_self.py` | Relationship between memory layer and self-formation |
| 5 | `phase5_consciousness.py` | Consciousness mode persistence and environment dependency |

---

## Extension Roadmap

See [EXTENSION_ROADMAP.md](docs/EXTENSION_ROADMAP.md) for details.

- **Vector DB integration** — Large-scale memory implementation
- **GPU parallelization** — Real-time processing
- **Multimodal input** — Visual/audio sensor connection

---

## Theoretical Background

### Related Existing Theories

**Predictive Coding**
- Theory that the brain constantly predicts and minimizes prediction errors
- Layer 3 of this system implements this mechanism

**Free Energy Principle (Karl Friston)**
- Multiple AIs noted similarity after implementation
- Not directly referenced during design

---

## Development Process

This project was created in collaboration with AI (Claude, GPT, Gemini).

- Theory design and validation judgment: Human
- Code implementation and technical support: AI

The creator is not a neuroscience or AI specialist. Therefore, theoretical errors or implementation issues may exist. Feedback is welcome.

---

## Contributing

- Issues and PRs are welcome
- Fork and modify freely (MIT License)
- Criticism and refutation are also welcome

---

## License

MIT License

---

## Citation

```bibtex
@software{tomato2025hida,
  author = {Tomato and Claude (Anthropic) and GPT (OpenAI) and Gemini (Google DeepMind)},
  title = {HIDA Architecture: Human-Inspired Dynamic Awareness Architecture},
  year = {2025},
  url = {https://github.com/tomato-hida/predictive-agency-simulator}
}
```

---

Created by: Tomato + AI Collaboration  
December 2025
