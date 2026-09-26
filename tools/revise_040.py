"""Apply the supplied naming inventory and the county-resolution 359 BC political revision.
One-time migration from 0.3.0. Reads the actual working tree, backs up changed files,
validates structural invariants before writing, and never launches the game.
The original name list and a PDF-to-title-ID concordance are kept in source_data/040.
"""
from pathlib import Path
from collections import defaultdict, Counter
import sys, re, json, hashlib, datetime, copy, csv, io
from pdx import parse, get, Node
from titles_040 import ROOT, START, read, index_titles, start_fields, current_localization

VERSION='0.4.0'
DATE='642.5.1'
DATA=ROOT/'source_data/040'
manifest=json.loads(read('source_data/040/title_manifest.json'))
assert len(manifest)==4760
assert 'version="0.3.0"' in read('descriptor.mod'), 'This migration requires the inspected 0.3.0 baseline.'
source=read('common/landed_titles/aq_world.txt')
T,parents=index_titles(source)
original_parents=parents.copy()
children={k:[n.key for n in v.value if n.key in T and parents[n.key]==k] for k,v in T.items()}
orig_children=copy.deepcopy(children)
properties=defaultdict(dict)
new_titles={}
loc={}
old_loc=current_localization()
changes=[]
Hsource=read('history/titles/aq_world.txt')
Hnodes={n.key:n for n in parse(Hsource)}
H={k:start_fields(n) for k,n in Hnodes.items()}
Hbefore=copy.deepcopy(H)
Csource=read('history/characters/aq_world.txt')
C={n.key:n for n in parse(Csource)}
new_characters={}
character_updates=defaultdict(dict)
new_dynasties={}
provenance=[]
outputs={}
rank={'b':0,'c':1,'d':2,'k':3,'e':4,'h':5}
counties=[k for k in T if k.startswith('c_') and any(x.key.startswith('b_') and get(x.value,'province') for x in T[k].value)]
assert len(counties)==3476
province_source=read('history/provinces/aq_world.txt')
province_nodes={n.key:n for n in parse(province_source)}
religion_hashes={p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in (ROOT/'common/religion').rglob('*') if p.is_file()}
culture_hash=hashlib.sha256((ROOT/'common/culture/cultures/aq_ancient_cultures.txt').read_bytes()).hexdigest()
culture_ids={n.key for n in parse(read('common/culture/cultures/aq_ancient_cultures.txt'))}
culture_ids.update(['persian','egyptian','bedouin','levantine'])

def put(rel,s): outputs[rel]=s

def descendants(k,tier='c'):
    result=[]
    for child in children.get(k,[]):
        if child.startswith(tier+'_'): result.append(child)
        result.extend(descendants(child,tier))
    return result

def native_ancestor(k,tier):
    seen=set()
    while k and k not in seen:
        if k.startswith(tier+'_'):return k
        seen.add(k);k=manifest.get(k,{}).get('parent')
    return None

def primary_titles(hist):
    primary={}
    for k,v in hist.items():
        h=v.get('holder','0')
        if h!='0' and (h not in primary or rank[k[0]]>rank[primary[h][0]]):primary[h]=k
    return primary

primary=primary_titles(H)
def top_realm(k,hist=H,primary=primary):
    seen=set()
    while True:
        assert k not in seen, 'Title/holder liege cycle: '+k
        seen.add(k);v=hist.get(k,{})
        p=primary.get(v.get('holder','0'))
        # A ruler's primary title determines the ownership of their personal domain.
        if p and rank[p[0]]>rank[k[0]]:k=p;continue
        l=v.get('liege','0')
        if l and l!='0':k=l;continue
        return k

before_realm={c:top_realm(c) for c in counties}
kingdom_for={c:next((a for a in [parents.get(parents.get(c))] if a and a.startswith('k_')),None) for c in counties}
# De jure nesting is regular in the baseline, but derive ancestors instead of relying on it.
for c in counties:
    a=c
    while a and not a.startswith('k_'):a=parents.get(a)
    kingdom_for[c]=a

state_holders={k:v['holder'] for k,v in H.items() if k.startswith('k_aq_') and v.get('holder','0')!='0'}
state_empire={k:('e_aq_persia' if k.startswith('k_aq_persia_') else None) for k in state_holders}
state_colors={
 'e_aq_persia':(166,220,233),'k_aq_macedon':(188,194,116),'k_aq_egypt':(102,219,112),
 'k_aq_carthage':(126,190,130),'e_aq_nanda':(73,204,223),'k_aq_kush':(188,208,82),
 'k_aq_qin':(202,205,134),'k_aq_zhao':(170,211,158),'k_aq_wei':(192,158,218),
 'k_aq_han':(227,190,121),'k_aq_qi':(133,200,192),'k_aq_song':(213,141,186),
 'k_aq_chu':(233,153,142),'k_aq_yan':(196,222,197),'k_aq_zhou':(222,208,155),
 'k_aq_yue':(173,209,175),'k_aq_lanka':(179,145,205),'k_aq_saba':(218,166,110),
 'k_aq_rome':(179,76,68),'k_aq_etruria':(156,120,187),'k_aq_bosporus':(229,203,85),
 'k_aq_syracuse':(123,166,205),'k_aq_thrace':(185,160,98),'k_aq_illyria':(171,184,133),
 'k_aq_epirus':(151,187,149),'k_aq_athens':(92,154,208),'k_aq_sparta':(188,104,83),
 'k_aq_thebes':(139,132,183),'k_aq_chalcidice':(153,178,87),'k_aq_paeonia':(200,180,139),
}
state_capitals={k:get(T[k].value,'capital') for k in state_holders}
state_labels={k:old_loc.get(k,k) for k in state_holders}
state_labels.update({'e_aq_persia':'Achaemenid Empire','k_aq_macedon':'Macedon','k_aq_egypt':'Kemet',
 'k_aq_bosporus':'Bosporan Kingdom','e_aq_nanda':'Nanda','k_aq_nanda':'Magadha'})

# Apply the user's names to the exact title keys. A regional fallback is not secretly promoted to evidence.
retired=set()
for key,row in manifest.items():
    if row['new']=='REMOVE':retired.add(key);continue
    loc[key]=row['new'];loc[key+'_adj']=row['new']
    if row['tag']=='M' and key not in ('k_france',):retired.add(key)
