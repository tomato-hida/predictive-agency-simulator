# ==========================================
# Phase 16: 飛騨アーキテクチャ（1ファイル版）
# 5層構造 + 予測ベース学習
# ==========================================

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Callable
from enum import Enum
import time
import threading
import json
import os
import math


# ==========================================
# L1: 身体層（プリミティブ）
# 機械のDNA = 生まれつきの能力
# ==========================================

class PrimitiveResult(Enum):
    """プリミティブの実行結果"""
    SUCCESS = "success"
    FAILURE = "failure"
    BLOCKED = "blocked"


@dataclass
class ArmPrimitive:
    """腕のプリミティブ（1本分）"""
    name: str
    
    shoulder_angle: float = 0.0
    elbow_angle: float = 0.0
    wrist_angle: float = 0.0
    wrist_rotation: float = 0.0
    hand_closed: bool = False
    
    def shoulder_up(self, amount: float = 10.0) -> PrimitiveResult:
        self.shoulder_angle = min(180.0, self.shoulder_angle + amount)
        return PrimitiveResult.SUCCESS
    
    def shoulder_down(self, amount: float = 10.0) -> PrimitiveResult:
        self.shoulder_angle = max(0.0, self.shoulder_angle - amount)
        return PrimitiveResult.SUCCESS
    
    def elbow_bend(self, amount: float = 10.0) -> PrimitiveResult:
        self.elbow_angle = min(150.0, self.elbow_angle + amount)
        return PrimitiveResult.SUCCESS
    
    def elbow_straight(self, amount: float = 10.0) -> PrimitiveResult:
        self.elbow_angle = max(0.0, self.elbow_angle - amount)
        return PrimitiveResult.SUCCESS
    
    def wrist_up(self, amount: float = 10.0) -> PrimitiveResult:
        self.wrist_angle = min(90.0, self.wrist_angle + amount)
        return PrimitiveResult.SUCCESS
    
    def wrist_down(self, amount: float = 10.0) -> PrimitiveResult:
        self.wrist_angle = max(-90.0, self.wrist_angle - amount)
        return PrimitiveResult.SUCCESS
    
    def wrist_rotate(self, amount: float = 10.0) -> PrimitiveResult:
        self.wrist_rotation = (self.wrist_rotation + amount) % 360.0
        return PrimitiveResult.SUCCESS
    
    def hand_open(self) -> PrimitiveResult:
        self.hand_closed = False
        return PrimitiveResult.SUCCESS
    
    def hand_close(self) -> PrimitiveResult:
        self.hand_closed = True
        return PrimitiveResult.SUCCESS
    
    def get_state(self) -> Dict:
        return {
            "name": self.name,
            "shoulder_angle": self.shoulder_angle,
            "elbow_angle": self.elbow_angle,
            "wrist_angle": self.wrist_angle,
            "wrist_rotation": self.wrist_rotation,
            "hand_closed": self.hand_closed,
        }


@dataclass
class HidaPrimitives:
    """飛騨のDNA（全プリミティブ）"""
    
    position: list = field(default_factory=lambda: [0.0, 0.0, 0.0])
    direction: float = 0.0
    waist_rotation: float = 0.0
    neck_horizontal: float = 0.0
    neck_vertical: float = 0.0
    arms: Dict[str, ArmPrimitive] = field(default_factory=dict)
    sim: Optional[object] = None
    
    def __post_init__(self):
        if not self.arms:
            self.arms["right"] = ArmPrimitive(name="right")
            self.arms["left"] = ArmPrimitive(name="left")
    
    # 移動系
    def move_forward(self, distance: float = 0.1) -> PrimitiveResult:
        rad = math.radians(self.direction)
        self.position[0] += math.cos(rad) * distance
        self.position[1] += math.sin(rad) * distance
        if self.sim:
            self.sim.move_robot(self.position)
        return PrimitiveResult.SUCCESS
    
    def move_back(self, distance: float = 0.1) -> PrimitiveResult:
        rad = math.radians(self.direction)
        self.position[0] -= math.cos(rad) * distance
        self.position[1] -= math.sin(rad) * distance
        if self.sim:
            self.sim.move_robot(self.position)
        return PrimitiveResult.SUCCESS
    
    def turn_left(self, angle: float = 10.0) -> PrimitiveResult:
        self.direction = (self.direction + angle) % 360.0
        if self.sim:
            self.sim.rotate_robot(self.direction)
        return PrimitiveResult.SUCCESS
    
    def turn_right(self, angle: float = 10.0) -> PrimitiveResult:
        self.direction = (self.direction - angle) % 360.0
        if self.sim:
            self.sim.rotate_robot(self.direction)
        return PrimitiveResult.SUCCESS
    
    def stop(self) -> PrimitiveResult:
        return PrimitiveResult.SUCCESS
    
    # 腰
    def waist_left(self, amount: float = 10.0) -> PrimitiveResult:
        self.waist_rotation = min(90.0, self.waist_rotation + amount)
        return PrimitiveResult.SUCCESS
    
    def waist_right(self, amount: float = 10.0) -> PrimitiveResult:
        self.waist_rotation = max(-90.0, self.waist_rotation - amount)
        return PrimitiveResult.SUCCESS
    
    # 首
    def neck_left(self, amount: float = 10.0) -> PrimitiveResult:
        self.neck_horizontal = min(90.0, self.neck_horizontal + amount)
        return PrimitiveResult.SUCCESS
    
    def neck_right(self, amount: float = 10.0) -> PrimitiveResult:
        self.neck_horizontal = max(-90.0, self.neck_horizontal - amount)
        return PrimitiveResult.SUCCESS
    
    def neck_up(self, amount: float = 10.0) -> PrimitiveResult:
        self.neck_vertical = min(45.0, self.neck_vertical + amount)
        return PrimitiveResult.SUCCESS
    
    def neck_down(self, amount: float = 10.0) -> PrimitiveResult:
        self.neck_vertical = max(-45.0, self.neck_vertical - amount)
        return PrimitiveResult.SUCCESS
    
    # 感覚系
    def look(self) -> PrimitiveResult:
        if self.sim:
            result = self.sim.get_visual_info()
            print(f"  [視覚] {result}")
        else:
            print(f"  [視覚] (シミュレーションなし)")
        return PrimitiveResult.SUCCESS
    
    def listen(self) -> PrimitiveResult:
        print(f"  [聴覚] 待機中...")
        return PrimitiveResult.SUCCESS
    
    # 出力系
    def say(self, text: str) -> PrimitiveResult:
        print(f"  飛騨: 「{text}」")
        return PrimitiveResult.SUCCESS
    
    # 腕管理
    def add_arm(self, name: str) -> ArmPrimitive:
        arm = ArmPrimitive(name=name)
        self.arms[name] = arm
        return arm
    
    def get_arm(self, name: str) -> Optional[ArmPrimitive]:
        return self.arms.get(name)
    
    def get_state(self) -> Dict:
        return {
            "position": self.position.copy(),
            "direction": self.direction,
            "waist_rotation": self.waist_rotation,
            "neck_horizontal": self.neck_horizontal,
            "neck_vertical": self.neck_vertical,
            "arms": {name: arm.get_state() for name, arm in self.arms.items()},
        }


