# 使い方ガイド（はじめて開いたときに出す。マニュアル形式のスライド）。2026-11-14 ユーザーの指示。
#   python3 patch_guide.py ../app/source.html ../app/source.html   （patch_tts.py のあとに当てる）
# - アプリを開くたびに出す。「今後は表示しない」を押すと出なくなる（localStorage の nihonshi_guide＝"hide"）。
# - 右上の「？」ボタンでいつでも開ける。
# - とくに読み上げと、iPhone で声を変える手順をくわしく書く。
import sys
src,dst=sys.argv[1],sys.argv[2]
s=open(src,encoding='utf-8').read()
if 'id="guide"' in s:
    print('already'); sys.exit(0)

CSS=r'''
  /* 使い方ガイド */
  .titlebar .tb-btns{display:flex;gap:8px;flex:0 0 auto;}
  .ghost.g-q{width:36px;padding:9px 0;font-weight:700;font-size:13px;}
  .guide{position:fixed;inset:0;z-index:80;background:rgba(6,9,16,.86);backdrop-filter:blur(4px);display:none;align-items:center;justify-content:center;padding:16px 12px;}
  .guide.open{display:flex;}
  .g-card{background:var(--card);border:1px solid var(--line);border-radius:20px;width:100%;max-width:440px;max-height:calc(100vh - 32px);max-height:calc(100dvh - 32px);display:flex;flex-direction:column;box-shadow:0 34px 80px -30px #000;overflow:hidden;}
  .g-head{display:flex;align-items:center;justify-content:space-between;padding:14px 16px 6px;}
  .g-step{font-family:var(--gothic);font-size:11.5px;letter-spacing:.12em;color:var(--gold-deep);}
  .g-x{background:transparent;border:1px solid var(--line);color:var(--ash);border-radius:9px;width:32px;height:32px;font-size:15px;cursor:pointer;}
  .g-body{padding:4px 18px 10px;overflow-y:auto;-webkit-overflow-scrolling:touch;flex:1;}
  .g-slide{display:none;}
  .g-slide.on{display:block;animation:gfade .25s ease;}
  @keyframes gfade{from{opacity:0;transform:translateY(6px);}to{opacity:1;transform:none;}}
  .g-ico{font-size:34px;line-height:1;margin:6px 0 8px;}
  .g-slide h3{font-family:var(--mincho);font-weight:800;font-size:20px;color:var(--ivory);margin-bottom:12px;line-height:1.4;}
  .g-list{list-style:none;counter-reset:g;margin:0 0 12px;padding:0;}
  .g-list li{counter-increment:g;position:relative;padding:9px 0 9px 36px;border-bottom:1px solid var(--line-soft);font-size:13.5px;line-height:1.7;color:var(--ivory-dim);}
  .g-list li:last-child{border-bottom:none;}
  .g-list li::before{content:counter(g);position:absolute;left:0;top:9px;width:24px;height:24px;border-radius:50%;background:var(--gold);color:#1a140a;font-family:var(--gothic);font-weight:700;font-size:12.5px;display:flex;align-items:center;justify-content:center;}
  .g-list.dot li{padding-left:20px;}
  .g-list.dot li::before{content:"";width:7px;height:7px;top:18px;left:4px;background:var(--gold-deep);}
  .g-list b{color:var(--ivory);}
  .g-ui{display:inline-flex;align-items:center;gap:4px;font-family:var(--gothic);font-size:12px;font-weight:600;padding:2px 9px;border-radius:999px;border:1px solid var(--gold-deep);color:var(--gold);white-space:nowrap;}
  .g-ui.main{background:var(--gold);color:#1a140a;border-color:var(--gold);}
  .g-ui.sub{border-color:var(--line);color:var(--ivory-dim);font-weight:500;}
  .g-path{display:flex;flex-wrap:wrap;align-items:center;gap:6px;margin:4px 0 12px;padding:11px 12px;background:var(--bg-2);border-radius:12px;font-family:var(--gothic);font-size:12.5px;}
  .g-path span{background:var(--card-2);border:1px solid var(--line);border-radius:8px;padding:4px 9px;color:var(--ivory);}
  .g-path i{font-style:normal;color:var(--ash);}
  .g-note{font-size:12px;line-height:1.75;color:var(--ash);background:var(--bg-2);border-left:2px solid var(--gold-deep);border-radius:0 9px 9px 0;padding:9px 12px;margin:4px 0 10px;}
  .g-colors{display:grid;gap:6px;margin:0 0 12px;font-size:13px;}
  .g-colors div{display:flex;align-items:center;gap:10px;color:var(--ivory-dim);}
  .g-colors em{font-style:normal;min-width:86px;}
  .g-tabs{display:flex;flex-wrap:wrap;gap:6px;margin:0 0 12px;}
  .g-tabs span{font-family:var(--gothic);font-size:12px;padding:5px 11px;border-radius:999px;border:1px solid var(--line);color:var(--ivory-dim);}
  .g-tabs span:first-child{background:var(--gold);color:#1a140a;border-color:var(--gold);}
  .g-foot{padding:10px 16px 14px;border-top:1px solid var(--line-soft);}
  .g-dots{display:flex;justify-content:center;gap:6px;margin-bottom:10px;}
  .g-dots i{width:7px;height:7px;border-radius:50%;background:var(--line);}
  .g-dots i.on{background:var(--gold);width:18px;border-radius:4px;}
  .g-nav{display:flex;gap:8px;}
  .g-nav button{flex:1;font-family:var(--gothic);font-size:13.5px;font-weight:600;padding:11px 0;border-radius:12px;cursor:pointer;border:1px solid var(--line);background:transparent;color:var(--ivory-dim);}
  .g-nav button.g-next{background:var(--gold);border-color:var(--gold);color:#1a140a;}
  .g-nav button:disabled{opacity:.35;}
  .g-hide{display:block;width:100%;margin-top:8px;background:transparent;border:none;color:var(--ash);font-family:var(--gothic);font-size:12px;text-decoration:underline;text-underline-offset:3px;padding:6px;cursor:pointer;}

'''
a="  /* ふりがな：<ruby>を独自の要素に置きかえて"
assert s.count(a)==1; s=s.replace(a,CSS+a)

