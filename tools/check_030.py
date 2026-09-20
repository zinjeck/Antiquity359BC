"""Load-order aware static audit for population, government, titles and preserved faiths."""
from pathlib import Path
from collections import Counter
import sys,zipfile,json,re,csv,hashlib
from pdx import parse,get,decode,TOKEN
from revise_020 import loc_read
root=Path(sys.argv[1]);z=zipfile.ZipFile(sys.argv[2]);errors=[]
def check(ok,msg):
 if not ok:errors.append(msg)
def rd(p):return (root/p).read_text(encoding='utf-8-sig')
def db(folder):
 files={p.removeprefix('game/'):decode(z.read(p)) for p in z.namelist() if p.startswith('game/'+folder+'/') and p.endswith('.txt')}
 files.update({p.relative_to(root).as_posix():p.read_text(encoding='utf-8-sig') for p in (root/folder).rglob('*.txt')})
 ns=[n for s in files.values() for n in parse(s)];return ns
def walk(ns):
 for n in ns:
  yield n
  if isinstance(n.value,list):yield from walk(n.value)
cns=db('common/culture/cultures');cultures={n.key:n.value for n in cns};pillars=db('common/culture/pillars');pkeys={n.key for n in pillars}
for k,v in Counter(n.key for n in cns).items():check(v==1,'Duplicate effective culture '+k)
arabic={k for k,v in cultures.items() if get(v,'heritage')=='heritage_arabic'}
check(arabic=={'bedouin','levantine','aq_sabaean'},'Arabic group '+str(arabic))
check({k for k,v in cultures.items() if 'egypt' in k}=={'egyptian'},'Duplicate Egyptian cultures')
check({p.key for p in pillars if 'egypt' in p.key and get(p.value,'type')=='heritage'}=={'heritage_egyptian'},'Duplicate Egyptian heritage')
check(get(cultures['egyptian'],'heritage')=='heritage_egyptian','Egyptian heritage assignment')
check('aq_arabian' not in cultures and 'aq_persian' not in cultures,'Obsolete culture definitions')
for key,v in cultures.items():
 if key.startswith('aq_') or key in ('egyptian','persian','bedouin','levantine'):
  for field in ('language','heritage','martial_custom','ethos'):check(get(v,field) in pkeys,key+' invalid '+field+' '+str(get(v,field)))
faiths={f.key for r in db('common/religion/religion_types') for f in get(r.value,'faiths',[])}
check(not set(cultures)&faiths,'Culture and faith keys collide')
religionhashes=json.loads(rd('source_data/revision_030.json'))['religion_definitions_sha256']
for p,h in religionhashes.items():check(hashlib.sha256((root/p).read_bytes()).hexdigest()==h,'Religion content changed: '+p)
loc={};keys=[]
for p in (root/'localization/english').rglob('*.yml'):
 parsed=loc_read(p.read_text(encoding='utf-8-sig'));loc.update(parsed);keys+=list(parsed)
 check(p.read_bytes().startswith(b'\xef\xbb\xbf'),'Missing localization BOM '+str(p))
check(len(keys)==len(set(keys)),'Duplicate custom localization keys '+str([k for k,v in Counter(keys).items() if v>1][:10]))
check([loc.get(k) for k in ('egyptian','persian','bedouin','levantine','aq_sabaean')]==['Egyptian','Persian','Bedouin','Mashriqi','Sabaean'],'Canonical culture display names')
for folder in ('history/characters','history/provinces','common/dynasties','common/bookmarks/bookmarks'):
 for p in (root/folder).rglob('*.txt'):
  for n in walk(parse(p.read_text(encoding='utf-8-sig'))):
   if n.key=='culture':check(n.value in cultures,'Unknown culture '+str(n.value))
   if n.key=='religion':check(n.value in faiths,'Unknown faith '+str(n.value))
for p in (root/'history/cultures').glob('*.txt'):
 if parse(p.read_text(encoding='utf-8-sig')):check(p.stem in cultures,'Obsolete culture history '+p.stem)
eras={n.key for n in parse(rd('common/culture/eras/00_culture_eras.txt'))}
innovations={n.key:n for n in db('common/culture/innovations')}
for key,n in innovations.items():
 if key.startswith('innovation_aq_'):check(get(n.value,'culture_era') in eras,'Invalid innovation era '+key)
for p in (root/'history/cultures').glob('*.txt'):
 for n in walk(parse(p.read_text(encoding='utf-8-sig'))):
  if n.key=='discover_innovation':check(n.value in innovations,'Unknown innovation '+str(n.value))
  if n.key=='join_era':check(n.value in eras,'Unknown culture era '+str(n.value))
check('nomad_government' in {n.key for n in db('common/governments')},'Native nomad government unavailable')
check('nomad_holding' in {n.key for n in db('common/holdings')},'Native nomad holding unavailable')
for p in root.rglob('*.txt'):
 if 'tools' in p.parts:continue
 balance=0
 for m in TOKEN.finditer(p.read_text(encoding='utf-8-sig')):
  if m[0]=='{':balance+=1
  elif m[0]=='}':balance-=1
  if balance<0:break
 check(balance==0,'Unbalanced braces '+str(p))
