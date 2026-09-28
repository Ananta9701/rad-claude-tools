# RELEASE v2.36 — manifest v56 — 2026-09-28

> **v2.36** — 발표 `260928_도구회신_K18테스트_py310_v1` 처리. **테스트 결함**: v2.35 의 `test_toolkit.py` 가 Python 3.12 에서만 통과(Cowork 는 3.10 — 인터벤션 v6 작업이 selfcheck 에서 멈춤). 도구 코드는 그대로. 이전 판 내용은 `HISTORY.md`.

## 1. 바뀐 것

| 도구 | 판 | 내용 |
|---|---|---|
| `test_toolkit.py` | 16.34 | `t_v1634_fit_layout_stage2` 의 `auto_size = True` → `MSO_AUTO_SIZE.SHAPE_TO_FIT_TEXT`. python-pptx 가 값을 열거형에 `in` 으로 확인하는데 3.12 는 `True in Enum` 을 값(1)으로 받아 우연히 통과, 3.10·3.11 은 TypeError. **Python 3.10.20 에서 180/180 재현·확인**(Cowork 와 같은 1개 실패를 먼저 재현) |
| `deck_toolkit.py` | 16.34 | 변경 없음 — 같은 모양(bool 을 열거형에 쓰기)이 도구에 없는 것을 확인 |

코드 전용 `release.py`: 빌드가 **Python 3.10 으로도 모든 테스트**를 돌려 통과 수가 같아야 zip 을 만든다(없으면 uv 로 3.10 을 만든다 — PyPI·GitHub 만 씀, 네트워크가 막히면 `--no-py310`). 배포 사고 ⑧(validate.py)·⑨(Python 판)는 둘 다 "빌드 환경과 Cowork 환경이 다른데 빌드 환경에서만 시험" 이 원인.

## 2. 회신 항목별 답

| 항목 | 반영 |
|---|---|
| K18 테스트를 열거형으로 | v2.36 — 발표가 코드를 읽어 찾은 원인 그대로(3.10 에서 재현 확인) |
| selfcheck 를 3.10 에서도 | release.py 가 빌드 때 3.10 으로 모든 테스트(5종: 34·180·41·26·28 모두 같음) |
| deck_toolkit 에 같은 모양 | 없음(python-pptx 열거형을 쓰지 않는다 — XML 을 직접 다룬다) |

## 3. 받을 파일

zip 두 개: `v2.36_GitHub.zip`(GitHub 에 전부), `v2.36_코드전용.zip`(코드 프로젝트 파일을 전부 지우고 5개).

<!-- sets:begin — release.py 가 만든다. 손으로 고치지 않는다 -->
### 저자 (7)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `claim_graph.py` | v15.8.1 | `dc3ac0780b61` | — |
| `test_claim_graph.py` | v15.8.1 | `bcfe1c1e42d6` | — |
| `CLAIM_GRAPH.md` | v15.8.1 | `ca0bd5652f32` | — |
| `verify_toolkit.py` | v1.3.4 | `e703af6d5418` | — |
| `test_verify_toolkit.py` | v1.3.4 | `aba65de39d87` | — |
| `TOOLS_MANIFEST.md` | v56 | `07eefffb9e5a` | ○ |
| `RELEASE.md` | v2.36 | — | 이 문서 |

### 발표 (11)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `claim_graph.py` | v15.8.1 | `dc3ac0780b61` | — |
| `test_claim_graph.py` | v15.8.1 | `bcfe1c1e42d6` | — |
| `CLAIM_GRAPH.md` | v15.8.1 | `ca0bd5652f32` | — |
| `deck_toolkit.py` | v16.34 | `2deea648cc99` | — |
| `test_toolkit.py` | v16.34 | `ee01434fcefb` | ○ |
| `DECK_SPEC.md` | v16.34 | `83786baadd59` | — |
| `handoff.py` | v2.0 | `642269d51cc5` | — |
| `test_handoff.py` | v2.0 | `3c660a5a654c` | — |
| `HANDOFF_FORMAT.md` | v2.0 | `577b9f35e9d9` | — |
| `TOOLS_MANIFEST.md` | v56 | `07eefffb9e5a` | ○ |
| `RELEASE.md` | v2.36 | — | 이 문서 |

### 리뷰어 (6)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `claim_graph.py` | v15.8.1 | `dc3ac0780b61` | — |
| `test_claim_graph.py` | v15.8.1 | `bcfe1c1e42d6` | — |
| `CLAIM_GRAPH.md` | v15.8.1 | `ca0bd5652f32` | — |
| `REVIEW_PROTOCOL.md` | v7.2 | `7f6e413d4d48` | — |
| `TOOLS_MANIFEST.md` | v56 | `07eefffb9e5a` | ○ |
| `RELEASE.md` | v2.36 | — | 이 문서 |

### 교과서 (5)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `textbook.py` | v0.5 | `5f916620c6c0` | — |
| `test_textbook.py` | v0.5 | `4b2da8dfcecb` | — |
| `TEXTBOOK.md` | v0.5 | `d441d67eea3e` | — |
| `TOOLS_MANIFEST.md` | v56 | `07eefffb9e5a` | ○ |
| `RELEASE.md` | v2.36 | — | 이 문서 |

### 코드 (22)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `claim_graph.py` | v15.8.1 | `dc3ac0780b61` | — |
| `test_claim_graph.py` | v15.8.1 | `bcfe1c1e42d6` | — |
| `CLAIM_GRAPH.md` | v15.8.1 | `ca0bd5652f32` | — |
| `deck_toolkit.py` | v16.34 | `2deea648cc99` | — |
| `test_toolkit.py` | v16.34 | `ee01434fcefb` | ○ |
| `DECK_SPEC.md` | v16.34 | `83786baadd59` | — |
| `verify_toolkit.py` | v1.3.4 | `e703af6d5418` | — |
| `test_verify_toolkit.py` | v1.3.4 | `aba65de39d87` | — |
| `handoff.py` | v2.0 | `642269d51cc5` | — |
| `test_handoff.py` | v2.0 | `3c660a5a654c` | — |
| `HANDOFF_FORMAT.md` | v2.0 | `577b9f35e9d9` | — |
| `textbook.py` | v0.5 | `5f916620c6c0` | — |
| `test_textbook.py` | v0.5 | `4b2da8dfcecb` | — |
| `TEXTBOOK.md` | v0.5 | `d441d67eea3e` | — |
| `REVIEW_PROTOCOL.md` | v7.2 | `7f6e413d4d48` | — |
| `TOOLS_MANIFEST.md` | v56 | `07eefffb9e5a` | ○ |
| `CODE_PROJECT_README.md` | v5 | `fc373977d111` | ○ |
| `HISTORY.md` | — | `8890855ea3b8` | ○ |
| `release.py` | — | `cb5c9f7c6296` | ○ |
| `GITHUB_README.md` | — | `a338fce401db` | — |
| `PRIVATE_TERMS.txt` | — | `6e8c2862cf5e` | — |
| `RELEASE.md` | v2.36 | — | 이 문서 |
<!-- sets:end -->

## 4. 각 프로젝트 대화창이 첫 세션에서 할 일

1. 발표: v6 지시를 그대로 다시(발표 말대로 "v2.35 이상" 이라 고칠 곳 없음).
2. 그 밖의 프로젝트: 도구 변경 없음.

## 5. 검증하지 않은 것

- 3.10 은 uv 가 받은 CPython 3.10.20(Cowork 는 3.10.12) — 패치 판 차이는 보지 않았다. python-pptx·Pillow 판도 Cowork 와 같다는 보장은 없다.