# Existing satrapal crowns are derived from native crowns and need the same localization coverage.
for key in T:
    if key.startswith('k_aq_persia_'):
        original='k_'+key.removeprefix('k_aq_persia_')
        if original in manifest:state_labels[key]=manifest[original]['new']
# Source date/geography corrections are explicit, localized overrides, recorded in the audit.
overrides={
 'd_jawf':('Dumat al-Jandal',"The source confuses northern al-Jawf with the southern Arabian Ma'in kingdom."),
 'c_al_jawf':('Dumat al-Jandal',"Northern Arabian oasis, not the Minaean capital in Yemen."),
 'd_bucellaria':('Northern Phrygia',"Galatian settlement postdates 359 BC; retain the pre-Galatian regional name."),
 'c_hadrianopolis':('Paphlagonian Interior',"Avoid a Roman imperial foundation name and the source's later Galatia fallback."),
 'k_galicia-volhynia':('Upper Dniester Lands',"Medieval Galicia-Volhynia was inadvertently retained in the supplied list."),
}
for key,(name,reason) in overrides.items():
    if key in T:loc[key]=name;loc[key+'_adj']=name;provenance.append({'title':key,'source_name':manifest.get(key,{}).get('new'),'implemented':name,'reason':reason})

# Mutable title tree: move complete definitions, never fabricate a county or change a province ID.
def move(key,new_parent):
    old=parents.get(key)
    if old==new_parent:return
    if old:children[old].remove(key)
    parents[key]=new_parent
    if new_parent:children[new_parent].append(key)
    changes.append({'title':key,'from':old,'to':new_parent})

def add_title(key,parent,label,capital=None,color=(165,157,131)):
    assert key not in T and key not in new_titles,key
    gate={'d':'aq_can_form_chiefdom_union_trigger','k':'aq_can_form_kingdom_trigger','e':'aq_can_form_empire_trigger'}[key[0]]
    new_titles[key]=(f'{key} = {{\n color = {{ {color[0]} {color[1]} {color[2]} }}\n'
      ' can_be_named_after_dynasty = no\n can_use_nomadic_naming = no\n'
      f' can_create = {{ {gate} = yes }}\n can_create_on_partition = {{ {gate} = yes }}\n'
      +(f' capital = {capital}\n' if capital else '')+'}\n')
    children[key]=[];parents[key]=None
    loc[key]=label;loc[key+'_adj']=label
    if parent:move(key,parent)

def add_state(key,label,capital,empire,holder=None,color=(165,157,131)):
    if key not in T and key not in new_titles:add_title(key,empire or 'e_byzantium',label,capital,color)
    state_holders[key]=holder
    state_empire[key]=empire
    state_capitals[key]=capital
    state_labels[key]=label
    state_colors[key]=color

# Keep tribal chiefdoms outside the colored states. They remain within geographical de jure regions.
def assign(cs,state):
    for c in cs:
        assert c in counties,c
        kingdom_for[c]=state

def territory(*keys):
    found=[]
    for k in keys:
        assert k in T,k
        found+=([k] if k.startswith('c_') else descendants(k))
    return found

def release(cs):
    for c in cs:
        dest=native_ancestor(c,'k')
        assert dest in T,(c,dest)
        kingdom_for[c]=dest

# Gaul is one de jure crown, not one invented pan-Gallic monarchy at the start.
for k in ('k_aquitaine','k_brittany'):
    for d in list(children[k]):move(d,'k_france')
loc['k_france']='Gaul';loc['k_france_adj']='Gallic'
properties['k_france']['capital']='c_ile_de_france'
# Retain e_france only as an unheld, uncreatable compatibility/de jure wrapper.
retired.update(['e_france','k_aquitaine','k_brittany'])

# Persian administration: smaller ancient regional satrapies replace medieval kingdom-shaped blobs.
# Count-level boundaries are gameplay reconstructions, not claims about surveyed satrapy boundaries.
persian_states=[
 ('lydia','Lydia','c_lydia',['d_ephese','d_thracesia']),
 ('caria','Caria','c_caria',['c_caria','c_lycia']),
 ('cappadocia','Cappadocia','c_kaisereia',['d_cappadocia','d_charsianon','d_sebasteia']),
 ('cilicia','Cilicia','c_cilicia',['d_cilicia','c_pamphylia']),
 ('hyrcania','Hyrcania','c_gurgan',['d_tabaristan','d_gurgan']),
 ('carmania','Carmania','c_kirman',['d_kirman','d_hormuz','d_jabal_kufs']),
 ('bactria','Bactria','c_balkh',['d_balkh','d_badakhshan','d_khuttal']),
 ('margiana','Margiana','c_merv',['d_merv']),
 ('aria','Aria','c_herat',['d_herat','d_ghur']),
 ('drangiana','Drangiana','c_zaranj',['d_sistan']),
 ('iberia','Iberia','c_tbilisi',['d_georgia']),
]
for slug,label,cap,keys in persian_states:
    key='k_aq_persia_'+slug
    add_state(key,label,cap,'e_aq_persia',color=state_colors['e_aq_persia'])
    assign(territory(*keys),key)
assign(territory('d_bucellaria','c_phrygia'),'k_aq_persia_anatolia')
assign(territory('d_hamadan','d_kermanshah','d_rayy','d_azerbaijan'),'k_aq_persia_daylam')
assign(territory('d_amman'),'k_aq_persia_jerusalem')
state_capitals.update({'k_aq_persia_cyprus':'c_famagusta','k_aq_persia_nikaea':'c_mysia',
 'k_aq_persia_anatolia':'c_phrygia','k_aq_persia_pontus':'c_sinope',
 'k_aq_persia_transoxiana':'c_samarkand','k_aq_persia_khorasan':'c_damghan',
 'k_aq_persia_daylam':'c_hamadan','k_aq_persia_jerusalem':'c_jerusalem',
 'k_aq_persia_syria':'c_damascus','k_aq_persia_mesopotamia':'c_baghdad',
 'k_aq_persia_jazira':'c_mosul'})
state_holders['k_aq_persia_nikaea']='aq_artabazos'
state_holders['k_aq_persia_cyprus']='aq_evagoras'
state_labels['k_aq_persia_nikaea']='Hellespontine Phrygia'
state_labels['k_aq_persia_anatolia']='Phrygia'

