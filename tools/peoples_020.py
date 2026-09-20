"""Original scenario data. No Fallen Eagle script or map assignments are copied.

County placements are authored approximations, not exact historical boundaries.
The supplied 300 BC map is used cautiously for peoples, never its successor states.
"""

# key | displayed culture | old template | faith suffix | language | title footprint
# Last matching entry wins, allowing counties to refine a larger region.
DATA = '''
samnite|Samnite|italic|mefitis|oscan|d_benevento d_salerno
umbrian|Umbrian|italic|iguvine|umbrian|d_spoleto
picene|Picene|italic|italic|picene|d_ancona
sabine|Sabine|italic|italic|oscan|c_tivoli c_abruzzi
marsian|Marsian|italic|italic|oscan|c_lanciano c_teramo
campanian|Campanian|italic|italic|oscan|d_capua
lucanian|Lucanian|italic|mefitis|oscan|c_camarda
bruttian|Bruttian|italic|mefitis|oscan|c_cosenza
iapygian|Iapygian|italic|italic|messapic|d_apulia
daunian|Daunian|italic|italic|messapic|c_foggia
messapian|Messapian|italic|italic|messapic|c_lecce
ligurian|Ligurian|italic|ligurian|ligurian|d_genoa c_cuneo c_tortona
taurinian|Taurini|gaulish|celtic|gaulish|c_turin c_monferrato
insubrian|Insubres|gaulish|celtic|gaulish|c_lombardia c_como c_pavia c_novara
cenomanian|Cenomani|gaulish|celtic|gaulish|c_brescia c_cremona
boian|Boii|gaulish|celtic|gaulish|d_emilia c_bologna c_parma
senonian|Senones|gaulish|celtic|gaulish|c_ravenna c_fermo
rhaetian|Rhaetian|italic|rhaetian|rhaetian|c_trent d_tyrol d_currezia
histrian|Histrian|illyrian|balkan|histrian|d_istria
carnian|Carni|gaulish|celtic|gaulish|c_friuli c_gorz
nuragic|Nuragic|italic|nuragic|nuragic|d_sardinia
corsican|Corsi|italic|nuragic|nuragic|d_corsica
sicanian|Sicani|italic|sicanian|sicanian|c_agrigento
elymian|Elymi|italic|elymian|elymian|c_palermo
lydian|Lydian|anatolian|artimu|lydian|d_thracesia
phrygian|Phrygian|anatolian|matar|phrygian|d_opsikion d_anatolia c_lower_galatia c_galatia
mysian|Mysian|anatolian|matar|mysian|c_mysia c_prusa
bithynian|Bithynian|thracian|balkan|thracian|d_optimatoi c_nikaea
paphlagonian|Paphlagonian|anatolian|ma|paphlagonian|d_paphlagonia c_honorias c_hadrianopolis
carian|Carian|anatolian|labraundos|carian|c_caria
lycian|Lycian|anatolian|leto|lycian|c_lycia
pamphylian|Pamphylian|hellenic|hellenic_pagan|greek|c_pamphylia
pisidian|Pisidian|anatolian|matar|pisidian|c_pisidia c_selge c_philomelium
isaurian|Isaurian|anatolian|sandas|luwian|c_isauria
lycaonian|Lycaonian|anatolian|sandas|luwian|c_lycaonia c_galatia_salutaris
cappadocian|Cappadocian|anatolian|ma|cappadocian|d_cappadocia d_charsianon d_sebasteia d_armeniac
cilician|Cilician|anatolian|sandas|luwian|d_cilicia
chalybian|Chalybes|anatolian|ma|chalybian|c_colonea c_satala
colchian|Colchian|kartvelian|anatolian|kartvelian|d_chaldia d_abkhazia
ionian|Ionian|hellenic|hellenic_pagan|greek|c_ionia
aeolian|Aeolian|hellenic|hellenic_pagan|greek|c_aeolis
odrysian|Odrysian|thracian|balkan|thracian|d_thrace d_philippopolis
bessian|Bessi|thracian|balkan|thracian|d_bulgaria
triballian|Triballi|thracian|balkan|thracian|d_vidin d_turnovo
getian|Getae|daco_getic|zalmonian|thracian|d_dobrudja d_muntenia d_oltenia k_moldavia
dacian|Dacian|daco_getic|zalmonian|thracian|d_transylvania d_transylvanian_alps d_bihar
paeonian|Paeonian|thracian|balkan|paeonian|c_skopje
dardanian|Dardanian|illyrian|balkan|illyrian|d_rashka d_macva
taulantian|Taulantii|illyrian|balkan|illyrian|d_dyrrachion
ardiaean|Ardiaei|illyrian|balkan|illyrian|d_duklja d_ragusa
delmatian|Delmatae|illyrian|balkan|illyrian|d_dalmatia d_bosna d_lower_bosna
liburnian|Liburni|illyrian|balkan|liburnian|d_croatia
pannonian|Pannonian|illyrian|balkan|pannonian|d_slavonia d_usora d_syrmia d_bacs
scordiscian|Middle Danubian Celts|gaulish|celtic|gaulish|d_somogy d_temes
tauriscian|Taurisci|gaulish|celtic|gaulish|d_krain d_carinthia d_steyermark
noric|Noric|gaulish|celtic|gaulish|d_salzburg d_osterreich
helvetian|Helvetii|gaulish|celtic|gaulish|d_transjurania d_upper_burgundy
arvernian|Arverni|gaulish|celtic|gaulish|d_auvergne
aeduian|Aedui|gaulish|celtic|gaulish|d_burgundy d_bourbon
biturigian|Bituriges|gaulish|celtic|gaulish|d_berry
parisian|Parisii|gaulish|celtic|gaulish|d_valois
carnutian|Carnutes|gaulish|celtic|gaulish|d_orleans
remian|Remi|gaulish|celtic|gaulish|d_champagne
venetian_gaul|Veneti of Armorica|gaulish|celtic|gaulish|d_brittany
aulercian|Aulerci|gaulish|celtic|gaulish|d_normandy
andecavian|Andecavi|gaulish|celtic|gaulish|d_anjou
pictonian|Pictones|gaulish|celtic|gaulish|d_poitou
santonian|Santones|gaulish|celtic|gaulish|d_aquitaine
volcian|Volcae|gaulish|celtic|gaulish|d_toulouse d_languedoc
aquitani|Aquitani|iberian|iberian|aquitanian|d_gascogne d_armagnac
allobrogian|Allobroges|gaulish|celtic|gaulish|d_savoie d_dauphine
saluvian|Salluvii|gaulish|celtic|gaulish|d_provence
menapian|Menapii|gaulish|celtic|gaulish|d_flanders d_brabant
treverian|Treveri|gaulish|celtic|gaulish|d_luxembourg d_lower_lorraine
mediomatrician|Mediomatrici|gaulish|celtic|gaulish|d_upper_lorraine d_bar
sequanian|Sequani|gaulish|celtic|gaulish|d_alsace
vindelician|Vindelici|gaulish|celtic|gaulish|d_augsburg d_swabia d_bavaria
boian_danube|Danubian Boii|gaulish|celtic|gaulish|k_bohemia d_nordgau
celtiberian_arevaci|Arevaci|celtiberian|celtic|celtiberian|d_castilla
vaccaean|Vaccaei|celtiberian|celtic|celtiberian|d_leon
asturian_ancient|Astures|celtiberian|celtic|celtiberian|d_asturias
cantabrian|Cantabri|celtiberian|celtic|celtiberian|d_cantabria
gallaecian|Gallaeci|celtiberian|celtic|celtiberian|d_galicia d_porto
lusitanian|Lusitani|celtiberian|lusitanian|lusitanian|d_coimbra d_beja
vettonian|Vettones|celtiberian|lusitanian|lusitanian|d_badajoz
carpetanian|Carpetani|celtiberian|celtic|celtiberian|d_toledo
turdetanian|Turdetani|iberian|iberian|tartessian|d_sevilla d_cordoba
bastetanian|Bastetani|iberian|iberian|iberian|d_granada d_murcia
contestanian|Contestani|iberian|iberian|iberian|d_valencia
edetanian|Edetani|iberian|iberian|iberian|d_aragon
ilercavonian|Ilercavones|iberian|iberian|iberian|d_barcelona
vasconian|Vascones|iberian|iberian|aquitanian|d_navarra d_viscaya
celtician|Celtici|celtiberian|celtic|celtiberian|d_algarve
talaiotic|Talaiotic|iberian|iberian|talaiotic|d_mallorca
brigantian|Brigantes|brythonic|celtic|brittonic|d_york d_lancaster
iceni|Iceni|brythonic|celtic|brittonic|d_norfolk
trinovantian|Trinovantes|brythonic|celtic|brittonic|d_bedford
cantiacian|Cantiaci|brythonic|celtic|brittonic|d_canterbury
dobunnian|Dobunni|brythonic|celtic|brittonic|d_gloucester
cornovian|Cornovii|brythonic|celtic|brittonic|d_hereford
dumnonian|Dumnonii|brythonic|celtic|brittonic|d_cornwall d_somerset
votadinian|Votadini|brythonic|celtic|brittonic|d_northumberland d_lothian
novantian|Novantae|brythonic|celtic|brittonic|d_galloway
damnonian|Damnonii|brythonic|celtic|brittonic|d_cumbria
ordovician|Ordovices|brythonic|celtic|brittonic|d_gwynedd d_powys
demetian|Demetae|brythonic|celtic|brittonic|d_deheubarth
caledonian|Caledonian|pictish|celtic|brittonic|d_albany d_moray
epidian|Epidii|pictish|celtic|brittonic|d_the_isles d_western_isles
voluntian|Voluntii|goidelic|celtic|goidelic|d_ulster
eblanian|Eblani|goidelic|celtic|goidelic|d_meath
brigantian_irish|Irish Brigantes|goidelic|celtic|goidelic|d_leinster
ivernian|Iverni|goidelic|celtic|goidelic|d_munster
nagnatian|Nagnatae|goidelic|celtic|goidelic|d_connacht
cimbrian|Cimbri|germanic|germanic|germanic|d_jylland
teutonian|Teutones|germanic|germanic|germanic|d_slesvig d_holstein
suionian|Suiones|germanic|germanic|germanic|d_svealand d_bergslagen
gautish|Gautar|germanic|germanic|germanic|d_vastergotland d_ostergotland d_smaland
gutnian|Gutones|germanic|germanic|germanic|d_gotland d_pomerelia
rugian|Rugii|germanic|germanic|germanic|d_viken d_agder d_vestlandi
chaucan|Chauci|germanic|germanic|germanic|d_frisia d_holland d_utrecht d_gelre
cheruscan|Cherusci|germanic|germanic|germanic|d_angria d_westfalen d_ostfalen
suebian|Suebi|germanic|germanic|germanic|d_anhalt d_thuringia d_hesse d_east_franconia d_west_franconia d_ostmark d_nordmark d_pommerania
harudian|Harudes|germanic|germanic|germanic|d_sjaelland d_skane
numidian_massylian|Massylii|berber|libyan|libyco_berber|d_bejaia d_zab d_kroumerie
numidian_masaesylian|Masaesyli|berber|libyan|libyco_berber|d_tlemcen d_tahert d_alger
maurian|Mauri|berber|libyan|libyco_berber|k_maghreb
gaetulian|Gaetuli|berber|libyan|libyco_berber|d_mzab d_jerid
garamantian|Garamantes|saharan|libyan|libyco_berber|d_fezzan d_ghat
nasamonian|Nasamones|berber|libyan|libyco_berber|d_syrte
gandharan|Gandharan|indo_aryan|rigvedic|gandhari|d_gandhara
kambojan|Kambojan|bactrian|steppe|iranian_eastern|d_kabul d_pamir
madra|Madra|indo_aryan|rigvedic|northwest_prakrit|d_lahore
trigartan|Trigarta|indo_aryan|rigvedic|northwest_prakrit|c_trigarta c_kangra
malava|Malava|indo_aryan|rigvedic|northwest_prakrit|d_multan
saindhava|Saindhava|indo_aryan|atharvavedic|sindhic|d_sauvira d_bhakkar
kuru|Kuru|indo_aryan|krishna_yajurvedic|shauraseni|d_kuru d_haritanaka
panchala|Panchala|indo_aryan|shukla_yajurvedic|shauraseni|d_vodamayutja c_hastinapura
surasena|Surasena|indo_aryan|samavedic|shauraseni|d_mathura
matsya|Matsya|indo_aryan|rigvedic|shauraseni|d_ajmer
salva|Salva|indo_aryan|rigvedic|shauraseni|d_jangladesh d_stravani
abhira|Abhira|indo_aryan|yaksha_naga|western_prakrit|d_maru
sivi|Sivi|indo_aryan|rigvedic|western_prakrit|d_medapata
avanti|Avanti|indo_aryan|samavedic|avanti_prakrit|d_dadhipadra d_akara_dasarna
anupa|Anupa|indo_aryan|yaksha_naga|avanti_prakrit|d_anupa
anarta|Anarta|indo_aryan|samavedic|western_prakrit|d_anartta d_gurjara_mandala
saurashtra|Saurashtra|indo_aryan|samavedic|western_prakrit|d_saurashtra
lata|Lata|indo_aryan|atharvavedic|western_prakrit|d_lata
kosalan|Kosalan|indo_aryan|shukla_yajurvedic|kosali_prakrit|d_saryupara d_kanyakubja
vatsa|Vatsa|indo_aryan|krishna_yajurvedic|shauraseni|c_prayaga c_asni c_manikpur
chedi|Chedi|indo_aryan|atharvavedic|central_prakrit|d_jejakabhukti d_dahala
kasi|Kashi|magadhan|shukla_yajurvedic|kosali_prakrit|d_kasi
videha|Videha|magadhan|shukla_yajurvedic|magadhi|d_tirabhukti
malla|Malla|magadhan|buddha|magadhi|c_kusinagara
anga|Anga|magadhan|ajivika|magadhi|c_mudgagiri
pundra|Pundra|gangetic|yaksha_naga|eastern_prakrit|d_varendra d_gauda
vanga|Vanga|gangetic|yaksha_naga|eastern_prakrit|d_vanga d_nadia
suhma|Suhma|gangetic|yaksha_naga|eastern_prakrit|d_suhma
kalinga|Kalingan|gangetic|nirgrantha|eastern_prakrit|d_kalinga d_tosali
atavi|Atavika|dravidian|forest_indian|munda|d_jharkand d_daksina_kosala d_ratanpur d_dandakaranya
pulinda|Pulinda|dravidian|forest_indian|central_dravidian|c_chauragarh c_damoh c_gurgi c_mandapika
kirata|Kirata|himalayan|himalayan|kirati|k_himalaya
kasmira|Kashmira|indo_aryan|atharvavedic|dardic|d_kasmira
pragjyotisha|Pragjyotisha|gangetic|yaksha_naga|eastern_prakrit|k_kamarupa
asmaka|Asmaka|indo_aryan|krishna_yajurvedic|maharashtri|d_devagiri d_nasikya
vidarbha|Vidarbha|indo_aryan|atharvavedic|maharashtri|d_vidharba
andhra|Andhra|dravidian|dravidian|telugu|k_andhra k_telingana
chola|Chola|dravidian|murukan|tamil|d_chola_nadu d_tondai_nadu
pandya|Pandya|dravidian|murukan|tamil|d_pandya_nadu
chera|Chera|dravidian|murukan|tamil|d_chera_nadu
alupa|Alupa|dravidian|dravidian|tulu|d_konkana
kadamba_early|Early Kannada|dravidian|dravidian|kannada|k_karnata d_rattapadi
'''

