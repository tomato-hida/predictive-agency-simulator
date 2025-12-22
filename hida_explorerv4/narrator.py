# narrator.py - 左脳（作話係）
# 行動を言語化するだけ。行動には影響しない。

import random

# ollamaを使う場合
USE_OLLAMA = False

def narrate(event, context=None):
    """行動を言語化する（作話）"""
    if USE_OLLAMA:
        return narrate_ollama(event, context)
    else:
        return narrate_simple(event, context)


def narrate_simple(event, context=None):
    """シンプルな作話（ランダム選択）"""
    
    narrations = {
        "start": [
            "さて、何があるか見てみよう",
            "探索開始だ",
            "どんな世界が広がってるかな",
        ],
        "turn_left": [
            "なんとなく左が気になる",
            "左に何かある気がする",
            "こっちに行ってみよう",
        ],
        "turn_right": [
            "右の方が良さそうだ",
            "右に行ってみるか",
            "なんとなく右かな",
        ],
        "forward": [
            "まっすぐ進もう",
            "この道で合ってるはず",
            "前に進むぞ",
        ],
        "blocked": [
            "あ、行き止まりだ",
            "壁か、別の道を探そう",
            "ここは通れないな",
        ],
        "found_ball": [
            "おっ、ボールだ！",
            "見つけた！赤いやつ！",
            "これだ、探してたやつ！",
        ],
        "found_goal": [
            "ゴールがあった！",
            "あそこがゴールか",
            "目的地を発見！",
        ],
        "grab": [
            "よし、ゲット！",
            "つかんだぞ",
            "これで持った",
        ],
        "move_to_goal": [
            "ゴールに向かおう",
            "確かあっちだったはず...",
            "記憶を頼りに進むぞ",
        ],
        "release": [
            "ここに置こう",
            "よし、届けた！",
            "ミッション完了だ",
        ],
        "lost": [
            "あれ、どこだっけ...",
            "ちょっと迷ったかも",
            "まあ、探せば見つかるさ",
        ],
        "explore_done": [
            "だいたい把握した",
            "もう行ける場所はないかな",
            "探索完了！",
        ],
        "prediction_error_missing": [
            "えっ、ないぞ？",
            "あれ？あったはずなのに...",
            "おかしい、ここにあったはず",
            "消えた...？",
        ],
        "prediction_error_appeared": [
            "おっ！何かある！",
            "あれ？こんなのあったっけ",
            "前はなかったのに...",
            "いつの間に？",
        ],
        "prediction_error_changed": [
            "えっ、変わってる！",
            "あれ？違う...",
            "記憶と違う！",
        ],
    }
    
    if event in narrations:
        return random.choice(narrations[event])
    else:
        return f"({event})"


def narrate_ollama(event, context=None):
    """ollamaで作話"""
    try:
        import subprocess
        import json
        
        prompt = f"""あなたはロボットです。短く一言で、今の行動を説明してください。
感情を込めて、自然な日本語で。10文字以内で。

状況: {event}
コンテキスト: {context if context else 'なし'}

説明:"""
        
        result = subprocess.run(
            ["ollama", "run", "gemma3:4b", prompt],
            capture_output=True,
            text=True,
            timeout=15,
            encoding='utf-8'
        )
        
        response = result.stdout.strip()
        # 最初の1行だけ
        return response.split('\n')[0][:50]
    
    except Exception as e:
        # 失敗したらシンプル版にフォールバック
        return narrate_simple(event, context)
