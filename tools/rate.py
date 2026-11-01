# 一問一答の難易度 d（1〜3）と重要度 i（3〜5）を、授業の作りから付け直す。
#   python3 rate.py ../app/source.html ../app/source.html bakumatsu kindai ...
# i：まとめ（point）と「入試ではこう出る」の両方に出る＝5、どちらか一方に出る＝4、それ以外＝3
# d：「難関＋」の囲み（教科書外）だけに出る＝3、i=5＝1、それ以外＝2。問題文が年・数などの数字を問うものは1段上げる。
#   （「まとめにも入試欄にも出ない語＝難しい」とすると基本語まで3になるので、そうしない）
import json,re,sys
src,out=sys.argv[1],sys.argv[2]; ids=sys.argv[3:]
s=open(src,encoding='utf-8').read()
m=re.search(r'const DEFAULT_PACKS = (\[[\s\S]*?\n\]);',s); packs=json.loads(m.group(1))
# 入試で最も問われる語（自動判定がずれたときの補正）
CORE=set('ペリー 日米和親条約 井伊直弼 日米修好通商条約 領事裁判権 関税自主権 安政の大獄 桜田門外の変 薩長連合 大政奉還 王政復古の大号令 戊辰戦争 五箇条の誓文 '
 '版籍奉還 廃藩置県 徴兵令 地租改正 地租改正条例 学制 岩倉使節団 明治六年の政変 民撰議院設立の建白書 西南戦争 国会開設の勅諭 明治十四年の政変 自由党 立憲改進党 松方正義 秩父事件 '
 '大日本帝国憲法 内閣制度 教育勅語 超然主義 民党 陸奥宗光 日英通商航海条約 小村寿太郎 下関条約 三国干渉 立憲政友会 日英同盟 ポーツマス条約 韓国併合 統監府 桂園時代 '
 '八幡製鉄所 寄生地主 工場法 足尾鉱毒事件 治安警察法'.split())
def plain(h): return re.sub(r'<[^>]+>','',re.sub(r'<rt>[^<]*</rt>','',h))
for p in packs:
    if p['id'] not in ids: continue
    L={l['no']:l for l in p['lessons']}
    for q in p['quiz']:
        l=L.get(q.get('link'));
        if not l: continue
        mk=q.get('mark') or q['a']; h=l['html']
        pts=re.findall(r"<div class='point'>([\s\S]*?)</div>",h); ny=re.findall(r"<div class='nyushi'>([\s\S]*?)</div>",h)
        pb=any(mk in plain(b) for x in pts for b in re.findall(r'<b>([\s\S]*?)</b>',x))
        if not pts:  # まとめの枠がない古い授業は、本文の太字で代用する
            pb=any(mk in plain(b) for b in re.findall(r'<b>([\s\S]*?)</b>',h))
        pp=any(mk in plain(x) for x in pts); nn=any(mk in plain(x) for x in ny)
        deeps=re.findall(r"<div class='deep'>[\s\S]*?</div>",h)
        main=h
        for x in deeps: main=main.replace(x,'')
        inl=mk in plain(main)  # 難関＋の囲みを除いた本文に出るか
        i=5 if ((pb or pp) and nn) else 4 if (pb or nn or pp) else 3
        if not inl: d,i=3,3
        else:
            d=1 if i==5 else 2
            if re.search(r'何年|何%|何円|何人|何番目|いくら|何か所|何次',q['q']): d=min(3,d+1)
        if mk in CORE: d,i=1,5
        q['d'],q['i']=d,i
    import collections
    print(p['id'],'d',dict(sorted(collections.Counter(q['d'] for q in p['quiz']).items())),'i',dict(sorted(collections.Counter(q['i'] for q in p['quiz']).items())))
s=s[:m.start(1)]+json.dumps(packs,ensure_ascii=False,indent=1)+s[m.end(1):]
open(out,'w',encoding='utf-8').write(s)