# ==========================================
# L2: クオリア層
# センサー入力 → ラベル + 評価値
# ==========================================

class Priority(Enum):
    """優先度"""
    CRITICAL = 4
    HIGH = 3
    MEDIUM = 2
    LOW = 1


@dataclass
class Qualia:
    """クオリア = パターン + ラベル + 評価値"""
    label: str
    value: float  # -1.0〜+1.0（不快〜快）
    priority: Priority
    source: str = ""
    target: Optional[str] = None
    
    def is_negative(self) -> bool:
        return self.value < 0
    
    def is_critical(self) -> bool:
        return self.priority == Priority.CRITICAL


@dataclass
class L2QualiaLayer:
    """第2層：クオリア層（人優先の評価システム）"""
    
    DNA_VALUES = {
        "人を検出": (+0.8, Priority.HIGH),
        "人の声": (+0.7, Priority.HIGH),
        "人にぶつかった": (-0.9, Priority.CRITICAL),
        "人が近い": (+0.5, Priority.HIGH),
        "人が離れた": (-0.2, Priority.MEDIUM),
        "壁にぶつかった": (-0.5, Priority.MEDIUM),
        "物にぶつかった": (-0.3, Priority.MEDIUM),
        "何かに触れた": (0.0, Priority.LOW),
        "タスク完了": (+0.6, Priority.MEDIUM),
        "タスク失敗": (-0.4, Priority.MEDIUM),
        "指示を受けた": (+0.5, Priority.HIGH),
        "停止中": (0.0, Priority.LOW),
        "移動中": (+0.1, Priority.LOW),
        "把持成功": (+0.4, Priority.MEDIUM),
        "把持失敗": (-0.3, Priority.MEDIUM),
        "エラー発生": (-0.6, Priority.HIGH),
        "バッテリー低下": (-0.7, Priority.HIGH),
    }
    
    current_qualia: List[Qualia] = field(default_factory=list)
    
    def clear_qualia(self):
        """クオリアをクリア（サイクル開始時に呼ぶ）"""
        self.current_qualia = []
    
    def process_sensor(self, sensor_type: str, data: Dict) -> List[Qualia]:
        qualia_list = []
        
        if sensor_type == "visual":
            qualia_list.extend(self._process_visual(data))
        elif sensor_type == "tactile":
            qualia_list.extend(self._process_tactile(data))
        elif sensor_type == "auditory":
            qualia_list.extend(self._process_auditory(data))
        
        # 上書きではなく追加
        self.current_qualia.extend(qualia_list)
        return qualia_list
    
    def _process_visual(self, data: Dict) -> List[Qualia]:
        qualia_list = []
        objects = data.get("objects", [])
        
        for obj in objects:
            obj_type = obj.get("type", "unknown")
            distance = obj.get("distance", 999)
            
            if obj_type == "human":
                if distance < 0.5:
                    q = self._create_qualia("人が近い", "visual", "人")
                else:
                    q = self._create_qualia("人を検出", "visual", "人")
                qualia_list.append(q)
            elif obj_type in ["ball", "box", "object"]:
                q = Qualia(
                    label="物体を検出",
                    value=0.1,
                    priority=Priority.LOW,
                    source="visual",
                    target=obj.get("name", obj_type)
                )
                qualia_list.append(q)
        
        return qualia_list
    
    def _process_tactile(self, data: Dict) -> List[Qualia]:
        qualia_list = []
        
        collision = data.get("collision", False)
        collision_target = data.get("collision_target", "unknown")
        
        if collision:
            if collision_target == "human":
                q = self._create_qualia("人にぶつかった", "tactile", "人")
            elif collision_target == "wall":
                q = self._create_qualia("壁にぶつかった", "tactile", "壁")
            else:
                q = self._create_qualia("物にぶつかった", "tactile", collision_target)
            qualia_list.append(q)
        
        grip = data.get("grip", None)
        if grip == "success":
            q = self._create_qualia("把持成功", "tactile")
            qualia_list.append(q)
        elif grip == "failure":
            q = self._create_qualia("把持失敗", "tactile")
            qualia_list.append(q)
        
        return qualia_list
    
    def _process_auditory(self, data: Dict) -> List[Qualia]:
        qualia_list = []
        
        voice = data.get("voice", False)
        is_human = data.get("is_human", False)
        text = data.get("text", "")
        
        if voice and is_human:
            q = self._create_qualia("人の声", "auditory", "人")
            qualia_list.append(q)
            
            if text:
                q = self._create_qualia("指示を受けた", "auditory")
                qualia_list.append(q)
        
        return qualia_list
    
    def _create_qualia(self, label: str, source: str, target: str = None) -> Qualia:
        if label in self.DNA_VALUES:
            value, priority = self.DNA_VALUES[label]
        else:
            value, priority = (0.0, Priority.LOW)
        
        return Qualia(
            label=label,
            value=value,
            priority=priority,
            source=source,
            target=target
        )
    
    def get_most_important(self) -> Optional[Qualia]:
        if not self.current_qualia:
            return None
        sorted_q = sorted(
            self.current_qualia,
            key=lambda q: (q.priority.value, abs(q.value)),
            reverse=True
        )
        return sorted_q[0]
    
    def has_critical(self) -> bool:
        return any(q.is_critical() for q in self.current_qualia)
    
    def get_total_value(self) -> float:
        if not self.current_qualia:
            return 0.0
        return sum(q.value for q in self.current_qualia) / len(self.current_qualia)


