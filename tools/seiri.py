# 「整理する」のセットをつくり、授業とのあいだに行き来のボタンを置く（2026-11-10 ユーザーの指示）。post.py の最後で毎回かかる（何度かけても同じ結果）。
#  1) seiri_data.py のカードから、セット「テーマ史：整理する」（id=seiri）をつくる（毎回つくり直す。一問一答はなし）。
#  2) 「ここで思い出そう」の箱に、その授業へ飛ぶボタンを足す。箱の中の（近代⑧）（授業03）などから行き先のセットを決め、
#     箱の文にいちばん多く出てくる色付きの語をもつ授業を選ぶ。その語が飛んだ先で光る。
#  3) 授業に「整理する」のカードの語（terms）が need 個以上あれば、授業の終わりにそのカードへ飛ぶボタンを足す。
#  4) カードのほうにも、いちばん関係の深い授業へ飛ぶボタンを足す。
# ボタンは <button class='jump' data-p=セットid data-s=授業のsrc data-m=光らせる語／カードid>。動かすのは app/source.html の .jump の処理。
import re,html
from seiri_data import G
PID='seiri'
def esc(s): return html.escape(s,quote=False)
def ink(s): return re.sub(r'《([^》]+)》',r"<b class='k'>\1</b>",esc(s))
def chain(items,cls):
    out=[]
    for x in items:
        if x[:1] in '↓↑→←': out.append(f"<span class='ar'>{ink(x)}</span>")
        else: out.append(f"<span class='bx'>{ink(x)}</span>")
    return f"<div class='{cls}'>"+''.join(out)+"</div>"
def block(b):
    k=b[0]
    if k=='v': return chain(b[1],'vch')
    if k=='h': return chain(b[1],'hch')
    if k=='t':
        h=''.join(f"<th>{ink(x)}</th>" for x in b[1])
        r=''.join('<tr>'+''.join(f"<td>{ink(c)}</td>" for c in row)+'</tr>' for row in b[2])
        return f"<div class='tw'><table><tr>{h}</tr>{r}</table></div>"
    if k=='tree': return f"<div class='rt'>{ink(b[1])}</div><div class='tr'>"+''.join(f"<div>{ink(x)}</div>" for x in b[2])+"</div>"
    if k=='p': return f"<p class='pp'>{ink(b[1])}</p>"
    if k=='s': return f"<p class='sm'>{ink(b[1])}</p>"
    if k=='lb': return f"<p class='lbp'><span class='lb'>{esc(b[1])}</span>{ink(b[2])}</p>"
    raise ValueError(k)
def plain(h): return re.sub(r'<[^>]+>','',re.sub(r'<rt>[^<]*</rt>','',h or ''))
def kwset(l):
    h=re.sub(r'<rt>[^<]*</rt>','',l.get('html') or '')
    return set(re.sub(r'<[^>]+>','',x) for x in re.findall(r"<span class='kw'>(.*?)</span>",h))
