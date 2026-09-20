"""Refine original cultural pillars; safe to re-run on the 0.2 staging tree."""
from pathlib import Path
import re
from pdx import parse
from peoples_020 import PEOPLES

def refine(root):
    from revise_020 import calendar_expression,loc_read
    root=Path(root)
    path=root/'common/culture/cultures/aq_ancient_cultures.txt'
    text=path.read_text(encoding='utf-8-sig')
    heritage_names={'anatolian':'Anatolian','palaeo_balkan':'Paleo-Balkan','hellenic':'Hellenic',
        'continental_celtic':'Continental Celtic','tyrrhenian':'Tyrrhenian','canaanite':'Canaanite',
        'egyptian':'Egyptian','munda':'Munda','early_germanic':'Early Germanic',
        'paleo_sardinian':'Paleo-Sardinian','ancient_iberian':'Ancient Iberian'}
    language_names={'etruscan':'Etruscan','phoenician':'Phoenician','egyptian':'Late Egyptian','kirati':'Early Kirati'}
    bases={('aq_'+p['key']):p['base'] for p in PEOPLES}
    edits=[]
    for n in parse(text):
        base=bases.get(n.key,n.key.removeprefix('aq_'))
        h={'anatolian':'anatolian','hellenic':'hellenic','macedonian':'hellenic',
           'thracian':'palaeo_balkan','illyrian':'palaeo_balkan','gaulish':'continental_celtic',
           'celtiberian':'continental_celtic','germanic':'early_germanic','etruscan':'tyrrhenian',
           'punic':'canaanite','egyptian':'egyptian','iberian':'ancient_iberian'}.get(base)
        if n.key in ('aq_phrygian','aq_mysian','aq_bithynian'):h='palaeo_balkan'
        if n.key in ('aq_ionian','aq_aeolian','aq_pamphylian'):h='hellenic'
        if n.key=='aq_rhaetian':h='tyrrhenian'
        if n.key=='aq_nuragic':h='paleo_sardinian'
        if n.key=='aq_atavi':h='munda'
        s=text[n.start:n.end]
        if h:s=re.sub(r'heritage\s*=\s*\w+','heritage = heritage_aq_'+h,s)
        if n.key=='aq_kirata':s=re.sub(r'heritage\s*=\s*\w+','heritage = heritage_tibetan',s)
        lang={'aq_etruscan':'etruscan','aq_punic':'phoenician','aq_egyptian':'egyptian',
              'aq_thracian':'thracian','aq_illyrian':'illyrian','aq_gaulish':'gaulish',
              'aq_germanic':'germanic','aq_magadhan':'magadhi','aq_celtiberian':'celtiberian',
              'aq_iberian':'iberian','aq_brythonic':'brittonic','aq_goidelic':'goidelic',
              'aq_libyan':'libyco_berber','aq_kirata':'kirati'}.get(n.key)
        if lang:s=re.sub(r'language\s*=\s*\w+','language = language_aq_'+lang,s)
        edits.append((n.start,n.end,s))
    for start,end,s in reversed(edits):text=text[:start]+s+text[end:]
    path.write_text(text,encoding='utf-8')
    pillars=[];loc={}
    for kind,items in [('heritage',heritage_names),('language',language_names)]:
        for key,name in items.items():
            ident=kind+'_aq_'+key
            pillars.append(f'{ident} = {{ type = {kind} color = {{ 140 150 120 }} ai_will_do = {{ value = 10 }} }}')
            loc[ident+'_name']=name;loc[ident]=name
            if kind=='heritage':loc[ident+'_collective_noun']=name
    (root/'common/culture/pillars/aq_refined_pillars.txt').write_text('\n'.join(pillars)+'\n',encoding='utf-8')
    for lang in ('english','french','german','spanish','russian','simp_chinese','korean','japanese','polish'):
        # Title-name replacements belong in replace/, not duplicated in the base file.
        override=root/f'localization/{lang}/replace/aq_overrides_l_{lang}.yml'
        override_keys=set(re.findall(r'^\s+([^ :]+):',override.read_text(encoding='utf-8-sig'),re.M))
        basepath=root/f'localization/{lang}/aq_l_{lang}.yml'
        lines=basepath.read_text(encoding='utf-8-sig').splitlines(keepends=True)
        basepath.write_text(''.join(line for line in lines if not (re.match(r'\s+([^ :]+):',line) and re.match(r'\s+([^ :]+):',line)[1] in override_keys)),encoding='utf-8-sig')
        p=root/f'localization/{lang}/aq_pillars_l_{lang}.yml'
        p.write_text('l_'+lang+':\n'+''.join(f' {k}:0 "{v}"\n' for k,v in sorted(loc.items())),encoding='utf-8-sig')
    # Other native interfaces bypass GetStringLong and request the year directly.
    extra={
        'CULTURE_LEDGER_DATE':'Est. '+calendar_expression('Culture.GetCreationDate.GetYear'),
        'PICK_ANY_CHARACTER':'Play as any ruler in #bold '+calendar_expression('GameSetup.GetSelectedBookmark.GetDate.GetYear')+'#!, or #bold create your own!#!',
        'LEGACY_REIGN':'Played: '+calendar_expression('LegacyItem.GetStartDate.GetYear')+'–'+calendar_expression('LegacyItem.GetEndDate.GetYear')+' ([LegacyItem.GetReignLength])',
        'LEGACY_REIGN_CURRENT':calendar_expression('LegacyItem.GetStartDate.GetYear')+'–',
        'LEGEND_DURATION_ACTIVE':calendar_expression('Legend.GetCreationDate.GetYear')+' – ...',
        'LEGEND_DURATION_COMPLETED':calendar_expression('Legend.GetCreationDate.GetYear')+' – '+calendar_expression('Legend.GetCompletionDate.GetYear'),
        'ach_coronation.0015.t':'The Great Stampede of '+calendar_expression('GetCurrentDate.GetYear'),
        'SUCCESSION_DYNASTY_INFO':'[Dynasty.GetName]\\n'+calendar_expression('SuccessionEventWindow.GetStartDate.GetYear')+' – '+calendar_expression('SuccessionEventWindow.GetEndDate.GetYear')+'\\n[Dynasty.GetNumberOfMembers] Members ([SuccessionEventWindow.GetNumberOfPlayed] Played)\\n[Dynasty.GetPrestigeLevelName]\\n[GetDataModelSize( Dynasty.GetDynastyHouses )] Houses',
    }
    for key,description in {
        'kochinim_history_loc':'Formed from [CULTURE.GetName] and an Israelite culture in ',
        'vlach_history_loc':'Formed from [CULTURE.GetName] and a South Slavic culture in ',
        'bulgarian_history_loc':'Formed from [CULTURE.GetName] and a South Slavic culture in ',
        'scythian_heritage_loc':'Diverged from Scythian in ',
        'bactrian_heritage_loc':'Formed from Bactrian and [CULTURE.GetName] in ',
    }.items():extra[key]=description+calendar_expression('DATE.GetYear')
    for lang in ('english','french','german','spanish','russian','simp_chinese','korean','japanese','polish'):
        p=root/f'localization/{lang}/replace/aq_calendar_l_{lang}.yml'
        entries=loc_read(p.read_text(encoding='utf-8-sig'));entries.update(extra)
        p.write_text('l_'+lang+':\n'+''.join(f' {k}:0 "{v}"\n' for k,v in sorted(entries.items())),encoding='utf-8-sig')

if __name__=='__main__':
    import sys
    refine(sys.argv[1])