# ==========================================
# L3: 構造化層
# 予測 + 誤差計算 + L4連携
# ==========================================

@dataclass
class L3StructureLayer:
    """第3層：構造化層（予測と誤差）"""
    
    predictions: Dict[str, float] = field(default_factory=dict)
    prediction_error: float = 0.0
    CONSCIOUSNESS_THRESHOLD = 0.3
    error_history: List[float] = field(default_factory=list)
    action_prediction: Dict = field(default_factory=dict)
    action_results: List[Dict] = field(default_factory=list)
    
    def __post_init__(self):
        self.predictions = {
            "collision": 0.0,
            "human_nearby": 0.0,
            "task_success": 0.8,
            "error": 0.0,
        }
        self.action_prediction = {}
    
    def process_qualia(self, qualia_list: List[Qualia]) -> float:
        if not qualia_list:
            self.prediction_error *= 0.9
            return self.prediction_error
        
        errors = []
        for q in qualia_list:
            error = self._calculate_error(q)
            errors.append(error)
        
        if errors:
            self.prediction_error = max(errors)
        
        self.error_history.append(self.prediction_error)
        if len(self.error_history) > 100:
            self.error_history.pop(0)
        
        return self.prediction_error
    
    def _calculate_error(self, q: Qualia) -> float:
        if "ぶつかった" in q.label:
            predicted = self.predictions.get("collision", 0.0)
            actual = 1.0
            error = abs(actual - predicted)
            if q.target == "人":
                error = 1.0
            return error
        
        if "人" in q.label:
            predicted = self.predictions.get("human_nearby", 0.0)
            actual = 1.0
            error = abs(actual - predicted)
            return error * 0.8
        
        if "タスク完了" in q.label:
            predicted = self.predictions.get("task_success", 0.8)
            actual = 1.0
            error = abs(actual - predicted)
            return error * 0.3
        
        if "タスク失敗" in q.label:
            predicted = self.predictions.get("task_success", 0.8)
            actual = 0.0
            error = abs(actual - predicted)
            return error
        
        if "エラー" in q.label:
            predicted = self.predictions.get("error", 0.0)
            actual = 1.0
            error = abs(actual - predicted)
            return error
        
        return abs(q.value) * 0.5
    
    def predict_action(self, word: str, l4_memory) -> Dict:
        """L4の記憶から行動を予測"""
        primitives = l4_memory.get_primitives(word)
        
        if primitives:
            self.action_prediction = {
                "word": word,
                "primitives": primitives,
                "expected_result": "success",
                "confidence": 0.9,
            }
            self.prediction_error = 0.1
        else:
            self.action_prediction = {
                "word": word,
                "primitives": None,
                "expected_result": "unknown",
                "confidence": 0.0,
            }
            self.prediction_error = 1.0
        
        return self.action_prediction
    
    def verify_action_result(self, actual_result: str, l4_memory) -> float:
        """行動結果を検証して予測誤差を計算"""
        if not self.action_prediction:
            return 0.0
        
        expected = self.action_prediction.get("expected_result", "unknown")
        word = self.action_prediction.get("word", "")
        primitives = self.action_prediction.get("primitives", [])
        
        if expected == actual_result:
            error = 0.1
            success = True
        elif expected == "unknown":
            error = 0.8
            success = (actual_result == "success")
        else:
            error = 0.9
            success = False
        
        self.action_results.append({
            "word": word,
            "primitives": primitives,
            "expected": expected,
            "actual": actual_result,
            "error": error,
        })
        
        if len(self.action_results) > 100:
            self.action_results.pop(0)
        
        self.prediction_error = error
        
        if success and primitives and word:
            self._reinforce_learning(word, primitives, l4_memory)
        
        return error
    
    def _reinforce_learning(self, word: str, primitives: List[str], l4_memory):
        """成功パターンを強化"""
        existing = l4_memory.get_primitives(word)
        if existing is None:
            l4_memory.learn(word, primitives, success=True)
            print(f"  [L3→L4 自主学習] 「{word}」→ {primitives}")
    
    def should_activate_consciousness(self) -> bool:
        return self.prediction_error > self.CONSCIOUSNESS_THRESHOLD
    
    def get_error_trend(self) -> str:
        if len(self.error_history) < 2:
            return "stable"
        recent = self.error_history[-5:]
        if len(recent) < 2:
            return "stable"
        diff = recent[-1] - recent[0]
        if diff > 0.1:
            return "increasing"
        elif diff < -0.1:
            return "decreasing"
        return "stable"


# ==========================================
# L4: 記憶層
# 言葉 → プリミティブ の紐づけ
# ==========================================

MEMORY_FILE = "hida_memory.json"


