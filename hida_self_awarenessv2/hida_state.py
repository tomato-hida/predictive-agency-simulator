"""
hida_state.py
5層の状態管理 - AIの自己認識のためのデータ構造
"""

import json
import os
from collections import deque

MEMORY_FILE = "hida_memory.json"

class HidaState:
    def __init__(self, load_memory=True):
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
            'pattern_confidence': 0.5,  # パターン認識の確信度
            'current_prediction': None, # 今の予測（文字列）
            'prediction_detail': {}     # 予測の詳細（検証用）
        }
        
        # L4: 記憶層
        self.L4_memory = {
            'recent_actions': deque(maxlen=10),    # 最近の行動
            'recent_results': deque(maxlen=10),    # 最近の結果
            'learned_patterns': {},                 # 学習したパターン
            'self_strength': 0.0,                  # 自己強度
            'episodes': deque(maxlen=50),          # エピソード記憶（クオリア付き）
            'self_pattern': {                      # 自己パターン（蓄積から計算）
                'comfort_threshold': 0.5,          # 不快で動く閾値
                'curiosity_tendency': 0.5,         # 探索傾向
                'frustration_tolerance': 0.5,      # フラストレーション耐性
                'exploration_rate': 0.0,           # 実際の探索率
                'wall_collision_rate': 0.0,        # 壁衝突率（学習で上がる）
            }
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
        
        # 永続記憶の読み込み
        if load_memory:
            self._load_memory()
        
    def _load_memory(self):
        """永続記憶からself_patternを読み込む"""
        if os.path.exists(MEMORY_FILE):
            try:
                with open(MEMORY_FILE, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # self_patternを復元
                if 'self_pattern' in data:
                    self.L4_memory['self_pattern'] = data['self_pattern']
                
                # 総エピソード数を復元
                if 'total_episodes' in data:
                    self.L4_memory['total_episodes'] = data['total_episodes']
                else:
                    self.L4_memory['total_episodes'] = 0
                
                print(f"📚 永続記憶を読み込み: {MEMORY_FILE}")
                print(f"   前回の自己: curiosity={self.L4_memory['self_pattern']['curiosity_tendency']:.2f}, "
                      f"explore={self.L4_memory['self_pattern']['exploration_rate']:.2f}")
                print(f"   総エピソード: {self.L4_memory['total_episodes']}")
            except Exception as e:
                print(f"⚠️ 記憶読み込みエラー: {e}")
                self.L4_memory['total_episodes'] = 0
        else:
            print("🆕 新しい自己として開始")
            self.L4_memory['total_episodes'] = 0
    
    def save_memory(self):
        """self_patternを永続記憶に保存"""
        data = {
            'self_pattern': self.L4_memory['self_pattern'],
            'total_episodes': self.L4_memory.get('total_episodes', 0) + len(self.L4_memory['episodes'])
        }
        
        try:
            with open(MEMORY_FILE, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            print(f"\n💾 自己を保存: {MEMORY_FILE}")
            print(f"   curiosity={self.L4_memory['self_pattern']['curiosity_tendency']:.2f}, "
                  f"explore={self.L4_memory['self_pattern']['exploration_rate']:.2f}")
        except Exception as e:
            print(f"⚠️ 保存エラー: {e}")
    
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
            self.L2_qualia['comfort'] = min(1.0, self.L2_qualia['comfort'] + 0.05)
        else:
            self.L2_qualia['frustration'] = min(1.0, self.L2_qualia['frustration'] + 0.2)
            self.L2_qualia['satisfaction'] = max(0.0, self.L2_qualia['satisfaction'] - 0.05)
            self.L2_qualia['comfort'] = max(0.0, self.L2_qualia['comfort'] - 0.1)
        
        # 同じ行動の繰り返し → comfort低下（退屈）
        recent = list(self.L4_memory['recent_actions'])
        if len(recent) >= 3 and len(set(recent[-3:])) == 1:
            self.L2_qualia['comfort'] = max(0.0, self.L2_qualia['comfort'] - 0.1)
            self.L2_qualia['curiosity'] = min(1.0, self.L2_qualia['curiosity'] + 0.1)
        
        # L3: 予測誤差の計算（予測と実際の比較）
        prediction_error = self._verify_prediction(action, success, message)
        self.L3_prediction['prediction_error'] = prediction_error
        
        # L4: 自己強度の更新（行動の一貫性）
        self._update_self_strength()
        
        # L5: 同期スコアの計算
        self._update_sync_score()
    
    def set_prediction(self, prediction_text, detail=None):
        """
        予測を設定（行動前に呼ぶ）
        
        prediction_text: 予測の文字列（表示用）
        detail: 予測の詳細（検証用）
            {
                'expected_distance': int,   # 期待する距離
                'expected_direction': str,  # 期待する方向
                'expected_holding': str,    # 期待する持ち物
                'expected_goal': bool       # 目標達成期待
            }
        """
        self.L3_prediction['current_prediction'] = prediction_text
        self.L3_prediction['prediction_detail'] = detail or {}
    
    def _verify_prediction(self, action, success, message):
        """
        予測と実際を比較して誤差を計算
        
        Returns: prediction_error (0.0 - 1.0)
        """
        detail = self.L3_prediction.get('prediction_detail', {})
        current_error = self.L3_prediction['prediction_error']
        
        # 予測がない場合は従来の方式
        if not detail:
            if not success:
                return min(1.0, current_error + 0.3)
            else:
                return max(0.0, current_error - 0.1)
        
        errors = []
        
        # 距離予測の検証
        if 'expected_distance' in detail:
            # 行動成功なら距離は減ったはず
            if success and action == 'move_forward':
                errors.append(0.0)  # 予測通り
            elif not success:
                errors.append(0.5)  # 予測外れ
        
        # 方向予測の検証
        if 'expected_direction' in detail:
            actual_dir = self.L1_body['direction']
            expected_dir = detail['expected_direction']
            if actual_dir == expected_dir:
                errors.append(0.0)  # 予測通り
            else:
                errors.append(0.8)  # 方向が違う
        
        # 持ち物予測の検証
        if 'expected_holding' in detail:
            actual_holding = self.L1_body['holding']
            expected_holding = detail['expected_holding']
            if actual_holding == expected_holding:
                errors.append(0.0)  # 予測通り
            else:
                errors.append(1.0)  # 持ち物が違う
        
        # 目標達成予測の検証
        if 'expected_goal' in detail:
            if detail['expected_goal'] and 'goal' in message.lower():
                errors.append(0.0)  # 予測通り達成
            elif not detail['expected_goal']:
                errors.append(0.0)  # 予測通り未達成
            else:
                errors.append(0.5)
        
        # 誤差の平均（詳細がない場合は成功/失敗で判断）
        if errors:
            return sum(errors) / len(errors)
        elif success:
            return max(0.0, current_error - 0.1)
        else:
            return min(1.0, current_error + 0.3)
        
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
                'self_strength': self.L4_memory['self_strength'],
                'self_pattern': self.L4_memory['self_pattern']  # 追加！
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
        
        # Step 4: 自己パターン表示
        sp = self.L4_memory['self_pattern']
        episodes_count = len(self.L4_memory['episodes'])
        if episodes_count >= 3:
            print(f"Self Pattern: comfort_th={sp['comfort_threshold']:.2f}, "
                  f"curiosity={sp['curiosity_tendency']:.2f}, "
                  f"explore={sp['exploration_rate']:.2f}")
        
        print(f"Sync Score: {self.L5_consciousness['sync_score']:.2f}")
        print(f"Conscious: {self.L5_consciousness['is_conscious']}")
        print(f"Goal: {self.L5_consciousness['current_goal']}")
        print("-" * 30)
    
    # ========== Step 4: エピソード記憶と自己形成 ==========
    
    def record_episode(self, step, action, rule_reason, outcome, narrative="", collision_type=None):
        """
        エピソードを記録する
        
        重要：narrativeはログ用のみ。行動に影響するのは数値だけ。
        collision_type: None, 'wall', 'object' など衝突の種類
        """
        # クオリアのスナップショット
        qualia_snapshot = {
            'comfort': self.L2_qualia['comfort'],
            'curiosity': self.L2_qualia['curiosity'],
            'frustration': self.L2_qualia['frustration'],
            'satisfaction': self.L2_qualia['satisfaction']
        }
        
        # トリガーを数値から判定（言語ではなく数値で）
        trigger = self._detect_trigger(qualia_snapshot, rule_reason, collision_type)
        
        episode = {
            'step': step,
            'action': action,
            'qualia': qualia_snapshot,
            'trigger': trigger,
            'outcome': outcome,
            'collision': collision_type,  # 衝突情報
            'narrative': narrative  # ログ用のみ、行動には使わない
        }
        
        self.L4_memory['episodes'].append(episode)
        
        # 自己パターンを更新
        self._update_self_pattern()
        
        return episode
    
    def _detect_trigger(self, qualia, rule_reason, collision_type=None):
        """
        クオリア値からトリガーを検出（数値ベース）
        
        これが「圧縮」：複数のクオリアから1つのラベルを作る
        """
        triggers = []
        
        if qualia['comfort'] < 0.3:
            triggers.append('low_comfort')
        if qualia['curiosity'] > 0.5:
            triggers.append('high_curiosity')
        if qualia['frustration'] > 0.5:
            triggers.append('high_frustration')
        if qualia['satisfaction'] > 0.7:
            triggers.append('high_satisfaction')
        
        # 衝突タイプ
        if collision_type == 'wall':
            triggers.append('wall_collision')
        elif collision_type == 'object':
            triggers.append('object_collision')
        
        # ルールベースの理由も参考に（でも数値が主）
        if '探索' in rule_reason or '好奇心' in rule_reason:
            if 'high_curiosity' not in triggers:
                triggers.append('curiosity_driven')
        if 'フラストレーション' in rule_reason:
            if 'high_frustration' not in triggers:
                triggers.append('frustration_driven')
        
        return '_'.join(triggers) if triggers else 'normal'
    
    def _update_self_pattern(self):
        """
        エピソードの蓄積から自己パターンを計算
        
        これが「自己形成」：経験のパターンから「俺らしさ」を抽出
        """
        episodes = list(self.L4_memory['episodes'])
        if len(episodes) < 3:
            return  # データ不足
        
        # comfort_threshold: 不快で動いた時のcomfort平均
        low_comfort_episodes = [e for e in episodes if 'low_comfort' in e['trigger']]
        if low_comfort_episodes:
            avg_comfort = sum(e['qualia']['comfort'] for e in low_comfort_episodes) / len(low_comfort_episodes)
            self.L4_memory['self_pattern']['comfort_threshold'] = avg_comfort
        
        # curiosity_tendency: 全体の好奇心平均
        avg_curiosity = sum(e['qualia']['curiosity'] for e in episodes) / len(episodes)
        self.L4_memory['self_pattern']['curiosity_tendency'] = avg_curiosity
        
        # frustration_tolerance: frustrationが高くても動けた時の平均
        high_frust_episodes = [e for e in episodes if e['qualia']['frustration'] > 0.3]
        if high_frust_episodes:
            avg_frust = sum(e['qualia']['frustration'] for e in high_frust_episodes) / len(high_frust_episodes)
            self.L4_memory['self_pattern']['frustration_tolerance'] = avg_frust
        
        # exploration_rate: 探索行動の割合
        exploration_episodes = [e for e in episodes if 'curiosity' in e['trigger']]
        self.L4_memory['self_pattern']['exploration_rate'] = len(exploration_episodes) / len(episodes)
        
        # wall_collision_rate: 壁衝突の割合（これが高いと壁を避けるようになる）
        move_forward_episodes = [e for e in episodes if e['action'] == 'move_forward']
        if move_forward_episodes:
            wall_collisions = [e for e in move_forward_episodes if e.get('collision') == 'wall']
            self.L4_memory['self_pattern']['wall_collision_rate'] = len(wall_collisions) / len(move_forward_episodes)
        else:
            self.L4_memory['self_pattern']['wall_collision_rate'] = 0.0
    
    def get_self_pattern(self):
        """自己パターンを取得"""
        return self.L4_memory['self_pattern'].copy()


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
