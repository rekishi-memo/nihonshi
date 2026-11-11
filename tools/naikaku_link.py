"""通史の授業に入っている内閣の表（ktab）を、テーマ史：内閣史への案内に置きかえる。
   2026-11-11 ユーザーの指示「これは内閣史にあるから飛べるようにしとけば十分」。
   post.py から毎回呼ぶ（rewrite_lessons が表を入れ直しても、ここでまた案内に変わる）。
   案内は「▶」で始まる段落なので、アプリが枠をつけ、「テーマ史：内閣史 授業NN」をタップで飛べるボタンにする。"""
import re
OPEN="<div class='viz vtab ktab'>"
def _block_end(h,i):
    # i は OPEN の位置。対応する </div> の直後の位置を返す
    depth=0
    for m in re.finditer(r'<div\b|</div>',h[i:]):
        depth+= 1 if m.group(0)!='</div>' else -1
        if depth==0: return i+m.end()
    return -1
_txt=lambda x: re.sub(r'<rt>.*?</rt>|<[^>]+>','',x)
def apply(packs):
    th=[p for p in packs if p['id']=='theme_naikaku']
    if not th: return 0
    plain=[(l['no'],_txt(l['html'])) for l in th[0]['lessons']]
    n=0
    for p in packs:
        if p['id'].startswith('theme_'): continue   # テーマ史の表（内閣史・為政者の表）はそのまま
        for l in p['lessons']:
            h=l['html']
            while OPEN in h:
                i=h.index(OPEN); j=_block_end(h,i)
                if j<0: break
                blk=h[i:j]
                cap=_txt(re.search(r"<div class='viz-cap'>(.*?)</div>",blk).group(1)).replace('表 ── ','').strip()
                names=[_txt(x).strip() for x in re.findall(r"<div class='vr'><span>(.*?)<span class='ky'>",blk)]
                tgt=None
                for no,t in plain:
                    if names and names[0] in t: tgt=no; break
                if tgt is None: tgt=plain[0][0]
                rng=names[0] if len(names)==1 else (names[0]+'〜'+names[-1]) if names else cap
                link=("<p class='klink'>▶ <b>内閣の表は「内閣史」にまとめた。</b>"+cap+"（"+rng+"）の、したこと・おもな閣僚・倒れた理由は、"
                      "テーマ史：内閣史 授業"+tgt+" で見られる。金色の点線の文字をタップすると飛べて、「← もとの授業にもどる」でここに帰れる。</p>")
                h=h[:i]+link+h[j:]; n+=1
            l['html']=h
    return n
