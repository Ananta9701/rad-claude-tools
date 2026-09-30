# RELEASE v2.79 — manifest v99 — 2026-09-30

> **v2.79** — ④ 문헌 그래프 2판: 우리 주장 ↔ 논문 주장 짝 `lit_links`(우리 그래프 맨 위 칸) · 짝 검사 `litcheck` · `mapgraph`·`impact --lit <문헌 보관소>` 가 짝 맺은 논문 주장을 `lit:<DOI>#<id>` 로 읽는 순간 합친다. 판정 전 논문 주장이 main 의 전제 사슬을 받치면 [필수].

## 1. 바뀐 것

| 도구 | 판 | 내용 |
|---|---|---|
| `claim_graph.py` | 16.21 | `LIT_RELS`(same·support → support · rebut → rebuttal · background → context) · `lit_merge(meta, claims, 보관소)` — 짝이 가리키는 논문 주장만 `lit:<DOI>#<id>`·`lit: true`·`lit_role` 로(자리·keys·간선·sources 없이), 우리 주장에 간선 하나, 우리 파일은 그대로 · [필수] lit_links 모양·ours 없음·rel·verdict 값·DOI 모양·보관소에 없는 DOI·논문 claims.json 없음/다른 논문·theirs 없음·**판정 전(proposed) 논문 주장이 same·support 로 main 전제 사슬 안 주장을 받침** · [참고] verdict 없음·sources 에 같은 DOI 없음·같은 짝 두 번·사람 이름 꼴·철회된 논문 주장 · 새 명령 `litcheck --claims --store`(종료 0/1) · `mapgraph`·`impact` 에 `--lit <보관소>`(`--oral` 과 같이면 종료 2), `--lit` 없이 mapgraph 하면 `lit_links N개` 안내 한 줄 |
| `CLAIM_GRAPH.md` | 16.21 | §3-8-1 새 절(짝·litcheck·--lit) · §4 명령 표 |
| 테스트 | — | test_claim_graph 5(합치기 성공·rel 별 간선·논문 주장 한 번·우리 파일 그대로·lit_links 없으면 그대로 / [필수] 8가지 / 판정 전 + main 사슬 [필수], 판정됨·사슬 밖·rebut·background 는 아님 / [참고] 5가지 / CLI litcheck 0·1·없음 · mapgraph --lit · 안내 줄 · impact lit id · --oral 같이 종료 2 · add 가 lit_links 보존) |

## 2. 회신 항목별 답

| 항목 | 반영 |
|---|---|
| 부관리자 지시 09-30(`권한방식과역할상태_v1` 3번): 작은 고침 다음 ④ 2판 | 위. 설계안 ④ §2 의 2판 몫(짝 칸·litcheck·합치기 `--lit` mapgraph·impact). mapstale·mapdraw·focus `--lit`·gaps 인정은 3판 |
| 사용자·부관리자 09-30 ④ 결정 1·2·5 | 새 칸 `lit_links` · same·support=support(premise 로 올리지 않음)·rebut=rebuttal·background=context · 판정 전 논문 주장이 main 전제 사슬 → [필수] |

## 3. 받을 파일

**zip 없음.** 코드 세션이 공개 저장소(`rad-claude-tools`)와 비공개 저장소(`rad-claude-private`)에 직접 올린다.

<!-- sets:begin — release.py 가 만든다. 손으로 고치지 않는다 -->
### 저자 (7)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `claim_graph.py` | v16.21 | `74e957423b4b` | ○ |
| `test_claim_graph.py` | v16.21 | `2eac787fe295` | ○ |
| `CLAIM_GRAPH.md` | v16.21 | `2c743663f04d` | ○ |
| `verify_toolkit.py` | v1.3.7 | `0833539073f1` | — |
| `test_verify_toolkit.py` | v1.3.7 | `ac6e42ed2103` | — |
| `TOOLS_MANIFEST.md` | v99 | `c3c8ef64a3b7` | ○ |
| `RELEASE.md` | v2.79 | — | 이 문서 |

### 발표 (11)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `claim_graph.py` | v16.21 | `74e957423b4b` | ○ |
| `test_claim_graph.py` | v16.21 | `2eac787fe295` | ○ |
| `CLAIM_GRAPH.md` | v16.21 | `2c743663f04d` | ○ |
| `deck_toolkit.py` | v16.51 | `c14c4686c2b1` | — |
| `test_toolkit.py` | v16.51 | `2193bcdf541c` | — |
| `DECK_SPEC.md` | v16.51 | `9ce13600b06d` | — |
| `handoff.py` | v2.2 | `d8b5305111f4` | — |
| `test_handoff.py` | v2.2 | `7b2a11d55b3a` | — |
| `HANDOFF_FORMAT.md` | v2.2 | `92fb4a11e9bb` | — |
| `TOOLS_MANIFEST.md` | v99 | `c3c8ef64a3b7` | ○ |
| `RELEASE.md` | v2.79 | — | 이 문서 |