# Egypt is independent. Cyrenaica is not simply a western Egyptian province in this start.
add_state('k_aq040_kyrene','Kyrene','c_barqa',None,color=(179,212,126))
move('k_aq040_kyrene','e_aq_nile')
assign(territory('d_cyrenaica'),'k_aq040_kyrene')

# Do not back-project Sparta's pre-369 possession of Messenia or later Macedonian conquests.
add_state('k_aq040_messenia','Messenia','c_messenia',None,color=(145,190,146))
assign(['c_messenia'],'k_aq040_messenia')
add_state('k_aq040_byzantion','Byzantion','c_byzantion',None,color=(130,184,192))
assign(['c_byzantion'],'k_aq040_byzantion')
release(['c_tivoli','c_aetolia','c_cephalonia','c_buthrotum'])
# The Chersonese was contested: no forced Athenian annexation is claimed in this reconstruction.
release(['c_kalliopolis'])
add_state('k_aq040_west_thrace','Western Thrace','c_mosynopolis',None,color=(176,182,107))
add_state('k_aq040_central_thrace','Central Thrace','c_philippopolis',None,color=(194,176,123))
move('k_aq040_west_thrace','e_aq_balkan');move('k_aq040_central_thrace','e_aq_balkan')
assign(['c_mosynopolis'],'k_aq040_west_thrace')
assign(['c_philippopolis','c_kran','c_rhodopes'],'k_aq040_central_thrace')
# Serres contains a broad Strymon/Amphipolis district; it is not awarded to Philip in 359.
release(['c_serres'])
state_labels['k_aq_thrace']='Odrysia'
assign(['c_tmutarakan'],'k_aq_bosporus')

# Punic possessions are coastal. Interior Sardinia/Numidia is not annexed wholesale.
release(['c_logudoro','c_tortoli','c_constantine','c_waddan'])
assign(['c_cadiz','c_iviza'],'k_aq_carthage')
# Gadir represents the map's Punic coastal sphere; direct control in 359 is not treated as certain.
provenance.append({'title':'c_cadiz','implemented':'Punic sphere under Carthage','reason':'Map-driven coastal affiliation. This is not a claim of a securely dated Carthaginian annexation.'})

# Nanda is explicitly retained from the supplied scenario map, despite disputed chronology.
# Do not replace the requested state silently with a different Magadhan dynasty.
add_title('e_aq_nanda',None,'Nanda','c_magadha',state_colors['e_aq_nanda'])
H['e_aq_nanda']={'holder':'aq_nanda','government':'tribal_government','liege':'0'}
move('k_aq_nanda','e_aq_nanda');state_empire['k_aq_nanda']='e_aq_nanda'
assign(territory('d_kuru','d_tosali','d_kalinga','d_daksina_kosala'),'k_aq_nanda')
# Group Nanda's regional governors under the imperial crown instead of one oversized personal domain.
nanda_counties=[c for c in counties if kingdom_for[c]=='k_aq_nanda']
nanda_groups=defaultdict(list)
for c in nanda_counties:nanda_groups[native_ancestor(c,'k')].append(c)
for native,cs in sorted(nanda_groups.items()):
    if native=='k_bihar':continue
    slug=native[2:];key='k_aq_nanda_'+slug
    label=manifest.get(native,{}).get('new',slug.title())
    caps={'k_delhi':'c_mathura','k_kosala':'c_kanyakubja','k_bengal':'c_gauda',
          'k_gondwana':'c_ratanpur','k_orissa':'c_kataka'}
    cap=caps.get(native,cs[0])
    if cap not in cs:cap=cs[0]
    add_state(key,label,cap,'e_aq_nanda',color=state_colors['e_aq_nanda'])
    assign(cs,key)

# Warring States: period geography, not the outlines of medieval Chinese circuits.
state_capitals['k_aq_zhao']='c_mingzhou' # Handan is an actual barony in this county.
assign(territory('d_hedong'),'k_aq_zhao')
assign(territory('d_zelu','d_heyang'),'k_aq_han')
assign(['c_weizhou','c_xiangzhou'],'k_aq_wei')
assign(['c_dezhou','c_dizhou','c_qizhou','c_yunzhou'],'k_aq_qi')
assign(['c_cangzhou'],'k_aq_yan')
assign(['c_yingzhou','c_caizhou','c_huaining','c_shenzhou'],'k_aq_chu')
# No premature Zhao takeover of the Ordos plain or Qin takeover of the Qiang uplands.
release(territory('d_xinan','d_fufang','d_xingfeng'))
add_state('k_aq040_zhongshan','Zhongshan','c_zhenzhou',None,color=(198,180,125))
add_state('k_aq040_lu','Lu','c_yanzhou',None,color=(181,166,95))
add_state('k_aq040_wey','Wey','c_puzhou_2',None,color=(224,184,194))
for k in ['k_aq040_zhongshan','k_aq040_lu','k_aq040_wey']:move(k,'e_zhongyuan')
assign(['c_zhenzhou','c_dingzhou'],'k_aq040_zhongshan')
assign(['c_yanzhou'],'k_aq040_lu')
assign(['c_puzhou_2'],'k_aq040_wey')
add_state('k_aq040_shu','Shu','c_chengdu',None,color=(214,185,141))
add_state('k_aq040_ba','Ba','c_yuzhou_2',None,color=(194,161,128))
for k in ['k_aq040_shu','k_aq040_ba']:move(k,'e_liangyi')
assign(territory('d_xichuan','d_dongchuan','d_qiongnan','d_xingyuan'),'k_aq040_shu')
assign(territory('d_baqu','d_kuizhong','d_wuxin'),'k_aq040_ba')

# South Arabian polities are not a medieval Yemeni kingdom under a single Sanaa chief.
add_state('k_aq040_main',"Ma'in",'c_jawf-al-yamani',None,color=(191,190,111))
add_state('k_aq040_qataban','Qataban','c_taizz',None,color=(196,153,121))
add_state('k_aq040_hadramaut','Hadramaut','c_hadramawt',None,color=(173,159,119))
for k in ['k_aq040_main','k_aq040_qataban','k_aq040_hadramaut']:move(k,'e_arabia')
assign(territory('d_jawf-al-yamani'),'k_aq040_main')
assign(territory('d_taizz'),'k_aq040_qataban')
assign(territory('d_hadramawt'),'k_aq040_hadramaut')
# Marib, when explicitly present in a county, must remain in Saba rather than Ma'in.
for c in counties:
    if any(b.key in ('b_marib','b_ma_rib') for b in T[c].value):
        assign([c],'k_aq_saba');state_capitals['k_aq_saba']=c

