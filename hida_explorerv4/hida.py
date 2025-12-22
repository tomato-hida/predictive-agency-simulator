"""
hida.py
HIDA - 内部世界モデルを持つエージェント（LTM/STM付き + L2クオリア）
"""

import random
from narrator import narrate
from qualia import QualiaLayer

class Hida:
    def __init__(self, start_pos=None):
        # L2: クオリア層
        self.l2 = QualiaLayer()
        
        # LTM: 長期記憶（全部屋の記憶）
        # {'A': {'map': {...}, 'objects': {...}}, 'B': {...}, ...}
        self.ltm = {}
        
        # STM: 短期記憶（今の部屋の記憶）= internal_map
        self.internal_map = {}
        
        # 見つけたオブジェクト（STMの一部）
        self.found_objects = {}  # 位置 → オブジェクト情報
        
        # 今いる部屋
        self.current_room = None
        
        # 自分の位置と向き（これは知ってる）
        self.pos = start_pos if start_pos else [2, 2]
        self.direction = 'N'
        
        # 持ってるもの
        self.holding = None
        
        # 行動の記憶
        self.action_memory = []
        
        # 直前の予測誤差（L2更新用）
        self.last_errors = []
    
    # === LTM/STM管理 ===
    
    def enter_room(self, room_id, start_pos=None):
        """部屋に入る（ワープ）"""
        # 今の部屋をLTMに保存
        if self.current_room:
            self._save_to_ltm()
        
        # 新しい部屋に移動
        self.current_room = room_id
        
        # 今回見たマスをリセット
        self.seen_this_session = set()
        
        # LTMから読み込み
        if room_id in self.ltm:
            memory = self.ltm[room_id]
            self.internal_map = memory['map'].copy()
            self.found_objects = memory['objects'].copy()
            print(f"  💭 「部屋{room_id}...覚えてる」")
            print(f"     記憶: {len(self.internal_map)}マス")
        else:
            self.internal_map = {}
            self.found_objects = {}
            print(f"  💭 「部屋{room_id}...初めて来た」")
        
        # 位置リセット
        if start_pos:
            self.pos = start_pos.copy()
        self.direction = 'S'
    
    def _save_to_ltm(self):
        """STMをLTMに保存"""
        if self.current_room:
            self.ltm[self.current_room] = {
                'map': self.internal_map.copy(),
                'objects': self.found_objects.copy()
            }
            print(f"  💾 部屋{self.current_room}の記憶を保存（{len(self.internal_map)}マス）")
    
    def leave_room(self):
        """部屋を出る"""
        self._save_to_ltm()
        self.current_room = None
    
    def total_memory(self):
        """全記憶マス数（LTM + STM）"""
        total = len(self.internal_map)
        for room_id, memory in self.ltm.items():
            if room_id != self.current_room:
                total += len(memory['map'])
        return total
    
    # === 既存の機能 ===
    
    def see_and_remember(self, world):
        """見て覚える（前方だけ）"""
        # 今いる場所を記録
        self.internal_map[tuple(self.pos)] = 'empty'
        
        # 前方を見る
        front_cell = world.see_front()
        front_pos = world.get_front_pos()
        
        # 記憶する
        if front_pos[0] >= 0 and front_pos[0] < world.width and \
           front_pos[1] >= 0 and front_pos[1] < world.height:
            self.internal_map[tuple(front_pos)] = front_cell
        
        return front_cell
    
    def look_around_and_remember(self, world):
        """首を回して4方向見て覚える（予測誤差検出付き）"""
        # 今いる場所を記録（危険ゾーンならdangerとして記録）
        current_cell = world.see_cell(self.pos)
        current_type = current_cell['type'] if isinstance(current_cell, dict) else current_cell
        if current_type in ['danger']:
            self.internal_map[tuple(self.pos)] = 'danger'
        else:
            self.internal_map[tuple(self.pos)] = 'empty'
        
        if hasattr(self, 'seen_this_session'):
            self.seen_this_session.add(tuple(self.pos))
        
        # 4方向を見る
        around = world.look_around()
        
        seen = {}
        prediction_errors = []
        
        for direction, info in around.items():
            pos = tuple(info['pos'])
            cell = info['cell']
            
            # 今回見たマスに追加
            if hasattr(self, 'seen_this_session'):
                self.seen_this_session.add(pos)
            
            # 実際に見えたもの
            actual = cell['type'] if isinstance(cell, dict) else cell
            
            # 予測（既存の記憶）
            expected = self.internal_map.get(pos)
            
            # 🚨 予測誤差チェック
            if expected is not None and expected != actual:
                # オブジェクトの有無の変化を検出
                if expected == 'object' and actual != 'object':
                    prediction_errors.append({
                        'pos': pos,
                        'expected': expected,
                        'actual': actual,
                        'message': f"あれ？{pos}に何かあったはずなのに..."
                    })
                elif expected != 'object' and actual == 'object':
                    prediction_errors.append({
                        'pos': pos,
                        'expected': expected,
                        'actual': actual,
                        'message': f"おっ！{pos}に何かある！前はなかったのに"
                    })
                elif expected == 'empty' and actual == 'wall':
                    prediction_errors.append({
                        'pos': pos,
                        'expected': expected,
                        'actual': actual,
                        'message': f"えっ？{pos}が壁になってる！"
                    })
                elif expected == 'wall' and actual == 'empty':
                    prediction_errors.append({
                        'pos': pos,
                        'expected': expected,
                        'actual': actual,
                        'message': f"壁がなくなってる！"
                    })
            
            # 記憶を更新
            self.internal_map[pos] = actual
            
            # オブジェクトがあれば記憶（danger内のオブジェクトも含む）
            has_object = actual == 'object' or (actual == 'danger' and cell.get('name'))
            if has_object:
                if pos not in self.found_objects:  # 新規発見のみ
                    self.found_objects[pos] = {
                        'name': cell['name'],
                        'color': cell['color']
                    }
                    if actual == 'danger':
                        print(f"  🔍 発見！ {cell['color']}の{cell['name']} at {list(pos)} ⚠️危険ゾーン内")
                    else:
                        print(f"  🔍 発見！ {cell['color']}の{cell['name']} at {list(pos)}")
            elif pos in self.found_objects and not has_object:
                # オブジェクトがなくなった！
                del self.found_objects[pos]
            
            seen[direction] = actual
        
        # 予測誤差があれば報告（narratorで言語化）
        for error in prediction_errors:
            # 予測誤差の種類を判定
            if error['expected'] == 'object' and error['actual'] != 'object':
                event = 'prediction_error_missing'
            elif error['expected'] != 'object' and error['actual'] == 'object':
                event = 'prediction_error_appeared'
            else:
                event = 'prediction_error_changed'
            
            # narratorで言語化
            reaction = narrate(event, context=str(error['pos']))
            print(f"  ⚡ 予測誤差 @ {error['pos']}")
            print(f"     予測: {error['expected']} → 現実: {error['actual']}")
            print(f"  💭 「{reaction}」")
        
        # 予測誤差の数を記録（新しい発見としてカウントするため）
        self.last_prediction_errors = len(prediction_errors)
        self.last_errors = prediction_errors  # L2更新用に保存
        
        # L2: クオリアを更新
        self.l2.update(prediction_errors, self.found_objects, self.internal_map, self.pos)
        self.l2.holding_update(self.holding)  # ボール持ってたらdesire維持
        
        # 予測誤差があった時だけ全クオリア表示
        if prediction_errors:
            print(f"  🎭 クオリア変化:")
            for key, val in self.l2.qualia.items():
                if val > 0.1:
                    bar_len = int(val * 10)
                    bar = '█' * bar_len + '░' * (10 - bar_len)
                    print(f"     {key:10s}: [{bar}] {val:.2f}")
        
        return seen
    
    def choose_action(self, front_cell):
        """行動を選ぶ（未知優先 + 確率）"""
        
        # front_cellが通れるか（emptyのみ）
        front_passable = (front_cell == 'empty')
        
        # 4方向チェック：未知で、かつ通れる方向
        dirs = ['N', 'E', 'S', 'W']
        deltas = {'N': (0, -1), 'E': (1, 0), 'S': (0, 1), 'W': (-1, 0)}
        
        # 進める未知の方向を探す
        good_unknown_dirs = []
        for d in dirs:
            dx, dy = deltas[d]
            next_pos = (self.pos[0] + dx, self.pos[1] + dy)
            
            # 次のマスが未知、または空
            if next_pos not in self.internal_map:
                good_unknown_dirs.append(d)
            elif self.internal_map.get(next_pos) == 'empty':
                # 空だけど、その先が未知かチェック
                dx2, dy2 = deltas[d]
                far_pos = (next_pos[0] + dx2, next_pos[1] + dy2)
                if far_pos not in self.internal_map:
                    good_unknown_dirs.append(d)
        
        # 今の向きで前が空いてるなら前進優先
        if front_passable:
            if self.direction in good_unknown_dirs:
                return 'forward'
            # それ以外でも確率で前進
            if random.random() < 0.5:
                return 'forward'
        
        # 未知の方向があれば、そっちに向く
        if good_unknown_dirs:
            target_dir = random.choice(good_unknown_dirs)
            if self.direction == target_dir:
                if front_passable:
                    return 'forward'
            return self._get_turn_to(target_dir)
        
        # 未知がなければランダム
        if front_passable:
            return random.choice(['forward', 'left', 'right'])
        else:
            return random.choice(['left', 'right'])
    
    def _get_turn_to(self, target_dir):
        """目標方向に向くための回転"""
        dirs = ['N', 'E', 'S', 'W']
        current_idx = dirs.index(self.direction)
        target_idx = dirs.index(target_dir)
        diff = (target_idx - current_idx) % 4
        
        if diff == 1:
            return 'right'
        elif diff == 3:
            return 'left'
        elif diff == 2:
            return random.choice(['left', 'right'])
        else:
            return 'forward'
    
    def record_action(self, action, found_new):
        """行動結果を記憶"""
        self.action_memory.append({
            'pos': tuple(self.pos),
            'dir': self.direction,
            'action': action,
            'found_new': found_new
        })
    
    def update_pos(self, world):
        """位置を同期"""
        self.pos = world.hida_pos.copy()
        self.direction = world.hida_dir
    
    def known_cells(self):
        """知ってるマスの数"""
        return len(self.internal_map)
    
    def has_unknown_reachable(self):
        """行ける未知の場所があるか（マップ外は除外）"""
        dirs = ['N', 'E', 'S', 'W']
        deltas = {'N': (0, -1), 'E': (1, 0), 'S': (0, 1), 'W': (-1, 0)}
        
        # 既知の空きマスから、隣接する未知があるか
        for known_pos, cell in self.internal_map.items():
            if cell not in ['empty']:  # 壁、out、objectは除外
                continue
            
            for d in dirs:
                dx, dy = deltas[d]
                neighbor = (known_pos[0] + dx, known_pos[1] + dy)
                
                # マップ外と判明してる場所は除外
                if neighbor in self.internal_map and self.internal_map[neighbor] == 'out':
                    continue
                
                # 隣が未知なら、まだ行ける場所がある
                if neighbor not in self.internal_map:
                    return True
        
        return False
    
    def find_path(self, goal):
        """内部マップだけで経路を探す（BFS）"""
        from collections import deque
        
        start = tuple(self.pos)
        goal = tuple(goal)
        
        if start == goal:
            return [start]
        
        # ゴールがobjectの場合、ゴールの隣に到達したら成功
        goal_is_object = self.internal_map.get(goal) == 'object'
        
        # BFS
        queue = deque([(start, [start])])
        visited = {start}
        
        while queue:
            pos, path = queue.popleft()
            
            # 4方向
            for dx, dy in [(0, -1), (0, 1), (1, 0), (-1, 0)]:
                next_pos = (pos[0] + dx, pos[1] + dy)
                
                if next_pos in visited:
                    continue
                
                # ゴール到達チェック（objectでも隣なら成功）
                if next_pos == goal:
                    if goal_is_object:
                        # ゴールの隣（今のpos）まで行く
                        return path
                    else:
                        return path + [next_pos]
                
                # 内部マップで確認
                if next_pos not in self.internal_map:
                    continue  # 知らない場所は行けない
                
                cell = self.internal_map[next_pos]
                if cell in ['wall', 'out', 'object']:
                    continue  # 壁、外、オブジェクトは通れない
                # 'empty' と 'danger' は通れる
                
                visited.add(next_pos)
                queue.append((next_pos, path + [next_pos]))
        
        return None  # 経路なし
    
    def show_map(self, size=None):
        """内部マップを表示（サイズは自動検出）"""
        if not self.internal_map:
            print("\n内部マップ: 空")
            return
        
        # マップの範囲を自動検出
        xs = [p[0] for p in self.internal_map.keys()]
        ys = [p[1] for p in self.internal_map.keys()]
        min_x, max_x = min(xs), max(xs)
        min_y, max_y = min(ys), max(ys)
        
        # 壁とout以外をカウント
        real_cells = sum(1 for c in self.internal_map.values() if c not in ['out'])
        
        arrows = {'N': '^', 'S': 'v', 'E': '>', 'W': '<'}
        
        print(f"\n内部マップ（{real_cells}マス）:")
        for y in range(min_y, max_y + 1):
            row = ""
            for x in range(min_x, max_x + 1):
                key = (x, y)
                if [x, y] == self.pos:
                    row += f"[{arrows[self.direction]}]"
                elif key in self.internal_map:
                    cell = self.internal_map[key]
                    if cell == 'wall':
                        row += "[#]"
                    elif cell == 'out':
                        row += "[X]"
                    elif cell == 'object':
                        # オブジェクトの種類で表示
                        if key in self.found_objects:
                            obj = self.found_objects[key]
                            if obj.get('name') == 'goal':
                                row += "[G]"
                            elif obj.get('color') == 'red':
                                row += "[r]"
                            else:
                                row += "[o]"
                        else:
                            row += "[o]"
                    else:
                        row += "[.]"
                else:
                    row += "[?]"
            print(row)
        
        if self.holding:
            print(f"持ってる: {self.holding['name']} ({self.holding.get('color', '')})")