a='      <button class="ghost" id="dataBtn">⚙ データ</button>\n'
assert s.count(a)==1
s=s.replace(a,'      <div class="tb-btns"><button class="ghost g-q" id="guideBtn" aria-label="使い方">？</button><button class="ghost" id="dataBtn">⚙ データ</button></div>\n')

SL=[
# 1
('📚','ようこそ。このアプリでできること',
 "<div class='g-tabs'><span>授業</span><span>一問一答</span><span>穴埋め</span><span>論述</span><span>用語</span><span>語呂</span><span>人物</span></div>"
 "<ul class='g-list dot'><li><b>授業</b>を読む・<b>声で聞く</b></li><li><b>一問一答</b>と<b>穴埋め</b>で覚えたか確かめる</li><li><b>論述</b>・<b>用語</b>・<b>語呂</b>・<b>人物</b>で整理する</li><li>通史（古代〜現代）と<b>テーマ史</b>のセットがある</li></ul>"
 "<div class='g-note'>次へ進むと、使い方を順に説明します。あとから右上の <span class='g-ui sub'>？</span> ボタンでいつでも開けます。</div>"),
# 2
('🗂','セットとタブの切りかえ',
 "<ol class='g-list'><li>いちばん上の<b>セットの選択</b>で、時代（古代①・中世③…）やテーマ史を選ぶ</li><li>その下の<b>タブ</b>で「授業」「一問一答」などを切りかえる</li><li>授業は<b>番号のチップ</b>（01・02…）で選ぶ。左右にスクロールできる</li><li>授業のいちばん下の <span class='g-ui sub'>次の授業 →</span> で次へ。セットの最後なら次のセットへ進む</li></ol>"),
# 3
('🎨','授業の読み方（色とリンク）',
 "<div class='g-colors'><div><em style='color:var(--gold);font-weight:800'>太い金</em>共テ必修。まずここ</div><div><em style='color:var(--gold);font-weight:600'>金</em>私大頻出</div><div><em style='color:#c7b98f'>うすい色</em>私大で出る細かめの語</div><div><em style='color:#cdb2ff'>紫（下の枠）</em>難関私大。本文では色なし</div></div>"
 "<ol class='g-list'><li><b>金色の点線</b>の「授業06」「中世③」などをタップすると、その授業に飛ぶ。<span class='g-ui sub'>← もとの授業にもどる</span> で帰れる</li><li><b>？</b>のカードはタップすると答えが出る</li><li>下の<b>難関私大</b>の枠の紫の語をタップすると、本文のその場所が光る</li></ol>"),
# 4
('✅','一問一答・今日のぶん・穴埋め',
 "<ol class='g-list'><li><b>今日のぶん</b>：一問一答タブの上の <span class='g-ui'>今日のぶんへ →</span> で、その日の問題（復習＋新しい問題）にとりくむ</li><li>上のボタンで出す問題をしぼれる：<span class='g-ui sub'>共テ必修</span> <span class='g-ui sub'>私大頻出</span> <span class='g-ui sub'>難関私大</span> <span class='g-ui sub'>過去問</span> <span class='g-ui sub'>苦手だけ</span></li><li><span class='g-ui sub'>答えを見る</span> で答えを出し、<span class='g-ui sub'>○ できた</span> か <span class='g-ui sub'>× まちがえた</span> を押す。まちがえた問題は「苦手だけ」や今日のぶんの復習に出てくる</li><li><b>穴埋め</b>は、空欄をタップすると答えが出る</li></ol>"),
# 5
('🔊','授業を声で聞く（読み上げ）',
 "<ol class='g-list'><li>授業の題の下の <span class='g-ui main'>▶ 読み上げ</span> を押す。読んでいる段落が光って、自動でスクロールする</li><li><span class='g-ui main'>⏸ 一時停止</span> → <span class='g-ui main'>▶ つづきから</span>。やめるときは <span class='g-ui'>■ 停止</span></li><li>読んでいる途中で<b>段落をタップ</b>すると、そこから読む</li><li><span class='g-ui sub'>速さ 1倍</span> で 0.8〜1.5倍を選べる</li><li><span class='g-ui sub'>声：Kyoko</span> で声を選べる（声の増やし方は次のページ）</li><li><span class='g-ui sub'>枠も読む</span> をオフにすると、「入試ではこう出る」「まとめ」などの枠をとばす</li></ol>"
 "<div class='g-note'>ふりがなのある語は、ふりがなの読みで読みます（漢字とふりがなを二重には読みません）。<br>画面を消したり、ほかのアプリに切りかえると止まります。もどったら「▶ つづきから」。</div>"),
# 6
('📱','iPhone で声を変える',
 "<p style='font-size:13px;color:var(--ivory-dim);line-height:1.75;margin-bottom:8px'>はじめは標準の声です。<b style='color:var(--ivory)'>高品質の声をダウンロード</b>すると、ずっと自然になります。</p>"
 "<div class='g-path'><span>設定</span><i>›</i><span>アクセシビリティ</span><i>›</i><span>読み上げコンテンツ</span><i>›</i><span>声</span><i>›</i><span>日本語</span></div>"
 "<ol class='g-list'><li>iPhone の<b>「設定」</b>アプリを開く</li><li><b>「アクセシビリティ」</b>→<b>「読み上げコンテンツ」</b>→<b>「声」</b>→<b>「日本語」</b>の順にタップ</li><li>声の名前（<b>Kyoko</b>・<b>Otoya</b> など）をタップし、<b>「拡張」</b>や<b>「プレミアム」</b>と書いてある声の <b>⬇︎</b> を押してダウンロード（Wi-Fi で。数百MBあることがある）</li><li>このアプリを<b>いったん完全に終了</b>して開き直す（画面の下から上にスワイプしてアプリを上に払う）</li><li>授業の <span class='g-ui sub'>声：…</span> を押して、ダウンロードした声（「（拡張）」などが付いた名前）を選ぶ。選ぶと「この声で読みます」と試しに読む</li></ol>"
 "<div class='g-note'>iOS のバージョンによって、項目の名前が少しちがうことがあります。<br>Siri の声は、このアプリからは選べないことが多いです。<br>声のメニューにダウンロードした声が出てこないときは、iPhone を再起動してみてください。</div>"),
# 7
('📶','オフラインと学習記録',
 "<ol class='g-list'><li>Safari で開いて <b>共有ボタン</b> →<b>「ホーム画面に追加」</b>すると、アプリのように使える。ネットがなくても動く</li><li>学習記録は、この iPhone の中に保存される</li><li>機種変更のときは <span class='g-ui sub'>⚙ データ</span> →「記録を書き出す」で保存して、新しい iPhone で読みこむ</li></ol>"
 "<div class='g-note'>この説明は、右上の <span class='g-ui sub'>？</span> ボタンでいつでも見られます。</div>"),
]
slides=''.join(f"<section class='g-slide' data-i='{i}'><div class='g-ico'>{ic}</div><h3>{t}</h3>{b}</section>" for i,(ic,t,b) in enumerate(SL))
HTML=f'''<div class="guide" id="guide" role="dialog" aria-modal="true" aria-label="使い方">
  <div class="g-card">
    <div class="g-head"><span class="g-step" id="gStep">1 / {len(SL)}</span><button class="g-x" id="gX" aria-label="閉じる">✕</button></div>
    <div class="g-body" id="gBody">{slides}</div>
    <div class="g-foot"><div class="g-dots" id="gDots">{''.join('<i></i>' for _ in SL)}</div>
      <div class="g-nav"><button id="gPrev">← もどる</button><button class="g-next" id="gNext">次へ →</button></div>
      <button class="g-hide" id="gHide">今後は表示しない</button></div>
  </div>
</div>
'''
a='<div class="modal" id="dataModal">'
assert s.count(a)==1; s=s.replace(a,HTML+a)