# Create or reuse historical elites. Unknown local rulers remain explicitly fictional.
def named_person(variants):
    for ident,n in C.items():
        name=old_loc.get(get(n.value,'name'),get(n.value,'name','')).casefold()
        if name in {v.casefold() for v in variants}:return ident
    return None

def new_person(ident,name,culture,faith,age=40,dynasty=None,historical=False):
    assert ident not in C and ident not in new_characters,ident
    assert culture in culture_ids,culture
    key='aq040_name_'+ident.removeprefix('aq040_')
    loc[key]=name
    dyn=dynasty or 'aq040_dyn_'+ident.removeprefix('aq040_')
    if not dynasty:new_dynasties[dyn]=(name,culture)
    body=(f'# {"Historical person; birth date and attributes are authoring estimates." if historical else "Fictional regional office-holder, not an attested ancient individual."}\n'
          f'{ident} = {{\n name = {key}\n dynasty = {dyn}\n culture = {culture}\n religion = {faith}\n'
          f' diplomacy = 8\n martial = 8\n stewardship = 9\n intrigue = 6\n learning = 7\n'
          f' trait = education_stewardship_2\n {642-age}.1.1 = {{ birth = yes }}\n}}\n')
    new_characters[ident]=body
    return ident

province_culture={};province_faith={}
for c in counties:
    b=next(b for b in T[c].value if b.key.startswith('b_') and get(b.value,'province'))
    p=province_nodes[get(b.value,'province')]
    province_culture[c]=get(p.value,'culture');province_faith[c]=get(p.value,'religion')

carian=next((c for c in ['aq_carian','aq_anatolian','aq_hellenic'] if c in culture_ids))
mausolos=named_person(['Mausolus','Mausolos','Maussollos'])
if not mausolos:
    new_dynasties['aq040_dyn_hecatomnid']=('Hecatomnid',carian)
    mausolos=new_person('aq040_mausolos','Mausolos',carian,province_faith['c_caria'],age=48,dynasty='aq040_dyn_hecatomnid',historical=True)
state_holders['k_aq_persia_caria']=mausolos
for key,name,culture,cap in [('k_aq040_west_thrace','Berisades','aq_odrysian','c_mosynopolis'),('k_aq040_central_thrace','Amadokos II','aq_odrysian','c_philippopolis')]:
    ident=named_person([name]) or new_person('aq040_'+key.removeprefix('k_aq040_'),name,culture,province_faith[cap],historical=True)
    state_holders[key]=ident
character_updates['aq_song']['name']='aq040_name_ticheng';character_updates['aq_song']['culture']='aq_song'
loc['aq040_name_ticheng']='Ticheng'
character_updates['aq_zhou']['name']='aq040_name_ji_pian';loc['aq040_name_ji_pian']='Ji Pian'
loc['aq040_name_evagoras_ii']='Evagoras II';character_updates['aq_evagoras']['name']='aq040_name_evagoras_ii'
# Existing Qi ruler is kept: competing fourth-century Qi chronologies must not be silently reconciled.

# Rebuild only the de jure boundaries touched by political reallocations. Split duchies at actual county edges.
# Gaul's earlier merge is authoritative for its counties even though it is not an occupied state.
for c in counties:
    if native_ancestor(c,'k') in ('k_france','k_aquitaine','k_brittany') and parents.get(parents.get(c))=='k_france':kingdom_for[c]='k_france'
original_duchies=[k for k in T if k.startswith('d_') and any(x.startswith('c_') for x in children.get(k,[]))]
for d in original_duchies:
    cs=[c for c in list(children[d]) if c.startswith('c_')]
    byking=defaultdict(list)
    for c in cs:byking[kingdom_for[c] or parents[d]].append(c)
    if len(byking)==1:
        dest=next(iter(byking))
        if dest!=parents[d]:move(d,dest)
        continue
    oldcap=get(T[d].value,'capital')
    keep=next((k for k,v in byking.items() if oldcap in v),max(byking,key=lambda k:len(byking[k])))
    move(d,keep)
    if oldcap not in byking[keep]:properties[d]['capital']=byking[keep][0]
    for king,group in byking.items():
        if king==keep:continue
        slug=re.sub('[^a-z0-9_]','_',king.lower().removeprefix('k_'))
        new='d_aq040_'+slug+'_'+d[2:]
        label=state_labels.get(king,loc.get(d,old_loc.get(d,d)))
        add_title(new,king,label,group[0],state_colors.get(king,(160,159,142)))
        for c in group:move(c,new)

# Choose ruler IDs and capitals after all borders are settled, avoiding double-service to foreign rulers.
occupied={k:descendants(k) for k in state_holders}
assert all(v for v in occupied.values()), [k for k,v in occupied.items() if not v]
reserved={}
for k,h in state_holders.items():
    if h:reserved.setdefault(h,set()).add(k)

def fictional_for(c,suffix=''):
    ident='aq040_local_'+re.sub('[^a-zA-Z0-9_]','_',c[2:])+suffix
    if ident in new_characters:return ident
    old=Hbefore[c]['holder'];n=C.get(old)
    # Keep a plausible inherited name, but never present a generated replacement as the historical named king.
    person_name=old_loc.get(get(n.value,'name'),get(n.value,'name','Local ruler')) if n and old.startswith('aq_chief_') else 'Local ruler'
    return new_person(ident,person_name,province_culture[c],province_faith[c],age=34)

for k,cs in occupied.items():
    cap=state_capitals.get(k)
    if cap not in cs:
        cap=cs[0];state_capitals[k]=cap
    h=state_holders.get(k)
    if not h:
        h=Hbefore[cap]['holder']
        if h in reserved:h=fictional_for(cap,'_governor')
        state_holders[k]=h;reserved.setdefault(h,set()).add(k)
    properties[k]['capital']=cap
    label=state_labels[k];loc[k]=label;loc[k+'_adj']=label
    properties[k]['color']='{ '+' '.join(map(str,state_colors.get(k,state_colors.get(state_empire.get(k),(170,159,138)))))+' }'
