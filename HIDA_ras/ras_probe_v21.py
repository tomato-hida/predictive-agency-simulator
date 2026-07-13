"""
ras_probe_v21.py
v2.1(引き込み機構あり)上で、RAS大域ゲインを重ねたときの結合ループ安定性を
実エージェントのstep()で測る。2x2: RAS{on/off} × entrainment{on/off}。

entrainment off は L5.ENTRAIN_K=0 で boost=1 に固定して実現。
LLM(reflect)は verbose=False で呼ばれない。
"""
import hida_v21_work as h

def setup(ras_on, entrain_on):
    world = h.create_test_world()
    # entrainment on/off をクラス定数で切替（boost=1+K*strength, K=0で無効化）
    h.L5Consciousness.ENTRAIN_K = 0.5 if entrain_on else 0.0
    a = h.HIDA(color_preference={'red':1.0,'blue':0.3,'green':0.3})
    a.ras_enabled = ras_on
    a.l1.position=[3,6]; a.l1.direction='N'; a.l1.energy=1.0
    # 発見済み＆マップ付与（run_test相当）
    for pos,info in {(6,3):{'name':'ball','color':'red'},(2,4):{'name':'ball','color':'blue'},
                     (2,7):{'name':'ball','color':'green'},(4,6):{'name':'ball','color':'yellow','rotten':True},
                     (7,7):{'name':'goal','color':None}}.items():
        a.l4.found_objects[pos]=info
    for x in range(1,9):
        for y in range(1,9):
            a.l4.internal_map[(x,y)]='danger' if world.get_cell(x,y)=='danger' else 'empty'
    return world,a

def run(ras_on, entrain_on, steps=40):
    world,a = setup(ras_on, entrain_on)
    tr=[]
    for _ in range(steps):
        r = a.step(world, verbose=False)
        tr.append((a.l2.arousal, a.l5.leader_strength, a.l5.sync_score,
                   a.last_ras_gain, dict(a.l5.entrain_gain)))
        if r['goal_reached'] or a.l1.energy<=0:
            break
    return a,tr

def report(name, tr):
    ar=[x[0] for x in tr]; ls=[x[1] for x in tr]; ss=[x[2] for x in tr]
    def band(v): return f"[{min(v):+.2f},{max(v):+.2f}]"
    # 発散/張り付き判定
    pin_ar = sum(1 for a in ar[-5:] if abs(a)>=0.999)==min(5,len(ar))
    nan = any(a!=a for a in ar+ls+ss)  # NaNチェック
    g3=[x[4].get('L3',1.0) for x in tr]
    print(f"  {name:<22} steps={len(tr):2d}  arousal{band(ar)} leader{band(ls)} "
          f"sync{band(ss)}  L3gain_max={max(g3):.2f} rasG_last={tr[-1][3]:.3f}"
          f"{'  <PIN>' if pin_ar else ''}{'  <NaN!>' if nan else ''}")

print("="*94)
print("2x2 安定性: RAS × entrainment  (v2.1 実エージェント, 40歩 or ゴール到達まで)")
print("="*94)
for entrain_on in (True, False):
    for ras_on in (True, False):
        _,tr = run(ras_on, entrain_on)
        report(f"RAS={'on ' if ras_on else 'off'} entrain={'on ' if entrain_on else 'off'}", tr)
