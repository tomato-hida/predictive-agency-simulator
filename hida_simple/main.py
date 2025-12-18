"""
main.py
シンプル版 - 記憶だけ
"""

import sys
import time
from simple_world import SimpleWorld
from hida_state import HidaState
from ai_brain import AIBrain


def setup_world():
    """6x6 壁ありマップ"""
    world = SimpleWorld(size=6)
    world.add_object("red_ball", 2, 0, {"color": "red"})
    world.add_object("goal", 5, 5, {"type": "destination"})
    
    # 壁
    world.add_object("wall_3_1", 3, 1, {"type": "wall"})
    world.add_object("wall_5_3", 5, 3, {"type": "wall"})
    world.add_object("wall_5_4", 5, 4, {"type": "wall"})
    
    world.hida_pos = [3, 3]
    return world


def run(max_steps=50):
    """シミュレーション実行"""
    world = setup_world()
    state = HidaState()
    brain = AIBrain()
    
    state.set_goal("red ballをgoalに届ける")
    state.update_from_world(world)
    
    print("=== シンプル版：記憶だけ ===")
    print(f"目標: {state.goal}")
    print(f"教え: {len(state.teachings)}件")
    world.display()
    
    for step in range(max_steps):
        print(f"\n--- Step {step + 1} ---")
        
        # 行動決定
        action, reason = brain.decide_action(state, world)
        print(f"行動: {action}")
        print(f"理由: {reason}")
        
        # 実行
        if action != 'wait':
            success, message = world.execute_primitive(action)
            print(f"結果: {'成功' if success else '失敗'} - {message}")
        else:
            success, message = True, "待機"
            print("待機")
        
        # 状態更新
        state.update_from_world(world)
        state.record_result(action, success, message)
        
        world.display()
        
        # 目標達成チェック
        if "at goal!" in message:
            print(f"\n🎉 目標達成！ Step {step + 1}")
            break
        
        time.sleep(0.3)
    
    state.save_memory()
    
    # 統計
    results = list(state.recent_results)
    success_count = sum(1 for r in results if r['success'])
    print(f"\n成功率: {success_count}/{len(results)}")


def teach():
    """教えを追加"""
    state = HidaState()
    print("\n📖 教える")
    print("=" * 30)
    condition = input("条件: ").strip()
    action = input("行動: ").strip()
    source = input("教師: ").strip() or "human"
    
    if condition and action:
        state.add_teaching(condition, action, source)
    else:
        print("❌ 条件と行動は必須")


def show_teachings():
    """教え一覧"""
    state = HidaState()
    print("\n📚 教え一覧")
    print("=" * 30)
    if state.teachings:
        for i, t in enumerate(state.teachings):
            print(f"{i+1}. 「{t['condition']}」→「{t['action']}」({t['source']})")
    else:
        print("まだ教えなし")


if __name__ == "__main__":
    args = sys.argv[1:]
    
    if "teach" in args:
        teach()
    elif "teachings" in args:
        show_teachings()
    elif "reset" in args:
        import os
        if os.path.exists("hida_memory.json"):
            os.remove("hida_memory.json")
            print("🗑️ 記憶をリセット")
    else:
        run()
