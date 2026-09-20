# Antiquity 359 BC — 0.2.0

For Crusader Kings III 1.19.0.6. Start a **new campaign** at “359 BC: The Rise of Macedon.” Restart CK3 after updating so it reloads localization. Faith identifiers and starting population history have changed; an existing 0.1 save is not a supported migration target.

The official working directory on this computer is `C:\antiquity_359_bc`. The launcher descriptor can point directly to this directory. The downloadable ZIP also includes a backup-preserving installer for a separate Documents installation.

## Changes in this release

- Added 171 regional culture definitions, for 237 custom definitions and 221 cultures used by counties at the bookmark. Reworked 1,048 county culture/faith assignments.
- Separated faith identifiers from culture identifiers, removing the localization collision that made cultures appear as “Anatolian Rites,” “Italic Rites,” and similar religious names.
- Added regional peoples across Italy, Anatolia, the Balkans, Gaul, Iberia, Britain, northern Europe, North Africa and India. Examples include Samnites, Umbrians, Carians, Lycians, Phrygians, Arverni, Arevaci, Brigantes, Kuru, Panchala, Vanga and Atavika.
- Defined 46 custom faiths, including five Vedic textual traditions, early Buddhist, Nirgrantha and Ajivika communities, and regional Mediterranean cults. Faiths and cultures are independently assigned.
- Removed the single Indo-Aryan culture from starting county populations. Regional Indo-Aryan-speaking cultures coexist with modeled Munda, Dravidian and Himalayan communities. This is a regional breakdown, not a claim that northern India stopped speaking Indo-Aryan languages.
- Corrected language and heritage links for several ancient peoples, including Etruscan, Punic, Egyptian, Anatolian and Munda cultures.
- Replaced offset-year displays in standard date formatting, era warnings, culture formation/entry dates, the culture ledger, ruler selection, legends and dynasty history.

## Expected technology dates

| Era | Earliest displayed availability |
|---|---|
| Early Antiquity | 359 BC start |
| Middle Antiquity | 100 BC |
| Late Antiquity | AD 200 |
| Pre-Medieval | AD 700 |
| Early Medieval | AD 900 |
| High Medieval | AD 1050 |
| Late Medieval | AD 1200 |

Other innovation and government prerequisites still apply. The dates do not force every culture to advance immediately.

## Verification

Static checks passed for identifiers, culture/faith naming collisions, language/heritage references, doctrines, holy sites, localization duplicates, innovation/era references and brace balance. County ownership is preserved. Calendar arithmetic includes the 1 BC → AD 1 boundary, with no year zero.

**This release has not been launched in CK3.** Native localization expressions were checked against the supplied game version, but their in-game rendering still needs a launch test. Check Middle Antiquity’s unavailable tooltip and the culture ledger first.

The English strings are mirrored under the other shipped language headers as fallbacks; they are not translations. Exact ancient borders and some tribal names are approximate: see `HISTORICAL_NOTES.md`. Vanilla graphics and name lists remain in use in many places.

`source_data/county_peoples_020.csv` records county assignments. `source_data/static_checks_020.json` records validation. `tools/revise_020.py` is a one-time migration from a backed-up 0.1 tree; do not run it over 0.2.
