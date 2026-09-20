# Antiquity 359 BC — 0.3.0

For CK3 1.19.0.6. Restart CK3 and start a **new campaign** at 359 BC. Existing 0.2 saves are not migrated: culture IDs, governments, title holders and de jure regions changed.

The official folder is `C:\antiquity_359_bc`. The launcher points there. The ZIP also includes an installer for a separate Documents installation.

## Cultures

- One Egyptian culture under one Egyptian heritage, outside Arabic.
- Arabic contains exactly **Mashriqi, Sabaean and Bedouin**. Removed the custom Arabian and duplicate Egyptian cultures. Maghrebi belongs to Berber heritage.
- Achaemenid Persian is now **Persian**. Added Median, Cadusian, Hyrcanian, Parthian, Arian, Margian, Elamite and Chorasmian regional populations. Achaemenid remains a dynasty.
- Added 61 cultures, bringing the starting map to 281 active cultures. Divided the former 48-county Suebi block into smaller populations.
- Added geographic divisions around the Vistula, Bug, Pripyat, Desna and Dnieper. These are reconstructions, not claims of attested 359 BC tribal names.
- China distinguishes Qin, Wei, Han of the Central Plains, Zhao, Yan, Qi, Lu, Song, Zhou, Chu, Wu, Yue, Ba, Shu, Zhongshan and southern communities.

## Realms

- Dissolved 739 generic independent duchies. There are 2,858 independent county-level chiefdoms. Major states and their vassal hierarchies remain.
- Assigned 323 steppe counties to native nomadic government and holdings. Populations include Scythians, Sarmatians, Saka, Dahae, Massagetae, Yuezhi and Donghu. They start as small political units, not vast unified confederations.
- Native nomadic play requires **Khans of the Steppe**. Startup no longer forces everyone into tribal government and respects the native DLC check.
- Replaced active medieval empire labels with Hellenic, Semitic, Gallic and other regional names. Eleven kingdoms moved into Egyptian-Nubian, Punic, Balkan and Caucasian de jure regions.
- Renamed formable steppe kingdoms, removing later Cuman and Kipchak labels. These are possible scenario empires, not claims they all existed in 359 BC.

## Nomadic progression

| Rule | Initially | Tribal Councils | Confederate Administration |
|---|---|---|---|
| League size | 3 rulers | 6 rulers | Early cap removed |
| Nomadic duchy conquest | Locked | Available | Available |
| Nomadic kingdom/empire formation | Locked | Locked | Available with fame requirements |
| Large nomadic invasion/subjugation | Locked | Locked | Available |
| Additional early war cost | 2x | 2x | Removed |

Native requirements still apply. Tribal Councils is an Early Antiquity innovation. Confederate Administration requires Middle Antiquity, available from **100 BC**. Nomadic kingdom/empire formation requires Living Legend fame. Existing kings and emperors have exemptions for further titles of their existing rank.

Before Confederate Administration, nomads have -10 vassal opinion, +100% title creation cost and reduced AI aggression. Realms exceeding eight counties also have -25 vassal opinion, -0.5 monthly prestige and +50% men-at-arms maintenance. Conditions refresh yearly. County conquest, migration and raiding remain available under native rules.

Gates cover de jure creation, automatic partition creation, custom-title decisions and relevant nomadic decisions. Offer and join interactions share the league-size check. These rules slow consolidation; strong rulers may still expand.

## Religion and verification

**Every file under common/religion is byte-identical to the pre-0.3 version.** No tenets, doctrines, holy sites or faith definitions changed. Only county and generated-family religious placement changed, primarily in steppe and Chinese regions. Named elites can retain their faiths.

Static checks passed for culture load order, Arabic/Egyptian membership, references, family cultures, governments/holdings, liege chains, creation gates, localization and innovations. All 3,476 counties retain holders. Previous BC/AD display changes remain.

**This build has not been launched or simulation-tested in CK3.** Check a new steppe ruler, culture map, chiefdom ranks, empire map and confederation tooltip. Long-term balance needs playtesting. Existing 0.2 logs also contain unrelated historical-character and faith-icon warnings; this revision does not claim to eliminate every pre-existing warning. Faith-file warnings were left alone to preserve the requested religious settings.

English strings are mirrored under other language headers as fallbacks, not translations. See HISTORICAL_NOTES.md and SOURCES.md for limitations. County assignments and checks are in source_data/county_peoples_030.csv and source_data/static_checks_030.json.

Migration helpers are one-time tools. From a backed-up 0.2 tree, with authored balance files present, run revise_030.py, finish_030.py, polish_030.py, reshape_030.py, then check_030.py. Do not run these over an already revised tree.
