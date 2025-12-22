"""
test_l5_verbalize.py
L5同期検知 + 言語化テスト

行動決定: L2/L3/L4（ルールベース）
言語化: ollama or SimpleVerbalizer
L5: 橋渡しのみ
"""

from world import World
from hida import Hida
from qualia import QualiaLayer
from l5_sync import L5Sync, calculate_l2_activity, calculate_l3_activity, calculate_l4_activity
from verbalizer import Verbalizer, SimpleVerbalizer

def create_test_world():
    """テスト用の世界"""
    world = World(size=10)
    
    # 外壁
    for i in range(10):
        world.add_wall(i, 0)
        world.add_wall(i, 9)
        world.add_wall(0, i)
        world.add_wall(9, i)
    
    # 危険ゾーン
    for x in range(5, 8):
        for y in range(3, 6):
            world.add_danger(x, y)
    
    # ボール
    world.add_object("ball", 6, 4, color="red")   # 危険ゾーン内
    world.add_object("ball", 2, 5, color="blue")  # 安全
    
    # ゴール
    world.add_object("goal", 7, 7, color=None)
    
    # HIDA
    world.hida_pos = [3, 3]
    world.hida_dir = 'S'
    
    return world


def run_with_verbalization(use_ollama=False):
    """L5同期 + 言語化付きで実行"""
    
    world = create_test_world()
    hida = Hida()
    
    # 赤好きに設定
    hida.l2 = QualiaLayer(color_preference={'red': 1.0, 'blue': 0.3, 'green': 0.3})
    
    hida.pos = world.hida_pos.copy()
    hida.direction = world.hida_dir
    hida.seen_this_session = set()
    
    # L5とVerbalizer
    l5 = L5Sync(threshold=0.5)  # 閾値を下げた
    if use_ollama:
        verbalizer = Verbalizer()
        if not verbalizer.available:
            print("⚠️ ollama未接続、SimpleVerbalizerを使用")
            verbalizer = SimpleVerbalizer()
    else:
        verbalizer = SimpleVerbalizer()
    
    print("=== L5同期 + 言語化テスト ===")
    print("赤好きのHIDAが探索")
    print("L5は判断せず、同期検知と橋渡しのみ")
    print()
    world.display()
    
    max_steps = 50
    last_words = ""
    
    for step in range(max_steps):
        # === L2/L3/L4が状態を更新 ===
        prediction_errors = []
        
        # 周りを見る（L3が予測誤差を検出）
        old_found = set(hida.found_objects.keys())
        hida.look_around_and_remember(world)
        new_found = set(hida.found_objects.keys()) - old_found
        
        for pos in new_found:
            prediction_errors.append({'pos': pos, 'type': 'new_object'})
        
        # === 各層の活動度を計算 ===
        l2_act = calculate_l2_activity(hida.l2.qualia)
        l3_act = calculate_l3_activity(prediction_errors)
        l4_act = calculate_l4_activity(hida.found_objects, hida.internal_map)
        
        # === L5: 同期チェック ===
        is_conscious = l5.check_sync(l2_act, l3_act, l4_act)
        
        # デバッグ: 最初の5ステップは活動度を表示
        if step < 5:
            print(f"  Step {step}: L2={l2_act:.2f} L3={l3_act:.2f} L4={l4_act:.2f} → {'ON' if is_conscious else 'off'}")
        
        # === 行動決定（L2/L3/L4が行う、L5は関与しない） ===
        q = hida.l2.qualia
        
        # ターゲット選択（クオリア状態から計算）
        target = None
        target_color = None
        action_desc = "explore"
        
        balls = {obj['color']: pos for pos, obj in hida.found_objects.items() 
                 if obj.get('name') == 'ball'}
        
        if balls and not hida.holding:
            scores = {}
            for color, pos in balls.items():
                dist = abs(pos[0] - hida.pos[0]) + abs(pos[1] - hida.pos[1])
                is_danger = hida.internal_map.get(pos) == 'danger'
                danger_cost = 10 if is_danger else 0
                preference = hida.l2.get_color_desire(color)
                
                # スコア計算（L2/L3/L4の状態から自然に決まる）
                score = preference * 10 - dist * 0.5 - (q['fear'] * danger_cost)
                scores[color] = score
            
            target_color = max(scores, key=scores.get)
            target = balls[target_color]
            action_desc = f"go_to_{target_color}"
        
        # === L5: 意識的なら言語化 ===
        if is_conscious:
            state = l5.get_state_for_verbalization(
                hida.l2,
                prediction_errors,
                list(hida.internal_map.keys())[-5:],  # 最近の記憶
                action_desc,
                hida.found_objects
            )
            
            words = verbalizer.verbalize(state)
            
            if words != last_words:
                print(f"\n  Step {step} [意識ON] L2={l2_act:.2f} L3={l3_act:.2f} L4={l4_act:.2f}")
                print(f"    fear={q['fear']:.2f}, desire={q['desire']:.2f}")
                print(f"    行動: {action_desc}")
                print(f"    💭 「{words}」")
                last_words = words
        
        # === 行動実行 ===
        if target:
            path = hida.find_path(target)
            if path and len(path) >= 2:
                hx, hy = hida.pos
                next_pos = path[1]
                dx = next_pos[0] - hx
                dy = next_pos[1] - hy
                
                if dx > 0: target_dir = 'E'
                elif dx < 0: target_dir = 'W'
                elif dy > 0: target_dir = 'S'
                else: target_dir = 'N'
                
                if hida.direction != target_dir:
                    dirs = ['N', 'E', 'S', 'W']
                    ci = dirs.index(hida.direction)
                    ti = dirs.index(target_dir)
                    diff = (ti - ci) % 4
                    if diff == 1 or diff == 2:
                        world.turn_right()
                    else:
                        world.turn_left()
                    hida.update_pos(world)
                else:
                    success, _ = world.move_forward()
                    if success:
                        hida.update_pos(world)
        else:
            # 探索
            import random
            action = random.choice(['forward', 'left', 'right'])
            if action == 'forward':
                success, _ = world.move_forward()
                if success:
                    hida.update_pos(world)
            elif action == 'left':
                world.turn_left()
                hida.update_pos(world)
            else:
                world.turn_right()
                hida.update_pos(world)
        
        # ボール取得チェック
        front = world.get_front_pos()
        if tuple(front) in world.objects:
            obj = world.objects[tuple(front)]
            if obj.get('name') == 'ball' and not hida.holding:
                color = obj.get('color')
                
                # 取得時の言語化
                grab_words = verbalizer.verbalize_grab(color, q['fear']) if hasattr(verbalizer, 'verbalize_grab') else f"{color}を取った"
                print(f"\n  🎉 {grab_words}")
                
                world.grab()
                hida.holding = world.hida_holding
                break
    
    # 同期履歴の統計
    conscious_count = sum(1 for h in l5.sync_history if h['conscious'])
    print(f"\n=== 統計 ===")
    print(f"  総ステップ: {len(l5.sync_history)}")
    print(f"  意識ON: {conscious_count}回 ({100*conscious_count/len(l5.sync_history):.0f}%)")


def main():
    print("【SimpleVerbalizer版】")
    run_with_verbalization(use_ollama=False)
    
    print("\n" + "=" * 60)
    print("\n【ollama版】")
    run_with_verbalization(use_ollama=True)


if __name__ == "__main__":
    main()
