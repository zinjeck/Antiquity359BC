"""One-time 0.2 -> 0.3 migration. Run only on a staged copy. Religion definitions stay byte-identical."""
from pathlib import Path
import sys,zipfile,re,json,csv,hashlib
from collections import Counter
from pdx import parse,get,decode,title_tree
from revise_020 import loc_read,tint
from peoples_030 import PEOPLES,NOMAD_CULTURES,EMPIRES

root=Path(sys.argv[1]);z=zipfile.ZipFile(sys.argv[2]);loc={}
def rd(p):return (root/p).read_text(encoding='utf-8-sig')
def wr(p,s):
    p=root/p;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(s,encoding='utf-8-sig' if p.suffix=='.yml' else 'utf-8',newline='\n')
def native(p):return decode(z.read('game/'+p))
def edits(s,changes):
    for a,b,v in sorted(changes,reverse=True):s=s[:a]+v+s[b:]
    return s
def inject(s,node,key,body):
    field=next((n for n in node.value if n.key==key),None)
    pos=s.index('{',field.start if field else node.start)+1
    return (pos,pos,('\n'+body+'\n') if field else ('\n'+key+' = { '+body+' }\n'))
def setlabels(key,name):
    for suffix in ('','_collective_noun','_prefix'):loc[key+suffix]=name
religion_hashes={p.relative_to(root).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in (root/'common/religion').rglob('*') if p.is_file()}
assert 'version="0.2.0"' in rd('descriptor.mod')
ts,vparents,_=title_tree(z);ancestry={}
for c in ts:
    if c.startswith('c_'):
        a={c};p=vparents[c]
        while p:a.add(p);p=vparents[p]
        ancestry[c]=a
unknown=[(p['key'],t) for p in PEOPLES for t in p['titles'].split() if t not in ts]
assert not unknown,unknown
ct=rd('common/culture/cultures/aq_ancient_cultures.txt');cn={n.key:n for n in parse(ct)}
assert 'aq_semnonian' not in cn
new=[]
for p in PEOPLES:
    key='aq_'+p['key'];base=cn['aq_'+p['base']];s=ct[base.start:base.end]
    s=re.sub(r'^aq_\w+',key,s);s=re.sub(r'color\s*=\s*\{[^}]+\}','color = { '+tint(key)+' }',s,count=1)
    if p['base']=='slavic':s=re.sub(r'heritage\s*=\s*\w+','heritage = heritage_aq_early_slavic',s)
    if p['base']=='sinitic':s=re.sub(r'heritage\s*=\s*\w+','heritage = heritage_aq_huaxia',s)
    new.append(s);setlabels(key,p['name'])
    wr('history/cultures/'+key+'.txt',rd('history/cultures/aq_'+p['base']+'.txt'))
wr('common/culture/cultures/aq_ancient_cultures.txt',ct+'\n\n'+'\n\n'.join(new)+'\n')
wr('common/culture/pillars/aq030_heritages.txt','heritage_aq_early_slavic = { type = heritage color = { 112 161 83 } }\nheritage_aq_huaxia = { type = heritage color = { 196 153 65 } }\n')
for k,name in [('heritage_aq_early_slavic','Early Slavic'),('heritage_aq_huaxia','Huaxia')]:
    loc[k]=name;loc[k+'_name']=name;loc[k+'_collective_noun']=name
# Egyptian and Persian keep native canonical IDs. Arabic has exactly three cultures.
remap={'aq_egyptian':'egyptian','ancient_egyptian':'egyptian','aq_persian':'persian','aq_arabian':'bedouin','yemeni':'aq_sabaean'}
for p in root.rglob('*.txt'):
    if 'tools' in p.parts or 'religion' in p.parts or 'cultures' in p.parts:continue
    s=p.read_text(encoding='utf-8-sig')
    s=re.sub(r'\b(culture\s*=\s*)(\w+)',lambda m:m[1]+remap.get(m[2],m[2]),s)
    s=re.sub(r'\bculture:(\w+)',lambda m:'culture:'+remap.get(m[1],m[1]),s)
    if s!=p.read_text(encoding='utf-8-sig'):p.write_text(s,encoding='utf-8')