# Recolor major states and empires without recoloring cultures or religions.
for k,color in state_colors.items():
    if k in T or k in new_titles:properties[k]['color']='{ '+' '.join(map(str,color))+' }'
loc.update({'e_aq_persia':'Achaemenid Empire','e_aq_persia_adj':'Achaemenid','e_aq_nanda':'Nanda','e_aq_nanda_adj':'Nanda'})

# All land reassigned across states or released from them receives an explicit start-date history.
active_counties=set(c for cs in occupied.values() for c in cs)
released={c for c in counties if before_realm[c].startswith(('k_aq_','e_aq_')) and c not in active_counties}
rebuilt_counties=active_counties|released
history_updates=defaultdict(dict)
for k,h in state_holders.items():
    emperor=state_empire[k]
    liege=emperor if emperor and H.get(emperor,{}).get('holder')!=h else '0'
    history_updates[k].update(holder=h,liege=liege,government='tribal_government')
history_updates['e_aq_nanda'].update(holder='aq_nanda',liege='0',government='tribal_government')
history_updates['e_aq_persia'].update(holder='aq_persia',liege='0',government='tribal_government')

# Reserve county holdings for their own crown, otherwise maintain the existing local families.
county_holders={c:Hbefore[c]['holder'] for c in counties}
for k,cs in occupied.items():
    for c in cs:
        old=county_holders[c]
        if old in reserved and k not in reserved[old]:county_holders[c]=fictional_for(c)
    county_holders[state_capitals[k]]=state_holders[k]
for c in released:
    if county_holders[c] in reserved:county_holders[c]=fictional_for(c)

# Clear old affected duchies first. Some old holders otherwise retain phantom title-based vassalage.
for d in set(original_duchies)|{k for k in new_titles if k.startswith('d_')}:
    cs=descendants(d)
    if set(cs)&rebuilt_counties or any(c in rebuilt_counties for c in [x for x in orig_children.get(d,[]) if x.startswith('c_')]):
        history_updates[d].update(holder='0',liege='0')

for k,cs in occupied.items():
    for d in [d for d in children[k] if d.startswith('d_')]:
        dc=descendants(d)
        if not dc:continue
        cap=properties[d].get('capital') or (get(T[d].value,'capital') if d in T else None)
        if cap not in dc:cap=state_capitals[k] if state_capitals[k] in dc else dc[0]
        properties[d]['capital']=cap
        dh=county_holders[cap]
        history_updates[d].update(holder=dh,liege='0' if dh==state_holders[k] else k,government='tribal_government')
        for c in dc:
            h=county_holders[c]
            # Personal domains inherit their owner's primary title; never vassalize the king under his own duke.
            l='0' if h==state_holders[k] or h==dh else d
            history_updates[c].update(holder=h,liege=l,government='tribal_government')
for c in released:
    history_updates[c].update(holder=county_holders[c],liege='0')
    # Preserve the baseline government for newly independent frontier rulers.
    if Hbefore[c].get('government'):history_updates[c]['government']=Hbefore[c]['government']

for key in retired:
    if key in T or key in new_titles:
        properties[key]['can_create']='{ always = no }'
        properties[key]['can_create_on_partition']='{ always = no }'
        history_updates[key].update(holder='0',liege='0')
# Obsolete kingdom wrappers and empty original duchies must not survive as held crowns.
for key in T:
    if key.startswith(('k_','d_')) and Hbefore.get(key,{}).get('holder','0')!='0' and not descendants(key):
        history_updates[key].update(holder='0',liege='0')

# Split duchy descriptions follow their actual region, not medieval 'X of Y' generated labels.
for k in new_titles:
    if k.startswith('d_'):
        king=parents[k];base=k.rsplit('_',1)[-1]
        # Unique political wrapper labels are intentional. Counties retain source local names.
        label=loc.get(k,state_labels.get(king,'Regional Chiefdom'))
        loc[k]=label;loc[k+'_adj']=label
for k in T:
    if k.startswith('d_aq_') and k not in manifest:
        # Derive the source duchy from a contained county's native parent when this is a split wrapper.
        cs=descendants(k)
        if cs:
            original=manifest.get(cs[0],{}).get('parent')
            if original in manifest:
                label=manifest[original]['new']
                loc[k]=label;loc[k+'_adj']=label

# Known capital city names are a separate layer from county-region labels.
# Only existing baronies are renamed; no coordinates or province identities are changed.
barony_labels={'b_thessaloniki':'Therma','b_veria':'Aigai','b_tunis':'Carthage',
 'b_constantinople':'Byzantion','b_byzantion':'Byzantion','b_handan':'Handan','b_lingshou':'Lingshou',
 'b_persepolis':'Persepolis','b_istakhr':'Persepolis','b_alexandria':'Rhakotis'}
for k,v in barony_labels.items():
    if k in T:loc[k]=v;loc[k+'_adj']=v
# Retain the exact source names for East Asia, while pointing Zhao's capital at the Handan county.

# A small second bookmark page makes the requested eastern states immediately selectable.
east_bookmarks=[]
for i,(title,char,label) in enumerate([('e_aq_nanda','aq_nanda','Mahapadma of Nanda'),('k_aq_qin','aq_qin','Quliang of Qin'),('k_aq_zhao','aq_zhao','Zhong of Zhao'),('k_aq_song','aq_song','Ticheng of Song'),('k_aq_chu','aq_chu','Xiong Liangfu of Chu')]):
    n=C[char];name='aq040_bookmark_'+char[3:];loc[name]=label
    culture=character_updates.get(char,{}).get('culture',get(n.value,'culture'));faith=get(n.value,'religion')
    birth=next((x.key for x in n.value if isinstance(x.value,list) and get(x.value,'birth')=='yes'),'602.1.1')
    east_bookmarks.append(f''' character = {{
 name = {name}
 history_id = {char}
 dynasty = {get(n.value,'dynasty')}
 type = male
 birth = {birth}
 title = {title}
 government = tribal_government
 culture = {culture}
 religion = {faith}
 difficulty = BOOKMARK_CHARACTER_DIFFICULTY_MEDIUM
 position = {{ {200+i*250} {350 if i%2==0 else 570} }}
 animation = personality_bold
 }}''')
