# AG opinions index checkpoint 2026-10-23

DATABASE_URL was unset, so no corpus rows were written. Discover-only read of https://law.georgia.gov/opinions and robots.txt.

| Source | URL | HTTP | Bytes | SHA-256 | Notes |
| --- | --- | ---: | ---: | --- | --- |
| opinions index | https://law.georgia.gov/opinions | 200 | 146,784 | `84e54cf4281caed04a05fe15df5940bad76a68531955e98e46a77bd966a9f0e1` | Index labels only; prior 2026-10-10 hash differed |
| robots.txt | https://law.georgia.gov/robots.txt | 200 | 1,677 | `1ec8e6c4fed3dc4f55da7a82412fc7bb6649941ba44ccc6b47ba7968604d1c1b` | Allows /opinions |

The index names approximately 60 hrefs containing "opinion" and several document download links (examples 81726-unofficial-ag-opinionpdf, 032426-official-ag-opinionpdf). Citation-like tokens such as 2013-2 through later years are present. None of the PDFs were downloaded. Category indexes and pagination were not walked. Lexis was not opened. These counts are not persisted coverage and not current-law verification.