# Rewrite effective native files, removing duplicated definitions instead of hiding their labels.
for p,removed in [('00_arabic.txt',{'egyptian','yemeni'}),('00_dead.txt',{'ancient_egyptian'}),('00_iranian.txt',{'persian'})]:
    rel='common/culture/cultures/'+p;s=rd(rel) if (root/rel).exists() else native(rel)
    s=edits(s,[(n.start,n.end,'') for n in parse(s) if n.key in removed])
    if p=='00_arabic.txt':
        changes=[]
        for n in parse(s):
            q=s[n.start:n.end]
            if n.key=='maghrebi':q=q.replace('heritage_arabic','heritage_berber')
            if n.key=='levantine':q=re.sub(r'\bcreated\s*=\s*\S+','created = 1.1.1',q)
            changes.append((n.start,n.end,q))
        s=edits(s,changes)
    wr(rel,s)
s=rd('common/culture/cultures/aq_ancient_cultures.txt');changes=[]
for n in parse(s):
    q=s[n.start:n.end]
    if n.key=='aq_arabian':q=''
    elif n.key=='aq_egyptian':q=q.replace('aq_egyptian =','egyptian =',1).replace('heritage_aq_egyptian','heritage_egyptian').replace('language_aq_egyptian','language_egyptian')
    elif n.key=='aq_persian':q=q.replace('aq_persian =','persian =',1)
    changes.append((n.start,n.end,q))
wr('common/culture/cultures/aq_ancient_cultures.txt',edits(s,changes))
# Empty old history files avoid two initializations while preserving an auditable migration.
for old,newid in [('aq_egyptian','egyptian'),('aq_persian','persian')]:
    wr('history/cultures/'+newid+'.txt',rd('history/cultures/'+old+'.txt'))
    wr('history/cultures/'+old+'.txt','# Canonical culture is '+newid+'.\n')
wr('history/cultures/bedouin.txt',rd('history/cultures/aq_arabian.txt'))
wr('history/cultures/levantine.txt',rd('history/cultures/aq_aramaic.txt'))
wr('history/cultures/aq_arabian.txt','# Canonical culture is bedouin.\n')
for removed in ('ancient_egyptian','yemeni'):
    wr('history/cultures/'+removed+'.txt','# Replaced by the canonical scenario culture.\n')
for p in (root/'common/culture/pillars').glob('*.txt'):
    s=p.read_text(encoding='utf-8-sig');q=edits(s,[(n.start,n.end,'') for n in parse(s) if n.key in ('heritage_aq_egyptian','language_aq_egyptian')])
    if q!=s:p.write_text(q,encoding='utf-8')
setlabels('egyptian','Egyptian');setlabels('persian','Persian');setlabels('bedouin','Bedouin');setlabels('levantine','Mashriqi');setlabels('aq_sabaean','Sabaean')
loc['heritage_egyptian_name']='Egyptian';loc['heritage_egyptian_collective_noun']='Egyptian';loc['language_egyptian_name']='Late Egyptian'
# Work from current map ownership, while geographic footprints come from the source map.
lt=rd('common/landed_titles/aq_world.txt');titles={};parents={}
def walk(ns,parent=None):
    for n in ns:
        if re.match('^[ekdcb]_',n.key) and isinstance(n.value,list):titles[n.key]=n;parents[n.key]=parent;walk(n.value,n.key)
walk(parse(lt))
pt=rd('history/provinces/aq_world.txt');pn={n.key:n for n in parse(pt)}
counties={};oldcounties={};baronies={}
for c,n in titles.items():
    if not c.startswith('c_'):continue
    bs=[b for b in n.value if b.key.startswith('b_') and get(b.value,'province')]
    if not bs:continue
    baronies[c]=bs;v=pn[get(bs[0].value,'province')].value
    cu,fa=get(v,'culture'),get(v,'religion');oldcounties[c]=(cu,fa)
    for p in PEOPLES:
        if ancestry[c]&set(p['titles'].split()):cu='aq_'+p['key']
    # Religion distribution only: preserve every existing faith definition and tenet.
    if cu.removeprefix('aq_') in NOMAD_CULTURES:
        fa='aq_faith_steppe' if cu not in ('aq_donghu','aq_ordos','aq_steppe_eastern') else 'aq_faith_asian'
    if cu in {'aq_'+x for x in 'qin jin_wei jin_han zhao yan qi lu song zhou chu wu_early ba shu zhongshan'.split()}:fa='aq_faith_chinese'
    if cu in {'aq_'+x for x in 'minyue dongou nanyue_early luoyue dian yelang'.split()}:fa='aq_faith_asian'
    if cu=='aq_qiang_early':fa='aq_faith_himalayan'
    if cu=='aq_elamite':fa='aq_faith_mesopotamian'
    counties[c]=(cu,fa)
