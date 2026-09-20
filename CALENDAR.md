# Calendar implementation

CK3 history and era gates use positive internal years, shifted by 1,000 years:

- An internal year at or below 1000 displays as `(1001 - year) BC`.
- An internal year above 1000 displays as `(year - 1000) AD`.
- 642 = 359 BC; 901 = 100 BC; 1000 = 1 BC; 1001 = AD 1; 1200 = AD 200; 1700 = AD 700.

Changing the actual gate from 901 to 100 would unlock Middle Antiquity before the bookmark. The gates therefore remain unchanged; the display is converted.

`localization/english/replace/aq_calendar_l_english.yml` overrides native date templates and the era warning `INNOVATION_ERA_NOT_IN_YEAR`. It uses native `LessThanOrEqualTo_int32`, `Subtract_int32`, `IntToString` and `Select_CString` localization functions. The numeric placeholder convention `'(int32)$YEAR|q$'` follows the typed placeholder pattern in 1.19.0.6 localization.

Direct `GetYear` UI strings are also converted: culture formation and culture ledger dates, ruler selection, reigns, legends and dynasty history. Era-entry labels convert their JOINED and LEFT year values. Initial culture era entry was moved from internal 641 to 642, the 359 BC bookmark year.

This is a display conversion, not an engine calendar replacement. Saved-game serialization, console/debug values and script comparisons continue to use the internal year. Durations, ages and yearly rates are not shifted. A future new native UI using a raw year rather than these templates will need its own override.

Static arithmetic and expression-shape checks are not a CK3 runtime test. Confirm the HUD, Middle Antiquity availability tooltip, culture formation/ledger dates and era-entry labels after restarting and starting a new campaign.
