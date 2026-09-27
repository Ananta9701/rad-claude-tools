# RELEASE v2.26 — manifest v46 — 2026-09-27

> **v2.26** — 발표가 오기 전에 미리 처리할 수 있는 것(사용자 09-27): 교과서 쪽 그림을 JPEG 로·작은 이미지 건너뜀·`split --part`(`textbook.py` 0.5), 발표 남은 요청 M3 덧붙임·N5(`handoff.py` 1.7). claim_graph·deck·verify 는 그대로. 이전 판 내용은 `HISTORY.md`.
> 교과서 첫 분할이 끝났다(09-27, 23권, 48.4 MB) — 대화창 Drive 검색·장 md 읽기·쪽 그림 모두 실물로 확인.
> **v2.25 결함 수정 포함 — 발표 Cowork 가 v2.25 에서 멈췄다**: validate.py 가 없는 Cowork VM 에서 `test_handoff.py` 3개 실패(selfcheck 불일치). 도구 동작은 맞고 **테스트가 빌드 환경(validate.py 있음)에만 맞춰져 있었다**. v2.26 은 두 환경 모두 통과하고, 빌드가 없는 환경을 흉내 내 한 번 더 돌린다.

## 1. 바뀐 것

| 도구 | 판 | 내용 |
|---|---|---|
| `textbook.py` | 0.5 | `page` 기본 JPEG(품질 90, `--png` 로 PNG) — 스캔 쪽 PNG 가 14.8 MB 였다. 32×32 픽셀보다 작은 이미지(스캔 PDF 의 1×1 마스크) 건너뜀. `split --part N`(장 파일 쪽 수 한도, 기본 30) |
| `test_textbook.py` | 0.5 | 28개(+1): JPEG·PNG·작은 이미지 건너뜀, `--part` |
| `TEXTBOOK.md` | 0.5 | §3 첫 분할 기록, JPEG, `--part` |
| `handoff.py` | 1.7 | **M3 덧붙임** 보고서에 "가져옴 메모 대조" — 가져온 슬라이드와 그 복제본의 기존 메모 구역이 원천 기대값 그대로인지 결과 덱에서 센다. **N5** `compare` 서식 비교를 문단마다 (수준, 실제 들여쓰기, 정렬, run 마다 글·실제 크기·굵게·기울임·밑줄·색)으로 — 크기·들여쓰기는 명시값이 없으면 레이아웃 같은 자리 표시자 → 마스터 bodyStyle/titleStyle 에서 풀어 온다(명시 20pt = 상속 20pt) |
| `test_handoff.py` | 1.7 | 23개(+1): 명시=상속 크기는 같은 서식·굵게는 다름, 병합 시험에 메모 대조 4/4. **validate 기대값을 환경에 맞게**(validate.py 없으면 '건너뜀' = None) — v2.25 가 Cowork VM 에서 3개 실패한 원인 |
| `HANDOFF_FORMAT.md` | 1.7 | v1.7 한 문단 |

## 2. 회신 항목별 답

| 항목 | 반영 |
|---|---|
| 발표 `260927_도구회신_병합넘김_준비_v1` M3 덧붙임(가져온 덱 메모 대조) | handoff 1.7 — `diff --map` 이 아니라 apply 보고서에서(가져옴마다 원천 기대값을 알고 있는 곳) |
| 발표 `260927_도구회신_v2.21_재시험_v1` N5 | handoff 1.7 |
| 발표 Cowork `260927_Cowork보고_근골격_v1_v1` — v2.25 selfcheck 불일치(test_handoff 실패 3)로 멈춤 | **결함(테스트)**: v1.6(K4)에서 validate.py 가 없으면 보고를 '건너뜀'(None)으로 바꿨는데, 테스트 3개가 '통과'(True)를 기대했다. 빌드 환경에는 validate.py 가 있어 잡히지 않았다. 재현(`HANDOFF_VALIDATE_PY=/nonexistent`) 뒤 고침, release.py 가 그 환경으로 한 번 더 돌린다. 같은 보고: `to발표` 직접 연결 통과(K5 — 폴더 이름 변경으로 풀림) |
| Cowork `260927_회신_Coworkto코드_교과서split_결과_v1` 7-1(1×1 PNG) | textbook 0.5 |
| 7-2(부모 Killed) | 고치지 않음 — 이어하기로 모두 복구됨. 큰 책 두 권 뒤에만 났다(메모리 추정) |
| 7-3(VM 파일 hardlink) | 도구 밖 — 기록만 |
| §3 19 인터벤션 7장 제목을 여는 쪽(PDF 83)에서 읽은 판단 | 사용자 09-27 받음 |

## 3. 받을 파일

zip 두 개: `v2.26_GitHub.zip`(GitHub 에 전부), `v2.26_코드전용.zip`(코드 프로젝트 파일을 전부 지우고 5개).

<!-- sets:begin — release.py 가 만든다. 손으로 고치지 않는다 -->
### 저자 (7)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `claim_graph.py` | v15.8.1 | `dc3ac0780b61` | — |
| `test_claim_graph.py` | v15.8.1 | `bcfe1c1e42d6` | — |
| `CLAIM_GRAPH.md` | v15.8.1 | `ca0bd5652f32` | — |
| `verify_toolkit.py` | v1.3.4 | `e703af6d5418` | — |
| `test_verify_toolkit.py` | v1.3.4 | `aba65de39d87` | — |
| `TOOLS_MANIFEST.md` | v46 | `56f8bcbb5004` | ○ |
| `RELEASE.md` | v2.26 | — | 이 문서 |

