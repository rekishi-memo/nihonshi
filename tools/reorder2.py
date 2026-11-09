# 授業の並べ替え 第2弾（2026-11-09）。近世以降も「文化は、前の授業と直接つながらない授業の手前に」の基準で並べ直す。
#   python3 reorder2.py ../app/source.html ../app/source.html
# ・桃山文化（近世②の01・02）を近世①の「刀狩」と「秀吉の対外政策」のあいだへ（朝鮮侵略 → 関ヶ原 を直結させる）
# ・大正：大戦景気を米騒動の前へ、大衆文化を「ワシントン体制」と「社会運動」のあいだへ（震災 → 震災恐慌 を直結）
# ・占領期の文化（現代②の03）を現代①の最後へ（講和 → 独立後の再編 を直結）
# ・寛政〜天保の改革（kinsei9）を宝暦・天明期の文化（kinsei8）より前にし、番号の⑧と⑨を入れかえる（田沼 → 寛政 を直結）
# 一問一答をほかのセットへ移したときは QMOVES に足す（reorder.py と同じしくみ）。2回目は何もしない。
import json,re,sys
src,out=sys.argv[1:3]
PLAN={
 'kinsei':[('kinsei',n) for n in ['01','02','03','04','05','06','07']]+[('kinsei2','01'),('kinsei2','02')]+[('kinsei','08')],
 'kinsei2':[('kinsei2',n) for n in ['03','04','05','06','07','08']],
 'taisho':[('taisho',n) for n in ['01','02','03','08','04','05','09','06','07']],
 'gendai':[('gendai',n) for n in ['01','02','03','04','05','06']]+[('gendai2','03')],
 'gendai2':[('gendai2',n) for n in ['01','02','04','05','06']],
}
s=open(src,encoding='utf-8').read()
m=re.search(r'const DEFAULT_PACKS = (\[[\s\S]*?\n\]);',s); packs=json.loads(m.group(1)); P={p['id']:p for p in packs}
if len(P['kinsei2']['lessons'])!=8: sys.exit('already reordered')
def plain(h): return re.sub(r'<[^>]+>','',re.sub(r'<rt>[^<]*</rt>','',h))
for p in packs:
    for l in p['lessons']: l.setdefault('src',f"{p['id']}-{l['no']}")
old={(p['id'],l['no']):l for p in packs for l in p['lessons']}
oldtxt={pid:{l['no']:plain(l['html']+l.get('colHtml','')) for l in P[pid]['lessons']} for pid in PLAN}
oldquiz={pid:list(P[pid]['quiz']) for pid in PLAN}
newlessons={}
for pid,seq in PLAN.items():
    newlessons[pid]=[]
    for i,(sp,sn) in enumerate(seq,1):
        l=dict(old[(sp,sn)]); l['no']=f'{i:02d}'; newlessons[pid].append(((sp,sn),l))
where={k:(pid,l['no']) for pid,v in newlessons.items() for k,l in v}
idmax={pid:max([q['id'] for q in oldquiz[pid]]+[P[pid].get('idMax',0)]) for pid in PLAN}
moves=[]
newquiz={pid:[] for pid in PLAN}
for sp in PLAN:
    for q in oldquiz[sp]:
        tp,tn=where[(sp,q['link'])]; q=dict(q); q['link']=tn
        newquiz[tp].append(q if tp==sp else ('MOVE',sp,q))
for pid in PLAN:
    res=[]
    for q in newquiz[pid]:
        if isinstance(q,tuple):
            _,sp,q=q; idmax[pid]+=1; moves.append([sp,q['id'],pid,idmax[pid]]); q['id']=idmax[pid]
        res.append(q)
    P[pid]['quiz']=res; P[pid]['lessons']=[l for _,l in newlessons[pid]]; P[pid]['idMax']=idmax[pid]
# 移した授業についていた年表・用語・語呂・論述・穴埋め
def move_aux(sp,nos,tp):
    mv=''.join(oldtxt[sp][n] for n in nos); rest=''.join(t for n,t in oldtxt[sp].items() if n not in nos)
    def goes(text): return bool(text) and text in mv and text not in rest
    a,b=P[sp],P[tp]
    for key,f in (('terms',lambda t:t['term']),('goro',lambda g:g['ans'].split('＝')[0].split('（')[0].strip())):
        keep=[]
        for x in a[key]: (b[key].append(x) if goes(f(x)) else keep.append(x))
        a[key]=keep
    keep=[]
    for t in a['timeline']:
        kws=re.findall(r'[一-鿿々ァ-ヶー]{2,}',t['t'])
        (b['timeline'].append(t) if kws and any(goes(k) for k in kws) and not any(k in rest for k in kws) else keep.append(t))
    a['timeline']=keep
    b['timeline'].sort(key=lambda t:int(re.match(r'\d+',t['y']).group(0)) if re.match(r'\d+',t['y']) else 0)
move_aux('kinsei2',['01','02'],'kinsei'); move_aux('gendai2',['03'],'gendai')
for key,test in (('cloze',lambda c:c['title'].startswith('桃山')),('ronjutsu',lambda r:'桃山' in r['q'])):
    keep=[]
    for x in P['kinsei2'][key]: (P['kinsei'][key].append(x) if test(x) else keep.append(x))
    P['kinsei2'][key]=keep
P['kinsei'].update(title='近世①（織豊政権と桃山文化）',subtitle=P['kinsei']['subtitle']+'・桃山文化')
P['kinsei2'].update(title='近世②（江戸幕府の成立）',subtitle=P['kinsei2']['subtitle'].replace('桃山文化・','').replace('・桃山文化',''))
P['gendai']['subtitle']=P['gendai'].get('subtitle','')+'・占領期の文化'
# 近世⑧と⑨：寛政〜天保（kinsei9）を先に
P['kinsei9']['order'],P['kinsei8']['order']=3.7,3.8
s=s[:m.start(1)]+json.dumps(packs,ensure_ascii=False,indent=1)+s[m.end(1):]
s=re.sub(r'const QMOVES=(\[[^;]*\]);',lambda mm:'const QMOVES='+json.dumps(json.loads(mm.group(1))+moves)+';',s)
open(out,'w',encoding='utf-8').write(s)
print('moved quiz',len(moves))
for pid in PLAN: print(pid,[l['src'] for l in P[pid]['lessons']])
