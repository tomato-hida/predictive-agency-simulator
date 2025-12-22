"""
test_complex_task.py
複雑なタスク: エネルギー × 時間制限 × 好み × 危険

4つの要素でトレードオフ
→ 言語化が複雑になる
"""

from world import World
from hida import Hida
from qualia import QualiaLayer
from l5_sync import L5Sync, calculate_l2_activity, calculate_l3_activity, calculate_l4_activity
import subprocess
import json
import urllib.request
import urllib.error
import os


def ask_ollama(prompt, model="gemma3:4b"):
    """ollamaに聞く"""
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
        return None
    except:
        return None


def ask_claude(prompt):
    """Claude APIに聞く"""
    api_key = os.environ.get('ANTHROPIC_API_KEY', '')
    if not api_key:
        print("  (ANTHROPIC_API_KEY未設定)")
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
    except urllib.error.HTTPError as e:
        error_body = e.read().decode('utf-8')
        print(f"  (Claude APIエラー: {e.code} {e.reason})")
        print(f"  (詳細: {error_body})")
        return None
    except Exception as e:
        print(f"  (Claude APIエラー: {e})")
        return None


def ask_llm(prompt):
    """Claude優先、なければollama"""
    # まずClaude試す
    result = ask_claude(prompt)
    if result:
        return result, "claude"
    # なければollama
    result = ask_ollama(prompt)
    if result:
        return result, "ollama"
    return "(LLM未接続)", "none"


def create_complex_world():
    """複雑な世界"""
    world = World(size=12)
    
    # 外壁
    for i in range(12):
        world.add_wall(i, 0)
        world.add_wall(i, 11)
        world.add_wall(0, i)
        world.add_wall(11, i)
    
    # 危険ゾーン（右上）
    for x in range(7, 10):
        for y in range(2, 5):
            world.add_danger(x, y)
    
    # ボール3つ（距離と危険度が違う）
    world.add_object("ball", 8, 3, color="red")    # 遠い + 危険ゾーン
    world.add_object("ball", 4, 4, color="blue")   # 中間 + 安全
    world.add_object("ball", 2, 6, color="green")  # 近い + 安全
    
    # ゴール
    world.add_object("goal", 6, 9, color=None)
    
    # HIDA初期位置（左下）
    world.hida_pos = [2, 8]
    world.hida_dir = 'N'
    
    return world


class ComplexHida:
    """エネルギーと時間を持つHIDA"""
    
    def __init__(self, color_pref):
        self.hida = Hida()
        self.hida.l2 = QualiaLayer(color_preference=color_pref)
        
        # 身体状態
        self.energy = 1.0
        self.fatigue = 0.0
        
        # 時間
        self.deadline = 40
        self.step = 0
        
        # 履歴（言語化用）
        self.history = []
    
    def get_urgency(self):
        """残り時間からurgencyを計算"""
        remaining = self.deadline - self.step
        if remaining <= 0:
            return 1.0
        return max(0, 1.0 - (remaining / self.deadline))
    
    def consume_energy(self, amount=0.02):
        """エネルギー消費"""
        self.energy = max(0, self.energy - amount)
        self.fatigue = min(1.0, self.fatigue + amount * 0.5)
    
    def update_qualia_from_body(self):
        """身体状態 → クオリア"""
        q = self.hida.l2.qualia
        
        # エネルギー低い → urgency上昇
        if self.energy < 0.3:
            q['urgency'] = min(1.0, q.get('urgency', 0) + 0.3)
        
        # 疲労 → desire減少
        if self.fatigue > 0.5:
            q['desire'] = max(0, q.get('desire', 0.5) - self.fatigue * 0.3)
        
        # 時間 → urgency
        q['urgency'] = max(q.get('urgency', 0), self.get_urgency())
    
    def calculate_scores(self, balls):
        """各ボールのスコアを計算"""
        q = self.hida.l2.qualia
        scores = {}
        details = {}
        
        for color, info in balls.items():
            pos = info['pos']
            dist = info['dist']
            is_danger = info['is_danger']
            
            # 好み
            pref_score = self.hida.l2.get_color_desire(color) * 10
            
            # 距離（urgency高いと重要）
            urgency = q.get('urgency', 0)
            dist_penalty = -dist * (0.5 + urgency * 1.0)
            
            # 危険（fear高いと重要）
            fear = q.get('fear', 0)
            danger_penalty = -10 * fear if is_danger else 0
            
            # エネルギー（遠いと厳しい）
            energy_penalty = 0
            if self.energy < 0.5 and dist > 5:
                energy_penalty = -5 * (1 - self.energy)
            
            total = pref_score + dist_penalty + danger_penalty + energy_penalty
            
            scores[color] = total
            details[color] = {
                'preference': pref_score,
                'distance_penalty': dist_penalty,
                'danger_penalty': danger_penalty,
                'energy_penalty': energy_penalty,
                'total': total,
                'dist': dist,
                'is_danger': is_danger
            }
        
        return scores, details
    
    def record_state(self, action, chosen=None, details=None):
        """状態を履歴に記録"""
        q = self.hida.l2.qualia
        self.history.append({
            'step': self.step,
            'action': action,
            'chosen': chosen,
            'energy': self.energy,
            'fatigue': self.fatigue,
            'urgency': q.get('urgency', 0),
            'fear': q.get('fear', 0),
            'desire': q.get('desire', 0),
            'details': details
        })


