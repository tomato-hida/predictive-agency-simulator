"""
world.py
5x5グリッド - 神は全部見える、HIDAは前方1マスだけ
"""

class World:
    def __init__(self, size=5):
        self.size = size
        self.grid = [[None for _ in range(size)] for _ in range(size)]
        self.hida_pos = [2, 2]
        self.hida_dir = 'N'
        self.objects = {}  # 位置 → オブジェクト
        self.hida_holding = None  # 持ってるもの
    
    def add_wall(self, x, y):
        """壁を配置"""
        self.grid[y][x] = 'wall'
    
    def add_object(self, name, x, y, color=None):
        """オブジェクトを配置"""
        self.objects[(x, y)] = {'name': name, 'color': color}
    
    def get_pos_in_dir(self, direction):
        """指定方向の座標"""
        x, y = self.hida_pos
        if direction == 'N': return [x, y-1]
        if direction == 'S': return [x, y+1]
        if direction == 'E': return [x+1, y]
        if direction == 'W': return [x-1, y]
    
    def see_cell(self, pos):
        """指定座標を見る"""
        x, y = pos
        if x < 0 or x >= self.size or y < 0 or y >= self.size:
            return {'type': 'out'}
        if self.grid[y][x] == 'wall':
            return {'type': 'wall'}
        
        # オブジェクトがあるか
        if (x, y) in self.objects:
            obj = self.objects[(x, y)]
            return {'type': 'object', 'name': obj['name'], 'color': obj['color']}
        
        return {'type': 'empty'}
    
    def get_front_pos(self):
        """前方の座標"""
        return self.get_pos_in_dir(self.hida_dir)
    
    def see_front(self):
        """前方1マスを見る"""
        front = self.get_front_pos()
        return self.see_cell(front)
    
    def look_around(self):
        """首を回して4方向を見渡す"""
        result = {}
        for direction in ['N', 'E', 'S', 'W']:
            pos = self.get_pos_in_dir(direction)
            result[direction] = {
                'pos': pos,
                'cell': self.see_cell(pos)
            }
        return result
    
    def move_forward(self):
        """前進"""
        front = self.get_front_pos()
        fx, fy = front
        
        if fx < 0 or fx >= self.size or fy < 0 or fy >= self.size:
            return False, "マップ外"
        
        if self.grid[fy][fx] == 'wall':
            return False, "壁"
        
        self.hida_pos = front
        return True, "移動した"
    
    def turn_left(self):
        turns = {'N': 'W', 'W': 'S', 'S': 'E', 'E': 'N'}
        self.hida_dir = turns[self.hida_dir]
        return True, f"{self.hida_dir}向き"
    
    def turn_right(self):
        turns = {'N': 'E', 'E': 'S', 'S': 'W', 'W': 'N'}
        self.hida_dir = turns[self.hida_dir]
        return True, f"{self.hida_dir}向き"
    
    def grab(self):
        """目の前のものをつかむ"""
        front = self.get_front_pos()
        key = tuple(front)
        
        if key in self.objects:
            obj = self.objects[key]
            del self.objects[key]
            self.hida_holding = obj
            return True, f"{obj['name']}をつかんだ"
        
        return False, "何もない"
    
    def release(self):
        """持ってるものを前に置く"""
        if not self.hida_holding:
            return False, "何も持ってない"
        
        front = self.get_front_pos()
        key = tuple(front)
        fx, fy = front
        
        # 置ける場所か確認
        if fx < 0 or fx >= self.size or fy < 0 or fy >= self.size:
            return False, "マップ外"
        if self.grid[fy][fx] == 'wall':
            return False, "壁"
        
        # ゴールの上は置ける、それ以外のオブジェクトはダメ
        if key in self.objects:
            if self.objects[key].get('name') != 'goal':
                return False, "何かある"
            # ゴールの場合、ゴールを消してボールを置く（ゴール達成）
            del self.objects[key]
        
        # 置く
        obj = self.hida_holding
        self.objects[key] = obj
        self.hida_holding = None
        return True, f"{obj['name']}をゴールに置いた"
    
    def tick(self, move_probability=0.3):
        """世界が1ステップ進む（壁が動く）"""
        import random
        
        moved = []
        
        # 動く壁のリストを取得（内壁のみ、外壁は動かない）
        moving_walls = []
        for y in range(1, self.size - 1):
            for x in range(1, self.size - 1):
                if self.grid[y][x] == 'wall':
                    moving_walls.append((x, y))
        
        for pos in moving_walls:
            if random.random() < move_probability:
                x, y = pos
                directions = [(0, -1), (0, 1), (-1, 0), (1, 0)]
                random.shuffle(directions)
                
                for dx, dy in directions:
                    nx, ny = x + dx, y + dy
                    # 移動先が有効か確認
                    if 1 <= nx < self.size - 1 and 1 <= ny < self.size - 1:
                        if self.grid[ny][nx] != 'wall':  # 壁じゃない
                            if (nx, ny) not in self.objects:  # オブジェクトがない
                                if [nx, ny] != self.hida_pos:  # HIDAがいない
                                    # 壁を移動
                                    self.grid[y][x] = None
                                    self.grid[ny][nx] = 'wall'
                                    moved.append({
                                        'type': 'wall',
                                        'from': pos,
                                        'to': (nx, ny)
                                    })
                                    break
        
        return moved
    
    def display(self, internal_map=None):
        """表示（神視点）"""
        arrows = {'N': '^', 'S': 'v', 'E': '>', 'W': '<'}
        
        print("\n=== 神視点 ===")
        for y in range(self.size):
            row = ""
            for x in range(self.size):
                if [x, y] == self.hida_pos:
                    row += f"[{arrows[self.hida_dir]}]"
                elif self.grid[y][x] == 'wall':
                    row += "[#]"
                elif (x, y) in self.objects:
                    obj = self.objects[(x, y)]
                    if obj.get('color') == 'red':
                        row += "[r]"
                    elif obj.get('name') == 'goal':
                        row += "[G]"
                    else:
                        row += "[o]"
                else:
                    row += "[ ]"
            print(row)
        
        if self.hida_holding:
            print(f"持ってる: {self.hida_holding['name']}")
