"""
qualia.py
L2: クオリア層 - 予測誤差に感情的強度をつける
"""

class QualiaLayer:
    def __init__(self, color_preference=None):
        # 基本クオリア（DNA初期値）
        self.qualia = {
            'surprise': 0.0,   # 予測誤差で上がる
            'curiosity': 0.5,  # 未知で上がる（初期値あり）
            'fear': 0.0,       # 壁に囲まれると上がる
            'desire': 0.0,     # ボール/ゴール発見で上がる
            'urgency': 0.0,    # 急ぎ度（時間制約で上がる）
        }
        
        # 減衰率（1ステップごとに掛ける）
        self.decay = {
            'surprise': 0.8,   # 早く消える（驚きは一瞬）
            'curiosity': 0.95, # ゆっくり減る（興味は持続）
            'fear': 0.9,       # まあまあ残る（警戒は続く）
            'desire': 0.95,    # ゆっくり減る（目標は忘れない）
            'urgency': 0.98,   # ゆっくり減る（締め切りは迫る）
        }
        
        # 色の好み（DNA由来の個性）
        # 0.0 = 嫌い、0.5 = 普通、1.0 = 大好き
        if color_preference:
            self.color_preference = color_preference
        else:
            self.color_preference = {
                'red': 0.5,
                'blue': 0.5,
                'yellow': 0.5,
                'green': 0.5,
            }
    
    def get_color_desire(self, color):
        """色に対する欲求度を返す"""
        return self.color_preference.get(color, 0.5)
    
    def update(self, prediction_errors, found_objects, internal_map, pos):
        """状況からクオリアを更新"""
        
        # 1. まず減衰
        for key in self.qualia:
            self.qualia[key] *= self.decay[key]
        
        # 2. 予測誤差 → surprise
        if prediction_errors:
            self.qualia['surprise'] += len(prediction_errors) * 0.3
            self.qualia['surprise'] = min(self.qualia['surprise'], 1.0)
        
        # 3. 予測誤差の種類で分岐
        for error in prediction_errors:
            if error['actual'] == 'wall':
                # 壁が増えた → fear
                self.qualia['fear'] += 0.3
            elif error['actual'] == 'object':
                # 何か出現 → curiosity
                self.qualia['curiosity'] += 0.2
            elif error['actual'] == 'danger':
                # 危険ゾーン発見 → fear
                self.qualia['fear'] += 0.2
        
        self.qualia['fear'] = min(self.qualia['fear'], 1.0)
        self.qualia['curiosity'] = min(self.qualia['curiosity'], 1.0)
        
        # 4. 今いる場所が危険ゾーンなら fear 上昇
        current_cell = internal_map.get(tuple(pos))
        if current_cell == 'danger':
            self.qualia['fear'] += 0.15
            self.qualia['fear'] = min(self.qualia['fear'], 1.0)
            print(f"  ⚠️ 危険ゾーン通過！ fear={self.qualia['fear']:.2f}")
        
        # 4. ボール/ゴール発見 → desire
        for obj in found_objects.values():
            if obj.get('color') == 'red':  # ボール
                self.qualia['desire'] = max(self.qualia['desire'], 0.8)
            if obj.get('name') == 'goal':
                self.qualia['desire'] = max(self.qualia['desire'], 0.6)
        
        # 5. 未知マスが多い → curiosity維持
        unknown_neighbors = self._count_unknown_neighbors(internal_map, pos)
        if unknown_neighbors > 0:
            self.qualia['curiosity'] += unknown_neighbors * 0.05
            self.qualia['curiosity'] = min(self.qualia['curiosity'], 1.0)
        
        # 6. 壁に囲まれてる → fear
        wall_neighbors = self._count_wall_neighbors(internal_map, pos)
        if wall_neighbors >= 3:
            self.qualia['fear'] += 0.2
            self.qualia['fear'] = min(self.qualia['fear'], 1.0)
    
    def holding_update(self, holding):
        """ボール持ってたらdesire維持"""
        if holding:
            self.qualia['desire'] = max(self.qualia['desire'], 0.7)
    
    def _count_unknown_neighbors(self, internal_map, pos):
        """周囲の未知マス数"""
        count = 0
        for dx, dy in [(0, -1), (0, 1), (-1, 0), (1, 0)]:
            neighbor = (pos[0] + dx, pos[1] + dy)
            if neighbor not in internal_map:
                count += 1
        return count
    
    def _count_wall_neighbors(self, internal_map, pos):
        """周囲の壁の数"""
        count = 0
        for dx, dy in [(0, -1), (0, 1), (-1, 0), (1, 0)]:
            neighbor = (pos[0] + dx, pos[1] + dy)
            if internal_map.get(neighbor) in ['wall', 'out']:
                count += 1
        return count
    
    def get_dominant(self):
        """最も強いクオリアを返す"""
        return max(self.qualia, key=self.qualia.get)
    
    def show(self):
        """クオリア状態を表示"""
        bars = []
        for key, val in self.qualia.items():
            bar_len = int(val * 10)
            bar = '█' * bar_len + '░' * (10 - bar_len)
            bars.append(f"  {key:10s}: [{bar}] {val:.2f}")
        return '\n'.join(bars)
    
    def __repr__(self):
        return f"Qualia({self.qualia})"