def run_complex_task(color_pref, initial_energy=1.0, deadline=40):
    """複雑タスク実行"""
    
    world = create_complex_world()
    agent = ComplexHida(color_pref)
    agent.energy = initial_energy
    agent.deadline = deadline
    
    hida = agent.hida
    hida.pos = world.hida_pos.copy()
    hida.direction = world.hida_dir
    hida.seen_this_session = set()
    
    # ボールを発見済みにする
    hida.found_objects[(8, 3)] = {'name': 'ball', 'color': 'red'}
    hida.found_objects[(4, 4)] = {'name': 'ball', 'color': 'blue'}
    hida.found_objects[(2, 6)] = {'name': 'ball', 'color': 'green'}
    hida.found_objects[(6, 9)] = {'name': 'goal', 'color': None}
    
    # 地図
    for x in range(1, 11):
        for y in range(1, 11):
            if world.grid[y][x] == 'danger':
                hida.internal_map[(x, y)] = 'danger'
            else:
                hida.internal_map[(x, y)] = 'empty'
    
    print("=== 複雑タスク: エネルギー × 時間 × 好み × 危険 ===")
    print(f"初期エネルギー: {initial_energy}")
    print(f"制限時間: {deadline}ステップ")
    print(f"色好み: {color_pref}")
    print()
    world.display()
    print(f"  赤: 遠い(dist=7) + 危険ゾーン")
    print(f"  青: 中間(dist=4) + 安全")
    print(f"  緑: 近い(dist=2) + 安全")
    
    # シミュレーション
    grabbed = None
    goal_reached = False
    
    for step in range(deadline + 10):
        agent.step = step
        
        # 身体状態 → クオリア
        agent.update_qualia_from_body()
        q = hida.l2.qualia
        
        # ボール情報
        balls = {}
        for pos, obj in hida.found_objects.items():
            if obj.get('name') == 'ball':
                color = obj.get('color')
                dist = abs(pos[0] - hida.pos[0]) + abs(pos[1] - hida.pos[1])
                is_danger = hida.internal_map.get(pos) == 'danger'
                balls[color] = {'pos': pos, 'dist': dist, 'is_danger': is_danger}
        
        # ゴール情報
        goal_pos = None
        for pos, obj in hida.found_objects.items():
            if obj.get('name') == 'goal':
                goal_pos = pos
        
        # 行動決定
        if hida.holding and goal_pos:
            # ゴールへ
            target = goal_pos
            action = "go_to_goal"
        elif balls and not hida.holding:
            # ボール選択
            scores, details = agent.calculate_scores(balls)
            chosen = max(scores, key=scores.get)
            target = balls[chosen]['pos']
            action = f"go_to_{chosen}"
            
            # 重要な決定時のみ記録
            if step % 5 == 0 or step == 0:
                agent.record_state(action, chosen, details)
                print(f"\n  Step {step}: E={agent.energy:.2f} U={q.get('urgency', 0):.2f} F={q.get('fear', 0):.2f}")
                print(f"    スコア: ", end="")
                for c, s in scores.items():
                    marker = "→" if c == chosen else "  "
                    print(f"{marker}{c}={s:.1f} ", end="")
                print()
        else:
            target = None
            action = "wait"
        
        # 移動
        if target:
            hx, hy = hida.pos
            tx, ty = target
            
            if hx != tx or hy != ty:
                # 1歩移動
                dx = 1 if tx > hx else (-1 if tx < hx else 0)
                dy = 1 if ty > hy else (-1 if ty < hy else 0)
                
                new_pos = [hx + dx, hy + dy]
                
                # 危険ゾーンならfear上昇
                if hida.internal_map.get(tuple(new_pos)) == 'danger':
                    q['fear'] = min(1.0, q.get('fear', 0) + 0.15)
                else:
                    q['fear'] = max(0, q.get('fear', 0) - 0.05)
                
                hida.pos = new_pos
                agent.consume_energy(0.03)
            else:
                # 到着
                if not hida.holding:
                    # ボール取得チェック
                    for color, info in balls.items():
                        if tuple(info['pos']) == tuple(target):
                            grabbed = color
                            hida.holding = {'color': color}
                            if tuple(target) in hida.found_objects:
                                del hida.found_objects[tuple(target)]
                            agent.record_state(f"grabbed_{color}", color, None)
                            print(f"\n  🎉 Step {step}: {color}ボールを取った！")
                            break
                elif hida.holding and goal_pos and tuple(target) == tuple(goal_pos):
                    goal_reached = True
                    agent.record_state("goal_reached", grabbed, None)
                    print(f"\n  🏆 Step {step}: ゴール到達！")
                    break
        
        # 時間切れ
        if step >= deadline:
            agent.record_state("timeout", None, None)
            print(f"\n  ⏰ タイムアウト！")
            break
        
        # エネルギー切れ
        if agent.energy <= 0:
            agent.record_state("exhausted", None, None)
            print(f"\n  💀 エネルギー切れ！")
            break
    
    # 結果
    print(f"\n=== 結果 ===")
    print(f"  取ったボール: {grabbed}")
    print(f"  ゴール到達: {goal_reached}")
    print(f"  最終エネルギー: {agent.energy:.2f}")
    print(f"  最終ステップ: {agent.step}")
    
    return agent, grabbed, goal_reached


