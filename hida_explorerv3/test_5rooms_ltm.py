"""
5部屋独立版テスト
explore_step（首振り+BFS）+ LTM/STM双方向更新
"""

from world import World
from hida import Hida
import random

def explore_step(hida, world):
    """今回まだ見てないマスへBFSで向かう"""
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
            hida.look_around_and_remember(world)
            world.turn_right()
            hida.update_pos(world)
            return True, f"壁！回転 → {hida.direction}"

def create_room(room_id, wall_positions=None):
    """10x10の部屋を作成（ボールとゴール両方あり）"""
    world = World(size=10)
    
    # 外壁
    for i in range(10):
        world.add_wall(i, 0)
        world.add_wall(i, 9)
        world.add_wall(0, i)
        world.add_wall(9, i)
    
    # 内壁
    if wall_positions:
        for wx, wy in wall_positions:
            world.add_wall(wx, wy)
    
    # ボール
    world.add_object("ball", 4, 3, color="red")
    
    # ゴール（ボールの近く）
    world.add_object("goal", 6, 3, color=None)
    
    # HIDA初期位置
    world.hida_pos = [2, 2]
    world.hida_dir = 'S'
    
    return world

def explore_room(hida, world, max_steps=200, wall_move_prob=0.05):
    """部屋を探索してボール→ゴール（まず全探索）"""
    exploration_done = False
    
    for step in range(max_steps):
        # 1. 周りを見る
        hida.look_around_and_remember(world)
        
        # 2. 壁が動く
        moved = world.tick(move_probability=wall_move_prob)
        if moved:
            for m in moved:
                print(f"  🧱 壁が動いた！ {m['from']} → {m['to']}")
        
        # 3. ボール/ゴール確認
        ball_pos = None
        goal_pos = None
        for pos, obj in hida.found_objects.items():
            if obj.get('color') == 'red':
                ball_pos = pos
            if obj.get('name') == 'goal':
                goal_pos = pos
        
        # 4. 今回まだ見てないマスがあるか確認
        unexplored = []
        seen = getattr(hida, 'seen_this_session', set())
        for y in range(1, 9):
            for x in range(1, 9):
                if (x, y) not in seen:
                    unexplored.append((x, y))
        
        # 5. 行動決定
        if unexplored and not exploration_done:
            # まだ未探索マスがある → 探索優先
            success, msg = explore_step(hida, world)
            if not success:
                # 到達不可 → 探索完了
                exploration_done = True
                print(f"  📍 探索完了！ 記憶: {hida.known_cells()}マス")
        else:
            # 探索完了 → ミッション
            if not exploration_done:
                exploration_done = True
                print(f"  📍 探索完了！ 記憶: {hida.known_cells()}マス")
            
            # ターゲット決定
            target = None
            if hida.holding and goal_pos:
                target = goal_pos
            elif ball_pos and not hida.holding:
                target = ball_pos
            
            if target:
                # BFSでターゲットへ
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
                        else:
                            hida.look_around_and_remember(world)
                            world.turn_right()
                            hida.update_pos(world)
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
        
        # 6. ボール/ゴール到達（探索完了後のみ）
        if exploration_done:
            front = world.get_front_pos()
            if tuple(front) in world.objects:
                obj = world.objects[tuple(front)]
                
                if obj.get('color') == 'red' and not hida.holding:
                    print(f"\n  🎉 ボール発見！つかんだ")
                    world.grab()
                    hida.holding = world.hida_holding
                    # found_objectsからボールを削除
                    ball_key = tuple(front)
                    if ball_key in hida.found_objects:
                        del hida.found_objects[ball_key]
                    # internal_mapも更新
                    hida.internal_map[ball_key] = 'empty'
                
                elif obj.get('name') == 'goal' and hida.holding:
                    print(f"\n  🎯 ゴール到達！")
                    world.release()
                    hida.holding = None
                    return 'mission_complete'
    
    return 'explored'

