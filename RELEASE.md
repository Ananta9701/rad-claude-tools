# RELEASE v2.67 — manifest v87 — 2026-09-29

> **v2.67** — Mac 에서도 테스트 전부 통과(글꼴 찾기)와 `mapfreeze --sources` 의 [필수] 멈춤(사용자 09-29). Mac(Claude Code Local)에는 `fc-list` 도 DejaVu 글꼴도 없어 test_toolkit 3건이 실패했다(398/401) — 건너뛰지 않고, `fc-list` 가 없으면 글꼴 폴더를 훑어 같은 색인을 만들고 테스트는 그 컴퓨터에 실제로 있는 글꼴(Linux DejaVu Sans · Mac Arial)로 같은 논리를 시험한다. 덱 테마 글꼴 파일을 못 찾아 근사 계산으로 넘어가면 [참고] 한 줄. `mapfreeze --sources` 는 보관소에 없는 DOI 를 만나면 `mapgraph --sources` 처럼 아무것도 기록하지 않고 멈춘다.

## 1. 바뀐 것

| 도구 | 판 | 내용 |
|---|---|---|
| `deck_toolkit.py` | 16.47 | 글꼴 색인: `fc-list` 가 없거나 비면 `FONT_DIRS`(`/System/Library/Fonts`·`/Library/Fonts`·`~/Library/Fonts`, fc-list 없는 Linux 의 `/usr/share/fonts`·`~/.fonts` 등)를 훑어 글꼴 파일의 이름 표(nameID 16·1 family — 지역 이름 포함, 17·2 style)로 fc-list 와 같은 색인. `.ttf`·`.otf`·`.ttc`·`.otc`, 모음의 둘째 이후 글꼴은 `x.ttc#N`(PIL 로 열 때 index). `fc-list` 가 있으면 전과 같다(같은 fc-list 출력에서 옛·새 색인이 같음을 확인). `overflow`·`fit-layout`·`fit-corner-boxes`: 테마 본문 글꼴 파일을 못 찾아 근사 모델로 잰 화면이 있으면 `[참고] 덱 테마 글꼴 "…" 파일을 이 컴퓨터에서 찾지 못해 …` 한 줄(돌려주는 문제 목록·종료 코드는 그대로). `theme_fonts_missing` 도 fc-list 가 없으면 이 색인으로(전에는 빈 목록) |
| `DECK_SPEC.md` | 16.47 | 머리에 한 줄, v16.13 글꼴 찾기 줄 |
| `claim_graph.py` | 16.10 | `mapfreeze --sources`: 문헌 근거의 DOI 가 보관소에 없으면 **[필수] — 아무것도 기록하지 않고 멈춤**(종료 코드 1, `-o` 파일 안 만듦, 없는 곳을 모두 적음). 보관소 폴더를 잘못 준 때도 멈춘다. `--sources` 가 없을 때·교과서 근거를 못 찾을 때·보관소에 있는 문헌의 `at` 을 못 찾을 때는 전과 같다 |
| `CLAIM_GRAPH.md` | 16.10 | §3-2 근거 칸 · 명령표 `mapfreeze` 줄 |
| 테스트 | — | test_toolkit: 글꼴 3건(overflow_font_path · v1613 · v1614)을 이 컴퓨터에 있는 Regular·Bold 짝 글꼴로(건너뜀 없음) + 2(fc-list 없이 실제 글꼴 폴더에서 같은 글꼴·굵은 짝 · 실제 Regular·Bold 로 만든 .ttc 두 글꼴과 `#1` · OTTO 머리 · 망가진·잘린 파일 · theme_fonts_missing · 근사 모델 알림 있음/없음 · CLI 세 명령의 [참고] 한 줄과 `--font-path` 면 없음). test_claim_graph 1(모두 있으면 기록 · 하나라도 없으면 멈추고 아무 주장에도 verified 없음 · 없는 폴더 · `--sources` 없으면 전처럼 · 교과서 못 찾음은 [참고] · CLI 종료 코드 1 과 출력 파일 없음) |

## 2. 회신 항목별 답

