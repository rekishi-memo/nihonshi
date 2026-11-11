"""通史の授業の終わりに、テーマ史：為政者の表への案内を1行足す（post.py から毎回呼ぶ。何度呼んでも1つだけ）。
   2026-11-11 ユーザーの指示「為政者たちの表をテーマ史に作って、授業とつなぐ」。"""
import re
MAP={'kodai':('01','天皇と、そのときの実力者'),'kodai2':('01','天皇と、そのときの実力者'),'kodai3':('01','天皇と、そのときの実力者'),
 'kodai4':('02','天皇と藤原氏（摂政・関白）'),'kodai5':('02','天皇と藤原氏（摂政・関白）'),
 'chusei':('03','天皇と、院政をした上皇'),'chusei2':('04','将軍と執権'),'chusei3':('04','将軍と執権'),
 'chusei4':('05','室町幕府の将軍'),'chusei5':('05','室町幕府の将軍'),'chusei6':('05','室町幕府の将軍'),
 'kinsei':('06','信長と秀吉の年表'),
 'kinsei2':('07','将軍と、政治を動かした人'),'kinsei3':('07','将軍と、政治を動かした人'),'kinsei4':('07','将軍と、政治を動かした人'),'kinsei5':('07','将軍と、政治を動かした人'),
 'kinsei6':('07','将軍と、政治を動かした人'),'kinsei7':('07','将軍と、政治を動かした人'),'kinsei8':('07','将軍と、政治を動かした人'),'kinsei9':('07','将軍と、政治を動かした人'),
 'kinsei10':('07','将軍と、政治を動かした人'),'bakumatsu':('07','将軍と、政治を動かした人')}
PAT=re.compile(r"<p class='ilink'>.*?</p>")
def apply(packs):
    if not any(p['id']=='theme_iseisha' for p in packs): return 0
    n=0
    for p in packs:
        if p['id'] not in MAP: continue
        no,what=MAP[p['id']]
        link=("<p class='ilink'>▶ <b>"+what+"を、表で見る。</b>テーマ史：為政者の表 授業"+no+" へ（金色の点線の文字をタップすると飛べる）。</p>")
        for l in p['lessons']:
            h=PAT.sub('',l['html'])
            k=h.find("<div class='nyushi'>")
            h=(h[:k]+link+h[k:]) if k>=0 else h+link
            l['html']=h; n+=1
    return n
