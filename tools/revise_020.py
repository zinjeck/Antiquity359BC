"""Apply the 0.2.0 data/calendar revision to a COPY of the 0.1.0 mod.
Reads a vanilla ZIP for native schema templates. No TFE files are imported.
Usage: python revise_020.py --mod STAGING_FOLDER --vanilla GAME_ZIP
The official working folder is C:/antiquity_359_bc. Back it up before applying.
"""
from pathlib import Path
from collections import defaultdict, Counter
import argparse, zipfile, re, json, csv, hashlib
from pdx import parse, get, vals, decode, title_tree
from peoples_020 import *

def tint(key):return ' '.join(str(45+b%190) for b in hashlib.sha256(key.encode()).digest()[:3])

def loc_read(s):
    return {m[1]:m[2] for m in re.finditer(r'^\s*([^ #:\n]+):(?:\d+)?\s*"(.*)"\s*$',s,re.M)}

def calendar_expression(value):
    """Native GUI functions; value is a typed literal or an actual Date.GetYear binding."""
    test=f"LessThanOrEqualTo_int32({value}, '(int32)1000')"
    year=f"Select_CString({test}, IntToString(Subtract_int32('(int32)1001', {value})), IntToString(Subtract_int32({value}, '(int32)1000')))"
    return f"[{year}][Select_CString({test}, ' BC', ' AD')]"

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--mod',required=True);ap.add_argument('--vanilla',required=True);a=ap.parse_args()
    root=Path(a.mod);z=zipfile.ZipFile(a.vanilla)
    def rd(p):return (root/p).read_text(encoding='utf-8-sig')
    def wr(p,s):
        f=root/p;f.parent.mkdir(parents=True,exist_ok=True);f.write_text(s,encoding='utf-8-sig' if p.endswith('.yml') else 'utf-8',newline='\n')
    def native(p):return decode(z.read('game/'+p))
    base_cultures=rd('common/culture/cultures/aq_ancient_cultures.txt')
    culture_nodes={n.key:n for n in parse(base_cultures)}
    assert 'aq_samnite' not in culture_nodes,'Run this once against a 0.1.0 copy, not an already revised mod.'
    original_loc=loc_read(rd('localization/english/aq_l_english.yml'))
    original_override=loc_read(rd('localization/english/replace/aq_overrides_l_english.yml'))
    loc={};labels={k:original_loc.get(k+'_collective_noun',k[3:]) for k in culture_nodes}
    old_religion=rd('common/religion/religion_types/aq_regional_rites.txt')
    old_faiths={};old_religions={}
    for n in parse(old_religion):
        old_religions[n.key]=n
        for faith in get(n.value,'faiths',[]):old_faiths[faith.key]=(n,faith)
    rename={k:'aq_faith_'+k[3:] for k in old_faiths}
    rename.update({k:'aq_religion_'+k[3:].removesuffix('_religion') for k in old_religions})
    # Replace exact database tokens. Culture tokens with the same spelling must NOT be renamed.
    for f in root.rglob('*.txt'):
        if '.git' in f.parts or 'tools' in f.parts:continue
        rel=f.relative_to(root).as_posix()
        if rel.startswith('common/religion/religion_types/'):continue
        s=rd(rel)
        s=re.sub(r'\b(religion\s*=\s*)(aq_\w+)',lambda m:m[1]+rename.get(m[2],m[2]),s)
        s=re.sub(r'\b(faith:|religion:)(aq_\w+)',lambda m:m[1]+rename.get(m[2],m[2]),s)
        if s!=rd(rel):wr(rel,s)
    # Restore culture labels first, eliminating the original shared-localization-key bug.
    for key,label in labels.items():original_loc[key]=label
    for old in old_faiths:
        for suffix in ('_adj','_adherent','_adherent_plural','_desc'):original_loc.pop(old+suffix,None)
        if old not in culture_nodes:original_loc.pop(old,None)
    for old in old_religions:
        for suffix in ('','_adj','_adherent','_adherent_plural','_desc'):original_loc.pop(old+suffix,None)
    # Make cultures from native 0.1.0 aesthetics, and add attested language groupings.
    language_defs=[];added=[];new_cultures={};faith_for_culture={}
    basefaith_byculture={}
    for n in parse(rd('history/provinces/aq_world.txt')):
        basefaith_byculture.setdefault(get(n.value,'culture'),get(n.value,'religion'))
    for p in PEOPLES:
        key='aq_'+p['key'];n=culture_nodes['aq_'+p['base']]
        text=base_cultures[n.start:n.end];text=re.sub(r'^aq_\w+',key,text)
        text=re.sub(r'color\s*=\s*\{[^}]+\}','color = { '+tint(key)+' }',text,count=1)
        lang=p['language']
        if lang in LANG_NAMES:
            langkey='language_aq_'+lang
            language_defs.append((langkey,f'{langkey} = {{ type = language color = {{ {tint(lang)} }} ai_will_do = {{ value = 10 }} }}'))
            loc[langkey+'_name']=LANG_NAMES[lang];loc[langkey]=LANG_NAMES[lang]
        else:langkey='language_'+lang
        text=re.sub(r'\blanguage\s*=\s*\w+','language = '+langkey,text)
        added.append(text);new_cultures[key]=p;labels[key]=p['name']
        for suffix in ('','_collective_noun','_prefix'):loc[key+suffix]=p['name']
        faith_for_culture[key]=p['faith'] if p['faith']=='hellenic_pagan' else 'aq_faith_'+p['faith']
        hist=rd('history/cultures/aq_'+p['base']+'.txt').replace('641.1.1','642.1.1')
        wr('history/cultures/'+key+'.txt',hist)
    wr('common/culture/cultures/aq_ancient_cultures.txt',base_cultures+'\n\n# Regional peoples added in 0.2.0\n'+'\n\n'.join(added))
    wr('common/culture/pillars/aq_ancient_languages.txt','\n'.join(dict(language_defs).values()))
    # Read vanilla geographic ancestry, not medieval sovereignty, for authored placements.
    vanilla_titles,vp,_=title_tree(z);ancestry={}
    for c in vanilla_titles:
        if not c.startswith('c_'):continue
        chain=[c];p=vp[c]
        while p:chain.append(p);p=vp[p]
        ancestry[c]=set(chain)
    bad=[(p['key'],t) for p in PEOPLES for t in p['titles'].split() if t not in vanilla_titles]
    assert not bad,('Unknown footprints',bad)
    title_text=rd('common/landed_titles/aq_world.txt')
    local_ts={};local_parents={}
    def walk(nodes,parent=None):
        for n in nodes:
            if isinstance(n.value,list) and re.match('^[hekdcb]_',n.key):
                local_ts[n.key]=n;local_parents[n.key]=parent;walk(n.value,n.key)
    walk(parse(title_text))
    provinces_text=rd('history/provinces/aq_world.txt');pnodes=parse(provinces_text);province_map={n.key:n for n in pnodes}
    county_baronies={};assignments={};base_assignments={}
    for c,n in local_ts.items():
        if not c.startswith('c_'):continue
        bs=[b for b in n.value if b.key.startswith('b_') and isinstance(b.value,list) and get(b.value,'province')]
        if not bs:continue
        county_baronies[c]=bs;v=province_map[get(bs[0].value,'province')].value
        cu=get(v,'culture');fa=get(v,'religion');base_assignments[c]=(cu,fa)
        for p in PEOPLES:
            if ancestry[c]&set(p['titles'].split()):cu='aq_'+p['key'];fa=faith_for_culture[cu]
        if cu=='aq_latin':fa='aq_faith_religio_romana'
        if cu=='aq_etruscan':fa='aq_faith_etruscan'
        if cu=='aq_magadhan':fa='aq_faith_shukla_yajurvedic'
        if fa=='aq_faith_vedic':fa='aq_faith_rigvedic'
        if c in FAITH_OVERRIDES:fa='aq_faith_'+FAITH_OVERRIDES[c]
        assignments[c]=(cu,fa)
    edits=[]
    for c,bs in county_baronies.items():
        cu,fa=assignments[c]
        for b in bs:
            n=province_map[get(b.value,'province')];text=provinces_text[n.start:n.end]
            text=re.sub(r'\bculture\s*=\s*\w+','culture = '+cu,text)
            text=re.sub(r'\breligion\s*=\s*\w+','religion = '+fa,text)
            edits.append((n.start,n.end,text))
    for start,end,s in sorted(edits,reverse=True):provinces_text=provinces_text[:start]+s+provinces_text[end:]
    wr('history/provinces/aq_world.txt',provinces_text)
    # Every generated local family follows its home population; named imperial elites stay distinct.
    hist_title=parse(rd('history/titles/aq_world.txt'));holders={}
    for n in hist_title:
        current=next((x.value for x in n.value if x.key=='642.5.1'),[])
        if get(current,'holder'):holders[n.key]=get(current,'holder')
    char_culture={};char_faith={}
    for c,(cu,fa) in assignments.items():
        h=holders[c]
        if h.startswith('aq_chief_'):
            for ident in (h,h+'_spouse',h+'_son',h+'_daughter'):char_culture[ident]=cu;char_faith[ident]=fa
    for h,cu in HISTORICAL_CULTURES.items():char_culture[h]='aq_'+cu;char_faith[h]=faith_for_culture['aq_'+cu]
    # Nanda's ruling household is Vedic even where the county is modeled with Ajivika communities.
    char_faith['aq_nanda']='aq_faith_shukla_yajurvedic'
    char_text=rd('history/characters/aq_world.txt');char_nodes=parse(char_text);edits=[];dyn_culture={}
    for n in char_nodes:
        text=char_text[n.start:n.end];cu=char_culture.get(n.key,get(n.value,'culture'));fa=char_faith.get(n.key,get(n.value,'religion'))
        if cu=='aq_latin':fa='aq_faith_religio_romana'
        if cu=='aq_etruscan':fa='aq_faith_etruscan'
        if fa=='aq_faith_vedic':fa='aq_faith_rigvedic'
        text=re.sub(r'\bculture\s*=\s*\w+','culture = '+cu,text)
        text=re.sub(r'\breligion\s*=\s*\w+','religion = '+fa,text)
        edits.append((n.start,n.end,text));dyn_culture[get(n.value,'dynasty')]=cu
    for start,end,s in sorted(edits,reverse=True):char_text=char_text[:start]+s+char_text[end:]
    wr('history/characters/aq_world.txt',char_text)
    dyntext=rd('common/dynasties/aq_dynasties.txt')
    for n in reversed(parse(dyntext)):
        if n.key in dyn_culture:
            s=re.sub(r'culture\s*=\s*\w+','culture = '+dyn_culture[n.key],dyntext[n.start:n.end]);dyntext=dyntext[:n.start]+s+dyntext[n.end:]
    wr('common/dynasties/aq_dynasties.txt',dyntext)
    bookmark=rd('common/bookmarks/bookmarks/aq_bookmark.txt').replace('religion = hellenic_pagan\n difficulty','religion = hellenic_pagan\n difficulty')
    # Only Rome's portrait changes faith; other Hellenic bookmark rulers retain theirs.
    bm=parse(bookmark)[0]
    for n in reversed(bm.value):
        if n.key=='character' and get(n.value,'history_id')=='aq_rome':
            t=bookmark[n.start:n.end].replace('religion = hellenic_pagan','religion = aq_faith_religio_romana');bookmark=bookmark[:n.start]+t+bookmark[n.end:]
    wr('common/bookmarks/bookmarks/aq_bookmark.txt',bookmark)
    # Tribes now have actual people names rather than "Italic of <medieval county>".
    tribal_names={'samnite':'Samnites','umbrian':'Umbri','picene':'Picentes','sabine':'Sabines','marsian':'Marsi','lucanian':'Lucani','bruttian':'Bruttii','lydian':'Lydians','phrygian':'Phrygians','carian':'Carians','lycian':'Lycians'}
    for d,n in local_ts.items():
        if not d.startswith('d_') or d not in holders:continue
        cs=[x.key for x in n.value if x.key in assignments]
        if not cs:continue
        # Only rename existing tribal polities, not Macedonia/Persia or their satrapal provinces.
        if ' of ' not in original_override.get(d,original_loc.get(d,'')):continue
        common=Counter(assignments[c][0] for c in cs).most_common(1)[0][0]
        if common in new_cultures:
            name=tribal_names.get(common[3:],labels[common]);original_override[d]=name;original_override[d+'_adj']=name
    # Build coherent religion families. Faith and culture IDs now live in separate namespaces.
    groups=defaultdict(list);group_template={};faith_base={}
    for key in FAITH_NAMES:
        if key in SPECIAL_FAITHS:
            template,group,tenets,desc=SPECIAL_FAITHS[key];group_template[group]=template;groups[group].append(key);faith_base[key]=(group,tenets,desc)
        else:
            if 'aq_'+key in old_faiths:group=key
            elif key in ('religio_romana','etruscan','mefitis','iguvine','rhaetian','sicanian','elymian'):group='italic'
            elif key in ('artimu','matar','labraundos','leto','sandas','ma'):group='anatolian'
            elif key=='zalmonian':group='balkan'
            elif key=='lusitanian':group='iberian'
            elif key=='ligurian':group='celtic'
            elif key=='nuragic':group='italic'
            else:group=key
            groups[group].append(key);group_template[group]='paganism'
            tenets='astrology ancestor_worship sanctity_of_nature'
            if key in ('religio_romana','etruscan','iguvine'):tenets='astrology ritual_hospitality communal_identity'
            if key in ('matar','ma','mefitis'):tenets='sacred_childbirth sanctity_of_nature esotericism'
            faith_base[key]=(group,tenets,'A regional ancient religious tradition. The label identifies a documented cult or uses a descriptive scholarly name where no umbrella endonym survives. Doctrines and county-level distribution are gameplay approximations.')
    religious=[];holy=[]
    for group,keys in groups.items():
        template=group_template[group];s=native('common/religion/religion_types/00_'+template+'.txt');n=parse(s)[0]
        fields=[s[x.start:x.end] for x in n.value if x.key not in ('faiths','holy_order_maa','holy_order_names') and not (x.key=='doctrine' and x.value=='special_doctrine_maitreya_hostility')]
        if group=='ajivika':
            # Do not leave Jain Tirthankara-specific theology as the Ajivika god/teacher vocabulary.
            fields=[x for x in fields if not x.startswith('localization')]
            p=native('common/religion/religion_types/00_paganism.txt');pn=parse(p)[0];ln=next(x for x in pn.value if x.key=='localization');fields.append(p[ln.start:ln.end])
        family_counties=[c for c,(cu,f) in assignments.items() if f.removeprefix('aq_faith_') in keys]
        faith_blocks=[]
        for key in keys:
            group,tenets,desc=faith_base[key];ident='aq_faith_'+key
            local=[c for c,(cu,f) in assignments.items() if f==ident]
            sites=list(dict.fromkeys(local+family_counties))[:5]
            if not sites:
                old='aq_'+key
                if old in old_faiths:sites=[get(x.value,'county') for x in parse(rd('common/religion/holy_sites/aq_holy_sites.txt')) if x.key.startswith('aq_'+key+'_')]
            if not sites:sites=['c_roma'] # unused compatibility fallback only
            sites=[c for c in sites if c in assignments]
            hs=[]
            for i,c in enumerate(sites):
                hid=f'aq020_{key}_{i}';holy.append(f'{hid} = {{ county = {c} character_modifier = {{ monthly_piety = 0.05 }} }}');hs.append('holy_site = '+hid)
                loc['holy_site_'+hid+'_name']=original_override.get(c,c[2:].replace('_',' ').title());loc['holy_site_'+hid+'_effect_name']='Sacred Place'
            icon={'hinduism':'vaishnavism','buddhism':'theravada','jainism':'digambara'}.get(template,'pagan')
            unreformed='doctrine = unreformed_faith_doctrine' if template=='paganism' else ''
            theology=''
            if key in ('rigvedic','krishna_yajurvedic','shukla_yajurvedic','samavedic','atharvavedic'):
                theology='localization = { HighGodName = aq_god_indra HighGodName2 = aq_god_indra HighGodNamePossessive = aq_god_indra_possessive CreatorName = aq_god_prajapati WarGodName = aq_god_indra KnowledgeGodName = aq_god_brihaspati ReligiousText = aq_text_veda ReligiousText2 = aq_text_veda ReligiousText3 = aq_text_veda }'
            if key=='ajivika':theology='localization = { HighGodName = aq_niyati HighGodName2 = aq_niyati HighGodNamePossessive = aq_niyati_possessive HighGodNameAlternate = aq_niyati CreatorName = aq_niyati FateGodName = aq_niyati ReligiousText = aq_ajivika_teaching ReligiousText2 = aq_ajivika_teaching ReligiousText3 = aq_ajivika_teaching }'
            faith_blocks.append(f'{ident} = {{ color = {{ {tint(ident)} }} icon = {icon}\n {unreformed}\n'+'\n'.join('doctrine = tenet_'+t for t in tenets.split())+'\n'+'\n'.join(hs)+'\n'+theology+'\n}')
            for suf,value in [('',FAITH_NAMES[key]),('_adj',FAITH_NAMES[key]),('_adherent',FAITH_NAMES[key]+' adherent'),('_adherent_plural',FAITH_NAMES[key]+' adherents'),('_desc',desc)]:loc[ident+suf]=value
        religion='aq_religion_'+group
        religious.append(religion+' = {\n'+'\n'.join(fields)+'\nfaiths = {\n'+'\n'.join(faith_blocks)+'\n}\n}\n')
        label={'shrauta':'Vaidika Dharma','buddhadharma':'Buddhadharma','nirgrantha':'Jain Dharma','ajivika':'Ājīvika','indian_local':'Local Indian Religions','tamil_sacred':'Tamil Religious Traditions'}.get(group,FAITH_NAMES.get(group,group.title()))
        for suf in ('','_adj','_adherent','_adherent_plural'):loc[religion+suf]=label
        loc[religion+'_desc']='Related religious traditions grouped for gameplay. This does not imply a single historical religious institution.'
    wr('common/religion/religion_types/aq_regional_rites.txt','\n'.join(religious))
    # Old holy-site definitions are retained for compatibility; new faiths use this revision's sites.
    wr('common/religion/holy_sites/aq020_holy_sites.txt','\n'.join(holy))
    loc.update(aq_god_indra='Indra',aq_god_indra_possessive="Indra's",aq_god_prajapati='Prajāpati',aq_god_brihaspati='Bṛhaspati',aq_text_veda='the Vedas',aq_niyati='Niyati',aq_niyati_possessive="Niyati's",aq_ajivika_teaching='the teaching of Gosala')
    # Correct dates at the common formatting layer, including engine-produced era warnings.
    # The |q numeric placeholder convention is present in this version's native localization.
    year=calendar_expression("'(int32)$YEAR|q$'")
    joined=calendar_expression("'(int32)$JOINED|q$'");left=calendar_expression("'(int32)$LEFT|q$'")
    date=calendar_expression('DATE.GetYear')
    calendar={
      'GAME_DATE_STRING':'$DAY$ $MONTH$, '+year,
      'GAME_DATE_STRING_SHORT':'$DAY$ $MONTH_SHORT$ '+year,
      'GAME_DATE_STRING_LONG':'$DAY|O$ of $MONTH$, '+year,
      'CURRENT_DATE':'[GetCurrentDate.GetStringLong]',
      'CURRENT_DATE_TOOLTIP':'[GetCurrentDate.GetStringLong]',
      'INNOVATION_ERA_NOT_IN_YEAR':'#N This Era is not available until '+year+'#!',
      'CULTURE_WINDOW_ERA_JOINED':joined+'–',
      'CULTURE_WINDOW_ERA_JOINED_LEFT':joined+'–'+left,
      'CULTURE_CREATION_DATE':'Formed in '+date,
      'CULTURE_CREATION_DATE_DIVERGED':'Diverged from [CULTURE.GetName] in '+date,
      'CULTURE_CREATION_DATE_HYBRID':'Formed from [CULTURE.GetName] and [TARGET_CULTURE.GetName] in '+date,
    }
    for k in calendar:original_override.pop(k,None);original_loc.pop(k,None)
    # Keep engine gates unchanged: 901=>100 BC, 1200=>AD 200, 1700=>AD 700.
    for f in (root/'history/cultures').glob('*.txt'):
        text=f.read_text(encoding='utf-8-sig');f.write_text(text.replace('641.1.1','642.1.1'),encoding='utf-8')
    original_loc.update(loc)
    def yaml(entries):return 'l_english:\n'+''.join(' '+k+':0 "'+v.replace('"',"'").replace('\n','\\n')+'"\n' for k,v in sorted(entries.items()))
    wr('localization/english/aq_l_english.yml',yaml(original_loc))
    wr('localization/english/replace/aq_overrides_l_english.yml',yaml(original_override))
    wr('localization/english/replace/aq_calendar_l_english.yml',yaml(calendar))
    # Mirror our English text under every shipped language so IDs/dates do not regress on locale change.
    for lang in ('french','german','spanish','russian','simp_chinese','korean','japanese','polish'):
        for path,entries in [('aq_l_'+lang+'.yml',original_loc),('replace/aq_overrides_l_'+lang+'.yml',original_override),('replace/aq_calendar_l_'+lang+'.yml',calendar)]:
            wr('localization/'+lang+'/'+path,yaml(entries).replace('l_english:\n','l_'+lang+':\n',1))
    wr('descriptor.mod',rd('descriptor.mod').replace('version="0.1.0"','version="0.2.0"'))
    (root/'source_data').mkdir(exist_ok=True)
    with (root/'source_data/county_peoples_020.csv').open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.writer(f);w.writerow(['county','old_culture','culture','faith','ruler','ruler_culture'])
        char_index={n.key:get(n.value,'culture') for n in parse(char_text)}
        for c,(cu,fa) in sorted(assignments.items()):w.writerow([c,base_assignments[c][0],cu,fa,holders[c],char_index[holders[c]]])
    summary={'version':'0.2.0','new_culture_definitions':len(new_cultures),'active_county_cultures':len(set(c for c,f in assignments.values())),'counties_changed':sum(assignments[c]!=base_assignments[c] for c in assignments),'new_language_definitions':len(dict(language_defs)),'custom_faith_definitions':sum(map(len,groups.values())),'active_county_faiths':len(set(f for c,f in assignments.values())),'faith_culture_key_collisions':[],'calendar_gate_examples':{'901':'100 BC','1200':'200 AD','1700':'700 AD'},'in_game_tested':False}
    from refine_020 import refine
    refine(root)
    wr('source_data/revision_020.json',json.dumps(summary,indent=2));print(json.dumps(summary,indent=2))

if __name__=='__main__':main()