| 항목 | 반영 |
|---|---|
| 사용자 09-29: mapfreeze `--sources` 가 보관소에 없는 DOI 면 mapgraph 처럼 [필수]로 멈춤 | 위 claim_graph 16.10 |
| 사용자 09-29(Mac Local 점검): test_toolkit 글꼴 3건 — 건너뛰지 말고 Linux·Mac 모두 실제 글꼴로, fc-list 없으면 Mac 글꼴 폴더, 근사 계산이면 [참고] 한 줄 | 위 deck_toolkit 16.47 |

## 3. 받을 파일

**zip 없음.** 코드 세션이 공개 저장소(`rad-claude-tools`)와 비공개 저장소(`rad-claude-private`)에 직접 올린다.

<!-- sets:begin — release.py 가 만든다. 손으로 고치지 않는다 -->
### 저자 (7)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `claim_graph.py` | v16.10 | `47f516373f16` | ○ |
| `test_claim_graph.py` | v16.10 | `5817f71b4016` | ○ |
| `CLAIM_GRAPH.md` | v16.10 | `539acf8f59bc` | ○ |
| `verify_toolkit.py` | v1.3.7 | `0833539073f1` | — |
| `test_verify_toolkit.py` | v1.3.7 | `ac6e42ed2103` | — |
| `TOOLS_MANIFEST.md` | v87 | `3c29bec0bc9d` | ○ |
| `RELEASE.md` | v2.67 | — | 이 문서 |

### 발표 (11)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `claim_graph.py` | v16.10 | `47f516373f16` | ○ |
| `test_claim_graph.py` | v16.10 | `5817f71b4016` | ○ |
| `CLAIM_GRAPH.md` | v16.10 | `539acf8f59bc` | ○ |
| `deck_toolkit.py` | v16.47 | `8b1ab74de52c` | ○ |
| `test_toolkit.py` | v16.47 | `819595d18946` | ○ |
| `DECK_SPEC.md` | v16.47 | `61bbe8c12ef1` | ○ |
| `handoff.py` | v2.2 | `d8b5305111f4` | — |
| `test_handoff.py` | v2.2 | `7b2a11d55b3a` | — |
| `HANDOFF_FORMAT.md` | v2.2 | `92fb4a11e9bb` | — |
| `TOOLS_MANIFEST.md` | v87 | `3c29bec0bc9d` | ○ |
| `RELEASE.md` | v2.67 | — | 이 문서 |

### 리뷰어 (6)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `claim_graph.py` | v16.10 | `47f516373f16` | ○ |
| `test_claim_graph.py` | v16.10 | `5817f71b4016` | ○ |
| `CLAIM_GRAPH.md` | v16.10 | `539acf8f59bc` | ○ |
| `REVIEW_PROTOCOL.md` | v7.2 | `7f6e413d4d48` | — |
| `TOOLS_MANIFEST.md` | v87 | `3c29bec0bc9d` | ○ |
| `RELEASE.md` | v2.67 | — | 이 문서 |

### 교과서 (5)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `textbook.py` | v0.7.2 | `446049895c66` | — |
| `test_textbook.py` | v0.7.2 | `93d75911d86c` | — |
| `TEXTBOOK.md` | v0.7.2 | `4bfff4aa0771` | — |
| `TOOLS_MANIFEST.md` | v87 | `3c29bec0bc9d` | ○ |
| `RELEASE.md` | v2.67 | — | 이 문서 |

### 문헌 (5)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `literature.py` | v0.8.4 | `0585dbb787b0` | — |
| `test_literature.py` | v0.8.4 | `940eca6399e2` | — |
| `LITERATURE.md` | v0.8.4 | `e35c0d149938` | — |
| `TOOLS_MANIFEST.md` | v87 | `3c29bec0bc9d` | ○ |
| `RELEASE.md` | v2.67 | — | 이 문서 |