### 발표 (11)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `claim_graph.py` | v15.8.1 | `dc3ac0780b61` | — |
| `test_claim_graph.py` | v15.8.1 | `bcfe1c1e42d6` | — |
| `CLAIM_GRAPH.md` | v15.8.1 | `ca0bd5652f32` | — |
| `deck_toolkit.py` | v16.26 | `cab6d76ae0d8` | — |
| `test_toolkit.py` | v16.26 | `b9405ff4bfd8` | — |
| `DECK_SPEC.md` | v16.26 | `ac64f8ec2607` | — |
| `handoff.py` | v1.7 | `36a1c91ccaed` | ○ |
| `test_handoff.py` | v1.7 | `3f27de5f6b18` | ○ |
| `HANDOFF_FORMAT.md` | v1.7 | `dd5c8634782e` | ○ |
| `TOOLS_MANIFEST.md` | v46 | `56f8bcbb5004` | ○ |
| `RELEASE.md` | v2.26 | — | 이 문서 |

### 리뷰어 (6)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `claim_graph.py` | v15.8.1 | `dc3ac0780b61` | — |
| `test_claim_graph.py` | v15.8.1 | `bcfe1c1e42d6` | — |
| `CLAIM_GRAPH.md` | v15.8.1 | `ca0bd5652f32` | — |
| `REVIEW_PROTOCOL.md` | v7.2 | `7f6e413d4d48` | — |
| `TOOLS_MANIFEST.md` | v46 | `56f8bcbb5004` | ○ |
| `RELEASE.md` | v2.26 | — | 이 문서 |

### 교과서 (5)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `textbook.py` | v0.5 | `5f916620c6c0` | ○ |
| `test_textbook.py` | v0.5 | `4b2da8dfcecb` | ○ |
| `TEXTBOOK.md` | v0.5 | `d441d67eea3e` | ○ |
| `TOOLS_MANIFEST.md` | v46 | `56f8bcbb5004` | ○ |
| `RELEASE.md` | v2.26 | — | 이 문서 |

### 코드 (22)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `claim_graph.py` | v15.8.1 | `dc3ac0780b61` | — |
| `test_claim_graph.py` | v15.8.1 | `bcfe1c1e42d6` | — |
| `CLAIM_GRAPH.md` | v15.8.1 | `ca0bd5652f32` | — |
| `deck_toolkit.py` | v16.26 | `cab6d76ae0d8` | — |
| `test_toolkit.py` | v16.26 | `b9405ff4bfd8` | — |
| `DECK_SPEC.md` | v16.26 | `ac64f8ec2607` | — |
| `verify_toolkit.py` | v1.3.4 | `e703af6d5418` | — |
| `test_verify_toolkit.py` | v1.3.4 | `aba65de39d87` | — |
| `handoff.py` | v1.7 | `36a1c91ccaed` | ○ |
| `test_handoff.py` | v1.7 | `3f27de5f6b18` | ○ |
| `HANDOFF_FORMAT.md` | v1.7 | `dd5c8634782e` | ○ |
| `textbook.py` | v0.5 | `5f916620c6c0` | ○ |
| `test_textbook.py` | v0.5 | `4b2da8dfcecb` | ○ |
| `TEXTBOOK.md` | v0.5 | `d441d67eea3e` | ○ |
| `REVIEW_PROTOCOL.md` | v7.2 | `7f6e413d4d48` | — |
| `TOOLS_MANIFEST.md` | v46 | `56f8bcbb5004` | ○ |
| `CODE_PROJECT_README.md` | v5 | `6db694b44ea6` | — |
| `HISTORY.md` | — | `d23c1b0baa2f` | ○ |
| `release.py` | — | `00abde82a376` | ○ |
| `GITHUB_README.md` | — | `a338fce401db` | — |
| `PRIVATE_TERMS.txt` | — | `d2562278023a` | — |
| `RELEASE.md` | v2.26 | — | 이 문서 |
<!-- sets:end -->

## 4. 각 프로젝트 대화창이 첫 세션에서 할 일

1. 발표: **v2.26 을 받아 Cowork 근골격 v1 을 다시**(v2.25 selfcheck 에서 멈춘 것 — 도구는 그대로, 테스트만 고침). selfcheck(handoff 1.7). 다음 적용 보고서에 "가져옴 메모 대조" 줄이 생긴다. `compare` 의 "서식" 잡음이 줄었는지 다음 비교에서 본다.
2. 교과서(Cowork): 다음 `page` 는 JPEG 로 나온다. 분할을 다시 할 일은 없다.
3. 저자·리뷰어·영상의학: 도구 변경 없음.

## 5. 검증하지 않은 것

- N5 는 fixture 덱의 본문 자리 표시자 하나로만 시험했다. 제목 자리 표시자, 마스터가 여러 개인 짜깁기 덱, `marL` 이 레이아웃에서만 정해진 경우는 발표 비교에서 처음 본다.
- JPEG 저장은 fixture 이미지로만 — 실제 스캔 쪽(흑백 1비트 등)의 모드 변환은 다음 `page` 에서 본다.
