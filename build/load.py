import csv,glob,re,unicodedata,collections,sys,os
RAW=os.path.join(os.path.dirname(__file__),'..','raw')
def fold(s):
    s=unicodedata.normalize('NFKD',s or '').encode('ascii','ignore').decode().lower()
    return re.sub(r'[^a-z0-9]+',' ',s).strip()
def ntitle(t):
    t=re.sub(r'\s*[\(\[](feat|ft|with|featuring)[^\)\]]*[\)\]]','',t,flags=re.I)
    t=t.replace('"','').replace('“','').replace('”','')
    return fold(t)
SPLIT=re.compile(r'\s+(?:feat\.?|featuring|ft\.?|with|&|and|x|×|vs\.?)\s+|,\s*',re.I)
def nartist(a): return fold(SPLIT.split(a or '')[0])
def names(field):
    out=[]
    for x in re.split(r';',field or ''):
        x=x.strip().strip('.')
        x=re.sub(r'\s*\((?:co-?|additional|vocal|uncredited)[^)]*\)','',x,flags=re.I).strip()
        if not x or x.lower() in ('none listed','(none listed)','n/a','unknown','—','-'): continue
        out.append(x)
    return out
def rows():
    for f in sorted(glob.glob(os.path.join(RAW,'*.tsv'))):
        with open(f,encoding='utf-8') as fh:
            for r in csv.DictReader(fh,delimiter='\t',quoting=csv.QUOTE_NONE):
                if not r.get('title'): continue
                r['_file']=os.path.basename(f); yield r
if __name__=='__main__':
    c=collections.Counter()
    for r in rows():
        for n in names(r.get('writers'))+names(r.get('producers')): c[n]+=1
    for n,k in c.most_common(): print(k,n,sep='\t')
