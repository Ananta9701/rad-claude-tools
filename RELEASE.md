# RELEASE v2.16 — manifest v36 — 2026-09-26

> **v2.16 — apply-handoff 1단계: 넘김 문서 문법과 미리보기.** 발표 `260925_도구회신_apply-handoff_요청_v1` 의 1단계. 새 도구 `handoff.py`(v1.0)와 문법 `HANDOFF_FORMAT.md`(발표 세트·GitHub). 적용(2단계)·검증 보고서(3단계)는 다음 판. 이전 판 내용은 `HISTORY.md`.
> v2.15 확인: GitHub 저장소에서 받은 세트로 `selfcheck --role 발표 --tests --compare /mnt/project` → 통과·같음(코드 프로젝트가 업로드 직후 직접 확인).

## 1. 바뀐 것

**`HANDOFF_FORMAT.md` v1.0** — 넘김 문서 문법. 원칙: **도구는 문법에 없는 줄을 만나면 추측하지 않고 멈춘다**(D2 — 변형을 알아서 받다가 대본 첫 줄을 버린 사고). 넘김 16건(바이트 수·sha256 을 발표 표와 대조, 16/16 일치)에서 실제로 쓰인 모양을 정리했다.
- 머리: `기준: **{기준 덱}**(N화면)` 필수(기준 판 대조), `기준 sha256` 선택.
- 구역: `### 화면 N — 제목`, `### 새 슬라이드 — …`, `## 본문 수정` 표. 그 밖의 `##`·`---` 는 설명(도구가 읽지 않음).
- 화면 구역 안은 **예약어 블록만**: `작업:`·`대본:`·`참고:`·`복제본(문제) 대본:`·`제목:`·`본문:`·`문단 교체/추가/삭제`. 대본 안의 `CT: …`·`영상: …` 같은 줄은 예약어가 아니다(말뭉치 확인).
- `작업:` 은 닫힌 작업어 집합, ` · ` 로 여럿, ` — ` 뒤와 괄호 속은 설명(`앞에 복제(…)`·`새 슬라이드(…)` 괄호만 작업어의 일부).
- `대본:`·`참고:` 필수(`변경 없음`·`없음`·`(삭제 화면)`). 같은 줄에 쓴 글은 첫 줄로 받고 경고. `앞에 복제` 는 `복제본(문제) 대본:` 필수, 해설 상자 여부(`해설 상자 "…"` / `해설 상자 없음`)를 안 적으면 경고.
- 문단 키는 본문에서 정확히 한 번. 긴 줄을 `…` 로 줄여 적은 키(말뭉치 8건)는 `…` 를 "무엇이든" 으로 대조.

**`handoff.py check 넘김.md [--deck 기준.pptx] [--sha 16자]`** — 문법 검사 + 미리보기(판정·문제 표·화면별 작업 표·새 슬라이드·적용 순서). `--deck` 을 주면 기준 덱과 **화면 수·화면 제목**(판 착오 D11 을 적용 전에 잡음), 문단 키 수, 본문 수정 원문(한 조각 1회, 아니면 조각 전체로 다시)을 대조한다. `--sha` 는 넘김 문서 자체의 sha256. 오류가 하나라도 있으면 종료 코드 1.

**말뭉치 결과**(16건, 문법만): 14건 오류 0. 남은 것은 ① H&N v5 — 구 형식(참고 칸 없음) 78곳, ② H&N v7 화면 67 — `참고:` 빠짐 1곳(실제 누락). 경고: 앞에 복제에 해설 상자 여부 미기재 8곳(HBP v1·LGI v2·흉부1 — 규칙이 생기기 전 문서), 작업어를 문장으로 쓴 1곳(복부2).

**claim_graph·deck_toolkit** — 코드 변경 없음. deck_toolkit 16.21 은 DECK_SPEC 과 짝을 맞추려 판만 올렸다.

**DECK_SPEC 16.21** — §0-B: 넘김 문법은 `HANDOFF_FORMAT.md` 가 진본, 적용 전 `handoff.py check` 필수, 오류면 돌려보낸다. §8: 대화창·Cowork 역할(사용자 09-26) — 대화창은 판단·대조·회신, 무거운 파일 작업(넘김 적용·교과서 분할)은 Cowork 가 Mac 동기화 폴더에서.

## 2. 회신 항목별 답

| 항목 | 반영 |
|---|---|
| apply-handoff 1단계(문법·미리보기) | 이 판 |
| 넘김자료 16건 대조 | 바이트 수·sha256 16/16 일치(15건 대화 업로드 + HBP v2 는 Drive 에서 받아 대조) |
| Cowork 시험 결과 | 전달 규약 v2(§4 바이트 그대로 통로, §6 결과) — Drive 맨 위 |
| 역할 분담(발표 제안 3) | 사용자 결정 — DECK_SPEC §8 |

## 3. 프로젝트별 받을 파일

GitHub 로 받는다(세션 시작 한 줄 — `README.md`). 프로젝트 파일은 예비로 두고 `--compare /mnt/project` 결과가 "다름" 이면 받은 것을 쓴다.

