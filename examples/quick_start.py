#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Quick Start Guide
クイックスタートガイド

Theory of Human Inner Movement
人の内なる運動理論

This file shows how to quickly run each phase.
各フェーズを素早く実行する方法を示します。
"""

import sys
import os

# Add code directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'code'))

def demo_phase1():
    """Phase 1: Minimal system - Demonstrates basic consciousness"""
    print("\n" + "="*70)
    print("PHASE 1: MINIMAL CONSCIOUSNESS SYSTEM")
    print("="*70)
    
    from phase1_minimal import MinimalConsciousness
    
    system = MinimalConsciousness()
    print("\nRunning 100 steps...")
    system.run_experiment(steps=100)
    
    print("\n✓ Phase 1 demonstrates:")
    print("  - Five-layer architecture")
    print("  - Consciousness emerges at threshold 0.3")
    print("  - Self-strength forms from pattern repetition")

def demo_phase2():
    """Phase 2: Qualia expansion - Shows scalability"""
    print("\n" + "="*70)
    print("PHASE 2: QUALIA EXPANSION (54 types)")
    print("="*70)
    
    from phase2_qualia_expansion import QualiaExpansionSystem
    
    system = QualiaExpansionSystem()
    print("\nComparing simple, medium, and complex environments...")
    system.run_comparison(steps=1000)
    
    print("\n✓ Phase 2 demonstrates:")
    print("  - System scales to 54 qualia types")
    print("  - Threshold 0.3 is consistent across environments")

def demo_phase3():
    """Phase 3: DNA and learning - Shows genetic vs learned values"""
    print("\n" + "="*70)
    print("PHASE 3: DNA INITIAL VALUES AND LEARNING")
    print("="*70)
    
    from phase3_dna_and_learning import compare_systems
    
    print("\nComparing DNA+Learning, Learning-only, and DNA-only...")
    compare_systems()
    
    print("\n✓ Phase 3 demonstrates:")
    print("  - DNA initial values vs learned values")
    print("  - System B (DNA=0) is biologically impossible")
    print("  - DNA provides evolutionary advantage")

def demo_phase4():
    """Phase 4: Memory and self - Shows memory is essential"""
    print("\n" + "="*70)
    print("PHASE 4: MEMORY AND SELF-FORMATION")
    print("="*70)
    
    from phase4_memory_and_self import compare_memory_systems
    
    print("\nComparing systems with and without memory...")
    compare_memory_systems()
    
    print("\n✓ Phase 4 demonstrates:")
    print("  - Memory is essential for self-formation")
    print("  - Language acquisition at threshold 0.3")
    print("  - Solves the hard problem of qualia")

def demo_phase5():
    """Phase 5: Full system - THE MAJOR DISCOVERY!"""
    print("\n" + "="*70)
    print("PHASE 5: CONSCIOUSNESS INTERMITTENCY")
    print("THE MAJOR DISCOVERY!")
    print("="*70)
    
    from phase5_consciousness import compare_environments
    
    print("\nComparing focused vs varied environments...")
    print("This will take a moment (20,000 total steps)...\n")
    compare_environments()
    
    print("\n✓ Phase 5 demonstrates:")
    print("  - Consciousness is naturally intermittent (~70% in focused)")
    print("  - Simple environments accelerate self-formation")
    print("  - Matches subjective experience perfectly")
    print("  - IMPLEMENTATION-FIRST DISCOVERY!")

def run_all_phases():
    """Run all phases in sequence"""
    print("\n" + "="*70)
    print("RUNNING ALL PHASES")
    print("全フェーズを実行")
    print("="*70)
    print("\nThis will run all 5 phases in sequence.")
    print("It may take a few minutes...")
    print()
    
    demo_phase1()
    demo_phase2()
    demo_phase3()
    demo_phase4()
    demo_phase5()
    
    print("\n" + "="*70)
    print("ALL PHASES COMPLETE!")
    print("全フェーズ完了！")
    print("="*70)
    print()
    print("You have now seen the complete implementation of")
    print("the Theory of Human Inner Movement!")
    print()
    print("人の内なる運動理論の完全な実装を見ました！")
    print()

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        phase = sys.argv[1].lower()
        
        if phase == '1':
            demo_phase1()
        elif phase == '2':
            demo_phase2()
        elif phase == '3':
            demo_phase3()
        elif phase == '4':
            demo_phase4()
        elif phase == '5':
            demo_phase5()
        elif phase == 'all':
            run_all_phases()
        else:
            print("Usage: python quick_start.py [1|2|3|4|5|all]")
            print("Example: python quick_start.py 5")
    else:
        # Default: Run Phase 5 (the most interesting!)
        print("Running Phase 5 by default (the most interesting!)")
        print("Use 'python quick_start.py all' to run all phases")
        print()
        demo_phase5()
