"""Apply progression hooks and finalize the staged population revision."""
from pathlib import Path
import sys,zipfile,re,csv,json
from pdx import parse,get,decode
from revise_020 import loc_read
root=Path(sys.argv[1]);z=zipfile.ZipFile(sys.argv[2])
def rd(p):return (root/p).read_text(encoding='utf-8-sig')
def wr(p,s):
    p=root/p;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(s,encoding='utf-8-sig' if p.suffix=='.yml' else 'utf-8')
def source(p):
    if (root/p).exists():return rd(p)
    s=decode(z.read('game/'+p))
    return re.sub(r'(?<![\w.])(\d{3,4})(\.\d{1,2}\.\d{1,2})(?![\w.])',lambda m:str(int(m[1])+1000)+m[2],s)
def apply(s,changes):
    for a,b,v in sorted(changes,reverse=True):s=s[:a]+v+s[b:]
    return s
def prepend_block(s,n,field,body):
    f=next(x for x in n.value if x.key==field);pos=s.index('{',f.start)+1
    return pos,pos,'\n'+body+'\n'
# Both offer and join routes enforce the same cap. Existing engine validity checks remain.
path='common/character_interactions/09_mpo_interactions.txt';s=source(path);changes=[]
for n in parse(s):
    who={'offer_confederation_interaction':'actor','join_confederation_interaction':'recipient'}.get(n.key)
    if who:changes.append(prepend_block(s,n,'is_valid_showing_failures_only','scope:'+who+' = { aq_confederation_room_trigger = yes }'))
wr(path,apply(s,changes))
# County conquest and migration remain usable; larger wars need political technology.
for filename,requirements in {
    '00_nomadic_conquest.txt':{'nomadic_conquest_duchy_cb':'aq_can_form_chiefdom_union_trigger = yes'},
    '09_mpo_wars.txt':{'mpo_nomad_invasion_cb':'aq030_large_conquest_trigger = yes','mpo_gok_onslaught_cb':'aq030_large_conquest_trigger = yes'},
    '00_subjugation.txt':{'tribal_subjugation_cb':'trigger_if = { limit = { government_has_flag = government_is_nomadic } aq030_large_conquest_trigger = yes }'},
}.items():
    p='common/casus_belli_types/'+filename;s=source(p);changes=[]
    for n in parse(s):
        if n.key in requirements:changes.append(prepend_block(s,n,'allowed_for_character',requirements[n.key]))
    assert changes,filename
    wr(p,apply(s,changes))
p='common/script_values/99_casus_belli_values.txt';s=source(p);n=next(n for n in parse(s) if n.key=='common_cb_cost_multiplier')
body='''
 if = {
  limit = { scope:attacker = { government_has_flag = government_is_nomadic NOT = { culture = { has_innovation = innovation_aq_confederate_administration } } } }
  multiply = { value = 2 desc = aq030_war_cost }
 }
'''
wr(p,s[:n.end-1]+body+s[n.end-1:])
p='common/on_action/yearly_on_actions.txt';s=rd(p);n=next(n for n in parse(s) if n.key=='yearly_playable_pulse')
wr(p,apply(s,[prepend_block(s,n,'effect','aq_early_nomad_balance_effect = yes')]))
p='common/on_action/game_start.txt';s=rd(p).replace('change_government = nomad_government\n','change_government = nomad_government\n    add_realm_law = nomadic_authority_1\n');wr(p,s)
# Nomad capitals need the native nomad holding. Other baronies remain empty.
rows=list(csv.DictReader((root/'source_data/county_peoples_030.csv').open(encoding='utf-8-sig')))
nomads={r['county'] for r in rows if r['government']=='nomad_government'}
county_provs={}
def walk(ns):
    for n in ns:
        if n.key.startswith('c_') and isinstance(n.value,list):
            bs=[b for b in n.value if b.key.startswith('b_') and isinstance(b.value,list)]
            county_provs[n.key]=[get(b.value,'province') for b in bs if get(b.value,'province')]
        if isinstance(n.value,list):walk(n.value)
