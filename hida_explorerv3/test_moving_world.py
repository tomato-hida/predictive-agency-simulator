"""
動く世界のテスト
壁が勝手に動く → HIDAは邪魔されるか？
"""

from world import World
from hida import Hida
from narrator import narrate
import random

def explore_step(hida, world):
    """未探索マスへBFSで向かう。成功したらTrue"""
    unexplored = []
    for y in range(1, 9):
        for x in range(1, 9):
            if (x, y) not in hida.internal_map:
                unexplored.append((x, y))
    
    if not unexplored:
        return False, "全探索済み"
    
    hx, hy = hida.pos
    candidates = []
    
    # DEBUG
    # print(f"    [DEBUG] 未探索: {len(unexplored)}個, 自分: ({hx}, {hy})")
    
    for ux, uy in unexplored:
        # 未探索マスの隣で到達可能な場所を探す
        for dx, dy in [(0, -1), (0, 1), (-1, 0), (1, 0)]:
            nx, ny = ux + dx, uy + dy
            # 自分の位置なら直接見える
            if (nx, ny) == (hx, hy):
                candidates.append({
                    'target': (hx, hy),
                    'dist': 0,
                    'path': [],
                    'look_dir': (-dx, -dy)  # 未探索マスの方を向く
                })
            elif (nx, ny) in hida.internal_map:
                if hida.internal_map[(nx, ny)] == 'empty':
                    path = hida.find_path((nx, ny))
                    if path:
                        candidates.append({
                            'target': (nx, ny),
                            'dist': len(path),
                            'path': path
                        })
    
    if not candidates:
        return False, "到達不可"
    
    # 最短経路
    candidates.sort(key=lambda c: c['dist'])
    best = candidates[0]
    
    # DEBUG
    # print(f"    [DEBUG] best: {best}")
    
    # 既に隣にいる場合はその方向を向く
    if best['dist'] == 0 and 'look_dir' in best:
        ldx, ldy = best['look_dir']
        if ldx > 0: target_dir = 'E'
        elif ldx < 0: target_dir = 'W'
        elif ldy > 0: target_dir = 'S'
        else: target_dir = 'N'
        
        if hida.direction != target_dir:
            dirs = ['N', 'E', 'S', 'W']
            current_idx = dirs.index(hida.direction)
            target_idx = dirs.index(target_dir)
            diff = (target_idx - current_idx) % 4
            if diff == 1 or diff == 2:
                world.turn_right()
            else:
                world.turn_left()
            hida.update_pos(world)
            return True, f"探索回転 → {hida.direction}"
        else:
            # 既に向いてる、周りを見る
            hida.look_around_and_remember(world)
            return True, "周囲確認"
    
    if not best['path'] or len(best['path']) < 2:
        return False, "経路なし"
    
    next_pos = best['path'][1]  # 自分の位置の次
    dx = next_pos[0] - hx
    dy = next_pos[1] - hy
    
    if dx > 0: target_dir = 'E'
    elif dx < 0: target_dir = 'W'
    elif dy > 0: target_dir = 'S'
    else: target_dir = 'N'
    
    if hida.direction != target_dir:
        dirs = ['N', 'E', 'S', 'W']
        current_idx = dirs.index(hida.direction)
        target_idx = dirs.index(target_dir)
        diff = (target_idx - current_idx) % 4
        if diff == 1 or diff == 2:
            world.turn_right()
        else:
            world.turn_left()
        hida.update_pos(world)
        return True, f"探索回転 → {hida.direction}"
    else:
        success, msg = world.move_forward()
        if success:
            hida.update_pos(world)
            hida.look_around_and_remember(world)
            return True, f"探索前進 → {hida.pos}"
        else:
            # 壁が動いてた！マップ更新して再計算
            hida.look_around_and_remember(world)  # マップ更新
            world.turn_right()
            hida.update_pos(world)
            return True, f"壁！回転 → {hida.direction}"

