# ふりがなの誤りをまとめて直す（何度かけても同じ結果になる）。
#   python3 fix_ruby.py ../app/source.html ../app/source.html
# 1) 2文字以下の語のルビが、前後の漢字とつながって別の熟語の一部になっているもの（左[大臣]、[結]果、日[本地]図、函[館] など）は外す
# 2) 「名」「結」は意味が変わりやすいので、荘園の「名（みょう）」・結（ゆい）の用語として単独で出るとき以外は外す
# 3) 読みそのものの誤り・表記ゆれを直す
import re,sys
K=re.compile(r'[一-鿿々〆ヶ]')
RUBY=re.compile(r'<ruby>([^<]+)<rt>([^<]*)</rt></ruby>')
READ={
 ('三世一身法','さんぜいっしんのほう'):'さんぜいっしんほう',
 ('二・二六事件','に・にろくじけん'):'にいにいろくじけん',
 ('三・一五事件','さん・いちごじけん'):'さんいちごじけん',
 ('五・一五事件','ご・いちごじけん'):'ごいちごじけん',
 ('五・三〇事件','ご・さんまるじけん'):'ごさんれいじけん',
 ('五・三〇事件','ごさんじけん'):'ごさんれいじけん',
 ('四・一六事件','し・いちろくじけん'):'しいちろくじけん',
 ('七・七禁令','しち・しちきんれい'):'しちしちきんれい',
 ('救世観音','くぜかんのん'):'くせかんのん',
 ('柳子新論','りゅうしししんろん'):'りゅうししんろん',
 ('生きてゐる兵隊','いきてゐるへいたい'):'いきているへいたい',
 ('塘沽停戦協定','タンクーていせんきょうてい'):'たんくーていせんきょうてい',
 ('寧波','ニンポー'):'にんぽー',
 ('寧波の乱','ニンポーのらん'):'にんぽーのらん',
 ('李承晩','イスンマン'):'りしょうばん',
 ('板門店','パンムンジョム'):'ぱんむんじょむ',
 ('金日成','キムイルソン'):'きむいるそん',
 ('青島','チンタオ'):'ちんたお',
 ('仁川','インチョン'):'いんちょん',
 ('坦庵','たんなん'):'たんあん',
 ('質地騒動','しちちそうどう'):'しっちそうどう',
 ('結城氏新法度','ゆうきしにいはっと'):'ゆうきししんはっと',
}
# 読みが2通りまざっているものは、山川の教科書の読みにそろえる
UNI={'高向玄理':'たかむこのげんり','国博士':'くにのはかせ','班田収授法':'はんでんしゅうじゅほう','小野道風':'おののとうふう',
 '草木灰':'そうもくかい','吾妻鏡':'あずまかがみ','叡尊':'えいそん','北山十八間戸':'きたやまじゅうはっけんど',
 '金沢実時':'かねさわさねとき','金沢文庫':'かねさわぶんこ','二条河原落書':'にじょうがわらのらくしょ','棟別銭':'むなべちせん',
 '畠山義就':'はたけやまよしなり','一条兼良':'いちじょうかねよし','立花':'りっか','聚楽第':'じゅらくてい',
 '高田屋嘉兵衛':'たかたやかへえ','大日本帝国憲法':'だいにほんていこくけんぽう','太政大臣':'だいじょうだいじん',
 '白村江の戦い':'はくすきのえのたたかい'}
def prev_char(s,i):
    j=i
    while j>0 and s[j-1]=='>':
        k=s.rfind('<',0,j-1)
        if k<0: break
        tag=s[k:j].lower()
        if tag.startswith('<br') or tag.startswith('<p') or tag.startswith('</p') or tag.startswith('<div') or tag.startswith('</div'): return ''
        j=k
    return s[j-1] if j>0 else ''
def next_char(s,i):
    j=i
    while j<len(s) and s[j]=='<':
        k=s.find('>',j)
        if k<0: break
        tag=s[j:k+1].lower()
        if tag.startswith('<br') or tag.startswith('<p') or tag.startswith('</p') or tag.startswith('<div') or tag.startswith('</div'): return ''
        j=k+1
    return s[j] if j<len(s) else ''
