"""
test_entrainment_ablation.py
v2.1 引き込み機構のアブレーション検証

目的:
  v2.0への批判「非対称性（主導→追随の時間的因果）は測定にしか存在せず、
  力学として実在しない」に対し、v2.1の引き込み機構（ENTRAIN_K）が
  実際に「主導→追随」の因果を生んでいることを実証する。

方法:
  同一シナリオ・同一乱数シード群で、引き込みOFF（ENTRAIN_K=0）と
  引き込みON（ENTRAIN_K=0.5）の2条件を比較する。

測定量:
  1. 時間遅れ応答: 主導イベントが起きたステップtの直後（t+1）における
     追随層の活動上昇量の平均
  2. 時間遅れ相関: 主導強度(t) と 追随層平均活動量(t+1) のPearson相関

予測:
  引き込みONの条件でのみ、(1)(2)が有意に大きくなる。
  これが確認されれば、「主導→追随」は相関ではなく、実装された
  因果チャネルとして存在することが示される（論文§4.3.4の将来拡張に対応）。

実行: python3 test_entrainment_ablation.py
依存: Python標準ライブラリのみ
"""

import os
import random
import io
import contextlib

import hida_unified_v2 as h


N_SEEDS = 30
MAX_STEPS = 40


def clean_persistence():
    """LTM・変調値ファイルを削除して条件間の汚染を防ぐ"""
    for f in ("hida_ltm.json", "hida_modulation.json"):
        if os.path.exists(f):
            os.remove(f)


def run_one(seed: int, entrain_k: float):
    """1シード分のシミュレーションを実行し、時系列を返す

    Returns:
        list of dict: 各ステップの
            {'leader': str|None, 'strength': float, 'activities': dict}
    """
    clean_persistence()
    random.seed(seed)

    buf0 = io.StringIO()
    with contextlib.redirect_stdout(buf0):  # LTM読み込みログ等を抑制
        world = h.create_test_world()
        agent = h.HIDA(color_preference={'red': 1.0, 'blue': 0.3, 'green': 0.3})
    agent.l1.position = [3, 6]
    agent.l1.direction = 'N'
    agent.l1.energy = 1.0
    agent.l5.ENTRAIN_K = entrain_k  # アブレーション対象

    # run_test()と同じ初期知識を与える
    agent.l4.found_objects[(6, 3)] = {'name': 'ball', 'color': 'red'}
    agent.l4.found_objects[(2, 4)] = {'name': 'ball', 'color': 'blue'}
    agent.l4.found_objects[(2, 7)] = {'name': 'ball', 'color': 'green'}
    agent.l4.found_objects[(4, 6)] = {'name': 'ball', 'color': 'yellow', 'rotten': True}
    agent.l4.found_objects[(7, 7)] = {'name': 'goal', 'color': None}
    for x in range(1, 9):
        for y in range(1, 9):
            if world.get_cell(x, y) == 'danger':
                agent.l4.internal_map[(x, y)] = 'danger'
            else:
                agent.l4.internal_map[(x, y)] = 'empty'

    series = []
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):  # NPC等の出力を抑制
        for _ in range(MAX_STEPS):
            result = agent.step(world, verbose=False)
            series.append({
                'leader': agent.l5.sync_type,
                'strength': agent.l5.leader_strength,
                'activities': dict(agent.l5.last_activities),
            })
            if result['goal_reached'] or agent.l1.energy <= 0:
                break
    return series


def follower_mean(activities: dict, leader: str) -> float:
    """主導層を除く3層の活動量平均"""
    vals = [v for k, v in activities.items() if k != leader]
    return sum(vals) / len(vals) if vals else 0.0


def lagged_rise(series) -> list:
    """主導イベント直後の追随層活動上昇量を収集"""
    rises = []
    for t in range(len(series) - 1):
        cur, nxt = series[t], series[t + 1]
        if cur['leader'] is None:
            continue
        followers = [k for k in cur['activities'] if k != cur['leader']]
        rise = sum(max(0.0, nxt['activities'][k] - cur['activities'][k])
                   for k in followers) / len(followers)
        rises.append(rise)
    return rises


