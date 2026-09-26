# Antiquity 359 BC: title and political-history revision 0.4.0

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

## Bosporan consistency refinement
Pantikapaion (Kerch) and Hermonassa (Taman) now use their attested Greek settlement names rather than the source list's broad Taurica/Maeotis fallback. Their capital holdings use the established Hellenic culture and faith; rural baronies retain their existing cultures. The new Taman governor Philiskos is explicitly fictional. Hermonassa's old nomad holding is now a tribal holding, and its ruler no longer has the nomadic_philosophy trait that would force a nomadic government back on game start. This is the single intentional reduction from 323 to 322 nomadic counties. No government or faith definitions are altered.
References for these identifications: https://en.wikipedia.org/wiki/Pantikapaion ; https://en.wikipedia.org/wiki/Tmutarakan ; the ancient-place discussion is distinct from any modern territorial claims.
Migration sequence from the backed-up 0.3 baseline: tools/revise_040.py, then tools/polish_040.py. Do not rerun the older 0.3 generators over 0.4 without reconciling their source data.

## Final Hellespont integration and launch registration
Abydos and its Troas/Hellespont county belong to the Persian satrapal hierarchy. The other Aegean islands are not annexed merely because the medieval map grouped them with Abydos. A separate Hellespont duchy keeps the native barony and province IDs intact. See https://en.wikipedia.org/wiki/Abydos_(Hellespont) for the historical overview and its references.
The reproducible sequence from the backed-up 0.3 baseline is revise_040.py, polish_040.py, then integrate_040.py. The latter is also safe to repeat on the resulting 0.4 tree; it does not reassign unrelated realms. render_040.ps1 produces a static native-province preview, not an in-game screenshot. All older generator snapshots remain historical records, not the authoritative 0.4 county distribution.
