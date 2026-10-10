# Georgia court rules indexes — discover-only checkpoint

Fetch date: 2026-10-10 09:01 UTC. DATABASE_URL was unset, so no corpus rows were written and no coverage is claimed.

Official indexes on www.gasupreme.us. robots.txt disallows `/wp-content/uploads/`, so no PDF was downloaded. Filenames are index labels only, not effective dates and not stored rule text. Lexis was not opened. Court of Appeals rules index was not readable (AWS WAF captcha, HTTP 405).

| Source | URL | HTTP | Bytes | SHA-256 | PDF links named |
| --- | --- | ---: | ---: | --- | ---: |
| Supreme Court rules index | https://www.gasupreme.us/rules/ | 200 | 1,594,903 | `95608f4a78399d2889a35b3a0356fb03c1fc5da0beede43840273563aa3fd9dc` | 3 |
| Other court rules index | https://www.gasupreme.us/other-court-rules/ | 200 | 1,594,928 | `51741266e74082e7fb01d06efedeb8124eac45335c43f1b9b3161c91333f1c50` | 7 |
| Other codes and rules index | https://www.gasupreme.us/other-codes-rules/ | 200 | 1,606,028 | `31c2c4c5a716930457027321cd97a3e8695a69533e1fc5f38379c0cc088e377b` | 27 |
| robots.txt | https://www.gasupreme.us/robots.txt | 200 | 71 | `2c3d50be784b56de8c6cbdc174817ab688c3b9892494616d3a414a115aa85196` | 0 |
| Court of Appeals rules | https://www.gaappeals.gov/court-rules/ | 405 | — | — | 0 (WAF captcha) |

These counts are not persisted coverage. A missing DATABASE_URL means no authority rows can be written.

## Named PDF labels on the Supreme Court rules index (not downloaded)

- `/wp-content/uploads/2026/07/SupremeCourtRules_eff-July-2-2026.pdf`
- `/wp-content/uploads/2026/07/CHART-WEB-POSTING-July-2-2026.pdf`
- `/wp-content/uploads/2026/01/QUICK-REFERENCE-RULES.pdf`

## Named PDF labels on the other-court-rules index (not downloaded)

- `/wp-content/uploads/2026/04/UNIFORM-SUPERIOR-COURT-RULES-2026_04_09.pdf`
- `/wp-content/uploads/2024/01/UNIFORM-STATE-COURT-RULES-2024_01_18.pdf`
- `/wp-content/uploads/2026/09/UNIFORM-JUVENILE-COURT-RULES-2026_09_03_ADA.pdf`
- `/wp-content/uploads/2023/05/UNIFORM-PROBATE-COURT-RULES-2023_06_01.pdf`
- `/wp-content/uploads/2023/03/UNIFORM-MAGISTRATE-COURT-RULES-2023_04_01.pdf`
- `/wp-content/uploads/2025/12/UNIFORM-MUNICIPAL-COURT-RULES-2024_12_12.pdf`
- `/wp-content/uploads/2026/06/State-wide-Business-Court-Rules-2026_06_11.pdf`

## Named PDF labels on the other-codes-rules index (not downloaded)

- `/wp-content/uploads/2025/12/Order_Amend-Part-A-Fitness-Board-Membership_issued.pdf`
- `/wp-content/uploads/2024/02/Code-of-Judicial-Conduct-2024_02_01.pdf`
- `/wp-content/uploads/2024/02/Rule-2.5-order_final_issued_1.pdf`
- `/wp-content/uploads/2020/07/order-amending-CJC-Terminology-section-definition-of-law-Issued.pdf`
- `/wp-content/uploads/2018/10/CODE_OF_JUDICIAL_CONDUCT_AMENDMENT_ORDER_OCTOBER_22_2018.pdf`
- `/wp-content/uploads/2016/09/Order_CJC_FINAL.pdf`
- `/wp-content/uploads/2016/09/Order_CJC_REDLINE-.pdf`
- `/wp-content/uploads/2015/06/georgia_code_judicial_conduct_revised_5-14-15.pdf`
- `/wp-content/uploads/2019/08/Civil_Domestic_Filing_Disposition_Form-FINAL-eff-010120.pdf`
- `/wp-content/uploads/2026/03/JQC-RULES-2023_02_03.pdf`
- `/wp-content/uploads/2026/03/JQC-Rules-Amendment-Approval-Order_entered_sub.pdf`
- `/wp-content/uploads/2026/03/Replacement-Citizen-Order_entered.pdf`
- `/wp-content/uploads/2026/03/JQC_RULES_AMENDMENT_ORDER_OCTOBER_22_2018.pdf`
- `/wp-content/uploads/2026/03/JQC_Final_Rules_Order.pdf`
- `/wp-content/uploads/2026/03/JQC_Interim_Rules_Order_06-28-17.pdf`
- `/wp-content/uploads/2019/04/JURY_COMPOSITION_RULE_2019-04-11.pdf`
- `/wp-content/uploads/2025/03/RulesForLegalInterpreting_updatedMarch2025.pdf`
- `/wp-content/uploads/2024/01/Order-_-Amended-Rules-for-LegaInterpreting.pdf`
- `/wp-content/uploads/2020/10/Statewide-Min-Standards-Rules-final.pdf`
- `/wp-content/uploads/2018/06/UNIFIED_APPEAL-06_06_18.pdf`
- `/wp-content/uploads/2025/12/2026-UAP-amendments-Final-Order_entered.pdf`
- `/wp-content/uploads/2019/02/Uniform_Misdemeanor_Citation_Approval_Order_jul_2019.pdf`
- `/wp-content/uploads/2019/02/Uniform_Misdemeanor_Citation_Rules_FINAL_REVISED_07-01-2019.pdf`
- `/wp-content/uploads/2018/12/Uniform_Misdemeanor_Citation_Approval_Order_dec_2018.pdf`
- `/wp-content/uploads/2018/12/Uniform_Misdemeanor_Citation_Rules_FINAL_ADOPTED_12-7-18.pdf`
- `/wp-content/uploads/2018/12/Uniform_Misdemeanor_Citation_Form-_FINAL_ADOPTED_12-7-18.pdf`
- `/wp-content/uploads/2018/12/Uniform_Transfer_Rule_Adopted_Judicial_Council_12-7-2018-_FINAL.pdf`

Gap notes: all listed PDFs live under `/wp-content/uploads/` and are blocked by robots.txt. Filename dates are not stored effective dates and not proof of currency. No rule text was parsed or persisted. Court of Appeals HTML rule pages remain unreachable behind WAF. These labels are not unannotated OCGA text.
