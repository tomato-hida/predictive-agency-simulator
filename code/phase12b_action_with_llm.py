#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Phase 12b: Language to Action with LLM Teacher
LLM を先生にして言語から行動を学ぶ

Theory of Human Inner Movement
人の内なる運動理論

改良点：
- 知らないコマンド → LLM に意味を聞く
- LLM が行動を推測 → 飛騨が覚える
- 人間は確認だけ（または完全自動）

流れ：
1. 人間：「あれ持ってきて」
2. 飛騨：知らない → LLM に聞く
3. LLM：「fetch（取ってくる）が近い」
4. 飛騨：覚える
5. 次から自分で理解
"""

import requests
import json
import os
from typing import Dict, Optional, Tuple, List
from datetime import datetime

# Ollama API settings
OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "gemma3:4b"

# Memory file path
ACTION_MEMORY_FILE = "hida_action_memory_v2.json"


def ask_ollama(prompt: str) -> str:
    """Ollama に質問"""
    try:
        response = requests.post(
            OLLAMA_URL,
            json={"model": MODEL_NAME, "prompt": prompt, "stream": False},
            timeout=30
        )
        return response.json().get('response', '').strip()
    except Exception as e:
        return f"エラー：{str(e)}"


class ActionMemoryV2:
    """
    言語 → 行動 の記憶 V2
    """
    
    def __init__(self, filepath: str = ACTION_MEMORY_FILE):
        self.filepath = filepath
        self.memory = self._load_or_create()
    
    def _load_or_create(self) -> Dict:
        if os.path.exists(self.filepath):
            with open(self.filepath, 'r', encoding='utf-8') as f:
                print(f"行動記憶を読み込みました: {self.filepath}")
                return json.load(f)
        else:
            print(f"新しい行動記憶を作成します: {self.filepath}")
            return self._create_initial_memory()
    
    def _create_initial_memory(self) -> Dict:
        """初期記憶（DNA的な基本行動）"""
        return {
            "created_at": datetime.now().isoformat(),
            "version": "2.0",
            "known_actions": [
                {"action": "carry", "name": "運ぶ", "description": "物を持って移動する"},
                {"action": "hold", "name": "保持する", "description": "物を持ち続ける"},
                {"action": "follow", "name": "追従する", "description": "対象についていく"},
                {"action": "stop", "name": "停止する", "description": "動きを止める"},
                {"action": "pick_up", "name": "拾う", "description": "物を拾い上げる"},
                {"action": "put_down", "name": "置く", "description": "物を下に置く"},
                {"action": "come", "name": "来る", "description": "呼んだ人の方へ移動する"},
                {"action": "wait", "name": "待機する", "description": "その場で待つ"},
                {"action": "search", "name": "探す", "description": "対象を探し回る"},
                {"action": "look", "name": "見る", "description": "対象を確認する"},
                {"action": "fetch", "name": "取ってくる", "description": "物を取りに行って戻ってくる"},
                {"action": "push", "name": "押す", "description": "物を押して動かす"},
                {"action": "pull", "name": "引く", "description": "物を引っ張る"},
                {"action": "open", "name": "開ける", "description": "ドアや容器を開ける"},
                {"action": "close", "name": "閉める", "description": "ドアや容器を閉める"},
            ],
            "language_to_action": [
                {"keywords": ["運んで", "運べ", "持っていって"], "action": "carry", "taught_by": "DNA"},
                {"keywords": ["持ってて", "持っていて", "ホールド"], "action": "hold", "taught_by": "DNA"},
                {"keywords": ["ついてきて", "ついてこい", "フォロー"], "action": "follow", "taught_by": "DNA"},
                {"keywords": ["止まれ", "止まって", "ストップ", "停止"], "action": "stop", "taught_by": "DNA"},
                {"keywords": ["取って", "取れ", "拾って", "ピック"], "action": "pick_up", "taught_by": "DNA"},
                {"keywords": ["置いて", "置け", "下ろして"], "action": "put_down", "taught_by": "DNA"},
                {"keywords": ["来て", "こっち", "おいで"], "action": "come", "taught_by": "DNA"},
                {"keywords": ["待って", "待て", "ウェイト"], "action": "wait", "taught_by": "DNA"},
                {"keywords": ["探して", "探せ", "見つけて"], "action": "search", "taught_by": "DNA"},
                {"keywords": ["見て", "見ろ", "確認して"], "action": "look", "taught_by": "DNA"},
            ],
            "stats": {
                "total_commands": 0,
                "understood": 0,
                "learned_from_llm": 0,
                "learned_from_human": 0
            }
        }
    
    def save(self):
        self.memory["last_updated"] = datetime.now().isoformat()
        with open(self.filepath, 'w', encoding='utf-8') as f:
            json.dump(self.memory, f, ensure_ascii=False, indent=2)
    
    def get_known_actions_prompt(self) -> str:
        """LLM に渡す行動リスト"""
        lines = []
        for a in self.memory["known_actions"]:
            lines.append(f"- {a['action']}（{a['name']}）: {a['description']}")
        return "\n".join(lines)
    
    def find_action(self, command: str) -> Optional[Dict]:
        command_lower = command.lower()
        for item in self.memory["language_to_action"]:
            for keyword in item["keywords"]:
                if keyword in command_lower or command_lower in keyword:
                    return item
        return None
    
    def get_action_info(self, action_code: str) -> Optional[Dict]:
        for a in self.memory["known_actions"]:
            if a["action"] == action_code:
                return a
        return None
    
    def learn(self, keyword: str, action: str, taught_by: str):
        """新しいキーワードを学習"""
        # 既存の action にキーワード追加を試みる
        for item in self.memory["language_to_action"]:
            if item["action"] == action:
                if keyword not in item["keywords"]:
                    item["keywords"].append(keyword)
                    self.save()
                return
        
        # なければ新規追加
        self.memory["language_to_action"].append({
            "keywords": [keyword],
            "action": action,
            "taught_by": taught_by,
            "timestamp": datetime.now().isoformat()
        })
        self.save()


class HidaActionWithLLM:
    """
    LLM を先生にする飛騨の行動システム
    """
    
    def __init__(self):
        self.memory = ActionMemoryV2()
    
    def understand_command(self, command: str) -> Tuple[str, str, str]:
        """
        コマンドを理解する
        Returns: (action_code, action_name, source)
        """
        self.memory.memory["stats"]["total_commands"] += 1
        
        # まず記憶を検索
        found = self.memory.find_action(command)
        
        if found:
            self.memory.memory["stats"]["understood"] += 1
            self.memory.save()
            action_info = self.memory.get_action_info(found["action"])
            action_name = action_info["name"] if action_info else found["action"]
            return found["action"], action_name, "memory"
        
        return "unknown", "不明", "unknown"
    
    def ask_llm_for_action(self, command: str) -> Tuple[str, str, float]:
        """
        LLM に行動を聞く
        Returns: (action_code, explanation, confidence)
        """
        actions_list = self.memory.get_known_actions_prompt()
        
        prompt = f"""
