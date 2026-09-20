"""Bounded static checks. This is not an in-game or GUI execution test."""
from pathlib import Path
import sys,zipfile,re,json,csv
from collections import Counter
from pdx import parse,get,decode,TOKEN
from revise_020 import loc_read

root=Path(sys.argv[1]);vanilla=zipfile.ZipFile(sys.argv[2]);errors=[]
def check(ok,message):
    if not ok:errors.append(message)
def local(p):return (root/p).read_text(encoding='utf-8-sig')
def database(folder):
    files={p.removeprefix('game/'):decode(vanilla.read(p)) for p in vanilla.namelist() if p.startswith('game/'+folder+'/') and p.endswith('.txt')}
    files.update({p.relative_to(root).as_posix():p.read_text(encoding='utf-8-sig') for p in (root/folder).glob('*.txt')})
    return [n for text in files.values() for n in parse(text)]
cultures={n.key:n.value for n in database('common/culture/cultures')}
custom={k:v for k,v in cultures.items() if k.startswith('aq_')}
pillars={n.key for n in database('common/culture/pillars')}
religions=database('common/religion/religion_types')
faiths={n.key for r in religions for n in get(r.value,'faiths',[])}
customfaiths={k for k in faiths if k.startswith('aq_')}
check(not set(custom)&faiths,'Culture / faith identifier collisions')
doctrines=set()
def walk(ns):
    for n in ns:
        yield n
        if isinstance(n.value,list):yield from walk(n.value)
for n in walk(database('common/religion/doctrine_types')):doctrines.add(n.key)
holy={n.key for n in database('common/religion/holy_sites')}
for r in religions:
    if not r.key.startswith('aq_'):continue
    for n in walk(r.value):
        if n.key=='doctrine':check(n.value in doctrines,'Unknown doctrine '+n.value)
        if n.key=='holy_site':check(n.value in holy,'Unknown holy site '+n.value)
for key,v in custom.items():
    for p in ('heritage','language','ethos','martial_custom'):
        check(get(v,p) in pillars,f'{key}: unknown {p} {get(v,p)}')
loc={};allkeys=[]
for p in (root/'localization/english').rglob('*.yml'):
    s=p.read_text(encoding='utf-8-sig');keys=list(loc_read(s));allkeys+=keys;loc.update(loc_read(s))
    check(p.read_bytes().startswith(b'\xef\xbb\xbf'),'Missing localization BOM '+str(p))
check(len(allkeys)==len(set(allkeys)),'Duplicate localization keys '+str([k for k,c in Counter(allkeys).items() if c>1][:30]))
for key in set(custom)|customfaiths:
    check(key in loc,'Missing display name '+key)
    check('rites' not in loc.get(key,'').lower(),'Rites label remains '+key)
for key,v in custom.items():
    check(loc.get(key) not in {loc.get(f) for f in customfaiths},'Shared culture/faith display name '+key)
for folder in ('history/provinces','history/characters','common/bookmarks/bookmarks','common/dynasties'):
    for p in (root/folder).glob('*.txt'):
        for n in walk(parse(p.read_text(encoding='utf-8-sig'))):
            if n.key=='culture':check(n.value in cultures,'Unknown culture '+str(n.value))
            if n.key=='religion':check(n.value in faiths,'Unknown faith '+str(n.value))
eras={n.key:get(n.value,'year') for n in parse(local('common/culture/eras/00_culture_eras.txt'))}
innovations={n.key for n in database('common/culture/innovations')}
for p in (root/'history/cultures').glob('*.txt'):
    if not parse(p.read_text(encoding='utf-8-sig')):continue
    check(p.stem in cultures,'Unknown culture history '+p.stem)
    for n in walk(parse(p.read_text(encoding='utf-8-sig'))):
        if n.key=='join_era':check(n.value in eras,'Invalid culture era '+str(n.value))
        if n.key=='discover_innovation':check(n.value in innovations,'Invalid innovation '+str(n.value))
for p in root.rglob('*.txt'):
    if 'tools' in p.parts:continue
    balance=0
    for m in TOKEN.finditer(p.read_text(encoding='utf-8-sig')):
        if m[0]=='{':balance+=1
        if m[0]=='}':balance-=1
        if balance<0:break
    check(balance==0,'Unbalanced braces '+str(p))
rows=list(csv.DictReader((root/'source_data/county_peoples_020.csv').open(encoding='utf-8-sig')))
check(len(rows)==3476,'Changed county count')
samples={r['county']:r for r in rows if r['county'] in ('c_caria','c_lycia','c_lydia','c_benevento','c_spoleto','c_delhi','c_magadha','c_jharkand','c_gaya')}
india=Counter(r['culture'] for r in rows if r['old_culture'] in ('aq_indo_aryan','aq_magadhan','aq_gangetic','aq_dravidian'))
calendar={int(y):(str(1001-int(y))+' BC' if int(y)<=1000 else str(int(y)-1000)+' AD') for y in ('642','901','1000','1001','1200','1700','1900','2050','2200')}
def number(v):return int(str(v).removeprefix('(int32)'))
functions={'LessThanOrEqualTo_int32':lambda a,b:number(a)<=number(b),
    'Subtract_int32':lambda a,b:number(a)-number(b),'IntToString':lambda a:str(number(a)),
    'Select_CString':lambda test,a,b:a if test else b}
# Evaluate the actual generated expression text, after numeric macro substitution.
for y,expected in calendar.items():
    template=loc['INNOVATION_ERA_NOT_IN_YEAR'].replace('$YEAR|q$',str(y))
    try:
        actual=''.join(str(eval(s,{'__builtins__':{}},functions)) for s in re.findall(r'\[([^\]]+)\]',template))
        check(actual==expected,f'Calendar expression {y}: {actual} != {expected}')
    except Exception as exc:check(False,'Calendar expression error '+repr(exc))
check(eras['culture_era_aq_middle']=='901','Middle era engine gate changed')
check(eras['culture_era_aq_late']=='1200','Late era engine gate changed')
check(eras['culture_era_tribal']=='1700','Pre-medieval engine gate changed')
report={'status':'FAIL' if errors else 'PASS','errors':sorted(set(errors)),
        'custom_culture_definitions':len(custom),'custom_faith_definitions':len(customfaiths),
        'counties':len(rows),'active_cultures':len(set(r['culture'] for r in rows)),
        'indian_population_counts':dict(india.most_common()),'sample_counties':samples,
        'calendar_arithmetic':calendar,'generated_calendar_expressions_checked':True,'in_game_tested':False}
(root/'source_data/static_checks_020.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps(report,indent=2));sys.exit(bool(errors))
