.tables

.schema reviews

.mode box

SELECT app\_name, COUNT(\*) FROM reviews GROUP BY app\_name;

.read queries.sql

.quit

&nbsp;

╭────────────────────────────────┬──────────╮

│            app\_name            │ COUNT(\*) │

╞════════════════════════════════╪══════════╡

│ IVY Period & Pregnancy Tracker │     5019 │

│ IVY Wellness Coach             │     1207 │

╰────────────────────────────────┴──────────╯

SQLite-3.54 ivy\_reviews.db-\> .read queries.sql

╭───────────────┬──────────┬────┬──────────┬───────┬─────┬──────────┬──────────╮

│   app\_name    │  store   │ n  │avg\_rating│pct\_1\_2│pct\_5│first\_date│last\_date │

╞═══════════════╪══════════╪════╪══════════╪═══════╪═════╪══════════╪══════════╡

│IVY Period &   │Apple App │4519│      3.51│   29.6│ 41.9│2011-06-04│2026-10-17│

│Pregnancy      │Store     │    │          │       │     │12:47:31  │23:34:36  │

│Tracker        │          │    │          │       │     │          │          │

├───────────────┼──────────┼────┼──────────┼───────┼─────┼──────────┼──────────┤

│IVY Period &   │Google    │ 500│      2.51│   60.0│ 27.0│2020-10-16│2026-09-05│

│Pregnancy      │Play      │    │          │       │     │18:58:34  │16:10:53  │

│Tracker        │          │    │          │       │     │          │          │

├───────────────┼──────────┼────┼──────────┼───────┼─────┼──────────┼──────────┤

│IVY Wellness   │Apple App │ 707│      3.14│   37.5│ 29.4│2015-07-12│2026-02-08│

│Coach          │Store     │    │          │       │     │03:26:32  │13:21:08  │

├───────────────┼──────────┼────┼──────────┼───────┼─────┼──────────┼──────────┤

│IVY Wellness   │Google    │ 500│      2.34│   62.0│ 16.8│2018-12-28│2026-09-06│

│Coach          │Play      │    │          │       │     │19:27:08  │16:45:01  │

╰───────────────┴──────────┴────┴──────────┴───────┴─────┴──────────┴──────────╯

╭────────────────────────────────┬─────────────────┬────┬─────────┬─────────╮

│            app\_name            │      store      │ n  │ avg\_12m │ pct\_1\_2 │

╞════════════════════════════════╪═════════════════╪════╪═════════╪═════════╡

│ IVY Period & Pregnancy Tracker │ Apple App Store │ 47 │    2.55 │    59.6 │

│ IVY Period & Pregnancy Tracker │ Google Play     │ 46 │    4.09 │    21.7 │

│ IVY Wellness Coach             │ Apple App Store │  2 │     1.5 │   100.0 │

│ IVY Wellness Coach             │ Google Play     │ 22 │    4.14 │    22.7 │

╰────────────────────────────────┴─────────────────┴────┴─────────┴─────────╯

╭─────────┬────────────────────────────────┬────┬────────────┬───────┬─────────╮

│  month  │            app\_name            │ n  │ avg\_rating │ pct\_5 │ pct\_1\_2 │

╞═════════╪════════════════════════════════╪════╪════════════╪═══════╪═════════╡

│ 2025-01 │ IVY Period & Pregnancy Tracker │  8 │       2.25 │  25.0 │    62.5 │

│ 2025-01 │ IVY Wellness Coach             │  2 │        2.0 │   0.0 │   100.0 │

│ 2025-02 │ IVY Period & Pregnancy Tracker │  8 │       2.63 │  25.0 │    62.5 │

│ 2025-02 │ IVY Wellness Coach             │  5 │        2.4 │  20.0 │    60.0 │

│ 2025-03 │ IVY Period & Pregnancy Tracker │  4 │       2.25 │   0.0 │    50.0 │

│ 2025-03 │ IVY Wellness Coach             │  3 │        3.0 │  33.3 │    33.3 │

│ 2025-04 │ IVY Period & Pregnancy Tracker │ 13 │       2.15 │   0.0 │    53.8 │

│ 2025-05 │ IVY Period & Pregnancy Tracker │ 13 │       2.08 │  15.4 │    69.2 │

