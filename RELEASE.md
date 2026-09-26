# RELEASE v2.17 — manifest v37 — 2026-09-26

> **v2.17** — 발표 회신 세 건(`handoff1단계_실물점검`, `Cowork_GitHub받기`, `Cowork클라우드_GitHub`)과 리뷰어 수령 확인 처리. 작은 판: handoff 1.1 · claim_graph 15.8 · 세션 시작 한 줄을 `git clone` 으로. 이전 판 내용은 `HISTORY.md`.
> v2.16 확인: 발표가 실제 기준 덱으로 16건을 돌려 14건 적용 가능·2건 멈춤(구 형식, 참고 누락 — 문법만 돌린 결과와 같고 기준 덱 대조로 새 오류 0). 틀린 판 덱 시험 6가지 중 5가지를 잡음. 리뷰어: GitHub 세트로 수용 검사 7항목 이전과 같음.

## 1. 바뀐 것

**handoff 1.1**
- **노트만 다른 판**(H&N v13 을 한 판 앞 v11 에 적용 — v12 의 화면 84 대본 수정이 조용히 사라지는 경우)은 화면 수·제목·문단 키로 구별되지 않는다(발표 시험). 머리의 `기준 sha256` 이 이것을 잡는 유일한 방법이라 **흐름으로 채운다**: 발표는 적용 회신마다 결과 pptx 의 sha256 앞 16자를 적고, 영상의학은 다음 넘김 머리에 옮긴다(DECK_SPEC §0-B, HANDOFF_FORMAT §1). `기준 sha256` 이 있고 다르면 오류 — 메시지는 "다른 판이거나 사용자가 고쳐 저장했는지 확인". 없으면 미리보기 끝에 한 줄 안내.
- 참고의 **`[메모 수정 요청]`** 을 화면별 작업 표에 "메모 수정 요청 N" 으로 드러낸다(요청서 3-4 — 원작자 메모 수정은 기본 멈춤).
- 적용 순서에 **원작자 메모 수정을 노트 쓰기 전에** 넣었다(D8 — 새 참고에 같은 문구가 있으면 2회 매치).
- D5·D7·D9(줄 앞 공백·탭·굵게)는 1단계 경고가 아니라 2단계(적용·`keep_format`) 시험 사례로 둔다 — 발표 판단과 같다.

**claim_graph 15.8** — `git clone` 으로 받은 폴더면 selfcheck 표에 **받은 커밋 해시**를 적는다. `.git` 은 세트 밖 파일로 잡지 않는다.

**세션 시작 한 줄 → `git clone --depth 1`** (발표 제안) — Cowork **클라우드 작업공간**이 tarball 주소(`codeload…`)를 세션 권한 문제로 막고(남의 공개 저장소도 403), `git clone` 과 raw 는 통과. 대화창·클라우드·Mac VM 셸에서 같은 한 줄을 쓴다. README·DECK_SPEC §8.

**DECK_SPEC 16.22** — 세션 시작 한 줄, Drive 동기화 폴더 등에 툴킷 사본을 두지 않는다(`Cowork 시험` 폴더의 v34 사본 — 발표 안내로 사용자가 지움), 적용 회신에 결과 sha256. deck_toolkit 은 판만 올림.

## 2. 회신 항목별 답

| 항목 | 반영 |
|---|---|
| 노트만 다른 판(D11 못 잡은 2건) | 기준 sha256 흐름 — 발표 적용 회신 → 영상의학 다음 넘김 머리 → check 오류 |
| `[메모 수정 요청]` 미리보기 | 반영 |
| 메모 수정을 노트 쓰기 전에 | 적용 순서에 반영(2단계에서 구현) |
| D5·D7·D9 | 2단계 시험 사례 |
| 공개 저장소의 `Case No.752/758/982` | 그대로 둔다 — 과 퀴즈 번호, 환자 식별 정보 아님(발표 판단과 같음) |
| Cowork GitHub 받기 | VM 셸 됨, 클라우드는 git clone 으로 — 한 줄을 git clone 으로 |
| 리뷰어 수령 확인 | 확인 |

## 3. 프로젝트별 받을 파일

GitHub 로 받는다 — 이번 판부터 **새 한 줄(`git clone`)**, `README.md`.

