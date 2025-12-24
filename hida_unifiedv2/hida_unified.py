"""
hida_unified.py
HIDA統合版 - 5層意識モデル + LLM言語化

L1: 身体層（プリミティブ、エネルギー）
L2: クオリア層（valence/arousal + 個別感情）
L3: 予測・構造化層（予測誤差）
L4: 記憶層（内部マップ、発見物、ラベル辞書）
L5: 意識層（自認、言語化、コミュニケーション）
"""

import math
import random
import subprocess
import json
import urllib.request
import urllib.error
import os
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
from enum import Enum


# ==========================================
# L1: 身体層
# ==========================================

class L1Body:
    """身体プリミティブとエネルギー管理"""
    
    def __init__(self):
        # 位置・方向
        self.position = [0, 0]
        self.direction = 'N'  # N, E, S, W
        
        # 身体状態
        self.energy = 1.0
        self.fatigue = 0.0
        self.damage = 0.0
        
        # 所持
        self.holding = None
        
        # 感覚バッファ（最新の知覚）
        self.sense_buffer = {}
    
    def move_forward(self, world) -> bool:
        """前進"""
        dx, dy = {'N': (0, -1), 'S': (0, 1), 'E': (1, 0), 'W': (-1, 0)}[self.direction]
        new_pos = [self.position[0] + dx, self.position[1] + dy]
        
        # 壁チェック
        if world.get_cell(new_pos[0], new_pos[1]) == 'wall':
            return False
        
        self.position = new_pos
        self._consume_energy(0.02)
        return True
    
    def turn_left(self):
        """左回転"""
        dirs = ['N', 'W', 'S', 'E']
        self.direction = dirs[(dirs.index(self.direction) + 1) % 4]
        self._consume_energy(0.005)
    
    def turn_right(self):
        """右回転"""
        dirs = ['N', 'E', 'S', 'W']
        self.direction = dirs[(dirs.index(self.direction) + 1) % 4]
        self._consume_energy(0.005)
    
    def grab(self, obj):
        """掴む"""
        self.holding = obj
        self._consume_energy(0.01)
    
    def release(self):
        """離す"""
        released = self.holding
        self.holding = None
        self._consume_energy(0.01)
        return released
    
    def look(self, world) -> Dict:
        """周囲を見る（感覚入力）"""
        visible = {}
        x, y = self.position
        
        # 周囲8方向 + 前方3マス
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                nx, ny = x + dx, y + dy
                cell = world.get_cell(nx, ny)
                obj = world.get_object(nx, ny)
                visible[(nx, ny)] = {'cell': cell, 'object': obj}
        
        # 前方を遠くまで見る
        fdx, fdy = {'N': (0, -1), 'S': (0, 1), 'E': (1, 0), 'W': (-1, 0)}[self.direction]
        for dist in range(1, 5):
            fx, fy = x + fdx * dist, y + fdy * dist
            cell = world.get_cell(fx, fy)
            if cell == 'wall':
                break
            obj = world.get_object(fx, fy)
            visible[(fx, fy)] = {'cell': cell, 'object': obj}
        
        self.sense_buffer = visible
        self._consume_energy(0.005)
        return visible
    
    def _consume_energy(self, amount: float):
        """エネルギー消費"""
        self.energy = max(0, self.energy - amount)
        self.fatigue = min(1.0, self.fatigue + amount * 0.3)
    
    def rest(self):
        """休憩（エネルギー回復）"""
        self.energy = min(1.0, self.energy + 0.05)
        self.fatigue = max(0, self.fatigue - 0.03)
    
    def get_state(self) -> Dict:
        return {
            'position': self.position.copy(),
            'direction': self.direction,
            'energy': self.energy,
            'fatigue': self.fatigue,
            'damage': self.damage,
            'holding': self.holding
        }


# ==========================================
# L2: クオリア層
# ==========================================

