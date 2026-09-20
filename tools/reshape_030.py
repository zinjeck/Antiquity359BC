"""Separate Egyptian, Punic and Balkan de jure regions; no de facto ownership changes."""
from pathlib import Path
import sys,json
from pdx import parse
from revise_020 import loc_read,tint
root=Path(sys.argv[1]);p=root/'common/landed_titles/aq_world.txt';s=p.read_text(encoding='utf-8-sig')
empires={n.key:n for n in parse(s) if n.key.startswith('e_')};kingdoms={}
for e,n in empires.items():
 for k in n.value:
  if k.key.startswith('k_'):kingdoms[k.key]=(e,k)
moves={
 'e_aq_nile':('Egyptian-Nubian Empire','Nile',['k_aq_egypt','k_aq_kush','k_blemmyia']),
 'e_aq_punic':('Punic Empire','Punic',['k_aq_carthage']),
 'e_aq_balkan':('Balkan Confederation','Balkan',['k_aq_illyria','k_aq_paeonia','k_aq_thrace','k_croatia','k_serbia','k_bulgaria']),
 'e_aq_caucasian':('Caucasian Confederation','Caucasian',['k_georgia']),
}
changes=[];added=[];audit=[];loc={}
for e,(name,adj,ks) in moves.items():
 blocks=[]
 for k in ks:
  old,n=kingdoms[k];blocks.append(s[n.start:n.end]);changes.append((n.start,n.end));audit.append({'kingdom':k,'old_empire':old,'new_empire':e})
 added.append(e+' = {\n color = { '+tint(e)+' }\n can_be_named_after_dynasty = no\n can_use_nomadic_naming = no\n can_create = { aq_can_form_empire_trigger = yes }\n can_create_on_partition = { aq_can_form_empire_trigger = yes }\n'+'\n'.join(blocks)+'\n}\n')
 loc[e]=name;loc[e+'_adj']=adj
for a,b in sorted(changes,reverse=True):s=s[:a]+s[b:]
p.write_text(s+'\n'+'\n'.join(added),encoding='utf-8-sig')
for lang in ('english','french','german','spanish','russian','simp_chinese','korean','japanese','polish'):
 p=root/f'localization/{lang}/replace/aq030_l_{lang}.yml';entries=loc_read(p.read_text(encoding='utf-8-sig'));entries.update(loc)
 p.write_text('l_'+lang+':\n'+''.join(f' {k}:0 "{v}"\n' for k,v in sorted(entries.items())),encoding='utf-8-sig')
(root/'source_data/de_jure_moves_030.json').write_text(json.dumps(audit,indent=2),encoding='utf-8')
print('Moved',len(audit),'kingdoms into four appropriate de jure regions.')
