# 授業の原稿（relesson の txt）から、多すぎる読点をへらす。
#   python3 decomma.py in.txt out.txt        … 書きかえ
#   python3 decomma.py in.txt -              … 数だけ見る
# 2026-11-12 ユーザーの指摘「句読点が多すぎる。文がおかしくなってる」。お手本（現代①〜④）は 100字あたり読点 3.4 個。
# 助詞のすぐあとの読点（「義教が、きいた」）を、文が短いときは取る。並列・日付・接続のことば・節の切れ目の読点は残す。
import re,sys
CONJ=set('そして でも ところが だから しかも ただ ただし いっぽう 一方 そこで じゃあ まず 次に つぎに つまり それでも しかし さらに そのうえ それから すると けっきょく 結局 なのに たとえば 例えば ちなみに では さて もちろん じつは 実は やがて こうして そのあと このあと その後 最後に はじめは 逆に むしろ たしかに なぜなら それに また なお おまけに ところで いや そう はい ほら もし たとえ かりに 一つ 二つ 三つ 一つめ 二つめ 三つめ 四つめ まして だが けれど けれども それなのに だからこそ とはいえ それで こんどは 今度は'.split())
ADV=set('なんで すぐ もう まだ みな いま ここで そこへ そこに こう どう ずっと やっと たくさん わざわざ とつぜん ついに やはり やっぱり かなり とても ほとんど すべて ぜんぶ いつも はじめ はじめて 初めて あとは いったん しばらく もともと そのまま このまま たがいに いっしょに ひとりで ひと目で どんどん じわじわ だんだん 次々に つぎつぎに さっそく いっせいに いきなり おそらく たぶん きっと かならず 必ず ようやく とうとう あっさり しぶしぶ ぴたりと がらりと'.split())
HIRA=re.compile(r'[ぁ-ゖー]')
def plain(x): return re.sub(r'[《》]','',x)
def keep(seg,run,nxt):
    """seg=直前の読点からここまで, run=最後に残した読点からここまで, nxt=次の読点・句点まで。True=読点を残す"""
    s=plain(seg).strip(); r=len(plain(run)); n=len(plain(nxt))
    if not s: return True
    last=s[-1]
    core=re.sub(r'^[「『（(]+','',s)
    if core in CONJ: return True
    if not HIRA.match(last): return True                      # 漢字・カタカナ・数字・かっこで終わる＝並列・同格・日付
    # ここから下は「取ってよい読点」だけを選ぶ。当てはまらなければ残す。
    if re.search(r'(まず|まだ|もう|すぐ|みな|ずっと|やっと|とても|かなり|ほぼ|たくさん|いちばん)$',s) and len(s)<=9: return False
    if re.search(r'(ても|でも|のに|ように|ために|うちに|かわりに|ときに|まえに|ほどに|たびに)$',s): return True
    if re.search(r'(た|だ|る|ない|ます|です|よう)が$',s): return True      # 逆接の「が」
    if re.search(r'[るいたくだ](と|から|し|けど|ので)$',s): return True   # 条件・理由
    if re.search(r'(んで|いで|って)$',s): return True                  # て形
    if re.search(r'(を|へ|の|まで|より)$',s): return r>26 and n>=10
    if re.search(r'(に|も)$',s): return r>20 and n>=10
    if re.search(r'(が|は|で|と|から)$',s): return r>=12 and n>=10
    if core in ADV: return False
    if re.search(r'[たるう]$',s) and n<=6 and re.match(r'[《一-龥々ァ-ヶ]',nxt.strip() or 'あ'): return False   # 連体修飾（つとめた、義円）
    return True
def fix_sentence(t):
    parts=t.split('、')
    if len(parts)==1: return t
    out=parts[0]; run=parts[0]
    for i in range(1,len(parts)):
        seg=parts[i-1]; nxt=parts[i]
        if keep(seg,run,nxt): out+='、'+nxt; run=nxt
        else: out+=nxt; run+=nxt
    return out
def fix_text(t):
    # 句点・かぎかっこ・かっこで文を切ってから処理
    toks=re.split(r'([。？！?!「」『』（）])',t)
    return ''.join(x if re.fullmatch(r'[。？！?!「」『』（）]',x) else fix_sentence(x) for x in toks)
def fix_file(src):
    out=[]
    for ln in src.split('\n'):
        if ln.startswith('P: '): out.append('P: '+fix_text(ln[3:]))
        elif ln.startswith('Y: ') and ' | ' in ln:
            h,b=ln[3:].split(' | ',1); out.append('Y: '+h+' | '+fix_text(b))
        else: out.append(ln)
    return '\n'.join(out)
if __name__=='__main__':
    s=open(sys.argv[1],encoding='utf-8').read(); o=fix_file(s)
    body=lambda x:''.join(l[3:] for l in x.split('\n') if l[:3] in('P: ','Y: '))
    a,b=body(s),body(o)
    print('%s 読点/100字 %.1f → %.1f'%(sys.argv[1].split('/')[-1],100*a.count('、')/len(a),100*b.count('、')/len(b)))
    if sys.argv[2]!='-': open(sys.argv[2],'w',encoding='utf-8').write(o)