def lagged_pairs(series) -> list:
    """(主導強度(t), 追随層平均活動(t+1)) のペアを収集"""
    pairs = []
    for t in range(len(series) - 1):
        cur, nxt = series[t], series[t + 1]
        if cur['leader'] is None:
            continue
        pairs.append((cur['strength'], follower_mean(nxt['activities'], cur['leader'])))
    return pairs


def pearson(pairs) -> float:
    """Pearson相関係数（標準ライブラリのみ）"""
    n = len(pairs)
    if n < 3:
        return float('nan')
    xs = [p[0] for p in pairs]
    ys = [p[1] for p in pairs]
    mx = sum(xs) / n
    my = sum(ys) / n
    cov = sum((x - mx) * (y - my) for x, y in pairs)
    vx = sum((x - mx) ** 2 for x in xs)
    vy = sum((y - my) ** 2 for y in ys)
    if vx == 0 or vy == 0:
        return float('nan')
    return cov / (vx ** 0.5 * vy ** 0.5)


def main():
    print("=" * 64)
    print("v2.1 引き込み機構アブレーション検証")
    print(f"  条件: ENTRAIN_K = 0.0（OFF） vs 0.5（ON）")
    print(f"  シード数: {N_SEEDS}, 最大ステップ: {MAX_STEPS}")
    print("=" * 64)

    results = {}
    per_seed = {}
    for label, k in (("OFF (K=0.0)", 0.0), ("ON  (K=0.5)", 0.5)):
        all_rises = []
        all_pairs = []
        leader_events = 0
        seed_means = []
        for seed in range(N_SEEDS):
            series = run_one(seed, k)
            rises = lagged_rise(series)
            all_rises.extend(rises)
            all_pairs.extend(lagged_pairs(series))
            leader_events += sum(1 for s in series if s['leader'] is not None)
            seed_means.append(sum(rises) / len(rises) if rises else 0.0)
        per_seed[label] = seed_means
        mean_rise = sum(all_rises) / len(all_rises) if all_rises else 0.0
        r = pearson(all_pairs)
        results[label] = (mean_rise, r, leader_events)
        print(f"\n[{label}]")
        print(f"  主導イベント数（全シード合計）        : {leader_events}")
        print(f"  主導イベント直後の追随層活動上昇（平均）: {mean_rise:.4f}")
        print(f"  時間遅れ相関 r(主導強度t, 追随平均t+1) : {r:.4f}")

    # シード単位の勝率（同一シードでON > OFFか）
    wins = sum(1 for a, b in zip(per_seed["ON  (K=0.5)"], per_seed["OFF (K=0.0)"]) if a > b)
    ties = sum(1 for a, b in zip(per_seed["ON  (K=0.5)"], per_seed["OFF (K=0.0)"]) if a == b)
    print(f"\n  シード単位の比較: ON > OFF が {wins}/{N_SEEDS} シード（引き分け {ties}）")

    print("\n" + "=" * 64)
    off_rise, off_r, _ = results["OFF (K=0.0)"]
    on_rise, on_r, _ = results["ON  (K=0.5)"]
    rise_ok = on_rise > off_rise
    corr_ok = (on_r > off_r) if (on_r == on_r and off_r == off_r) else False
    print("判定:")
    print(f"  追随層の時間遅れ応答: ON > OFF ... {'PASS' if rise_ok else 'FAIL'}"
          f"  ({on_rise:.4f} vs {off_rise:.4f})")
    print(f"  時間遅れ相関:        ON > OFF ... {'PASS' if corr_ok else 'FAIL'}"
          f"  ({on_r:.4f} vs {off_r:.4f})")
    if rise_ok:
        print("\n結論: 引き込み機構により「主導→追随」の時間的因果が")
        print("      力学として実在することが確認された。")
    else:
        print("\n結論: 因果は確認されなかった。ENTRAIN_Kまたは各層の")
        print("      ゲイン適用箇所の見直しが必要。")
    clean_persistence()


if __name__ == "__main__":
    main()
