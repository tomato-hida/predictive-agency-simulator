"""
test_planning.py
LLMに計画を立てさせるテスト（確認ループ付き）
"""

import requests
import json

def ask_ollama(prompt, model="gemma3:4b"):
    """ollamaに質問"""
    try:
        response = requests.post(
            'http://localhost:11434/api/generate',
            json={
                'model': model,
                'prompt': prompt,
                'stream': False
            },
            timeout=120
        )
        result = response.json()
        return result.get('response', 'エラー')
    except Exception as e:
        return f"エラー: {e}"


def test_planning():
    map_str = '''
[ ][ ][r][ ][ ][ ]   y=0
[ ][ ][ ][#][ ][ ]   y=1  
[ ][ ][ ][ ][ ][ ]   y=2
[ ][ ][ ][^][ ][#]   y=3  
[ ][ ][ ][ ][ ][#]   y=4  
[ ][ ][ ][ ][ ][g]   y=5  
  0  1  2  3  4  5
'''

    # 壁の座標（プログラムで抽出した想定）
    walls = "[3,1], [5,3], [5,4]"

    # ===== Step 1: 計画を立てる =====
    prompt1 = f'''あなたはロボットの計画担当です。

マップ:
{map_str}

記号:
^ = あなた（今 [3,3] にいる、北向き）
r = red ball [2,0]
g = goal [5,5]
# = 壁（通れない）

目標: red ballを拾ってgoalに届ける

壁を避けて、どの順番で移動すべきですか？
座標のリストで答えてください。

例: [3,3] → [2,3] → [2,2] → ...

まずred ballまでの経路、次にgoalまでの経路を示してください。
'''

    print("=" * 50)
    print("Step 1: 計画を立てる")
    print("=" * 50)
    
    plan = ask_ollama(prompt1)
    print(plan)
    
    # ===== Step 2: 確認する =====
    prompt2 = f'''以下の経路を確認してください。

経路:
{plan}

壁の座標: {walls}

質問: この経路に壁の座標が含まれていますか？
「はい」か「いいえ」で答えて、含まれている場合はどの座標か指摘してください。
'''

    print()
    print("=" * 50)
    print("Step 2: 確認する")
    print("=" * 50)
    
    check = ask_ollama(prompt2)
    print(check)
    
    # ===== Step 3: 修正が必要なら修正 =====
    if "はい" in check or "含まれ" in check or "[3,1]" in check:
        prompt3 = f'''前回の経路に壁が含まれていました。

マップ:
{map_str}

壁の座標（絶対に通れない）: {walls}

現在地: [3,3]
目標1: [2,0]（red ball）
目標2: [5,5]（goal）

壁を避けた正しい経路を示してください。
{walls} を絶対に通らないでください。
'''
        
        print()
        print("=" * 50)
        print("Step 3: 修正する")
        print("=" * 50)
        
        fixed_plan = ask_ollama(prompt3)
        print(fixed_plan)


if __name__ == "__main__":
    test_planning()
