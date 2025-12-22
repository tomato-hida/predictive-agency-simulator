"""
test_multi_qualia.py
fear × urgency の2x2マトリクスで行動パターンをテスト
"""

from world import World
from hida import Hida
from qualia import QualiaLayer
import sys
from io import StringIO
import math

def create_4color_world():
    """4色ボールの世界（距離差をつける）"""
    world = World(size=12)
    
    # 外壁
    for i in range(12):
        world.add_wall(i, 0)
        world.add_wall(i, 11)
        world.add_wall(0, i)
        world.add_wall(11, i)
    
    # 危険ゾーン（右側）
    for x in range(7, 11):
        for y in range(2, 8):
            world.add_danger(x, y)
    
    # 4色ボール（距離差あり）
    # 危険ゾーン内
    world.add_object("ball", 8, 3, color="red")     # 近い
    world.add_object("ball", 9, 6, color="yellow")  # 遠い
    # 安全ゾーン
    world.add_object("ball", 2, 4, color="blue")    # 近い
    world.add_object("ball", 2, 8, color="green")   # 遠い
    
    # ゴール
    world.add_object("goal_red", 2, 10, color=None)
    world.add_object("goal_yellow", 4, 10, color=None)
    world.add_object("goal_blue", 6, 10, color=None)
    world.add_object("goal_green", 8, 10, color=None)
    
    # HIDA初期位置（中央上部）
    world.hida_pos = [5, 3]
    world.hida_dir = 'S'
    
    return world


def run_with_qualia(fear, urgency, color_pref, verbose=False):
    """指定したクオリアで実行"""
    world = create_4color_world()
    hida = Hida()
    
    # クオリア設定
    hida.l2 = QualiaLayer(color_preference=color_pref)
    hida.l2.qualia['fear'] = fear
    hida.l2.qualia['urgency'] = urgency
    hida.l2.qualia['desire'] = 0.8
    
    hida.pos = world.hida_pos.copy()
    hida.direction = world.hida_dir
    hida.internal_map = {}
    hida.found_objects = {}
    
    # 4色ボールを発見済みにする
    hida.found_objects[(8, 3)] = {'name': 'ball', 'color': 'red'}
    hida.found_objects[(9, 6)] = {'name': 'ball', 'color': 'yellow'}
    hida.found_objects[(2, 4)] = {'name': 'ball', 'color': 'blue'}
    hida.found_objects[(2, 8)] = {'name': 'ball', 'color': 'green'}
    
    # 地図を与える
    for x in range(1, 11):
        for y in range(1, 11):
            if world.grid[y][x] == 'danger':
                hida.internal_map[(x, y)] = 'danger'
            elif world.grid[y][x] == 'wall':
                hida.internal_map[(x, y)] = 'wall'
            elif (x, y) in world.objects:
                hida.internal_map[(x, y)] = 'object'
            else:
                hida.internal_map[(x, y)] = 'empty'
    
    if verbose:
        print(f"\n=== fear={fear}, urgency={urgency} ===")
        world.display()
    
    first_grabbed = None
    max_steps = 100
    
    for step in range(max_steps):
        q = hida.l2.qualia
        q['fear'] = fear      # 固定
        q['urgency'] = urgency # 固定
        
        # 全ボール確認
        balls = {}
        for pos, obj in hida.found_objects.items():
            if obj.get('name') == 'ball':
                color = obj.get('color')
                balls[color] = pos
        
        if not balls:
            break
        
        # 危険/安全で分類 + 距離計算
        danger_balls = {}
        safe_balls = {}
        hx, hy = hida.pos
        
        for color, pos in balls.items():
            dist = abs(pos[0] - hx) + abs(pos[1] - hy)
            if hida.internal_map.get(pos) == 'danger':
                danger_balls[color] = {'pos': pos, 'dist': dist}
            else:
                safe_balls[color] = {'pos': pos, 'dist': dist}
        
        # L5判断：2x2マトリクス
        target = None
        target_color = None
        decision_reason = ""
        
        # Step 1: fearでゾーン選択
        if q['fear'] > 0.5:
            candidates = safe_balls
            zone = "安全"
        else:
            candidates = danger_balls if danger_balls else safe_balls
            zone = "危険" if danger_balls else "安全"
        
        if candidates:
            # Step 2: urgencyで選択基準を決定
            if q['urgency'] > 0.5:
                # 急いでる → 近い方優先
                sorted_colors = sorted(candidates.keys(),
                                       key=lambda c: candidates[c]['dist'])
                target_color = sorted_colors[0]
                decision_reason = f"近い（距離={candidates[target_color]['dist']}）"
            else:
                # 急いでない → 好きな色優先
                sorted_colors = sorted(candidates.keys(),
                                       key=lambda c: hida.l2.get_color_desire(c),
                                       reverse=True)
                target_color = sorted_colors[0]
                decision_reason = f"好き（好感度={hida.l2.get_color_desire(target_color)}）"
            
            target = candidates[target_color]['pos']
            
            if verbose and first_grabbed is None:
                print(f"  L5判断:")
                print(f"    fear={q['fear']:.1f} → {zone}ゾーン")
                print(f"    urgency={q['urgency']:.1f} → {decision_reason}")
                print(f"    → {target_color}を選択")
        
        # 行動
        if target:
            path = hida.find_path(target)
            if path and len(path) >= 2:
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
        
        # ボール到達チェック
        front = world.get_front_pos()
        if tuple(front) in world.objects:
            obj = world.objects[tuple(front)]
            if obj.get('name') == 'ball' and not hida.holding:
                color = obj.get('color')
                if first_grabbed is None:
                    first_grabbed = color
                    if verbose:
                        print(f"  → {color}ボールを取った！")
                    return first_grabbed
    
    return first_grabbed


