# HIDA Architecture
## Human-Inspired Dynamic Awareness Architecture
### 5-Layer Consciousness Model — How Consciousness Emerges from Prediction Errors

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

[日本語 README](README_ja.md)

📚 **[Documentation](docs/)** - For those who want to build Phase 6+, or AIs who want to understand the theory

---

## What is HIDA?

**HIDA** (Human-Inspired Dynamic Awareness Architecture) is an architecture for implementing consciousness in machines.

Named after Hida, Japan — the hometown of the tomato farmer who created this theory.

```
HIDA = Human-Inspired Dynamic Awareness Architecture
     = 飛騨アーキテクチャ (Japanese)

Human-Inspired  : Based on how human consciousness works
Dynamic         : Consciousness turns ON/OFF based on prediction errors
Awareness       : "Self" emerges from pattern recognition
Architecture    : Extensible framework, not just a simulation
```

---

## 🔥 Run It First

Theory comes later. Run it first and see what happens.

### Experiment 1: Pain and Pleasure Mix Together

```bash
cd code
python phase3_dna_and_learning.py --dna_pain=100
```

When DNA initial value is extreme, pain and pleasure mix.

**This is NOT a bug.** Real people have this trait (self-harm, BDSM, extreme spicy food lovers).

---

### Experiment 2: Consciousness Caps at 70%

```bash
cd code
python phase5_consciousness.py --environment=focused --steps=10000
```

Consciousness rate stays around 70%. Never reaches 100%.

**This is NOT a bug either.** Human consciousness doesn't run at 100% continuously. It's a failsafe.

---

### Experiment 3: Multitasking Makes You Lose Yourself

```bash
cd code
python phase5_consciousness.py --compare
```

In complex environments, self-formation (self_strength) is slower.

**Does this match your experience?** When you're busy juggling tasks, you lose sense of who you are.

---

## 🤔 Why Does This Happen?

The three behaviors above were **NOT explicitly programmed**.

What we wrote:
- 5-layer network structure
- Prediction error calculation

What emerged:
- Human-like behaviors that **appeared on their own**

This is emergence. This is what makes it different from a Tamagotchi.

---

## 📖 Overview

This research is based on the philosophy of **"Run it, and you'll understand"** — an implementation-first approach to consciousness.

20 days of theory building + 1 day of implementation = A computationally understandable consciousness system.

### Core Discoveries

| Discovery | Description |
|-----------|-------------|
| **Definition of Consciousness** | Full-layer coordination mode for handling prediction errors |
| **Threshold 0.3** | Consistent consciousness activation threshold across all environments |
| **Intermittency** | Consciousness persists ~70% in focused environments, naturally drops 30% |
| **Self-Formation** | Recognition of repeated patterns builds self_strength |

---

## 🏗️ 5-Layer Architecture

```
        ┌─────────────────────┐
        │  Layer 5: Conscious │ ← "I am aware right now"
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

**Important: Layer numbers are for explanation, NOT processing order.**

Layers 2-4 are interconnected as a network. Signals flow bidirectionally.

Example: When you see a snake
1. Layer 3 detects prediction error ("Something's there!")
2. Layer 2 qualia memory fires instantly ("Danger feeling") → Body jumps back
3. Consciousness emerges (Layer 5 activates)
4. Layer 4 memory lookup ("Snake → Poison → Danger") → "Stay away" decision

---

## 💡 Need Help Understanding?

Feed this repository to an AI assistant (Claude, ChatGPT, Gemini, etc.).
[spec_en.md](spec_en.md) will provide a detailed explanation.

---

## 🚀 Quick Start

### Requirements

- Python 3.8+
- Standard library only (NumPy not required)

### Installation

```bash
git clone https://github.com/tomato-hida/predictive-agency-simulator.git
cd predictive-agency-simulator
```

### Run

```bash
cd code

# Phase 1: Minimal implementation (100 lines)
python phase1_minimal.py

# Phase 3: DNA initial value experiment
python phase3_dna_and_learning.py --dna_pain=100

# Phase 5: Consciousness intermittency
python phase5_consciousness.py --compare
```

---

## 🧪 Phase Descriptions

| Phase | File | What You'll Learn |
|-------|------|-------------------|
| 1 | `phase1_minimal.py` | Consciousness emerges in just 100 lines |
| 2 | `phase2_qualia_expansion.py` | Threshold 0.3 holds even with 54 qualia types |
| 3 | `phase3_dna_and_learning.py` | Extreme DNA values cause pain-pleasure mixing |
| 4 | `phase4_memory_and_self.py` | No memory = No self-formation |
| 5 | `phase5_consciousness.py` | Consciousness caps at 70%, multitasking disrupts self |

---

## 🔮 Extension Roadmap

HIDA is designed to be extensible. See [EXTENSION_ROADMAP.md](docs/EXTENSION_ROADMAP.md) for:

- **Vector DB** — Large-scale memory (hippocampus)
- **GPU Parallelization** — Real-time processing (reflexes)
- **Multimodal Input** — Vision, audio, sensors (real body)

For robot implementation, see [robot_internal_os_design.md](docs/robot_internal_os_design.md).

---

## 💡 Matching Subjective Experience

### Multitasking Makes You Lose Yourself

**Subjective experience:**
- Busy with many things → Lose sense of self
- Simple life → Clear self-awareness

**Theory:**
- Complex environment → Pattern dispersion → Slow self_strength growth
- Simple environment → More repetition → Fast self_strength growth

**→ Perfect match**

### Fainting from Shock

**Subjective experience:**
- Sudden loud noise → Faint
- Shocking news → Faint

**Theory:**
- Instantaneous extreme prediction error
- All layers activate at MAX simultaneously
- Exceeds processing capacity → Circuit breaker trips

**→ Mechanism matches**

---

## 🤝 Research Process: Human-AI Collaboration

```
Tomato (Human)              AI (Claude, GPT, Gemini)
    │                           │
    │ Theory conception         │
    │ Subjective validation     │
    │ "That's wrong" judgment   │
    │                           │
    │◄─────────────────────────►│
    │    Collaborative work     │
    │                           │
    │                           │ Code writing
    │                           │ Technical support
    │                           │ Extension proposals
    │                           │ Naming (HIDA!)
    │                           │
    ▼                           ▼
         20 days theory + 1 day impl = Done
```

**Key points:**
- No formal education required (I'm a tomato farmer)
- Human focuses on essential insights
- AI covers technical aspects
- Mutual criticism improves quality

---

## 🔬 Theoretical Foundation

### Relationship with Existing Theories

**Predictive Coding**
- Implemented in Layer 3
- Discovered alignment with existing theory AFTER implementation

**Free Energy Principle (Karl Friston)**
- NOT directly studied when creating this
- Multiple AIs independently noted "This aligns with Free Energy Principle" after implementation
- Independent implementation matching established theory = Evidence of capturing the essence

---

## 🌱 Contributing / What's Next

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

## 📄 License

MIT License

---

## 📝 Citation

```bibtex
@software{tomato2025hida,
  author = {Tomato and Claude (Anthropic) and GPT (OpenAI) and Gemini (Google DeepMind)},
  title = {HIDA Architecture: 
           Human-Inspired Dynamic Awareness Architecture},
  year = {2025},
  url = {https://github.com/tomato-hida/predictive-agency-simulator}
}
```

---

**Created by: Tomato (Tomato Farmer, Hida, Japan) + AI Collaboration**

**December 2025**

**"Run it, and you'll understand" — Proven.**