│ 2025-05 │ IVY Wellness Coach             │  2 │        2.5 │   0.0 │    50.0 │

│ 2025-06 │ IVY Period & Pregnancy Tracker │  7 │       2.43 │  14.3 │    57.1 │

│ 2025-06 │ IVY Wellness Coach             │  1 │        3.0 │   0.0 │     0.0 │

│ 2025-07 │ IVY Period & Pregnancy Tracker │  7 │       2.29 │  28.6 │    71.4 │

│ 2025-08 │ IVY Period & Pregnancy Tracker │ 11 │       2.82 │  45.5 │    54.5 │

│ 2025-08 │ IVY Wellness Coach             │  1 │        3.0 │   0.0 │     0.0 │

│ 2025-09 │ IVY Period & Pregnancy Tracker │  3 │        5.0 │ 100.0 │     0.0 │

│ 2025-09 │ IVY Wellness Coach             │  1 │        1.0 │   0.0 │   100.0 │

│ 2025-10 │ IVY Period & Pregnancy Tracker │  7 │       2.14 │  14.3 │    71.4 │

│ 2025-10 │ IVY Wellness Coach             │  1 │        2.0 │   0.0 │   100.0 │

│ 2025-11 │ IVY Period & Pregnancy Tracker │  2 │        2.5 │   0.0 │    50.0 │

│ 2025-12 │ IVY Period & Pregnancy Tracker │  6 │       2.33 │  16.7 │    66.7 │

│ 2025-12 │ IVY Wellness Coach             │  1 │        1.0 │   0.0 │   100.0 │

│ 2026-01 │ IVY Period & Pregnancy Tracker │  8 │       1.38 │   0.0 │    87.5 │

│ 2026-01 │ IVY Wellness Coach             │  2 │        3.0 │  50.0 │    50.0 │

│ 2026-02 │ IVY Period & Pregnancy Tracker │  5 │        1.6 │   0.0 │    80.0 │

│ 2026-02 │ IVY Wellness Coach             │  1 │        2.0 │   0.0 │   100.0 │

│ 2026-03 │ IVY Period & Pregnancy Tracker │  4 │        3.5 │  50.0 │    25.0 │

│ 2026-04 │ IVY Period & Pregnancy Tracker │  8 │       3.13 │  37.5 │    62.5 │

│ 2026-04 │ IVY Wellness Coach             │  3 │       2.67 │  33.3 │    66.7 │

│ 2026-05 │ IVY Period & Pregnancy Tracker │  8 │       3.38 │  50.0 │    37.5 │

│ 2026-06 │ IVY Period & Pregnancy Tracker │  7 │       2.57 │  28.6 │    57.1 │

│ 2026-06 │ IVY Wellness Coach             │  1 │        1.0 │   0.0 │   100.0 │

│ 2026-07 │ IVY Period & Pregnancy Tracker │ 25 │        4.2 │  80.0 │    20.0 │

│ 2026-07 │ IVY Wellness Coach             │ 15 │        5.0 │ 100.0 │     0.0 │

│ 2026-08 │ IVY Period & Pregnancy Tracker │ 15 │        4.6 │  80.0 │     6.7 │

│ 2026-09 │ IVY Period & Pregnancy Tracker │  3 │       3.33 │  33.3 │    33.3 │

│ 2026-09 │ IVY Wellness Coach             │  1 │        1.0 │   0.0 │   100.0 │

│ 2026-10 │ IVY Period & Pregnancy Tracker │  2 │        1.0 │   0.0 │   100.0 │

╰─────────┴────────────────────────────────┴────┴────────────┴───────┴─────────╯

╭──────┬────────────────────────────────┬─────┬───────────────┬─────────────╮

│ year │            app\_name            │  n  │ loss\_mentions │ pct\_of\_year │

╞══════╪════════════════════════════════╪═════╪═══════════════╪═════════════╡

│ 2022 │ IVY Period & Pregnancy Tracker │ 120 │            23 │        19.2 │

│ 2022 │ IVY Wellness Coach             │  97 │             6 │         6.2 │

│ 2023 │ IVY Period & Pregnancy Tracker │ 642 │            65 │        10.1 │

