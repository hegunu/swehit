import sys,os,re,json,csv,glob,collections
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from load import rows,fold,ntitle,names,SPLIT
from swedes import SW
EXTRA=os.path.join(os.path.dirname(__file__),'extra_swedes.json')
if os.path.exists(EXTRA):
    for k,v in json.load(open(EXTRA)).items(): SW.setdefault(k,v)
for af in glob.glob(os.path.join(os.path.dirname(__file__),'..','raw','*.acts.txt')):
    for line in open(af,encoding='utf-8'):
        f=line.rstrip('\n').split('\t')
        if len(f)<2 or not f[0].strip() or f[0].lower().startswith('name'): continue
        nm=f[0].strip()
        if nm in SW or any(nm in v.get('al',[]) for v in SW.values()): continue
        SW[nm]=dict(al=[],b=f[1].strip() if len(f)>1 else None,be=f[2].strip() if len(f)>2 else None,born=(f[3].strip() or None) if len(f)>3 else None,w=(f[4].strip() or None) if len(f)>4 else None)
ACT_AL={'Sylvia Vrethammar':['Sylvia'],'Yngwie Malmsteen':["Yngwie J. Malmsteen's Rising Force",'Yngwie J. Malmsteen'],'Siw Malmkvist':['Siv Malmqvist','Siw Malmqvist','Siv Malmkvist'],'Frida':['Anni-Frid Lyngstad','Frida Lyngstad'],'Herreys':['Herrey']}
for k,als in ACT_AL.items():
    if k in SW: SW[k]['al']=SW[k].get('al',[])+als
EA=os.path.join(os.path.dirname(__file__),'extra_alias.json')
if os.path.exists(EA):
    for k,als in json.load(open(EA)).items(): SW[k]['al']=SW[k].get('al',[])+als
AFIX={'p!nk':'pink','*nsync':'nsync',"n'sync":'nsync','n sync':'nsync','ke$ha':'kesha','beyoncé':'beyonce'}
def akey(a):
    m=SPLIT.split(a or '')[0].strip().lower()
    m=AFIX.get(m,m)
    return fold(m).replace(' ','')
# alias index
idx={}
for k,v in SW.items():
    if v.get('skip'): continue
    for n in [k]+v.get('al',[]): idx[fold(n)]=k
def who(n):
    f=fold(n)
    if f in idx: return idx[f]
    f2=fold(re.sub(r'\(.*?\)','',n))
    return idx.get(f2)
def peakparse(p):
    us=uk=None;t10=False
    for m in re.finditer(r'\b(US|UK)\s*(?:Hot 100\s*)?(\d+)\b',p or ''):
        v=int(m.group(2))
        if m.group(1)=='US': us=v if us is None else min(us,v)
        else: uk=v if uk is None else min(uk,v)
    if re.search(r'US\s*top\s*10',p or '',re.I): t10=True
    return us,uk,t10
songs={}
for r in rows():
    t=r['title'].strip().strip('"')
    if re.search(r'unreleased',t,re.I) or fold(r['artist'])=='max martin' or re.search(r'remix',r['artist'],re.I): continue
    key=(ntitle(t),akey(r['artist']))
    s=songs.get(key)
    if not s:
        s=songs[key]=dict(t=t,a=r['artist'].strip(),y=None,w=[],p=[],us=None,uk=None,t10=False,src=[],ox={})
    try:
        y=int(re.match(r'\d{4}',r.get('year') or '').group())
        s['y']=y if s['y'] is None else min(s['y'],y)
    except Exception: pass
    for fld,lst in (('writers','w'),('producers','p')):
        for n in names(r.get(fld)):
            if n not in s[lst]: s[lst].append(n)
    us,uk,t10=peakparse(r.get('peak'))
    if us: s['us']=us if s['us'] is None else min(s['us'],us)
    if uk: s['uk']=uk if s['uk'] is None else min(s['uk'],uk)
    s['t10']|=t10
    for m in re.finditer(r'\b(SWE|DE|GER|NL|NOR|BEL|AUT|SWI|AUS|CAN|IRE|JPN|FRA|ITA|DEN|FIN|NZ)\s*(\d+)\b',r.get('peak') or ''):
        c=m.group(1).replace('GER','DE'); v=int(m.group(2))
        s['ox'][c]=min(s['ox'].get(c,999),v)
    for u in re.split(r'\s*[|;]\s*',r.get('source') or ''):
        if u.startswith('http') and u not in s['src']: s['src'].append(u)
