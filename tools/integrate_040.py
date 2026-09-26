"""Integrate the last Hellespont border and launcher registration for revision 0.4.
Run after revise_040.py and polish_040.py. No game process is launched.
"""
from pathlib import Path
from collections import Counter, defaultdict
import csv, io, json, re, sys, datetime, hashlib, runpy
from pdx import parse, get
from titles_040 import ROOT, read, index_titles, start_fields

assert 'version="0.4.0"' in read('descriptor.mod')
DATA = ROOT / 'source_data/040'
backup = Path(r'C:\antiquity_backups') / ('integrate_040_' + datetime.datetime.now().strftime('%Y%m%d_%H%M%S'))
written = []
def save(rel, text):
    path = ROOT / rel
    data = text.encode('utf-8-sig' if path.suffix == '.yml' else 'utf-8')
    if path.exists() and path.read_bytes() == data:
        return
    if path.exists():
        target = backup / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(path.read_bytes())
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix + '.aq040tmp')
    temp.write_bytes(data)
    temp.replace(path)
    written.append({'path': rel, 'bytes': len(data), 'sha256': hashlib.sha256(data).hexdigest()})

def splice(text, edits):
    for start, end, value in sorted(edits, reverse=True):
        text = text[:start] + value + text[end:]
    return text

land = read('common/landed_titles/aq_world.txt')
T, P = index_titles(land)
initial_provinces = {key: get(n.value, 'province') for key,n in T.items() if key.startswith('b_')}
history = read('history/titles/aq_world.txt')
HN = {n.key: n for n in parse(history)}
H = {key: start_fields(n) for key,n in HN.items()}
new_duchy = 'd_aq040_hellespont'
county = 'c_abydos'
kingdom = 'k_aq_persia_nikaea'
if P[county] != new_duchy:
    assert new_duchy not in T, 'Unexpected partial Hellespont migration'
    assert P[county] == 'd_aegean_islands'
    assert H[county]['holder'].startswith('aq_chief_')
    cn, kn = T[county], T[kingdom]
    block = land[cn.start:cn.end]
    added = ('\n' + new_duchy + ' = {\n'
             ' color = { 145 203 219 }\n capital = c_abydos\n'
             ' can_be_named_after_dynasty = no\n can_use_nomadic_naming = no\n'
             ' can_create = { aq_can_form_chiefdom_union_trigger = yes }\n'
             ' can_create_on_partition = { aq_can_form_chiefdom_union_trigger = yes }\n'
             + block + '\n}\n')
    save('common/landed_titles/aq_world.txt', splice(land, [(cn.start,cn.end,''),(kn.end-1,kn.end-1,added)]))
    hn = HN[county]
    hblock = history[hn.start:hn.end]
    assert 'liege' not in H[county]
    hblock = hblock.replace('642.5.1 = {', '642.5.1 = {\n liege = 0', 1)
    hnew = (f'\n# Asian Hellespont: Persian territory, not part of a medieval island league.\n'
            f'{new_duchy} = {{\n 642.5.1 = {{\n holder = {H[county]["holder"]}\n'
            f' liege = {kingdom}\n government = tribal_government\n'
            ' succession_laws = { partition_succession_law male_preference_law }\n }\n}\n')
    save('history/titles/aq_world.txt', splice(history,[(hn.start,hn.end,hblock)])+hnew)
    moves = json.loads(read('source_data/040/de_jure_moves.json'))
    moves += [{'title':county, 'from':P[county], 'to':new_duchy},
              {'title':new_duchy, 'from':None, 'to':kingdom}]
    save('source_data/040/de_jure_moves.json', json.dumps(moves,ensure_ascii=False,indent=1))

# Moving Abydos out also requires moving the residual Aegean duchy's capital.
land_now = read('common/landed_titles/aq_world.txt')
current_t,current_p = index_titles(land_now)
ae = current_t['d_aegean_islands']
if get(ae.value,'capital') == 'c_abydos':
    part = land_now[ae.start:ae.end]
    part = re.sub(r'capital\s*=\s*c_abydos', 'capital = c_naxos', part, count=1)
    save('common/landed_titles/aq_world.txt',splice(land_now,[(ae.start,ae.end,part)]))