@dataclass
class L4Memory:
    """第4層：記憶層"""
    
    word_to_primitive: Dict[str, List[str]] = field(default_factory=dict)
    learning_history: List[Dict] = field(default_factory=list)
    
    DNA_KNOWLEDGE = {
        # ==========================================
        # 基本移動
        # ==========================================
        "前に進め": ["move_forward"],
        "前進": ["move_forward"],
        "進め": ["move_forward"],
        "後ろに進め": ["move_back"],
        "後退": ["move_back"],
        "下がれ": ["move_back"],
        "左を向け": ["turn_left"],
        "左向け": ["turn_left"],
        "右を向け": ["turn_right"],
        "右向け": ["turn_right"],
        "止まれ": ["stop"],
        "ストップ": ["stop"],
        "停止": ["stop"],
        
        # ==========================================
        # 腰
        # ==========================================
        "腰を左に": ["waist_left"],
        "腰を右に": ["waist_right"],
        
        # ==========================================
        # 首（基本）
        # ==========================================
        "上を見ろ": ["neck_up"],
        "下を見ろ": ["neck_down"],
        "左を見ろ": ["neck_left"],
        "右を見ろ": ["neck_right"],
        
        # ==========================================
        # 右腕（基本）
        # ==========================================
        "右手を上げろ": ["right.shoulder_up"],
        "右手を下げろ": ["right.shoulder_down"],
        "右肘を曲げろ": ["right.elbow_bend"],
        "右肘を伸ばせ": ["right.elbow_straight"],
        "右手を開け": ["right.hand_open"],
        "右手を握れ": ["right.hand_close"],
        
        # ==========================================
        # 左腕（基本）
        # ==========================================
        "左手を上げろ": ["left.shoulder_up"],
        "左手を下げろ": ["left.shoulder_down"],
        "左肘を曲げろ": ["left.elbow_bend"],
        "左肘を伸ばせ": ["left.elbow_straight"],
        "左手を開け": ["left.hand_open"],
        "左手を握れ": ["left.hand_close"],
        
        # ==========================================
        # 両手（基本）
        # ==========================================
        "手を開け": ["right.hand_open", "left.hand_open"],
        "手を握れ": ["right.hand_close", "left.hand_close"],
        "両手を上げろ": ["right.shoulder_up", "left.shoulder_up"],
        "両手を下げろ": ["right.shoulder_down", "left.shoulder_down"],
        
        # ==========================================
        # コミュニケーション動作（Claude の知識）
        # ==========================================
        # うなずき
        "うなずいて": ["neck_down", "neck_up", "neck_down", "neck_up"],
        "うなずけ": ["neck_down", "neck_up", "neck_down", "neck_up"],
        "はい": ["neck_down", "neck_up"],
        "OK": ["neck_down", "neck_up"],
        "わかった": ["neck_down", "neck_up"],
        
        # 首を振る（否定）
        "首を振って": ["neck_left", "neck_right", "neck_left", "neck_right"],
        "いいえ": ["neck_left", "neck_right", "neck_left", "neck_right"],
        "違う": ["neck_left", "neck_right"],
        
        # 挨拶
        "挨拶して": ["right.shoulder_up", "right.hand_open", "waist_left", "waist_right", "right.shoulder_down"],
        "こんにちは": ["right.shoulder_up", "right.hand_open", "waist_left", "waist_right", "right.shoulder_down"],
        "バイバイ": ["right.shoulder_up", "right.hand_open", "right.hand_close", "right.hand_open", "right.hand_close", "right.hand_open"],
        "さようなら": ["right.shoulder_up", "right.hand_open", "right.hand_close", "right.hand_open", "right.shoulder_down"],
        "手を振って": ["right.shoulder_up", "right.hand_open", "waist_left", "waist_right", "waist_left", "waist_right"],
        
        # 感情表現
        "喜んで": ["right.shoulder_up", "left.shoulder_up", "neck_up"],
        "悲しんで": ["right.shoulder_down", "left.shoulder_down", "neck_down"],
        "驚いて": ["right.shoulder_up", "left.shoulder_up", "neck_up", "right.hand_open", "left.hand_open"],
        "考えて": ["neck_down", "right.elbow_bend", "right.shoulder_up"],
        "お手上げ": ["right.shoulder_up", "left.shoulder_up", "right.hand_open", "left.hand_open"],
        "降参": ["right.shoulder_up", "left.shoulder_up", "right.hand_open", "left.hand_open"],
        
        # ==========================================
        # 感覚動作（Claude の知識）
        # ==========================================
        "見て": ["look"],
        "見ろ": ["look"],
        "聞いて": ["listen"],
        "聞け": ["listen"],
        "上を見て": ["neck_up", "look"],
        "下を見て": ["neck_down", "look"],
        "左を見て": ["neck_left", "look"],
        "右を見て": ["neck_right", "look"],
        "周りを見て": ["neck_left", "look", "neck_right", "neck_right", "look", "neck_left"],
        "キョロキョロして": ["neck_left", "look", "neck_right", "look", "neck_left", "look", "neck_right", "look"],
        
        # 探索
        "探して": ["turn_left", "look", "turn_right", "turn_right", "look", "turn_left"],
        "見回して": ["turn_left", "look", "turn_left", "look", "turn_left", "look", "turn_left", "look"],
        "確認して": ["neck_down", "look", "neck_up", "look"],
        
        # ==========================================
        # 把持動作（Claude の知識）
        # ==========================================
        "取って": ["right.shoulder_down", "right.elbow_bend", "right.hand_open", "right.hand_close"],
        "つかんで": ["right.hand_open", "right.hand_close"],
        "握って": ["right.hand_close"],
        "離して": ["right.hand_open"],
        "放して": ["right.hand_open"],
        "持ち上げて": ["right.hand_close", "right.shoulder_up"],
        "置いて": ["right.shoulder_down", "right.hand_open"],
        "渡して": ["right.shoulder_up", "right.elbow_straight", "right.hand_open"],
        "受け取って": ["right.shoulder_up", "right.elbow_bend", "right.hand_open", "right.hand_close"],
        
        # ==========================================
        # 複合動作（Claude の知識）
        # ==========================================
        # ダンス系
        "踊って": ["turn_left", "right.shoulder_up", "turn_right", "left.shoulder_up", "turn_left", "right.shoulder_down", "left.shoulder_down"],
        "ダンス": ["turn_left", "right.shoulder_up", "turn_right", "left.shoulder_up", "turn_left"],
        
        # 体操系
        "ストレッチ": ["right.shoulder_up", "left.shoulder_up", "neck_up", "right.shoulder_down", "left.shoulder_down", "neck_down"],
        "体操して": ["right.shoulder_up", "right.shoulder_down", "left.shoulder_up", "left.shoulder_down", "turn_left", "turn_right"],
        "伸びして": ["right.shoulder_up", "left.shoulder_up", "neck_up"],
        
        # 待機・準備
        "待って": ["stop"],
        "待機": ["stop"],
        "準備して": ["right.shoulder_down", "left.shoulder_down", "right.hand_open", "left.hand_open", "neck_up"],
        "気をつけ": ["right.shoulder_down", "left.shoulder_down", "right.hand_close", "left.hand_close", "neck_up"],
        "休め": ["right.shoulder_down", "left.shoulder_down", "neck_down"],
        
        # 移動系（複合）
        "回れ": ["turn_left", "turn_left", "turn_left", "turn_left"],
        "回れ右": ["turn_right", "turn_right"],
        "回れ左": ["turn_left", "turn_left"],
        "一周して": ["turn_left", "turn_left", "turn_left", "turn_left"],
        "振り返って": ["turn_left", "turn_left"],
        "戻って": ["turn_left", "turn_left", "move_forward"],
        "近づいて": ["move_forward", "move_forward", "move_forward"],
        "離れて": ["move_back", "move_back", "move_back"],
    }
    
    # 意図（動詞）→ プリミティブ列（対象に依存しない行動パターン）
    INTENT_KNOWLEDGE = {
        "持ってきて": ["search_target", "move_to_target", "right.hand_open", "right.hand_close", "move_back", "right.hand_open"],
        "探して": ["search_target"],
        "見つけて": ["search_target"],
        "取って": ["move_to_target", "right.hand_open", "right.hand_close"],
        "置いて": ["right.shoulder_down", "right.hand_open"],
        "渡して": ["move_to_target", "right.shoulder_up", "right.hand_open"],
        "触って": ["move_to_target", "right.elbow_bend"],
        "押して": ["move_to_target", "move_forward"],
        "見て": ["look_at_target"],
    }
    
    # 対象（名詞）→ 知覚キー（どう見えるか）
    TARGET_KNOWLEDGE = {
        "赤いボール": {"color": "red", "shape": "sphere"},
        "青いボール": {"color": "blue", "shape": "sphere"},
        "緑のボール": {"color": "green", "shape": "sphere"},
        "ボール": {"shape": "sphere"},
        "赤い箱": {"color": "red", "shape": "box"},
        "青い箱": {"color": "blue", "shape": "box"},
        "箱": {"shape": "box"},
        "人": {"type": "human"},
        "壁": {"type": "wall"},
    }
    
    def __post_init__(self):
        for word, primitives in self.DNA_KNOWLEDGE.items():
            if word not in self.word_to_primitive:
                self.word_to_primitive[word] = primitives
    
    def parse_command(self, command: str) -> Tuple[Optional[str], Optional[str], Optional[str]]:
        """
        命令を「意図」と「対象」に分解
        
        Returns: (intent, target, remaining)
        
        例:
          「赤いボールを持ってきて」→ ("持ってきて", "赤いボール", None)
          「前に進め」→ (None, None, "前に進め")  # 従来方式
        """
        # 意図を探す（長い方優先）
        found_intent = None
        for intent in sorted(self.INTENT_KNOWLEDGE.keys(), key=len, reverse=True):
            if intent in command:
                found_intent = intent
                break
        
        # 対象を探す（長い方優先）
        found_target = None
        for target in sorted(self.TARGET_KNOWLEDGE.keys(), key=len, reverse=True):
            if target in command:
                found_target = target
                break
        
        # 意図も対象も見つからない → 従来方式
        if not found_intent and not found_target:
            return None, None, command
        
        # 意図だけ見つかった
        if found_intent and not found_target:
            return found_intent, None, None
        
        # 対象だけ見つかった（意図がない）
        if not found_intent and found_target:
            return None, found_target, command
        
        # 両方見つかった
        return found_intent, found_target, None
    
    def get_intent_primitives(self, intent: str) -> Optional[List[str]]:
        """意図からプリミティブ列を取得"""
        return self.INTENT_KNOWLEDGE.get(intent)
    
    def get_target_features(self, target: str) -> Optional[Dict]:
        """対象から知覚キーを取得"""
        # DNA知識を優先
        if target in self.TARGET_KNOWLEDGE:
            return self.TARGET_KNOWLEDGE[target]
        # 学習した対象を検索（将来用）
        return None
    
    def learn_target(self, target: str, features: Dict):
        """対象を学習"""
        self.TARGET_KNOWLEDGE[target] = features
        print(f"  [L4学習] 対象「{target}」→ {features}")
    
    def learn_intent(self, intent: str, primitives: List[str]):
        """意図を学習"""
        self.INTENT_KNOWLEDGE[intent] = primitives
        print(f"  [L4学習] 意図「{intent}」→ {primitives}")
    
    def get_primitives(self, word: str) -> Optional[List[str]]:
        # 完全一致を優先
        if word in self.word_to_primitive:
            return self.word_to_primitive[word]
        
        # 部分マッチ（長い方を優先）
        matches = []
        for key, value in self.word_to_primitive.items():
            if key in word:
                matches.append((key, value))
        
        if matches:
            # 長いキーを優先（「回れ右」>「回れ」）
            matches.sort(key=lambda x: len(x[0]), reverse=True)
            return matches[0][1]
        
        return None
    
    def learn(self, word: str, primitives: List[str], success: bool = True):
        if success:
            self.word_to_primitive[word] = primitives
            print(f"  [L4学習] 「{word}」→ {primitives}")
        self.learning_history.append({
            "word": word,
            "primitives": primitives,
            "success": success,
        })
    
    def save(self, filepath: str = MEMORY_FILE):
        learned = {k: v for k, v in self.word_to_primitive.items() 
                   if k not in self.DNA_KNOWLEDGE}
        data = {
            "word_to_primitive": learned,
            "learning_history": self.learning_history[-100:],
        }
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            print(f"  [L4保存] {filepath}")
        except Exception as e:
            print(f"  [L4保存エラー] {e}")
    
    def load(self, filepath: str = MEMORY_FILE):
        if not os.path.exists(filepath):
            print(f"  [L4] 保存ファイルなし、DNA知識のみで開始")
            return False
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            if "word_to_primitive" in data:
                for word, primitives in data["word_to_primitive"].items():
                    self.word_to_primitive[word] = primitives
            if "learning_history" in data:
                self.learning_history = data["learning_history"]
            learned_count = len(data.get("word_to_primitive", {}))
            print(f"  [L4読込] 学習済み: {learned_count}件")
            return True
        except Exception as e:
            print(f"  [L4読込エラー] {e}")
            return False