# peaks enrichment
pk={}
for f in glob.glob(os.path.join(os.path.dirname(__file__),'..','raw','*.peaks')):
    with open(f,encoding='utf-8') as fh:
        for r in csv.DictReader(fh,delimiter='\t',quoting=csv.QUOTE_NONE):
            if not r.get('title'): continue
            k=(ntitle(r['title'].strip('"')),akey(r['artist']))
            def iv(x):
                try: return int(re.match(r'\d+',x or '').group())
                except Exception: return None
            pk[k]=(iv(r.get('us')),iv(r.get('uk')))
            pk.setdefault((ntitle(r['title'].strip('"')),'*'+akey(r['artist'])),pk[k])
hitp=0
for k,s in songs.items():
    if k in pk:
        us,uk=pk[k]; hitp+=1
        if us and not s['us']: s['us']=us
        if uk and not s['uk']: s['uk']=uk
FIX={('lush life','zaralarsson'):dict(us=75),('stateside','zaralarsson'):dict(us=None),("ain t my fault",'zaralarsson'):dict(us=None),('midnight sun','zaralarsson'):dict(us=None)}
for k,v in FIX.items():
    if k in songs: songs[k].update(v)
BEN=json.load(open(os.path.join(os.path.dirname(__file__),'bios_en.json')))
# people
pid={};people=[]
def P(name):
    if name not in pid:
        pid[name]=len(people); v=SW[name]
        people.append(dict(id=pid[name],n=name,be=BEN.get(name) or v.get('be'),al=v.get('al',[]),full=v.get('full'),born=(re.match(r'\d{4}',v.get('born') or '') or [None])[0],b=v.get('b'),w=v.get('w'),act=v.get('act',0)))
    return pid[name]
out=[];unknown=collections.Counter()
DATES={}
DF=os.path.join(os.path.dirname(__file__),'..','raw','dates.tsv')
if os.path.exists(DF):
    for line in open(DF,encoding='utf-8'):
        f=line.rstrip('\n').split('\t')
        if len(f)>=3 and re.match(r'\d{4}-\d{2}-\d{2}$',f[2].strip()): DATES[(ntitle(f[0]),akey(f[1]))]=f[2].strip()
for s in sorted(songs.values(),key=lambda s:(s['y'] or 0,s['t'])):
    cr=collections.OrderedDict(); ow=[]; op=[]
    for n in s['w']:
        k=who(n)
        if k: cr[k]=cr.get(k,0)|1
        else: ow.append(n); unknown[n]+=1
    for n in s['p']:
        k=who(n)
        if k: cr[k]=cr.get(k,0)|2
        else: op.append(n); unknown[n]+=1
    for part in SPLIT.split(s['a']):
        k=who(part.strip())
        if k: cr[k]=cr.get(k,0)|4
    if not cr: continue
    us,uk=s['us'],s['uk']
    dt=DATES.get((ntitle(s['t']),akey(s['a'])))
    if dt and s['y'] and int(dt[:4])!=s['y']: dt=None
    out.append(dict(id=len(out),t=s['t'],a=s['a'],y=s['y'],d=dt,us=us,uk=uk,t10=1 if (s['t10'] and not us) else 0,
        cr=[[P(k),m] for k,m in cr.items()],ow=', '.join(ow),op=', '.join(op),ox='; '.join(f'{k} {v}' for k,v in sorted(s['ox'].items(),key=lambda x:x[1])[:5]),src=(s['src'] or [''])[0]))
json.dump(dict(songs=out,people=people,meta=dict(sources='Engelska Wikipedia (produktionsdiskografier, låtlistor, artistdiskografier och låtartiklar)',date='oktober 2026')),
          open(sys.argv[1],'w'),ensure_ascii=False,separators=(',',':'))
print('songs',len(out),'people',len(people),'peak-enriched',hitp,file=sys.stderr)
if len(sys.argv)>2:
    with open(sys.argv[2],'w') as f:
        for n,c in unknown.most_common(): f.write(f'{c}\t{n}\n')