JS=r'''/* ---- 使い方ガイド：開くたびに出す。「今後は表示しない」で出なくなる。右上の「？」でいつでも開ける ---- */
const GUIDE_KEY="nihonshi_guide";
let gIdx=0;
function guideShow(i){ const ss=document.querySelectorAll("#guide .g-slide"), n=ss.length; gIdx=Math.max(0,Math.min(i,n-1));
  ss.forEach((x,k)=>x.classList.toggle("on",k===gIdx)); document.querySelectorAll("#gDots i").forEach((x,k)=>x.classList.toggle("on",k===gIdx));
  document.getElementById("gStep").textContent=(gIdx+1)+" / "+n; document.getElementById("gPrev").disabled=gIdx===0;
  document.getElementById("gNext").textContent=gIdx===n-1?"はじめる":"次へ →"; document.getElementById("gBody").scrollTop=0; }
function guideOpen(i){ document.getElementById("guide").classList.add("open"); document.body.style.overflow="hidden"; guideShow(i||0); }
function guideClose(){ document.getElementById("guide").classList.remove("open"); document.body.style.overflow=""; }
document.getElementById("guideBtn").addEventListener("click",()=>guideOpen(0));
document.getElementById("gX").addEventListener("click",guideClose);
document.getElementById("gPrev").addEventListener("click",()=>guideShow(gIdx-1));
document.getElementById("gNext").addEventListener("click",()=>{ if(gIdx>=document.querySelectorAll("#guide .g-slide").length-1) guideClose(); else guideShow(gIdx+1); });
document.getElementById("gHide").addEventListener("click",()=>{ try{localStorage.setItem(GUIDE_KEY,"hide");}catch(e){} guideClose(); toast("次からは出ません。右上の「？」で開けます"); });
{ let x0=null; const b=document.getElementById("gBody");
  b.addEventListener("touchstart",e=>{ x0=e.touches[0].clientX; },{passive:true});
  b.addEventListener("touchend",e=>{ if(x0==null) return; const dx=e.changedTouches[0].clientX-x0; x0=null; if(Math.abs(dx)>60) guideShow(gIdx+(dx<0?1:-1)); },{passive:true}); }
{ let hide=null; try{ hide=localStorage.getItem(GUIDE_KEY); }catch(e){} if(hide!=="hide") guideOpen(0); }

'''
a="/* ふりがなの置きかえ */"
assert s.count(a)==1; s=s.replace(a,JS+a)
open(dst,'w',encoding='utf-8').write(s); print('ok')
