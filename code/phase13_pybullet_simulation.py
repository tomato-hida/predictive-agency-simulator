#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Phase 13: PyBullet Simulation
飛騨の行動コードでロボットを動かす

Theory of Human Inner Movement
人の内なる運動理論

これでソフトウェアからハードウェア（シミュレーション）への接続が完成
"""

import pybullet as p
import pybullet_data
import time
import math

class HidaRobotSimulation:
    """
    飛騨のロボットシミュレーション
    行動コードを受け取って動く
    """
    
    def __init__(self):
        # シミュレーション開始
        self.physics_client = p.connect(p.GUI)  # GUI モード
        p.setAdditionalSearchPath(pybullet_data.getDataPath())
        p.setGravity(0, 0, -10)
        
        # 床を作成
        self.plane_id = p.loadURDF("plane.urdf")
        
        # ロボット（車）を作成
        self.robot_id = self._create_simple_robot()
        
        # 対象物（ボール）を作成
        self.ball_id = self._create_ball([2, 0, 0.5])
        
        # 状態
        self.is_holding = False
        self.target_position = None
        
        print("シミュレーション開始")
        print("ロボット（青い箱）と ボール（赤い球）が表示されます")
    
    def _create_simple_robot(self):
        """シンプルなロボット（箱）を作成"""
        # 箱の形状
        collision_shape = p.createCollisionShape(p.GEOM_BOX, halfExtents=[0.3, 0.2, 0.1])
        visual_shape = p.createVisualShape(p.GEOM_BOX, halfExtents=[0.3, 0.2, 0.1], 
                                           rgbaColor=[0.2, 0.4, 0.8, 1])
        
        # ロボット本体
        robot_id = p.createMultiBody(
            baseMass=1,
            baseCollisionShapeIndex=collision_shape,
            baseVisualShapeIndex=visual_shape,
            basePosition=[0, 0, 0.2]
        )
        
        return robot_id
    
    def _create_ball(self, position):
        """ボールを作成"""
        collision_shape = p.createCollisionShape(p.GEOM_SPHERE, radius=0.2)
        visual_shape = p.createVisualShape(p.GEOM_SPHERE, radius=0.2,
                                           rgbaColor=[0.9, 0.2, 0.2, 1])
        
        ball_id = p.createMultiBody(
            baseMass=0.5,
            baseCollisionShapeIndex=collision_shape,
            baseVisualShapeIndex=visual_shape,
            basePosition=position
        )
        
        return ball_id
    
    def get_robot_position(self):
        """ロボットの位置を取得"""
        pos, _ = p.getBasePositionAndOrientation(self.robot_id)
        return pos
    
    def get_ball_position(self):
        """ボールの位置を取得"""
        pos, _ = p.getBasePositionAndOrientation(self.ball_id)
        return pos
    
    def execute_action(self, action: str) -> str:
        """
        行動コードを実行
        Phase 12 からの出力を受け取る
        """
        print(f"\n【行動実行】{action}")
        
        if action == "search":
            return self._action_search()
        elif action == "pick_up":
            return self._action_pick_up()
        elif action == "carry":
            return self._action_carry()
        elif action == "put_down":
            return self._action_put_down()
        elif action == "stop":
            return self._action_stop()
        elif action == "come":
            return self._action_come()
        elif action == "wait":
            return self._action_wait()
        elif action == "follow":
            return self._action_follow()
        else:
            return f"未対応の行動: {action}"
    
    def _move_robot_to(self, target_x, target_y, steps=100):
        """ロボットを目標位置に移動"""
        for i in range(steps):
            current_pos = self.get_robot_position()
            
            # 方向を計算
            dx = target_x - current_pos[0]
            dy = target_y - current_pos[1]
            distance = math.sqrt(dx*dx + dy*dy)
            
            if distance < 0.1:
                break
            
            # 少しずつ移動
            speed = 0.05
            new_x = current_pos[0] + (dx / distance) * speed
            new_y = current_pos[1] + (dy / distance) * speed
            
            p.resetBasePositionAndOrientation(
                self.robot_id, 
                [new_x, new_y, 0.2],
                [0, 0, 0, 1]
            )
            
            # ボールを持ってる場合は一緒に動かす
            if self.is_holding:
                p.resetBasePositionAndOrientation(
                    self.ball_id,
                    [new_x, new_y, 0.5],
                    [0, 0, 0, 1]
                )
            
            p.stepSimulation()
            time.sleep(0.02)
    
    def _action_search(self):
        """探す：周囲を見回す"""
        print("周囲を探索中...")
        
        ball_pos = self.get_ball_position()
        robot_pos = self.get_robot_position()
        
        # ボールの方向に少し移動
        self._move_robot_to(ball_pos[0] * 0.3, ball_pos[1] * 0.3, steps=50)
        
        distance = math.sqrt(
            (ball_pos[0] - robot_pos[0])**2 + 
            (ball_pos[1] - robot_pos[1])**2
        )
        
        return f"ボールを発見！距離: {distance:.1f}m"
    
    def _action_pick_up(self):
        """拾う：ボールに近づいて拾う"""
        print("ボールを拾いに行きます...")
        
        ball_pos = self.get_ball_position()
        
        # ボールに近づく
        self._move_robot_to(ball_pos[0], ball_pos[1], steps=100)
        
        # 拾う
        self.is_holding = True
        p.resetBasePositionAndOrientation(
            self.ball_id,
            [ball_pos[0], ball_pos[1], 0.5],
            [0, 0, 0, 1]
        )
        
        return "ボールを拾いました"
    
    def _action_carry(self):
        """運ぶ：持っている物を運ぶ"""
        if not self.is_holding:
            return "何も持っていません"
        
        print("運搬中...")
        
        # 原点に向かって運ぶ
        self._move_robot_to(0, 0, steps=100)
        
        return "運搬完了"
    
    def _action_put_down(self):
        """置く：持っている物を置く"""
        if not self.is_holding:
            return "何も持っていません"
        
        print("ボールを置きます...")
        
        robot_pos = self.get_robot_position()
        
        # ボールを少し前に置く
        p.resetBasePositionAndOrientation(
            self.ball_id,
            [robot_pos[0] + 0.5, robot_pos[1], 0.2],
            [0, 0, 0, 1]
        )
        
        self.is_holding = False
        
        return "ボールを置きました"
    
    def _action_stop(self):
        """停止：その場で止まる"""
        print("停止")
        time.sleep(0.5)
        return "停止しました"
    
    def _action_come(self):
        """来る：原点に戻る"""
        print("原点に向かいます...")
        self._move_robot_to(0, 0, steps=100)
        return "到着しました"
    
    def _action_wait(self):
        """待機：その場で待つ"""
        print("待機中...")
        for _ in range(50):
            p.stepSimulation()
            time.sleep(0.02)
        return "待機しています"
    
    def _action_follow(self):
        """追従：ボールを追いかける"""
        print("追従中...")
        
        for _ in range(3):
            ball_pos = self.get_ball_position()
            self._move_robot_to(ball_pos[0], ball_pos[1], steps=30)
        
        return "追従完了"
    
    def run_interactive(self):
        """対話モード"""
        print("\n" + "=" * 50)
        print("飛騨ロボット シミュレーション")
        print("=" * 50)
        print("\n行動コマンド:")
        print("  search  - 探す")
        print("  pick_up - 拾う")
        print("  carry   - 運ぶ")
        print("  put_down - 置く")
        print("  stop    - 停止")
        print("  come    - 来る")
        print("  wait    - 待機")
        print("  follow  - 追従")
        print("  q       - 終了")
        print()
        
        while True:
            try:
                action = input("行動コード: ").strip().lower()
                
                if action == 'q':
                    break
                
                if action:
                    result = self.execute_action(action)
                    print(f"結果: {result}")
                
            except KeyboardInterrupt:
                break
        
        self.close()
    
    def close(self):
        """シミュレーション終了"""
        p.disconnect()
        print("シミュレーション終了")


def demo():
    """デモ実行"""
    print("=" * 50)
    print("Phase 13: PyBullet シミュレーション デモ")
    print("=" * 50)
    
    sim = HidaRobotSimulation()
    
    print("\n【デモ開始】")
    print("5秒後に自動で行動します...")
    time.sleep(5)
    
    # デモシーケンス
    actions = [
        ("search", "ボールを探す"),
        ("pick_up", "ボールを拾う"),
        ("carry", "ボールを運ぶ"),
        ("put_down", "ボールを置く"),
        ("come", "原点に戻る"),
    ]
    
    for action, description in actions:
        print(f"\n--- {description} ---")
        result = sim.execute_action(action)
        print(f"結果: {result}")
        time.sleep(1)
    
    print("\n【デモ終了】")
    print("10秒後にウィンドウを閉じます...")
    time.sleep(10)
    
    sim.close()


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "demo":
        demo()
    else:
        sim = HidaRobotSimulation()
        sim.run_interactive()
