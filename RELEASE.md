# RELEASE v2.15 — manifest v35 — 2026-09-26

> **v2.15 — 첫 GitHub 릴리스.** 도구를 공개 저장소 `github.com/Ananta9701/rad-claude-tools` 하나에 두고, 각 대화창이 세션 시작 때 직접 받는다(발표 `260926_도구회신_전달체계_Drive_GitHub_v1` §3, 사용자 결정 09-26). 이번 판은 전환 판이라 프로젝트별 세트도 지금처럼 함께 낸다. 이전 판 내용은 `HISTORY.md`(코드 프로젝트에만).

## 1. 바뀐 것

**GitHub 배포**
- 저장소 하나에 저자·발표·리뷰어 세트의 합(11개) + `README.md`. 역할별로 나누지 않는다 — 각 대화창은 전부 받아(1 MB 안팎) 자기 역할 파일만 쓴다.
- 세션 시작 한 줄(`README.md` 에도 있음):
  ```
  rm -rf /tmp/rct && mkdir -p /tmp/rct && curl -sL https://codeload.github.com/Ananta9701/rad-claude-tools/tar.gz/refs/heads/main | tar xz -C /tmp/rct --strip-components=1 && python3 /tmp/rct/claim_graph.py selfcheck --dir /tmp/rct --role 발표 --tests --compare /mnt/project
  ```
  `--role` 은 `발표`·`저자`·`리뷰어`. 이후 도구는 `/tmp/rct` 에서.
- **claim_graph 15.7** — `selfcheck --role`: 전체 세트에서 프로젝트를 추정하지 않고 그 역할로 본다(안 쓰는 도구는 삭제 후보가 아님). `--compare DIR`: 예비로 둔 프로젝트 파일과 manifest 판·해시를 대조해 "같음 / 다름 — 받은 것을 쓴다".
- **공개 전 개인정보·연구 내용 정리** — 공개 저장소는 프로필을 비공개로 해도 누구나 볼 수 있으므로:
  - DECK_SPEC 머리의 사용자 이름·소속 기관 줄, 예시 나이/성별(`NN/F` 로) 삭제
  - 테스트·규약 예시에 쓰인 원고 주제어·수치·주장 id·파일 이름을 가짜로 바꿈(병변 지표 X, `DOC_v47`, `{원고}_v{N}` 등). REVIEW_PROTOCOL 의 파일 이름 예시는 `{원고}_v{N}_claims.json` 꼴로(뜻은 같음)
  - 학회 이름을 '학회' 로
  - 도구 동작은 바뀌지 않았다(테스트 전부 통과). 판: deck_toolkit 16.20 · verify_toolkit 1.3.3 · REVIEW_PROTOCOL v7.2 · CLAIM_GRAPH 15.7
- **release.py** — 공개 세트(`v2.15_GitHub.zip`)를 만들며 코드 전용 `PRIVATE_TERMS.txt`(사람·기관 이름, 연구 주제어)와 나이/성별·이메일 모양을 찾아 하나라도 있으면 빌드를 멈춘다. 역할 3개로 공개 세트를 selfcheck 한다. 코드 전용 파일(HISTORY·CODE_PROJECT_README·release.py·PRIVATE_TERMS·GITHUB_README)은 올리지 않는다.
- 테스트 fixture(원고 모양 docx)를 매번 새로 만든다 — 지난 실행의 캐시가 남아 fixture 를 고쳐도 옛 내용으로 돌던 것.

**DECK_SPEC 16.20 (§8)** — 사용자 규칙 두 줄: 반복되는 문제는 작업규약과 코드로 옮긴다(09-25), 프로젝트 사이 md 는 Drive `Claude 전달함` 으로(09-26). 세션 시작은 GitHub 에서.

## 2. 회신 항목별 답

| 항목 | 반영 |
|---|---|
| 전달체계 §2 Drive 규약 | 공통 통보(`Claude 전달함` 맨 위)로 확정, DECK_SPEC §8 |
| 전달체계 §3 GitHub | 이 판 — 한 저장소, `--role`, 세션 시작 한 줄, 공개 전 정리 |
| 전달체계 §6·apply-handoff §5 규칙 | DECK_SPEC §8 두 줄 |
| apply-handoff | 채택, 세 단계 — 다음 판부터(넘김 문서 14건 수령 대기) |

## 3. 프로젝트별 받을 파일 — 이번이 마지막 손 배포 (전부 삭제 → 전부 재업로드)

