# RELEASE v2.18 — manifest v38 — 2026-09-26

> **v2.18** — 발표 회신 세 건(`v2.17수령`, `조사규칙_B1철회`, `Cowork_gitclone`) 처리 + 코드 프로젝트도 GitHub 에서 받기. 이전 판 내용은 `HISTORY.md`.
> v2.17 확인: 발표가 git clone 한 줄로 받아 통과(받은 커밋 `73831b8`), 기준 sha256 흐름이 노트만 다른 판(H&N v13 ← v11)을 잡음, 메모 수정 요청 표시. Cowork 클라우드·Mac 셸도 git clone 으로 통과 — 세 곳(발표 대화창·클라우드·Mac 셸) 출력이 같다.

## 1. 바뀐 것

- **치환 흔적 lint 에서 '영어 + 다' 를 잡지 않는다** (deck 16.23) — 사용자 결정(09-26): 영어 낱말 뒤 조사는 **한국어로 읽은 소리**를 기준으로 한다(`segment다` = 세그먼트다, 맞음). 철자로는 읽은 소리의 받침을 알 수 없으므로 v2.14 의 B1 규칙(모음 글자 뒤만 통과)을 철회한다 — 발표 제안이었고 발표가 철회했다. 이 규칙이 맞게 잡은 사례는 0건. 한글 명사가 붙은 오염(`Wirsung관`)은 계속 잡는다. DECK_SPEC §6 에 사용자 규칙 한 줄.
- **테스트 출력에 '건너뜀' 칸 통일** — `test_claim_graph`·`test_verify_toolkit`·`test_handoff` 도 `통과 N / 건너뜀 0 / 실패 0`(발표 요청 — 표만 보고 판정). 판만 올림: claim_graph 15.8.1 · verify_toolkit 1.3.4 · handoff 1.1.1.
- **코드 프로젝트도 공개 도구를 GitHub 에서 받는다**(사용자 질문 09-26) — 프로젝트 파일에는 코드 전용 5개(HISTORY·PRIVATE_TERMS·CODE_PROJECT_README·release.py·GITHUB_README)만. 세션 시작 명령은 `CODE_PROJECT_README.md` 첫머리. `release.py check` 가 HISTORY 맨 위 릴리스와 GitHub manifest 릴리스를 대조해, 사용자가 한쪽을 안 올렸으면 알린다.
- **zip 을 올릴 것만** — 프로젝트별 zip 을 없애고 `GitHub`·`코드전용` 두 개만, 파일을 zip 맨 위에 둬 풀면 "전부 선택 → 끌어다 놓기" 가 되게(사용자 09-26 — 골라 넣지 않게).
- **HISTORY 결함 복구** — 위 대조를 넣자 드러났다: release.py 가 §3 접수 기록의 "반영 판" 칸(`| v2.12 |`)을 보고 §1 요지 줄이 이미 있다고 착각해, **v2.5–v2.17 의 요지 12줄을 넣지 않았다.** 빌드 요약 문구로 되살렸고, 찾는 범위를 §1 표로 좁혔다.

## 2. 회신 항목별 답

| 항목 | 반영 |
|---|---|
| v2.17 수령(발표) | 확인 — sha 흐름·메모 수정 요청 실물 통과 |
| B1 철회 · '영어+다' 규칙 빼기 | 반영(deck 16.23) + DECK_SPEC §6 사용자 규칙 |
| selfcheck 테스트 표 건너뜀 칸 | 반영(테스트 셋 출력) |
| Cowork git clone | 확인 — 통보 v2 §6 "아직 모르는 것" 닫힘(다음 공통 통보·지침 문안에 반영) |

## 3. 프로젝트별 받을 파일

사용자에게 주는 것은 zip 두 개(풀면 파일이 바로 나온다): `v2.18_GitHub.zip`(15개 → GitHub 에 전부), `v2.18_코드전용.zip`(5개 → 코드 프로젝트 파일을 전부 지우고 전부). 세 프로젝트는 GitHub(`git clone` 한 줄)로 받는다 — 아래 표는 대조용.