│ 2023 │ IVY Wellness Coach             │  45 │             2 │         4.4 │

│ 2024 │ IVY Period & Pregnancy Tracker │ 225 │            14 │         6.2 │

│ 2024 │ IVY Wellness Coach             │  45 │             2 │         4.4 │

│ 2025 │ IVY Period & Pregnancy Tracker │  89 │             9 │        10.1 │

│ 2025 │ IVY Wellness Coach             │  17 │             1 │         5.9 │

│ 2026 │ IVY Period & Pregnancy Tracker │  85 │             9 │        10.6 │

│ 2026 │ IVY Wellness Coach             │  23 │             0 │         0.0 │

╰──────┴────────────────────────────────┴─────┴───────────────┴─────────────╯

╭───────────────┬────────────────┬────────┬──────────┬────────────┬────────────╮

│   app\_name    │     theme      │mentions│avg\_rating│negative\_1\_2│positive\_4\_5│

╞═══════════════╪════════════════╪════════╪══════════╪════════════╪════════════╡

│IVY Period &   │App Bugs,       │     187│      1.56│         161│          16│

│Pregnancy      │Crashes &       │        │          │            │            │

│Tracker        │Login/Data Loss │        │          │            │            │

├───────────────┼────────────────┼────────┼──────────┼────────────┼────────────┤

│IVY Period &   │Cycle &         │     172│      2.58│         102│          62│

│Pregnancy      │Pregnancy       │        │          │            │            │

│Tracker        │Tracking        │        │          │            │            │

├───────────────┼────────────────┼────────┼──────────┼────────────┼────────────┤

│IVY Period &   │Wearable Sync & │      35│      3.11│          17│          18│

│Pregnancy      │Hardware        │        │          │            │            │

│Tracker        │(IVY+/Leaf)     │        │          │            │            │

├───────────────┼────────────────┼────────┼──────────┼────────────┼────────────┤

│IVY Period &   │Subscription &  │      33│      2.21│          21│           7│

│Pregnancy      │Paywall (       │        │          │            │            │

│Tracker        │Membership)     │        │          │            │            │

├───────────────┼────────────────┼────────┼──────────┼────────────┼────────────┤

│IVY Period &   │AI Assistant &  │       7│      4.57│           0│           6│

│Pregnancy      │Chat/Coach      │        │          │            │            │

│Tracker        │                │        │          │            │            │

├───────────────┼────────────────┼────────┼──────────┼────────────┼────────────┤

│IVY Wellness   │Wearable Sync & │     660│      2.66│         335│         209│

│Coach          │Hardware        │        │          │            │            │

│               │(IVY+/Leaf)     │        │          │            │            │

├───────────────┼────────────────┼────────┼──────────┼────────────┼────────────┤

│IVY Wellness   │App Bugs,       │     253│      2.18│         161│          48│

│Coach          │Crashes &       │        │          │            │            │

│               │Login/Data Loss │        │          │            │            │

├───────────────┼────────────────┼────────┼──────────┼────────────┼────────────┤

│IVY Wellness   │Cycle &         │     153│      2.76│          69│          50│

│Coach          │Pregnancy       │        │          │            │            │

│               │Tracking        │        │          │            │            │

├───────────────┼────────────────┼────────┼──────────┼────────────┼────────────┤

│IVY Wellness   │Subscription &  │     127│      1.72│         103│          16│

│Coach          │Paywall (       │        │          │            │            │

│               │Membership)     │        │          │            │            │

├───────────────┼────────────────┼────────┼──────────┼────────────┼────────────┤

│IVY Wellness   │AI Assistant &  │      34│      2.65│          18│          13│

│Coach          │Chat/Coach      │        │          │            │            │

╰───────────────┴────────────────┴────────┴──────────┴────────────┴────────────╯

╭────────────────────────────────┬──────────┬────┬────────────┬─────────╮

│            app\_name            │ is\_burst │ n  │ avg\_rating │ pct\_1\_2 │

╞════════════════════════════════╪══════════╪════╪════════════╪═════════╡

│ IVY Period & Pregnancy Tracker │        0 │ 53 │       2.53 │    60.4 │

│ IVY Period & Pregnancy Tracker │        1 │ 40 │       4.35 │    15.0 │

