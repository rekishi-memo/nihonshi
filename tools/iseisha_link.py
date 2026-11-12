"""通史の授業の終わりに、テーマ史：為政者の表への案内を1行足す（post.py から毎回呼ぶ。何度呼んでも1つだけ）。
   2026-11-11 ユーザーの指示「為政者たちの表をテーマ史に作って、授業とつなぐ」。"""
import re
MAP={'kodai':('01','このころの倭の王（卑弥呼・倭の五王など）'),'kodai2':('02','天皇と、そのときの実力者'),'kodai3':('02','天皇と、そのときの実力者'),
 'kodai4':('03','天皇と藤原氏（摂政・関白）'),'kodai5':('03','天皇と藤原氏（摂政・関白）'),
 'chusei':('04','天皇と、院政をした上皇'),'chusei2':('05','将軍と執権'),'chusei3':('05','将軍と執権'),
 'chusei4':('06','室町幕府の将軍'),'chusei5':('06','室町幕府の将軍'),'chusei6':('06','室町幕府の将軍'),
 'kinsei':('07','信長と秀吉の年表'),
 'kinsei2':('08','将軍と、政治を動かした人'),'kinsei3':('08','将軍と、政治を動かした人'),'kinsei4':('08','将軍と、政治を動かした人'),'kinsei5':('08','将軍と、政治を動かした人'),
 'kinsei6':('08','将軍と、政治を動かした人'),'kinsei7':('08','将軍と、政治を動かした人'),'kinsei8':('08','将軍と、政治を動かした人'),'kinsei9':('08','将軍と、政治を動かした人'),
 'kinsei10':('08','将軍と、政治を動かした人'),'bakumatsu':('08','将軍と、政治を動かした人')}
PAT=re.compile(r"<p class='ilink'>.*?</p>")
def apply(packs):
    if not any(p['id']=='theme_iseisha' for p in packs): return 0
    n=0
    for p in packs:
        if p['id'] not in MAP: continue
        no,what=MAP[p['id']]
        for l in p['lessons']:
            h=PAT.sub('',l['html'])
            if p['id']=='kodai' and not re.search('卑弥呼|倭の五王|奴国|ヤマト政権|大王',h): l['html']=h; continue   # 旧石器・縄文には王がいない
            if p['id']=='kodai2' and l['no']=='01': no,what='01','継体・欽明天皇と、そのときの実力者'
            elif p['id']=='kodai2': no,what=MAP['kodai2']
            link=("<p class='ilink'>▶ <b>"+what+"を、表で見る。</b>テーマ史：為政者の表 授業"+no+" へ（金色の点線の文字をタップすると飛べる）。</p>")
            k=h.find("<div class='nyushi'>")
            h=(h[:k]+link+h[k:]) if k>=0 else h+link
            l['html']=h; n+=1
    return n
