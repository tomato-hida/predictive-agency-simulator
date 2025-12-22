"""
test_random_stats.py
ランダム配置で大量テスト → 統計を取る
"""

from world import World
from hida import Hida
import random

def create_random_world(seed=None):
    """ランダムな世界を生成"""
    if seed is not None:
        random.seed(seed)
    
    world = World(size=10)
    
    # 外壁
    for i in range(10):
        world.add_wall(i, 0)
        world.add_wall(i, 9)
        world.add_wall(0, i)
        world.add_wall(9, i)
    
    # 危険ゾーン（ランダムな位置とサイズ）
    danger_x = random.randint(3, 6)
    danger_y = random.randint(2, 5)
    danger_w = random.randint(2, 4)
    danger_h = random.randint(2, 4)
    
    danger_cells = set()
    for x in range(danger_x, min(danger_x + danger_w, 9)):
        for y in range(danger_y, min(danger_y + danger_h, 9)):
            world.add_danger(x, y)
            danger_cells.add((x, y))
    
    # 赤ボール（危険ゾーン内）
    danger_list = list(danger_cells)
    if danger_list:
        red_pos = random.choice(danger_list)
        world.add_object("ball", red_pos[0], red_pos[1], color="red")
    else:
        red_pos = (5, 3)
        world.add_object("ball", 5, 3, color="red")
    
    # 青ボール（安全ゾーン）
    safe_positions = []
    for x in range(1, 9):
        for y in range(1, 9):
            if (x, y) not in danger_cells and (x, y) != red_pos:
                safe_positions.append((x, y))
    
    blue_pos = random.choice(safe_positions)
    world.add_object("ball", blue_pos[0], blue_pos[1], color="blue")
    safe_positions.remove(blue_pos)
    
    # ゴール（安全ゾーン）
    red_goal = random.choice(safe_positions)
    world.add_object("goal_red", red_goal[0], red_goal[1], color=None)
    safe_positions.remove(red_goal)
    
    blue_goal = random.choice(safe_positions)
    world.add_object("goal_blue", blue_goal[0], blue_goal[1], color=None)
    safe_positions.remove(blue_goal)
    
    # HIDA初期位置（安全ゾーン）
    hida_pos = random.choice(safe_positions)
    world.hida_pos = list(hida_pos)
    world.hida_dir = random.choice(['N', 'E', 'S', 'W'])
    
    return world, {
        'red_ball': red_pos,
        'blue_ball': blue_pos,
        'red_goal': red_goal,
        'blue_goal': blue_goal,
        'hida_start': hida_pos,
        'danger_cells': len(danger_cells)
    }


