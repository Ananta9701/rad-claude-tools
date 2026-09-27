# RELEASE v2.28 — manifest v48 — 2026-09-27

> **v2.28** — 발표 근골격 첫 실전 병합 회신(P1–P4)과 Google Slides 서식 회신(K7). `handoff.py` 1.9, `deck_toolkit.py` 16.27. K8(가져옴 제목 띠)은 자료를 받은 뒤. claim_graph·verify·textbook 은 그대로. 이전 판 내용은 `HISTORY.md`.
> 사용자 결정(09-27): P1 은 **기본 멈춤**, 옵션으로 감싸기·덮기.

## 1. 바뀐 것

| 도구 | 판 | 내용 |
|---|---|---|
| `handoff.py` | 1.9 | **P1** 원작자 노트뿐인 기준 덱(3부 구조가 어디에도 없음)에 `대본:` 을 쓰면 check 오류·apply 멈춤. `--protect-memo`(적용 전에 표지 없는 노트를 기존 메모 구역으로 감쌈 — 근골격 v3 에서 발표가 손 스크립트로 한 것) · `--notes-are-scripts`(덮어쓰기). 3부 구조가 있는 덱의 표지 없는 노트는 대본만 쓴 우리 노트로 보고 경고. 경고 문구의 "normalize-notes 된 판이면 정상" 을 고침(틀렸다). **P3** 보고서 원작자 메모 줄을 수로 — 메모 구역이 있던 기준 화면·메모 문단 수 그대로, 감싼 화면 k/n 원래 노트 그대로, 표지 없는 노트를 덮은 화면 수. 슬라이드 파일 번호로 짝지음(병합에서도). **P4** 가져옴 줄에 넘침 [심각] 원천 → 결과(늘면 "가져오며 생김") |
| `test_handoff.py` | 1.9 | 25개(+1): 원작자 노트 덱 멈춤·protect(원래 노트가 메모로)·scripts(덮은 수), CLI check 기본 멈춤, 병합 시험에 넘침 비교. 원작자 노트 fixture 로 대본을 쓰던 시험은 `notes_mode='scripts'` |
| `HANDOFF_FORMAT.md` | 1.9 | v1.9 한 문단 |
| `deck_toolkit.py` | 16.27 | **P2** CLI `protect-memo [--screens]`. **K7** `fit_corner_boxes`·CLI `fit-corner-boxes` — 가장자리에 붙은 채우기·테두리 없는 글상자를 붙은 쪽 고정으로 글에 맞게 키움(테마 본문 글꼴로 폭을 잼, pad 15%), 반대쪽 자리가 없으면 건너뛰고 새로 겹치는 상자는 알림. **작은 것** 제목을 띠에 맞추려 줄이는 하한 16 → 24pt(lint 제목 최소와 같게 — 23pt 로 줄여 부딪침) |
| `test_toolkit.py` | 16.27 | 172개(+1): 구석 상자(오른쪽·아래 고정·겹침 알림·가운데/채운 상자 제외), protect-memo CLI, 하한 24. 기존 제목 맞춤 시험은 새 하한으로(24pt 밑이면 [!]) |
| `DECK_SPEC.md` | 16.27 | §0-B 기준 덱은 원작자 노트를 감싼 판(normalize-notes 는 감싸지 않음), 사용자 결정 3줄(Google Slides 검토·밖에 둔 상자 그대로·서식 보정은 발표가 따로), 판 기록 |

## 2. 회신 항목별 답

| 항목 | 반영 |
|---|---|
| 발표 `260927_도구회신_근골격병합적용_v1` P1 | handoff 1.9 — 기본 멈춤(사용자 결정), `--protect-memo`·`--notes-are-scripts` |
| P2 | deck 16.27 `protect-memo` |
| P3 | handoff 1.9 — apply 보고서에서(파일 번호로 짝지음). `diff --by-file` 은 만들지 않았다 — 보고서가 같은 일을 한다 |
| P4 | handoff 1.9 |
| 작은 것 ① 내용 해시 식 | 도구 변경 없음 — `handoff.content_hash()` 하나(발표가 그렇게 정함) |
| 작은 것 ② 제목 23pt | deck 16.27 — 하한 24pt |
| 발표 `260927_도구회신_근골격_구글슬라이드서식_v1` K7 | deck 16.27 `fit-corner-boxes` |
| K8 가져옴 제목 띠 0.66" | **이번 판에 넣지 않음** — 재현에 그 덱의 제목 규격 값이 필요하다. `to발표` 에 요청(`titles` 출력). 추정(확인 안 됨): 규격이 1줄로 판정했지만 Google Slides 는 다른 글꼴로 넓게 그려 2줄이 되고, spAutoFit 을 따르지 않아 띠를 키우지 않는다 |
| DECK_SPEC §0 추가안 3줄 | DECK_SPEC 16.27 |

## 3. 받을 파일

zip 두 개: `v2.28_GitHub.zip`(GitHub 에 전부), `v2.28_코드전용.zip`(코드 프로젝트 파일을 전부 지우고 5개).

<!-- sets:begin — release.py 가 만든다. 손으로 고치지 않는다 -->
### 저자 (7)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `claim_graph.py` | v15.8.1 | `dc3ac0780b61` | — |
| `test_claim_graph.py` | v15.8.1 | `bcfe1c1e42d6` | — |
| `CLAIM_GRAPH.md` | v15.8.1 | `ca0bd5652f32` | — |
| `verify_toolkit.py` | v1.3.4 | `e703af6d5418` | — |
| `test_verify_toolkit.py` | v1.3.4 | `aba65de39d87` | — |
| `TOOLS_MANIFEST.md` | v48 | `54b99bf88ca6` | ○ |
| `RELEASE.md` | v2.28 | — | 이 문서 |

