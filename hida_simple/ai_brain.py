"""
ai_brain.py
シンプル版 - 記憶を使った行動決定

クオリアなし、好奇心なし
基本ルール + 教わったこと + 自己記憶
"""


class AIBrain:
    def __init__(self):
        pass
    
    def decide_action(self, state, world):
        """行動を決定"""
        goal = state.goal
        holding = state.holding
        position = state.position
        direction = state.direction
        front_cell = world.get_front_cell()
        legal_actions = world.get_legal_actions()
        
        # ========== 目的がないと動かない ==========
        if not goal:
            return 'wait', "目的がない"
        
        # ========== 教わったことをチェック ==========
        teaching_action = self._check_teachings(state, front_cell, legal_actions, world)
        if teaching_action:
            return teaching_action
        
        # ========== 基本ルール ==========
        
        # 目標物が正面にあって手が空 → grab
        if 'red_ball' in str(front_cell) and not holding and 'grab' in legal_actions:
            return 'grab', "red_ballを掴む"
        
        # 目標物を持っていてゴールが正面 → release
        if holding == 'red_ball' and front_cell == 'goal' and 'release' in legal_actions:
            return 'release', "goalに届ける"
        
        # 目標物を持っている → goalへ向かう
        if holding == 'red_ball':
            goal_pos = world.find_object('goal')
            if goal_pos:
                return self._move_toward(position, direction, goal_pos, legal_actions, "goal")
        
        # 目標物を持っていない → red_ballへ向かう
        else:
            ball_pos = world.find_object('red_ball')
            if ball_pos:
                return self._move_toward(position, direction, ball_pos, legal_actions, "red_ball")
        
        # どうしようもない → wait
        return 'wait', "判断できない"
    
    def _check_teachings(self, state, front_cell, legal_actions, world):
        """教わったことに該当するか確認"""
        teachings = state.teachings
        recent = list(state.recent_results)
        position = state.position
        
        if not teachings:
            return None
        
        # この場所での経験を集計
        pos_str = f"{position[0]},{position[1]}"
        move_failures_here = 0  # move_forwardの失敗だけカウント
        actions_here = []
        
        for r in recent:
            r_pos = r.get('position', [])
            if isinstance(r_pos, list) and len(r_pos) == 2:
                r_pos_str = f"{r_pos[0]},{r_pos[1]}"
                if r_pos_str == pos_str:
                    actions_here.append(r.get('action', ''))
                    # move_forwardの失敗だけカウント
                    if r.get('action') == 'move_forward' and not r.get('success', True):
                        move_failures_here += 1
        
        for teaching in teachings:
            condition = teaching.get('condition', '')
            action_text = teaching.get('action', '')
            
            # 条件: 同じ場所で失敗 + 前がブロックされてる
            if '同じ場所' in condition and '失敗' in condition:
                # 前が空いてたら教えは適用しない（新しい方向で試せ）
                if front_cell == 'empty' or front_cell is None:
                    continue
                    
                import re
                nums = re.findall(r'(\d+)回', condition)
                threshold = int(nums[0]) if nums else 2
                
                if move_failures_here >= threshold:
                    action = self._resolve_action(action_text, actions_here, legal_actions, world)
                    if action:
                        return action, f"教え適用: {condition}"
            
            # 条件: 壁
            if '壁' in condition:
                if front_cell and str(front_cell).startswith('wall'):
                    action = self._resolve_action(action_text, actions_here, legal_actions, world)
                    if action:
                        return action, f"教え適用: {condition}"
        
        return None
    
    def _resolve_action(self, action_text, actions_here, legal_actions, world):
        """教えのアクションを具体的な行動に変換（進める方向を選ぶ）"""
        
        if '別' in action_text or '他' in action_text or '違う' in action_text:
            # 進める方向を探す
            current_dir = world.hida_dir
            turns = {'N': 'E', 'E': 'S', 'S': 'W', 'W': 'N'}  # 右回転
            turns_left = {'N': 'W', 'W': 'S', 'S': 'E', 'E': 'N'}  # 左回転
            
            # 右に回ったら進めるか？
            right_dir = turns[current_dir]
            world.hida_dir = right_dir
            right_front = world.get_front_cell()
            right_can_move = 'move_forward' in world.get_legal_actions() and not str(right_front).startswith('wall')
            
            # 左に回ったら進めるか？
            left_dir = turns_left[current_dir]
            world.hida_dir = left_dir
            left_front = world.get_front_cell()
            left_can_move = 'move_forward' in world.get_legal_actions() and not str(left_front).startswith('wall')
            
            # 元に戻す
            world.hida_dir = current_dir
            
            # 進める方向を選ぶ
            if right_can_move and not left_can_move:
                return 'turn_right'
            elif left_can_move and not right_can_move:
                return 'turn_left'
            elif right_can_move and left_can_move:
                # 両方進める → 試した回数が少ない方
                left_count = actions_here.count('turn_left')
                right_count = actions_here.count('turn_right')
                return 'turn_left' if left_count <= right_count else 'turn_right'
            else:
                # どちらも進めない → とりあえず回転
                return 'turn_right' if 'turn_right' in legal_actions else 'turn_left'
        
        if '右' in action_text and 'turn_right' in legal_actions:
            return 'turn_right'
        
        if '左' in action_text and 'turn_left' in legal_actions:
            return 'turn_left'
        
        return None
    
    def _move_toward(self, pos, direction, target_pos, legal_actions, target_name):
        """目標に向かう"""
        dx = target_pos[0] - pos[0]
        dy = target_pos[1] - pos[1]
        
        # 目標方向を決定
        if abs(dx) >= abs(dy):
            primary = 'E' if dx > 0 else 'W'
            secondary = 'N' if dy < 0 else 'S' if dy > 0 else None
        else:
            primary = 'S' if dy > 0 else 'N'
            secondary = 'E' if dx > 0 else 'W' if dx < 0 else None
        
        # 既に目標方向を向いている → 前進
        if direction == primary:
            if 'move_forward' in legal_actions:
                return 'move_forward', f"{target_name}に向かって前進"
            else:
                # 前が塞がっている → 横に回る
                if 'turn_left' in legal_actions:
                    return 'turn_left', "前が塞がっている、左へ"
                if 'turn_right' in legal_actions:
                    return 'turn_right', "前が塞がっている、右へ"
        
        # secondary方向を向いてる → goalに近づくなら前進
        if secondary and direction == secondary:
            if 'move_forward' in legal_actions:
                return 'move_forward', f"回り込み中、前進"
        
        # それ以外の方向を向いてる → goalに近づくかチェック
        # 前進したら距離が縮まるか？
        move_delta = {'N': (0, -1), 'S': (0, 1), 'E': (1, 0), 'W': (-1, 0)}
        if direction in move_delta and 'move_forward' in legal_actions:
            mdx, mdy = move_delta[direction]
            new_pos = [pos[0] + mdx, pos[1] + mdy]
            current_dist = abs(dx) + abs(dy)
            new_dist = abs(target_pos[0] - new_pos[0]) + abs(target_pos[1] - new_pos[1])
            if new_dist < current_dist:
                return 'move_forward', f"回り込み中、前進"
        
        # goal方向を向く
        turn = self._get_turn(direction, primary)
        if turn in legal_actions:
            return turn, f"{target_name}の方向（{primary}）を向く"
        
        return 'wait', "判断できない"
    
    def _get_turn(self, current, target):
        """目標方向に向くための回転を決定"""
        dirs = ['N', 'E', 'S', 'W']
        ci = dirs.index(current)
        ti = dirs.index(target)
        diff = (ti - ci) % 4
        return 'turn_right' if diff <= 2 else 'turn_left'