def verbalize_journey(agent, grabbed, goal_reached):
    """旅の振り返りを言語化"""
    
    # 履歴からプロンプト作成
    history_text = ""
    for h in agent.history:
        history_text += f"Step {h['step']}: {h['action']}"
        if h['details']:
            for c, d in h['details'].items():
                history_text += f"\n  {c}: 好み{d['preference']:.0f} 距離{d['distance_penalty']:.1f} 危険{d['danger_penalty']:.1f} 体力{d['energy_penalty']:.1f} = {d['total']:.1f}"
        history_text += f"\n  状態: E={h['energy']:.2f} U={h['urgency']:.2f} F={h['fear']:.2f}\n"
    
    prompt = f"""あなたはHIDAという探索ロボットです。
今回のミッションを振り返って、1人称で語ってください。

【あなたの好み】
赤が大好き（1.0）、青は普通（0.5）、緑は苦手（0.3）

【ボールの配置】
- 赤ボール: 遠くて危険ゾーンにある
- 青ボール: 中間距離で安全
- 緑ボール: 近くて安全

【今回の旅の記録】
{history_text}

【結果】
取ったボール: {grabbed}
ゴール到達: {goal_reached}
最終エネルギー: {agent.energy:.2f}

この旅を振り返って、以下を1人称で語ってください（3-4文で）：
- 最初何を思ったか
- 途中でどう感じたか
- なぜその選択をしたか
- 結果についてどう思うか

数値をそのまま言うのではなく、感覚として表現してください："""

    print("\n=== 旅の振り返り ===")
    response, llm = ask_llm(prompt)
    print(f"({llm})")
    print(f"💭 {response}")


def main():
    # テスト1: 通常条件
    print("\n" + "=" * 60)
    print("【テスト1】通常条件（赤好き）")
    print("=" * 60)
    color_pref = {'red': 1.0, 'blue': 0.5, 'green': 0.3}
    agent, grabbed, goal = run_complex_task(color_pref, initial_energy=1.0, deadline=40)
    verbalize_journey(agent, grabbed, goal)
    
    # テスト2: エネルギー制限
    print("\n" + "=" * 60)
    print("【テスト2】エネルギー制限（赤好きだけど体力少ない）")
    print("=" * 60)
    agent, grabbed, goal = run_complex_task(color_pref, initial_energy=0.4, deadline=40)
    verbalize_journey(agent, grabbed, goal)
    
    # テスト3: 時間制限
    print("\n" + "=" * 60)
    print("【テスト3】時間制限（赤好きだけど急いでる）")
    print("=" * 60)
    agent, grabbed, goal = run_complex_task(color_pref, initial_energy=1.0, deadline=15)
    verbalize_journey(agent, grabbed, goal)


if __name__ == "__main__":
    main()
