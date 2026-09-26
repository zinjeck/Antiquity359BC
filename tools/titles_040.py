"""Shared read-only helpers for the 359 BC title and political-history revision."""
from pathlib import Path
from collections import defaultdict
import re, unicodedata, zipfile
from pdx import parse, get, decode, title_tree
from revise_020 import loc_read
ROOT = Path(__file__).resolve().parents[1]
START = (642, 5, 1)
TITLE = re.compile(r'^[hekdcb]_[^\s{}=:]+$')

def norm(value):
    value = value.translate(str.maketrans({'\u00e6':'ae','\u00c6':'Ae','\u00f8':'o','\u00d8':'O','\u0142':'l','\u0141':'L','\u00fe':'th','\u00de':'Th','\u00f0':'d','\u00d0':'D','\u00df':'ss'}))
    value = unicodedata.normalize('NFKD', value).encode('ascii','ignore').decode().lower()
    return re.sub('[^a-z0-9]', '', value).replace('isledefrance','iledefrance')

def read(rel):
    return (ROOT / rel).read_text(encoding='utf-8-sig')

def index_titles(text):
    titles, parents = {}, {}
    def walk(nodes, parent=None):
        for n in nodes:
            if TITLE.fullmatch(n.key) and isinstance(n.value,list):
                assert n.key not in titles, 'Duplicate title '+n.key
                titles[n.key] = n
                parents[n.key] = parent
                walk(n.value,n.key)
    walk(parse(text))
    return titles,parents

def start_fields(node):
    fields={n.key:n.value for n in node.value if not isinstance(n.value,list)}
    dated=[]
    for n in node.value:
        if re.fullmatch(r'\d+\.\d+\.\d+',n.key):
            date=tuple(map(int,n.key.split('.')))
            if date<=START:dated.append((date,n))
    for _,n in sorted(dated):fields.update({x.key:x.value for x in n.value})
    return fields

def source_rows():
    tier=None; rows=[]
    for lineno,line in enumerate(read('source_data/040/title_renames_source.txt').splitlines(),1):
        for label,t in [('EMPIRES','e'),('KINGDOMS','k'),('DUCHIES','d'),('COUNTIES','c')]:
            if line.startswith(label+' '):tier=t
        m=re.match(r'(.+?) -> (.+?) \[([^\]]+)\] \{([^}]+)\}(.*)',line)
        if m and tier:
            old,new,tag,category,context=m.groups()
            rows.append(dict(tier=tier,original=old,new=new,tag=tag,category=category,context=context,line=lineno))
    assert len(rows)==4760,len(rows)
    return rows

def vanilla(path):
    with zipfile.ZipFile(path) as z:
        ts,parents,text=title_tree(z)
    return ts,parents,text

def aliases_for_id(key):
    name=key[2:]
    variants={name,re.sub(r'_\d+$','',name)}
    for prefix in ('BAL_','BOR_','IDO_','MNG_','PHI_','SuMa_','MPK_'):
        if name.startswith(prefix):variants.add(name[len(prefix):])
    return variants

def current_localization():
    loc={}
    for p in (ROOT/'localization/english').rglob('*.yml'):
        loc.update(loc_read(p.read_text(encoding='utf-8-sig')))
    return loc

if __name__=='__main__':
    import sys,json
    ts,pa,txt=vanilla(sys.argv[1]);idx=defaultdict(set)
    for key in ts:
        for alias in aliases_for_id(key):idx[(key[0],norm(alias))].add(key)
    unresolved=[]
    for row in source_rows():
        ids=idx[(row['tier'],norm(row['original']))]
        if not ids:unresolved.append(row)
    print('Matched by identifier:',4760-len(unresolved),'Unresolved:',len(unresolved))
    print('CHANGED UNRESOLVED')
    for row in unresolved:
        if row['tag']!='K':print(row['tier'],row['original'],'->',row['new'])
    print('RETAINED UNRESOLVED')
    print(json.dumps([(x['tier'],x['original']) for x in unresolved if x['tag']=='K'],ensure_ascii=True))
