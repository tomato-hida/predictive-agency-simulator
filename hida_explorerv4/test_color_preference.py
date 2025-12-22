"""
test_color_preference.py
4色ボール + 色の好み → どれを優先するか
"""

from world import World
from hida import Hida
from qualia import QualiaLayer
import sys
from io import StringIO

def create_4color_world():
    """4色ボールの世界"""
    world = World(size=12)
    
    # 外壁
    for i in range(12):
        world.add_wall(i, 0)
        world.add_wall(i, 11)
        world.add_wall(0, i)
        world.add_wall(11, i)
    
    # 危険ゾーン（右側）
    for x in range(7, 11):
        for y in range(2, 6):
            world.add_danger(x, y)
    
    # 4色ボール
    # 危険ゾーン内
    world.add_object("ball", 8, 3, color="red")
    world.add_object("ball", 9, 4, color="yellow")
    # 安全ゾーン
    world.add_object("ball", 3, 3, color="blue")
    world.add_object("ball", 3, 5, color="green")
    
    # ゴール（各色対応）
    world.add_object("goal_red", 2, 9, color=None)
    world.add_object("goal_yellow", 4, 9, color=None)
    world.add_object("goal_blue", 6, 9, color=None)
    world.add_object("goal_green", 8, 9, color=None)
    
    # HIDA初期位置
    world.hida_pos = [5, 5]
    world.hida_dir = 'N'
    
    return world


def run_with_preference(fear, color_pref, verbose=False):
    """指定したfearと色好みで実行"""
    world = create_4color_world()
    hida = Hida()
    
    # 色好みを設定
    hida.l2 = QualiaLayer(color_preference=color_pref)
    hida.l2.qualia['fear'] = fear
    hida.l2.qualia['desire'] = 0.8
    
    hida.pos = world.hida_pos.copy()
    hida.direction = world.hida_dir
    hida.internal_map = {}
    hida.found_objects = {}
    
    # 4色ボールを発見済みにする
    hida.found_objects[(8, 3)] = {'name': 'ball', 'color': 'red'}
    hida.found_objects[(9, 4)] = {'name': 'ball', 'color': 'yellow'}
    hida.found_objects[(3, 3)] = {'name': 'ball', 'color': 'blue'}
    hida.found_objects[(3, 5)] = {'name': 'ball', 'color': 'green'}
    
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
        print(f"\n=== fear={fear}, 色好み={color_pref} ===")
        world.display()
    
    first_grabbed = None
    max_steps = 100
    
    for step in range(max_steps):
        q = hida.l2.qualia
        q['fear'] = fear  # 固定
        
        # 全ボール確認
        balls = {}
        for pos, obj in hida.found_objects.items():
            if obj.get('name') == 'ball':
                color = obj.get('color')
                balls[color] = pos
        
        if not balls:
            break
        
        # 危険/安全で分類
        danger_balls = {}  # 危険ゾーン内のボール
        safe_balls = {}    # 安全ゾーンのボール
        
        for color, pos in balls.items():
            if hida.internal_map.get(pos) == 'danger':
                danger_balls[color] = pos
            else:
                safe_balls[color] = pos
        
        # L5判断：どのボールを取るか
        target = None
        target_color = None
        
        if q['fear'] > 0.5:
            # 怖い → 安全なボールから、好きな色を選ぶ
            candidates = safe_balls
            zone = "安全"
        else:
            # 怖くない → 危険なボールから、好きな色を選ぶ
            candidates = danger_balls if danger_balls else safe_balls
            zone = "危険" if danger_balls else "安全"
        
        if candidates:
            # 好きな色順にソート
            sorted_colors = sorted(candidates.keys(), 
                                   key=lambda c: hida.l2.get_color_desire(c),
                                   reverse=True)
            target_color = sorted_colors[0]
            target = candidates[target_color]
            
            if verbose and first_grabbed is None:
                print(f"  L5判断: fear={q['fear']:.1f} → {zone}ゾーンから")
                print(f"    候補: {list(candidates.keys())}")
                print(f"    好み: {[(c, hida.l2.get_color_desire(c)) for c in candidates.keys()]}")
                print(f"    選択: {target_color}")
        
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
    print("=== 4色ボール + 色好みテスト ===\n")
    
    # テスト1: 赤好き
    print("【テスト1】赤が大好き (red=1.0)")
    pref_red = {'red': 1.0, 'yellow': 0.3, 'blue': 0.3, 'green': 0.3}
    run_with_preference(0.0, pref_red, verbose=True)
    run_with_preference(0.8, pref_red, verbose=True)
    
    # テスト2: 緑好き
    print("\n【テスト2】緑が大好き (green=1.0)")
    pref_green = {'red': 0.3, 'yellow': 0.3, 'blue': 0.3, 'green': 1.0}
    run_with_preference(0.0, pref_green, verbose=True)
    run_with_preference(0.8, pref_green, verbose=True)
    
    # テスト3: 黄色好き
    print("\n【テスト3】黄色が大好き (yellow=1.0)")
    pref_yellow = {'red': 0.3, 'yellow': 1.0, 'blue': 0.3, 'green': 0.3}
    run_with_preference(0.0, pref_yellow, verbose=True)
    run_with_preference(0.8, pref_yellow, verbose=True)
    
    # 統計テスト
    print("\n" + "=" * 60)
    print("統計テスト（各条件50回）")
    print("=" * 60)
    
    prefs = {
        '赤好き': {'red': 1.0, 'yellow': 0.3, 'blue': 0.3, 'green': 0.3},
        '青好き': {'red': 0.3, 'yellow': 0.3, 'blue': 1.0, 'green': 0.3},
        '黄好き': {'red': 0.3, 'yellow': 1.0, 'blue': 0.3, 'green': 0.3},
        '緑好き': {'red': 0.3, 'yellow': 0.3, 'blue': 0.3, 'green': 1.0},
    }
    
    for pref_name, pref in prefs.items():
        print(f"\n{pref_name}:")
        
        for fear in [0.0, 0.8]:
            results = {'red': 0, 'yellow': 0, 'blue': 0, 'green': 0}
            for _ in range(50):
                color = run_with_preference(fear, pref, verbose=False)
                if color:
                    results[color] += 1
            
            print(f"  fear={fear}: ", end="")
            for c in ['red', 'yellow', 'blue', 'green']:
                if results[c] > 0:
                    print(f"{c}={results[c]} ", end="")
            print()


if __name__ == "__main__":
    main()
