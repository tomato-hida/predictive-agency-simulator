#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Phase 12: Language to Action
言語から行動への変換

Theory of Human Inner Movement
人の内なる運動理論

ロボットに必要なもの：
1. 入力を受ける（センサー、言葉）
2. 理解する
3. 行動する

このフェーズでは：
- 言語コマンド → 行動コード の変換
- 知らない言葉は人間に聞く
- 教わったら覚える
"""

import json
import os
from typing import Dict, Optional, Tuple, List
from datetime import datetime

# Memory file path
ACTION_MEMORY_FILE = "hida_action_memory.json"


class ActionMemory:
    """
    言語 → 行動 の記憶
    """
    
    def __init__(self, filepath: str = ACTION_MEMORY_FILE):
        self.filepath = filepath
        self.memory = self._load_or_create()
    
    def _load_or_create(self) -> Dict:
        """記憶ファイルを読み込む、なければ作る"""
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
            "version": "1.0",
            "language_to_action": [
                # DNA的な初期値（基本コマンド）
                {
                    "keywords": ["運んで", "運べ", "持っていって"],
                    "action": "carry",
                    "action_name": "運ぶ",
                    "taught_by": "DNA"
                },
                {
                    "keywords": ["持ってて", "持っていて", "ホールド"],
                    "action": "hold",
                    "action_name": "保持する",
                    "taught_by": "DNA"
                },
                {
                    "keywords": ["ついてきて", "ついてこい", "フォロー"],
                    "action": "follow",
                    "action_name": "追従する",
                    "taught_by": "DNA"
                },
                {
                    "keywords": ["止まれ", "止まって", "ストップ", "停止"],
                    "action": "stop",
                    "action_name": "停止する",
                    "taught_by": "DNA"
                },
                {
                    "keywords": ["取って", "取れ", "拾って", "ピック"],
                    "action": "pick_up",
                    "action_name": "拾う",
                    "taught_by": "DNA"
                },
                {
                    "keywords": ["置いて", "置け", "下ろして"],
                    "action": "put_down",
                    "action_name": "置く",
                    "taught_by": "DNA"
                },
                {
                    "keywords": ["来て", "こっち", "おいで"],
                    "action": "come",
                    "action_name": "来る",
                    "taught_by": "DNA"
                },
                {
                    "keywords": ["待って", "待て", "ウェイト"],
                    "action": "wait",
                    "action_name": "待機する",
                    "taught_by": "DNA"
                },
                {
                    "keywords": ["探して", "探せ", "見つけて"],
                    "action": "search",
                    "action_name": "探す",
                    "taught_by": "DNA"
                },
                {
                    "keywords": ["見て", "見ろ", "確認して"],
                    "action": "look",
                    "action_name": "見る",
                    "taught_by": "DNA"
                },
            ],
            "unknown_commands": [],  # わからなかったコマンド
            "stats": {
                "total_commands": 0,
                "understood": 0,
                "asked_human": 0
            }
        }
    
    def save(self):
        """記憶をファイルに保存"""
        self.memory["last_updated"] = datetime.now().isoformat()
        with open(self.filepath, 'w', encoding='utf-8') as f:
            json.dump(self.memory, f, ensure_ascii=False, indent=2)
    
    def find_action(self, command: str) -> Optional[Dict]:
        """
        コマンドから行動を探す
        """
        command_lower = command.lower()
        
        for item in self.memory["language_to_action"]:
            for keyword in item["keywords"]:
                if keyword in command_lower or command_lower in keyword:
                    return item
        
        return None
    
    def learn_action(self, keywords: List[str], action: str, action_name: str):
        """新しい行動を学習"""
        self.memory["language_to_action"].append({
            "keywords": keywords,
            "action": action,
            "action_name": action_name,
            "taught_by": "human",
            "timestamp": datetime.now().isoformat()
        })
        self.memory["stats"]["asked_human"] += 1
        self.save()
    
    def add_keyword_to_action(self, new_keyword: str, action: str):
        """既存の行動に新しいキーワードを追加"""
        for item in self.memory["language_to_action"]:
            if item["action"] == action:
                if new_keyword not in item["keywords"]:
                    item["keywords"].append(new_keyword)
                    self.save()
                return True
        return False
    
    def get_stats(self) -> Dict:
        """統計"""
        return {
            "known_actions": len(self.memory["language_to_action"]),
            "total_keywords": sum(len(item["keywords"]) for item in self.memory["language_to_action"]),
            "stats": self.memory["stats"]
        }


class HidaActionSystem:
    """
    飛騨の行動システム
    言語 → 行動 の変換
    """
    
    def __init__(self):
        self.memory = ActionMemory()
        self.last_command = ""
    
    def understand_command(self, command: str) -> Tuple[str, str, str]:
        """
        コマンドを理解する
        
        Returns:
            (action_code, action_name, source)
            source: "memory" = 知ってた, "unknown" = わからない
        """
        self.last_command = command
        self.memory.memory["stats"]["total_commands"] += 1
        
        # 記憶を検索
        found = self.memory.find_action(command)
        
        if found:
            self.memory.memory["stats"]["understood"] += 1
            self.memory.save()
            return found["action"], found["action_name"], "memory"
        else:
            return "unknown", "不明", "unknown"
    
    def learn(self, keywords: List[str], action: str, action_name: str):
        """人間から教わる"""
        self.memory.learn_action(keywords, action, action_name)
        print(f"  → 覚えました: {keywords} → {action} ({action_name})")
    
    def execute_action(self, action: str) -> str:
        """
        行動を実行（シミュレーション）
        実際のロボットならここでモーター制御
        """
        actions = {
            "carry": "【行動】物を持って移動します...",
            "hold": "【行動】物を保持しています...",
            "follow": "【行動】あなたについていきます...",
            "stop": "【行動】停止しました。",
            "pick_up": "【行動】物を拾います...",
            "put_down": "【行動】物を置きます...",
            "come": "【行動】そちらに向かいます...",
            "wait": "【行動】待機しています...",
            "search": "【行動】探索を開始します...",
            "look": "【行動】確認しています...",
        }
        
        return actions.get(action, f"【行動】{action} を実行します...")


def interactive_mode():
    """対話モード"""
    print("=" * 70)
    print("Phase 12: Language to Action")
    print("言語から行動への変換")
    print("=" * 70)
    print()
    print("使い方：")
    print("  コマンドを入力 → 飛騨が理解して行動する")
    print("  わからなければ → 人間が教える")
    print()
    print("  'q' で終了")
    print("  's' で統計表示")
    print("  'l' で学習内容一覧")
    print()
    print("=" * 70)
    
    hida = HidaActionSystem()
    
    # 統計表示
    stats = hida.memory.get_stats()
    print(f"\n【行動記憶の状態】")
    print(f"  知っている行動: {stats['known_actions']} 種類")
    print(f"  登録キーワード: {stats['total_keywords']} 個")
    print()
    
    while True:
        print("-" * 40)
        
        command = input("コマンド: ").strip()
        
        if command.lower() == 'q':
            break
        elif command.lower() == 's':
            stats = hida.memory.get_stats()
            print(f"\n【統計】")
            print(f"  知っている行動: {stats['known_actions']} 種類")
            print(f"  登録キーワード: {stats['total_keywords']} 個")
            print(f"  総コマンド数: {stats['stats']['total_commands']}")
            print(f"  理解できた: {stats['stats']['understood']}")
            print(f"  人間に聞いた: {stats['stats']['asked_human']}")
            continue
        elif command.lower() == 'l':
            print(f"\n【学習内容】")
            for item in hida.memory.memory["language_to_action"]:
                keywords = ", ".join(item["keywords"])
                print(f"  {item['action']} ({item['action_name']})")
                print(f"    キーワード: {keywords}")
            continue
        
        if not command:
            continue
        
        # コマンドを理解
        action, action_name, source = hida.understand_command(command)
        
        if source == "memory":
            print(f"  → 理解: {action} ({action_name}) [★記憶から]")
            # 行動実行
            result = hida.execute_action(action)
            print(f"  {result}")
        else:
            print(f"  → 飛騨: わかりません。教えてください。")
            print()
            print("  教え方：")
            print("    1. 行動コード（英語、例: push, pull, turn）")
            print("    2. 行動名（日本語、例: 押す, 引く, 回る）")
            print("    3. 他のキーワード（カンマ区切り）")
            print()
            
            action_code = input("  行動コード: ").strip()
            if not action_code:
                print("  → スキップしました")
                continue
                
            action_name = input("  行動名: ").strip()
            if not action_name:
                action_name = action_code
            
            other_keywords = input("  他のキーワード（カンマ区切り、なければ空）: ").strip()
            
            keywords = [command]
            if other_keywords:
                keywords.extend([k.strip() for k in other_keywords.split(",")])
            
            hida.learn(keywords, action_code, action_name)
            
            # 学習後に実行
            result = hida.execute_action(action_code)
            print(f"  {result}")
    
    # 終了時の統計
    print("\n" + "=" * 70)
    print("【終了】")
    stats = hida.memory.get_stats()
    print(f"  知っている行動: {stats['known_actions']} 種類")
    print(f"  登録キーワード: {stats['total_keywords']} 個")
    print(f"\n記憶は {ACTION_MEMORY_FILE} に保存されました。")
    print("=" * 70)


def show_memory():
    """記憶の内容を表示"""
    if os.path.exists(ACTION_MEMORY_FILE):
        with open(ACTION_MEMORY_FILE, 'r', encoding='utf-8') as f:
            memory = json.load(f)
        print(json.dumps(memory, ensure_ascii=False, indent=2))
    else:
        print("記憶ファイルがありません")


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "show":
        show_memory()
    else:
        interactive_mode()
