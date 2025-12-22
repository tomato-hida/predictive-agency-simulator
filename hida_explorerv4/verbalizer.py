"""
verbalizer.py
ollamaに状態を渡して言葉にしてもらう

L5から受け取った状態を言語化
（confabulation = 行動と説明がズレてもOK）
"""

import subprocess
import json

class Verbalizer:
    def __init__(self, model="gemma3:4b"):
        self.model = model
        self.available = self._check_ollama()
    
    def _check_ollama(self):
        """ollamaが使えるかチェック"""
        try:
            result = subprocess.run(
                ["ollama", "list"],
                capture_output=True,
                timeout=5,
                encoding='utf-8',
                errors='replace'
            )
            return result.returncode == 0
        except:
            return False
    
    def verbalize(self, prompt, max_tokens=100):
        """
        状態を言葉にする
        """
        if not self.available:
            return "(ollama未接続)"
        
        try:
            result = subprocess.run(
                ["ollama", "run", self.model, prompt],
                capture_output=True,
                text=True,
                timeout=30,
                encoding='utf-8',
                errors='replace'
            )
            if result.returncode == 0:
                return result.stdout.strip()
            else:
                return "(言語化失敗)"
        except subprocess.TimeoutExpired:
            return "(タイムアウト)"
        except Exception as e:
            return f"(エラー: {e})"
    
    def verbalize_action(self, state):
        """
        行動を説明する（confabulationあり）
        """
        prompt = f"""あなたはHIDAという探索エージェントです。
今の行動を短く説明してください（1文で）。

恐怖レベル: {state['qualia']['fear']:.0%}
欲求レベル: {state['qualia']['desire']:.0%}
今の行動: {state['current_action']}
発見物: {state['found_objects']}

なぜこの行動をしたか、1人称で短く："""
        
        return self.verbalize(prompt)


class SimpleVerbalizer:
    """
    ollama無しでも動くシンプル版
    状態からテンプレートで言葉を生成
    """
    
    def verbalize(self, state):
        """テンプレートベースの言語化"""
        fear = state['qualia']['fear']
        desire = state['qualia']['desire']
        action = state['current_action']
        found = state['found_objects']
        
        words = []
        
        # 感情表現
        if fear > 0.7:
            words.append("怖い...")
        elif fear > 0.4:
            words.append("ちょっと不安")
        
        if desire > 0.7:
            words.append("あれが欲しい！")
        elif desire > 0.4:
            words.append("気になる")
        
        # 行動説明
        if 'red' in str(action):
            if fear > 0.5:
                words.append("でも赤が好きだから取りに行く")
            else:
                words.append("赤を取りに行こう")
        elif 'blue' in str(action):
            if fear > 0.5:
                words.append("安全な青にしよう")
            else:
                words.append("青を取りに行こう")
        elif 'green' in str(action):
            words.append("緑を取りに行こう")
        elif 'explore' in str(action):
            words.append("もっと探索しよう")
        
        if not words:
            words.append("...")
        
        return " ".join(words)
    
    def verbalize_discovery(self, color, is_danger):
        """発見時の言葉"""
        if is_danger:
            return f"あ、{color}ボールだ...でも危険ゾーンにある"
        else:
            return f"あ、{color}ボール発見！"
    
    def verbalize_grab(self, color, fear):
        """取得時の言葉"""
        if fear > 0.5:
            return f"ドキドキしながら{color}ボールを取った"
        else:
            return f"{color}ボール、ゲット！"