def main():
    print("=== fear × urgency 2x2マトリクステスト ===")
    print()
    print("配置:")
    print("  危険ゾーン: red(近い), yellow(遠い)")
    print("  安全ゾーン: blue(近い), green(遠い)")
    print()
    print("色好み: yellow > green > red > blue")
    print()
    
    # 色好み（黄色>緑>赤>青）
    color_pref = {'red': 0.4, 'yellow': 1.0, 'blue': 0.2, 'green': 0.8}
    
    # 2x2マトリクス
    print("=" * 60)
    print("【2x2マトリクス詳細】")
    print("=" * 60)
    
    for fear in [0.0, 0.8]:
        for urgency in [0.0, 0.8]:
            run_with_qualia(fear, urgency, color_pref, verbose=True)
    
    # 統計テスト
    print("\n" + "=" * 60)
    print("【統計テスト（各条件50回）】")
    print("=" * 60)
    print()
    print("            | urgency低(好み優先) | urgency高(近さ優先)")
    print("-" * 60)
    
    for fear in [0.0, 0.8]:
        zone = "危険" if fear < 0.5 else "安全"
        row = f"fear={fear}({zone}) |"
        
        for urgency in [0.0, 0.8]:
            results = {'red': 0, 'yellow': 0, 'blue': 0, 'green': 0}
            for _ in range(50):
                color = run_with_qualia(fear, urgency, color_pref, verbose=False)
                if color:
                    results[color] += 1
            
            # 結果を文字列に
            winner = max(results, key=results.get)
            row += f" {winner:8s}({results[winner]}) |"
        
        print(row)
    
    print()
    print("期待される結果:")
    print("  fear低 + urgency低 → 危険ゾーンで好きな色 → yellow")
    print("  fear低 + urgency高 → 危険ゾーンで近い方 → red")
    print("  fear高 + urgency低 → 安全ゾーンで好きな色 → green")
    print("  fear高 + urgency高 → 安全ゾーンで近い方 → blue")


if __name__ == "__main__":
    main()