### 코드 (25)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `claim_graph.py` | v16.10 | `47f516373f16` | ○ |
| `test_claim_graph.py` | v16.10 | `5817f71b4016` | ○ |
| `CLAIM_GRAPH.md` | v16.10 | `539acf8f59bc` | ○ |
| `deck_toolkit.py` | v16.47 | `8b1ab74de52c` | ○ |
| `test_toolkit.py` | v16.47 | `819595d18946` | ○ |
| `DECK_SPEC.md` | v16.47 | `61bbe8c12ef1` | ○ |
| `verify_toolkit.py` | v1.3.7 | `0833539073f1` | — |
| `test_verify_toolkit.py` | v1.3.7 | `ac6e42ed2103` | — |
| `handoff.py` | v2.2 | `d8b5305111f4` | — |
| `test_handoff.py` | v2.2 | `7b2a11d55b3a` | — |
| `HANDOFF_FORMAT.md` | v2.2 | `92fb4a11e9bb` | — |
| `textbook.py` | v0.7.2 | `446049895c66` | — |
| `test_textbook.py` | v0.7.2 | `93d75911d86c` | — |
| `TEXTBOOK.md` | v0.7.2 | `4bfff4aa0771` | — |
| `literature.py` | v0.8.4 | `0585dbb787b0` | — |
| `test_literature.py` | v0.8.4 | `940eca6399e2` | — |
| `LITERATURE.md` | v0.8.4 | `e35c0d149938` | — |
| `REVIEW_PROTOCOL.md` | v7.2 | `7f6e413d4d48` | — |
| `TOOLS_MANIFEST.md` | v87 | `3c29bec0bc9d` | ○ |
| `CODE_PROJECT_README.md` | v5 | `cbffb6ca85db` | — |
| `HISTORY.md` | — | `bb3a9d7c7819` | ○ |
| `release.py` | — | `9edb619b0a0b` | ○ |
| `GITHUB_README.md` | — | `c81d29504e46` | — |
| `PRIVATE_TERMS.txt` | — | `6e8c2862cf5e` | — |
| `RELEASE.md` | v2.67 | — | 이 문서 |
<!-- sets:end -->

## 4. 각 프로젝트 대화창이 첫 세션에서 할 일

1. 모든 역할: selfcheck 로 manifest v87 이상.
2. 저자·발표·리뷰어: `mapfreeze … --sources <문헌 보관소>` 가 `[멈춤] [필수] 근거 문헌 N곳이 보관소에 없어` 로 멈추면, 적힌 근거를 sources 에서 빼 작업표(gaps)에 두거나 문헌 역할에 원문을 받아 달라고 한 뒤 다시 freeze 한다. 그 전에는 검증 기록이 생기지 않는다.
3. 발표(Mac 에서 도구를 돌리는 곳): `overflow` 끝에 `[참고] 덱 테마 글꼴 "…" 파일을 이 컴퓨터에서 찾지 못해` 가 나오면 그 판정은 근사 계산이다 — 글꼴을 설치하거나 `--font-path` 로 준다. 최종 기준은 전처럼 PowerPoint.

## 5. 검증하지 않은 것

- 이번 판은 Mac(macOS 26 · Python 3.12·3.10)에서 빌드했다. Linux 컨테이너에서는 돌리지 않았다 — 대신 Mac 에서 Linux 형식의 `fc-list` 출력(이 Mac 의 글꼴 371개)을 흉내 내 옛·새 색인이 같고 테스트가 그 길로도 통과함을 확인했다. 첫 Linux 환경(클라우드·Cowork)의 selfcheck `--tests` 결과로 확인한다.
- Mac 의 내려받기 글꼴(시스템 설정에서 받는 것, `/System/Library/AssetsV2` 아래)은 훑지 않는다. 테스트에서 `.otf` 는 이름 표 읽기만(가짜 OTTO 머리) 본다 — 실제 CFF 글꼴은 이 Mac 에서 손으로만 확인했다(시스템 `.otf` 38개·`.ttc` 128개 모두 색인에 들어가고, `.otf` 하나로 글자폭을 잼). Linux 컨테이너에 같은 글꼴이 있다는 보장이 없어 테스트에는 넣지 않았다.
- 실제 덱(Pretendard·맑은 고딕 테마)을 Mac 에서 돌린 적은 없다 — 그 글꼴이 이 Mac 에 없어 [참고] 한 줄이 나올 것으로 예상.