class L2Qualia:
    """クオリア（感情的評価）"""
    
    def __init__(self, color_preference=None):
        # 基本2軸（Russell円環モデル）
        self.valence = 0.0   # 快-不快 (-1 to 1)
        self.arousal = 0.0   # 覚醒-沈静 (-1 to 1)
        
        # 個別クオリア（基本軸から派生 or 直接設定）
        self.qualia = {
            'fear': 0.0,       # 恐怖
            'desire': 0.0,     # 欲求
            'surprise': 0.0,   # 驚き
            'curiosity': 0.5,  # 好奇心
            'urgency': 0.0,    # 緊急度
            'anger': 0.0,      # 怒り（新規）
            'sadness': 0.0,    # 悲しみ（新規）
            'joy': 0.0,        # 喜び（新規）
            'disgust': 0.0,    # 嫌悪（新規）
        }
        
        # 減衰率
        self.decay = {
            'fear': 0.9,
            'desire': 0.95,
            'surprise': 0.7,
            'curiosity': 0.98,
            'urgency': 0.95,
            'anger': 0.85,     # 怒りは比較的早く収まる
            'sadness': 0.92,   # 悲しみはゆっくり消える
            'joy': 0.9,        # 喜びも比較的早く消える
            'disgust': 0.8,    # 嫌悪は早く消える
        }
        
        # 色の好み（DNA由来）
        self.color_preference = color_preference or {
            'red': 0.5, 'blue': 0.5, 'yellow': 0.5, 'green': 0.5
        }
        
        # 変調値（経験から）
        self.modulation = {
            'fear_weight': 1.0,
            'safe_preference': 0.0,
            'energy_caution': 0.0
        }
    
    def apply_modulation(self, mod: Dict):
        """変調値を適用"""
        self.modulation = mod.copy()
    
    def update_from_body(self, l1_state: Dict):
        """L1身体状態からクオリア更新"""
        energy = l1_state['energy']
        fatigue = l1_state['fatigue']
        damage = l1_state['damage']
        
        # エネルギー低下 → 不快 + 沈静 + urgency
        if energy < 0.3:
            self.valence -= 0.1
            self.arousal -= 0.05
            self.qualia['urgency'] = min(1.0, self.qualia['urgency'] + 0.2)
        
        # 疲労 → 不快 + 沈静
        if fatigue > 0.5:
            self.valence -= 0.05 * fatigue
            self.arousal -= 0.05 * fatigue
        
        # ダメージ → fear + 不快
        if damage > 0:
            self.qualia['fear'] = min(1.0, self.qualia['fear'] + damage * 0.5)
            self.valence -= damage * 0.3
        
        # 範囲制限
        self.valence = max(-1, min(1, self.valence))
        self.arousal = max(-1, min(1, self.arousal))
    
    def update_from_prediction_error(self, errors: List[Dict]):
        """L3予測誤差からクオリア更新"""
        for error in errors:
            error_type = error.get('type', '')
            magnitude = error.get('magnitude', 0.5)
            
            if error_type == 'new_object':
                self.qualia['surprise'] = min(1.0, self.qualia['surprise'] + magnitude * 0.5)
                self.qualia['curiosity'] = min(1.0, self.qualia['curiosity'] + magnitude * 0.3)
                self.arousal += magnitude * 0.2
            
            if error_type == 'danger':
                self.qualia['fear'] = min(1.0, self.qualia['fear'] + magnitude * 0.3)
                self.valence -= magnitude * 0.2
                self.arousal += magnitude * 0.3
            
            if error_type == 'goal_found':
                self.qualia['desire'] = min(1.0, self.qualia['desire'] + magnitude * 0.5)
                self.valence += magnitude * 0.3
        
        self.valence = max(-1, min(1, self.valence))
        self.arousal = max(-1, min(1, self.arousal))
    
    def update_in_danger_zone(self, in_danger: bool):
        """危険ゾーン内での更新"""
        if in_danger:
            self.qualia['fear'] = min(1.0, self.qualia['fear'] + 0.15)
            self.arousal = min(1.0, self.arousal + 0.1)
        else:
            self.qualia['fear'] = max(0, self.qualia['fear'] - 0.05)
    
    def decay_qualia(self):
        """クオリアの自然減衰"""
        for key in self.qualia:
            self.qualia[key] *= self.decay.get(key, 0.95)
        
        # 基本軸も中央に戻る
        self.valence *= 0.98
        self.arousal *= 0.95
    
    def get_color_desire(self, color: str) -> float:
        """色への欲求度"""
        return self.color_preference.get(color, 0.5)
    
    def get_state(self) -> Dict:
        return {
            'valence': self.valence,
            'arousal': self.arousal,
            'qualia': self.qualia.copy(),
            'color_preference': self.color_preference.copy()
        }


# ==========================================
# L3: 予測・構造化層
# ==========================================

class L3Prediction:
    """予測と誤差検出"""
    
    def __init__(self):
        self.predictions = {}  # 予測した内容
        self.errors = []       # 今ステップの予測誤差
    
    def predict(self, l4_memory) -> Dict:
        """L4記憶に基づいて予測"""
        # 既知のマップから次に見えるものを予測
        self.predictions = l4_memory.internal_map.copy()
        return self.predictions
    
    def compare_with_reality(self, sense_data: Dict, l4_memory) -> List[Dict]:
        """感覚データと予測を比較、誤差を検出"""
        self.errors = []
        
        for pos, data in sense_data.items():
            predicted = self.predictions.get(pos, 'unknown')
            actual_cell = data['cell']
            actual_obj = data['object']
            
            # 新しいオブジェクト発見
            if actual_obj and pos not in l4_memory.found_objects:
                error = {
                    'type': 'new_object',
                    'pos': pos,
                    'object': actual_obj,
                    'magnitude': 0.8
                }
                
                # 危険ゾーン内のオブジェクト
                if actual_cell == 'danger':
                    error['type'] = 'danger'
                    error['magnitude'] = 1.0
                
                # ゴール発見
                if actual_obj.get('name') == 'goal':
                    error['type'] = 'goal_found'
                
                self.errors.append(error)
            
            # 未知のセルを発見
            if predicted == 'unknown' and actual_cell != 'unknown':
                if actual_cell == 'danger':
                    self.errors.append({
                        'type': 'danger',
                        'pos': pos,
                        'magnitude': 0.6
                    })
        
        return self.errors
    
    def get_state(self) -> Dict:
        return {
            'predictions_count': len(self.predictions),
            'errors': self.errors.copy()
        }


# ==========================================
# L4: 記憶層
# ==========================================

