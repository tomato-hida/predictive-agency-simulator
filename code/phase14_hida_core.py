#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Phase 14: HIDA Core Architecture
飛騨アーキテクチャ本体

L1〜L5 が常時ループ
予測誤差で意識が ON/OFF
行動は「決める」んじゃなく「生まれる」

これが本物の飛騨
"""

import time
import math
import threading
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

# シミュレーション用
import pybullet as p
import pybullet_data


class ConsciousnessState(Enum):
    """意識状態"""
    IDLE = "待機"          # 予測誤差なし、暇
    ALERT = "注意"         # 名前呼ばれた
    ACTIVE = "活動"        # 行動中
    SEARCHING = "探索"     # 何か探してる
    HOLDING = "保持"       # 何か持ってる


@dataclass
class Qualia:
    """第2層：クオリア（感覚）"""
    visual: Dict = None      # 視覚情報
    auditory: str = ""       # 聴覚情報（言葉）
    touch: float = 0.0       # 触覚（-1〜+1）
    
    def __post_init__(self):
        if self.visual is None:
            self.visual = {}


@dataclass 
class Memory:
    """第4層：記憶"""
    objects: Dict = None       # 物体の記憶 {"赤いボール": {"color": "red", "shape": "sphere"}}
    last_seen: Dict = None     # 最後に見た位置 {"赤いボール": {"position": [2,1,0], "time": 123}}
    original_pos: Dict = None  # 初期位置（元に戻す用）{"赤いボール": [2,1,0]}
    success_rate: Dict = None  # 成功率 {"赤いボール": {"found": 3, "failed": 1}}
    experiences: List = None   # 経験の記録
    preferences: Dict = None   # 学習した好み {"verbs": {...}, "responses": {...}}
    
    def __post_init__(self):
        if self.objects is None:
            self.objects = {
                "赤いボール": {"color": "red", "shape": "sphere", "size": 0.2},
                "黄色いボール": {"color": "yellow", "shape": "sphere", "size": 0.2},
                "青いボール": {"color": "blue", "shape": "sphere", "size": 0.2},
                "青い箱": {"color": "blue", "shape": "box", "size": 0.3},
            }
        if self.last_seen is None:
            self.last_seen = {}
        if self.original_pos is None:
            self.original_pos = {}
        if self.success_rate is None:
            self.success_rate = {}
        if self.experiences is None:
            self.experiences = []
        if self.preferences is None:
            self.preferences = {
                "verbs": {},      # 動詞の言い方 {"ゲット": "fetch"}
                "responses": {},  # 応答 {"おはよう": "おはようございます"}
            }
    
    def remember_position(self, obj_name: str, position: List[float]):
        """物体の位置を記憶"""
        import time as t
        self.last_seen[obj_name] = {
            "position": position,
            "time": t.time(),
        }
        # 初期位置がなければ記録（初めて見た場所）
        if obj_name not in self.original_pos:
            self.original_pos[obj_name] = list(position)
            print(f"  [記憶] {obj_name} の初期位置を記録: {position}")
    
    def get_last_position(self, obj_name: str) -> Optional[List[float]]:
        """最後に見た位置を取得"""
        if obj_name in self.last_seen:
            return self.last_seen[obj_name]["position"]
        return None
    
    def get_original_position(self, obj_name: str) -> Optional[List[float]]:
        """初期位置を取得（元に戻す用）"""
        return self.original_pos.get(obj_name)
    
    def record_success(self, obj_name: str, found: bool):
        """探索の成功/失敗を記録"""
        if obj_name not in self.success_rate:
            self.success_rate[obj_name] = {"found": 0, "failed": 0}
        
        if found:
            self.success_rate[obj_name]["found"] += 1
        else:
            self.success_rate[obj_name]["failed"] += 1
    
    def get_success_rate(self, obj_name: str) -> float:
        """成功率を取得"""
        if obj_name not in self.success_rate:
            return 0.5  # 未知は50%
        
        stats = self.success_rate[obj_name]
        total = stats["found"] + stats["failed"]
        if total == 0:
            return 0.5
        return stats["found"] / total
    
    # learn_preference は削除（preferences の構造 verbs/responses/custom_actions と衝突するため）
    # 学習は _handle_answer 内で直接 verbs/responses/custom_actions に書き込む
    
    def get_preference(self, keyword: str) -> Optional[str]:
        """学習した好みを取得（後方互換用）"""
        # verbs, responses, custom_actions を検索
        if keyword in self.preferences.get("verbs", {}):
            return self.preferences["verbs"][keyword]
        if keyword in self.preferences.get("responses", {}):
            return self.preferences["responses"][keyword]
        if keyword in self.preferences.get("custom_actions", {}):
            return self.preferences["custom_actions"][keyword]
        return None


class HidaCore:
    """
    飛騨アーキテクチャ本体
    L1〜L5 が常時ループ
    """
    
    def __init__(self):
        # ===== 5層構造 =====
        # L1: 身体層（センサー/モーター）
        self.body_state = {
            "position": [0, 0, 0],
            "holding": None,
            "energy": 1.0,
        }
        
        # L2: クオリア層（感覚）
        self.qualia = Qualia()
        
        # L3: 構造化層（予測と誤差）
        self.prediction = {
            "expected_state": None,
            "current_goal": None,
        }
        self.prediction_error = 0.0
        
        # L4: 記憶層
        self.memory = Memory()
        
        # L5: 意識層
        self.consciousness = ConsciousnessState.IDLE
        self.self_strength = 0.1
        self.attention_target = None
        
        # ===== システム =====
        self.name = "飛騨"
        self.running = False
        self.loop_interval = 0.1  # 100ms
        
        # シミュレーション
        self.sim = None
        
        # 行動キュー（複数タスク対応）
        self.action_queue = []
        self.current_action = None
        
        # 質問待ち状態
        self.waiting_for_answer = False
        self.pending_question = None  # {"type": "which_object", "keyword": "ボール", "options": [...]}
        
        print("飛騨アーキテクチャ 起動")
    
    # ==========================================
    # メインループ（常時回る）
    # ==========================================
    
    def start_loop(self):
        """L1〜L5 ループ開始"""
        self.running = True
        print("ループ開始...")
        
        while self.running:
            self._loop_cycle()
            time.sleep(self.loop_interval)
    
    def stop_loop(self):
        """ループ停止"""
        self.running = False
        print("ループ停止")
    
    def _loop_cycle(self):
        """1サイクル：L1→L2→L3→L4→L5→行動"""
        
        # L1: 身体からの入力
        self._layer1_body_input()
        
        # L2: クオリアに変換
        self._layer2_qualia()
        
        # L3: 構造化・予測誤差
        self._layer3_structure()
        
        # L4: 記憶参照
        self._layer4_memory()
        
        # L5: 意識・統合
        self._layer5_consciousness()
        
        # 行動出力
        self._action_output()
    
    # ==========================================
    # 各層の処理
    # ==========================================
    
    def _layer1_body_input(self):
        """L1: 身体層 - センサー入力"""
        if self.sim:
            # シミュレーションから位置取得
            pos = self.sim.get_robot_position()
            self.body_state["position"] = list(pos)
            
            # 視覚情報取得
            self.qualia.visual = self.sim.get_visual_info()
    
    def _layer2_qualia(self):
        """L2: クオリア層 - 感覚を生成"""
        # 聴覚入力があれば処理
        if self.qualia.auditory:
            # 名前が呼ばれたか？
            if self.name in self.qualia.auditory:
                self.prediction_error += 0.5  # 誤差増大
                self.attention_target = "caller"
            # 聴覚入力は1回で消費（次サイクルでの誤差二重加算を防ぐ）
            self.qualia.auditory = ""
    
    def _layer3_structure(self):
        """L3: 構造化層 - 予測と誤差"""
        
        # 目標がある場合、現状との差を計算
        if self.prediction["current_goal"]:
            goal = self.prediction["current_goal"]
            
            if goal["type"] == "find_object":
                # 物体を探す目標
                target_name = goal["target"]
                found = self._search_in_visual(target_name)
                
                if found:
                    self.prediction_error = 0.1  # 見つかった、誤差小
                    goal["found"] = True
                    goal["position"] = found
                else:
                    self.prediction_error = 0.6  # 見つからない、誤差大
            
            elif goal["type"] == "reach_object":
                # 物体に近づく目標
                if goal.get("position"):
                    distance = self._distance_to(goal["position"])
                    self.prediction_error = min(distance / 3.0, 1.0)
            
            elif goal["type"] == "deliver":
                # 届ける目標
                if self.body_state["holding"]:
                    distance = self._distance_to([0, 0, 0])  # 原点に届ける
                    self.prediction_error = min(distance / 3.0, 1.0)
        else:
            # 目標なし → 暇
            self.prediction_error *= 0.9  # 徐々に減衰
    
    def _layer4_memory(self):
        """L4: 記憶層 - 記憶検索と活用"""
        
        goal = self.prediction.get("current_goal")
        if not goal:
            return
        
        target = goal.get("target")
        if not target:
            return
        
        # 記憶から最後に見た位置を取得
        last_pos = self.memory.get_last_position(target)
        if last_pos and not goal.get("checked_memory"):
            print(f"  [記憶] {target} は前回 {last_pos} にあった")
            goal["hint_position"] = last_pos
            goal["checked_memory"] = True
        
        # 成功率を確認
        rate = self.memory.get_success_rate(target)
        if rate < 0.3 and not goal.get("warned"):
            print(f"  [記憶] {target} の発見率は {rate:.0%}、見つかりにくいかも")
            goal["warned"] = True
    
    def _layer5_consciousness(self):
        """L5: 意識層 - 統合と判断"""
        
        # 予測誤差と自己強度で意識状態を決定
        if self.prediction_error > 0.5:
            if self.consciousness == ConsciousnessState.IDLE:
                self.consciousness = ConsciousnessState.ALERT
                print(f"  [意識ON] 予測誤差: {self.prediction_error:.2f}")
        elif self.prediction_error < 0.1:
            if self.consciousness not in [ConsciousnessState.IDLE]:
                self.consciousness = ConsciousnessState.IDLE
                print(f"  [意識OFF] 待機状態")
        
        # 自己強度の更新
        if self.prediction_error > 0.3:
            self.self_strength = min(1.0, self.self_strength + 0.01)
    
    def _action_output(self):
        """行動出力 - キューから行動を取り出して実行"""
        
        # 現在の行動がなければキューから取り出す
        if not self.current_action and self.action_queue:
            self.current_action = self.action_queue.pop(0)
            print(f"  [キュー] 次のタスク開始（残り: {len(self.action_queue)}件）")
        
        if not self.current_action:
            return
        
        action = self.current_action
        
        if action["type"] == "search":
            self._do_search(action["target"])
        elif action["type"] == "fetch":
            self._do_fetch(action["target"])
        elif action["type"] == "put_back":
            self._do_put_back(action["target"])
        elif action["type"] == "pick_up":
            self._do_pick_up()
        elif action["type"] == "deliver":
            self._do_deliver()
        elif action["type"] == "return_to_origin":
            self._do_return_to_origin()
        elif action["type"] == "wait":
            self.current_action = None
            if self.action_queue:
                print(f"  [キュー] 残りタスク: {len(self.action_queue)}件")
    
    # ==========================================
    # 補助関数
    # ==========================================
    
    def _search_in_visual(self, target_name: str) -> Optional[List[float]]:
        """視覚情報から対象を探す"""
        if not self.qualia.visual:
            return None
        
        # 記憶から対象の特徴を取得
        target_features = self.memory.objects.get(target_name, {})
        if not target_features:
            return None
        
        target_color = target_features.get("color")
        
        # 視覚情報と照合
        for obj_id, obj_info in self.qualia.visual.items():
            if obj_info.get("color") == target_color:
                return obj_info.get("position")
        
        return None
    
    def _distance_to(self, target: List[float]) -> float:
        """対象までの距離"""
        pos = self.body_state["position"]
        return math.sqrt(
            (target[0] - pos[0])**2 + 
            (target[1] - pos[1])**2
        )
    
    # ==========================================
    # 行動実行
    # ==========================================
    
    def _do_search(self, target_name: str):
        """探索行動"""
        print(f"  [探索中] {target_name}")
        
        # goal がなければ作成
        if not self.prediction.get("current_goal"):
            self.prediction["current_goal"] = {
                "type": "find_object",
                "target": target_name,
            }
        
        goal = self.prediction["current_goal"]
        
        # まず記憶のヒント位置に向かう
        hint_pos = goal.get("hint_position")
        if hint_pos and not goal.get("checked_hint"):
            print(f"  [記憶活用] 前回の位置 {hint_pos} を確認")
            if self.sim:
                self.sim.move_toward(hint_pos)
            goal["checked_hint"] = True
            return  # 次のサイクルで視覚確認
        
        # 視覚で探す
        found = self._search_in_visual(target_name)
        
        if found:
            print(f"  [発見] 位置: {found}")
            # 記憶を更新
            self.memory.remember_position(target_name, found)
            self.memory.record_success(target_name, True)
            
            self.prediction["current_goal"] = {
                "type": "reach_object",
                "target": target_name,
                "position": found,
            }
            self.current_action = {"type": "pick_up"}
        else:
            # まだ見つからない、探し続ける
            self.memory.record_success(target_name, False)
            if self.sim:
                self.sim.move_randomly()
    
    def _do_pick_up(self):
        """拾う行動"""
        goal = self.prediction["current_goal"]
        if not goal or not goal.get("position"):
            return
        
        pos = goal["position"]
        distance = self._distance_to(pos)
        
        if distance < 0.5:
            # 近い、拾える
            target_name = goal['target']
            print(f"  [拾う] {target_name}")
            # 対象の色を取得してシミュレーションに渡す
            target_features = self.memory.objects.get(target_name, {})
            target_color = target_features.get("color")
            if self.sim:
                self.sim.pick_up(target_color)
            self.body_state["holding"] = target_name
            
            # 次の目標：届ける
            self.prediction["current_goal"] = {"type": "deliver"}
            self.current_action = {"type": "deliver"}
        else:
            # まだ遠い、近づく
            print(f"  [接近中] 距離: {distance:.2f}")
            if self.sim:
                self.sim.move_toward(pos)
    
    def _do_deliver(self):
        """届ける行動"""
        if not self.body_state["holding"]:
            self.current_action = None
            return
        
        distance = self._distance_to([0, 0, 0])
        
        if distance < 0.5:
            # 到着、置く
            obj_name = self.body_state["holding"]
            print(f"  [完了] {obj_name} を届けました")
            if self.sim:
                self.sim.put_down()
            
            # 経験を記録
            self.memory.experiences.append({
                "action": "deliver",
                "object": obj_name,
                "success": True,
                "time": time.time(),
            })
            print(f"  [経験] 成功体験を記録（累計: {len(self.memory.experiences)}件）")
            
            self.body_state["holding"] = None
            self.prediction["current_goal"] = None
            self.current_action = {"type": "wait"}
            
            # キューに次のタスクがあれば続行、なければ待機
            if not self.action_queue:
                self.consciousness = ConsciousnessState.IDLE
        else:
            # まだ遠い、運ぶ
            print(f"  [運搬中] 距離: {distance:.2f}")
            if self.sim:
                self.sim.move_toward([0, 0, 0])
    
    def _do_fetch(self, target_name: str):
        """取ってくる（search + pick_up + deliver の複合）"""
        # まず探す
        self._do_search(target_name)
    
    def _do_put_back(self, target_name: str):
        """元に戻す行動"""
        # 初期位置を記憶から取得
        original_pos = self.memory.get_original_position(target_name)
        
        if not original_pos:
            print(f"  → [L4] {target_name} の初期位置がわかりません")
            self.current_action = None
            return
        
        goal = self.prediction.get("current_goal", {})
        
        # まだ持ってない → 探して拾う
        if not self.body_state["holding"]:
            # 探す
            found = self._search_in_visual(target_name)
            if found:
                distance = self._distance_to(found)
                if distance < 0.5:
                    print(f"  [拾う] {target_name}")
                    # 対象の色を取得してシミュレーションに渡す
                    target_features = self.memory.objects.get(target_name, {})
                    target_color = target_features.get("color")
                    if self.sim:
                        self.sim.pick_up(target_color)
                    self.body_state["holding"] = target_name
                    # 初期位置を goal に保存
                    self.prediction["current_goal"] = {
                        "type": "put_back",
                        "target": target_name,
                        "origin": original_pos,
                    }
                    print(f"  [戻す] 初期位置 {original_pos} に向かいます")
                else:
                    print(f"  [接近中] 距離: {distance:.2f}")
                    if self.sim:
                        self.sim.move_toward(found)
            else:
                print(f"  [探索中] {target_name}")
                if self.sim:
                    self.sim.move_randomly()
        else:
            # 持ってる → 初期位置に運ぶ
            origin = goal.get("origin", original_pos)
            distance = self._distance_to(origin)
            
            if distance < 0.5:
                print(f"  [完了] {target_name} を初期位置 {origin} に戻しました")
                if self.sim:
                    self.sim.put_down()
                
                self.memory.experiences.append({
                    "action": "put_back",
                    "object": target_name,
                    "success": True,
                    "time": time.time(),
                })
                print(f"  [経験] 成功体験を記録（累計: {len(self.memory.experiences)}件）")
                
                self.body_state["holding"] = None
                self.prediction["current_goal"] = None
                self.current_action = {"type": "wait"}
                
                if not self.action_queue:
                    self.consciousness = ConsciousnessState.IDLE
            else:
                print(f"  [戻し中] 初期位置まで: {distance:.2f}")
                if self.sim:
                    self.sim.move_toward(origin)
    
    def _do_return_to_origin(self):
        """原点に戻る"""
        distance = self._distance_to([0, 0, 0])
        if distance < 0.5:
            print(f"  [完了] 原点に戻りました")
            self.current_action = None
            if not self.action_queue:
                self.consciousness = ConsciousnessState.IDLE
        else:
            print(f"  [移動中] 原点まで: {distance:.2f}")
            if self.sim:
                self.sim.move_toward([0, 0, 0])
    
    # ==========================================
    # 外部入力
    # ==========================================
    
    def hear(self, text: str):
        """聴覚入力（人間からの言葉）"""
        print(f"\n【聞こえた】「{text}」")
        self.qualia.auditory = text
        
        # 質問の回答待ちの場合
        if self.waiting_for_answer and self.pending_question:
            self._handle_answer(text)
            return
        
        # 名前が含まれてるか
        if self.name in text:
            print(f"  → 呼ばれた！")
            self.consciousness = ConsciousnessState.ALERT
            self.prediction_error = 0.6
            
            # コマンド解析
            self._parse_command(text)
    
    def _handle_answer(self, text: str):
        """質問への回答を処理"""
        question = self.pending_question
        
        if question["type"] == "which_object":
            # 対象の回答（覚えない）
            options = question["options"]
            action_type = question.get("action_type", "search")  # 元のアクションを取得
            
            # 回答から対象を特定
            selected = None
            for opt in options:
                if "赤" in text and "赤" in opt:
                    selected = opt
                    break
                elif "黄" in text and "黄" in opt:
                    selected = opt
                    break
                elif "青" in text and "青" in opt:
                    selected = opt
                    break
                elif opt in text:
                    selected = opt
                    break
            
            if selected:
                print(f"  → 了解！「{selected}」ですね")
                # 行動開始（元のアクションタイプを使う）
                self._start_action(selected, action_type)
            else:
                print(f"  → すみません、わかりませんでした")
            
            # 質問終了
            self.waiting_for_answer = False
            self.pending_question = None
        
        elif question["type"] == "which_verb":
            # 動詞/応答の回答（覚える）
            original_text = question["original_text"]
            
            # 「応答を教える」が選ばれた場合
            if "応答" in text or "返事" in text:
                # 次の質問：何と言えばいい？
                self.pending_question = {
                    "type": "teach_response",
                    "original_text": original_text,
                }
                print(f"  → 【質問】「{original_text}」に対して何と言えばいいですか？")
                return
            
            # 「行動を教える」が選ばれた場合
            if "行動" in text:
                # 次の質問：何をすればいい？
                self.pending_question = {
                    "type": "teach_action",
                    "original_text": original_text,
                }
                print(f"  → 【質問】「{original_text}」で何をすればいいですか？（例: 全部数える、報告する、など）")
                return
            
            # 回答から動詞を特定
            verb_map = {
                "持ってくる": "fetch",
                "持って": "fetch",
                "探す": "search",
                "探し": "search",
                "置く": "put",
                "置い": "put",
                "元に戻す": "put_back",
                "戻す": "put_back",
                "返す": "put_back",
                "返し": "put_back",
            }
            
            action_type = None
            for key, action in verb_map.items():
                if key in text:
                    action_type = action
                    break
            
            if action_type:
                # 元のテキストから動詞部分を抽出して覚える
                keywords_to_learn = []
                for word in ["ゲット", "取ってこい", "持ってこい", "フェッチ", "get", "fetch"]:
                    if word.lower() in original_text.lower():
                        keywords_to_learn.append(word)
                
                if not keywords_to_learn:
                    clean_text = original_text.replace("飛騨、", "").replace("飛騨，", "").replace("飛騨", "").strip()
                    for i in range(min(5, len(clean_text)), 0, -1):
                        candidate = clean_text[-i:]
                        if candidate not in self.memory.objects:
                            keywords_to_learn.append(candidate)
                            break
                
                # 学習
                if "verbs" not in self.memory.preferences:
                    self.memory.preferences["verbs"] = {}
                
                for keyword in keywords_to_learn:
                    self.memory.preferences["verbs"][keyword] = action_type
                    print(f"  [学習] 「{keyword}」→「{action_type}」を覚えました")
                
                print(f"  → 了解！もう一度言ってください")
            else:
                print(f"  → すみません、わかりませんでした。「応答を教える」と言うと、返事を教えられます")
            
            # 質問終了
            self.waiting_for_answer = False
            self.pending_question = None
        
        elif question["type"] == "teach_response":
            # 応答を教える
            original_text = question["original_text"]
            response_text = text.strip()
            
            # キーワードを抽出（「飛騨、」を除く）
            keyword = original_text.replace("飛騨、", "").replace("飛騨，", "").replace("飛騨", "").strip()
            
            # 学習
            if "responses" not in self.memory.preferences:
                self.memory.preferences["responses"] = {}
            
            self.memory.preferences["responses"][keyword] = response_text
            print(f"  [学習] 「{keyword}」→「{response_text}」を覚えました")
            print(f"  → 了解！")
            
            # 質問終了
            self.waiting_for_answer = False
            self.pending_question = None
        
        elif question["type"] == "teach_action":
            # 行動を教える
            original_text = question["original_text"]
            action_description = text.strip()
            
            # キーワードを抽出（「飛騨、」を除く）
            keyword = original_text.replace("飛騨、", "").replace("飛騨，", "").replace("飛騨", "").strip()
            
            # 学習（カスタムアクションとして保存）
            if "custom_actions" not in self.memory.preferences:
                self.memory.preferences["custom_actions"] = {}
            
            self.memory.preferences["custom_actions"][keyword] = action_description
            print(f"  [学習] 「{keyword}」→ 行動「{action_description}」を覚えました")
            print(f"  → 了解！")
            
            # 質問終了
            self.waiting_for_answer = False
            self.pending_question = None
    

    def _parse_command(self, text: str):
        """コマンドを解析（L3の構造化）- L4 記憶ベース、人間に学ぶ"""
        
        # 「止まれ」は即座に対応
        if "止まれ" in text or "止まって" in text or "ストップ" in text:
            print(f"  → 停止（キューをクリア）")
            self.action_queue.clear()
            self.current_action = None
            self.prediction["current_goal"] = None
            self.consciousness = ConsciousnessState.IDLE
            return
        
        # ===== 学習済みの応答をチェック =====
        responses = self.memory.preferences.get("responses", {})
        for keyword, response in responses.items():
            if keyword in text:
                print(f"  → [L4] 「{keyword}」→「{response}」")
                print(f"  飛騨: 「{response}」")
                self.consciousness = ConsciousnessState.IDLE
                return
        
        # ===== 学習済みのカスタム行動をチェック =====
        custom_actions = self.memory.preferences.get("custom_actions", {})
        for keyword, action_desc in custom_actions.items():
            if keyword in text:
                print(f"  → [L4] 「{keyword}」→ 行動「{action_desc}」")
                # カスタム行動を実行（今は報告するだけ）
                self._execute_custom_action(keyword, action_desc)
                return
        
        # ===== 動詞の解析 =====
        # 知っている動詞パターン
        action_patterns = {
            "持ってきて": "fetch",
            "取って": "fetch",
            "とって": "fetch",
            "探して": "search",
            "見つけて": "search",
            "返して": "put_back",
            "戻して": "put_back",
        }
        
        # 学習済みの動詞もチェック
        action_patterns.update(self.memory.preferences.get("verbs", {}))
        
        action_type = None
        for pattern, action in action_patterns.items():
            if pattern in text:
                action_type = action
                break
        
        # 動詞がわからない場合
        if not action_type:
            # 新しい言い方を学習するか聞く
            print(f"  → [L4] この言い方がわかりません")
            self._ask_verb_question(text)
            return
        
        # ===== 対象の解析 =====
        # 1. 知っている物体を直接検索
        found_objects = []
        for obj_name in self.memory.objects.keys():
            if obj_name in text:
                found_objects.append(obj_name)
        
        # 完全一致があればそれを使う
        if found_objects:
            if len(found_objects) == 1:
                print(f"  → [L4] 「{found_objects[0]}」を認識")
                self._start_action(found_objects[0], action_type if action_type else "search")
            else:
                # 複数あれば全部
                print(f"  → [L4] 複数認識: {', '.join(found_objects)}")
                for obj in found_objects:
                    self.action_queue.append({"type": action_type if action_type else "search", "target": obj})
                self.prediction["current_goal"] = {
                    "type": "find_object",
                    "target": found_objects[0],
                }
                print(f"  [キュー] {len(found_objects)}件のタスクを追加")
                self.consciousness = ConsciousnessState.SEARCHING
            return
        
        # 2. 色名で推測
        color_map = {"赤": "赤いボール", "黄": "黄色いボール", "青": "青いボール"}
        for color, obj in color_map.items():
            if color in text and obj in self.memory.objects:
                print(f"  → [L4] 「{color}」→「{obj}」と推測")
                self._start_action(obj, action_type if action_type else "search")
                return
        
        # 3. 「全部」「全て」チェック
        if "全部" in text or "全て" in text or "すべて" in text:
            if "ボール" in text:
                balls = [obj for obj in self.memory.objects.keys() if "ボール" in obj]
                if balls:
                    print(f"  → [L4] 全ボール: {', '.join(balls)}")
                    for ball in balls:
                        self.action_queue.append({"type": action_type if action_type else "search", "target": ball})
                    self.prediction["current_goal"] = {
                        "type": "find_object",
                        "target": balls[0],
                    }
                    print(f"  [キュー] {len(balls)}件のタスクを追加")
                    self.consciousness = ConsciousnessState.SEARCHING
                    return
        
        # 4. 対象が曖昧 → 毎回聞く（覚えない）
        if "ボール" in text:
            balls = [obj for obj in self.memory.objects.keys() if "ボール" in obj]
            self._ask_object_question("ボール", balls, action_type if action_type else "search")
            return
        
        # 5. 完全に不明 → 何を取るか聞く
        all_objects = list(self.memory.objects.keys())
        print(f"  → [L4] 何を指しているかわかりません")
        self._ask_object_question("対象", all_objects, action_type if action_type else "search")
    
    def _start_action(self, target: str, action_type: str = "search"):
        """行動を開始"""
        self.prediction["current_goal"] = {
            "type": "find_object",
            "target": target,
            "action": action_type,  # fetch, search, put_back
        }
        self.action_queue.append({"type": action_type, "target": target})
        print(f"  [キュー] 1件のタスクを追加（{action_type}）")
        self.consciousness = ConsciousnessState.SEARCHING
    
    def _execute_custom_action(self, keyword: str, action_desc: str):
        """カスタム行動を実行"""
        print(f"  [カスタム行動] {action_desc}")
        
        # 「数える」「何個」が含まれていたらボールを数える
        if "数え" in action_desc or "何個" in action_desc or "カウント" in action_desc:
            if self.sim:
                visual = self.sim.get_visual_info()
                count = len([v for v in visual.values() if v.get("shape") == "sphere"])
                print(f"  飛騨: 「ボールは{count}個あります」")
            else:
                print(f"  飛騨: 「視覚情報がありません」")
        
        # 「報告」が含まれていたら状態を報告
        elif "報告" in action_desc or "状態" in action_desc:
            holding = self.body_state.get("holding")
            if holding:
                print(f"  飛騨: 「{holding}を持っています」")
            else:
                print(f"  飛騨: 「何も持っていません」")
        
        # それ以外は行動内容を言うだけ
        else:
            print(f"  飛騨: 「{action_desc}...了解しました」")
        
        self.consciousness = ConsciousnessState.IDLE
    
    def _ask_object_question(self, keyword: str, options: List[str], action_type: str = "search"):
        """対象を聞く（毎回聞く、覚えない）"""
        self.waiting_for_answer = True
        self.pending_question = {
            "type": "which_object",
            "keyword": keyword,
            "options": options,
            "action_type": action_type,  # 元のアクションを保持
            "learn": False,
        }
        options_str = "、".join(options)
        print(f"  → 【質問】どの{keyword}ですか？（{options_str}）")
    
    def _ask_verb_question(self, original_text: str):
        """動詞/応答の意味を聞く（覚える）"""
        self.waiting_for_answer = True
        self.pending_question = {
            "type": "which_verb",
            "original_text": original_text,
            "options": ["持ってくる", "探す", "置く", "元に戻す", "応答を教える", "行動を教える"],
            "learn": True,
        }
        print(f"  → 【質問】「{original_text}」はどういう意味ですか？（持ってくる、探す、置く、元に戻す、応答を教える、行動を教える）")
    


# ==========================================
# シミュレーション（簡易版）
# ==========================================

class HidaSimulation:
    """飛騨用シミュレーション"""
    
    def __init__(self):
        self.physics_client = p.connect(p.GUI)
        p.setAdditionalSearchPath(pybullet_data.getDataPath())
        p.setGravity(0, 0, -10)
        
        # 床
        self.plane_id = p.loadURDF("plane.urdf")
        
        # ロボット
        self.robot_id = self._create_robot()
        
        # ボール3つ
        self.balls = {
            "red": self._create_ball([2, 1, 0.3], [0.9, 0.1, 0.1, 1]),
            "yellow": self._create_ball([-1, 2, 0.3], [0.9, 0.9, 0.1, 1]),
            "blue": self._create_ball([1, -2, 0.3], [0.1, 0.3, 0.9, 1]),
        }
        
        self.is_holding = False
        self.holding_ball = None
        self.put_count = 0  # 置いた回数
        print("シミュレーション起動（ボール3つ）")
    
    def _create_robot(self):
        col = p.createCollisionShape(p.GEOM_BOX, halfExtents=[0.3, 0.2, 0.1])
        vis = p.createVisualShape(p.GEOM_BOX, halfExtents=[0.3, 0.2, 0.1],
                                  rgbaColor=[0.2, 0.4, 0.8, 1])
        return p.createMultiBody(baseMass=1, baseCollisionShapeIndex=col,
                                 baseVisualShapeIndex=vis, basePosition=[0, 0, 0.2])
    
    def _create_ball(self, pos, color):
        col = p.createCollisionShape(p.GEOM_SPHERE, radius=0.2)
        vis = p.createVisualShape(p.GEOM_SPHERE, radius=0.2, rgbaColor=color)
        return p.createMultiBody(baseMass=0.5, baseCollisionShapeIndex=col,
                                 baseVisualShapeIndex=vis, basePosition=pos)
    
    def get_robot_position(self):
        pos, _ = p.getBasePositionAndOrientation(self.robot_id)
        return pos
    
    def get_visual_info(self) -> Dict:
        """視覚情報を返す（複数ボール対応）"""
        result = {}
        
        for color, ball_id in self.balls.items():
            pos, _ = p.getBasePositionAndOrientation(ball_id)
            result[f"ball_{color}"] = {
                "color": color,
                "shape": "sphere",
                "position": list(pos),
            }
        
        return result
    
    def move_toward(self, target):
        """対象に向かって移動"""
        pos = list(self.get_robot_position())
        dx = target[0] - pos[0]
        dy = target[1] - pos[1]
        dist = math.sqrt(dx*dx + dy*dy)
        
        if dist > 0.1:
            speed = 0.1
            pos[0] += (dx / dist) * speed
            pos[1] += (dy / dist) * speed
            p.resetBasePositionAndOrientation(self.robot_id, [pos[0], pos[1], 0.2], [0,0,0,1])
            
            if self.is_holding and self.holding_ball:
                p.resetBasePositionAndOrientation(
                    self.balls[self.holding_ball], 
                    [pos[0], pos[1], 0.5], [0,0,0,1]
                )
        
        p.stepSimulation()
    
    def move_randomly(self):
        """ランダムに動く（探索）"""
        import random
        pos = list(self.get_robot_position())
        pos[0] += random.uniform(-0.1, 0.1)
        pos[1] += random.uniform(-0.1, 0.1)
        p.resetBasePositionAndOrientation(self.robot_id, [pos[0], pos[1], 0.2], [0,0,0,1])
        p.stepSimulation()
    
    def pick_up(self, color: str = None):
        """拾う（指定した色のボール）"""
        robot_pos = self.get_robot_position()
        
        # 色が指定されていればその色を拾う
        if color and color in self.balls:
            self.is_holding = True
            self.holding_ball = color
            pos = self.get_robot_position()
            p.resetBasePositionAndOrientation(
                self.balls[color], 
                [pos[0], pos[1], 0.5], [0,0,0,1]
            )
            return
        
        # 色が指定されてなければ一番近いボールを拾う
        closest_color = None
        closest_dist = float('inf')
        
        for c, ball_id in self.balls.items():
            pos, _ = p.getBasePositionAndOrientation(ball_id)
            dist = math.sqrt((pos[0]-robot_pos[0])**2 + (pos[1]-robot_pos[1])**2)
            if dist < closest_dist:
                closest_dist = dist
                closest_color = c
        
        if closest_color:
            self.is_holding = True
            self.holding_ball = closest_color
            pos = self.get_robot_position()
            p.resetBasePositionAndOrientation(
                self.balls[closest_color], 
                [pos[0], pos[1], 0.5], [0,0,0,1]
            )
    
    def put_down(self):
        """置く"""
        if self.holding_ball:
            pos = self.get_robot_position()
            # 置いた回数でずらす
            offset_x = 0.3 + self.put_count * 0.3
            self.put_count += 1
            p.resetBasePositionAndOrientation(
                self.balls[self.holding_ball],
                [pos[0]+offset_x, pos[1], 0.2], [0,0,0,1]
            )
            self.is_holding = False
            self.holding_ball = None
    
    def close(self):
        p.disconnect()


# ==========================================
# 実行
# ==========================================

def main():
    print("=" * 60)
    print("Phase 14: HIDA Core Architecture")
    print("飛騨アーキテクチャ本体")
    print("=" * 60)
    print()
    print("L1〜L5 が常時ループ")
    print("名前を呼ぶと意識 ON")
    print()
    
    # 飛騨起動
    hida = HidaCore()
    
    # シミュレーション接続
    hida.sim = HidaSimulation()
    
    # ループを別スレッドで開始
    loop_thread = threading.Thread(target=hida.start_loop, daemon=True)
    loop_thread.start()
    
    print("\n" + "-" * 60)
    print("コマンド入力（例: 「飛騨、赤いボールを持ってきて」）")
    print("'q' で終了")
    print("-" * 60)
    
    try:
        while True:
            text = input("\nあなた: ").strip()
            if text.lower() == 'q':
                break
            if text:
                hida.hear(text)
                # 行動が終わるまで待つ
                time.sleep(0.5)
                while hida.current_action or hida.action_queue:
                    time.sleep(0.2)
    except KeyboardInterrupt:
        pass
    
    hida.stop_loop()
    hida.sim.close()
    print("\n終了")


if __name__ == "__main__":
    main()
