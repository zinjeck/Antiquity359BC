"""Authored 359 BC population refinements. Later tribal attestations are scenario proxies."""
# key | name | 0.2 template | geographic footprints (vanilla county/duchy keys)
DATA='''
semnonian|Semnones|suebian|d_anhalt d_nordmark
hermundurian|Hermunduri|suebian|d_thuringia d_east_franconia
chattian|Chatti|suebian|d_hesse
marcomannic_early|Marcomanni|suebian|d_west_franconia
langobardic_early|Langobardi|suebian|d_ostfalen
varinian|Varini|suebian|d_pommerania
lemovian|Lemovii|suebian|d_ostmark
ubian|Ubii|germanic|c_aachen c_cleves
eburonian|Eburones|menapian|c_maastricht
raumarician|Raumarici|germanic|c_hedmork c_eystridalir c_gudbrandsdalir
trondish_early|Trondelag|germanic|c_trandheim c_gauldala c_namdalfylki
haelsingian|Haelsingi|germanic|c_halsingland c_medelpad c_angermanland
rani_early|Ranii|germanic|c_norwegian_more c_firdafylki
vistulan_early|Upper Vistulan|slavic|d_lesser_poland d_upper_silesia
bugian_early|Western Bug|slavic|d_cherven_cities d_volhynia d_mazovia
pripyatian|Pripyat|slavic|d_pinsk d_turov d_minsk
dnieper_upper|Upper Dnieper|slavic|d_smolensk d_karachev
desnian|Desna|slavic|d_chernigov d_novosil
dnieper_middle|Middle Dnieper|slavic|d_kiev d_pereyaslavl
dniestrian_early|Upper Dniester|slavic|d_halych
pomeranian_early|Pomeranian|slavic|d_kuyavia d_wielkopolska
odra_early|Oder|slavic|d_lower_silesia d_lausitz d_meissen
median|Median|persian|d_hamadan d_rayy d_kermanshah d_azerbaijan
cadusian|Cadusian|persian|d_daylam d_shirvan
hyrcanian|Hyrcanian|persian|d_gurgan d_tabaristan
parthian_early|Parthian|persian|d_nishapur d_nasa
arian_early|Arian|persian|d_herat d_ghur
margian|Margian|persian|d_merv
elamite|Elamite|persian|d_khuzestan
chorasmian|Chorasmian|sogdian|d_khorezm
dahaean|Dahae|saka|d_transcaspiana d_garabogazkol d_uzboy
massagetan|Massagetae|saka|d_aral_il d_aral_karakum d_syr_darya d_barsuki
tigraxauda|Saka Tigraxauda|saka|d_talas_alatau d_muyunkum d_zhetysu d_ili-alatau
haumavarga|Saka Haumavarga|saka|d_ferghana d_chah
issедonian|Issedones|saka|d_saryarka d_qyzylsaryarka d_betpa d_karkaraly
pazyryk|Pazyryk|saka|d_altay d_akaltay d_katu_yaryk d_khovd
yuezhi_early|Yuezhi|steppe_eastern|d_guasha d_gansu d_qilian d_xiutu d_juyan
donghu|Donghu|steppe_eastern|d_EM_onon d_EM_wajiezi d_EM_yujuelu d_dauria d_em_wuguguo d_em_tataria
ordos|Ordos|steppe_eastern|d_langshan d_shuofang d_tiande
qin|Qin|sinitic|d_yongxing d_fengxiang d_binning d_jingyuan d_jinshang d_qincheng d_longyou
jin_wei|Wei|sinitic|d_hezhong d_zhenghua d_yuncao
jin_han|Han of the Central Plains|sinitic|d_heyang d_chenxu d_shanguo
zhao|Zhao|sinitic|d_hedong d_zelu d_chengde d_xingming d_yanmen
yan|Yan|sinitic|d_youzhou d_sanggan d_yunshuo d_yingmo
qi|Qi|sinitic|d_ziqing d_yideng d_cangjing d_weibo
lu|Lu|sinitic|d_yanhai
song|Song|sinitic|d_biansong d_xusi
zhou|Zhou|sinitic|d_xinan d_dongji
chu|Chu|sinitic|d_xiangdeng d_jingnan d_eyue d_hunan d_huainan d_huaixi d_jiangxi d_lingling
wu_early|Wu|sinitic|d_jiangdong d_zhexi d_xuanshe
yue|Yue|baiyue|d_zhedong
minyue|Minyue|baiyue|d_weiwu d_jianning d_zhaoxin
dongou|Dong'ou|baiyue|d_pinghai
ba|Ba|sinitic|d_baqu d_kuizhong d_wuxin
shu|Shu|sinitic|d_xichuan d_dongchuan d_xingyuan d_qiongnan
zhongshan|Zhongshan|sinitic|c_zhenzhou
nanyue_early|Southern Yue|baiyue|d_lingnan d_gaoliang d_huixun d_rongguan d_yongguan d_guiguan d_jingjiang
luoyue|Luoyue|baiyue|d_thang_long d_lam_tay d_nghe_an d_hai_dong
dian|Dian|baiyue|d_tuodong d_tonghai d_yinsheng
yelang|Yelang|baiyue|d_zangke d_luoshi d_luodian d_qianzhong
qiang_early|Qiang|tibetan|d_xiasui d_fufang
'''.strip()
DATA=DATA.replace('issедonian','issedonian')
PEOPLES=[dict(zip(('key','name','base','titles'),line.split('|'))) for line in DATA.splitlines()]
NOMAD_CULTURES=set('scythian sarmatian saka dahaean massagetan tigraxauda issedonian pazyryk yuezhi_early donghu ordos steppe_eastern'.split())
# Archaeological names are not asserted to be named political confederations.
EMPIRES={
'e_byzantium':('Hellenic Empire','Hellenic'),'e_aq_persia':('Persian Empire','Persian'),
'e_arabia':('Semitic Empire','Semitic'),'e_france':('Gallic Empire','Gallic'),
'e_italy':('Italic Empire','Italic'),'e_germany':('Germanic Confederation','Germanic'),
'e_scandinavia':('Northern Tribal Confederation','Northern'),'e_britannia':('Britannic Confederation','Britannic'),
'e_wendish_empire':('Baltic Confederation','Baltic'),'e_west_slavia':('Vistula-Oder Confederation','Vistula-Oder'),
'e_russia':('Dnieper Confederation','Dnieper'),'e_volga-ural':('Volga-Ural Confederation','Volga-Ural'),
'e_siberia':('Ob-Irtysh Confederation','Ob-Irtysh'),'e_mongolia':('Eastern Steppe Confederation','Eastern Steppe'),
'e_tartaria':('Saka Confederation','Saka'),'e_turan':('Transoxian Empire','Transoxian'),
'e_caspian-pontic_steppe':('Scythian Confederation','Scythian'),'e_carpathia':('Danubian Confederation','Danubian'),
'e_maghreb':('Libyan Empire','Libyan'),'e_spain':('Iberian Confederation','Iberian'),
'e_abyssinia':('Nile-Horn Empire','Nile-Horn'),'e_azania':('East African Confederation','East African'),
'e_kanem_bornu':('Central Sahel Confederation','Central Sahel'),'e_mali':('Niger Confederation','Niger'),
'e_guinea':('Western Forest Confederation','Western Forest'),'e_bengal':('Gangetic Empire','Gangetic'),
'e_deccan':('Dakshinapatha Empire','Dakshinapatha'),'e_rajastan':('Aryavarta Empire','Aryavarta'),
'e_tibet':('Himalayan Confederation','Himalayan'),'e_andong':('Liao Confederation','Liao'),
'e_amur':('Amur Confederation','Amur'),'e_srivijaya':('Malay Confederation','Malay'),
'e_japan':('Wa Confederation','Wa'),'e_goryeo':('Samhan Confederation','Samhan'),
'e_nusantara':('Island Confederation','Island'),'e_suvarnabhumi':('Mainland Austroasiatic Confederation','Austroasiatic'),
'e_kambuja':('Mekong Confederation','Mekong'),'e_yongliang':('Western Huaxia Empire','Western Huaxia'),
'e_zhongyuan':('Central Huaxia Empire','Central Huaxia'),'e_jingyang':('Chu-Yue Empire','Chu-Yue'),
'e_liangyi':('Ba-Shu Empire','Ba-Shu'),'e_lingnan':('Southern Yue Confederation','Southern Yue'),
}