changes=[]
for c,bs in baronies.items():
    cu,fa=counties[c]
    for b in bs:
        n=pn[get(b.value,'province')];q=pt[n.start:n.end]
        q=re.sub(r'\bculture\s*=\s*\w+','culture = '+cu,q);q=re.sub(r'\breligion\s*=\s*\w+','religion = '+fa,q)
        changes.append((n.start,n.end,q))
wr('history/provinces/aq_world.txt',edits(pt,changes))
# De facto ranks. Retain major states and their internal hierarchy; dissolve generic independent duchies.
ht=rd('history/titles/aq_world.txt');hn={n.key:n for n in parse(ht)}
def atstart(n):
    v={}
    for x in n.value:
        if re.match(r'^\d+\.\d+\.\d+$',x.key) and tuple(map(int,x.key.split('.')))<=(642,5,1):
            v.update({k.key:k.value for k in x.value})
    return v
states={k:atstart(n) for k,n in hn.items()};demoted=set()
for k,v in states.items():
    if k.startswith('d_') and v.get('holder','').startswith('aq_chief_') and v.get('liege','0')=='0':demoted.add(k)
nomad_counties={c for c,(cu,fa) in counties.items() if cu.removeprefix('aq_') in NOMAD_CULTURES}
# Preserve settled imperial provinces: a people's presence does not make a satrapy nomadic.
def toprealm(k):
    seen=set()
    while states.get(k,{}).get('liege','0') not in ('0',''):
        if k in seen:raise AssertionError('Liege cycle')
        seen.add(k);k=states[k]['liege']
    return k
nomad_counties={c for c in nomad_counties if not toprealm(c).startswith(('e_','k_aq_persia')) and toprealm(c) not in ('k_aq_persia','k_aq_nanda')}
nomad_rulers={states[c]['holder'] for c in nomad_counties}
changes=[]
for k,n in hn.items():
    q=ht[n.start:n.end]
    if k in demoted:q=k+' = { 642.5.1 = { holder = 0 liege = 0 } }'
    else:
        if states[k].get('liege') in demoted:q=re.sub(r'\bliege\s*=\s*[\w-]+','liege = 0',q)
        if k in nomad_counties:
            q=q.replace('government = tribal_government','government = nomad_government')
            q=re.sub(r'\bsuccession_laws\s*=\s*\{[^}]*\}','',q)
    changes.append((n.start,n.end,q))
wr('history/titles/aq_world.txt',edits(ht,changes))
# Generated local families follow the population of their home county. Named elites remain independent.
ch=rd('history/characters/aq_world.txt');cns={n.key:n for n in parse(ch)};assign={}
for c,(cu,fa) in counties.items():
    holder=states[c]['holder']
    if holder.startswith('aq_chief_'):
        for ident in (holder,holder+'_spouse',holder+'_son',holder+'_daughter'):assign[ident]=(cu,fa)
for key,cu in {'aq_qin':'qin','aq_qi':'qi','aq_zhao':'zhao','aq_yan':'yan','aq_wei':'jin_wei','aq_han':'jin_han','aq_chu':'chu','aq_zhou':'zhou','aq_yue':'yue'}.items():
    if key in cns:assign[key]=('aq_'+cu,get(cns[key].value,'religion'))
changes=[]
for key,n in cns.items():
    q=ch[n.start:n.end]
    if key in assign:
        cu,fa=assign[key];q=re.sub(r'\bculture\s*=\s*\w+','culture = '+cu,q);q=re.sub(r'\breligion\s*=\s*\w+','religion = '+fa,q)
    if key in nomad_rulers and 'trait = nomadic_philosophy' not in q:q=q.replace('{','{\n trait = nomadic_philosophy',1)
    changes.append((n.start,n.end,q))
