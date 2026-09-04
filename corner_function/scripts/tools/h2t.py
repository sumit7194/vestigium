import sys,re
from html.parser import HTMLParser
class P(HTMLParser):
    def __init__(s): super().__init__(); s.out=[]; s.skip=0; s.inmath=0
    def handle_starttag(s,tag,attrs):
        a=dict(attrs)
        if tag in('script','style'): s.skip+=1
        if tag=='math':
            s.inmath+=1
            if 'alttext' in a: s.out.append(' $'+a['alttext']+'$ ')
        if tag in('p','div','tr','br','h1','h2','h3','h4','li','table','figcaption'): s.out.append('\n')
        if tag in('td','th'): s.out.append(' | ')
    def handle_endtag(s,tag):
        if tag in('script','style'): s.skip-=1
        if tag=='math': s.inmath-=1
        if tag in('p','div','tr','h1','h2','h3','h4','li','table','figcaption'): s.out.append('\n')
    def handle_data(s,d):
        if s.skip or s.inmath: return
        s.out.append(d)
for f in sys.argv[1:]:
    p=P(); p.feed(open(f,encoding='utf-8',errors='replace').read())
    t=''.join(p.out); t=re.sub(r'[ \t]+',' ',t); t=re.sub(r'\n\s*\n+','\n',t)
    open(f.replace('.html','.txt'),'w').write(t); print(f, len(t))