# ==========================================
# L5: 意識層
# 1-4層が同期したときに創発
# ==========================================

class ConsciousnessState(Enum):
    """意識状態"""
    IDLE = "idle"
    ALERT = "alert"
    FOCUSED = "focused"
    CRITICAL = "critical"


@dataclass
class L5Consciousness:
    """第5層：意識層（全層同期）"""
    
    state: ConsciousnessState = ConsciousnessState.IDLE
    sync_level: float = 0.0
    active_count: int = 0
    total_count: int = 0
    
    ACTIVATION_THRESHOLD = 0.3
    FOCUS_THRESHOLD = 0.6
    CRITICAL_THRESHOLD = 0.9
    MAX_PERSISTENCE = 0.7  # 70%ルール
    
    def update(self, prediction_error: float, has_critical: bool, qualia_value: float):
        self.total_count += 1
        
        importance = 1.0 if has_critical else (0.5 + abs(qualia_value) * 0.5)
        self.sync_level = prediction_error * importance
        
        if has_critical:
            self.state = ConsciousnessState.CRITICAL
            self.active_count += 1
            return
        
        if self.sync_level > self.CRITICAL_THRESHOLD:
            self.state = ConsciousnessState.CRITICAL
            self.active_count += 1
        elif self.sync_level > self.FOCUS_THRESHOLD:
            self.state = ConsciousnessState.FOCUSED
            self.active_count += 1
        elif self.sync_level > self.ACTIVATION_THRESHOLD:
            self.state = ConsciousnessState.ALERT
            self.active_count += 1
        else:
            self.state = ConsciousnessState.IDLE
        
        # 過負荷保護（70%ルール）
        if self.total_count > 10:
            persistence = self.active_count / self.total_count
            if persistence > self.MAX_PERSISTENCE:
                self.state = ConsciousnessState.IDLE
                self.sync_level *= 0.5
    
    def is_active(self) -> bool:
        return self.state != ConsciousnessState.IDLE
    
    def get_persistence(self) -> float:
        if self.total_count == 0:
            return 0.0
        return self.active_count / self.total_count


