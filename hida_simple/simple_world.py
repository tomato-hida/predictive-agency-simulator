"""
simple_world.py
5x5グリッドの仮想環境
"""

import random

class SimpleWorld:
    def __init__(self, size=5):
        self.size = size
        self.grid = [[None for _ in range(size)] for _ in range(size)]
        self.objects = {}
        self.hida_pos = [2, 2]  # 中央からスタート
        self.hida_dir = 'N'     # 北向き
        self.hida_holding = None
        
    def add_object(self, name, x, y, properties=None):
        """オブジェクトを配置"""
        if 0 <= x < self.size and 0 <= y < self.size:
            self.objects[name] = {
                'pos': [x, y],
                'properties': properties or {}
            }
            self.grid[y][x] = name
            
    def get_sensor_data(self):
        """飛騨のセンサーデータを取得"""
        x, y = self.hida_pos
        
        # 前方のオブジェクト
        front = self._get_front_pos()
        front_obj = None
        if front and 0 <= front[0] < self.size and 0 <= front[1] < self.size:
            front_obj = self.grid[front[1]][front[0]]
        
        # 周囲のオブジェクト
        nearby = []
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                nx, ny = x + dx, y + dy
                if 0 <= nx < self.size and 0 <= ny < self.size:
                    if self.grid[ny][nx]:
                        nearby.append({
                            'name': self.grid[ny][nx],
                            'direction': self._get_direction(dx, dy),
                            'distance': 1
                        })
        
        return {
            'position': self.hida_pos.copy(),
            'direction': self.hida_dir,
            'front_object': front_obj,
            'nearby_objects': nearby,
            'holding': self.hida_holding
        }
    
    def _get_front_pos(self):
        """前方の座標を取得"""
        x, y = self.hida_pos
        if self.hida_dir == 'N': return [x, y-1]
        if self.hida_dir == 'S': return [x, y+1]
        if self.hida_dir == 'E': return [x+1, y]
        if self.hida_dir == 'W': return [x-1, y]
        
    def _get_direction(self, dx, dy):
        """相対方向を文字列で"""
        if dy < 0: return 'N'
        if dy > 0: return 'S'
        if dx > 0: return 'E'
        if dx < 0: return 'W'
        return 'here'
    
    # === プリミティブ動作 ===
    
    def move_forward(self):
        """前進"""
        front = self._get_front_pos()
        if front and 0 <= front[0] < self.size and 0 <= front[1] < self.size:
            # オブジェクトがなければ移動可能
            if self.grid[front[1]][front[0]] is None:
                self.hida_pos = front
                return True, "moved forward"
            return False, "blocked by object"
        return False, "wall"
    
    def turn_left(self):
        """左回転"""
        turns = {'N': 'W', 'W': 'S', 'S': 'E', 'E': 'N'}
        self.hida_dir = turns[self.hida_dir]
        return True, f"turned left, now facing {self.hida_dir}"
    
    def turn_right(self):
        """右回転"""
        turns = {'N': 'E', 'E': 'S', 'S': 'W', 'W': 'N'}
        self.hida_dir = turns[self.hida_dir]
        return True, f"turned right, now facing {self.hida_dir}"
    
    def grab(self):
        """前方のオブジェクトを掴む"""
        if self.hida_holding:
            return False, "already holding something"
        front = self._get_front_pos()
        if front and 0 <= front[0] < self.size and 0 <= front[1] < self.size:
            obj = self.grid[front[1]][front[0]]
            if obj and obj != 'goal' and not obj.startswith('wall'):
                self.hida_holding = obj
                self.grid[front[1]][front[0]] = None
                # objectsからも削除
                if obj in self.objects:
                    del self.objects[obj]
                return True, f"grabbed {obj}"
        return False, "nothing to grab"
    
    def release(self):
        """持っているオブジェクトを前方に置く"""
        if not self.hida_holding:
            return False, "not holding anything"
        front = self._get_front_pos()
        if front and 0 <= front[0] < self.size and 0 <= front[1] < self.size:
            front_obj = self.grid[front[1]][front[0]]
            if front_obj is None or front_obj == 'goal':
                # goal上に置く場合もOK
                obj = self.hida_holding
                self.hida_holding = None
                if front_obj != 'goal':
                    self.grid[front[1]][front[0]] = obj
                return True, f"released {obj}" + (" at goal!" if front_obj == 'goal' else "")
        return False, "cannot release here"
    
    def execute_primitive(self, action):
        """プリミティブを実行"""
        actions = {
            'move_forward': self.move_forward,
            'turn_left': self.turn_left,
            'turn_right': self.turn_right,
            'grab': self.grab,
            'release': self.release
        }
        if action in actions:
            return actions[action]()
        return False, f"unknown action: {action}"
    
    def get_legal_actions(self):
        """実行可能な行動のリストを返す"""
        legal = ['turn_left', 'turn_right', 'wait']  # 常に可能
        
        # move_forward: 正面がマップ外でなければ常に選択肢
        # （壁にぶつかるかは実行してみないとわからない＝学習対象）
        front = self._get_front_pos()
        if front and 0 <= front[0] < self.size and 0 <= front[1] < self.size:
            legal.append('move_forward')
        
        # grab: 手が空で、正面にオブジェクトがある（goal、wallは掴めない）
        if not self.hida_holding:
            if front and 0 <= front[0] < self.size and 0 <= front[1] < self.size:
                front_obj = self.grid[front[1]][front[0]]
                if front_obj is not None and front_obj != 'goal' and not front_obj.startswith('wall'):
                    legal.append('grab')
        
        # release: 何か持っていて、正面が空いているか、goalがある
        if self.hida_holding:
            if front and 0 <= front[0] < self.size and 0 <= front[1] < self.size:
                front_obj = self.grid[front[1]][front[0]]
                if front_obj is None or front_obj == 'goal':
                    legal.append('release')
        
        return legal
    
    def get_front_cell(self):
        """正面のセルの内容を返す"""
        front = self._get_front_pos()
        if front and 0 <= front[0] < self.size and 0 <= front[1] < self.size:
            obj = self.grid[front[1]][front[0]]
            return obj if obj else 'empty'
        return 'wall'
    
    def find_object(self, name):
        """オブジェクトの位置を返す"""
        for obj_name, obj_data in self.objects.items():
            if name in obj_name:
                return obj_data['pos']
        return None
    
    def display(self):
        """グリッドを表示"""
        print("\n" + "="*(self.size*3))
        for y in range(self.size):
            row = ""
            for x in range(self.size):
                if [x, y] == self.hida_pos:
                    # 飛騨の向きを表示
                    arrows = {'N': '^', 'S': 'v', 'E': '>', 'W': '<'}
                    row += f"[{arrows[self.hida_dir]}]"
                elif self.grid[y][x]:
                    obj = self.grid[y][x]
                    if obj.startswith('wall'):
                        row += "[#]"  # 壁
                    else:
                        row += f"[{obj[0]}]"  # 頭文字
                else:
                    row += "[ ]"
            print(row)
        print("="*(self.size*3))
        if self.hida_holding:
            print(f"Holding: {self.hida_holding}")


# テスト
if __name__ == "__main__":
    world = SimpleWorld()
    world.add_object("red_ball", 1, 1, {"color": "red", "size": "small"})
    world.add_object("blue_box", 3, 0, {"color": "blue", "size": "large"})
    world.add_object("goal", 4, 4, {"type": "destination"})
    
    world.display()
    print("\nSensor data:", world.get_sensor_data())
    
    # テスト動作
    world.turn_left()
    world.move_forward()
    world.display()