put('common/bookmarks/bookmarks/aq040_eastern_bookmark.txt',f'''bm_aq040_east = {{
 start_date = {DATE}
 is_playable = yes
 recommended = no
 group = bm_group_aq_359
 weight = {{ value = 90 }}
'''+ '\n'.join(east_bookmarks)+'\n}\n')
loc['bm_aq040_east']='359 BC: The Eastern Kingdoms'
loc['bm_aq040_east_desc']='The Nanda realm and the competing states of Zhou China. This bookmark uses the supplied scenario map; its early Nanda chronology is a documented scenario convention.'

# Lossless title rendering applies narrow span edits and leaves all unmodified subtree bytes intact.
def field_edits(raw,node,fields,base=0):
    ed=[];added=[]
    for key,value in fields.items():
        found=[n for n in node.value if n.key==key]
        if found:
            ed.append((found[0].start-base,found[0].end-base,key+' = '+str(value)))
            for duplicate in found[1:]:ed.append((duplicate.start-base,duplicate.end-base,''))
        else:added.append(' '+key+' = '+str(value))
    if added:
        pos=raw.rfind('}')
        ed.append((pos,pos,'\n'+'\n'.join(added)+'\n'))
    return ed

def splice(raw,edits):
    for a,b,s in sorted(edits,key=lambda x:(x[0],x[1]),reverse=True):raw=raw[:a]+s+raw[b:]
    return raw

rendered={}
def render_title(k):
    if k in rendered:return rendered[k]
    if k in T:
        n=T[k];raw=source[n.start:n.end];offset=n.start
        ed=field_edits(raw,n,properties.get(k,{}),offset)
        for child in orig_children[k]:
            cn=T[child]
            ed.append((cn.start-offset,cn.end-offset,render_title(child) if parents.get(child)==k else ''))
        additions=[render_title(c) for c in children[k] if c not in orig_children[k]]
    else:
        raw=new_titles[k];n=parse(raw)[0]
        ed=field_edits(raw,n,properties.get(k,{}));additions=[render_title(c) for c in children[k]]
    if additions:
        pos=raw.rfind('}');ed.append((pos,pos,'\n'+'\n'.join(additions)+'\n'))
    rendered[k]=splice(raw,ed)
    return rendered[k]
root_ed=[]
for n in parse(source):
    if n.key in T:root_ed.append((n.start,n.end,render_title(n.key) if parents[n.key] is None else ''))
landed=splice(source,root_ed)
landed+='\n'+'\n'.join(render_title(k) for k in new_titles if parents[k] is None)+'\n'
put('common/landed_titles/aq_world.txt',landed)

# Modify the actual start blocks, preserving earlier history and avoiding late-file duplicate title definitions.
hed=[]
for k,fields in history_updates.items():
    if k in Hnodes:
        n=Hnodes[k];raw=Hsource[n.start:n.end]
        dated=next((d for d in n.value if d.key==DATE),None)
        if dated:
            block=Hsource[dated.start:dated.end]
            block=splice(block,field_edits(block,dated,fields,dated.start))
            raw=splice(raw,[(dated.start-n.start,dated.end-n.start,block)])
        else:
            pos=raw.rfind('}');raw=raw[:pos]+DATE+' = {\n'+''.join(' '+a+' = '+str(v)+'\n' for a,v in fields.items())+'}\n'+raw[pos:]
        hed.append((n.start,n.end,raw))
    else:
        new=f'{k} = {{\n {DATE} = {{\n'+''.join('  '+a+' = '+str(v)+'\n' for a,v in fields.items())+' }\n}\n'
        hed.append((len(Hsource),len(Hsource),'\n'+new))
put('history/titles/aq_world.txt',splice(Hsource,hed))
ced=[]
for k,fields in character_updates.items():
    n=C[k];raw=Csource[n.start:n.end];raw=splice(raw,field_edits(raw,n,fields,n.start));ced.append((n.start,n.end,raw))
put('history/characters/aq_world.txt',splice(Csource,ced)+'\n'+'\n'.join(new_characters.values()))
if new_dynasties:
    dyn='\n'.join(f'{k} = {{ name = {k} culture = {cu} }}' for k,(name,cu) in new_dynasties.items())+'\n'
    put('common/dynasties/aq040_dynasties.txt',dyn)
    for k,(name,cu) in new_dynasties.items():loc[k]=name

# Clean exactly the overridden keys from earlier mod localization, not unrelated culture/calendar strings.
for lang in ['english','french','german','spanish','russian','simp_chinese','korean','japanese','polish']:
    for p in (ROOT/'localization'/lang).rglob('*.yml'):
        ss=p.read_text(encoding='utf-8-sig')
        clean=''.join(line for line in ss.splitlines(True) if not ((m:=re.match(r'^\s*([^ #:\n]+):',line)) and m[1] in loc))
        if clean!=ss:put(p.relative_to(ROOT).as_posix(),clean)
    def escape(s):return s.replace('\\','\\\\').replace('"','\\"').replace('\n',' ')
    put(f'localization/{lang}/replace/aq040_titles_l_{lang}.yml','l_'+lang+':\n'+''.join(f' {k}:0 "{escape(v)}"\n' for k,v in sorted(loc.items())))

# Minimal structural acceptance checks run on the planned files, before committing any content to disk.
NT,NP=index_titles(landed)
assert set(T)<=set(NT),'Existing title IDs were removed.'
assert {k for k in NT if k.startswith('c_')}=={k for k in T if k.startswith('c_')},'County identities changed.'
for k,n in T.items():
    if k.startswith('b_'):assert get(n.value,'province')==get(NT[k].value,'province'),k
NH={n.key:start_fields(n) for n in parse(outputs['history/titles/aq_world.txt'])}
NC={n.key:n for n in parse(outputs['history/characters/aq_world.txt'])}
assert len(NC)==len(C)+len(new_characters)
assert len(parse(outputs['history/titles/aq_world.txt']))==len(NH),'Duplicate title history.'
for k,v in NH.items():
    h=v.get('holder','0');l=v.get('liege','0')
    assert k in NT,('unknown history title',k)
    assert h=='0' or h in NC,('missing holder',k,h)
    assert l=='0' or l in NH and NH[l].get('holder','0')!='0',('unheld liege',k,l)
    if l!='0':assert rank[l[0]]>rank[k[0]],('rank',k,l)
    if h!='0':
        life=NC[h]
        born=[tuple(map(int,d.key.split('.'))) for d in life.value if re.fullmatch(r'\d+\.\d+\.\d+',d.key) and isinstance(d.value,list) and get(d.value,'birth')=='yes']
        assert born and min(born)<=START,('unborn holder',k,h)
        assert not any(re.fullmatch(r'\d+\.\d+\.\d+',d.key) and tuple(map(int,d.key.split('.')))<=START and isinstance(d.value,list) and get(d.value,'death') for d in life.value),('dead holder',h)