# ==========================================
# 飛騨アーキテクチャ（統合）
# ==========================================

class HidaCore:
    """
    飛騨アーキテクチャ（Phase 16）
    
    L1: 身体層（プリミティブ）
    L2: クオリア層（ラベル + 評価値）
    L3: 構造化層（予測 + 誤差）
    L4: 記憶層（言葉 → プリミティブ）
    L5: 意識層（全層同期）
    """
    
    def __init__(self):
        print("=" * 60)
        print("Phase 16: 飛騨アーキテクチャ")
        print("=" * 60)
        
        # L1〜L5 初期化
        self.l1 = HidaPrimitives()
        self.l2 = L2QualiaLayer()
        self.l3 = L3StructureLayer()
        self.l4 = L4Memory()
        self.l5 = L5Consciousness()
        
        self.l4.load()
        
        print(f"  [L1] 身体層（DNA知識: {len(self.l4.DNA_KNOWLEDGE)}個）")
        print(f"  [L2] クオリア層")
        print(f"  [L3] 構造化層")
        print(f"  [L4] 記憶層（意図: {len(self.l4.INTENT_KNOWLEDGE)}個、対象: {len(self.l4.TARGET_KNOWLEDGE)}個）")
        print(f"  [L5] 意識層")
        
        # システム
        self.name = "飛騨"
        self.running = False
        self.loop_interval = 0.1
        self.auditory_buffer = ""
        self.waiting_for_teaching = False
        self.pending_word = None
        self.waiting_input = False
        
        # 対象追跡用
        self.current_target = None  # 今探している対象
        self.current_target_features = None  # 対象の特徴
        self.target_found = False  # 対象を見つけたか
        
        # スレッド安全用ロック
        self._process_lock = threading.Lock()
        
        print("\n飛騨アーキテクチャ 起動完了")
    
    # ==========================================
    # メインループ
    # ==========================================
    
    def start_loop(self):
        self.running = True
        while self.running:
            self._loop_cycle()
            time.sleep(self.loop_interval)
    
    def stop_loop(self):
        self.running = False
    
    def _loop_cycle(self):
        """1サイクル：L1→L2→L3→L4→L5"""
        sensor_data = self._layer1_input()
        qualia_list, error = self._layer2_3_process(sensor_data)
        
        # auditory_buffer の処理は Lock で保護
        with self._process_lock:
            if self.auditory_buffer:
                self._layer4_process()
        
        self._layer5_update(error, qualia_list)
    
    def _layer1_input(self) -> Dict:
        # 視覚情報を取得（シミュレーションがあれば）
        if self.l1.sim:
            visual_data = self.l1.sim.get_visual_info()
        else:
            visual_data = {"objects": []}
        
        return {
            "visual": visual_data,
            "tactile": {"collision": False},
            "auditory": {
                "voice": bool(self.auditory_buffer),
                "is_human": True,
                "text": self.auditory_buffer
            }
        }
    
    def _layer2_3_process(self, sensor_data: Dict) -> Tuple[List[Qualia], float]:
        # サイクル開始時にクオリアをクリア
        self.l2.clear_qualia()
        
        all_qualia = []
        max_error = 0.0
        
        for sensor_type, data in sensor_data.items():
            if data:
                qualia_list = self.l2.process_sensor(sensor_type, data)
                all_qualia.extend(qualia_list)
                error = self.l3.process_qualia(qualia_list)
                max_error = max(max_error, error)
        
        return all_qualia, max_error
    
    def _layer4_process(self):
        """L4: 記憶参照 + L3予測 + 意図/対象分離"""
        text = self.auditory_buffer
        self.auditory_buffer = ""
        
        if not text:
            return
        
        # 学習待ちの場合
        if self.waiting_for_teaching:
            # キャンセル処理
            if any(w in text for w in ["キャンセル", "やめ", "cancel", "忘れて"]):
                print(f"  → キャンセルしました")
                self.waiting_for_teaching = False
                self.pending_word = None
                return
            self._handle_teaching(text)
            return
        
        # 名前で呼ばれたか
        if self.name not in text:
            return
        
        # 名前を除去
        command = text.replace(f"{self.name}、", "").replace(f"{self.name}，", "").replace(self.name, "").strip()
        
        if not command:
            return
        
        # 忘却機能: 「〇〇を忘れて」
        if "を忘れて" in command or "を忘れろ" in command:
            word_to_forget = command.replace("を忘れて", "").replace("を忘れろ", "").strip()
            self._forget(word_to_forget)
            return
        
        # 修飾語を解析（力加減）
        clean_command, multiplier = self._parse_modifier(command)
        
        # 意図と対象を分離
        intent, target, remaining = self.l4.parse_command(clean_command)
        
        # 意図と対象が見つかった場合
        if intent and target:
            print(f"  [L4] 意図: 「{intent}」, 対象: 「{target}」")
            
            # 対象を設定
            self.current_target = target
            self.current_target_features = self.l4.get_target_features(target)
            self.target_found = False
            
            if self.current_target_features:
                print(f"  [L4] 対象の特徴: {self.current_target_features}")
            
            # 意図のプリミティブ列を取得
            primitives = self.l4.get_intent_primitives(intent)
            if primitives:
                print(f"  [L3] 予測: 意図「{intent}」→ {primitives} (確信度: 0.9)")
                success = self._execute_primitives_with_target(primitives, multiplier)
                print(f"  [L3] 検証: {'success' if success else 'failure'}, 予測誤差: 0.10")
            return
        
        # 意図だけ見つかった（対象なし）
        if intent and not target:
            print(f"  [L4] 意図: 「{intent}」（対象なし）")
            primitives = self.l4.get_intent_primitives(intent)
            if primitives:
                print(f"  [L3] 予測: 意図「{intent}」→ {primitives} (確信度: 0.9)")
                success = self._execute_primitives(primitives, multiplier)
                print(f"  [L3] 検証: {'success' if success else 'failure'}, 予測誤差: 0.10")
            return
        
        # 従来方式（意図も対象もない）
        search_command = remaining if remaining else clean_command
        
        # L3: L4の記憶から予測
        prediction = self.l3.predict_action(search_command, self.l4)
        
        if prediction["primitives"]:
            print(f"  [L3] 予測: 「{search_command}」→ {prediction['primitives']} (確信度: {prediction['confidence']:.1f})")
            
            success = self._execute_primitives(prediction["primitives"], multiplier)
            
            actual_result = "success" if success else "failure"
            error = self.l3.verify_action_result(actual_result, self.l4)
            
            print(f"  [L3] 検証: {actual_result}, 予測誤差: {error:.2f}")
        else:
            print(f"  [L3] 予測不能: 「{search_command}」は知らない言葉")
            print(f"  [L3] 予測誤差: {self.l3.prediction_error:.2f}")
            print(f"  → 【質問】何をすればいいですか？")
            self.waiting_for_teaching = True
            self.pending_word = search_command
    
    def _forget(self, word: str):
        """学習した言葉を忘れる"""
        # DNA知識は消せない
        if word in self.l4.DNA_KNOWLEDGE:
            print(f"  → 「{word}」は生まれつきの知識なので忘れられません")
            return
        
        # 学習した知識を削除
        if word in self.l4.word_to_primitive:
            del self.l4.word_to_primitive[word]
            self.l4.save()
            print(f"  → 「{word}」を忘れました")
        else:
            print(f"  → 「{word}」は知りません")
    
    def _layer5_update(self, prediction_error: float, qualia_list: List[Qualia]):
        has_critical = any(q.is_critical() for q in qualia_list)
        qualia_value = sum(q.value for q in qualia_list) / len(qualia_list) if qualia_list else 0.0
        
        old_state = self.l5.state
        self.l5.update(prediction_error, has_critical, qualia_value)
        
        if not self.waiting_input and old_state != self.l5.state:
            if self.l5.state == ConsciousnessState.IDLE:
                print(f"  [L5] 意識OFF")
            elif self.l5.state == ConsciousnessState.ALERT:
                print(f"  [L5] 意識ON（警戒）誤差: {prediction_error:.2f}")
            elif self.l5.state == ConsciousnessState.FOCUSED:
                print(f"  [L5] 意識ON（集中）誤差: {prediction_error:.2f}")
            elif self.l5.state == ConsciousnessState.CRITICAL:
                print(f"  [L5] ！緊急対応！ 誤差: {prediction_error:.2f}")
    
    # ==========================================
    # 入力
    # ==========================================
    
    def hear(self, text: str):
        """聴覚入力（バッファに積むだけ、処理はループで）"""
        print(f"\n【聞こえた】「{text}」")
        with self._process_lock:
            self.auditory_buffer = text
        # 処理はループ側に任せる（スレッド競合を防ぐ）
    
    def hear_and_process(self, text: str):
        """聴覚入力して即処理（対話モード用）"""
        print(f"\n【聞こえた】「{text}」")
        with self._process_lock:
            self.auditory_buffer = text
            self._layer4_process()
    
    # ==========================================
    # 修飾語（力加減）
    # ==========================================
    
    # 修飾語 → 倍率
    MODIFIERS = {
        # 速度・量を減らす
        "ゆっくり": 0.3,
        "そっと": 0.3,
        "軽く": 0.3,
        "少し": 0.5,
        "ちょっと": 0.5,
        "やや": 0.7,
        
        # 速度・量を増やす
        "速く": 2.0,
        "早く": 2.0,
        "強く": 2.0,
        "大きく": 2.0,
        "思いっきり": 3.0,
        "全力で": 3.0,
        "もっと": 1.5,
        "すごく": 2.0,
        "かなり": 2.0,
    }
    
    def _parse_modifier(self, command: str) -> Tuple[str, float]:
        """
        修飾語を解析して倍率を返す
        
        Returns: (修飾語を除いた命令, 倍率)
        """
        multiplier = 1.0
        clean_command = command
        
        for mod, mult in self.MODIFIERS.items():
            if mod in command:
                multiplier = mult
                clean_command = command.replace(mod, "").strip()
                print(f"  [修飾語] 「{mod}」→ 倍率 {mult}x")
                break
        
        return clean_command, multiplier
    
    # ==========================================
    # プリミティブ実行
    # ==========================================
    
    def _execute_primitives(self, primitives: List[str], multiplier: float = 1.0) -> bool:
        for prim_name in primitives:
            result = self._execute_one(prim_name, multiplier)
            if result != PrimitiveResult.SUCCESS:
                print(f"  [L1] {prim_name} → 失敗")
                return False
            if multiplier != 1.0:
                print(f"  [L1] {prim_name} (x{multiplier}) → 成功")
            else:
                print(f"  [L1] {prim_name} → 成功")
        return True
    
    def _execute_primitives_with_target(self, primitives: List[str], multiplier: float = 1.0) -> bool:
        """対象を追跡しながらプリミティブを実行"""
        for prim_name in primitives:
            # 特殊プリミティブ（対象依存）
            if prim_name == "search_target":
                result = self._search_target()
            elif prim_name == "move_to_target":
                result = self._move_to_target()
            elif prim_name == "look_at_target":
                result = self._look_at_target()
            else:
                result = self._execute_one(prim_name, multiplier)
            
            if result != PrimitiveResult.SUCCESS:
                print(f"  [L1] {prim_name} → 失敗")
                return False
            if multiplier != 1.0:
                print(f"  [L1] {prim_name} (x{multiplier}) → 成功")
            else:
                print(f"  [L1] {prim_name} → 成功")
        return True
    
    def _search_target(self) -> PrimitiveResult:
        """対象を探索（条件付きループ）"""
        if not self.current_target:
            print(f"  [探索] 対象が設定されていません")
            return PrimitiveResult.FAILURE
        
        print(f"  [探索] 「{self.current_target}」を探しています...")
        
        # 最大8方向を探索（シミュレーション）
        for i in range(8):
            # 視覚情報を取得
            visual_data = self._get_visual_data()
            
            # 対象を探す
            if self._check_target_in_view(visual_data):
                print(f"  [探索] 「{self.current_target}」を発見！")
                self.target_found = True
                return PrimitiveResult.SUCCESS
            
            # 見つからなければ回転
            self.l1.turn_left(angle=45.0)
            print(f"  [探索] 左に45度回転... ({i+1}/8)")
        
        print(f"  [探索] 「{self.current_target}」は見つかりませんでした")
        self.target_found = False
        return PrimitiveResult.SUCCESS  # 探索自体は成功（見つからなくても）
    
    def _move_to_target(self) -> PrimitiveResult:
        """対象に接近"""
        if not self.target_found:
            print(f"  [移動] 対象が見つかっていません")
            return PrimitiveResult.FAILURE
        
        print(f"  [移動] 「{self.current_target}」に接近中...")
        
        # シミュレーション: 3歩前進
        for i in range(3):
            self.l1.move_forward(distance=0.1)
        
        print(f"  [移動] 「{self.current_target}」に到達")
        return PrimitiveResult.SUCCESS
    
    def _look_at_target(self) -> PrimitiveResult:
        """対象を見る"""
        if not self.current_target:
            print(f"  [視線] 対象が設定されていません")
            return PrimitiveResult.FAILURE
        
        print(f"  [視線] 「{self.current_target}」を見ています")
        self.l1.look()
        return PrimitiveResult.SUCCESS
    
    def _get_visual_data(self) -> Dict:
        """視覚データを取得"""
        if self.l1.sim:
            return self.l1.sim.get_visual_info()
        
        # シミュレーションなし: ランダムに対象が見つかる（テスト用）
        import random
        if random.random() < 0.3:  # 30%の確率で見つかる
            if self.current_target_features:
                return {"objects": [self.current_target_features]}
        return {"objects": []}
    
    def _check_target_in_view(self, visual_data: Dict) -> bool:
        """視覚データに対象があるか確認"""
        if not self.current_target_features:
            return False
        
        objects = visual_data.get("objects", [])
        for obj in objects:
            # 特徴が一致するか
            match = True
            for key, value in self.current_target_features.items():
                if obj.get(key) != value:
                    match = False
                    break
            if match:
                return True
        return False
    
    def _execute_one(self, prim_name: str, multiplier: float = 1.0) -> PrimitiveResult:
        # 腕のプリミティブ
        if "." in prim_name:
            parts = prim_name.split(".")
            arm_name = parts[0]
            method_name = parts[1]
            
            arm = self.l1.get_arm(arm_name)
            if arm and hasattr(arm, method_name):
                method = getattr(arm, method_name)
                # 倍率を渡せるメソッドは渡す
                try:
                    return method(amount=10.0 * multiplier)
                except TypeError:
                    return method()
            return PrimitiveResult.FAILURE
        
        # 本体のプリミティブ
        if hasattr(self.l1, prim_name):
            method = getattr(self.l1, prim_name)
            if callable(method):
                # 倍率を渡せるメソッドは渡す
                try:
                    # 移動系は distance、回転系は angle
                    if "move" in prim_name:
                        return method(distance=0.1 * multiplier)
                    elif "turn" in prim_name:
                        return method(angle=10.0 * multiplier)
                    elif "waist" in prim_name or "neck" in prim_name:
                        return method(amount=10.0 * multiplier)
                    else:
                        return method()
                except TypeError:
                    return method()
        
        return PrimitiveResult.FAILURE
    
    # ==========================================
    # 学習
    # ==========================================
    
    def _handle_teaching(self, answer: str):
        word = self.pending_word
        
        if any(w in answer for w in ["キャンセル", "やめ", "cancel"]):
            print(f"  → キャンセルしました")
            self.waiting_for_teaching = False
            self.pending_word = None
            return
        
        primitives = [p.strip() for p in answer.split(",")]
        
        print(f"  [テスト] {primitives}")
        success = self._execute_primitives(primitives)
        
        if success:
            self.l4.learn(word, primitives, success=True)
            self.l4.save()
            print(f"  → 学習完了！「{word}」を覚えました")
        else:
            print(f"  → 失敗。もう一度教えてください")
            return
        
        self.waiting_for_teaching = False
        self.pending_word = None
    
    # ==========================================
    # 状態
    # ==========================================
    
    def get_status(self) -> Dict:
        return {
            "L1_position": self.l1.position,
            "L1_direction": self.l1.direction,
            "L2_qualia_count": len(self.l2.current_qualia),
            "L3_prediction_error": self.l3.prediction_error,
            "L4_known_words": len(self.l4.word_to_primitive),
            "L5_state": self.l5.state.value,
            "L5_sync_level": self.l5.sync_level,
            "L5_persistence": f"{self.l5.get_persistence()*100:.1f}%",
        }


# ==========================================
# メイン
# ==========================================

def main():
    hida = HidaCore()
    
    loop_thread = threading.Thread(target=hida.start_loop, daemon=True)
    loop_thread.start()
    
    print("\n" + "-" * 60)
    print("コマンド入力（例: 「飛騨、前に進め」「飛騨、右手を握れ」）")
    print("'q' で終了、'状態' で全層状態表示")
    print("-" * 60)
    
    try:
        while True:
            hida.waiting_input = True
            text = input("\nあなた: ").strip()
            hida.waiting_input = False
            
            if text.lower() == 'q':
                break
            
            if text == '状態':
                status = hida.get_status()
                print("\n【5層状態】")
                for k, v in status.items():
                    print(f"  {k}: {v}")
                continue
            
            if text:
                # 対話モードでは即処理（ループは待たない）
                hida.hear_and_process(text)
    
    except KeyboardInterrupt:
        pass
    
    hida.l4.save()
    hida.stop_loop()
    print("\n終了")


if __name__ == "__main__":
    main()
