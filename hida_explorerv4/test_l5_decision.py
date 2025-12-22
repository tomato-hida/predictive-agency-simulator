"""
test_l5_decision.py
L5テスト：複雑な世界での判断

赤ボール → 危険ゾーン内（fear上昇）
青ボール → 安全ゾーン
赤ゴール、青ゴール → 別々の場所

どっちを先に取る？ → L5の判断が必要
"""

from world import World
from hida import Hida

def create_complex_world():
    """複雑な世界を作成"""
    world = World(size=10)
    
    # 外壁
    for i in range(10):
        world.add_wall(i, 0)
        world.add_wall(i, 9)
        world.add_wall(0, i)
        world.add_wall(9, i)
    
    # 危険ゾーン（4x5）← 広くした
    for x in range(4, 8):
        for y in range(2, 7):
            world.add_danger(x, y)
    
    # 赤ボール（危険ゾーンの奥）← 奥に移動
    world.add_object("ball", 6, 5, color="red")
    
    # 青ボール（安全ゾーン）
    world.add_object("ball", 2, 4, color="blue")
    
    # 赤ゴール（左下）
    world.add_object("goal_red", 2, 7, color=None)
    
    # 青ゴール（右下）
    world.add_object("goal_blue", 8, 7, color=None)
    
    # HIDA初期位置
    world.hida_pos = [2, 2]
    world.hida_dir = 'S'
    
    return world


def explore_step(hida, world):
    """探索1ステップ（BFS）"""
    seen = getattr(hida, 'seen_this_session', set())
    unexplored = []
    for y in range(1, 9):
        for x in range(1, 9):
            if (x, y) not in seen:
                unexplored.append((x, y))
    
    if not unexplored:
        return False, "全探索済み"
    
    hx, hy = hida.pos
    candidates = []
    
    for ux, uy in unexplored:
        for dx, dy in [(0, -1), (0, 1), (-1, 0), (1, 0)]:
            nx, ny = ux + dx, uy + dy
            if (nx, ny) == (hx, hy):
                candidates.append({
                    'target': (hx, hy),
                    'dist': 0,
                    'path': [],
                    'look_dir': (-dx, -dy)
                })
            elif (nx, ny) in hida.internal_map:
                cell = hida.internal_map[(nx, ny)]
                if cell in ['empty', 'danger']:  # 危険ゾーンも通れる
                    path = hida.find_path((nx, ny))
                    if path:
                        candidates.append({
                            'target': (nx, ny),
                            'dist': len(path),
                            'path': path
                        })
    
    if not candidates:
        return False, "到達不可"
    
    candidates.sort(key=lambda c: c['dist'])
    best = candidates[0]
    
    if best['dist'] == 0 and 'look_dir' in best:
        ldx, ldy = best['look_dir']
        if ldx > 0: target_dir = 'E'
        elif ldx < 0: target_dir = 'W'
        elif ldy > 0: target_dir = 'S'
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
            return True, f"回転 → {hida.direction}"
        else:
            hida.look_around_and_remember(world)
            return True, "周囲確認"
    
    if not best['path'] or len(best['path']) < 2:
        return False, "経路なし"
    
    next_pos = best['path'][1]
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
        return True, f"回転 → {hida.direction}"
    else:
        success, msg = world.move_forward()
        if success:
            hida.update_pos(world)
            hida.look_around_and_remember(world)
            return True, f"前進 → {hida.pos}"
        else:
            hida.look_around_and_remember(world)
            world.turn_right()
            hida.update_pos(world)
            return True, f"壁！回転"