# Descriptive labels are used where no ancient name for an entire religion is attested.
# These are not claims that modern reconstruction labels were ancient self-designations.
FAITH_NAMES = {
 'balkan':'Thracian Polytheism', 'italic':'Italic Polytheism', 'punic':'Cult of Baal Hammon',
 'kemetic':'Netjeru', 'mesopotamian':'Mesopotamian Polytheism', 'anatolian':'Anatolian Polytheism',
 'steppe':'Scythian Polytheism', 'celtic':'Druidism', 'iberian':'Iberian Polytheism',
 'germanic':'Germanic Polytheism', 'libyan':'Libyco-Berber Polytheism',
 'african':'Ancestral Veneration', 'arabian':'South Semitic Polytheism', 'vedic':'Śrauta',
 'dravidian':'Southern Indian Polytheism', 'himalayan':'Himalayan Ancestor Worship',
 'chinese':'Zhou Ancestral Religion', 'asian':'Local Spirit Worship',
 'religio_romana':'Religio Romana', 'etruscan':'Disciplina Etrusca',
 'mefitis':'Cult of Mefitis', 'iguvine':'Iguvine Religion', 'ligurian':'Ligurian Polytheism',
 'rhaetian':'Rhaetian Polytheism', 'nuragic':'Nuragic Religion', 'sicanian':'Sicanian Polytheism',
 'elymian':'Cult of Eryx', 'artimu':'Cult of Artimu', 'matar':'Cult of Matar',
 'labraundos':'Cult of Zeus Labraundos', 'leto':'Cult of Leto', 'sandas':'Cult of Sandas',
 'ma':'Cult of Ma', 'zalmonian':'Cult of Zalmoxis', 'lusitanian':'Lusitanian Polytheism',
 'rigvedic':'Ṛgvedic Śrauta', 'krishna_yajurvedic':'Kṛṣṇa-Yajurvedic Śrauta',
 'shukla_yajurvedic':'Śukla-Yajurvedic Śrauta', 'samavedic':'Sāmavedic Śrauta',
 'atharvavedic':'Ātharvavedic Tradition', 'buddha':'Buddhadharma', 'nirgrantha':'Nirgrantha Dharma',
 'ajivika':'Ājīvika', 'yaksha_naga':'Yakṣa-Nāga Worship', 'forest_indian':'Forest Ancestor Worship',
 'murukan':'Murukaṉ Worship',
}

