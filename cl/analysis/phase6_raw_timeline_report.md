# Phase 6 — Raw timeline inspection for Q2 diary days

대표 Q2 0→1 날짜를 raw sensor/app timeline으로 그려서 Phase 5의 `inward day` 해석이 시간축에서도 보이는지 확인했다. 예측모델/OOF/submission 없음.

## Timeline summary

| subject_id | lifelog_date | note | labels | top_apps | total_app_min | night_top_category | night_top_min | night_screen_sum | activity_sum_raw | gps_points | hr_mean |
|---|---|---|---|---|---|---|---|---|---|---|---|
| id10 | 2024-09-07 | night social phone / low mobility | Q1=1 Q2=1 Q3=0 S1=1 S2=1 S3=1 S4=1 | 카카오톡(256m), one ui 홈(256m), threads(98m), naver(90m), instagram(54m), 코레일톡(22m) | 936.88 | messaging_social | 123.26 | 276 | 5520 | 15486 | 88.32 |
| id05 | 2024-09-22 | zero-step + YouTube/night-phone | Q1=1 Q2=1 Q3=0 S1=0 S2=0 S3=0 S4=0 | one ui 홈(121m), youtube(110m), naver(80m), new york mysteries 1(51m), 캐시워크(41m), 카카오톡(32m) | 515.26 | other | 110.13 | 218 | 3847 | 15805 | nan |
| id01 | 2024-08-31 | low-mobility/low-HR/rest | Q1=1 Q2=1 Q3=1 S1=1 S2=1 S3=1 S4=1 | one ui 홈(102m), ✝️성경일독q(80m), gs shop(50m), 쿠팡(40m), naver(39m), youtube(36m) | 530.55 | video_music_media | 25.31 | 75 | 4104 | 7009 | 63.00 |
| id09 | 2024-07-13 | webtoon/TikTok/night-phone | Q1=0 Q2=1 Q3=1 S1=1 S2=1 S3=0 S4=1 | 카카오톡(123m), microsoft launcher(104m), 네이버 웹툰(95m), one ui 홈(94m), youtube(16m), 네이버 지도(15m) | 558.82 | utility_home | 89.98 | 137 | 5193 | 19934 | 68.83 |
| id08 | 2024-08-16 | Q2=1 Q3=0 app/internal case | Q1=0 Q2=1 Q3=0 S1=1 S2=0 S3=1 S4=0 | one ui 홈(148m), 시스템 ui(126m), 카카오톡(72m), youtube(65m), google play 스토어(42m), 클래시 로얄(38m) | 636.02 | utility_home | 24.28 | 48 | 5728 | 0 | nan |
| id03 | 2024-07-25 | high-Q anchor, active but Q2 flip | Q1=1 Q2=1 Q3=1 S1=1 S2=0 S3=0 S4=0 | 시스템 ui(232m), 카카오톡(76m), one ui 홈(50m), 통화(28m), 재난문자(18m), instagram(14m) | 475.93 | utility_home | 49.78 | 29 | 4312 | 10209 | 106.93 |


## Figures

- `id10 2024-09-07` — night social phone / low mobility: `/Users/kbsoo/Downloads/cl/analysis/figures/phase6_timelines/id10_2024-09-07.png`

- `id05 2024-09-22` — zero-step + YouTube/night-phone: `/Users/kbsoo/Downloads/cl/analysis/figures/phase6_timelines/id05_2024-09-22.png`

- `id01 2024-08-31` — low-mobility/low-HR/rest: `/Users/kbsoo/Downloads/cl/analysis/figures/phase6_timelines/id01_2024-08-31.png`

- `id09 2024-07-13` — webtoon/TikTok/night-phone: `/Users/kbsoo/Downloads/cl/analysis/figures/phase6_timelines/id09_2024-07-13.png`

- `id08 2024-08-16` — Q2=1 Q3=0 app/internal case: `/Users/kbsoo/Downloads/cl/analysis/figures/phase6_timelines/id08_2024-08-16.png`

- `id03 2024-07-25` — high-Q anchor, active but Q2 flip: `/Users/kbsoo/Downloads/cl/analysis/figures/phase6_timelines/id03_2024-07-25.png`


## 해석 메모

- Q2 diary 대표일은 대체로 외부 이동 증가보다는 app/screen burst, 낮은 activity, 적은 GPS/context, 또는 긴 screen-off/rest block 중 하나로 설명된다.

- 다만 id03처럼 활동량이 높은데도 Q2가 켜지는 contradiction day가 있어, Q2는 단일 규칙이 아니라 subject-specific transition subtype으로 봐야 한다.

- 이 단계는 feature selection이 아니라 label semantics 검증이다. 다음은 S2 contradiction timeline 또는 subtype별 subject comparison이 자연스럽다.
