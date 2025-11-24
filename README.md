Markdown

# Predictive Agency Simulator
### (Formerly: Theory of Human Inner Movement)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

**Python implementation of a self-organizing agent based on Predictive Coding and the Free Energy Principle.**

[Japanese README / 日本語ドキュメント](README_ja.md)

---

## 📖 Overview

This project is an experimental implementation designed to verify whether **"Agency" and "Consciousness Intermittency" emerge from the process of minimizing prediction error**, rather than through a top-down design of consciousness.

In a simulation using a 5-layer architecture with just a few hundred lines of Python code, we observed **"Intermittency," where the agent's meta-cognitive function naturally toggles ON and OFF depending on environmental complexity** (operating at approx. 70% in focused states).

This behavior mathematically aligns with human subjective experiences such as "flow states" or "confusion during multitasking."

## 🧪 Key Findings

Results from 60,000 steps of verification in the simulator (Phase 5):

### 1. Emergence of Intermittent Consciousness
* **Focused Environment:** The agent activated its higher-order layer (Consciousness) **70.6%** of the time, leaving the remaining 30% to automatic processing. This aligns with biological mechanisms of "habituation" and energy conservation.
* **Varied Environment:** This activation rate dropped to **40.0%**, demonstrating how excessive prediction errors inhibit self-formation.

### 2. Universality of the Threshold
Across environments ranging from simple to complex multi-dimensional qualia, a consistent `Sync Score` threshold of **approx. 0.3** was observed for stable self-organization.

### 3. Dynamic Self-Boundary
Through the interaction of Memory and Prediction, the agent dynamically learns the boundary between "Self" (controllable region) and "Environment" (uncontrollable region) based on external stimulus patterns.

## 🏗️ Architecture

The system adopts a 5-layer structure that (posteriorly) aligns with Friston's Free Energy Principle and Predictive Coding theory.

graph TD
    L5[Layer 5: Consciousness (Global Workspace)] -->|Top-down| L4
    L4[Layer 4: Memory & Self-Model] -->|Prediction| L3
    L3[Layer 3: Predictive Coding (Error Detection)] -->|Error Signal| L4
    L3 -->|Sensory Prediction| L2
    L2[Layer 2: Qualia Processing] -->|Raw Data| L3
    L1[Layer 1: Body / Sensor Inputs] -->|Stimulus| L2
Layer 3 (Structuring): Calculates Prediction Error.

Layer 4 (Self-Model): Updates the internal model (World Model) based on error feedback.

Layer 5 (Meta-Cognition): Monitors the synchronization level (Sync Score) between prediction error and self-consistency, triggering "Consciousness Mode" only under specific conditions.

🚀 Quick Start
Minimal Implementation
The core logic of self-formation via predictive coding is implemented in just 100 lines.

Python

from code.phase1_minimal import MinimalConsciousness

# Initialize Agent
system = MinimalConsciousness()

# Run 100 steps simulation
for step in range(100):
    result = system.process_step()
    
    if result['is_conscious']:
        print(f"Step {step}: Agency Activated! (Sync: {result['sync_score']:.3f})")
Full Simulation (Phase 5)
Code to verify the intermittency of consciousness.

Python

from code.phase5_consciousness import ConsciousnessSystem

system = ConsciousnessSystem()
# Experiment in a Focused Environment
results = system.run_experiment(steps=10000, environment='focused')
🤝 Background: Implementation-First Approach
This project was not developed by a specialized AI research institute but through a collaborative dialogue between a tomato farmer with an "Implementation-First" philosophy and multiple LLMs (Claude, Gemini, GPT).

Instead of starting with theory, we piled up implementation requirements based on "how the system should behave in response to prediction errors." The fact that the resulting code showed high consistency with modern neuroscience theories (such as the Free Energy Principle) is a notable achievement of this project.

For more details on the history and theoretical background, please refer to the docs folder.


## 🧬 Architectural Philosophy: Why this is NOT a "Tamagotchi"

At first glance, this system might look like a simple rule-based character (a "Tamagotchi"). However, there is a fundamental difference in design philosophy: this system implements **"Dynamics," not "Rules."**

### 1. Process over Result
* **Scripted (Tamagotchi):** Directly codes the result, e.g., `if hungry then cry`.
* **Emergent (This System):** Only codes the mechanism, e.g., `if prediction_error > threshold then update_model`. "Consciousness" or "Agency" are not explicitly programmed but **emerge** as byproducts of the process of minimizing prediction error.

### 2. The "Self" is a Dynamic Equilibrium, not a Constant
* **Static Self:** In typical programs, the agent exists unconditionally.
* **Dynamic Self:** In this system, `self_strength` is not a fixed constant. It is a **dynamic equilibrium** maintained only through successful prediction of the environment. If the environment becomes too chaotic, the self collapses (`self_strength ≈ 0`), representing a mathematical state of "panic" or "loss of agency."

### 3. Error as Energy
* **Error as Failure:** Usually, errors are bad states to be avoided.
* **Error as Trigger:** This system uses prediction error (surprise) as a **trigger/fuel to activate consciousness**. It naturally reproduces biological resource management: saving energy with automatic processing (Zombie Mode) during calm times, and allocating full computational resources (Consciousness Awakening) only when facing unexpected events.

* 
📄 License
MIT License

Copyright (c) 2025 Tomato Farmer Theorist
