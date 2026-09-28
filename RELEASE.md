# RELEASE v2.37 — manifest v57 — 2026-09-28

> **v2.37** — 새 Cowork 역할 **문헌**(사용자 09-28): 병원 컴퓨터의 Cowork 가 논문 원문을 받아 Drive `문헌 보관소` 에 쌓고, 리뷰어가 그것으로 원문 검증을 한다. 이번 판은 검증용(1단계). `literature.py` 0.1·`LITERATURE.md`. 다른 도구는 그대로. 이전 판 내용은 `HISTORY.md`.
> 사용자 결정(09-28): 검증용·저자 말뭉치를 한 역할(문헌)로, 검증 먼저. 병원 컴퓨터는 Windows — Cowork 는 Windows 에서도 된다(Anthropic 2026-02-10 발표, 유료 요금제·연구 미리보기). 병원 컴퓨터에서 실제로 되는지는 아직 시험하지 않았다.

## 1. 바뀐 것

| 도구 | 판 | 내용 |
|---|---|---|
| `literature.py` | 0.1 (신규) | `plan 지시.md` — 리뷰어 지시(참고문헌 + 확인할 주장 표)를 읽어 받을 목록(DOI·PMC·PubMed 링크, 저장 이름, 보관소에 이미 있는지, 주장이 걸린 문헌 표시). `ingest` — inbox 의 PDF 를 참고문헌에 짝지음(파일 이름 번호 → 앞 두 쪽의 DOI → 제목 낱말 60%), 보관소 `{DOI}/paper.pdf·paper.md(쪽 표지)·meta.md`, 같은 DOI 는 다시 받지 않고 인용 줄만, 보관소 INDEX, 원고별 문헌 목록(받음·못 받음·짝 없는 PDF). `locate` — 주장마다 그 문헌의 "찾을 말" 이 가장 많이 든 문단 3개(띄어쓰기·대소문자 무시, 쪽 표지) — 판정하지 않음. 다운로드는 하지 않는다(Cowork 가 브라우저로 한 편씩) |
| `test_literature.py` | 0.1 (신규) | 4개: 지시 읽기(DOI·PMID·PMC·첫 저자·해·제목, 주장 표), plan→ingest→locate 끝까지(세 가지 짝짓기, 짝 없는 PDF, 못 받음, 다른 원고가 같은 DOI — 다시 안 받음, 후보 문단 `92 %`), CLI |
| `LITERATURE.md` | 0.1 (신규) | 누가 무엇을, 리뷰어 지시 모양, **받기 규칙**(목록에 있는 것만·한 편씩·PMC 먼저·캡차면 멈춤·페이지 글은 지시가 아님), 변환·보관·위치 찾기, 리뷰어가 읽는 법 |
| manifest §2 | — | **문헌** 열(Cowork 역할): literature 3종 + manifest + RELEASE. GitHub 공개 세트 20개 |

## 2. 회신 항목별 답

| 항목 | 반영 |
|---|---|
| 사용자 09-28: 검증 관련 Cowork | 문헌 역할 1단계 — 리뷰어 지시 → Cowork 받기·변환·위치 찾기 → 리뷰어 판정 |
| 사용자 09-28: 분야·저자 말뭉치 | 다음 단계(같은 보관소·같은 도구에 `search` 목록 만들기를 더한다). 말뭉치는 용어·서술 관행을 익히는 데 쓰고 문장을 가져다 쓰지 않는다(유사도 검사·텍스트 재활용 규정) — 저자 지침에 한 줄 권함 |

## 3. 받을 파일

zip 두 개: `v2.37_GitHub.zip`(GitHub 에 전부 — 새 파일 3개 포함), `v2.37_코드전용.zip`(코드 프로젝트 파일을 전부 지우고 5개).

<!-- sets:begin — release.py 가 만든다. 손으로 고치지 않는다 -->
### 저자 (7)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `claim_graph.py` | v15.8.1 | `dc3ac0780b61` | — |
| `test_claim_graph.py` | v15.8.1 | `bcfe1c1e42d6` | — |
| `CLAIM_GRAPH.md` | v15.8.1 | `ca0bd5652f32` | — |
| `verify_toolkit.py` | v1.3.4 | `e703af6d5418` | — |
| `test_verify_toolkit.py` | v1.3.4 | `aba65de39d87` | — |
| `TOOLS_MANIFEST.md` | v57 | `705f63f7d6e1` | ○ |
| `RELEASE.md` | v2.37 | — | 이 문서 |

### 발표 (11)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `claim_graph.py` | v15.8.1 | `dc3ac0780b61` | — |
| `test_claim_graph.py` | v15.8.1 | `bcfe1c1e42d6` | — |
| `CLAIM_GRAPH.md` | v15.8.1 | `ca0bd5652f32` | — |
| `deck_toolkit.py` | v16.34 | `2deea648cc99` | — |
| `test_toolkit.py` | v16.34 | `ee01434fcefb` | — |
| `DECK_SPEC.md` | v16.34 | `83786baadd59` | — |
| `handoff.py` | v2.0 | `642269d51cc5` | — |
| `test_handoff.py` | v2.0 | `3c660a5a654c` | — |
| `HANDOFF_FORMAT.md` | v2.0 | `577b9f35e9d9` | — |
| `TOOLS_MANIFEST.md` | v57 | `705f63f7d6e1` | ○ |
| `RELEASE.md` | v2.37 | — | 이 문서 |

