"""Finish 0.4's Bosporan settlement, source audit, and static-map rendering inputs.
No third-party packages and no game execution. Run after revise_040.py.
"""
from pathlib import Path
from collections import Counter
import re,json,csv,io,sys,hashlib,zipfile,datetime
from pdx import parse,get,decode
from titles_040 import ROOT,read,index_titles,start_fields
assert 'version="0.4.0"' in read('descriptor.mod')
T,P=index_titles(read('common/landed_titles/aq_world.txt'))
H={n.key:start_fields(n) for n in parse(read('history/titles/aq_world.txt'))}
DATA=ROOT/'source_data/040'
backup=Path(r'C:\antiquity_backups')/('finish_040_'+datetime.datetime.now().strftime('%Y%m%d_%H%M%S'))
written=[]
def save(rel,s):
 p=ROOT/rel;b=s.encode('utf-8-sig' if p.suffix=='.yml' else 'utf-8')
 if p.exists() and p.read_bytes()==b:return
 if p.exists():q=backup/rel;q.parent.mkdir(parents=True,exist_ok=True);q.write_bytes(p.read_bytes())
 p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(b)
 written.append({'path':rel,'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()})
def splice(s,changes):
 for a,b,t in sorted(changes,reverse=True):s=s[:a]+t+s[b:]
 return s

# The existing game-start action converts every landed nomadic_philosophy holder back to nomad.
# Hermonassa is now a Bosporan settled colony, so its holding and character must agree with its title.
oldchar=H['c_tmutarakan']['holder'];cs=read('history/characters/aq_world.txt')
char=next(n for n in parse(cs) if n.key==oldchar);block=cs[char.start:char.end]
block=re.sub(r'^\s*trait\s*=\s*nomadic_philosophy\s*$', '',block,flags=re.M)
block=re.sub(r'\bname\s*=\s*\S+','name = aq040_name_philiskos',block,count=1)
block=re.sub(r'\bculture\s*=\s*\S+','culture = aq_hellenic',block,count=1)
block=re.sub(r'\breligion\s*=\s*\S+','religion = hellenic_pagan',block,count=1)
save('history/characters/aq_world.txt',splice(cs,[(char.start,char.end,block)]))
ps=read('history/provinces/aq_world.txt');pn={n.key:n for n in parse(ps)};ed=[];settled=[]
for county in ['c_kerch','c_tmutarakan']:
 b=next(b for b in T[county].value if b.key.startswith('b_') and get(b.value,'province'))
 pid=get(b.value,'province');n=pn[pid];block=ps[n.start:n.end]
 for field,value in [('culture','aq_hellenic'),('religion','hellenic_pagan'),('holding','tribal_holding')]:
  block,count=re.subn(r'\b'+field+r'\s*=\s*\S+',field+' = '+value,block,count=1)
  assert count==1,(pid,field)
 ed.append((n.start,n.end,block));settled.append({'county':county,'capital_barony':b.key,'province_id':int(pid)})
save('history/provinces/aq_world.txt',splice(ps,ed))
labels={'c_kerch':'Pantikapaion','c_tmutarakan':'Hermonassa','b_kerch':'Pantikapaion','b_tmutarakan':'Hermonassa'}
for k,v in list(labels.items()):labels[k+'_adj']=v
labels['aq040_name_philiskos']='Philiskos'
for lang in ['english','french','german','spanish','russian','simp_chinese','korean','japanese','polish']:
 path=f'localization/{lang}/replace/aq040_titles_l_{lang}.yml';s=read(path)
 for k,v in labels.items():
  s,n=re.subn(r'^\s*'+re.escape(k)+r':\d*\s*".*"\s*$',f' {k}:0 "{v}"',s,flags=re.M)
  if not n:s+=' '+k+':0 "'+v+'"\n'
 save(path,s)
audit=json.loads(read('source_data/040/applied_title_names.json'))
for row in audit:
 if row['title_id'] in labels:row['implemented_name']=labels[row['title_id']]
save('source_data/040/applied_title_names.json',json.dumps(audit,ensure_ascii=False,indent=1))
overrides=json.loads(read('source_data/040/historical_overrides.json'))
for k,name in [('c_kerch','Pantikapaion'),('c_tmutarakan','Hermonassa')]:
 if not any(x['title']==k for x in overrides):overrides.append({'title':k,'implemented':name,'reason':'Attested Greek settlement replaces a broad regional fallback. Coastal capital is Hellenic; surrounding rural baronies are not homogenized.'})
save('source_data/040/historical_overrides.json',json.dumps(overrides,ensure_ascii=False,indent=1))
rows=list(csv.DictReader(io.StringIO(read('source_data/040/county_realms.csv'))))
for r in rows:
 if r['county_id'] in labels:r['implemented_county_name']=labels[r['county_id']]
f=io.StringIO();w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
save('source_data/040/county_realms.csv',f.getvalue())
revision=json.loads(read('source_data/040/revision.json'))
revision['nomad_settlement_exception']={'county':'c_tmutarakan','new_holding':'tribal_holding','nomadic_philosophy_removed_from':oldchar,'reason':'Settled Hermonassa under the Bosporan Kingdom; all other 322 nomadic counties retain their original government.'}
revision['coastal_capitals_refined']=settled
revision['fictional_taman_governor']='Philiskos is a fictional local office-holder, not a claim of an attested historical person.'
revision['province_history_updated']=True
revision['localization_keys_written_per_language']=len(re.findall(r'^ [^ :]+:',read('localization/english/replace/aq040_titles_l_english.yml'),re.M))
save('source_data/040/revision.json',json.dumps(revision,indent=2))
notes=read('RELEASE_NOTES_040.md')
if '## Bosporan consistency refinement' not in notes:
 notes+='''\n## Bosporan consistency refinement
Pantikapaion (Kerch) and Hermonassa (Taman) now use their attested Greek settlement names rather than the source list's broad Taurica/Maeotis fallback. Their capital holdings use the established Hellenic culture and faith; rural baronies retain their existing cultures. The new Taman governor Philiskos is explicitly fictional. Hermonassa's old nomad holding is now a tribal holding, and its ruler no longer has the nomadic_philosophy trait that would force a nomadic government back on game start. This is the single intentional reduction from 323 to 322 nomadic counties. No government or faith definitions are altered.
References for these identifications: https://en.wikipedia.org/wiki/Pantikapaion ; https://en.wikipedia.org/wiki/Tmutarakan ; the ancient-place discussion is distinct from any modern territorial claims.
Migration sequence from the backed-up 0.3 baseline: tools/revise_040.py, then tools/polish_040.py. Do not rerun the older 0.3 generators over 0.4 without reconciling their source data.
'''
save('RELEASE_NOTES_040.md',notes)

# No runtime test: prepare a colour lookup for a faithful native-province preview using Windows GDI+.
# Full PNG remains in the supplied game archive; it is not installed as a mod asset.
archive=Path(r'C:\Users\Super\Downloads\game.zip')
reference=Path(r'C:\Users\Super\Downloads\game (1).zip')
with zipfile.ZipFile(archive) as z,zipfile.ZipFile(reference) as ref:
 definitions=z.read('game/map_data/definition.csv')
 assert hashlib.sha256(definitions).digest()==hashlib.sha256(ref.read('game/map_data/definition.csv')).digest(), 'Preview archive uses different province definitions.'
 map_rules=decode(z.read('game/map_data/default.map'))
 water=set();mountains=set()
 for category,typ,body in re.findall(r'^(sea_zones|impassable_seas|river_provinces|lakes|impassable_mountains)\s*=\s*(RANGE|LIST)\s*\{([^}]+)\}',map_rules,re.M):
  nums=list(map(int,re.findall(r'\d+',body)));target=mountains if category=='impassable_mountains' else water
  target.update(range(nums[0],nums[1]+1) if typ=='RANGE' else nums)
 realm=json.loads(read('source_data/040/realm_manifest.json'))
 state_keys=sorted(realm);state_code={k:i+1 for i,k in enumerate(state_keys)}
 county_state={r['county_id']:r['top_realm'] for r in rows}
 provstate={}
 for c in county_state:
  for b in T[c].value:
   if b.key.startswith('b_') and get(b.value,'province'):provstate[int(get(b.value,'province'))]=state_code.get(county_state[c],0)
 lines=[]
 for line in decode(definitions).splitlines():
  parts=line.split(';')
  if len(parts)<4:continue
  try:pid,red,green,blue=map(int,parts[:4])
  except ValueError:continue
  code=provstate.get(pid,0)
  if code:color=realm[state_keys[code-1]]['color']
  elif pid == 0 or pid in water:color=[154,180,202]
  else:color=[246,246,241]
  packed=(red<<16)|(green<<8)|blue
  argb=-16777216+(int(color[0])<<16)+(int(color[1])<<8)+int(color[2])
  lines.append(f'{packed};{argb};{code};{1 if pid in mountains else 0}')
 save('source_data/040/province_preview_lookup.csv','\n'.join(lines)+'\n')
 save('source_data/040/preview_labels.csv','\n'.join(str(state_code[k])+';'+realm[k]['label'] for k in state_keys)+'\n')
# Game-start consistency checks for the one settled former nomadic county.
newchar=next(n for n in parse(read('history/characters/aq_world.txt')) if n.key==oldchar)
assert not any(n.key=='trait' and n.value=='nomadic_philosophy' for n in newchar.value)
assert get(newchar.value,'culture')=='aq_hellenic'
assert H['c_tmutarakan']['government']=='tribal_government'
print(json.dumps({'files_updated':len(written),'bosporan_capitals':settled,'nomadic_counties':322,'backup':str(backup),'preview_lookup_rows':len(lines)},indent=2))
(DATA/'finishing_files.json').write_text(json.dumps({'backup':str(backup),'files':written},indent=2),encoding='utf-8')
