import re
F = r'c:\Users\Jules\Desktop\GPS0\minijeux\niveau2.html'
with open(F,'rb') as f: b=f.read()
fixes=[(b'\xe2\x9c\xa8','\u2728'.encode()),(b'\xe2\x9c\xa6','\u2726'.encode()),(b'\xe2\x9a\xa1','\u26a1'.encode()),(b'\xe2\x86\x92','\u2192'.encode()),(b'\xe2\x80\x94','\u2014'.encode()),(b'\xe2\x80\x99','\u2019'.encode()),(b'\xe2\x94\x80','\u2500'.encode()),(b'\xc2\xb7','\xb7'.encode()),(b'\xc2\xa0','\xa0'.encode()),(b'\xc3\x89','\xc9'.encode()),(b'\xc3\xa9','\xe9'.encode()),(b'\xc3\xa8','\xe8'.encode()),(b'\xc3\xa0','\xe0'.encode()),(b'\xc3\xb9','\xf9'.encode()),(b'\xc3\xae','\xee'.encode()),(b'\xc3\xb4','\xf4'.encode()),(b'\xc3\xbb','\xfb'.encode()),(b'\xc3\xa7','\xe7'.encode()),(b'\xc3\xaf','\xef'.encode()),(b'\xc3\xa2','\xe2'.encode()),(b'\xc3\xaa','\xea'.encode()),(b'\xc5\x93','\u0153'.encode())]
for bad,good in fixes: b=b.replace(bad,good)
try: t=b.decode('utf-8')
except: t=b.decode('utf-8',errors='replace')
for a,c in [('\u00e2\u00a4\u00e2\u00a4\u00e2\u00a4','\u2764\u2764\u2764'),('\u00e2\u00a4\u00e2\u00a4','\u2764\u2764'),('\u00e2\u00a4','\u2764'),('\u00c2\u00b7','\xb7'),('\u00c2','')]: t=t.replace(a,c)
t=re.sub(r'window\.TUTO_TEXT\s*=\s*".*?";','window.TUTO_TEXT = "Lune Phobos \u2014 Tape pour sauter \xb7 \xc9vite les colonnes \xb7 3 vies<br><small>Les bords ne te tuent pas \xb7 Cristaux \u2726 = +1 poussi\xe8re</small>";',t,flags=re.DOTALL)
print('HUD lives:',repr(re.search(r'id="lives">(.*?)</span>',t).group(1) if re.search(r'id="lives">(.*?)</span>',t) else '?'))
checks=['TUTO_TEXT','drawCosmonaut','loseLife','GPS0_running']
for c in checks: print('OK' if c in t else 'MISSING',c)
with open(F,'w',encoding='utf-8') as f: f.write(t)
print('Saved',len(t),'chars')
