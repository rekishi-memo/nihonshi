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
 ('五・三〇事件','ご・さんまるじけん'):'ごさんじけん',
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
         ("金田城","<ruby>金田城<rt>かねたのき</rt></ruby>")]
    for a,b in ctx:
        if a=="金田城": s=re.sub(r'(?<!<ruby>)金田城',b,s)  # ルビなしの「金田城」にだけ付ける
        else: s=s.replace(a,b)
    return s,n_un,n_rd
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