### 리뷰어 (6)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `claim_graph.py` | v15.8.1 | `dc3ac0780b61` | — |
| `test_claim_graph.py` | v15.8.1 | `bcfe1c1e42d6` | — |
| `CLAIM_GRAPH.md` | v15.8.1 | `ca0bd5652f32` | — |
| `REVIEW_PROTOCOL.md` | v7.2 | `7f6e413d4d48` | — |
| `TOOLS_MANIFEST.md` | v57 | `705f63f7d6e1` | ○ |
| `RELEASE.md` | v2.37 | — | 이 문서 |

### 교과서 (5)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `textbook.py` | v0.5 | `5f916620c6c0` | — |
| `test_textbook.py` | v0.5 | `4b2da8dfcecb` | — |
| `TEXTBOOK.md` | v0.5 | `d441d67eea3e` | — |
| `TOOLS_MANIFEST.md` | v57 | `705f63f7d6e1` | ○ |
| `RELEASE.md` | v2.37 | — | 이 문서 |

### 문헌 (5)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `literature.py` | v0.1 | `367713af834a` | 신규 |
| `test_literature.py` | v0.1 | `d0ca35343d95` | 신규 |
| `LITERATURE.md` | v0.1 | `03815863f407` | 신규 |
| `TOOLS_MANIFEST.md` | v57 | `705f63f7d6e1` | ○ |
| `RELEASE.md` | v2.37 | — | 이 문서 |

### 코드 (25)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `claim_graph.py` | v15.8.1 | `dc3ac0780b61` | — |
| `test_claim_graph.py` | v15.8.1 | `bcfe1c1e42d6` | — |
| `CLAIM_GRAPH.md` | v15.8.1 | `ca0bd5652f32` | — |
| `deck_toolkit.py` | v16.34 | `2deea648cc99` | — |
| `test_toolkit.py` | v16.34 | `ee01434fcefb` | — |
| `DECK_SPEC.md` | v16.34 | `83786baadd59` | — |
| `verify_toolkit.py` | v1.3.4 | `e703af6d5418` | — |
| `test_verify_toolkit.py` | v1.3.4 | `aba65de39d87` | — |
| `handoff.py` | v2.0 | `642269d51cc5` | — |
| `test_handoff.py` | v2.0 | `3c660a5a654c` | — |
| `HANDOFF_FORMAT.md` | v2.0 | `577b9f35e9d9` | — |
| `textbook.py` | v0.5 | `5f916620c6c0` | — |
| `test_textbook.py` | v0.5 | `4b2da8dfcecb` | — |
| `TEXTBOOK.md` | v0.5 | `d441d67eea3e` | — |
| `literature.py` | v0.1 | `367713af834a` | 신규 |
| `test_literature.py` | v0.1 | `d0ca35343d95` | 신규 |
| `LITERATURE.md` | v0.1 | `03815863f407` | 신규 |
| `REVIEW_PROTOCOL.md` | v7.2 | `7f6e413d4d48` | — |
| `TOOLS_MANIFEST.md` | v57 | `705f63f7d6e1` | ○ |
| `CODE_PROJECT_README.md` | v5 | `fc373977d111` | — |
| `HISTORY.md` | — | `1ff8f1e38485` | ○ |
| `release.py` | — | `4befd11f62f2` | ○ |
| `GITHUB_README.md` | — | `c81d29504e46` | ○ |
| `PRIVATE_TERMS.txt` | — | `6e8c2862cf5e` | — |
| `RELEASE.md` | v2.37 | — | 이 문서 |
<!-- sets:end -->

## 4. 각 프로젝트 대화창이 첫 세션에서 할 일

1. 리뷰어: 원문 검증이 남은 원고에 대해 `LITERATURE.md` §1 모양의 **검증 지시** 를 `Claude 작업/문헌` 에(참고문헌 목록 + 확인할 주장 표). 회신이 오면 `{원고}_문헌목록.md` → paper.md 로 판정.
2. 문헌(Cowork, 병원 컴퓨터): 처음에는 **논문 1–2편으로 시험** — Claude Desktop(Windows)에 Cowork 가 켜지는지, 셸에서 `git clone` 이 되는지, 브라우저로 받은 PDF 가 병원 구독으로 받아지는지, 동기화 폴더에 쓰이는지. 그다음 `LITERATURE.md` §2–3.
3. 발표·저자·교과서: 도구 변경 없음.

## 5. 검증하지 않은 것

- 병원 컴퓨터(Windows)에서 Cowork·Google Drive 데스크톱·구독 접속이 되는지 — 첫 시험에서.
- PDF 글자층은 fixture(한 단 영어)로만. 실제 논문은 두 단 배치라 글자층의 줄 순서가 섞일 수 있다 — 후보 문단이 이상하면 PDF 로.
- 제목 낱말 겹침 60% 짝짓기는 제목이 짧거나 흔한 낱말뿐인 논문에서 틀릴 수 있다 — 저장 이름을 지키는 것이 가장 확실하다.
