# Phase 15: HIDA Core Architecture - Action Learning
# 飛騨アーキテクチャ本体 + 行動学習 + 永続記憶

## 概要

Phase 15 は飛騨アーキテクチャに「行動学習」と「永続記憶」を追加。
再起動しても学習内容が残り、行動レシピで複雑な動作を実行できる。

## 実行方法

```bash
python phase15_hida_core.py
```

## Phase 14 からの追加機能

| 機能 | Phase 14 | Phase 15 |
|------|----------|----------|
| 行動レシピ | なし | プリミティブの組み合わせ |
| 永続記憶 | なし | JSON 保存/読込 |
| 忘却機能 | なし | 「〇〇を忘れて」 |
| キャンセル | なし | 「キャンセル」「やめて」 |
| print 抑制 | なし | 入力待ち中は抑制 |

## 永続記憶

### 保存されるもの

```python
hida_memory.json:
{
  "preferences": {
    "verbs": {"ゲット": "fetch"},
    "responses": {"おはよう": "おはようございます"},
    "custom_actions": {"片づけて": "全部元の位置に戻す"}
  },
  "action_recipes": {...},
  "original_pos": {"赤いボール": [2.0, 1.0, 0.3]},
  "experiences": [...],  # 最新100件
  "success_rate": {...}
}
```

### 保存タイミング

- 学習した時（verbs, responses, custom_actions）
- 終了時（q で終了）

### 読込タイミング

- 起動時に自動読込

## 行動レシピ

### プリミティブ（基本動作）

| プリミティブ | 説明 |
|-------------|------|
| count | 対象を数える |
| report | 結果を報告 |
| fetch | 取ってくる |
| move_to | 移動 |
| put_down | 置く |
| for_each | 繰り返し |

### 組み込みレシピ

```python
"数える": [
    {"primitive": "count", "target": "all_balls"},
    {"primitive": "report", "content": "count_result"},
]

"片付ける": [
    {"primitive": "for_each", "target": "all_balls", "do": [
        {"primitive": "fetch", "target": "$item"},
        {"primitive": "move_to", "target": "$item.original_pos"},
        {"primitive": "put_down"},
    ]},
]

"全部取ってくる": [
    {"primitive": "for_each", "target": "all_balls", "do": [
        {"primitive": "fetch", "target": "$item"},
    ]},
]
```

### 使用例

```
飛騨、片付けて
→ 行動を教える
→ 全部元の位置に戻す
→ 学習完了

飛騨、片付けて
→ [for_each] 赤いボール
→ [for_each] 黄色いボール
→ [for_each] 青いボール
→ 全部元の位置に戻す
```

## 忘却機能

学習を間違えた時に削除できる。

```
飛騨、おやすみを忘れて
→ [忘却] 「おやすみ」の行動を忘れました
→ [記憶保存] hida_memory.json
```

対応するもの：
- custom_actions（行動）
- responses（応答）
- verbs（動詞）

## キャンセル機能

質問中にキャンセルできる。

```
飛騨、こんにちは
→ 「どういう意味？」
→ キャンセル
→ キャンセルしました
```

キャンセルキーワード：
- キャンセル
- やめて
- 間違えた
- 違う
- やっぱ

## コマンド一覧

### 基本コマンド

| コマンド | 動作 |
|---------|------|
| 飛騨、赤いボール取って | 赤いボールを取ってくる |
| 飛騨、赤返して | 赤いボールを初期位置に戻す |
| 飛騨、片付けて | 全ボールを元に戻す |
| 飛騨、止まって | 行動を中断 |
| q | 終了（記憶を保存） |

### 学習コマンド

| コマンド | 動作 |
|---------|------|
| 応答を教える | 言葉の返事を学習 |
| 行動を教える | カスタム行動を学習 |
| 〇〇を忘れて | 学習を削除 |
| キャンセル | 質問を中断 |

### 挨拶（学習済みの例）

| コマンド | 応答 |
|---------|------|
| 飛騨、おはよう | おはようございます |
| 飛騨、こんにちは | こんにちは |
| 飛騨、おやすみ | おやすみなさい |
| 飛騨、お疲れ | お疲れ様でした |

## 技術的特徴

### 入力待ち中の print 抑制

```python
# 問題: 入力待ち中にバックグラウンドループが print
# 解決: waiting_input フラグで抑制

hida.waiting_input = True   # input() 前
text = input("\nあなた: ")
hida.waiting_input = False  # input() 後

# _layer5_consciousness で
if self.waiting_input:
    return  # print しない
```

### 質問待ち中の意識維持

```python
# 問題: 質問中に意識が OFF になる
# 解決: waiting_for_answer 中は意識状態を変更しない

if self.waiting_for_answer:
    return
```

## L4 記憶の構造

```python
Memory:
    objects: {...}           # 物体の知識
    last_seen: {...}         # 最後に見た位置
    original_pos: {...}      # 初期位置（返す用）
    success_rate: {...}      # 成功率
    experiences: [...]       # 経験
    preferences: {           # 学習した好み
        "verbs": {...},
        "responses": {...},
        "custom_actions": {...},
    }
    action_recipes: {...}    # 行動レシピ
    
    save()                   # JSON に保存
    load()                   # JSON から読込
```

## ファイル構成

```
phase15_hida_core.py    # 本体（約1400行）
hida_memory.json        # 永続記憶（自動生成）
phase15_readme.md       # このドキュメント
```

## 今後の課題

1. **複数選択の改善**: 「赤と青」で両方取る
2. **レシピの動的追加**: 人間が新しいレシピを教える
3. **視覚照合の強化**: 同色オブジェクトの区別
4. **障害物回避**: 物理的な経路計画

## 実行例

```
[記憶読込] hida_memory.json
  - verbs: 0件
  - responses: 4件
  - custom_actions: 0件
  - experiences: 23件

あなた: 飛騨、おはよう
【聞こえた】「飛騨、おはよう」
  → 呼ばれた！
  → [L4] 「おはよう」→「おはようございます」
  飛騨: 「おはようございます」

あなた: 飛騨、赤持ってきて
【聞こえた】「飛騨、赤持ってきて」
  → 呼ばれた！
  → [L4] 「赤」→「赤いボール」と推測
  [キュー] 1件のタスクを追加（fetch）
  [探索中] 赤いボール
  [発見] 位置: [2.0, 1.0, 0.3]
  ...
  [完了] 赤いボール を届けました
  [経験] 成功体験を記録（累計: 24件）

あなた: q
[記憶保存] hida_memory.json
終了
```

## まとめ

Phase 15 で実現したこと：

1. **行動レシピ**: プリミティブの組み合わせで複雑な動作
2. **永続記憶**: 再起動しても学習が残る
3. **忘却機能**: 間違えた学習を削除
4. **キャンセル機能**: 質問を中断
5. **UX改善**: 入力待ち中の print 抑制

飛騨は「育てる」ロボットになった。

---

Created: 2025-12-13
Author: とまと + Claude
License: MIT
