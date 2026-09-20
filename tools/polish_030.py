"""Close alternate title-creation routes and name formable steppe confederations."""
from pathlib import Path
import sys,zipfile,re
from pdx import parse,decode
from revise_020 import loc_read
root=Path(sys.argv[1]);z=zipfile.ZipFile(sys.argv[2])
def source(p):
    if (root/p).exists():return (root/p).read_text(encoding='utf-8-sig')
    return re.sub(r'(?<![\w.])(\d{3,4})(\.\d{1,2}\.\d{1,2})(?![\w.])',lambda m:str(int(m[1])+1000)+m[2],decode(z.read('game/'+p)))
for rel,keys in {
 'common/decisions/80_major_decisions.txt':{'found_duchy_decision':'aq_can_form_chiefdom_union_trigger','found_kingdom_decision':'aq_can_form_kingdom_trigger','found_empire_decision':'aq_can_form_empire_trigger'},
 'common/decisions/80_major_decisions_central_asia.txt':{'become_greatest_of_khans_decision':'aq_can_form_empire_trigger'},
 'common/decisions/dlc_decisions/mpo/mpo_decisions.txt':{'confederation_kingdom_decision':'aq_can_form_kingdom_trigger','mpo_become_greatest_of_khans_decision':'aq_can_form_empire_trigger'},
}.items():
 s=source(rel);changes=[]
 for n in parse(s):
  if n.key not in keys:continue
  f=next(x for x in n.value if x.key=='is_valid');pos=s.index('{',f.start)+1
  changes.append((pos,'\n'+keys[n.key]+' = yes\n'))
 for pos,value in sorted(changes,reverse=True):s=s[:pos]+value+s[pos:]
 p=root/rel;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(s,encoding='utf-8-sig')
names={
 'k_pontic_steppe':'Scythian Confederation','k_caspian_steppe':'Sarmatian Confederation','k_caucasus':'North Caucasian Confederation',
 'k_otuken':'Orkhon Confederation','k_naimania':'Altai Confederation','k_tuva':'Sayan Confederation',
 'k_khakassia':'Tagar Confederation','k_buryatia':'Baikal Confederation','k_angara':'Angara Confederation','k_gobi':'Gobi Confederation',
 'k_zhetysu':'Saka Tigraxauda Confederation','k_cuman':'Northern Saka Confederation','k_qara_dala':'Eastern Saka Confederation',
 'k_saryarka':'Issedonian Confederation','k_kipchak':'Western Saka Confederation','k_dzungaria':'Dzungarian Confederation',
 'k_khotan':'Tarim League','k_oghuz_il':'Dahae Confederation','k_syr_darya':'Massagetae Confederation','k_transoxiana':'Sogdian League',
 'k_hexi':'Yuezhi Confederation','k_xia':'Ordos Confederation','k_balhae':'Eastern Manchurian Confederation',
 'k_shiwei':'Northeastern Forest Confederation','k_khitan':'Donghu Confederation','k_luzhen':'Liao League','k_raole':'Rehe Confederation',
}
for lang in ('english','french','german','spanish','russian','simp_chinese','korean','japanese','polish'):
 entries={}
 for key,value in names.items():entries[key]=value;entries[key+'_adj']=value.removesuffix(' Confederation').removesuffix(' League')
 for p in (root/'localization'/lang).rglob('*.yml'):
  lines=p.read_text(encoding='utf-8-sig').splitlines(True)
  p.write_text(''.join(l for l in lines if not ((m:=re.match(r'\s+([^ :]+):',l)) and m[1] in entries)),encoding='utf-8-sig')
 p=root/f'localization/{lang}/replace/aq030_confederations_l_{lang}.yml'
 p.write_text('l_'+lang+':\n'+''.join(f' {k}:0 "{v}"\n' for k,v in sorted(entries.items())),encoding='utf-8-sig')
# Move vanilla title overrides into replace/ to avoid native localization collisions.
for lang in ('english','french','german','spanish','russian','simp_chinese','korean','japanese','polish'):
 p=root/f'localization/{lang}/aq_l_{lang}.yml';s=p.read_text(encoding='utf-8-sig');moved={};kept=[]
 for l in s.splitlines(True):
  m=re.match(r'\s+([ekdcb]_[^ :]+):',l)
  if m:moved.update(loc_read(l))
  else:kept.append(l)
 p.write_text(''.join(kept),encoding='utf-8-sig')
 q=root/f'localization/{lang}/replace/aq030_title_adjectives_l_{lang}.yml'
 q.write_text('l_'+lang+':\n'+''.join(f' {k}:0 "{v}"\n' for k,v in sorted(moved.items())),encoding='utf-8-sig')
# Generated dynasty localization had one confirmed engine hash collision with a native decision.
for p in root.rglob('*'):
 if not p.is_file() or p.suffix not in ('.yml','.txt') or 'tools' in p.parts or 'religion' in p.parts:continue
 s=p.read_text(encoding='utf-8-sig')
 if p.suffix=='.yml':s=re.sub(r'(?m)^(\s*)aq_dyn_1459:',r'\1aq030_dynasty_name_1459:',s)
 elif 'dynasties' in p.parts:s=re.sub(r'(\bname\s*=\s*)aq_dyn_1459\b',r'\1aq030_dynasty_name_1459',s)
 if s!=p.read_text(encoding='utf-8-sig'):p.write_text(s,encoding='utf-8-sig')
# Engine reports UTF-8 BOM expectations for scripted data. Preserve religion bytes as requested.
for folder in ('common','history','events'):
 for p in (root/folder).rglob('*.txt'):
  if 'religion' in p.parts:continue
  if not p.read_bytes().startswith(b'\xef\xbb\xbf'):p.write_text(p.read_text(encoding='utf-8-sig'),encoding='utf-8-sig')
print('Alternative formation decisions and regional title names updated.')