│ IVY Wellness Coach             │        0 │  9 │       2.11 │    77.8 │

│ IVY Wellness Coach             │        1 │ 15 │        5.0 │     0.0 │

╰────────────────────────────────┴──────────┴────┴────────────┴─────────╯

╭────────────────────────────────┬────────┬────╮

│            app\_name            │ rating │ n  │

╞════════════════════════════════╪════════╪════╡

│ IVY Period & Pregnancy Tracker │    1.0 │  4 │

│ IVY Period & Pregnancy Tracker │    4.0 │  3 │

│ IVY Period & Pregnancy Tracker │    5.0 │ 18 │

│ IVY Wellness Coach             │    1.0 │  5 │

│ IVY Wellness Coach             │    2.0 │  2 │

│ IVY Wellness Coach             │    5.0 │ 17 │

╰────────────────────────────────┴────────┴────╯

╭────────────────────────────────┬─────────────────┬─────────┬──────┬────╮

│            app\_name            │      store      │ paywall │ sync │ ai │

╞════════════════════════════════╪═════════════════╪═════════╪══════╪════╡

│ IVY Period & Pregnancy Tracker │ Apple App Store │      36 │   15 │  8 │

│ IVY Period & Pregnancy Tracker │ Google Play     │      17 │    8 │  0 │

│ IVY Wellness Coach             │ Apple App Store │      10 │  125 │  0 │

│ IVY Wellness Coach             │ Google Play     │      13 │  187 │  2 │

╰────────────────────────────────┴─────────────────┴─────────┴──────┴────╯

╭──────────────────────────────┬───────────────┬───┬───────┬──────────╮

│           app\_name           │     store     │ n │replied│reply\_rate│

╞══════════════════════════════╪═══════════════╪═══╪═══════╪══════════╡

│IVY Period & Pregnancy Tracker│Google Play    │500│    479│      95.8│

│IVY Wellness Coach            │Apple App Store│500│      0│       0.0│

│IVY Wellness Coach            │Google Play    │500│    475│      95.0│

╰──────────────────────────────┴───────────────┴───┴───────┴──────────╯

╭────────────────────────────────┬─────────────────┬─────────┬─────╮

│            app\_name            │      store      │ country │  n  │

╞════════════════════════════════╪═════════════════╪═════════╪═════╡

│ IVY Period & Pregnancy Tracker │ Apple App Store │ au      │ 500 │

│ IVY Period & Pregnancy Tracker │ Apple App Store │ ca      │ 500 │

│ IVY Period & Pregnancy Tracker │ Apple App Store │ gb      │ 500 │

│ IVY Period & Pregnancy Tracker │ Apple App Store │ mx      │ 500 │

│ IVY Period & Pregnancy Tracker │ Apple App Store │ us      │ 500 │

│ IVY Period & Pregnancy Tracker │ Google Play     │ us      │ 500 │

│ IVY Wellness Coach             │ Apple App Store │ us      │ 500 │

│ IVY Wellness Coach             │ Google Play     │ us      │ 500 │

│ IVY Period & Pregnancy Tracker │ Apple App Store │ nz      │ 478 │

│ IVY Period & Pregnancy Tracker │ Apple App Store │ ie      │ 379 │

│ IVY Period & Pregnancy Tracker │ Apple App Store │ de      │ 352 │

│ IVY Period & Pregnancy Tracker │ Apple App Store │ nl      │ 300 │

│ IVY Period & Pregnancy Tracker │ Apple App Store │ it      │ 264 │

│ IVY Period & Pregnancy Tracker │ Apple App Store │ es      │ 246 │

│ IVY Wellness Coach             │ Apple App Store │ ca      │  82 │

│ IVY Wellness Coach             │ Apple App Store │ gb      │  58 │

│ IVY Wellness Coach             │ Apple App Store │ au      │  41 │

│ IVY Wellness Coach             │ Apple App Store │ de      │   9 │

│ IVY Wellness Coach             │ Apple App Store │ nl      │   4 │

│ IVY Wellness Coach             │ Apple App Store │ fr      │   3 │

╰────────────────────────────────┴─────────────────┴─────────┴─────╯

&nbsp;

&nbsp;