<!-- sets:begin — release.py 가 만든다. 손으로 고치지 않는다 -->
### 저자 (7)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `claim_graph.py` | v15.8 | `07f372d3ee2b` | ○ |
| `test_claim_graph.py` | v15.8 | `e3e905e90df3` | ○ |
| `CLAIM_GRAPH.md` | v15.8 | `54641dae9902` | ○ |
| `verify_toolkit.py` | v1.3.3 | `6683437604f9` | — |
| `test_verify_toolkit.py` | v1.3.3 | `ffd443ae7943` | — |
| `TOOLS_MANIFEST.md` | v37 | `7f76c1638306` | ○ |
| `RELEASE.md` | v2.17 | — | 이 문서 |

### 발표 (11)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `claim_graph.py` | v15.8 | `07f372d3ee2b` | ○ |
| `test_claim_graph.py` | v15.8 | `e3e905e90df3` | ○ |
| `CLAIM_GRAPH.md` | v15.8 | `54641dae9902` | ○ |
| `deck_toolkit.py` | v16.22 | `10bd522ad6b8` | ○ |
| `test_toolkit.py` | v16.22 | `f49bddc6e08d` | ○ |
| `DECK_SPEC.md` | v16.22 | `d30257e3a5c7` | ○ |
| `handoff.py` | v1.1 | `d86e4a07f64d` | ○ |
| `test_handoff.py` | v1.1 | `d80aba1b8799` | ○ |
| `HANDOFF_FORMAT.md` | v1.1 | `b7ae9c4d6043` | ○ |
| `TOOLS_MANIFEST.md` | v37 | `7f76c1638306` | ○ |
| `RELEASE.md` | v2.17 | — | 이 문서 |

### 리뷰어 (6)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `claim_graph.py` | v15.8 | `07f372d3ee2b` | ○ |
| `test_claim_graph.py` | v15.8 | `e3e905e90df3` | ○ |
| `CLAIM_GRAPH.md` | v15.8 | `54641dae9902` | ○ |
| `REVIEW_PROTOCOL.md` | v7.2 | `7f6e413d4d48` | — |
| `TOOLS_MANIFEST.md` | v37 | `7f76c1638306` | ○ |
| `RELEASE.md` | v2.17 | — | 이 문서 |

### 코드 (19)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `claim_graph.py` | v15.8 | `07f372d3ee2b` | ○ |
| `test_claim_graph.py` | v15.8 | `e3e905e90df3` | ○ |
| `CLAIM_GRAPH.md` | v15.8 | `54641dae9902` | ○ |
| `deck_toolkit.py` | v16.22 | `10bd522ad6b8` | ○ |
| `test_toolkit.py` | v16.22 | `f49bddc6e08d` | ○ |
| `DECK_SPEC.md` | v16.22 | `d30257e3a5c7` | ○ |
| `verify_toolkit.py` | v1.3.3 | `6683437604f9` | — |
| `test_verify_toolkit.py` | v1.3.3 | `ffd443ae7943` | — |
| `handoff.py` | v1.1 | `d86e4a07f64d` | ○ |
| `test_handoff.py` | v1.1 | `d80aba1b8799` | ○ |
| `HANDOFF_FORMAT.md` | v1.1 | `b7ae9c4d6043` | ○ |
| `REVIEW_PROTOCOL.md` | v7.2 | `7f6e413d4d48` | — |
| `TOOLS_MANIFEST.md` | v37 | `7f76c1638306` | ○ |
| `CODE_PROJECT_README.md` | v4 | `0f2f45890804` | — |
| `HISTORY.md` | — | `d8014880a95e` | ○ |
| `release.py` | — | `7ad307268638` | — |
| `GITHUB_README.md` | — | `60aa56dc93ea` | ○ |
| `PRIVATE_TERMS.txt` | — | `4285e1f439fb` | — |
| `RELEASE.md` | v2.17 | — | 이 문서 |
<!-- sets:end -->

## 4. 각 프로젝트 대화창이 첫 세션에서 할 일

1. 새 한 줄(`README.md`)로 받아 selfcheck — 표에 "받은 커밋" 줄이 있어야 한다. 표를 수령 회신 §1 에.
2. 발표: 다음 적용 회신부터 결과 pptx 의 sha256 앞 16자를 적는다.
3. 영상의학: 다음 넘김 머리에 `> 기준 sha256: \`…\``(발표가 적어 준 값) — 코드가 따로 알림.
4. 저자·리뷰어: 도구 변경 없음(claim_graph 15.8 은 selfcheck 표 한 줄 추가뿐).

## 5. 검증하지 않은 것

Mac VM 셸에서 `git clone`(tarball 은 됐다). Cowork 클라우드에서 selfcheck 끝까지.