def run_silent(world, hida, max_steps=200):
    """静かに実行して結果だけ返す"""
    hida.pos = world.hida_pos.copy()
    hida.direction = world.hida_dir
    hida.seen_this_session = set()
    hida.internal_map = {}
    hida.found_objects = {}
    
    completed = {'red': False, 'blue': False}
    first_grabbed = None  # 最初に取ったボールの色
    max_fear = 0.0
    both_found_fear = None  # 両方見つかった時のfear
    
    for step in range(max_steps):
        # 周りを見る（出力抑制）
        import sys
        from io import StringIO
        old_stdout = sys.stdout
        sys.stdout = StringIO()
        try:
            hida.look_around_and_remember(world)
        finally:
            sys.stdout = old_stdout
        
        # クオリア
        q = hida.l2.qualia
        max_fear = max(max_fear, q['fear'])
        
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
        
        # 両方見つかった時のfearを記録
        if red_ball and blue_ball and both_found_fear is None:
            both_found_fear = q['fear']
        
        # ターゲット決定（L5判断）
        target = None
        if hida.holding:
            if hida.holding.get('color') == 'red' and red_goal:
                target = red_goal
            elif hida.holding.get('color') == 'blue' and blue_goal:
                target = blue_goal
        else:
            if red_ball and blue_ball:
                # 両方見つかってる → fearで判断
                if q['fear'] > 0.5:
                    target = blue_ball
                else:
                    target = red_ball
            elif red_ball:
                target = red_ball
            elif blue_ball:
                target = blue_ball
        
        # 行動
        if target and q['desire'] > 0.3:
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
            # 探索（BFSベース）
            unexplored = []
            for y in range(1, 9):
                for x in range(1, 9):
                    if (x, y) not in hida.internal_map:
                        unexplored.append((x, y))
            
            if unexplored:
                # 最も近い未探索マスへ
                hx, hy = hida.pos
                unexplored.sort(key=lambda p: abs(p[0]-hx) + abs(p[1]-hy))
                
                for ux, uy in unexplored:
                    # 未探索マスの隣へ行く
                    for dx, dy in [(0,-1), (0,1), (-1,0), (1,0)]:
                        nx, ny = ux + dx, uy + dy
                        if (nx, ny) in hida.internal_map:
                            cell = hida.internal_map[(nx, ny)]
                            if cell in ['empty', 'danger']:
                                path = hida.find_path((nx, ny))
                                if path and len(path) >= 2:
                                    next_pos = path[1]
                                    ddx = next_pos[0] - hx
                                    ddy = next_pos[1] - hy
                                    
                                    if ddx > 0: target_dir = 'E'
                                    elif ddx < 0: target_dir = 'W'
                                    elif ddy > 0: target_dir = 'S'
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
                                    break
                    else:
                        continue
                    break
        
        # ボール/ゴール到達チェック
        front = world.get_front_pos()
        if tuple(front) in world.objects:
            obj = world.objects[tuple(front)]
            
            if obj.get('name') == 'ball' and not hida.holding:
                color = obj.get('color')
                if first_grabbed is None:
                    first_grabbed = color
                world.grab()
                hida.holding = world.hida_holding
                ball_key = tuple(front)
                if ball_key in hida.found_objects:
                    del hida.found_objects[ball_key]
                hida.internal_map[ball_key] = 'empty'
            
            elif obj.get('name') == 'goal_red' and hida.holding:
                if hida.holding.get('color') == 'red':
                    world.release()
                    hida.holding = None
                    completed['red'] = True
            
            elif obj.get('name') == 'goal_blue' and hida.holding:
                if hida.holding.get('color') == 'blue':
                    world.release()
                    hida.holding = None
                    completed['blue'] = True
        
        if completed['red'] and completed['blue']:
            return {
                'success': True,
                'steps': step + 1,
                'first_grabbed': first_grabbed,
                'max_fear': max_fear,
                'both_found_fear': both_found_fear
            }
    
    return {
        'success': False,
        'steps': max_steps,
        'first_grabbed': first_grabbed,
        'max_fear': max_fear,
        'both_found_fear': both_found_fear
    }


def main():
    print("=== ランダムテスト（100回） ===\n")
    
    results = []
    
    for i in range(100):
        world, config = create_random_world(seed=None)  # 完全ランダム
        hida = Hida()
        
        result = run_silent(world, hida)
        result['config'] = config
        results.append(result)
        
        if (i + 1) % 10 == 0:
            print(f"  {i + 1}/100 完了...")
    
    # 統計
    print("\n" + "=" * 50)
    print("統計結果")
    print("=" * 50)
    
    success_count = sum(1 for r in results if r['success'])
    print(f"\n成功率: {success_count}/100 ({success_count}%)")
    
    # 最初に取ったボールの統計
    first_red = sum(1 for r in results if r['first_grabbed'] == 'red')
    first_blue = sum(1 for r in results if r['first_grabbed'] == 'blue')
    print(f"\n最初に取ったボール:")
    print(f"  赤（危険ゾーン）: {first_red}回")
    print(f"  青（安全ゾーン）: {first_blue}回")
    
    # 両方見つかった時のfear別の統計
    both_found = [r for r in results if r['both_found_fear'] is not None]
    print(f"\n両方のボールを見つけたケース: {len(both_found)}回")
    
    if both_found:
        high_fear = [r for r in both_found if r['both_found_fear'] > 0.5]
        low_fear = [r for r in both_found if r['both_found_fear'] <= 0.5]
        
        print(f"\n【両方見つかった時点で fear > 0.5】: {len(high_fear)}回")
        if high_fear:
            hf_blue_first = sum(1 for r in high_fear if r['first_grabbed'] == 'blue')
            print(f"  → 青を先に取った: {hf_blue_first}回 ({100*hf_blue_first//len(high_fear)}%)")
        
        print(f"\n【両方見つかった時点で fear <= 0.5】: {len(low_fear)}回")
        if low_fear:
            lf_red_first = sum(1 for r in low_fear if r['first_grabbed'] == 'red')
            print(f"  → 赤を先に取った: {lf_red_first}回 ({100*lf_red_first//len(low_fear)}%)")
    
    # 成功したケースのステップ数
    success_results = [r for r in results if r['success']]
    if success_results:
        avg_steps = sum(r['steps'] for r in success_results) / len(success_results)
        print(f"\n成功時の平均ステップ数: {avg_steps:.1f}")


if __name__ == "__main__":
    main()