wr('history/characters/aq_world.txt',edits(ch,changes))
# Title creation gates also apply to automatic partition creation.
changes=[]
for k,n in titles.items():
    if k[0] not in 'edk' or not any(x.key.startswith(('k_','d_','c_')) for x in n.value):continue
    gate={'d':'aq_can_form_chiefdom_union_trigger','k':'aq_can_form_kingdom_trigger','e':'aq_can_form_empire_trigger'}[k[0]]
    for field in ('can_create','can_create_on_partition'):changes.append(inject(lt,n,field,gate+' = yes'))
wr('common/landed_titles/aq_world.txt',edits(lt,changes))
for k,(name,adj) in EMPIRES.items():loc[k]=name;loc[k+'_adj']=adj
# Keep the startup hooks small; government assignment is conditional, not a global tribal reset.
wr('common/on_action/game_start.txt','''on_game_start = {
 effect = {
  set_global_variable = { name = is_game_start_date days = 1 }
  set_global_variable = { name = aq_scenario_active value = yes }
  set_global_variable = { name = start_epidemic_grace value = yes years = 10 }
 }
}
on_game_start_after_lobby = {
 effect = {
  every_living_character = {
   limit = { is_landed = yes }
   if = {
    limit = { has_trait = nomadic_philosophy has_mpo_dlc_trigger = yes }
    change_government = nomad_government
    if = { limit = { exists = domicile } domicile = { change_herd = 500 } }
   }
   else_if = { limit = { government_has_flag = government_is_nomadic NOT = { has_mpo_dlc_trigger = yes } } change_government = tribal_government }
   aq_early_nomad_balance_effect = yes
  }
 }
}
''')
# Update only localization keys owned by this revision; remove previous duplicate definitions.
for lang in ('english','french','german','spanish','russian','simp_chinese','korean','japanese','polish'):
    for p in (root/'localization'/lang).rglob('*.yml'):
        lines=p.read_text(encoding='utf-8-sig').splitlines(True)
        obsolete=set(loc)|{'heritage_aq_egyptian','heritage_aq_egyptian_name','heritage_aq_egyptian_collective_noun','language_aq_egyptian','language_aq_egyptian_name'}
        p.write_text(''.join(line for line in lines if not ((m:=re.match(r'\s+([^ :]+):',line)) and m[1] in obsolete)),encoding='utf-8-sig')
    wr('localization/'+lang+'/replace/aq030_l_'+lang+'.yml','l_'+lang+':\n'+''.join(f' {k}:0 "{v}"\n' for k,v in sorted(loc.items())))
wr('descriptor.mod',rd('descriptor.mod').replace('version="0.2.0"','version="0.3.0"'))
assert all(hashlib.sha256((root/p).read_bytes()).hexdigest()==h for p,h in religion_hashes.items()),'Religion definitions were changed'
with (root/'source_data/county_peoples_030.csv').open('w',encoding='utf-8-sig',newline='') as f:
    w=csv.writer(f);w.writerow(['county','old_culture','culture','faith','government','holder','former_liege'])
    for c,(cu,fa) in sorted(counties.items()):w.writerow([c,oldcounties[c][0],cu,fa,'nomad_government' if c in nomad_counties else 'tribal_government',states[c]['holder'],states[c].get('liege','0')])
summary={'new_cultures':len(PEOPLES),'active_cultures':len(set(c for c,f in counties.values())),
    'dissolved_independent_duchies':len(demoted),'nomadic_counties':len(nomad_counties),'nomadic_rulers':len(nomad_rulers),
    'religion_definitions_sha256':religion_hashes,'suebian_counties_before':sum(c=='aq_suebian' for c,f in oldcounties.values()),'suebian_counties_after':sum(c=='aq_suebian' for c,f in counties.values()),'in_game_tested':False}
wr('source_data/revision_030.json',json.dumps(summary,indent=2));print(json.dumps({k:v for k,v in summary.items() if k!='religion_definitions_sha256'},indent=2))