# Faiths are grouped by related traditions; not one religion per tribe.
# suffix: (native template, family key, three tenets, description)
SPECIAL_FAITHS = {
 'rigvedic':('hinduism','shrauta','literalism astrology ritual_hospitality','A Vedic recitational and sacrificial tradition centered on the Rigveda. Represented as a CK3 faith for gameplay, not a claim of a separate historical church.'),
 'krishna_yajurvedic':('hinduism','shrauta','literalism esotericism ritual_hospitality','Black Yajurvedic ritual transmission, combining sacrificial formulas and explanatory prose. County placement is a regional approximation.'),
 'shukla_yajurvedic':('hinduism','shrauta','literalism reincarnation ritual_hospitality','White Yajurvedic ritual transmission, associated with the Vajasaneyi tradition. The model distinguishes textual lineages without asserting exclusive territorial congregations.'),
 'samavedic':('hinduism','shrauta','literalism communal_identity ritual_hospitality','Vedic ritual communities emphasizing the chanted melodies of the Samaveda. This is an overlapping priestly tradition represented through CK3 faith mechanics.'),
 'atharvavedic':('hinduism','shrauta','literalism esotericism sanctity_of_nature','Atharvavedic transmission joins domestic, healing and royal ritual with Vedic learning. Its distribution is provisional.'),
 'buddha':('buddhism','buddhadharma','dharmic_pacifism monasticism mendicant_preachers','Early Buddhist communities following the Buddha and the sangha, before the later Mahayana and Theravada identities used by the medieval game.'),
 'nirgrantha':('jainism','nirgrantha','dharmic_pacifism asceticism vows_of_poverty','Early Nirgrantha communities associated with Mahavira, before the later sectarian divisions represented in vanilla CK3.'),
 'ajivika':('jainism','ajivika','asceticism astrology mendicant_preachers','The ascetic Ajivika tradition associated with Makkhali Gosala and niyati, or destiny. Surviving accounts are largely external and its county distribution is approximate.'),
 'yaksha_naga':('paganism','indian_local','sanctity_of_nature ancestor_worship esotericism','Local veneration of yakshas, nagas and sacred places. Such practices crossed linguistic and social boundaries and are not treated as simply Vedic.'),
 'forest_indian':('paganism','indian_local','sanctity_of_nature ancestor_worship communal_identity','A conservative umbrella for poorly documented forest-community traditions. This label does not invent a supposedly attested ancient endonym.'),
 'murukan':('paganism','tamil_sacred','sanctity_of_nature sacred_childbirth communal_identity','An early Tamil sacred tradition represented around Murukan. Later devotional institutions are not projected wholesale into this start.'),
}