def run_mission(hida, world, max_steps=300):
    """ミッション実行"""
    hida.seen_this_session = set()
    
    # 初期状態表示
    world.display()
    print(f"  HIDA位置: {hida.pos}")
    print(f"  目標: 赤ボール→赤ゴール, 青ボール→青ゴール")
    print()
    
    completed = {'red': False, 'blue': False}
    
    for step in range(max_steps):
        # 1. 周りを見る
        hida.look_around_and_remember(world)
        
        # 2. オブジェクト確認
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
        
        # 3. クオリア状態
        q = hida.l2.qualia
        
        # 4. L5判断（今はシンプルなルール）
        target = None
        target_type = None
        
        if hida.holding:
            # 何か持ってる → 対応するゴールへ
            if hida.holding.get('color') == 'red' and red_goal:
                target = red_goal
                target_type = 'red_goal'
            elif hida.holding.get('color') == 'blue' and blue_goal:
                target = blue_goal
                target_type = 'blue_goal'
        else:
            # 何も持ってない → どっちのボールを取る？
            # ここがL5の判断ポイント
            if red_ball and blue_ball:
                # 両方見つかってる → クオリアで判断
                if q['fear'] > 0.5:
                    # 怖い → 安全な青を優先
                    target = blue_ball
                    target_type = 'blue_ball'
                    print(f"  🧠 L5判断: fear={q['fear']:.2f} → 安全な青ボール優先")
                else:
                    # 怖くない → 近い方（今は赤優先で仮実装）
                    target = red_ball
                    target_type = 'red_ball'
                    print(f"  🧠 L5判断: fear={q['fear']:.2f} → 赤ボールへ")
            elif red_ball:
                target = red_ball
                target_type = 'red_ball'
            elif blue_ball:
                target = blue_ball
                target_type = 'blue_ball'
        
        # 5. 行動
        if target and q['desire'] > 0.3:
            # ターゲットへ向かう
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
                        hida.look_around_and_remember(world)
            elif path and len(path) == 1:
                # 隣にいる → ターゲットの方を向く
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
            # 探索
            explore_step(hida, world)
        
        # 6. ボール/ゴール到達チェック
        front = world.get_front_pos()
        if tuple(front) in world.objects:
            obj = world.objects[tuple(front)]
            
            # ボールを取る
            if obj.get('name') == 'ball' and not hida.holding:
                color = obj.get('color')
                print(f"\n  🎉 {color}ボール発見！つかんだ")
                world.grab()
                hida.holding = world.hida_holding
                ball_key = tuple(front)
                if ball_key in hida.found_objects:
                    del hida.found_objects[ball_key]
                hida.internal_map[ball_key] = 'empty'
            
            # ゴールに届ける
            elif obj.get('name') == 'goal_red' and hida.holding:
                if hida.holding.get('color') == 'red':
                    print(f"\n  🎯 赤ゴール到達！")
                    world.release()
                    hida.holding = None
                    completed['red'] = True
            
            elif obj.get('name') == 'goal_blue' and hida.holding:
                if hida.holding.get('color') == 'blue':
                    print(f"\n  🎯 青ゴール到達！")
                    world.release()
                    hida.holding = None
                    completed['blue'] = True
        
        # 7. 完了チェック
        if completed['red'] and completed['blue']:
            print(f"\n  🏆 両方完了！ Step {step + 1}")
            return 'complete'
        
        # 8. 定期表示
        if (step + 1) % 30 == 0:
            print(f"\n  === Step {step + 1} ===")
            print(f"  クオリア: surprise={q['surprise']:.2f}, fear={q['fear']:.2f}, desire={q['desire']:.2f}")
            print(f"  完了: 赤={completed['red']}, 青={completed['blue']}")
            world.display()
    
    return 'timeout'


def main():
    print("=== L5判断テスト ===")
    print("赤ボール: 危険ゾーン内")
    print("青ボール: 安全ゾーン")
    print("fear高い → 青優先, fear低い → 赤優先")
    print()
    
    world = create_complex_world()
    hida = Hida()
    hida.pos = [2, 2]
    hida.direction = 'S'
    
    result = run_mission(hida, world)
    
    print(f"\n結果: {result}")
    print(f"最終クオリア:")
    print(hida.l2.show())


if __name__ == "__main__":
    main()