walk(parse(rd('common/landed_titles/aq_world.txt')))
nomad_provs={p for c in nomads for p in county_provs[c]}
p='history/provinces/aq_world.txt';s=rd(p);changes=[]
for n in parse(s):
    if n.key in nomad_provs:
        q=s[n.start:n.end].replace('holding = tribal_holding','holding = nomad_holding');changes.append((n.start,n.end,q))
wr(p,apply(s,changes))
# Correct the family assignment loop from the initial staged pass, and dynasty metadata.
p='history/characters/aq_world.txt';s=rd(p);ns={n.key:n for n in parse(s)};family={};dynasties={}
for r in rows:
    h=r['holder']
    if h.startswith('aq_chief_'):
        for ident in (h,h+'_spouse',h+'_son',h+'_daughter'):family[ident]=(r['culture'],r['faith'])
        dynasties[get(ns[h].value,'dynasty')]=r['culture']
changes=[]
for key,(cu,fa) in family.items():
    if key not in ns:continue
    n=ns[key];q=s[n.start:n.end]
    q=re.sub(r'\bculture\s*=\s*\w+','culture = '+cu,q);q=re.sub(r'\breligion\s*=\s*\w+','religion = '+fa,q)
    changes.append((n.start,n.end,q))
wr(p,apply(s,changes))
for f in (root/'common/dynasties').glob('*.txt'):
    s=f.read_text(encoding='utf-8-sig');changes=[]
    for n in parse(s):
        if n.key in dynasties:changes.append((n.start,n.end,re.sub(r'\bculture\s*=\s*\w+','culture = '+dynasties[n.key],s[n.start:n.end])))
    if changes:f.write_text(apply(s,changes),encoding='utf-8')
loc={
'innovation_aq_tribal_councils':'Tribal Councils',
'innovation_aq_tribal_councils_desc':'Recognized assemblies and negotiated obligations allow chiefdom unions, duchy-scale nomadic conquest and leagues of up to six independent rulers.',
'innovation_aq_confederate_administration':'Confederate Administration',
'innovation_aq_confederate_administration_desc':'Envoys, durable levies and a shared political order support larger confederations, nomadic kingdoms and empire formation. Requires Middle Antiquity, available from 100 BC.',
'aq030_chiefdom_union_requirement':'Requires Tribal Councils, or an existing kingdom or empire.',
'aq030_kingdom_requirement':'Requires Tribal Councils and Exalted among Men fame; nomads require Confederate Administration and Living Legend fame. Existing kings and emperors are exempt.',
'aq030_empire_requirement':'Requires Confederate Administration and Living Legend fame, or an existing empire.',
'aq030_confederation_limit':'An early league can contain three rulers, or six with Tribal Councils. Confederate Administration removes this limit.',
'aq030_large_conquest_requirement':'Large nomadic conquest requires Confederate Administration.',
'aq030_war_cost':'Early nomadic war organization',
'aq030_fragile_tribal_authority':'Fragile Tribal Authority',
'aq030_fragile_tribal_authority_desc':'Tribal loyalties limit early nomadic government until Confederate Administration is discovered.',
'aq030_overextended_confederation':'Overextended Confederation',
'aq030_overextended_confederation_desc':'More than eight counties strain a nomadic realm without Confederate Administration.',
'aq030_count_male':'Chief','aq030_count_female':'Chieftess','aq030_county':'Chiefdom',
'aq030_duke_male':'High Chief','aq030_duke_female':'High Chieftess','aq030_duchy':'Chiefdom Union',
}
for lang in ('english','french','german','spanish','russian','simp_chinese','korean','japanese','polish'):
    p='localization/'+lang+'/replace/aq030_l_'+lang+'.yml';entries=loc_read(rd(p));entries.update(loc)
    wr(p,'l_'+lang+':\n'+''.join(f' {k}:0 "{v}"\n' for k,v in sorted(entries.items())))
print('Progression hooks, native nomad holdings, family histories and localization finalized.')