def main():
    print("=== 3部屋LTM/STMテスト ===")
    print("explore_step（首振り+BFS）+ LTM/STM双方向更新\n")
    
    # 3つの部屋
    rooms = {
        'A': create_room('A', wall_positions=[]),
        'B': create_room('B', wall_positions=[]),
        'C': create_room('C', wall_positions=[]),
    }
    
    # HIDA（LTM付き）
    hida = Hida()
    
    # Phase 1: 部屋Aでミッション
    print("=" * 40)
    print("Phase 1: 部屋Aでボール→ゴール")
    print("=" * 40)
    hida.enter_room('A', start_pos=[2, 2])
    rooms['A'].hida_pos = hida.pos.copy()
    rooms['A'].hida_dir = hida.direction
    rooms['A'].display()
    result = explore_room(hida, rooms['A'], max_steps=200, wall_move_prob=0)
    print(f"結果: {result}, 記憶: {hida.known_cells()}マス")
    hida.holding = None  # 次の部屋用にリセット
    
    # Phase 2: 部屋Bでミッション
    print("\n" + "=" * 40)
    print("Phase 2: 部屋Bでボール→ゴール")
    print("=" * 40)
    hida.enter_room('B', start_pos=[2, 2])
    rooms['B'].hida_pos = hida.pos.copy()
    rooms['B'].hida_dir = hida.direction
    result = explore_room(hida, rooms['B'], max_steps=200, wall_move_prob=0)
    print(f"結果: {result}, 記憶: {hida.known_cells()}マス")
    hida.holding = None
    
    # Phase 3: 部屋Aに戻る（記憶テスト）
    print("\n" + "=" * 40)
    print("Phase 3: 部屋Aに戻る（壁が動いてる）")
    print("=" * 40)
    
    # 神の介入（壁・ボール・ゴール全部変える）
    print("  👁️ 神の介入：部屋Aを改造")
    print("     壁: (3, 3) に追加")
    print("     ボール: 新しい位置 (5, 3)")  # 元のゴール付近
    print("     ゴール: 新しい位置 (7, 3)")
    
    # 壁を追加
    rooms['A'].grid[3][3] = 'wall'
    
    # 古いボール/ゴールがあれば削除
    if (4, 3) in rooms['A'].objects:
        del rooms['A'].objects[(4, 3)]
    if (6, 3) in rooms['A'].objects:
        del rooms['A'].objects[(6, 3)]
    
    # 新しい位置にボール/ゴール配置（探索済みエリア内）
    rooms['A'].add_object("ball", 5, 3, color="red")
    rooms['A'].add_object("goal", 7, 3, color=None)
    
    hida.enter_room('A', start_pos=[2, 2])
    rooms['A'].hida_pos = hida.pos.copy()
    rooms['A'].hida_dir = hida.direction
    rooms['A'].display()
    result = explore_room(hida, rooms['A'], max_steps=200, wall_move_prob=0)
    print(f"結果: {result}, 記憶: {hida.known_cells()}マス")
    
    # Phase 4: 部屋Cに行く
    print("\n" + "=" * 40)
    print("Phase 4: 部屋Cでボール→ゴール")
    print("=" * 40)
    hida.enter_room('C', start_pos=[2, 2])
    rooms['C'].hida_pos = hida.pos.copy()
    rooms['C'].hida_dir = hida.direction
    hida.holding = None
    result = explore_room(hida, rooms['C'], max_steps=200, wall_move_prob=0)
    print(f"結果: {result}, 記憶: {hida.known_cells()}マス")
    
    # Phase 5: 部屋Aに再度戻る
    print("\n" + "=" * 40)
    print("Phase 5: 部屋Aに再度戻る（LTM更新確認）")
    print("=" * 40)
    hida.enter_room('A', start_pos=[2, 2])
    rooms['A'].hida_pos = hida.pos.copy()
    rooms['A'].hida_dir = hida.direction
    print("  前回の予測誤差が修正されてるか確認")
    result = explore_room(hida, rooms['A'], max_steps=30, wall_move_prob=0)
    print(f"結果: {result}, 記憶: {hida.known_cells()}マス")
    
    # 最終状態
    print("\n" + "=" * 40)
    print("最終状態")
    print("=" * 40)
    print(f"総記憶: {hida.total_memory()}マス")
    print("LTM内容:")
    for room_id in sorted(hida.ltm.keys()):
        memory = hida.ltm[room_id]
        print(f"  部屋{room_id}: {len(memory['map'])}マス")

if __name__ == "__main__":
    main()