NPri=primary_titles(NH)
actual={c:top_realm(c,NH,NPri) for c in counties}
expected={c:(state_empire.get(kingdom_for[c]) or kingdom_for[c]) for c in active_counties}
for c,e in expected.items():assert actual[c]==e,('wrong realm',c,actual[c],e)
for c in released:assert actual[c]==c,('release failed',c,actual[c])
for c in counties:
    if c not in rebuilt_counties:assert actual[c]==before_realm[c],('unrelated ownership changed',c)
assert not descendants('k_aquitaine') and not descendants('k_brittany'), 'Gaul merger left obsolete de jure land.'
assert len(descendants('k_france'))>=90, 'Gaul merge did not include the intended heartland.'
# Each non-crown character has only one employer across their explicit title liens.
lieges=defaultdict(set)
for k,v in NH.items():
    h=v.get('holder','0');l=v.get('liege','0')
    if h!='0' and l!='0' and NH[l].get('holder')!=h:lieges[h].add(NH[l]['holder'])
conflicts={h:sorted(v) for h,v in lieges.items() if len(v)>1}
assert not conflicts,('contradictory vassalage',conflicts)

# Auditable source mapping and county-level territory manifest, not just renamed map labels.
audit=[]
for key,row in manifest.items():
    audit.append({'title_id':key,**row,'implemented_name':loc.get(key,old_loc.get(key)),
     'status':'retired' if key in retired else 'localized' if key in NT else 'source title absent from mod'})
put('source_data/040/applied_title_names.json',json.dumps(audit,ensure_ascii=False,indent=1))
put('source_data/040/de_jure_moves.json',json.dumps(changes,ensure_ascii=False,indent=1))
put('source_data/040/historical_overrides.json',json.dumps(provenance,ensure_ascii=False,indent=1))
realm_counts=Counter(actual.values())
summary={'version':VERSION,'internal_start_date':DATE,'display_start':'359 BC','source_title_rows':len(manifest),
 'county_count':len(counties),'localization_keys_written_per_language':len(loc),'new_title_definitions':len(new_titles),
 'title_history_blocks_updated':len(history_updates),'new_characters':len(new_characters),
 'county_realm_changes':sum(actual[c]!=before_realm[c] for c in counties),
 'nomadic_counties_before':sum(Hbefore[c].get('government')=='nomad_government' for c in counties),
 'nomadic_counties_after':sum(NH[c].get('government')=='nomad_government' for c in counties),
 'gaul_de_jure_counties':len(descendants('k_france')),'major_realms':{k:v for k,v in realm_counts.items() if k.startswith(('k_aq','e_aq'))},
 'checks':'PASS: IDs, holders, life dates, title ranks, holder-aware realm chains, complete county coverage, barony/province identity, unrelated ownership',
 'in_game_tested':False,'religion_definitions_unchanged':True,'culture_definitions_unchanged':True}
put('source_data/040/revision.json',json.dumps(summary,indent=2))
state_manifest={k:{'label':loc.get(k,old_loc.get(k,k)),'capital':state_capitals.get(k) or properties.get(k,{}).get('capital') or (get(NT[k].value,'capital') if k in NT else None),'color':state_colors.get(k,(158,170,145)),'counties':sorted(c for c in counties if actual[c]==k)} for k in summary['major_realms']}
put('source_data/040/realm_manifest.json',json.dumps(state_manifest,ensure_ascii=False,indent=1))
buf=io.StringIO();w=csv.writer(buf);w.writerow(['county_id','source_county_name','implemented_county_name','de_jure_duchy','de_jure_kingdom','top_realm','holder','government','source_basis'])
for c in sorted(counties):w.writerow([c,manifest[c]['old'],loc.get(c,old_loc.get(c,c)),NP[c],NP.get(NP[c]),actual[c],NH[c]['holder'],NH[c].get('government','tribal_government'),manifest[c]['tag']])
put('source_data/040/county_realms.csv',buf.getvalue())
put('descriptor.mod',read('descriptor.mod').replace('version="0.3.0"','version="0.4.0"'))