### 리뷰어 (6)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `claim_graph.py` | v16.21 | `74e957423b4b` | ○ |
| `test_claim_graph.py` | v16.21 | `2eac787fe295` | ○ |
| `CLAIM_GRAPH.md` | v16.21 | `2c743663f04d` | ○ |
| `REVIEW_PROTOCOL.md` | v7.2 | `7f6e413d4d48` | — |
| `TOOLS_MANIFEST.md` | v99 | `c3c8ef64a3b7` | ○ |
| `RELEASE.md` | v2.79 | — | 이 문서 |

### 교과서 (5)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `textbook.py` | v0.7.2 | `446049895c66` | — |
| `test_textbook.py` | v0.7.2 | `93d75911d86c` | — |
| `TEXTBOOK.md` | v0.7.2 | `4bfff4aa0771` | — |
| `TOOLS_MANIFEST.md` | v99 | `c3c8ef64a3b7` | ○ |
| `RELEASE.md` | v2.79 | — | 이 문서 |

### 문헌 (5)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `literature.py` | v0.8.5 | `2d1bddcb98e6` | — |
| `test_literature.py` | v0.8.5 | `c0c1ad7ce476` | — |
| `LITERATURE.md` | v0.8.5 | `25e2f224c92f` | — |
| `TOOLS_MANIFEST.md` | v99 | `c3c8ef64a3b7` | ○ |
| `RELEASE.md` | v2.79 | — | 이 문서 |

### 코드 (25)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `claim_graph.py` | v16.21 | `74e957423b4b` | ○ |
| `test_claim_graph.py` | v16.21 | `2eac787fe295` | ○ |
| `CLAIM_GRAPH.md` | v16.21 | `2c743663f04d` | ○ |
| `deck_toolkit.py` | v16.51 | `c14c4686c2b1` | — |
| `test_toolkit.py` | v16.51 | `2193bcdf541c` | — |
| `DECK_SPEC.md` | v16.51 | `9ce13600b06d` | — |
| `verify_toolkit.py` | v1.3.7 | `0833539073f1` | — |
| `test_verify_toolkit.py` | v1.3.7 | `ac6e42ed2103` | — |
| `handoff.py` | v2.2 | `d8b5305111f4` | — |
| `test_handoff.py` | v2.2 | `7b2a11d55b3a` | — |
| `HANDOFF_FORMAT.md` | v2.2 | `92fb4a11e9bb` | — |
| `textbook.py` | v0.7.2 | `446049895c66` | — |
| `test_textbook.py` | v0.7.2 | `93d75911d86c` | — |
| `TEXTBOOK.md` | v0.7.2 | `4bfff4aa0771` | — |
| `literature.py` | v0.8.5 | `2d1bddcb98e6` | — |
| `test_literature.py` | v0.8.5 | `c0c1ad7ce476` | — |
| `LITERATURE.md` | v0.8.5 | `25e2f224c92f` | — |
| `REVIEW_PROTOCOL.md` | v7.2 | `7f6e413d4d48` | — |
| `TOOLS_MANIFEST.md` | v99 | `c3c8ef64a3b7` | ○ |
| `CODE_PROJECT_README.md` | v5 | `f4c839b0b750` | — |
| `HISTORY.md` | — | `7b15679d7827` | ○ |
| `release.py` | — | `d0fe4b4d184a` | — |
| `GITHUB_README.md` | — | `c81d29504e46` | — |
| `PRIVATE_TERMS.txt` | — | `6e8c2862cf5e` | — |
| `RELEASE.md` | v2.79 | — | 이 문서 |
<!-- sets:end -->

## 4. 각 프로젝트 대화창이 첫 세션에서 할 일

1. 모든 역할: selfcheck 로 manifest v99 이상.
2. 문헌 그래프·짝은 아직 실물이 없다 — 첫 실물(문헌 Cowork 가 논문 그래프 초안 → 리뷰어 판정 → 짝)은 따로 지시가 간다. 그 전에는 할 일 없음.

## 5. 검증하지 않은 것

- 실물 없음 — 가짜 보관소(가짜 DOI 두 편)로만. 실제 보관소 폴더 이름·meta.md 첫 줄 모양은 v2.77 `sources` 찾기와 같은 규칙이라 그쪽 실물(09-29 보관소 3편)에 기댄다.
- `--lit` 합친 그래프로 `mapdraw`·`focus` 는 아직 안 된다(3판) — 논문 주장 id 에 `:`·`/`·`#` 이 있어 Mermaid 상자 이름을 따로 만들어야 한다.
- 논문 주장이 철회되면 우리 하류에 [변경] 을 내는 것(`mapstale --lit`)은 3판 — 지금은 `litcheck` 의 [참고] 한 줄과 `impact --lit` 로 사람이 본다.
