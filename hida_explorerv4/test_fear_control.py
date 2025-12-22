"""
test_fear_control.py
配置を固定してfearの初期値だけ変える → 行動の違いを直接検証
"""

from world import World
from hida import Hida
import sys
from io import StringIO

def create_fixed_world():
    """固定配置の世界"""
    world = World(size=10)
    
    # 外壁
    for i in range(10):
        world.add_wall(i, 0)
        world.add_wall(i, 9)
        world.add_wall(0, i)
        world.add_wall(9, i)
    
    # 危険ゾーン（右側）
    for x in range(6, 9):
        for y in range(3, 7):
            world.add_danger(x, y)
    
    # 赤ボール（危険ゾーン内、遠い）
    world.add_object("ball", 7, 5, color="red")
    
    # 青ボール（安全ゾーン、左側、遠い）
    world.add_object("ball", 2, 5, color="blue")
    
    # ゴール
    world.add_object("goal_red", 2, 7, color=None)
    world.add_object("goal_blue", 7, 7, color=None)
    
    # HIDA初期位置（中央、両方のボールから離れた位置）
    world.hida_pos = [4, 2]
    world.hida_dir = 'S'
    
    return world


def run_with_initial_fear(initial_fear, verbose=False):
    """指定した初期fearで実行"""
    world = create_fixed_world()
    hida = Hida()
    hida.pos = world.hida_pos.copy()
    hida.direction = world.hida_dir
    hida.seen_this_session = set()
    hida.internal_map = {}
    hida.found_objects = {}
    
    # 初期fearを設定
    hida.l2.qualia['fear'] = initial_fear
    hida.l2.qualia['desire'] = 0.8  # ボールを取りたい
    
    # ★ 両方のボールを最初から発見済みにする
    hida.found_objects[(7, 5)] = {'name': 'ball', 'color': 'red'}
    hida.found_objects[(2, 5)] = {'name': 'ball', 'color': 'blue'}
    
    # 基本的な地図も与える（経路探索用）
    for x in range(1, 9):
        for y in range(1, 9):
            if world.grid[y][x] == 'danger':
                hida.internal_map[(x, y)] = 'danger'
            elif world.grid[y][x] == 'wall':
                hida.internal_map[(x, y)] = 'wall'
            elif (x, y) in world.objects:
                hida.internal_map[(x, y)] = 'object'
            else:
                hida.internal_map[(x, y)] = 'empty'
    
    first_grabbed = None
    max_steps = 150
    
    if verbose:
        print(f"\n=== 初期fear={initial_fear} ===")
        world.display()
    
    for step in range(max_steps):
        # 周りを見る
        old_stdout = sys.stdout
        sys.stdout = StringIO()
        try:
            hida.look_around_and_remember(world)
        finally:
            sys.stdout = old_stdout
        
        # クオリア（fearは固定 - テスト用）
        q = hida.l2.qualia
        q['fear'] = initial_fear  # 減衰させない
        
        # オブジェクト確認
        red_ball = None
        blue_ball = None
        red_goal = None
        blue_goal = None
        
        for pos, obj in hida.found_objects.items():
            if obj.get('color') == 'red' and obj.get('name') == 'ball':
                red_ball = pos
            if obj.get('color') == 'blue' and obj.get('name') == 'ball':
                blue_ball = pos
            if obj.get('name') == 'goal_red':
                red_goal = pos
            if obj.get('name') == 'goal_blue':
                blue_goal = pos
        
        # 両方見つかったらログ
        if verbose and red_ball and blue_ball and first_grabbed is None:
            print(f"  Step {step}: 両方発見！ fear={q['fear']:.2f}")
        
        # ターゲット決定（L5判断）
        target = None
        if hida.holding:
            if hida.holding.get('color') == 'red' and red_goal:
                target = red_goal
            elif hida.holding.get('color') == 'blue' and blue_goal:
                target = blue_goal
        else:
            if red_ball and blue_ball:
                if q['fear'] > 0.5:
                    target = blue_ball
                    if verbose and first_grabbed is None:
                        print(f"  → L5判断: fear={q['fear']:.2f} > 0.5 → 青優先")
                else:
                    target = red_ball
                    if verbose and first_grabbed is None:
                        print(f"  → L5判断: fear={q['fear']:.2f} <= 0.5 → 赤優先")
            elif red_ball:
                target = red_ball
            elif blue_ball:
                target = blue_ball
        
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
                        print(f"  Step {step}: {color}ボールを取った！")
                    return first_grabbed
                world.grab()
                hida.holding = world.hida_holding
    
    return first_grabbed


def main():
    print("=== 条件固定テスト ===")
    print("配置は同じ、初期fearだけ変える")
    print()
    
    # まず1回詳細表示
    print("【詳細表示】")
    run_with_initial_fear(0.0, verbose=True)
    run_with_initial_fear(0.8, verbose=True)
    
    # 統計テスト
    print("\n" + "=" * 50)
    print("統計テスト（各条件100回）")
    print("=" * 50)
    
    fear_levels = [0.0, 0.2, 0.4, 0.6, 0.8, 1.0]
    
    for fear in fear_levels:
        red_first = 0
        blue_first = 0
        
        for _ in range(100):
            result = run_with_initial_fear(fear, verbose=False)
            if result == 'red':
                red_first += 1
            elif result == 'blue':
                blue_first += 1
        
        print(f"\n初期fear={fear:.1f}:")
        print(f"  赤先: {red_first}回 | 青先: {blue_first}回")


if __name__ == "__main__":
    main()
