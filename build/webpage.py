"""Make a self-contained index.html for hosting: inline fonts and d3, no third-party requests.
usage: python3 -I build/webpage.py page.html selfhost/ index.html"""
import sys,re,os
src,assets,out=sys.argv[1:4]
s=open(src,encoding='utf-8').read()
s=re.sub(r'<link rel="preconnect"[^>]*>\n?','',s)
css=open(os.path.join(assets,'fonts.css'),encoding='utf-8').read()
s=re.sub(r'<link rel="stylesheet" href="https://fonts\.googleapis\.com[^>]*>',lambda m:'<style>'+css+'</style>',s)
d3=open(os.path.join(assets,'d3.min.js'),encoding='utf-8').read()
s=re.sub(r'<script src="https://cdnjs[^"]*d3\.min\.js"></script>',lambda m:'<script>'+d3+'</script>',s)
assert 'googleapis' not in s and 'cdnjs' not in s
head='<!doctype html>\n<html lang="sv">\n<head>\n<meta charset="utf-8">\n<meta name="viewport" content="width=device-width, initial-scale=1">\n'
open(out,'w',encoding='utf-8').write(head+s+'\n</html>\n')