あなたはロボットの言語理解システムです。

以下のコマンドを理解して、最も適切な行動を選んでください。

コマンド：「{command}」

選択可能な行動：
{actions_list}

回答形式（必ずこの形式で）：
行動: [action_code]
理由: [なぜその行動を選んだか]

例：
行動: fetch
理由: 「持ってきて」は物を取りに行って戻る動作なので fetch が適切
"""
        
        response = ask_ollama(prompt)
        
        # レスポンスをパース
        action = "unknown"
        explanation = response
        
        lines = response.split("\n")
        for line in lines:
            if "行動:" in line or "行動：" in line:
                # 行動コードを抽出
                parts = line.replace("行動:", "").replace("行動：", "").strip()
                # 最初の単語を取得
                action = parts.split()[0] if parts.split() else "unknown"
                # 余計な記号を除去
                action = action.strip("[]（）()「」")
                break
        
        # 既知の行動か確認
        if self.memory.get_action_info(action):
            confidence = 0.8
        else:
            confidence = 0.3
            action = "unknown"
        
        return action, explanation, confidence
    
    def learn_from_llm(self, command: str, action: str):
        """LLM から学んだことを記憶"""
        self.memory.learn(command, action, "LLM")
        self.memory.memory["stats"]["learned_from_llm"] += 1
        self.memory.save()
    
    def learn_from_human(self, command: str, action: str):
        """人間から学んだことを記憶"""
        self.memory.learn(command, action, "human")
        self.memory.memory["stats"]["learned_from_human"] += 1
        self.memory.save()
    
    def execute_action(self, action: str) -> str:
        """行動を実行（シミュレーション）"""
        action_info = self.memory.get_action_info(action)
        if action_info:
            return f"【行動】{action_info['description']}..."
        return f"【行動】{action} を実行します..."


def interactive_mode():
    """対話モード"""
    print("=" * 70)
    print("Phase 12b: Language to Action with LLM Teacher")
    print("LLM を先生にして言語から行動を学ぶ")
    print("=" * 70)
    print()
    print("流れ：")
    print("  1. コマンド入力")
    print("  2. 知ってる → 即実行")
    print("  3. 知らない → LLM に聞く → 覚える")
    print()
    print("  'q' で終了")
    print("  's' で統計")
    print("  'l' で学習内容一覧")
    print()
    print("=" * 70)
    
    hida = HidaActionWithLLM()
    
    while True:
        print("-" * 40)
        command = input("コマンド: ").strip()
        
        if command.lower() == 'q':
            break
        elif command.lower() == 's':
            stats = hida.memory.memory["stats"]
            print(f"\n【統計】")
            print(f"  総コマンド: {stats['total_commands']}")
            print(f"  即理解: {stats['understood']}")
            print(f"  LLM から学習: {stats['learned_from_llm']}")
            print(f"  人間から学習: {stats['learned_from_human']}")
            continue
        elif command.lower() == 'l':
            print(f"\n【学習内容】")
            for item in hida.memory.memory["language_to_action"]:
                keywords = ", ".join(item["keywords"])
                taught = item.get("taught_by", "DNA")
                print(f"  {item['action']}: {keywords} [{taught}]")
            continue
        
        if not command:
            continue
        
        # コマンドを理解
        action, action_name, source = hida.understand_command(command)
        
        if source == "memory":
            print(f"  → 理解: {action} ({action_name}) [★記憶から]")
            result = hida.execute_action(action)
            print(f"  {result}")
        else:
            print(f"  → 記憶にない。LLM に聞きます...")
            
            # LLM に聞く
            llm_action, explanation, confidence = hida.ask_llm_for_action(command)
            
            print(f"\n  【LLM の回答】")
            print(f"  {explanation[:100]}...")
            print(f"  → 推測: {llm_action} (確信度: {confidence:.0%})")
            
            if llm_action != "unknown" and confidence >= 0.5:
                # LLM の答えを使う
                confirm = input(f"\n  これで覚えていい？ (y/n): ").strip().lower()
                
                if confirm == 'y' or confirm == '':
                    hida.learn_from_llm(command, llm_action)
                    print(f"  → 覚えました: 「{command}」 → {llm_action}")
                    result = hida.execute_action(llm_action)
                    print(f"  {result}")
                else:
                    # 人間が訂正
                    print(f"\n  正しい行動を教えてください。")
                    print(f"  選択肢: {', '.join(a['action'] for a in hida.memory.memory['known_actions'])}")
                    correct_action = input("  行動: ").strip()
                    if correct_action:
                        hida.learn_from_human(command, correct_action)
                        print(f"  → 覚えました: 「{command}」 → {correct_action}")
                        result = hida.execute_action(correct_action)
                        print(f"  {result}")
            else:
                # LLM もわからない → 人間に聞く
                print(f"\n  LLM もわかりませんでした。教えてください。")
                print(f"  選択肢: {', '.join(a['action'] for a in hida.memory.memory['known_actions'])}")
                human_action = input("  行動: ").strip()
                if human_action:
                    hida.learn_from_human(command, human_action)
                    print(f"  → 覚えました: 「{command}」 → {human_action}")
                    result = hida.execute_action(human_action)
                    print(f"  {result}")
    
    print("\n" + "=" * 70)
    print("【終了】")
    stats = hida.memory.memory["stats"]
    print(f"  総コマンド: {stats['total_commands']}")
    print(f"  LLM から学習: {stats['learned_from_llm']}")
    print(f"  人間から学習: {stats['learned_from_human']}")
    print(f"\n記憶は {ACTION_MEMORY_FILE} に保存されました。")
    print("=" * 70)


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "show":
        if os.path.exists(ACTION_MEMORY_FILE):
            with open(ACTION_MEMORY_FILE, 'r', encoding='utf-8') as f:
                print(json.dumps(json.load(f), ensure_ascii=False, indent=2))
    else:
        interactive_mode()
