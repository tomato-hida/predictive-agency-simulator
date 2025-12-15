"""
hida_state.py
5層の状態管理 - AIの自己認識のためのデータ構造
"""

import json
from collections import deque

class HidaState:
    def __init__(self):
        # L1: 身体層
        self.L1_body = {
            'position': [0, 0],
            'direction': 'N',
            'holding': None,
            'sensor_data': {}
        }
        
        # L2: クオリア層（状態の快/不快）
        self.L2_qualia = {
            'comfort': 0.5,      # 全体的な快適さ (0-1)
            'curiosity': 0.5,    # 好奇心/興味 (0-1)
            'frustration': 0.0, # フラストレーション (0-1)
            'satisfaction': 0.0 # 達成感 (0-1)
        }
        
        # L3: 予測層
        self.L3_prediction = {
            'expected_next': None,      # 次に起こると予測していること
            'prediction_error': 0.0,    # 予測誤差
            'pattern_confidence': 0.5   # パターン認識の確信度
        }
        
        # L4: 記憶層
        self.L4_memory = {
            'recent_actions': deque(maxlen=10),    # 最近の行動
            'recent_results': deque(maxlen=10),    # 最近の結果
            'learned_patterns': {},                 # 学習したパターン
            'self_strength': 0.0                   # 自己強度
        }
        
        # L5: 意識層
        self.L5_consciousness = {
            'sync_score': 0.0,          # 同期スコア
            'is_conscious': False,       # 意識ON/OFF
            'current_goal': None,        # 現在の目標
            'attention_focus': None      # 注意の焦点
        }
        
        # 履歴
        self.history = []
        
    def update_from_world(self, world):
        """ワールドから状態を更新"""
        sensor = world.get_sensor_data()
        
        # L1更新
        self.L1_body['position'] = sensor['position']
        self.L1_body['direction'] = sensor['direction']
        self.L1_body['holding'] = sensor['holding']
        self.L1_body['sensor_data'] = sensor
        
    def update_after_action(self, action, success, message):
        """行動後の状態更新"""
        # L4: 記憶に追加
        self.L4_memory['recent_actions'].append(action)
        self.L4_memory['recent_results'].append({
            'success': success,
            'message': message
        })
        
        # L2: クオリア更新
        if success:
            self.L2_qualia['satisfaction'] = min(1.0, self.L2_qualia['satisfaction'] + 0.1)
            self.L2_qualia['frustration'] = max(0.0, self.L2_qualia['frustration'] - 0.1)
        else:
            self.L2_qualia['frustration'] = min(1.0, self.L2_qualia['frustration'] + 0.2)
            self.L2_qualia['satisfaction'] = max(0.0, self.L2_qualia['satisfaction'] - 0.05)
        
        # L3: 予測誤差の計算（実際の結果で更新）
        if not success:
            # 失敗 = 予測誤差大
            self.L3_prediction['prediction_error'] = min(1.0, 
                self.L3_prediction['prediction_error'] + 0.3)
        else:
            # 成功 = 予測誤差減少
            self.L3_prediction['prediction_error'] = max(0.0,
                self.L3_prediction['prediction_error'] - 0.1)
        
        # L4: 自己強度の更新（行動の一貫性）
        self._update_self_strength()
        
        # L5: 同期スコアの計算
        self._update_sync_score()
        
    def _update_self_strength(self):
        """自己強度の更新 - 行動の成功に基づく"""
        actions = list(self.L4_memory['recent_actions'])
        results = list(self.L4_memory['recent_results'])
        
        if not actions:
            return
            
        last_action = actions[-1]
        last_result = results[-1] if results else {'success': False}
        
        # 穴①修正: waitでは自己強度を上げない、むしろ減衰
        if last_action == 'wait':
            self.L4_memory['self_strength'] = max(0.0,
                self.L4_memory['self_strength'] * 0.95)
            return
        
        # 行動成功時のみ上昇
        if last_result.get('success', False):
            self.L4_memory['self_strength'] = min(1.0, 
                self.L4_memory['self_strength'] + 0.05)
        else:
            # 失敗時は減少
            self.L4_memory['self_strength'] = max(0.0,
                self.L4_memory['self_strength'] - 0.05)
                    
    def _update_sync_score(self):
        """同期スコアの計算 - 4層がどれだけ連携しているか"""
        scores = []
        
        # L1-L2連携: 身体状態とクオリアの整合性
        if self.L1_body['holding']:
            scores.append(0.7)  # 何か持っている = 能動的
        else:
            scores.append(0.3)
            
        # L2-L3連携: 予測と感情の整合性
        if self.L3_prediction['prediction_error'] > 0.5:
            # 予測誤差大 → 注意が必要 → 同期必要
            scores.append(0.8)
        else:
            scores.append(0.4)
            
        # L3-L4連携: 予測と記憶の整合性
        if self.L4_memory['self_strength'] > 0.3:
            scores.append(0.6)
        else:
            scores.append(0.3)
            
        # L4-L5連携: 記憶と目標の整合性
        if self.L5_consciousness['current_goal']:
            scores.append(0.7)
        else:
            scores.append(0.2)
        
        self.L5_consciousness['sync_score'] = sum(scores) / len(scores)
        
        # 意識ON/OFF判定
        self.L5_consciousness['is_conscious'] = (
            self.L5_consciousness['sync_score'] >= 0.3 and
            self.L4_memory['self_strength'] >= 0.2
        )
        
    def set_goal(self, goal):
        """目標を設定"""
        self.L5_consciousness['current_goal'] = goal
        self.L2_qualia['curiosity'] = 0.7
        
    def to_json(self):
        """AI向けにJSON形式で出力"""
        return {
            'L1_body': self.L1_body,
            'L2_qualia': self.L2_qualia,
            'L3_prediction': {
                'expected_next': self.L3_prediction['expected_next'],
                'prediction_error': self.L3_prediction['prediction_error'],
                'pattern_confidence': self.L3_prediction['pattern_confidence']
            },
            'L4_memory': {
                'recent_actions': list(self.L4_memory['recent_actions']),
                'recent_results': list(self.L4_memory['recent_results']),
                'self_strength': self.L4_memory['self_strength']
            },
            'L5_consciousness': self.L5_consciousness
        }
        
    def to_json_string(self):
        """JSON文字列で出力"""
        return json.dumps(self.to_json(), indent=2, ensure_ascii=False)
    
    def summary(self):
        """状態のサマリーを表示"""
        print("\n--- HIDA State Summary ---")
        print(f"Position: {self.L1_body['position']}, Facing: {self.L1_body['direction']}")
        print(f"Holding: {self.L1_body['holding']}")
        print(f"Qualia: comfort={self.L2_qualia['comfort']:.2f}, "
              f"frustration={self.L2_qualia['frustration']:.2f}")
        print(f"Prediction Error: {self.L3_prediction['prediction_error']:.2f}")
        print(f"Self Strength: {self.L4_memory['self_strength']:.2f}")
        print(f"Sync Score: {self.L5_consciousness['sync_score']:.2f}")
        print(f"Conscious: {self.L5_consciousness['is_conscious']}")
        print(f"Goal: {self.L5_consciousness['current_goal']}")
        print("-" * 30)


# テスト
if __name__ == "__main__":
    state = HidaState()
    state.set_goal("find red ball")
    
    # 擬似的な行動
    state.update_after_action("move_forward", True, "moved")
    state.update_after_action("turn_left", True, "turned")
    state.update_after_action("move_forward", False, "blocked")
    
    state.summary()
    print("\nJSON for AI:")
    print(state.to_json_string())