notes='''# Antiquity 359 BC: title and political-history revision 0.4.0

## What is implemented
The supplied 4,760-row naming list has been matched to stable CK3 title IDs using the four supplied wiki PDFs and the vanilla title tree. Every existing county and barony ID is preserved. Source titles that are already unheld compatibility stubs are not resurrected as medieval states. Localization is mirrored into all nine existing language files with the original English terminology, not represented as a translation.

France, Aquitaine and Brittany now have one de jure Gaul crown. The Barcelona duchy was already outside Aquitaine in this scenario and remains outside Gaul. Gaul is not assigned a fictitious common king. The old Aquitaine and Brittany crowns and the Francia empire wrapper are unheld and uncreatable.

Persia is an Achaemenid empire under Artaxerxes II, with regional satrapal crowns and actual chains of vassalage. Caria under Mausolos, Lydia, Cappadocia, Cilicia, Hyrcania, Carmania, Bactria, Margiana, Aria, Drangiana and an eastern Caucasian frontier are distinguished. Egypt remains independent. Nanda is an imperial realm with regional governors, rather than a renamed collection of independent counties. Qin, Zhao, Wei, Han, Qi, Yan, Song, Chu and Yue retain separate crowns; Zhongshan, Lu, Wey, Ba and Shu have separate county-based territories. Zhao's capital is in the county containing Handan. Song's ruler is named Ticheng. Zhou's ruler uses the personal name Ji Pian rather than the posthumous title Xian.

Sparta no longer holds Messenia. Byzantion is independent. Western, central and eastern Thracian power centres are distinguished. Bosporan territory includes the Taman side of the strait. Rome is not awarded independent Tibur merely because it shares the medieval Latium duchy. Carthage keeps a coastal Punic sphere without automatically annexing the Sardinian and Numidian interior. Saba, Ma'in, Qataban and Hadramaut are separately represented.

## Source hierarchy and uncertainty
1. The uploaded title list governs title vocabulary. Its [R] and [A/R] markers denote provisional regional reconstructions, not newly verified historical findings. Repeated county labels remain traceable in applied_title_names.json and county_realms.csv.
2. The uploaded 359 BC image governs the broad scenario and its named powers. It mixes political states with peoples and language groups. Uncoloured regions labelled Celts, Arabs, Xiongnu or similar are not converted into fictional unified empires. The image has no geographical metadata or county-scale borders. County assignments are an authored approximation using CK3's existing geography, not a pixel-perfect traced map.
3. Historical reference checks refine boundaries where the medieval starting layout is clearly inappropriate. All exact boundary lines, office-holder ages, attributes and unnamed local rulers remain gameplay reconstruction. No new invented ruler is described as a documented ancient person.
4. The requested Nanda state and existing Anuradhapura scenario are retained. Conventional chronologies often place their consolidation later than 359 BC. The broader Nanda outline and the Kalinga connection are therefore map-driven scenario conventions, not an assertion of secure control in that year.
5. Persian control at the Indus and Caucasian fringes is simplified. Satrapies are administrative gameplay wrappers, not medieval hereditary kingdoms. The old Sindh/Gandhara extent is retained from the scenario. Gadir is represented within a Punic sphere; the exact degree of direct Carthaginian rule in 359 is uncertain. The whole Spanish interior is not made Carthaginian.
6. Kyrene is independent rather than an ordinary Egyptian province. The map's broad north-African colouring is not treated as proof of Egyptian sovereignty over all Cyrenaica. South Arabian crowns likewise distinguish the named local kingdoms instead of turning all Yemen into Saba.
7. The supplied list's northern al-Jawf -> Ma'in mapping was geographically wrong: northern Dumat al-Jandal and southern Minaean territory are not the same place. Galatia is not used as the duchy name before the later Celtic settlement. These corrections and the accidentally retained Galicia-Volhynia label are explicit in historical_overrides.json.
8. Fourth-century Qi reign dates vary between chronologies. The existing Yinqi character is retained rather than silently replacing him on the strength of an inconsistent chronology. Song and Zhou name corrections do not force future scripted successions.

## Preserved systems
The existing 0.3 culture definitions, faith definitions, innovations, government/progression mechanics, calendar offset, and physical map assets are not replaced. Existing nomadic chiefdoms outside the reconstructed states remain nomadic. This pass does not revert 0.3 to the older all-tribal prototype. Major settled states continue using the established tribal gameplay model. The internal date is still 642.5.1, displayed as 359 BC.

## Historical references consulted
- User: ck3_359BC_title_renames.txt and Screenshot 2026-09-25 175136.png; the four CK3 Wiki title-list PDF exports are the inventory concordance, not historical authorities.
- Ruediger Schmitt, Encyclopaedia Iranica, Artaxerxes II: https://www.iranicaonline.org/articles/artaxerxes-ii-achaemenid-king/
- Encyclopaedia Iranica, Achaemenid Satrapies: https://www.iranicaonline.org/articles/achaemenid-satrapies/
- Ulrich Theobald, ChinaKnowledge, Zhou geography and the regional-state histories: https://www.chinaknowledge.de/History/Zhou/zhou-map.html ; https://www.chinaknowledge.de/History/Zhou/rulers-song.html ; https://www.chinaknowledge.de/History/Zhou/zhou-rulers.html ; https://www.chinaknowledge.de/History/Zhou/rulers-qi.html
- INFLIBNET, Outlines of Indian History, Mahajanapadas / Nandas: https://ebooks.inflibnet.ac.in/icp01/chapter/mahajanapadas-rise-of-magadha-nandas-invasion-of-alexander/
- Historical atlas map of Macedonian growth 359-336 BC, USF collection: https://etc.usf.edu/maps/pages/3600/3606/3606.htm
- Mausolos' Carian rule is also attested numismatically: Historia Numorum / Sylloge Nummorum Graecorum catalogue references, linked via https://en.numista.com/385893
- Epaminondas and the liberation of Messenia: https://en.wikipedia.org/wiki/Epaminondas (synthesis with references to Roy, Luraghi, Cawkwell and others).
- Thracian successor kingdoms: https://en.wikipedia.org/wiki/Berisades (with ancient-text references and Smith's dictionary).
These establish historical orientation, not a source citation for every synthetic county boundary.

## Verification and loading
Only static checks were performed. CK3 was not opened and an actual in-game load is not claimed. Save compatibility across this de jure/ownership overhaul is not promised; use a new 359 BC campaign. The migration backs up all changed existing files outside the mod directory before replacing them.
'''
put('RELEASE_NOTES_040.md',notes)
put('README.md','# Current revision: 0.4.0\n\nTitle names and the 359 BC political map have been rebuilt from the supplied naming inventory and scenario image. Read RELEASE_NOTES_040.md for implementation details, historical conventions and the static-only verification status. The earlier 0.3 documentation below describes the preserved underlying systems.\n\n'+read('README.md'))

# Final conservation checks on immutable content, then back up precisely the paths being changed.
assert all(hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h for p,h in religion_hashes.items())
assert hashlib.sha256((ROOT/'common/culture/cultures/aq_ancient_cultures.txt').read_bytes()).hexdigest()==culture_hash
stamp=datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
backup=Path(r'C:\antiquity_backups')/('before_040_'+stamp)
backup.mkdir(parents=True,exist_ok=False)
written=[]
for rel,text in outputs.items():
    dest=ROOT/rel
    encoded=text.encode('utf-8-sig' if dest.suffix=='.yml' else 'utf-8')
    if dest.exists() and dest.read_bytes()==encoded:continue
    if dest.exists():
        saved=backup/rel;saved.parent.mkdir(parents=True,exist_ok=True);saved.write_bytes(dest.read_bytes())
    dest.parent.mkdir(parents=True,exist_ok=True)
    temp=dest.with_suffix(dest.suffix+'.aq040tmp');temp.write_bytes(encoded);temp.replace(dest)
    written.append({'path':rel,'bytes':len(encoded),'sha256':hashlib.sha256(encoded).hexdigest()})
(DATA/'written_files.json').write_text(json.dumps({'backup':str(backup),'files':written},indent=2),encoding='utf-8')
print(json.dumps(summary,indent=2))
print('Changed files:',len(written),'Backup:',backup)
