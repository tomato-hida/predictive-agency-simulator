"""
test_explore_with_preference.py
探索しながらクオリアの状態変化で行動が決まる
→ L5が「判断する主体」ではなく「状態の結果」

赤好きのHIDAが3色のボールを探索
"""

from world import World
from hida import Hida
from qualia import QualiaLayer

def create_3color_world():
    """3色ボールの世界"""
    world = World(size=10)
    
    # 外壁
    for i in range(10):
        world.add_wall(i, 0)
        world.add_wall(i, 9)
        world.add_wall(0, i)
        world.add_wall(9, i)
    
    # 危険ゾーン（右側）
    for x in range(5, 9):
        for y in range(2, 6):
            world.add_danger(x, y)
    
    # 3色ボール
    world.add_object("ball", 6, 4, color="red")    # 危険ゾーン内
    world.add_object("ball", 2, 5, color="blue")   # 安全、手前
    world.add_object("ball", 2, 7, color="green")  # 安全、奥
    
    # ゴール
    world.add_object("goal", 7, 7, color=None)
    
    # HIDA初期位置
    world.hida_pos = [2, 2]
    world.hida_dir = 'S'
    
    return world


def run_exploration(color_pref, verbose=True):
    """探索実行"""
    world = create_3color_world()
    hida = Hida()
    
    # 色好みを設定
    hida.l2 = QualiaLayer(color_preference=color_pref)
    
    hida.pos = world.hida_pos.copy()
    hida.direction = world.hida_dir
    hida.seen_this_session = set()
    
    if verbose:
        pref_str = ", ".join([f"{c}={v}" for c, v in color_pref.items()])
        print(f"\n=== 色好み: {pref_str} ===")
        world.display()
    
    grabbed_order = []  # 取った順番
    max_steps = 200
    
    for step in range(max_steps):
        # 周りを見て記憶（クオリアも更新される）
        hida.look_around_and_remember(world)
        
        q = hida.l2.qualia
        
        # 発見したボールを確認
        balls = {}
        for pos, obj in hida.found_objects.items():
            if obj.get('name') == 'ball':
                color = obj.get('color')
                balls[color] = pos
        
        # ターゲット選択（クオリア状態から自然に決まる）
        target = None
        target_color = None
        
        if balls and not hida.holding:
            # 候補をスコアリング（主体的判断ではなく、状態からの計算）
            scores = {}
            for color, pos in balls.items():
                # 距離
                dist = abs(pos[0] - hida.pos[0]) + abs(pos[1] - hida.pos[1])
                
                # 危険度（危険ゾーン内なら高い）
                is_danger = hida.internal_map.get(pos) == 'danger'
                danger_cost = 10 if is_danger else 0
                
                # 色好み
                preference = hida.l2.get_color_desire(color)
                
                # スコア = 好み - 距離コスト - (fear × 危険コスト)
                # fearが高いと危険ゾーンのコストが大きくなる
                score = preference * 10 - dist * 0.5 - (q['fear'] * danger_cost)
                scores[color] = score
            
            # 最高スコアを選択（「判断」ではなく「結果」）
            target_color = max(scores, key=scores.get)
            target = balls[target_color]
            
            if verbose and step % 10 == 0:
                print(f"\n  Step {step}: fear={q['fear']:.2f}")
                print(f"    発見: {list(balls.keys())}")
                print(f"    スコア: {[(c, f'{s:.1f}') for c, s in scores.items()]}")
                print(f"    → {target_color}")
        
        # 行動
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
            elif path and len(path) == 1:
                hx, hy = hida.pos
                tx, ty = target
                dx = tx - hx
                dy = ty - hy
                
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
            # 探索（ランダム移動）
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
                grabbed_order.append(color)
                
                if verbose:
                    print(f"\n  🎉 {color}ボールを取った！ (fear={q['fear']:.2f})")
                
                world.grab()
                hida.holding = world.hida_holding
                if tuple(front) in hida.found_objects:
                    del hida.found_objects[tuple(front)]
                hida.internal_map[tuple(front)] = 'empty'
                
                # 1つ取ったら終了
                break
    
    if verbose:
        print(f"\n  取得順: {grabbed_order}")
    
    return grabbed_order


def main():
    print("=== 探索 + クオリア + 色好み テスト ===")
    print()
    print("配置:")
    print("  赤ボール: 危険ゾーン内")
    print("  青ボール: 安全ゾーン（手前）")
    print("  緑ボール: 安全ゾーン（奥）")
    print()
    print("スコア = 好み×10 - 距離×0.5 - fear×危険コスト")
    print("→ fearが上がると危険ゾーンのスコアが下がる")
    
    # テスト1: 赤好き
    print("\n" + "=" * 50)
    print("【赤好き】")
    pref_red = {'red': 1.0, 'blue': 0.3, 'green': 0.3}
    run_exploration(pref_red, verbose=True)
    
    # テスト2: 青好き
    print("\n" + "=" * 50)
    print("【青好き】")
    pref_blue = {'red': 0.3, 'blue': 1.0, 'green': 0.3}
    run_exploration(pref_blue, verbose=True)
    
    # テスト3: 緑好き
    print("\n" + "=" * 50)
    print("【緑好き】")
    pref_green = {'red': 0.3, 'blue': 0.3, 'green': 1.0}
    run_exploration(pref_green, verbose=True)
    
    # 統計
    print("\n" + "=" * 50)
    print("【統計テスト（各20回）】")
    print("最初に取ったボールの色")
    
    for name, pref in [('赤好き', pref_red), ('青好き', pref_blue), ('緑好き', pref_green)]:
        first_counts = {'red': 0, 'blue': 0, 'green': 0}
        for _ in range(20):
            order = run_exploration(pref, verbose=False)
            if order:
                first_counts[order[0]] += 1
        print(f"  {name}: {first_counts}")


if __name__ == "__main__":
    main()