# Add a single localization authority, then remove only exact duplicate keys from older files.
key_pattern = re.compile(r'^\s*([^ #:\n]+):')
langs = ['english','french','german','spanish','russian','simp_chinese','korean','japanese','polish']
duplicates_removed = 0
for lang in langs:
    relative = f'localization/{lang}/replace/aq040_titles_l_{lang}.yml'
    current = read(relative)
    for key in (new_duchy, new_duchy + '_adj'):
        if not re.search(r'^\s*'+re.escape(key)+r':',current,re.M):
            current += f' {key}:0 "Hellespont"\n'
    save(relative,current)
    authority = {m[1] for line in current.splitlines() if (m:=key_pattern.match(line)) and not m[1].startswith('l_')}
    for path in (ROOT / 'localization' / lang).rglob('*.yml'):
        if path == ROOT / relative:
            continue
        prior = path.read_text(encoding='utf-8-sig')
        clean = []
        for line in prior.splitlines(True):
            match = key_pattern.match(line)
            if match and match[1] in authority:
                duplicates_removed += 1
            else:
                clean.append(line)
        clean = ''.join(clean)
        if not re.search(r'^l_'+re.escape(lang)+r':',clean,re.M):
            clean = 'l_'+lang+':\n'+clean.lstrip('\n')
        save(path.relative_to(ROOT).as_posix(), clean)

# Keep the finishing renderer reproducible and ensure empty ocean province zero is not drawn as land.
polish = read('tools/polish_040.py')
polish = polish.replace('elif pid in water:color=[154,180,202]', 'elif pid == 0 or pid in water:color=[154,180,202]')
save('tools/polish_040.py',polish)
render = read('tools/render_040.ps1')
render = render.replace('float x=(centers[k].X-crop.X)*scale,y=(centers[k].Y-crop.Y)*scale+52;SizeF size=',
    'float x=(centers[k].X-crop.X)*scale,y=(centers[k].Y-crop.Y)*scale+52; if(!all && kv.Value=="Macedon") { x+=28; y+=24; } SizeF size=')
render = render.replace('if(collision&&!all)continue;', 'if(collision&&!all&&kv.Value!="Macedon"&&kv.Value!="Rome")continue;')
render = render.replace('occupied.Add(box);g.FillRectangle(new SolidBrush(Color.FromArgb(185,255,255,255)),box);',
    'occupied.Add(box);using(SolidBrush backing=new SolidBrush(Color.FromArgb(185,255,255,255)))g.FillRectangle(backing,box);')
save('tools/render_040.ps1',render)

# Recompute the audit from actual history, accounting for royal personal domains with liege=0.
T,P = index_titles(read('common/landed_titles/aq_world.txt'))
H = {n.key:start_fields(n) for n in parse(read('history/titles/aq_world.txt'))}
rank = {'b':0,'c':1,'d':2,'k':3,'e':4,'h':5}
primary = {}
for title,fields in H.items():
    holder=fields.get('holder','0')
    if holder!='0' and (holder not in primary or rank[title[0]]>rank[primary[holder][0]]):
        primary[holder]=title

def top(title):
    seen=set()
    while True:
        assert title not in seen, ('liege cycle',title)
        seen.add(title)
        f=H.get(title,{})
        pr=primary.get(f.get('holder','0'))
        if pr and rank[pr[0]]>rank[title[0]]:
            title=pr
        elif f.get('liege','0')!='0':
            title=f['liege']
        else:
            return title

rows=list(csv.DictReader(io.StringIO(read('source_data/040/county_realms.csv'))))
assert len(rows)==3476
previous_realms={r['county_id']:r['top_realm'] for r in rows}
for row in rows:
    c=row['county_id']
    row.update(de_jure_duchy=P[c],de_jure_kingdom=P.get(P[c]),top_realm=top(c),holder=H[c]['holder'],government=H[c].get('government','tribal_government'))
assert top('c_abydos')=='e_aq_persia'
assert all(top(c)==realm for c,realm in previous_realms.items() if c!='c_abydos'), 'Unrelated realm changed'
f=io.StringIO();w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
save('source_data/040/county_realms.csv',f.getvalue())
realms=json.loads(read('source_data/040/realm_manifest.json'))
for key in realms:
    realms[key]['counties']=sorted(r['county_id'] for r in rows if r['top_realm']==key)
save('source_data/040/realm_manifest.json',json.dumps(realms,ensure_ascii=False,indent=1))
revision=json.loads(read('source_data/040/revision.json'))
if not revision.get('hellespont_border_integrated'):
    revision['new_title_definitions']+=1
    revision['title_history_blocks_updated']+=2
    revision['county_realm_changes']+=1
