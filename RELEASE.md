# RELEASE v2.45 — manifest v65 — 2026-09-28

> **v2.45** — `literature.py` 0.5. `oa --fetch` 첫 실시험(코드 세션, 09-28 — 네트워크 허용 뒤)에서 찾은 표 결함 2개: Europe PMC 전문 XML 의 표에서 **세로로 합쳐진 칸 뒤 행이 한 칸씩 밀렸고**(표 수치를 다른 열로 읽을 위험), **칸 안 줄바꿈이 붙어 버렸다**(`p = 0.076Adj p`). 이전 판 내용은 `HISTORY.md`.

## 1. 바뀐 것

| 도구 | 판 | 내용 |
|---|---|---|
| `literature.py` | 0.5 | `oa` 의 JATS 표 → md: 세로 병합(rowspan)은 아래 행마다 값을 채움, 가로 병합(colspan)은 빈 칸으로 열 수를 맞춤, 칸 안 `<break/>` 는 ` / `. 병합은 그 표 안에서만 이어지고, 숫자가 아닌 span 은 1 로 본다 |
| `LITERATURE.md` | 0.5 | `oa` 표 한 줄 |
| `test_literature.py` | 0.5 | 시험 1개(성공: 병합·줄바꿈 표가 모든 행 같은 칸 수 · 실패: 표보다 긴 rowspan 이 다음 표로 새지 않음, 숫자 아닌 span) |

## 2. 회신 항목별 답

| 항목 | 반영 |
|---|---|
| 코드 09-28 `oa --fetch` 첫 실시험 — 결함 후보 2(병합 칸 밀림, 줄바꿈 붙음) | 재현(고치기 전 코드에서 Rt 행 3칸·`0.076Adj`) → 고침. 같은 논문의 실제 Europe PMC XML 로 다시 확인: 표마다 행의 칸 수가 한결같다(5칸 13행·8칸 40행) |
| 사용자 09-28: 병합 칸은 행마다 값을 채우고 줄바꿈은 공백이나 ` / ` | ` / ` 로 |

## 3. 받을 파일

**zip 없음.** 코드 세션이 공개 저장소(`rad-claude-tools`)와 비공개 저장소(`rad-claude-private`)에 직접 올린다.

<!-- sets:begin — release.py 가 만든다. 손으로 고치지 않는다 -->
### 저자 (7)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `claim_graph.py` | v15.8.2 | `14e977e99a39` | — |
| `test_claim_graph.py` | v15.8.2 | `bd5f5c99691a` | — |
| `CLAIM_GRAPH.md` | v15.8.2 | `a2d9f4dd1749` | — |
| `verify_toolkit.py` | v1.3.4 | `e703af6d5418` | — |
| `test_verify_toolkit.py` | v1.3.4 | `aba65de39d87` | — |
| `TOOLS_MANIFEST.md` | v65 | `f85af79a86dd` | ○ |
| `RELEASE.md` | v2.45 | — | 이 문서 |

### 발표 (11)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `claim_graph.py` | v15.8.2 | `14e977e99a39` | — |
| `test_claim_graph.py` | v15.8.2 | `bd5f5c99691a` | — |
| `CLAIM_GRAPH.md` | v15.8.2 | `a2d9f4dd1749` | — |
| `deck_toolkit.py` | v16.37 | `75507c4a9834` | — |
| `test_toolkit.py` | v16.37 | `4a9355ac210d` | — |
| `DECK_SPEC.md` | v16.37 | `d5b88da3990f` | — |
| `handoff.py` | v2.0 | `642269d51cc5` | — |
| `test_handoff.py` | v2.0 | `3c660a5a654c` | — |
| `HANDOFF_FORMAT.md` | v2.0 | `577b9f35e9d9` | — |
| `TOOLS_MANIFEST.md` | v65 | `f85af79a86dd` | ○ |
| `RELEASE.md` | v2.45 | — | 이 문서 |