titles={n.key:n for n in walk(parse(rd('common/landed_titles/aq_world.txt'))) if re.match('^[ekdcb]_',n.key) and isinstance(n.value,list)}
chars={n.key:n for n in parse(rd('history/characters/aq_world.txt'))}
def start(n):
 v={}
 for d in n.value:
  if re.match(r'^\d+\.\d+\.\d+$',d.key) and tuple(map(int,d.key.split('.')))<=(642,5,1):v.update({x.key:x.value for x in d.value})
 return v
hist={n.key:start(n) for n in parse(rd('history/titles/aq_world.txt'))};rows=list(csv.DictReader((root/'source_data/county_peoples_030.csv').open(encoding='utf-8-sig')))
check(len(rows)==3476,'County count changed')
for key,v in hist.items():
 h=v.get('holder','0');l=v.get('liege','0')
 check(key in titles,'Unknown history title '+key)
 check(h=='0' or h in chars,'Unknown holder '+h)
 check(l=='0' or l in hist and hist[l].get('holder','0')!='0','Invalid or unheld liege '+key+': '+l)
 seen=set();cur=key
 while hist.get(cur,{}).get('liege','0')!='0':
  check(cur not in seen,'Liege cycle '+key)
  if cur in seen:break
  seen.add(cur);cur=hist[cur]['liege']
provs={n.key:n for n in parse(rd('history/provinces/aq_world.txt'))}
nomads=[]
for r in rows:
 c=r['county'];h=hist[c]['holder'];check(h==r['holder'],'County ownership drift '+c)
 bs=[b for b in titles[c].value if b.key.startswith('b_') and get(b.value,'province')]
 capital=get(bs[0].value,'province')
 for b in bs:
  p=provs[get(b.value,'province')]
  check(get(p.value,'culture')==r['culture'] and get(p.value,'religion')==r['faith'],'County CSV mismatch '+c)
 if r['government']=='nomad_government':
  nomads.append(c);check(hist[c]['government']=='nomad_government','Nomad government missing '+c)
  check(get(provs[capital].value,'holding')=='nomad_holding','Nomad holding missing '+c)
  check(any(n.key=='trait' and n.value=='nomadic_philosophy' for n in chars[h].value),'Nomad philosophy missing '+h)
 if h.startswith('aq_chief_'):
  for ident in (h,h+'_spouse',h+'_son',h+'_daughter'):
   if ident in chars:check(get(chars[ident].value,'culture')==r['culture'],'Family culture mismatch '+ident)
for key,n in titles.items():
 if key[0] in 'edk' and any(c.key.startswith(('k_','d_','c_')) for c in n.value):
  check(get(n.value,'can_create') is not None and get(n.value,'can_create_on_partition') is not None,'Missing title progression gate '+key)
real_empires=[k for k,n in titles.items() if k.startswith('e_') and any(x.key.startswith('k_') for x in n.value)]
for key in real_empires:check(key in loc,'No era-appropriate empire localization '+key)
check(loc['e_byzantium']=='Hellenic Empire' and loc['e_france']=='Gallic Empire' and loc['e_arabia']=='Semitic Empire','Empire labels incorrect')
checks={
 'common/character_interactions/09_mpo_interactions.txt':['scope:actor = { aq_confederation_room_trigger = yes }','scope:recipient = { aq_confederation_room_trigger = yes }'],
 'common/decisions/80_major_decisions.txt':['aq_can_form_kingdom_trigger = yes','aq_can_form_empire_trigger = yes'],
 'common/decisions/dlc_decisions/mpo/mpo_decisions.txt':['aq_can_form_kingdom_trigger = yes','aq_can_form_empire_trigger = yes'],
 'common/casus_belli_types/09_mpo_wars.txt':['aq030_large_conquest_trigger = yes'],
 'common/casus_belli_types/00_nomadic_conquest.txt':['aq_can_form_chiefdom_union_trigger = yes'],
 'common/on_action/yearly_on_actions.txt':['aq_early_nomad_balance_effect = yes'],
}
for p,needles in checks.items():
 for needle in needles:check(needle in rd(p),'Missing progression hook '+p+':'+needle)
summary={'status':'FAIL' if errors else 'PASS','errors':sorted(set(errors)),
 'arabic_cultures':sorted(arabic),'egyptian_cultures':['egyptian'],'egyptian_heritages':['heritage_egyptian'],
 'active_cultures':len(set(r['culture'] for r in rows)),'nomadic_counties':len(nomads),
 'independent_chiefdoms':sum(k.startswith('c_') and v.get('holder','0')!='0' and v.get('liege','0')=='0' for k,v in hist.items()),
 'remaining_independent_generic_duchies':sum(k.startswith('d_') and v.get('holder','').startswith('aq_chief_') and v.get('liege','0')=='0' for k,v in hist.items()),
 'religion_files_unchanged':not any('Religion content changed' in e for e in errors),
 'progression_routes_checked':len(checks),'in_game_tested':False}
(root/'source_data/static_checks_030.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
print(json.dumps(summary,indent=2));sys.exit(bool(errors))
