"""
hida_state.py
シンプル版 - 記憶だけ

クオリアなし、好奇心なし、意識ONなし
基本：位置、向き、持ち物、記憶
"""

import json
import os
from collections import deque

MEMORY_FILE = "hida_memory.json"


class HidaState:
    def __init__(self):
        # 身体状態
        self.position = [0, 0]
        self.direction = 'N'
        self.holding = None
        
        # 短期記憶（最近の経験）
        self.recent_results = deque(maxlen=20)
        
        # 教わったこと
        self.teachings = []
        
        # 目標
        self.goal = None
        
        # 永続記憶を読み込む
        self._load_memory()
    
    def _load_memory(self):
        """永続記憶から読み込む"""
        if os.path.exists(MEMORY_FILE):
            try:
                with open(MEMORY_FILE, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                if 'teachings' in data:
                    self.teachings = data['teachings']
                    print(f"📚 記憶を読み込み: 教え{len(self.teachings)}件")
            except Exception as e:
                print(f"⚠️ 読み込みエラー: {e}")
        else:
            print("🆕 新しい記憶で開始")
    
    def save_memory(self):
        """永続記憶に保存"""
        data = {
            'teachings': self.teachings
        }
        try:
            with open(MEMORY_FILE, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            print(f"💾 記憶を保存: 教え{len(self.teachings)}件")
        except Exception as e:
            print(f"⚠️ 保存エラー: {e}")
    
    def update_from_world(self, world):
        """ワールドから状態を更新"""
        sensor = world.get_sensor_data()
        self.position = sensor['position']
        self.direction = sensor['direction']
        self.holding = sensor['holding']
    
    def record_result(self, action, success, message):
        """行動結果を記憶"""
        self.recent_results.append({
            'position': self.position.copy(),
            'direction': self.direction,
            'action': action,
            'success': success,
            'message': message
        })
    
    def add_teaching(self, condition, action, source="unknown"):
        """教えを記憶"""
        from datetime import datetime
        teaching = {
            "condition": condition,
            "action": action,
            "source": source,
            "learned_at": datetime.now().isoformat()
        }
        self.teachings.append(teaching)
        print(f"📖 教え: 「{condition}」→「{action}」 (from {source})")
        self.save_memory()
    
    def set_goal(self, goal):
        """目標を設定"""
        self.goal = goal
    
    def summary(self):
        """状態表示"""
        print(f"\n--- 状態 ---")
        print(f"位置: {self.position}, 向き: {self.direction}")
        print(f"持ち物: {self.holding}")
        print(f"目標: {self.goal}")
        print(f"記憶: {len(self.recent_results)}件")
        print(f"------------")