revision['major_realms']={key:len(v['counties']) for key,v in realms.items()}
revision['hellespont_border_integrated']={'county':'c_abydos','duchy':new_duchy,'kingdom':kingdom,'empire':'e_aq_persia','source':'Abydos (Hellespont), ancient history; https://en.wikipedia.org/wiki/Abydos_(Hellespont)'}
save('source_data/040/revision.json',json.dumps(revision,indent=2))
notes=read('RELEASE_NOTES_040.md')
if '## Final Hellespont integration' not in notes:
    notes+='''\n## Final Hellespont integration and launch registration
Abydos and its Troas/Hellespont county belong to the Persian satrapal hierarchy. The other Aegean islands are not annexed merely because the medieval map grouped them with Abydos. A separate Hellespont duchy keeps the native barony and province IDs intact. See https://en.wikipedia.org/wiki/Abydos_(Hellespont) for the historical overview and its references.
The reproducible sequence from the backed-up 0.3 baseline is revise_040.py, polish_040.py, then integrate_040.py. The latter is also safe to repeat on the resulting 0.4 tree; it does not reassign unrelated realms. render_040.ps1 produces a static native-province preview, not an in-game screenshot. All older generator snapshots remain historical records, not the authoritative 0.4 county distribution.
'''
save('RELEASE_NOTES_040.md',notes)

# Rebuild source lookup and name counts using the integrated realm audit.
runpy.run_path(str(ROOT/'tools/polish_040.py'),run_name='__main__')

# Static acceptance, not a runtime test.
C={n.key:n for n in parse(read('history/characters/aq_world.txt'))}
errors=[]
for key,fields in H.items():
    h,l=fields.get('holder','0'),fields.get('liege','0')
    if key not in T:errors.append('Undefined title '+key)
    if h!='0' and h not in C:errors.append('Undefined holder '+key)
    if l!='0' and (l not in H or H[l].get('holder','0')=='0' or rank[l[0]]<=rank[key[0]]):errors.append('Invalid liege '+key)
assert not errors,errors[:20]
assert len({k for k,n in T.items() if k.startswith('c_') and any(b.key.startswith('b_') for b in n.value)})==3476
assert initial_provinces=={k:get(n.value,'province') for k,n in T.items() if k.startswith('b_')}
for lang in langs:
    keys=[]
    for path in (ROOT/'localization'/lang).rglob('*.yml'):
        assert path.read_bytes().startswith(b'\xef\xbb\xbf'),str(path)
        assert re.search(r'^l_'+re.escape(lang)+r':',path.read_text(encoding='utf-8-sig'),re.M),str(path)
        keys += [m[1] for line in path.read_text(encoding='utf-8-sig').splitlines() if (m:=key_pattern.match(line))]
    repeats=[k for k,v in Counter(keys).items() if v>1 and not k.startswith('l_')]
    assert not repeats,(lang,repeats[:20])

registration=None
if '--register' in sys.argv:
    launch=Path(r'C:\Users\Super\Documents\Paradox Interactive\Crusader Kings III\mod\antiquity_359_bc.mod')
    old=launch.read_text(encoding='utf-8-sig')
    assert 'name="Antiquity 359 BC"' in old
    assert len(re.findall(r'^path=',old,re.M))==1
    new=re.sub(r'^version="[^"]+"','version="0.4.0"',old,flags=re.M)
    new=re.sub(r'^path="[^"]+"','path="C:/antiquity_359_bc"',new,flags=re.M)
    if new!=old:
        target=backup/'launcher/antiquity_359_bc.mod'
        target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(launch.read_bytes())
        launch.write_text(new,encoding='utf-8',newline='\n')
    assert 'path="C:/antiquity_359_bc"' in launch.read_text(encoding='utf-8-sig')
    registration={'descriptor':str(launch),'active_path':str(ROOT),'old_documents_mod_left_untouched':True,'game_launched':False}
    save('source_data/040/launcher_registration.json',json.dumps(registration,indent=2))
    intro=read('README.md')
    line='The existing launcher entry now loads `C:\\antiquity_359_bc` directly. The older Documents mod folder is retained untouched. Start a new 359 BC campaign; no in-game launch was performed.\n\n'
    if line not in intro:save('README.md',intro.replace('# Current revision: 0.4.0\n\n','# Current revision: 0.4.0\n\n'+line,1))

report={'status':'PASS','counties':len(rows),'source_title_rows':len(json.loads(read('source_data/040/applied_title_names.json'))),'persian_counties':len(realms['e_aq_persia']['counties']),'nanda_counties':len(realms['e_aq_nanda']['counties']),'nomadic_counties':sum(r['government']=='nomad_government' for r in rows),'localization_languages':len(langs),'duplicate_keys_removed':duplicates_removed,'unchanged_barony_province_ids':len(initial_provinces),'launcher':registration,'in_game_tested':False}
save('source_data/040/final_checks.json',json.dumps(report,indent=2))
(DATA/'integration_files.json').write_text(json.dumps({'backup':str(backup),'files':written},indent=2),encoding='utf-8')
print(json.dumps(report,indent=2));print('Final integration backup:',backup)