JUMP=re.compile(r"<button class='jump'[^>]*>.*?</button>")
SL=re.compile(r"<!--seiri-->[\s\S]*?<!--/seiri-->")
def btn(pid,src,mark,label): return f"<button class='jump' data-p='{pid}' data-s='{src}' data-m='{html.escape(mark,quote=True)}'>{esc(label)}</button>"
def apply(packs):
    packs[:]=[p for p in packs if p['id']!=PID]
    era=[p for p in packs]
    short=lambda p: re.sub(r'（.*$','',p['title'])
    by_label={short(p):p for p in packs}
    for p in packs:
        for l in p['lessons']: l.setdefault('src',f"{p['id']}-{l['no']}")
    KW={l['src']:kwset(l) for p in packs for l in p['lessons']}
    # --- 3) 授業 → カード
    cards=[(g,c) for g in G for c in g['cards']]
    links={}  # src -> [(card,gno)]
    best={}   # card id -> (score, pid, src, mark)
    for p in packs:
        for l in p['lessons']:
            for g,c in cards:
                hit=[t for t in c['terms'] if t in KW[l['src']]]
                if len(hit)>=c['need']: links.setdefault(l['src'],[]).append((c,g['no']))
                if hit and not p['id'].startswith('theme_'):
                    sc=len(hit)
                    if sc>best.get(c['id'],(0,))[0]: best[c['id']]=(sc,p['id'],l['src'],max(hit,key=len),short(p)+' '+(l.get('navTitle') or ''))
    n_link=0
    for p in packs:
        for l in p['lessons']:
            h=SL.sub('',l['html'])
            ls=links.get(l['src'])
            if ls:
                box="<!--seiri--><div class='seiri-link'><span class='bx-tag'>整理する</span>"+''.join(btn(PID,f"{PID}-{gno}",c['id'],c['title']+' →') for c,gno in ls[:4])+"</div><!--/seiri-->"
                k=h.rfind("<!--flow--><div class='flow next'")
                h=h[:k]+box+h[k:] if k>=0 else h+box
                n_link+=1
            l['html']=h
    # --- 2) 「ここで思い出そう」→ 授業
    n_r=0
    def fix_recall(p,l):
        nonlocal n_r
        def one(m):
            nonlocal n_r
            inner=JUMP.sub('',m.group(1)); txt=plain(inner)
            targets=[]
            for lab in re.findall(r'[（(]((?:古代|中世|近世|近代|現代)[①-⑩])',txt):
                if lab in by_label and by_label[lab] not in targets: targets.append(by_label[lab])
            for th in re.findall(r'テーマ史：([^）)、・]+)',txt):
                for q in packs:
                    if q['title'].startswith('テーマ史：'+th[:3]) and q not in targets: targets.append(q)
            same=re.findall(r'授業(\d\d)',txt)
            bs=[]
            for q in targets:
                bestl=None
                for x in q['lessons']:
                    hit=[t for t in KW[x['src']] if len(t)>=2 and t in txt]
                    sc=sum(len(t) for t in hit)
                    if hit and (bestl is None or sc>bestl[0]): bestl=(sc,x,max(hit,key=len))
                if bestl: bs.append(btn(q['id'],bestl[1]['src'],bestl[2],f"{short(q)}「{bestl[1].get('navTitle') or ''}」を開く →"))
            for no in same:
                x=[y for y in p['lessons'] if y['src'].endswith('-'+no) and y['src'].split('-')[0] in (p['id'],l['src'].split('-')[0])]
                if x:
                    hit=[t for t in KW[x[0]['src']] if len(t)>=2 and t in txt]
                    bs.append(btn(p['id'],x[0]['src'],max(hit,key=len) if hit else '',f"授業{no}「{x[0].get('navTitle') or ''}」を開く →"))
            if bs: n_r+=1
            return "<div class='recall'>"+inner+''.join(bs[:3])+"</div>"
        l['html']=re.sub(r"<div class='recall'>([\s\S]*?)</div>",one,l['html'])
    for p in packs:
        for l in p['lessons']: fix_recall(p,l)
    # --- 1) セットをつくる
    lessons=[]
    for g in G:
        hs=["<p class='seiri-intro'>まぎらわしい所を、見てわかる形にまとめたカード。色の文字が大事な語。</p>"]
        for c in g['cards']:
            go=''
            if c['id'] in best:
                _,pid,src,mark,lab=best[c['id']]
                go="<div class='mm-go'>"+btn(pid,src,mark,'授業で読む：'+lab+' →')+"</div>"
            hs.append(f"<div class='mm {c['color']}' data-card='{c['id']}'><h4>{esc(c['title'])}</h4>"+''.join(block(b) for b in c['blocks'])+go+"</div>")
        lessons.append(dict(no=g['no'],navTitle=g['nav'],title=g['title'],theme=g['theme'],html=''.join(hs),src=f"{PID}-{g['no']}"))
    pack=dict(id=PID,title='テーマ史：整理する（まぎらわしい所のまとめ）',subtitle='似た語・似た制度・人物のしたことを、付箋のように見てわかる形で',order=9.9,
              range='時代をまたいで、わかりにくい所だけを集めた。授業の「整理する」ボタンからも飛べる。',timeline=[],lessons=lessons,quiz=[],terms=[],goro=[],ronjutsu=[],cloze=None)
    i=next((k for k,p in enumerate(packs) if p.get('order',99)>9.9),len(packs))
    packs.insert(i,pack)
    return dict(cards=len(cards),lesson_links=n_link,recall_buttons=n_r,cards_with_lesson=len(best))
