"""
ai_brain.py
AI脳 - 飛騨アーキテクチャ準拠版

【重要な変更】
- 飛騨側（ルールベース）で行動を決定
- LLMは「なぜその行動か」を説明するだけ
- 「力学で出た行動を言語が後追い説明する」
"""

import json
import os
import random
import requests

# Claude APIを使う場合
try:
    import anthropic
    HAS_ANTHROPIC = True
except ImportError:
    HAS_ANTHROPIC = False


class AIBrain:
    def __init__(self, use_ollama=False, ollama_model="gemma3:4b", use_api=False, api_key=None):
        self.use_ollama = use_ollama
        self.ollama_model = ollama_model
        self.use_api = use_api and HAS_ANTHROPIC
        self.api_key = api_key or os.environ.get('ANTHROPIC_API_KEY')
        
        if self.use_api and self.api_key:
            self.client = anthropic.Anthropic(api_key=self.api_key)
        else:
            self.client = None
            
        self.available_actions = [
            'move_forward',
            'turn_left', 
            'turn_right',
            'grab',
            'release',
            'wait'
        ]
        
        # LLMは説明用のみ
        self.explain_prompt = """あなたは「飛騨」というロボットの内省担当です。
飛騨が選んだ行動について、なぜその行動が選ばれたかを説明してください。

重要：あなたは行動を決めません。行動は既に決まっています。
あなたの仕事は「その行動の理由」と「自己認識」を言語化することです。

注意：
- 理由が分からない場合は「理由は不明」「説明できない」と正直に言ってください
- 過度に意味を付与しないでください
- 単純な行動には単純な説明で十分です
- waitの場合、特に深い意味はないかもしれません

出力形式（JSON）：
{
  "reasoning": "なぜこの行動が選ばれたか（分からなければ「不明」でも可）",
  "self_awareness": "今の自分の状態（シンプルに）"
}"""

    def decide_action(self, state_json, world):
        """
        行動を決定する
        
        1. 飛騨のルールで行動を決定
        2. LLMで説明を生成（オプション）
        """
        # Step 1: 飛騨のルールで行動決定
        action, rule_reason = self._decide_by_rule(state_json, world)
        
        # Step 2: LLMで説明生成（use_ollama が True の場合のみ）
        if self.use_ollama or self.use_api:
            explanation = self._explain_with_llm(state_json, action, rule_reason)
        else:
            explanation = {
                "reasoning": rule_reason,
                "self_awareness": self._generate_self_awareness(state_json)
            }
        
        return {
            "action": action,
            "rule_reason": rule_reason,  # 飛騨のルールによる理由
            "reasoning": explanation.get("reasoning", rule_reason),  # LLMの説明
            "self_awareness": explanation.get("self_awareness", "")
        }
    
    def _decide_by_rule(self, state_json, world):
        """
        飛騨のルールベース行動決定
        
        優先順位：
        0. 意識ON時に微小探索ノイズ（穴③修正）
        1. 目標物が正面にあって手が空 → grab
        2. 目標物を持っていてゴールが正面 → release
        3. 目標物を持っていてゴールが近い → ゴール方向へ
        4. 目標物が見える → 目標物方向へ
        5. 目標物が見えない → 探索 or 目標達成
        """
        body = state_json.get('L1_body', {})
        consciousness = state_json.get('L5_consciousness', {})
        qualia = state_json.get('L2_qualia', {})
        
        goal = consciousness.get('current_goal', '')
        holding = body.get('holding')
        position = body.get('position', [0, 0])
        direction = body.get('direction', 'N')
        front_cell = world.get_front_cell()
        legal_actions = world.get_legal_actions()
        is_conscious = consciousness.get('is_conscious', False)
        curiosity = qualia.get('curiosity', 0)
        
        # ========== 穴③修正: 意識ON時に微小探索ノイズ ==========
        if is_conscious and curiosity > 0.5:
            if random.random() < 0.1:  # 10%の確率で探索
                explore_actions = [a for a in legal_actions if a != 'wait']
                if explore_actions:
                    return random.choice(explore_actions), "好奇心による探索行動"
        
        # 目標物を特定
        target_obj = None
        if 'red' in goal.lower():
            target_obj = 'red_ball'
        elif 'blue' in goal.lower():
            target_obj = 'blue_box'
        
        # ========== 優先度1: 目標物を掴む ==========
        if target_obj and not holding:
            if front_cell == target_obj and 'grab' in legal_actions:
                return 'grab', f"目標の{target_obj}が正面にあるので掴む"
        
        # ========== 優先度2: ゴールで置く ==========
        if holding and ('goal' in goal.lower() or '届け' in goal):
            if front_cell == 'goal' and 'release' in legal_actions:
                return 'release', f"ゴールに到着したので{holding}を置く"
        
        # ========== 優先度3: ゴールに向かう（持っている場合） ==========
        if holding and ('goal' in goal.lower() or '届け' in goal):
            goal_pos = world.find_object('goal')
            if goal_pos:
                action, reason = self._move_toward(position, direction, goal_pos, legal_actions, 'goal')
                if action:
                    return action, reason
        
        # ========== 優先度4: 目標物に向かう ==========
        if target_obj and not holding:
            target_pos = world.find_object(target_obj)
            if target_pos:
                action, reason = self._move_toward(position, direction, target_pos, legal_actions, target_obj)
                if action:
                    return action, reason
            else:
                # 目標物が見つからない = 既にgoalに届けた可能性
                return 'wait', "目標達成！ red_ballをgoalに届けました"
        
        # ========== 優先度5: 探索 ==========
        return self._explore(legal_actions)
    
    def _move_toward(self, pos, direction, target_pos, legal_actions, target_name):
        """目標に向かう行動を決定"""
        dx = target_pos[0] - pos[0]
        dy = target_pos[1] - pos[1]
        
        # 目標方向を決定
        target_dir = None
        if abs(dx) >= abs(dy):
            target_dir = 'E' if dx > 0 else 'W'
        else:
            target_dir = 'S' if dy > 0 else 'N'
        
        # 既に目標方向を向いている
        if direction == target_dir:
            if 'move_forward' in legal_actions:
                return 'move_forward', f"{target_name}に向かって前進"
            else:
                # 前が塞がっている → 迂回
                return self._detour(direction, legal_actions, target_name)
        
        # 目標方向を向く
        turn = self._get_turn_direction(direction, target_dir)
        if turn in legal_actions:
            return turn, f"{target_name}の方向（{target_dir}）を向く"
        
        return None, ""
    
    def _get_turn_direction(self, current, target):
        """目標方向に向くための回転を決定"""
        dirs = ['N', 'E', 'S', 'W']
        current_idx = dirs.index(current)
        target_idx = dirs.index(target)
        
        diff = (target_idx - current_idx) % 4
        if diff == 1:
            return 'turn_right'
        elif diff == 3:
            return 'turn_left'
        elif diff == 2:
            # 180度 → どちらでも
            return 'turn_right'
        return 'wait'
    
    def _detour(self, direction, legal_actions, target_name):
        """迂回行動"""
        if 'turn_right' in legal_actions:
            return 'turn_right', f"前が塞がっているので迂回（{target_name}へ）"
        if 'turn_left' in legal_actions:
            return 'turn_left', f"前が塞がっているので迂回（{target_name}へ）"
        return 'wait', "動けない"
    
    def _explore(self, legal_actions):
        """探索行動"""
        if 'move_forward' in legal_actions:
            return 'move_forward', "探索のため前進"
        if 'turn_right' in legal_actions:
            return 'turn_right', "探索のため方向転換"
        if 'turn_left' in legal_actions:
            return 'turn_left', "探索のため方向転換"
        return 'wait', "動けない"
    
    def _generate_self_awareness(self, state_json):
        """ルールベースの自己認識生成"""
        qualia = state_json.get('L2_qualia', {})
        prediction = state_json.get('L3_prediction', {})
        consciousness = state_json.get('L5_consciousness', {})
        body = state_json.get('L1_body', {})
        
        frustration = qualia.get('frustration', 0)
        pred_error = prediction.get('prediction_error', 0)
        sync = consciousness.get('sync_score', 0)
        is_conscious = consciousness.get('is_conscious', False)
        goal = consciousness.get('current_goal', '')
        holding = body.get('holding')
        
        parts = []
        
        if is_conscious:
            parts.append(f"意識ON（同期{sync:.1%}）")
        else:
            parts.append(f"反射モード（同期{sync:.1%}）")
        
        if holding:
            parts.append(f"{holding}を保持中")
        
        if goal:
            parts.append(f"目標「{goal}」")
        
        if pred_error > 0.5:
            parts.append("予測誤差大：状況を再評価中")
        
        if frustration > 0.5:
            parts.append("フラストレーション高：別のアプローチを検討")
        
        return "。".join(parts) + "。"
    
    def _explain_with_llm(self, state_json, action, rule_reason):
        """LLMで行動の説明を生成"""
        prompt = f"""{self.explain_prompt}

【飛騨の現在の状態】
{json.dumps(state_json, indent=2, ensure_ascii=False)}

【選ばれた行動】
{action}

【ルールによる理由】
{rule_reason}

この行動の理由と、飛騨の自己認識を言語化してください。
JSONのみを出力してください。"""

        if self.use_ollama:
            return self._call_ollama(prompt)
        elif self.use_api and self.client:
            return self._call_claude_api(prompt)
        else:
            return {"reasoning": rule_reason, "self_awareness": ""}
    
    def _call_ollama(self, prompt):
        """ollamaを呼び出す"""
        try:
            response = requests.post(
                'http://localhost:11434/api/generate',
                json={
                    'model': self.ollama_model,
                    'prompt': prompt,
                    'stream': False
                },
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                response_text = result.get('response', '')
                return self._parse_json_response(response_text)
            else:
                print(f"ollama error: {response.status_code}")
                return {}
                
        except requests.exceptions.ConnectionError:
            print("ollama is not running")
            return {}
        except Exception as e:
            print(f"ollama Error: {e}")
            return {}
    
    def _call_claude_api(self, prompt):
        """Claude APIを呼び出す"""
        try:
            message = self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=500,
                messages=[{"role": "user", "content": prompt}]
            )
            response_text = message.content[0].text
            return self._parse_json_response(response_text)
        except Exception as e:
            print(f"Claude API Error: {e}")
            return {}
    
    def _parse_json_response(self, text):
        """LLMの応答からJSONを抽出"""
        try:
            # ```json ... ``` の形式に対応
            if "```json" in text:
                text = text.split("```json")[1].split("```")[0]
            elif "```" in text:
                text = text.split("```")[1].split("```")[0]
            
            # JSONっぽい部分を探す
            start = text.find('{')
            end = text.rfind('}') + 1
            if start != -1 and end > start:
                text = text[start:end]
            
            return json.loads(text.strip())
        except json.JSONDecodeError:
            return {"reasoning": text[:200], "self_awareness": ""}


# テスト
if __name__ == "__main__":
    brain = AIBrain(use_ollama=False)
    print("AIBrain initialized (rule-based mode)")
