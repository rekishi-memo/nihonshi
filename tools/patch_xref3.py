# 本文の「テーマ史：外交史（欧米） 授業01」が、名前のかっこで切れて同じセットの「授業01」に飛んでしまうのを直す（2026-11-14）。
#   python3 patch_xref3.py ../app/source.html ../app/source.html （何度かけても同じ）
import sys
src,out=sys.argv[1:3]; s=open(src,encoding='utf-8').read()
a="|テーマ史[：〈]([^（）〉、。 　]+)〉?(?:[ 　の]*授業(\\d{2}))?|"
b="|テーマ史[：〈](外交史（(?:欧米|中国・朝鮮)）|[^（）〉、。 　]+)〉?(?:[ 　の]*授業(\\d{2}))?|"
if b not in s:
    assert s.count(a)==1; s=s.replace(a,b)
open(out,'w',encoding='utf-8').write(s); print('ok')