def fix(s):
    out=[];last=0;n_un=0;n_rd=0
    for m in RUBY.finditer(s):
        w,r=m.group(1),m.group(2)
        a=prev_char(s,m.start()); b=next_char(s,m.end())
        rep=m.group(0)
        unwrap=False
        if len(w)<=2 and (K.match(a or ' ') or K.match(b or ' ')): unwrap=True
        if not K.search(w): unwrap=True  # カタカナ・ひらがなだけの語にふりがなはいらない（2026-11-13）
        if w=='名' and not (b in ('','<') or s[m.end():m.end()+3].startswith('を請')): unwrap=True
        if w=='結' and b not in ('','<','・','、','）','(','（',')'): unwrap=True
        if unwrap: rep=w; n_un+=1
        elif (w,r) in READ: rep=f'<ruby>{w}<rt>{READ[(w,r)]}</rt></ruby>'; n_rd+=1
        elif w in UNI and UNI[w]!=r: rep=f'<ruby>{w}<rt>{UNI[w]}</rt></ruby>'; n_rd+=1
        else:
            r2=r.replace('う゛','ゔ')
            if r2!=r: rep=f'<ruby>{w}<rt>{r2}</rt></ruby>'; n_rd+=1
        out.append(s[last:m.start()]); out.append(rep); last=m.end()
    out.append(s[last:]); s=''.join(out)
    # 文脈で読みが変わるもの
    ctx=[("<ruby>上野<rt>こうずけ</rt></ruby>・浅草","<ruby>上野<rt>うえの</rt></ruby>・浅草"),
         ("<ruby>上野<rt>こうずけ</rt></ruby>忍ヶ岡","<ruby>上野<rt>うえの</rt></ruby>忍ヶ岡"),
         ("金田城","<ruby>金田城<rt>かねたのき</rt></ruby>"),
         # 長い語の一部だけにふりがながついていたもの（2026-11-13）
         ("後<ruby>鳥羽天皇<rt>とばてんのう</rt></ruby>","<ruby>後鳥羽天皇<rt>ごとばてんのう</rt></ruby>"),
         ("<ruby>六波羅<rt>ろくはら</rt></ruby>蜜寺","<ruby>六波羅蜜寺<rt>ろくはらみつじ</rt></ruby>"),
         ("<ruby>延喜格<rt>えんぎきゃく</rt></ruby>式","<ruby>延喜格式<rt>えんぎきゃくしき</rt></ruby>"),
         ("皇朝<ruby>十二銭<rt>じゅうにせん</rt></ruby>","<ruby>皇朝十二銭<rt>こうちょうじゅうにせん</rt></ruby>")]
    for a,b in ctx:
        if a=="金田城": s=re.sub(r'(?<!<ruby>)金田城',b,s)  # ルビなしの「金田城」にだけ付ける
        else: s=s.replace(a,b)
    # 長い語の一部だけにふりがなと色がついたものを、長い語ひとつにまとめる（2026-11-13）
    for pre,w,suf,nw,rd in MERGE:
        pat=re.escape(pre)+r"(?:<span class='kw'>)?<ruby>"+re.escape(w)+r"<rt>[^<]*</rt></ruby>(?:</span>)?"+re.escape(suf)
        s=re.sub(pat,f"<span class='kw'><ruby>{nw}<rt>{rd}</rt></ruby></span>",s)
    # 別の語の一部に色（kw）がついているものは色をはずす（2026-11-13 ユーザーの指摘「色字の判定がおかしい」）
    for pre,w,suf in FRAG:
        pat=re.escape(pre)+r"((?:</span>|</ruby>|<rt>[^<]*</rt>)*)<span class='kw'>(?:<ruby>)?"+re.escape(w)+r"(?:<rt>[^<]*</rt></ruby>)?</span>(?="+re.escape(suf)+")"
        s=re.sub(pat,lambda mm: pre+mm.group(1)+w,s)
    return s,n_un,n_rd
MERGE=[('後','鳥羽天皇','','後鳥羽天皇','ごとばてんのう'),('','六波羅','蜜寺','六波羅蜜寺','ろくはらみつじ'),('皇朝','十二銭','','皇朝十二銭','こうちょうじゅうにせん')]
# (前の字, 色がついた語, 後の字)：この並びのときは別の語の一部なので色をはずす
FRAG=[('資','本家',''),('韓','国人',''),('帝','国人','造'),('自','民党',''),('','野田','佳彦'),('佐','渡島',''),
 ('第','2段','階'),('','北朝','鮮'),('','図書','館'),('','立花','隆'),('','山口','判事'),('','吉野','源三郎'),
 ('','上洛','殿'),('','茶道','具'),('直','訴状',''),('','山田','美妙'),('','笠懸','村'),('主','義政','権'),
 ('皇','親政','治'),('','中宮','寺'),('','石井','部隊'),('','公事','方御定書'),('','延喜格','式'),
 ('一遍','上人',''),('空也','上人',''),('重源','上人','')]
if __name__=='__main__':
    src,dst=sys.argv[1:3]
    s=open(src,encoding='utf-8').read()
    U=R=0
    while True:
        s2,u,r=fix(s); U+=u; R+=r
        if s2==s: break
        s=s2
    open(dst,'w',encoding='utf-8').write(s)
    print('unwrapped',U,'reread',R)

# 授業ごとに読みを決める語（同じ字で読みが変わるもの）。post.py が授業ごとにかける（2026-11-13）
#   (セットid, 授業no) : {語: 正しい読み}
LESSON_RD={
 ('kodai5','01'):{'源信':'みなもとのまこと'},          # 応天門の変の左大臣（僧の源信＝げんしん とは別人）
 ('chusei3','01'):{'時宗':'ときむね'}, ('chusei3','02'):{'時宗':'ときむね'},   # 北条時宗（一遍の時宗＝じしゅう とは別）
 ('kinsei7','01'):{'名主':'なぬし'}, ('kinsei7','03'):{'名主':'なぬし'},       # 江戸時代の村役人
 ('kinsei8','04'):{'名主':'なぬし'}, ('kinsei10','02'):{'名主':'なぬし'},
 ('theme_tochi','07'):{'名主':'みょうしゅ'},                                   # 荘園の名主
 ('kinsei2','02'):{'大臣':'だいじん'}, ('kinsei9','02'):{'大臣':'だいじん'}, ('theme_kahei','09'):{'大臣':'だいじん'},
}
def fix_lessons(packs):
    n=0
    for p in packs:
        for l in p.get('lessons',[]):
            rd=LESSON_RD.get((p['id'],l.get('no')))
            if not rd: continue
            for k in ('html','colHtml'):
                h=l.get(k) or ''
                for w,r in rd.items():
                    h2=re.sub(r'<ruby>'+re.escape(w)+r'<rt>[^<]*</rt></ruby>',f'<ruby>{w}<rt>{r}</rt></ruby>',h)
                    if h2!=h: n+=1; h=h2
                l[k]=h
    return n
