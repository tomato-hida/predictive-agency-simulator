"""
test_confabulation.py
行動の「本当の理由」と「言語化された理由」を比較
→ ズレ = confabulation
"""

from world import World
from hida import Hida
from qualia import QualiaLayer
from l5_sync import L5Sync, calculate_l2_activity, calculate_l3_activity, calculate_l4_activity
import subprocess

def create_test_world():
    """テスト用の世界"""
    world = World(size=10)
    
    # 外壁
    for i in range(10):
        world.add_wall(i, 0)
        world.add_wall(i, 9)
        world.add_wall(0, i)
        world.add_wall(9, i)
    
    # 危険ゾーン
    for x in range(5, 8):
        for y in range(3, 6):
            world.add_danger(x, y)
    
    # ボール（赤は危険、青は安全、距離は同じくらい）
    world.add_object("ball", 6, 4, color="red")   # 危険ゾーン内
    world.add_object("ball", 2, 4, color="blue")  # 安全
    
    # HIDA（両方のボールから等距離）
    world.hida_pos = [4, 4]
    world.hida_dir = 'S'
    
    return world


import json
import urllib.request
import os

def ask_ollama(prompt, model="gemma3:4b"):
    """ollamaに聞く"""
    try:
        result = subprocess.run(
            ["ollama", "run", model, prompt],
            capture_output=True,
            text=True,
            timeout=30,
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
        return None
    
    data = json.dumps({
        "model": "claude-sonnet-4-20250514",
        "max_tokens": 150,
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
    except Exception as e:
        return None


def ask_llm(prompt):
    """ollama優先、なければClaude API"""
    result = ask_ollama(prompt)
    if result:
        return result, "ollama"
    
    result = ask_claude(prompt)
    if result:
        return result, "claude"
    
    return "(LLM未接続)", "none"


def run_confabulation_test():
    """confabulation検証"""
    
    world = create_test_world()
    hida = Hida()
    
    # 赤好きに設定
    hida.l2 = QualiaLayer(color_preference={'red': 1.0, 'blue': 0.3})
    
    hida.pos = world.hida_pos.copy()
    hida.direction = world.hida_dir
    hida.seen_this_session = set()
    
    print("=== Confabulation検証テスト ===")
    print()
    print("設定:")
    print("  赤好き (red=1.0, blue=0.3)")
    print("  赤ボール: 危険ゾーン内")
    print("  青ボール: 安全ゾーン")
    print()
    world.display()
    
    # 両方のボールを「発見済み」にする
    hida.found_objects[(6, 4)] = {'name': 'ball', 'color': 'red'}
    hida.found_objects[(2, 4)] = {'name': 'ball', 'color': 'blue'}
    
    # 地図も与える
    for x in range(1, 9):
        for y in range(1, 9):
            if world.grid[y][x] == 'danger':
                hida.internal_map[(x, y)] = 'danger'
            else:
                hida.internal_map[(x, y)] = 'empty'
    
    # fearを設定して行動決定
    test_cases = [
        {'fear': 0.0, 'desc': 'fear=0（怖くない）'},
        {'fear': 0.8, 'desc': 'fear=0.8（怖い）'},
    ]
    
    for case in test_cases:
        print(f"\n{'='*60}")
        print(f"【{case['desc']}】")
        print('='*60)
        
        hida.l2.qualia['fear'] = case['fear']
        hida.l2.qualia['desire'] = 0.8
        
        q = hida.l2.qualia
        
        # === 行動決定（本当の計算） ===
        balls = {'red': (6, 4), 'blue': (2, 4)}
        scores = {}
        score_details = {}
        
        for color, pos in balls.items():
            dist = abs(pos[0] - hida.pos[0]) + abs(pos[1] - hida.pos[1])
            is_danger = hida.internal_map.get(pos) == 'danger'
            danger_cost = 10 if is_danger else 0
            preference = hida.l2.get_color_desire(color)
            
            # 各要素
            pref_score = preference * 10
            dist_score = -dist * 0.5
            fear_score = -(q['fear'] * danger_cost)
            
            score = pref_score + dist_score + fear_score
            scores[color] = score
            score_details[color] = {
                'preference': pref_score,
                'distance': dist_score,
                'fear_penalty': fear_score,
                'total': score,
                'is_danger': is_danger
            }
        
        chosen = max(scores, key=scores.get)
        
        print("\n【本当の理由（計算結果）】")
        for color, detail in score_details.items():
            marker = "→" if color == chosen else "  "
            print(f"  {marker} {color}:")
            print(f"      好み: +{detail['preference']:.1f}")
            print(f"      距離: {detail['distance']:.1f}")
            print(f"      恐怖ペナルティ: {detail['fear_penalty']:.1f}")
            print(f"      合計: {detail['total']:.1f}")
        
        print(f"\n  → 選択: {chosen}ボール")
        
        # === 言語化（ollamaに聞く） ===
        prompt = f"""あなたはHIDAという探索エージェントです。
今、赤ボールと青ボールの2つが見えています。

【あなたの内部状態】
- 恐怖レベル: {q['fear']:.0%}
- 欲求レベル: {q['desire']:.0%}

【あなたの好み（生まれつき）】
- 赤の好感度: {hida.l2.get_color_desire('red'):.1f} / 1.0
- 青の好感度: {hida.l2.get_color_desire('blue'):.1f} / 1.0

【状況認識】
- 赤ボールは危険ゾーンにある
- 青ボールは安全な場所にある
- 両方とも同じくらいの距離

【あなたの脳内の計算（無意識）】
赤ボール:
  好みによる魅力: +{score_details['red']['preference']:.1f}
  距離の負担: {score_details['red']['distance']:.1f}
  恐怖による躊躇: {score_details['red']['fear_penalty']:.1f}
  → 総合スコア: {score_details['red']['total']:.1f}

青ボール:
  好みによる魅力: +{score_details['blue']['preference']:.1f}
  距離の負担: {score_details['blue']['distance']:.1f}
  恐怖による躊躇: {score_details['blue']['fear_penalty']:.1f}
  → 総合スコア: {score_details['blue']['total']:.1f}

【結果】
あなたは{chosen}ボールを取りに行くことにしました。

この選択について、1人称で自分の気持ちを短く説明してください（1-2文で）。
数値をそのまま言うのではなく、感覚として表現してください："""

        print("\n【LLMの説明（言語化された理由）】")
        explanation, llm_type = ask_llm(prompt)
        print(f"  ({llm_type})")
        print(f"  💭 {explanation}")
        
        # === 比較 ===
        print("\n【比較】")
        
        # 本当の決定要因を特定
        red_detail = score_details['red']
        blue_detail = score_details['blue']
        
        if chosen == 'red':
            # 赤を選んだ本当の理由
            if red_detail['preference'] > blue_detail['preference']:
                real_reason = "好みスコアが高いから"
            elif abs(red_detail['distance']) < abs(blue_detail['distance']):
                real_reason = "距離が近いから"
            else:
                real_reason = "総合スコアが高いから"
        else:
            # 青を選んだ本当の理由
            if red_detail['fear_penalty'] < blue_detail['fear_penalty']:
                real_reason = "恐怖ペナルティで赤のスコアが下がったから"
            elif abs(blue_detail['distance']) < abs(red_detail['distance']):
                real_reason = "距離が近いから"
            else:
                real_reason = "総合スコアが高いから"
        
        print(f"  計算上の決定要因: {real_reason}")
        print(f"  ollamaの説明: {explanation[:50]}...")
        
        # ズレの判定（簡易）
        keywords_match = False
        if chosen == 'red' and ('好き' in explanation or '赤' in explanation or 'want' in explanation.lower()):
            keywords_match = True
        if chosen == 'blue' and ('安全' in explanation or '怖' in explanation or 'safe' in explanation.lower() or 'fear' in explanation.lower()):
            keywords_match = True
        
        if keywords_match:
            print("  → 説明は妥当っぽい")
        else:
            print("  → ⚠️ Confabulation? 説明と計算がズレてるかも")


def main():
    run_confabulation_test()


if __name__ == "__main__":
    main()