<!-- sets:begin — release.py 가 만든다. 손으로 고치지 않는다 -->
### 저자 (7)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `claim_graph.py` | v15.7 | `be1559a3ace8` | — |
| `test_claim_graph.py` | v15.7 | `6946b6a49119` | — |
| `CLAIM_GRAPH.md` | v15.7 | `836652b84421` | — |
| `verify_toolkit.py` | v1.3.3 | `6683437604f9` | — |
| `test_verify_toolkit.py` | v1.3.3 | `ffd443ae7943` | — |
| `TOOLS_MANIFEST.md` | v36 | `e1cf649df172` | ○ |
| `RELEASE.md` | v2.16 | — | 이 문서 |

### 발표 (11)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `claim_graph.py` | v15.7 | `be1559a3ace8` | — |
| `test_claim_graph.py` | v15.7 | `6946b6a49119` | — |
| `CLAIM_GRAPH.md` | v15.7 | `836652b84421` | — |
| `deck_toolkit.py` | v16.21 | `f6314d3068bd` | ○ |
| `test_toolkit.py` | v16.21 | `7f0e7684556e` | ○ |
| `DECK_SPEC.md` | v16.21 | `22ec2cd7906e` | ○ |
| `handoff.py` | v1.0 | `ac46b281ca9d` | 신규 |
| `test_handoff.py` | v1.0 | `598d9fb30a95` | 신규 |
| `HANDOFF_FORMAT.md` | v1.0 | `9df63e3200f7` | 신규 |
| `TOOLS_MANIFEST.md` | v36 | `e1cf649df172` | ○ |
| `RELEASE.md` | v2.16 | — | 이 문서 |

### 리뷰어 (6)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `claim_graph.py` | v15.7 | `be1559a3ace8` | — |
| `test_claim_graph.py` | v15.7 | `6946b6a49119` | — |
| `CLAIM_GRAPH.md` | v15.7 | `836652b84421` | — |
| `REVIEW_PROTOCOL.md` | v7.2 | `7f6e413d4d48` | — |
| `TOOLS_MANIFEST.md` | v36 | `e1cf649df172` | ○ |
| `RELEASE.md` | v2.16 | — | 이 문서 |

### 코드 (19)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `claim_graph.py` | v15.7 | `be1559a3ace8` | — |
| `test_claim_graph.py` | v15.7 | `6946b6a49119` | — |
| `CLAIM_GRAPH.md` | v15.7 | `836652b84421` | — |
| `deck_toolkit.py` | v16.21 | `f6314d3068bd` | ○ |
| `test_toolkit.py` | v16.21 | `7f0e7684556e` | ○ |
| `DECK_SPEC.md` | v16.21 | `22ec2cd7906e` | ○ |
| `verify_toolkit.py` | v1.3.3 | `6683437604f9` | — |
| `test_verify_toolkit.py` | v1.3.3 | `ffd443ae7943` | — |
| `handoff.py` | v1.0 | `ac46b281ca9d` | 신규 |
| `test_handoff.py` | v1.0 | `598d9fb30a95` | 신규 |
| `HANDOFF_FORMAT.md` | v1.0 | `9df63e3200f7` | 신규 |
| `REVIEW_PROTOCOL.md` | v7.2 | `7f6e413d4d48` | — |
| `TOOLS_MANIFEST.md` | v36 | `e1cf649df172` | ○ |
| `CODE_PROJECT_README.md` | v4 | `0f2f45890804` | — |
| `HISTORY.md` | — | `5aacc49d52f2` | ○ |
| `release.py` | — | `7ad307268638` | ○ |
| `GITHUB_README.md` | — | `2e2886c5a453` | ○ |
| `PRIVATE_TERMS.txt` | — | `4285e1f439fb` | — |
| `RELEASE.md` | v2.16 | — | 이 문서 |
<!-- sets:end -->

## 4. 각 프로젝트 대화창이 첫 세션에서 할 일

1. GitHub 한 줄(`--role` 역할에 맞게) — 표를 수령 회신 §1 에. `--compare /mnt/project` 는 "다름"(프로젝트 파일이 v2.15)이 정상 — 이번 판부터 프로젝트 파일은 갱신하지 않아도 된다.
2. 발표: 다음 넘김부터 적용 전에 `handoff.py check 넘김.md --deck 기준.pptx --sha …`. 지금까지의 넘김 16건 중 원하는 것으로 한 번 돌려 보고 결과를 회신에(기준 덱이 발표 쪽에만 있다).
3. 영상의학: `HANDOFF_FORMAT.md` 를 GitHub 에서 읽어 다음 넘김부터 따른다(코드가 따로 알림).
4. 저자·리뷰어: 도구 변경 없음.

## 5. 검증하지 않은 것

기준 덱 대조(`--deck`)는 fixture 덱으로만 시험했다 — 실제 기준 덱(H&N·LGI 등)은 발표 쪽에 있다(§4-2).