def main():
    # 10x10の世界
    world = World(size=10)
    
    # 外壁
    for i in range(10):
        world.add_wall(i, 0)
        world.add_wall(i, 9)
        world.add_wall(0, i)
        world.add_wall(9, i)
    
    # 内壁（少なめ）
    world.add_wall(4, 4)
    world.add_wall(4, 5)
    world.add_wall(5, 5)
    
    # ボール（近く）
    world.add_object("ball", 4, 3, color="red")
    
    # ゴール（右下）
    world.add_object("goal", 7, 7, color=None)
    
    # HIDA（左上からスタート）
    world.hida_pos = [2, 2]
    world.hida_dir = 'S'
    
    hida = Hida()
    hida.pos = [2, 2]
    hida.direction = 'S'
    
    print("=== 動く世界テスト ===")
    print("壁が5%の確率で動く")
    print("HIDAは邪魔されるか？\n")
    
    world.display()
    
    # メインループ
    for step in range(200):
        print(f"\n--- Step {step + 1} ---")
        
        # 1. HIDAが周りを見る
        hida.look_around_and_remember(world)
        
        # 2. 世界が動く（壁が動くかも）
        moved = world.tick(move_probability=0.05)  # 5%に下げた
        if moved:
            for m in moved:
                print(f"  🧱 壁が動いた！ {m['from']} → {m['to']}")
                print(f"     （HIDAはまだ知らない...）")
        
        # 3. ボール/ゴール見つけてる？
        ball_pos = None
        goal_pos = None
        for pos, obj in hida.found_objects.items():
            if obj.get('color') == 'red':
                ball_pos = pos
            if obj.get('name') == 'goal':
                goal_pos = pos
        
        if hida.holding:
            if goal_pos:
                print(f"  記憶: ゴールは {goal_pos}、ボール持ってる！")
            else:
                print(f"  記憶: ゴール未発見、ボール持ってる")
        elif ball_pos:
            print(f"  記憶: ボールは {ball_pos} にあるはず")
        else:
            print(f"  記憶: ボール未発見")
        
        # 4. 行動
        target = None
        if hida.holding and goal_pos:
            target = goal_pos  # ゴールへ向かう
        elif ball_pos and not hida.holding:
            target = ball_pos  # ボールへ向かう
        
        if target:
            dx = target[0] - hida.pos[0]
            dy = target[1] - hida.pos[1]
            
            # 方向決定
            if abs(dx) > abs(dy):
                target_dir = 'E' if dx > 0 else 'W'
            else:
                target_dir = 'S' if dy > 0 else 'N'
            
            # 向きを変える or 前進
            if hida.direction != target_dir:
                # 最短回転を計算
                dirs = ['N', 'E', 'S', 'W']
                current_idx = dirs.index(hida.direction)
                target_idx = dirs.index(target_dir)
                diff = (target_idx - current_idx) % 4
                
                if diff == 1 or diff == 2:
                    world.turn_right()
                else:  # diff == 3
                    world.turn_left()
                hida.update_pos(world)
                print(f"  行動: 回転 → {hida.direction}")
            else:
                success, msg = world.move_forward()
                if success:
                    hida.update_pos(world)
                    print(f"  行動: 前進 → {hida.pos}")
                    
                    # 周りを見る（移動後）
                    hida.look_around_and_remember(world)
                else:
                    world.turn_right()
                    hida.update_pos(world)
                    print(f"  行動: 壁！回転 → {hida.direction}")
        else:
            # 探索（未探索マスへBFSで向かう）
            success, msg = explore_step(hida, world)
            if success:
                print(f"  行動: {msg}")
        
        # 5. 状態表示（10ステップごと）
        if (step + 1) % 10 == 0:
            print(f"\n  === 10ステップ経過 ===")
            print(f"  HIDA位置: {hida.pos}, 向き: {hida.direction}")
            print(f"  記憶してるマス: {hida.known_cells()}")
            world.display()
        
        # 6. ボール/ゴール到達チェック
        front = world.get_front_pos()
        if tuple(front) in world.objects:
            obj = world.objects[tuple(front)]
            
            # ボールを取る
            if obj.get('color') == 'red' and not hida.holding:
                print(f"\n  🎉 ボール発見！目の前にある！")
                success, msg = world.grab()
                if success:
                    hida.holding = world.hida_holding
                    print(f"  {msg}")
            
            # ゴールに届ける
            elif obj.get('name') == 'goal' and hida.holding:
                print(f"\n  🎯 ゴール到達！")
                success, msg = world.release()
                if success:
                    print(f"  {msg}")
                    print(f"\n  🏆 ミッション成功！")
                    break

    print("\n=== 終了 ===")
    print(f"最終位置: {hida.pos}")
    print(f"持ってる: {hida.holding}")
    print(f"記憶してるマス: {hida.known_cells()}")
    world.display()

if __name__ == "__main__":
    main()