### 리뷰어 (6)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `claim_graph.py` | v15.8.2 | `14e977e99a39` | — |
| `test_claim_graph.py` | v15.8.2 | `bd5f5c99691a` | — |
| `CLAIM_GRAPH.md` | v15.8.2 | `a2d9f4dd1749` | — |
| `REVIEW_PROTOCOL.md` | v7.2 | `7f6e413d4d48` | — |
| `TOOLS_MANIFEST.md` | v65 | `f85af79a86dd` | ○ |
| `RELEASE.md` | v2.45 | — | 이 문서 |

### 교과서 (5)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `textbook.py` | v0.6 | `505e14289fd2` | — |
| `test_textbook.py` | v0.6 | `29298da49346` | — |
| `TEXTBOOK.md` | v0.6 | `f8dd10b4611d` | — |
| `TOOLS_MANIFEST.md` | v65 | `f85af79a86dd` | ○ |
| `RELEASE.md` | v2.45 | — | 이 문서 |

### 문헌 (5)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `literature.py` | v0.5 | `9a4167578ad4` | ○ |
| `test_literature.py` | v0.5 | `30c01cdb3ac1` | ○ |
| `LITERATURE.md` | v0.5 | `ce1ea0cade3d` | ○ |
| `TOOLS_MANIFEST.md` | v65 | `f85af79a86dd` | ○ |
| `RELEASE.md` | v2.45 | — | 이 문서 |

### 코드 (25)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `claim_graph.py` | v15.8.2 | `14e977e99a39` | — |
| `test_claim_graph.py` | v15.8.2 | `bd5f5c99691a` | — |
| `CLAIM_GRAPH.md` | v15.8.2 | `a2d9f4dd1749` | — |
| `deck_toolkit.py` | v16.37 | `75507c4a9834` | — |
| `test_toolkit.py` | v16.37 | `4a9355ac210d` | — |
| `DECK_SPEC.md` | v16.37 | `d5b88da3990f` | — |
| `verify_toolkit.py` | v1.3.4 | `e703af6d5418` | — |
| `test_verify_toolkit.py` | v1.3.4 | `aba65de39d87` | — |
| `handoff.py` | v2.0 | `642269d51cc5` | — |
| `test_handoff.py` | v2.0 | `3c660a5a654c` | — |
| `HANDOFF_FORMAT.md` | v2.0 | `577b9f35e9d9` | — |
| `textbook.py` | v0.6 | `505e14289fd2` | — |
| `test_textbook.py` | v0.6 | `29298da49346` | — |
| `TEXTBOOK.md` | v0.6 | `f8dd10b4611d` | — |
| `literature.py` | v0.5 | `9a4167578ad4` | ○ |
| `test_literature.py` | v0.5 | `30c01cdb3ac1` | ○ |
| `LITERATURE.md` | v0.5 | `ce1ea0cade3d` | ○ |
| `REVIEW_PROTOCOL.md` | v7.2 | `7f6e413d4d48` | — |
| `TOOLS_MANIFEST.md` | v65 | `f85af79a86dd` | ○ |
| `CODE_PROJECT_README.md` | v5 | `cbffb6ca85db` | — |
| `HISTORY.md` | — | `e9066193817e` | ○ |
| `release.py` | — | `a5dad4e3e398` | — |
| `GITHUB_README.md` | — | `c81d29504e46` | — |
| `PRIVATE_TERMS.txt` | — | `6e8c2862cf5e` | — |
| `RELEASE.md` | v2.45 | — | 이 문서 |
<!-- sets:end -->

## 4. 각 프로젝트 대화창이 첫 세션에서 할 일

1. 리뷰어·문헌(Cowork): selfcheck 로 manifest v65 이상·literature 0.5 확인. **v0.4 `oa` 로 받은 paper.md 중 표가 있는 것은 표 수치를 쓰기 전에 다시 받는다**(`oa --fetch` 를 그 DOI 폴더를 비우고 다시 — 보관소 파일은 사용자 허용 뒤에). 지금까지 `oa` 로 받은 실물은 코드 세션 시험 1편뿐이라 보관소에는 없을 것으로 본다(확인 안 함).
2. 다른 역할: 할 일 없음.

## 5. 검증하지 않은 것

- 병합이 여러 겹인 복잡한 표(가로·세로 병합이 한 칸에 함께 있는 것)는 시험 표 1개와 실물 1편으로만 확인했다.
