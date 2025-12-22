"""
l5_sync.py
L5: 意識層 - 同期検知と言語系への橋渡し

L5は「判断」しない
- 各層の活動度をチェック
- 閾値を超えたら「意識ON」
- 状態をまとめてollamaに渡す
"""

class L5Sync:
    def __init__(self, threshold=1.5):
        self.threshold = threshold
        self.is_conscious = False
        self.sync_history = []
    
    def check_sync(self, l2_activity, l3_activity, l4_activity):
        """
        全層の活動度をチェック
        閾値を超えたら意識ON
        """
        total_activity = l2_activity + l3_activity + l4_activity
        self.is_conscious = total_activity > self.threshold
        
        # 履歴を記録
        self.sync_history.append({
            'l2': l2_activity,
            'l3': l3_activity,
            'l4': l4_activity,
            'total': total_activity,
            'conscious': self.is_conscious
        })
        
        return self.is_conscious
    
    def get_state_for_verbalization(self, l2, l3_errors, l4_memory, current_action, found_objects):
        """
        状態をまとめる（判断はしない）
        ollamaに渡すためのパッケージ
        """
        state = {
            # L2: クオリア状態
            'qualia': {
                'fear': l2.qualia.get('fear', 0),
                'desire': l2.qualia.get('desire', 0),
                'surprise': l2.qualia.get('surprise', 0),
                'curiosity': l2.qualia.get('curiosity', 0),
            },
            'color_preference': l2.color_preference if hasattr(l2, 'color_preference') else {},
            
            # L3: 予測誤差
            'prediction_errors': l3_errors,
            
            # L4: 記憶
            'recent_memory': l4_memory,
            
            # 現在の状態
            'current_action': current_action,
            'found_objects': list(found_objects.keys()) if found_objects else [],
            
            # 意識状態
            'is_conscious': self.is_conscious
        }
        return state
    
    def format_state_as_prompt(self, state):
        """
        状態をollamaへのプロンプトに整形
        """
        prompt = f"""あなたはHIDAという探索エージェントです。
今の状態を短く言葉にしてください（1-2文で）。

【クオリア（感情状態）】
- 恐怖: {state['qualia']['fear']:.2f}
- 欲求: {state['qualia']['desire']:.2f}
- 驚き: {state['qualia']['surprise']:.2f}
- 好奇心: {state['qualia']['curiosity']:.2f}

【色の好み】
{state['color_preference']}

【発見したもの】
{state['found_objects']}

【今の行動】
{state['current_action']}

【意識状態】
{'意識的' if state['is_conscious'] else '無意識的'}

この状態を1人称で短く言葉にしてください："""
        
        return prompt


def calculate_l2_activity(qualia):
    """L2の活動度を計算"""
    # クオリアの強度の合計
    return sum(abs(v) for v in qualia.values())


def calculate_l3_activity(prediction_errors):
    """L3の活動度を計算"""
    # 予測誤差の数
    return len(prediction_errors) * 0.5


def calculate_l4_activity(found_objects, internal_map):
    """L4の活動度を計算"""
    # 記憶の使用度（発見物の数 + 地図の更新）
    return len(found_objects) * 0.2 + min(len(internal_map) * 0.01, 0.5)