<!-- sets:begin — release.py 가 만든다. 손으로 고치지 않는다 -->
### 저자 (7)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `claim_graph.py` | v15.7 | `be1559a3ace8` | ○ |
| `test_claim_graph.py` | v15.7 | `6946b6a49119` | ○ |
| `CLAIM_GRAPH.md` | v15.7 | `836652b84421` | ○ |
| `verify_toolkit.py` | v1.3.3 | `6683437604f9` | ○ |
| `test_verify_toolkit.py` | v1.3.3 | `ffd443ae7943` | ○ |
| `TOOLS_MANIFEST.md` | v35 | `00e98d8b71f1` | ○ |
| `RELEASE.md` | v2.15 | — | 이 문서 |

### 발표 (8)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `claim_graph.py` | v15.7 | `be1559a3ace8` | ○ |
| `test_claim_graph.py` | v15.7 | `6946b6a49119` | ○ |
| `CLAIM_GRAPH.md` | v15.7 | `836652b84421` | ○ |
| `deck_toolkit.py` | v16.20 | `58d415b5f386` | ○ |
| `test_toolkit.py` | v16.20 | `37733a678996` | ○ |
| `DECK_SPEC.md` | v16.20 | `2ff161dce2a9` | ○ |
| `TOOLS_MANIFEST.md` | v35 | `00e98d8b71f1` | ○ |
| `RELEASE.md` | v2.15 | — | 이 문서 |

### 리뷰어 (6)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `claim_graph.py` | v15.7 | `be1559a3ace8` | ○ |
| `test_claim_graph.py` | v15.7 | `6946b6a49119` | ○ |
| `CLAIM_GRAPH.md` | v15.7 | `836652b84421` | ○ |
| `REVIEW_PROTOCOL.md` | v7.2 | `7f6e413d4d48` | ○ |
| `TOOLS_MANIFEST.md` | v35 | `00e98d8b71f1` | ○ |
| `RELEASE.md` | v2.15 | — | 이 문서 |

### 코드 (16)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `claim_graph.py` | v15.7 | `be1559a3ace8` | ○ |
| `test_claim_graph.py` | v15.7 | `6946b6a49119` | ○ |
| `CLAIM_GRAPH.md` | v15.7 | `836652b84421` | ○ |
| `deck_toolkit.py` | v16.20 | `58d415b5f386` | ○ |
| `test_toolkit.py` | v16.20 | `37733a678996` | ○ |
| `DECK_SPEC.md` | v16.20 | `2ff161dce2a9` | ○ |
| `verify_toolkit.py` | v1.3.3 | `6683437604f9` | ○ |
| `test_verify_toolkit.py` | v1.3.3 | `ffd443ae7943` | ○ |
| `REVIEW_PROTOCOL.md` | v7.2 | `7f6e413d4d48` | ○ |
| `TOOLS_MANIFEST.md` | v35 | `00e98d8b71f1` | ○ |
| `CODE_PROJECT_README.md` | v4 | `0f2f45890804` | ○ |
| `HISTORY.md` | — | `d3d83a97996a` | ○ |
| `release.py` | — | `f2e41ea81fed` | ○ |
| `GITHUB_README.md` | — | `c8f5dfa53ca1` | 신규 |
| `PRIVATE_TERMS.txt` | — | `4285e1f439fb` | 신규 |
| `RELEASE.md` | v2.15 | — | 이 문서 |
<!-- sets:end -->

## 4. 각 프로젝트 대화창이 첫 세션에서 할 일

1. 이번에는 지금처럼 세트를 교체하고 `python3 claim_graph.py selfcheck --dir /mnt/project --tests` (판 15.7 이 떠야 한다).
2. 이어서 GitHub 한 줄(위 §1)을 역할에 맞게 돌린다 — `--compare /mnt/project` 결과가 **같음** 이어야 한다. 표 두 개를 수령 회신 §1 에.
3. 다음 판부터는 GitHub 한 줄만 돌린다. 프로젝트 파일의 도구는 한두 판 동안 예비로 두고, `--compare` 가 계속 같으면 사용자가 지운다.
4. 각 프로젝트 지침의 세션 시작 절차를 GitHub 한 줄로 바꾸는 문안은 코드 프로젝트가 따로 드린다.

## 5. 검증하지 않은 것

GitHub 에서 받는 명령은 사용자가 저장소에 첫 업로드를 한 뒤에야 확인된다(지금 저장소는 비어 있다) — 코드 프로젝트가 업로드 직후 같은 명령으로 받아 selfcheck 를 돌려 확인한다.