FAITH_OVERRIDES = {
 'c_gaya':'buddha','c_sravasti':'buddha','c_kusinagara':'buddha','c_simaramapura':'nirgrantha',
 'c_magadha':'ajivika','c_rothas':'forest_indian','c_damin_i_koh':'forest_indian',
 'c_udabhanda':'rigvedic','c_munda':'forest_indian','c_jharkand':'forest_indian',
}

# Deliberate elite/local differences, rather than copying the ruler to the whole county.
HISTORICAL_CULTURES = {'aq_mausolus':'carian','aq_artemisia':'carian','aq_idrieus':'carian','aq_ada':'carian','aq_hecatomnus':'carian','aq_paeonia':'paeonian','aq_thrace':'odrysian','aq_berisades':'odrysian','aq_amadocus':'odrysian'}

# Names used only for new language pillars, never religious names.
LANG_NAMES = {
 'oscan':'Oscan','umbrian':'Umbrian','picene':'South Picene','messapic':'Messapic',
 'ligurian':'Ligurian','gaulish':'Gaulish','rhaetian':'Rhaetian','histrian':'Histrian',
 'nuragic':'Paleo-Sardinian','sicanian':'Sicanian','elymian':'Elymian','lydian':'Lydian',
 'phrygian':'Phrygian','mysian':'Mysian','thracian':'Thracian','paphlagonian':'Paphlagonian',
 'carian':'Carian','lycian':'Lycian','pisidian':'Pisidian','luwian':'Luwian',
 'cappadocian':'Cappadocian','chalybian':'Chalybian','kartvelian':'Kartvelian',
 'paeonian':'Paeonian','illyrian':'Illyrian','liburnian':'Liburnian','pannonian':'Pannonian',
 'aquitanian':'Aquitanian','celtiberian':'Celtiberian','lusitanian':'Lusitanian',
 'tartessian':'Tartessian','iberian':'Iberian','talaiotic':'Balearic',
 'brittonic':'Common Brittonic','goidelic':'Early Goidelic','germanic':'Proto-Germanic',
 'libyco_berber':'Libyco-Berber','gandhari':'Gandhari','iranian_eastern':'Eastern Iranian',
 'northwest_prakrit':'Northwestern Prakrit','sindhic':'Early Sindhic','shauraseni':'Shauraseni Prakrit',
 'western_prakrit':'Western Prakrit','avanti_prakrit':'Avanti Prakrit','kosali_prakrit':'Eastern Middle Indo-Aryan',
 'central_prakrit':'Central Prakrit','magadhi':'Magadhi Prakrit','eastern_prakrit':'Eastern Prakrit',
 'munda':'Early Munda','central_dravidian':'Central Dravidian','dardic':'Early Dardic',
 'maharashtri':'Western Deccan Prakrit','tulu':'Early Tulu',
}

PEOPLES = [dict(zip(('key','name','base','faith','language','titles'),line.split('|'))) for line in DATA.strip().splitlines()]
# Atavika is an Indic forest population, never use the old African aesthetic placeholder.
for row in PEOPLES:
    if row['key']=='atavi':row['base']='dravidian'