<!-- sets:begin — release.py 가 만든다. 손으로 고치지 않는다 -->
### 저자 (7)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `claim_graph.py` | v15.8.1 | `dc3ac0780b61` | ○ |
| `test_claim_graph.py` | v15.8.1 | `bcfe1c1e42d6` | ○ |
| `CLAIM_GRAPH.md` | v15.8.1 | `ca0bd5652f32` | ○ |
| `verify_toolkit.py` | v1.3.4 | `e703af6d5418` | ○ |
| `test_verify_toolkit.py` | v1.3.4 | `aba65de39d87` | ○ |
| `TOOLS_MANIFEST.md` | v38 | `7ea24f878e73` | ○ |
| `RELEASE.md` | v2.18 | — | 이 문서 |

### 발표 (11)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `claim_graph.py` | v15.8.1 | `dc3ac0780b61` | ○ |
| `test_claim_graph.py` | v15.8.1 | `bcfe1c1e42d6` | ○ |
| `CLAIM_GRAPH.md` | v15.8.1 | `ca0bd5652f32` | ○ |
| `deck_toolkit.py` | v16.23 | `3806458d8fb5` | ○ |
| `test_toolkit.py` | v16.23 | `e01154831325` | ○ |
| `DECK_SPEC.md` | v16.23 | `623b710d8b1a` | ○ |
| `handoff.py` | v1.1.1 | `651155810001` | ○ |
| `test_handoff.py` | v1.1.1 | `158fa13253c9` | ○ |
| `HANDOFF_FORMAT.md` | v1.1.1 | `0d806320abb9` | ○ |
| `TOOLS_MANIFEST.md` | v38 | `7ea24f878e73` | ○ |
| `RELEASE.md` | v2.18 | — | 이 문서 |

### 리뷰어 (6)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `claim_graph.py` | v15.8.1 | `dc3ac0780b61` | ○ |
| `test_claim_graph.py` | v15.8.1 | `bcfe1c1e42d6` | ○ |
| `CLAIM_GRAPH.md` | v15.8.1 | `ca0bd5652f32` | ○ |
| `REVIEW_PROTOCOL.md` | v7.2 | `7f6e413d4d48` | — |
| `TOOLS_MANIFEST.md` | v38 | `7ea24f878e73` | ○ |
| `RELEASE.md` | v2.18 | — | 이 문서 |

### 코드 (19)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `claim_graph.py` | v15.8.1 | `dc3ac0780b61` | ○ |
| `test_claim_graph.py` | v15.8.1 | `bcfe1c1e42d6` | ○ |
| `CLAIM_GRAPH.md` | v15.8.1 | `ca0bd5652f32` | ○ |
| `deck_toolkit.py` | v16.23 | `3806458d8fb5` | ○ |
| `test_toolkit.py` | v16.23 | `e01154831325` | ○ |
| `DECK_SPEC.md` | v16.23 | `623b710d8b1a` | ○ |
| `verify_toolkit.py` | v1.3.4 | `e703af6d5418` | ○ |
| `test_verify_toolkit.py` | v1.3.4 | `aba65de39d87` | ○ |
| `handoff.py` | v1.1.1 | `651155810001` | ○ |
| `test_handoff.py` | v1.1.1 | `158fa13253c9` | ○ |
| `HANDOFF_FORMAT.md` | v1.1.1 | `0d806320abb9` | ○ |
| `REVIEW_PROTOCOL.md` | v7.2 | `7f6e413d4d48` | — |
| `TOOLS_MANIFEST.md` | v38 | `7ea24f878e73` | ○ |
| `CODE_PROJECT_README.md` | v5 | `1a446a99c379` | ○ |
| `HISTORY.md` | — | `1be7c964eb89` | ○ |
| `release.py` | — | `8ce7a3ea9b82` | ○ |
| `GITHUB_README.md` | — | `60aa56dc93ea` | — |
| `PRIVATE_TERMS.txt` | — | `4285e1f439fb` | — |
| `RELEASE.md` | v2.18 | — | 이 문서 |
<!-- sets:end -->

## 4. 각 프로젝트 대화창이 첫 세션에서 할 일

1. git clone 한 줄로 받아 selfcheck — 테스트 표 세 줄 모두 "건너뜀 0".
2. 발표: 흉부1 v2 lint 에서 `segment다`·`point다` 가 사라지는지.
3. 저자·리뷰어: 도구 동작 변경 없음.

## 5. 검증하지 않은 것

없음.
