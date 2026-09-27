# RELEASE v2.27 — manifest v47 — 2026-09-27

> **v2.27** — `handoff.py` 1.8 `--base-origin` 하나. 발표 Cowork 근골격 v1 이 5단계(적용용 넘김 사본)에서 멈춘 것의 코드 결정(Cowork 가 사용자 지시로 결정을 코드에 넘김). 다른 도구는 그대로. 이전 판 내용은 `HISTORY.md`.

## 1. 바뀐 것

| 도구 | 판 | 내용 |
|---|---|---|
| `handoff.py` | 1.8 | `check`·`apply --base-origin 정리 전 원본` — 넘김의 `기준 sha256` 은 원본(파일 sha 또는 내용 해시)으로, 화면 수·제목·문단 키·본문 수정은 `--deck`(정리본)으로 대조. 미리보기에 "기준 대조" 줄. 원본이 없거나 다른 판이면 오류, 넘김에 기준 sha256 이 없으면 경고 |
| `test_handoff.py` | 1.8 | 24개(+1): 정리본만으로는 sha 오류, 원본을 주면 통과, 다른 판·없는 원본은 오류, CLI apply |
| `HANDOFF_FORMAT.md` | 1.8 | v1.8 한 문단 — 넘김 사본을 만들어 기준 sha 줄을 지우지 않는다 |

## 2. 회신 항목별 답

| 항목 | 반영 |
|---|---|
| Cowork `260927_회신_Cowork_근골격v1_5단계줄바꿈_v1` — (가) 끝 줄바꿈 허용 / (나) 줄바꿈 보존 사본 / (다) 그 밖 | **(다)** — 사본을 만드는 5단계를 없앤다. 사본이 필요했던 이유(정리한 기준 덱은 넘김의 기준 sha256 과 다름)를 도구가 `--base-origin` 으로 받는다. 넘김은 받은 바이트 그대로 쓰니 `--sha` 는 보냄기록 값(`d82841e2eec7d757`)과 맞고, 줄바꿈 문제는 생기지 않는다. (가)는 멈춤 조건을 느슨하게 하고, (나)는 적용용 sha 가 또 하나 생긴다 |

## 3. 받을 파일

zip 두 개: `v2.27_GitHub.zip`(GitHub 에 전부), `v2.27_코드전용.zip`(코드 프로젝트 파일을 전부 지우고 5개).

<!-- sets:begin — release.py 가 만든다. 손으로 고치지 않는다 -->
### 저자 (7)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `claim_graph.py` | v15.8.1 | `dc3ac0780b61` | — |
| `test_claim_graph.py` | v15.8.1 | `bcfe1c1e42d6` | — |
| `CLAIM_GRAPH.md` | v15.8.1 | `ca0bd5652f32` | — |
| `verify_toolkit.py` | v1.3.4 | `e703af6d5418` | — |
| `test_verify_toolkit.py` | v1.3.4 | `aba65de39d87` | — |
| `TOOLS_MANIFEST.md` | v47 | `c3ae5f4ab328` | ○ |
| `RELEASE.md` | v2.27 | — | 이 문서 |

### 발표 (11)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `claim_graph.py` | v15.8.1 | `dc3ac0780b61` | — |
| `test_claim_graph.py` | v15.8.1 | `bcfe1c1e42d6` | — |
| `CLAIM_GRAPH.md` | v15.8.1 | `ca0bd5652f32` | — |
| `deck_toolkit.py` | v16.26 | `cab6d76ae0d8` | — |
| `test_toolkit.py` | v16.26 | `b9405ff4bfd8` | — |
| `DECK_SPEC.md` | v16.26 | `ac64f8ec2607` | — |
| `handoff.py` | v1.8 | `889e4ba03ff4` | ○ |
| `test_handoff.py` | v1.8 | `eba5982e7ce4` | ○ |
| `HANDOFF_FORMAT.md` | v1.8 | `16023928d734` | ○ |
| `TOOLS_MANIFEST.md` | v47 | `c3ae5f4ab328` | ○ |
| `RELEASE.md` | v2.27 | — | 이 문서 |

### 리뷰어 (6)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `claim_graph.py` | v15.8.1 | `dc3ac0780b61` | — |
| `test_claim_graph.py` | v15.8.1 | `bcfe1c1e42d6` | — |
| `CLAIM_GRAPH.md` | v15.8.1 | `ca0bd5652f32` | — |
| `REVIEW_PROTOCOL.md` | v7.2 | `7f6e413d4d48` | — |
| `TOOLS_MANIFEST.md` | v47 | `c3ae5f4ab328` | ○ |
| `RELEASE.md` | v2.27 | — | 이 문서 |

### 교과서 (5)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `textbook.py` | v0.5 | `5f916620c6c0` | — |
| `test_textbook.py` | v0.5 | `4b2da8dfcecb` | — |
| `TEXTBOOK.md` | v0.5 | `d441d67eea3e` | — |
| `TOOLS_MANIFEST.md` | v47 | `c3ae5f4ab328` | ○ |
| `RELEASE.md` | v2.27 | — | 이 문서 |

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
| `handoff.py` | v1.8 | `889e4ba03ff4` | ○ |
| `test_handoff.py` | v1.8 | `eba5982e7ce4` | ○ |
| `HANDOFF_FORMAT.md` | v1.8 | `16023928d734` | ○ |
| `textbook.py` | v0.5 | `5f916620c6c0` | — |
| `test_textbook.py` | v0.5 | `4b2da8dfcecb` | — |
| `TEXTBOOK.md` | v0.5 | `d441d67eea3e` | — |
| `REVIEW_PROTOCOL.md` | v7.2 | `7f6e413d4d48` | — |
| `TOOLS_MANIFEST.md` | v47 | `c3ae5f4ab328` | ○ |
| `CODE_PROJECT_README.md` | v5 | `6db694b44ea6` | — |
| `HISTORY.md` | — | `64550cd914de` | ○ |
| `release.py` | — | `00abde82a376` | — |
| `GITHUB_README.md` | — | `a338fce401db` | — |
| `PRIVATE_TERMS.txt` | — | `d2562278023a` | — |
| `RELEASE.md` | v2.27 | — | 이 문서 |
<!-- sets:end -->

## 4. 각 프로젝트 대화창이 첫 세션에서 할 일

1. 발표: Cowork 지시의 **5단계(적용용 사본)를 빼고**, 6단계 `check`·`apply` 에 `--deck {정리본} --base-origin {정리 전 원본 기준 덱} --sha {보냄기록의 넘김 sha}`. 근골격 v1 을 1단계부터 다시.
2. 그 밖의 프로젝트: 도구 변경 없음.

## 5. 검증하지 않은 것

- 실제 근골격 v1 넘김·덱으로는 돌리지 않았다(fixture 덱 + 노트 한 곳 바꾼 정리본).