class L4Memory:
    """記憶（内部マップ、発見物、ラベル辞書、長期記憶）"""
    
    LTM_FILE = "hida_ltm.json"
    
    def __init__(self):
        self.internal_map = {}      # (x,y) -> cell_type
        self.found_objects = {}     # (x,y) -> object_info
        self.visited = set()        # 訪れた場所
        
        # 短期記憶（今回のセッション）
        self.stm = []
        
        # 長期記憶（永続化）
        self.ltm = self._load_ltm()
        
        # 感情ラベル辞書（L2の数値 → 言葉）
        self.emotion_labels = {
            'ワクワク': {'valence': (0.3, 1.0), 'arousal': (0.5, 1.0)},
            'リラックス': {'valence': (0.2, 1.0), 'arousal': (-1.0, -0.3)},
            'イライラ': {'valence': (-1.0, -0.3), 'arousal': (0.3, 1.0)},
            'へとへと': {'valence': (-0.5, 0.0), 'arousal': (-1.0, -0.5)},
            '怖い': {'fear': (0.5, 1.0)},
            '欲しい': {'desire': (0.6, 1.0)},
            '驚いた': {'surprise': (0.5, 1.0)},
            '急がなきゃ': {'urgency': (0.6, 1.0)},
        }
        
        # 経験から学んだ傾向（長期記憶から構築）
        self.learned_tendencies = self._build_tendencies()
        
        # 変調値（数値のみ、テキストなし）
        self.modulation = self._load_modulation()
        self._update_modulation()
    
    def _load_modulation(self) -> Dict:
        """変調値をファイルから読み込む"""
        try:
            with open("hida_modulation.json", 'r', encoding='utf-8') as f:
                mod = json.load(f)
                print(f"  [Mod] 変調値を読み込み: fear={mod.get('fear_weight', 1.0):.2f}, safe={mod.get('safe_preference', 0.0):.2f}")
                return mod
        except FileNotFoundError:
            return {
                'fear_weight': 1.0,      # 恐怖感度（1.0=標準）
                'safe_preference': 0.0,  # 安全志向（0.0=なし）
                'energy_caution': 0.0,   # エネルギー慎重さ
                'experience_count': 0    # 経験回数
            }
        except:
            return {'fear_weight': 1.0, 'safe_preference': 0.0, 'energy_caution': 0.0, 'experience_count': 0}
    
    def _save_modulation(self):
        """変調値をファイルに保存"""
        try:
            with open("hida_modulation.json", 'w', encoding='utf-8') as f:
                json.dump(self.modulation, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"  [Mod] 保存エラー: {e}")
    
    def _update_modulation(self):
        """経験から変調値を更新（数値のみ）"""
        t = self.learned_tendencies
        old_mod = self.modulation.copy()
        
        # 経験回数
        self.modulation['experience_count'] = t['total_sessions']
        
        # 安全志向: 経験がある場合は計算、ない場合は0
        total_success = t['success_with_safe'] + t['success_with_red']
        if total_success > 0:
            safe_ratio = t['success_with_safe'] / total_success
            self.modulation['safe_preference'] = safe_ratio * 0.3  # 最大0.3
        else:
            self.modulation['safe_preference'] = 0.0  # 経験なしなら0
        
        # 危険経験 → fear感度が上がる
        if t['danger_encounters'] > 0:
            self.modulation['fear_weight'] = 1.0 + (t['danger_encounters'] * 0.1)  # 経験ごとに+0.1
        
        # 忘却: fear_weightが徐々に下がる（最低1.0まで）
        if self.modulation['fear_weight'] > 1.0:
            self.modulation['fear_weight'] *= 0.95  # 毎セッション5%減衰
            if self.modulation['fear_weight'] < 1.0:
                self.modulation['fear_weight'] = 1.0
        
        # 忘却: safe_preferenceも徐々に下がる（最低0.0まで）
        if self.modulation['safe_preference'] > 0.0:
            self.modulation['safe_preference'] *= 0.98  # 毎セッション2%減衰
            if self.modulation['safe_preference'] < 0.01:
                self.modulation['safe_preference'] = 0.0
        
        # エネルギー切れ経験 → エネルギー慎重さが上がる
        if t['avg_final_energy'] < 0.3:
            self.modulation['energy_caution'] = (0.3 - t['avg_final_energy']) * 2  # 最大0.6
        
        # 変化があれば保存
        if self.modulation != old_mod:
            self._save_modulation()
            print(f"  [Mod] 変調値更新: fear={self.modulation['fear_weight']:.2f}, safe={self.modulation['safe_preference']:.2f}")
    
    def get_modulation(self) -> Dict:
        """変調値を返す"""
        return self.modulation.copy()
    
    def _load_ltm(self) -> List[Dict]:
        """長期記憶をファイルから読み込む"""
        try:
            with open(self.LTM_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                print(f"  [LTM] {len(data)}件の記憶を読み込み")
                return data
        except FileNotFoundError:
            print(f"  [LTM] 新規（記憶なし）")
            return []
        except Exception as e:
            print(f"  [LTM] 読み込みエラー: {e}")
            return []
    
    def _save_ltm(self):
        """長期記憶をファイルに保存"""
        try:
            with open(self.LTM_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.ltm, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"  [LTM] 保存エラー: {e}")
    
    def _build_tendencies(self) -> Dict:
        """長期記憶から傾向を構築"""
        tendencies = {
            'danger_pain': 0,          # 痛い経験の回数
            'danger_fatigue': 0,       # 疲労経験の回数
            'danger_encounters': 0,    # 危険に遭遇した回数（互換用）
            'danger_fear_total': 0.0,  # 危険時のfear合計
            'success_with_red': 0,     # 赤で成功した回数
            'success_with_safe': 0,    # 安全色で成功した回数
            'total_sessions': 0,       # 総セッション数
            'avg_final_energy': 0.5,   # 平均最終エネルギー
        }
        
        if not self.ltm:
            return tendencies
        
        for memory in self.ltm:
            event = memory.get('event', '')
            qualia = memory.get('qualia', {})
            
            # 痛み経験
            if 'danger_pain' in event:
                tendencies['danger_pain'] += 1
                tendencies['danger_encounters'] += 1
                tendencies['danger_fear_total'] += qualia.get('fear', 0)
            
            # 疲労経験
            if 'danger_fatigue' in event:
                tendencies['danger_fatigue'] += 1
            
            # goal_reached_with_XXX を解析
            if 'goal_reached_with_red' in event:
                tendencies['success_with_red'] += 1
            elif 'goal_reached_with_green' in event or 'goal_reached_with_blue' in event:
                tendencies['success_with_safe'] += 1
            
            if memory.get('is_session_end'):
                tendencies['total_sessions'] += 1
                energy = memory.get('energy', 0.5)
                # 移動平均
                tendencies['avg_final_energy'] = (
                    tendencies['avg_final_energy'] * 0.7 + 
                    energy * 0.3
                )
        
        return tendencies
    
    def remember_consciously(self, event: str, l1_state: Dict, l2_state: Dict, 
                             is_session_end: bool = False):
        """意識的に記憶する（L5がONの時だけ呼ばれる）"""
        memory = {
            'timestamp': self._get_timestamp(),
            'event': event,
            'position': l1_state.get('position'),
            'energy': l1_state.get('energy'),
            'qualia': {
                'fear': l2_state.get('qualia', {}).get('fear', 0),
                'desire': l2_state.get('qualia', {}).get('desire', 0),
                'urgency': l2_state.get('qualia', {}).get('urgency', 0),
                'valence': l2_state.get('valence', 0),
                'arousal': l2_state.get('arousal', 0),
            },
            'emotion_label': self.get_emotion_label(l2_state),
            'is_session_end': is_session_end
        }
        
        # 短期記憶に追加
        self.stm.append(memory)
        
        # 重要なイベントは長期記憶にも
        if self._is_significant(event, memory):
            self.ltm.append(memory)
            self._save_ltm()
            print(f"  [LTM] 記憶保存: {event}")
    
    def _is_significant(self, event: str, memory: Dict) -> bool:
        """重要なイベントかどうか"""
        # 重要イベント
        significant_events = ['grabbed', 'goal_reached', 'danger', 'exhausted', 'timeout']
        if any(e in event for e in significant_events):
            return True
        
        # 強い感情
        qualia = memory.get('qualia', {})
        if qualia.get('fear', 0) > 0.5:
            return True
        if qualia.get('urgency', 0) > 0.7:
            return True
        
        # セッション終了
        if memory.get('is_session_end'):
            return True
        
        return False
    
    def _get_timestamp(self) -> str:
        import datetime
        return datetime.datetime.now().isoformat()
    
    def get_fear_modifier(self) -> float:
        """過去の経験からfear修正値を返す"""
        if self.learned_tendencies['danger_encounters'] == 0:
            return 0.0
        
        # 危険経験が多いほどfearが上がりやすい
        avg_fear = (self.learned_tendencies['danger_fear_total'] / 
                   self.learned_tendencies['danger_encounters'])
        return avg_fear * 0.2  # 20%の影響
    
    def get_personality_description(self) -> str:
        """性格の説明を返す"""
        t = self.learned_tendencies
        
        if t['total_sessions'] == 0:
            return "まだ経験が少ない新人"
        
        descriptions = []
        
        # 危険への態度
        if t['danger_encounters'] > 3 and t['danger_fear_total'] > 2:
            descriptions.append("慎重派")
        elif t['success_with_red'] > t['success_with_safe']:
            descriptions.append("冒険好き")
        
        # エネルギー管理
        if t['avg_final_energy'] > 0.5:
            descriptions.append("余裕を持って行動")
        elif t['avg_final_energy'] < 0.2:
            descriptions.append("限界まで頑張る")
        
        return "、".join(descriptions) if descriptions else "バランス型"
    
    def update_from_sense(self, sense_data: Dict):
        """感覚データから記憶更新"""
        for pos, data in sense_data.items():
            self.internal_map[pos] = data['cell']
            if data['object']:
                self.found_objects[pos] = data['object']
    
    def update_from_errors(self, errors: List[Dict], qualia_intensity: float):
        """予測誤差から記憶更新（クオリア強度で重み付け）"""
        for error in errors:
            pos = error.get('pos')
            if pos and error.get('object'):
                # クオリア強度が高いほど記憶に残りやすい
                self.found_objects[pos] = {
                    **error['object'],
                    'memory_strength': qualia_intensity
                }
    
    def mark_visited(self, pos: Tuple[int, int]):
        """訪問記録"""
        self.visited.add(pos)
    
    def remove_object(self, pos: Tuple[int, int]):
        """オブジェクト削除（取得時）"""
        if pos in self.found_objects:
            del self.found_objects[pos]
    
    def get_emotion_label(self, l2_state: Dict) -> str:
        """L2状態から最も近い感情ラベルを返す"""
        best_label = None
        best_score = -1
        
        for label, conditions in self.emotion_labels.items():
            score = 0
            match = True
            
            for key, (low, high) in conditions.items():
                if key in ['valence', 'arousal']:
                    value = l2_state.get(key, 0)
                else:
                    value = l2_state.get('qualia', {}).get(key, 0)
                
                if low <= value <= high:
                    score += 1
                else:
                    match = False
                    break
            
            if match and score > best_score:
                best_score = score
                best_label = label
        
        return best_label or '普通'
    
    def get_state(self) -> Dict:
        return {
            'map_size': len(self.internal_map),
            'objects_found': len(self.found_objects),
            'visited_count': len(self.visited),
            'found_objects': dict(self.found_objects)
        }


# ==========================================
# L5: 意識層（自認・言語化・コミュニケーション）
# ==========================================

class L5Consciousness:
    """意識（自認、言語化、コミュニケーション）"""
    
    def __init__(self, threshold=1.0):
        self.threshold = threshold
        self.is_conscious = False
        self.sync_level = 0.0
        self.state_package = {}
    
    def check_sync(self, l1: L1Body, l2: L2Qualia, l3: L3Prediction, l4: L4Memory) -> bool:
        """全層の同期をチェック"""
        # 各層の活動度
        l1_activity = (1 - l1.energy) + l1.fatigue  # 身体的負荷
        l2_activity = abs(l2.valence) + abs(l2.arousal) + sum(l2.qualia.values())
        l3_activity = len(l3.errors) * 0.5
        l4_activity = len(l4.found_objects) * 0.1
        
        self.sync_level = l1_activity + l2_activity + l3_activity + l4_activity
        self.is_conscious = self.sync_level > self.threshold
        
        return self.is_conscious
    
    def self_recognize(self, l1: L1Body, l2: L2Qualia, l3: L3Prediction, l4: L4Memory) -> Dict:
        """L1〜L4の状態を自認してパッケージ化"""
        l2_state = l2.get_state()
        emotion_label = l4.get_emotion_label(l2_state)
        
        self.state_package = {
            # L1: 身体
            'body': {
                'energy': l1.energy,
                'fatigue': l1.fatigue,
                'position': l1.position,
                'holding': l1.holding
            },
            # L2: クオリア
            'qualia': {
                'valence': l2.valence,
                'arousal': l2.arousal,
                'fear': l2.qualia['fear'],
                'desire': l2.qualia['desire'],
                'urgency': l2.qualia['urgency'],
                'anger': l2.qualia['anger'],
                'sadness': l2.qualia['sadness'],
                'joy': l2.qualia['joy'],
                'disgust': l2.qualia['disgust'],
            },
            # L3: 予測誤差
            'prediction': {
                'errors_count': len(l3.errors),
                'recent_errors': l3.errors[-3:] if l3.errors else []
            },
            # L4: 記憶
            'memory': {
                'objects_found': list(l4.found_objects.keys()),
                'visited_count': len(l4.visited)
            },
            # L5: 意識状態
            'consciousness': {
                'is_conscious': self.is_conscious,
                'sync_level': self.sync_level
            }
        }
        
        return self.state_package
    
    def format_for_llm(self, action: str, decision_details: Dict = None, modulation: Dict = None) -> str:
        """LLM用のプロンプト生成"""
        pkg = self.state_package
        
        # 変調値から経験レベルを表現
        exp_count = modulation.get('experience_count', 0) if modulation else 0
        fear_weight = modulation.get('fear_weight', 1.0) if modulation else 1.0
        safe_pref = modulation.get('safe_preference', 0.0) if modulation else 0.0
        
        prompt = f"""あなたはHIDAという探索ロボットです。
今の状態を1人称で短く語ってください（2-3文で）。

【経験】
- これまでの探索回数: {exp_count}回
- 恐怖への感度: {fear_weight:.2f}（1.0が標準、高いほど怖がり）
- 安全志向度: {safe_pref:.2f}（0.0が標準、高いほど安全重視）

【身体状態】
- エネルギー: {pkg['body']['energy']:.0%}
- 疲労度: {pkg['body']['fatigue']:.0%}
- 持っているもの: {pkg['body']['holding'] or 'なし'}

【感情状態】
- 快-不快: {pkg['qualia']['valence']:.2f}
- 覚醒度: {pkg['qualia']['arousal']:.2f}
- 恐怖: {pkg['qualia']['fear']:.0%}
- 欲求: {pkg['qualia']['desire']:.0%}
- 緊急度: {pkg['qualia']['urgency']:.0%}
- 怒り: {pkg['qualia']['anger']:.0%}
- 悲しみ: {pkg['qualia']['sadness']:.0%}
- 喜び: {pkg['qualia']['joy']:.0%}
- 嫌悪: {pkg['qualia']['disgust']:.0%}

【認識】
- 発見したもの: {len(pkg['memory']['objects_found'])}個
- 探索した場所: {pkg['memory']['visited_count']}箇所

【今の行動】
{action}
"""
        
        if decision_details:
            prompt += f"""
【行動の内部計算】
{json.dumps(decision_details, ensure_ascii=False, indent=2)}
"""
        
        prompt += """
数値をそのまま言うのではなく、感覚として表現してください："""
        
        return prompt
    
    def get_state(self) -> Dict:
        return {
            'is_conscious': self.is_conscious,
            'sync_level': self.sync_level,
            'state_package': self.state_package
        }


# ==========================================
# LLM連携
# ==========================================

class LLMVerbalizer:
    """LLM言語化（ollama / Claude）"""
    
    def __init__(self, prefer_claude=True):
        self.prefer_claude = prefer_claude
    
    def verbalize(self, prompt: str) -> Tuple[str, str]:
        """プロンプトを言語化"""
        if self.prefer_claude:
            result = self._ask_claude(prompt)
            if result:
                return result, "claude"
        
        result = self._ask_ollama(prompt)
        if result:
            return result, "ollama"
        
        return "(LLM未接続)", "none"
    
    def _ask_ollama(self, prompt: str, model="gemma3:4b") -> Optional[str]:
        try:
            result = subprocess.run(
                ["ollama", "run", model, prompt],
                capture_output=True,
                text=True,
                timeout=60,
                encoding='utf-8',
                errors='replace'
            )
            if result.returncode == 0:
                return result.stdout.strip()
        except:
            pass
        return None
    
    def _ask_claude(self, prompt: str) -> Optional[str]:
        api_key = os.environ.get('ANTHROPIC_API_KEY', '')
        if not api_key:
            return None
        
        data = json.dumps({
            "model": "claude-sonnet-4-20250514",
            "max_tokens": 300,
            "messages": [{"role": "user", "content": prompt}]
        }).encode('utf-8')
        
        req = urllib.request.Request(
            "https://api.anthropic.com/v1/messages",
            data=data,
            headers={
                "Content-Type": "application/json",
                "x-api-key": api_key,
                "anthropic-version": "2023-06-01"
            }
        )
        
        try:
            with urllib.request.urlopen(req, timeout=30) as response:
                result = json.loads(response.read().decode('utf-8'))
                return result['content'][0]['text']
        except:
            return None


# ==========================================
# NPC（他のエージェント）
# ==========================================

class NPC:
    """他のエージェント（邪魔する存在）"""
    
    def __init__(self, name: str, position: List[int]):
        self.name = name
        self.position = position.copy()
        self.holding = None
    
    def step(self, world):
        """ランダムに動く"""
        directions = [(0, -1), (0, 1), (-1, 0), (1, 0)]
        random.shuffle(directions)
        
        for dx, dy in directions:
            nx, ny = self.position[0] + dx, self.position[1] + dy
            cell = world.get_cell(nx, ny)
            if cell not in ['wall', 'danger']:
                self.position = [nx, ny]
                break
    
    def get_position(self) -> tuple:
        return tuple(self.position)


# ==========================================
# World（環境）
# ==========================================

class World:
    """グリッドワールド環境"""
    
    def __init__(self, size=10):
        self.size = size
        self.grid = [['empty' for _ in range(size)] for _ in range(size)]
        self.objects = {}
        self.npcs = []  # 他のエージェント
    
    def add_npc(self, npc: NPC):
        self.npcs.append(npc)
    
    def get_npc_at(self, x, y) -> Optional[NPC]:
        """指定位置のNPCを取得"""
        for npc in self.npcs:
            if npc.position[0] == x and npc.position[1] == y:
                return npc
        return None
    
    def step_npcs(self):
        """全NPCを動かす"""
        for npc in self.npcs:
            npc.step(self)
    
    def add_wall(self, x, y):
        if 0 <= x < self.size and 0 <= y < self.size:
            self.grid[y][x] = 'wall'
    
    def add_danger(self, x, y):
        if 0 <= x < self.size and 0 <= y < self.size:
            self.grid[y][x] = 'danger'
    
    def add_object(self, name, x, y, color=None, rotten=False):
        self.objects[(x, y)] = {'name': name, 'color': color, 'rotten': rotten}
    
    def get_cell(self, x, y) -> str:
        if 0 <= x < self.size and 0 <= y < self.size:
            return self.grid[y][x]
        return 'wall'
    
    def get_object(self, x, y) -> Optional[Dict]:
        return self.objects.get((x, y))
    
    def remove_object(self, x, y):
        if (x, y) in self.objects:
            del self.objects[(x, y)]
    
    def display(self, hida_pos=None, hida_dir=None):
        dir_chars = {'N': '^', 'S': 'v', 'E': '>', 'W': '<'}
        print("\n=== World ===")
        for y in range(self.size):
            row = ""
            for x in range(self.size):
                if hida_pos and hida_pos[0] == x and hida_pos[1] == y:
                    row += f"[{dir_chars.get(hida_dir, '?')}]"
                elif self.get_npc_at(x, y):
                    row += "[N]"  # NPC
                elif (x, y) in self.objects:
                    obj = self.objects[(x, y)]
                    if obj['color']:
                        row += f"[{obj['color'][0]}]"
                    else:
                        row += "[G]"
                elif self.grid[y][x] == 'wall':
                    row += "[#]"
                elif self.grid[y][x] == 'danger':
                    row += "[!]"
                else:
                    row += "[ ]"
            print(row)


# ==========================================
# HIDA統合クラス
# ==========================================

class HIDA:
    """5層統合エージェント"""
    
    def __init__(self, color_preference=None):
        self.l1 = L1Body()
        self.l2 = L2Qualia(color_preference)
        self.l3 = L3Prediction()
        self.l4 = L4Memory()
        self.l5 = L5Consciousness(threshold=0.8)
        self.llm = LLMVerbalizer(prefer_claude=True)
        
        self.step_count = 0
        self.action_history = []
    
    def sense(self, world: World):
        """感覚入力（L1 → L3 → L4）"""
        # L1: 見る
        sense_data = self.l1.look(world)
        
        # L3: 予測と比較
        self.l3.predict(self.l4)
        errors = self.l3.compare_with_reality(sense_data, self.l4)
        
        # L4: 記憶更新
        self.l4.update_from_sense(sense_data)
        qualia_intensity = sum(self.l2.qualia.values())
        self.l4.update_from_errors(errors, qualia_intensity)
        
        # L2: クオリアに予測誤差を反映
        self.l2.update_from_prediction_error(errors)
        
        # 危険ゾーンチェック
        current_cell = world.get_cell(self.l1.position[0], self.l1.position[1])
        self.l2.update_in_danger_zone(current_cell == 'danger')
        
        return errors
    
    def think(self, world: World) -> Tuple[str, Dict]:
        """思考・行動決定（L2/L3/L4で決定、L5は関与しない）"""
        # 発見したボール
        balls = {}
        for pos, obj in self.l4.found_objects.items():
            if obj.get('name') == 'ball':
                color = obj.get('color', 'unknown')
                dist = abs(pos[0] - self.l1.position[0]) + abs(pos[1] - self.l1.position[1])
                is_danger = self.l4.internal_map.get(pos) == 'danger'
                is_rotten = obj.get('rotten', False)
                balls[color] = {'pos': pos, 'dist': dist, 'is_danger': is_danger, 'is_rotten': is_rotten}
        
        # ゴール
        goal_pos = None
        for pos, obj in self.l4.found_objects.items():
            if obj.get('name') == 'goal':
                goal_pos = pos
        
        # 行動決定
        if self.l1.holding and goal_pos:
            return 'go_to_goal', {'target': goal_pos}
        
        if balls and not self.l1.holding:
            # スコア計算
            scores = {}
            details = {}
            q = self.l2.qualia
            mod = self.l2.modulation
            
            for color, info in balls.items():
                pref = self.l2.get_color_desire(color) * 10
                dist_penalty = -info['dist'] * (0.5 + q['urgency'])
                # 危険ゾーン: fear_weightで基本ペナルティも変わる
                fear_weight = mod.get('fear_weight', 1.0)
                base_danger = -3 * fear_weight  # 基本ペナルティもfear_weightで変化
                fear_penalty = -5 * q['fear'] * fear_weight
                danger_penalty = (base_danger + fear_penalty) if info['is_danger'] else 0
                # 安全志向: 安全なものにボーナス（係数を下げて赤が勝てるように）
                safe_bonus = mod.get('safe_preference', 0.0) * 2 if not info['is_danger'] else 0
                # エネルギー慎重さ
                energy_caution = mod.get('energy_caution', 0.0)
                energy_penalty = -5 * (1 - self.l1.energy) * (1 + energy_caution) if info['dist'] > 3 and self.l1.energy < 0.5 else 0
                # 🤢 腐ったものペナルティ（disgust経験で増加）
                disgust_penalty = -8 * (1 + q['disgust']) if info['is_rotten'] else 0
                
                total = pref + dist_penalty + danger_penalty + safe_bonus + energy_penalty + disgust_penalty
                scores[color] = total
                details[color] = {
                    'preference': pref,
                    'distance_penalty': dist_penalty,
                    'danger_penalty': danger_penalty,
                    'safe_bonus': safe_bonus,
                    'energy_penalty': energy_penalty,
                    'disgust_penalty': disgust_penalty,
                    'total': total
                }
            
            chosen = max(scores, key=scores.get)
            return f'go_to_{chosen}', {'target': balls[chosen]['pos'], 'scores': details, 'chosen': chosen}
        
        return 'explore', {}
    
    def act(self, world: World, action: str, details: Dict) -> bool:
        """行動実行（L1）"""
        target = details.get('target')
        
        if target:
            # ターゲットに向かう
            tx, ty = target
            hx, hy = self.l1.position
            
            if hx == tx and hy == ty:
                # 到着
                obj = world.get_object(tx, ty)
                if obj and obj.get('name') == 'ball' and not self.l1.holding:
                    self._last_grabbed_color = obj.get('color', 'unknown')  # 色を保存
                    
                    # 🤢 腐ったボールならdisgust上昇
                    if obj.get('rotten'):
                        self.l2.qualia['disgust'] = min(1.0, self.l2.qualia['disgust'] + 0.6)
                        self.l2.valence -= 0.4
                        print(f"    🤢 腐ってる！ disgust={self.l2.qualia['disgust']:.2f}")
                    
                    self.l1.grab(obj)
                    world.remove_object(tx, ty)
                    self.l4.remove_object((tx, ty))
                    return True
                elif obj and obj.get('name') == 'goal' and self.l1.holding:
                    self.l1.release()
                    return True
            else:
                # 移動
                dx = 1 if tx > hx else (-1 if tx < hx else 0)
                dy = 1 if ty > hy else (-1 if ty < hy else 0)
                
                # 方向調整
                if dx > 0:
                    target_dir = 'E'
                elif dx < 0:
                    target_dir = 'W'
                elif dy > 0:
                    target_dir = 'S'
                else:
                    target_dir = 'N'
                
                if self.l1.direction != target_dir:
                    # 回転
                    dirs = ['N', 'E', 'S', 'W']
                    ci = dirs.index(self.l1.direction)
                    ti = dirs.index(target_dir)
                    diff = (ti - ci) % 4
                    if diff == 1:
                        self.l1.turn_right()
                    else:
                        self.l1.turn_left()
                else:
                    # NPCブロックチェック
                    dx, dy = {'N': (0, -1), 'S': (0, 1), 'E': (1, 0), 'W': (-1, 0)}[self.l1.direction]
                    next_pos = (self.l1.position[0] + dx, self.l1.position[1] + dy)
                    npc = world.get_npc_at(next_pos[0], next_pos[1])
                    if npc:
                        # 😠 邪魔された！
                        self.l2.qualia['anger'] = min(1.0, self.l2.qualia['anger'] + 0.3)
                        self.l2.arousal += 0.2
                        print(f"    😠 {npc.name}に邪魔された！ anger={self.l2.qualia['anger']:.2f}")
                    else:
                        self.l1.move_forward(world)
                        # 危険ゾーンダメージチェック（33%）
                        self._check_danger_damage(world)
        else:
            # 探索（ランダム）
            action = random.choice(['forward', 'left', 'right'])
            if action == 'forward':
                self.l1.move_forward(world)
                self._check_danger_damage(world)
            elif action == 'left':
                self.l1.turn_left()
            else:
                self.l1.turn_right()
        
        return False
    
    def _check_danger_damage(self, world: World):
        """危険ゾーンで2種類のダメージ判定"""
        x, y = self.l1.position
        if world.get_cell(x, y) == 'danger':
            
            # 痛み（33%）→ 恐怖・怒り上昇
            if random.random() < 0.33:
                self.l2.qualia['fear'] = min(1.0, self.l2.qualia['fear'] + 0.4)
                self.l2.qualia['anger'] = min(1.0, self.l2.qualia['anger'] + 0.2)  # 痛いと怒る
                self.l2.valence -= 0.3
                self.l2.arousal += 0.3
                
                self.l4.remember_consciously(
                    "danger_pain",
                    self.l1.get_state(),
                    self.l2.get_state()
                )
                print(f"    ⚡ 痛い！ fear={self.l2.qualia['fear']:.2f} anger={self.l2.qualia['anger']:.2f}")
            
            # 疲労（33%）→ エネルギー減少・悲しみ上昇
            if random.random() < 0.33:
                damage = 0.15
                self.l1.energy = max(0, self.l1.energy - damage)
                self.l2.qualia['sadness'] = min(1.0, self.l2.qualia['sadness'] + 0.15)  # 疲れると悲しくなる
                
                self.l4.remember_consciously(
                    "danger_fatigue",
                    self.l1.get_state(),
                    self.l2.get_state()
                )
                print(f"    💦 疲れた！ E={self.l1.energy:.2f} sadness={self.l2.qualia['sadness']:.2f}")
    
    def reflect(self, action: str, details: Dict) -> Optional[str]:
        """内省・言語化（L5 → LLM）"""
        # L5: 同期チェック
        is_conscious = self.l5.check_sync(self.l1, self.l2, self.l3, self.l4)
        
        if not is_conscious:
            return None
        
        # L5: 自認
        self.l5.self_recognize(self.l1, self.l2, self.l3, self.l4)
        
        # L4: 意識的に記憶する
        self.l4.remember_consciously(
            action, 
            self.l1.get_state(), 
            self.l2.get_state()
        )
        
        # L5: プロンプト生成（変調値を数値として渡す）
        modulation = self.l4.get_modulation()
        prompt = self.l5.format_for_llm(action, details.get('scores'), modulation)
        
        # LLM: 言語化
        response, llm_type = self.llm.verbalize(prompt)
        
        return f"({llm_type}) {response}"
    
    def step(self, world: World, verbose=True) -> Dict:
        """1ステップ実行"""
        self.step_count += 1
        
        # 変調値をL2に適用
        self.l2.apply_modulation(self.l4.get_modulation())
        
        # L2: 身体状態からクオリア更新
        self.l2.update_from_body(self.l1.get_state())
        
        # 感覚入力
        errors = self.sense(world)
        
        # 思考
        action, details = self.think(world)
        
        # 行動
        goal_reached = self.act(world, action, details)
        
        # 訪問記録
        self.l4.mark_visited(tuple(self.l1.position))
        
        # クオリア減衰
        self.l2.decay_qualia()
        
        # 内省（意識的なら）
        reflection = None
        if verbose and self.step_count % 5 == 0:
            reflection = self.reflect(action, details)
        
        # ゴール到達時に記憶（releaseする前に色を取得）
        if goal_reached:
            grabbed_color = 'unknown'
            # holdingがある場合（actでreleaseする前に保存された）
            if hasattr(self, '_last_grabbed_color'):
                grabbed_color = self._last_grabbed_color
            
            # 🎉 joy上昇（目標達成）
            self.l2.qualia['joy'] = min(1.0, self.l2.qualia['joy'] + 0.5)
            # 好きな色だったらさらにjoy
            color_pref = self.l2.color_preference.get(grabbed_color, 0.5)
            if color_pref > 0.7:
                self.l2.qualia['joy'] = min(1.0, self.l2.qualia['joy'] + 0.3)
            self.l2.valence += 0.3  # 快方向へ
            
            self.l4.remember_consciously(
                f"goal_reached_with_{grabbed_color}",
                self.l1.get_state(),
                self.l2.get_state(),
                is_session_end=True
            )
        
        result = {
            'step': self.step_count,
            'action': action,
            'position': self.l1.position.copy(),
            'energy': self.l1.energy,
            'holding': self.l1.holding,
            'conscious': self.l5.is_conscious,
            'goal_reached': goal_reached,
            'reflection': reflection
        }
        
        if verbose:
            q = self.l2.qualia
            print(f"\n  Step {self.step_count}: {action}")
            print(f"    E={self.l1.energy:.2f} F={q['fear']:.2f} D={q['desire']:.2f} U={q['urgency']:.2f}")
            if details.get('scores'):
                print(f"    Scores: {[(c, f'{d['total']:.1f}') for c, d in details['scores'].items()]}")
            if reflection:
                print(f"    💭 {reflection}")
        
        # NPCも動かす
        world.step_npcs()
        
        return result


# ==========================================
# テスト
# ==========================================

def create_test_world():
    """テスト用ワールド"""
    world = World(size=10)
    
    # 外壁
    for i in range(10):
        world.add_wall(i, 0)
        world.add_wall(i, 9)
        world.add_wall(0, i)
        world.add_wall(9, i)
    
    # 危険ゾーン
    for x in range(5, 8):
        for y in range(2, 5):
            world.add_danger(x, y)
    
    # ボール
    world.add_object("ball", 6, 3, color="red")    # 危険ゾーン
    world.add_object("ball", 2, 4, color="blue")   # 安全
    world.add_object("ball", 2, 7, color="green")  # 安全
    world.add_object("ball", 4, 6, color="yellow", rotten=True)  # 腐ってる（近い）
    
    # ゴール
    world.add_object("goal", 7, 7)
    
    # NPC（邪魔する存在）
    npc = NPC("ボブ", [4, 5])
    world.add_npc(npc)
    
    return world


def run_test(color_pref, initial_energy=1.0, max_steps=50):
    """テスト実行"""
    world = create_test_world()
    hida = HIDA(color_preference=color_pref)
    hida.l1.position = [3, 6]
    hida.l1.direction = 'N'
    hida.l1.energy = initial_energy
    
    # 変調値表示
    mod = hida.l4.get_modulation()
    personality = hida.l4.get_personality_description()
    print(f"  性格: {personality}")
    print(f"  変調: fear_weight={mod['fear_weight']:.2f}, safe_pref={mod['safe_preference']:.2f}, exp={mod['experience_count']}")
    
    # ボールを最初から発見済みにする
    hida.l4.found_objects[(6, 3)] = {'name': 'ball', 'color': 'red'}
    hida.l4.found_objects[(2, 4)] = {'name': 'ball', 'color': 'blue'}
    hida.l4.found_objects[(2, 7)] = {'name': 'ball', 'color': 'green'}
    hida.l4.found_objects[(4, 6)] = {'name': 'ball', 'color': 'yellow', 'rotten': True}
    hida.l4.found_objects[(7, 7)] = {'name': 'goal', 'color': None}
    
    # マップも与える
    for x in range(1, 9):
        for y in range(1, 9):
            if world.get_cell(x, y) == 'danger':
                hida.l4.internal_map[(x, y)] = 'danger'
            else:
                hida.l4.internal_map[(x, y)] = 'empty'
    
    print(f"\n{'='*60}")
    print(f"色好み: {color_pref}")
    print(f"初期エネルギー: {initial_energy}")
    print(f"  赤: 危険ゾーン内")
    print(f"  青: 安全、やや遠い")
    print(f"  緑: 安全、近い")
    world.display(hida.l1.position, hida.l1.direction)
    
    for _ in range(max_steps):
        result = hida.step(world)
        
        if result['goal_reached']:
            print(f"\n🏆 ゴール到達！")
            break
        
        if result['holding'] and 'go_to' in result['action']:
            # ボール取得
            pass
        
        if hida.l1.energy <= 0:
            print(f"\n💀 エネルギー切れ")
            break
    
    # 最終内省
    print(f"\n=== 最終内省 ===")
    final_action = f"結果: {result['holding']}を取得" if result['holding'] else "探索中"
    reflection = hida.reflect(final_action, {})
    if reflection:
        print(f"💭 {reflection}")
    
    return hida


if __name__ == "__main__":
    import sys
    
    # コマンドライン引数でモード選択
    if len(sys.argv) > 1 and sys.argv[1] == "loop":
        # ループモード：低エネルギーで5回実行して信念形成を見る
        print("=== 低エネルギー5回（慎重になる）===")
        for i in range(5):
            print(f"\n{'#'*60}")
            print(f"# セッション {i+1}")
            print(f"{'#'*60}")
            run_test({'red': 1.0, 'blue': 0.3, 'green': 0.3}, initial_energy=0.3, max_steps=30)
    
    elif len(sys.argv) > 1 and sys.argv[1] == "loop_high":
        # 高エネルギーループ：冒険的になる
        print("=== 高エネルギー5回（冒険的になる）===")
        for i in range(5):
            print(f"\n{'#'*60}")
            print(f"# セッション {i+1}")
            print(f"{'#'*60}")
            run_test({'red': 1.0, 'blue': 0.3, 'green': 0.3}, initial_energy=1.0, max_steps=30)
    
    elif len(sys.argv) > 1 and sys.argv[1] == "reset":
        # リセットモード
        import os
        for f in ["hida_ltm.json", "hida_modulation.json"]:
            if os.path.exists(f):
                os.remove(f)
                print(f"削除: {f}")
        print("記憶と変調値をリセットしました")
    
    else:
        # 通常モード
        print("=== HIDA統合版テスト ===")
        print("（loop: 低E5回, loop_high: 高E5回, reset: リセット）")
        
        # テスト1: 赤好き、通常エネルギー
        print("\n【テスト1】赤好き、通常エネルギー")
        run_test({'red': 1.0, 'blue': 0.3, 'green': 0.3}, initial_energy=1.0)
        
        # テスト2: 赤好き、低エネルギー
        print("\n【テスト2】赤好き、低エネルギー")
        run_test({'red': 1.0, 'blue': 0.3, 'green': 0.3}, initial_energy=0.3)
