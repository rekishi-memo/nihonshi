# 授業の並べ替え（2026-11-08 ユーザーの指示「時代が交差している。流れを追いやすく。文化史は時代の切れ目に」）。
#   python3 reorder.py ../app/source.html ../app/source.html
# ・各授業に src（もとの「セットid-授業番号」）を付ける。tools のスクリプト（rewrite_lessons / merge_add / add_maps / add_col）は
#   src で授業を探すので、*_text.py などのキー（もとの番号）はそのまま使える（buildpack.locate を参照）
# ・同じセットの中の並べ替え：授業番号を振り直し、一問一答の link を付け替える（一問一答の id は変えない）
# ・別のセットへ移す授業：その授業の一問一答も移し、移し先で新しい id を振る。旧 id の学習記録は
#   アプリの QMOVES（[旧セット,旧id,新セット,新id]）で読み込み時に引き継ぐ
# 2回目以降は何もしない（src が付いていれば済み）
import json,re,sys
src,out=sys.argv[1:3]
PLAN={
 'kodai5':[('kodai5',n) for n in ['01','02','03','09','11','10','04','05','06','07','08']],
 'chusei3':[('chusei3',n) for n in ['01','02','03','06','07','08','09','04','05']],
 'chusei4':[('chusei4',n) for n in ['01','02','03','04','05','06']]+[('chusei6','01'),('chusei6','02')]+[('chusei4','07'),('chusei4','08')],
 'chusei5':[('chusei5',n) for n in ['01','02','03','04','05','06','07','08']]+[('chusei6','03'),('chusei6','04'),('chusei6','05')],
 'chusei6':[('chusei6',n) for n in ['06','07','08','09']],
}
META={
 'chusei4':dict(title='中世④（南北朝〜室町幕府・北山文化）',subtitle='建武の新政・南北朝の動乱・守護大名・室町幕府・南北朝の文化・北山文化・能・日明日朝貿易・琉球と蝦夷ヶ島'),
 'chusei5':dict(title='中世⑤（惣村・一揆・応仁の乱・東山文化）',subtitle='惣村・幕府の動揺・土一揆・応仁の乱・国一揆と一向一揆・農業と商工業の発達・東山文化・庶民文芸・文化の地方普及'),
 'chusei6':dict(title='中世⑥（戦国大名と都市）',subtitle='戦国大名・家臣団と分国法・領国経営・都市の発展と町衆',range='戦国大名 ── 下剋上の時代・分国法・城下町・堺と京都の町衆'),
}
s=open(src,encoding='utf-8').read()
m=re.search(r'const DEFAULT_PACKS = (\[[\s\S]*?\n\]);',s); packs=json.loads(m.group(1)); P={p['id']:p for p in packs}
if any(l.get('src') for l in P['chusei6']['lessons']): sys.exit('already reordered')
for p in packs:
    for l in p['lessons']: l['src']=f"{p['id']}-{l['no']}"
old={(p['id'],l['no']):l for p in packs for l in p['lessons']}
oldquiz={pid:list(P[pid]['quiz']) for pid in PLAN}
moves=[]; newlessons={}
for pid,seq in PLAN.items():
    newlessons[pid]=[]
    for i,(sp,sn) in enumerate(seq,1):
        l=old[(sp,sn)]; l=dict(l); l['no']=f'{i:02d}'; newlessons[pid].append(((sp,sn),l))
# 一問一答の付け替え
newquiz={pid:[] for pid in PLAN}
where={k:(pid,l['no']) for pid,v in newlessons.items() for k,l in v}
for sp in PLAN:
    for q in oldquiz[sp]:
        tp,tn=where[(sp,q['link'])]
        q=dict(q); q['link']=tn
        if tp==sp: newquiz[sp].append(q)
        else: newquiz[tp].append(('MOVE',sp,q))
idmax={pid:max([q['id'] for q in oldquiz[pid]]+[P[pid].get('idMax',0)]) for pid in PLAN}
for pid in PLAN:
    res=[]
    for q in newquiz[pid]:
        if isinstance(q,tuple):
            _,sp,q=q; idmax[pid]+=1; moves.append([sp,q['id'],pid,idmax[pid]]); q['id']=idmax[pid]
        res.append(q)
    P[pid]['quiz']=res; P[pid]['lessons']=[l for _,l in newlessons[pid]]
    P[pid]['idMax']=idmax[pid]
P['chusei6']['idMax']=max(P['chusei6']['idMax'],max(q['id'] for q in oldquiz['chusei6']))  # 移した問題の旧 id を二度と使わない
# 文化の授業に付いていた年表・用語・語呂・論述・穴埋めも移す
def plain(h): return re.sub(r'<[^>]+>','',re.sub(r'<rt>[^<]*</rt>','',h))
txt={pid:plain(''.join(l['html']+l.get('colHtml','') for l in P[pid]['lessons'] if l['src'].startswith('chusei6-'))) for pid in ('chusei4','chusei5')}
c6=P['chusei6']
def dest(text):
    for pid in ('chusei4','chusei5'):
        if text and text in txt[pid]: return pid
    return None
keep=[]
for t in c6['terms']:
    d=dest(t['term']); (P[d]['terms'].append(t) if d else keep.append(t))
c6['terms']=keep
keep=[]
for t in c6['timeline']:
    y=int(re.match(r'\d+',t['y']).group(0))
    if y<1420: P['chusei4']['timeline'].append(t)
    elif t['y'] in ('1439','1467','1482','1488','1495','1518'): P['chusei5']['timeline'].append(t)
    else: keep.append(t)
c6['timeline']=keep
for pid in ('chusei4','chusei5'): P[pid]['timeline'].sort(key=lambda t:int(re.match(r'\d+',t['y']).group(0)))
keep=[]
for g in c6['goro']:
    d=dest(g['ans'].split('＝')[0].split('・')[0].split('（')[0].strip()) or dest(g['phrase'].split('・')[0])
    (P[d]['goro'].append(g) if d else keep.append(g))
c6['goro']=keep
keep=[]
for r in c6['ronjutsu']:
    if '文化' in r['q']: P['chusei5' if ('東山' in r['q'] or '室町文化' in r['q']) else 'chusei4']['ronjutsu'].append(r)
    else: keep.append(r)
c6['ronjutsu']=keep
keep=[]
for c in c6['cloze']:
    if c['title'].startswith('南北朝・北山'): P['chusei4']['cloze'].append(c)
    elif c['title'].startswith('東山'): P['chusei5']['cloze'].append(c)
    else: keep.append(c)
c6['cloze']=keep
for pid,d in META.items(): P[pid].update(d)
s=s[:m.start(1)]+json.dumps(packs,ensure_ascii=False,indent=1)+s[m.end(1):]
# 学習記録の引き継ぎ表をアプリに入れる
js='const QMOVES='+json.dumps(moves)+';'
if 'const QMOVES=' in s: s=re.sub(r'const QMOVES=\[[^;]*\];',js,s)
else:
    k=s.index('const PK_KEY=')
    s=s[:k]+'/* 授業をほかのセットへ移したときの一問一答の学習記録の引き継ぎ（[旧セット,旧id,新セット,新id]） */\n'+js+'\n'+s[k:]
open(out,'w',encoding='utf-8').write(s)
print('moved quiz',len(moves))
for pid in PLAN: print(pid,[l['src'] for l in P[pid]['lessons']])