### 발표 (11)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `claim_graph.py` | v15.8.1 | `dc3ac0780b61` | — |
| `test_claim_graph.py` | v15.8.1 | `bcfe1c1e42d6` | — |
| `CLAIM_GRAPH.md` | v15.8.1 | `ca0bd5652f32` | — |
| `deck_toolkit.py` | v16.27 | `fa4d7c520938` | ○ |
| `test_toolkit.py` | v16.27 | `459011607cb3` | ○ |
| `DECK_SPEC.md` | v16.27 | `aa1858df7dca` | ○ |
| `handoff.py` | v1.9 | `36df9ec98b79` | ○ |
| `test_handoff.py` | v1.9 | `bc5c482ccb99` | ○ |
| `HANDOFF_FORMAT.md` | v1.9 | `a0e89ec847a8` | ○ |
| `TOOLS_MANIFEST.md` | v48 | `54b99bf88ca6` | ○ |
| `RELEASE.md` | v2.28 | — | 이 문서 |

### 리뷰어 (6)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `claim_graph.py` | v15.8.1 | `dc3ac0780b61` | — |
| `test_claim_graph.py` | v15.8.1 | `bcfe1c1e42d6` | — |
| `CLAIM_GRAPH.md` | v15.8.1 | `ca0bd5652f32` | — |
| `REVIEW_PROTOCOL.md` | v7.2 | `7f6e413d4d48` | — |
| `TOOLS_MANIFEST.md` | v48 | `54b99bf88ca6` | ○ |
| `RELEASE.md` | v2.28 | — | 이 문서 |

### 교과서 (5)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `textbook.py` | v0.5 | `5f916620c6c0` | — |
| `test_textbook.py` | v0.5 | `4b2da8dfcecb` | — |
| `TEXTBOOK.md` | v0.5 | `d441d67eea3e` | — |
| `TOOLS_MANIFEST.md` | v48 | `54b99bf88ca6` | ○ |
| `RELEASE.md` | v2.28 | — | 이 문서 |

### 코드 (22)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `claim_graph.py` | v15.8.1 | `dc3ac0780b61` | — |
| `test_claim_graph.py` | v15.8.1 | `bcfe1c1e42d6` | — |
| `CLAIM_GRAPH.md` | v15.8.1 | `ca0bd5652f32` | — |
| `deck_toolkit.py` | v16.27 | `fa4d7c520938` | ○ |
| `test_toolkit.py` | v16.27 | `459011607cb3` | ○ |
| `DECK_SPEC.md` | v16.27 | `aa1858df7dca` | ○ |
| `verify_toolkit.py` | v1.3.4 | `e703af6d5418` | — |
| `test_verify_toolkit.py` | v1.3.4 | `aba65de39d87` | — |
| `handoff.py` | v1.9 | `36df9ec98b79` | ○ |
| `test_handoff.py` | v1.9 | `bc5c482ccb99` | ○ |
| `HANDOFF_FORMAT.md` | v1.9 | `a0e89ec847a8` | ○ |
| `textbook.py` | v0.5 | `5f916620c6c0` | — |
| `test_textbook.py` | v0.5 | `4b2da8dfcecb` | — |
| `TEXTBOOK.md` | v0.5 | `d441d67eea3e` | — |
| `REVIEW_PROTOCOL.md` | v7.2 | `7f6e413d4d48` | — |
| `TOOLS_MANIFEST.md` | v48 | `54b99bf88ca6` | ○ |
| `CODE_PROJECT_README.md` | v5 | `6db694b44ea6` | — |
| `HISTORY.md` | — | `eeaa17c45e2b` | ○ |
| `release.py` | — | `00abde82a376` | — |
| `GITHUB_README.md` | — | `a338fce401db` | — |
| `PRIVATE_TERMS.txt` | — | `d2562278023a` | — |
| `RELEASE.md` | v2.28 | — | 이 문서 |
<!-- sets:end -->

## 4. 각 프로젝트 대화창이 첫 세션에서 할 일

1. 발표: selfcheck(handoff 1.9·deck 16.27). **원작자 노트뿐인 덱에 적용할 때는 `--protect-memo`**(Cowork 지시의 파이썬 조각 대신). 근골격 서식 보정: `bake-autofit --screens …` → `fit-corner-boxes --dry-run` 으로 먼저 보고 적용 → 전후 diff(글·노트 불변) → 새 sha 를 영상의학에. K8 자료(`to발표` 요청).
2. 영상의학: 넘김 문법 변경 없음. 넘김 안내의 "normalize-notes(또는 protect_memo)" 는 "protect-memo" 로 읽는다.
3. 저자·리뷰어·교과서: 도구 변경 없음.

## 5. 검증하지 않은 것

- `fit-corner-boxes` 는 fixture 상자로만 — 실제 근골격 덱의 인용 상자 크기(3.11 × 0.27", 10pt)와 테마 글꼴로 Google Slides 에서 한 줄에 드는지는 발표·사용자 확인.
- P1 의 "3부 구조가 어디에도 없으면 원작자 노트 덱" 판정은 근골격 하지 덱(표지 0개)에 맞췄다. 일부만 손본 덱은 경고만 나올 수 있다.
- P4 넘침 비교는 원천 덱 글꼴 기준과 결과 덱 글꼴 기준이 다를 수 있다(테마가 다르면) — 차이를 '가져오며 생김' 으로 표시할 뿐 원인은 사람이 본다.
