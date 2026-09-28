# RELEASE v2.39 — manifest v59 — 2026-09-28

> **v2.39** — **v2.38 을 포함한다**(v2.38 은 GitHub 에 올리지 않은 채 이 판으로 넘어간다 — v2.38 zip 은 버린다). 더한 것: 리뷰어의 문헌 시험 회신 4건 — `literature.py` 0.2·`LITERATURE.md` 0.2. 이전 판 내용은 `HISTORY.md`.
> 병원 컴퓨터 첫 시험(09-28): Windows Cowork 는 PC 에서 셸이 돌지 않고(클라우드 작업공간), Drive 가상 드라이브(`G:\`) 연결 거절, PubMed·PMC 캡차, doi.org(출판사)는 통과·PDF 는 사람 손으로 5–6 번 만에. 리뷰어가 **경로 (b)**(사용자가 PDF 를 Drive inbox 에, 리뷰어가 Drive 연결로 직접 읽기)를 시험해 글 근거 주장에는 충분함을 확인. 사용자 결정: 병원 컴퓨터 저장 폴더 `C:\Users\user\Desktop\문헌작업`. **이어진 문헌 Cowork 시험 v2**(07:02): `문헌작업` 폴더는 연결됨, 무료 공개 논문 1편을 앱 내장 브라우저로 받음, Wiley(구독)는 봇 확인에서 멈춤 → 사용자가 받음. 2/2 확보.

## 1. 바뀐 것 — v2.39 에서 더한 것

| 도구 | 판 | 내용 |
|---|---|---|
| `literature.py` | 0.2 | 쪽마다 붙는 **출판사 다운로드 안내 줄**(기관·날짜 — Wiley 등)을 paper.md 에서 뺌. `check` 가 사용자가 받은 이름(저장 이름이 아닌 것)도 DOI·제목으로 짝지어 대조. `locate`: 주장마다 **원문 전체에서 0회인 찾을 말** 한 줄, **찾을 말별 첫 자리**(요약 문단 편향을 피해 — 같은 문단이면 한 번만). `plan`: 찾을 곳 순서 doi.org → "(안 되면)" PMC → PubMed 는 DOI·PMC 가 없을 때만, 머리에 받기 규칙(쿠키 배너·최대 3 번·멈춤 기록). 새 `check`: 받은 파일 검사(`%PDF`·쪽 수 > 1·앞쪽 DOI 가 그 문헌 것인지) |
| `test_literature.py` | 0.2 | 6개(+2): 안내 줄 빼기(이름이 다른 파일을 안내 줄의 DOI 로 짝짓기), check 짝짓기, 0회 줄(원고의 97%·PPV 가 원문에 없음), 찾을 말별 자리, check(HTML → ✗, 1쪽 → ✗, 다른 DOI → △, DOI 없음 → △), PubMed 링크를 DOI 있을 때 안 줌 |
| `LITERATURE.md` | 0.2 | 병원 컴퓨터 현실에 맞춰 다시(시험 두 번): 무료 공개는 Cowork 앱 브라우저로 `문헌작업` 에, **구독·봇 확인 사이트는 사용자가 평소 브라우저로 같은 폴더에**, Cowork 가 클라우드 셸에서 check·ingest·locate 하고 **md 만 Drive 로**, 사용자는 PDF 를 Drive inbox 로 한 번에. 리뷰어는 paper.md 로, 표·그림은 PDF(경로 (b)). 받기 규칙 8가지(리뷰어 제안 1·3·4·5 포함), 주장은 요소별 한 행, `> 원고:` 값이 폴더 이름 |

## 1′. v2.38 에서 바뀐 것 (함께 올라간다)

| 도구 | 판 | 내용 |
|---|---|---|
| `deck_toolkit.py` | 16.35 | **K19-1** `fit-layout` 이 하한에서 못 맞춘 화면에도 제목 빼기·이름표(자리·맨 앞)는 적용하고 크기·위치만 건너뛴다. **K19-2** 인용·출처 메모를 그림 설명에서 빼고 우하단·슬라이드 안으로(아래부터 위로 쌓기, 그림이 피할 자리로 먼저), 옮긴 주석·설명이 슬라이드 밖이면 안으로 들이거나 옮기지 않고 알림, 그림 설명 판정 근거 한 줄 |
| `test_toolkit.py` | 16.35 | 181개(+1): 못 맞춘 화면의 제목 뺌·이름표 맨 앞·글자 그대로, 인용·메모는 설명이 아님·우하단·모든 상자 슬라이드 안, 판정 함수 |
| `DECK_SPEC.md` | 16.35 | 판 기록 |

## 2. 회신 항목별 답

| 항목 | 반영 |
|---|---|
| K19-1 못 맞춘 화면도 제목 빼기·이름표 | deck 16.35 — 보고 `[!] … 크기 조정 못 함 · 제목 뺌·이름표만` |
| K19-2 ① 인용·출처 메모는 그림 설명이 아님, 우하단 | deck 16.35 — 판정은 글 모양: 인용(학술지 이름·해;권:쪽·et al·doi), 메모(날짜 6자리로 시작, '출처'·source 로 시작, 또는 60자 이하이면서 '발표'·'선생님'·'강의' — 긴 본문 속 '발표' 는 아님) |
| 리뷰어 `260928_도구회신_GitHub_v2_37미반영_리뷰어_v1` | v2.37 은 그 뒤 GitHub 에 올라갔다(커밋 `1ab9cf9`). 리뷰어의 시험 검증 지시(v1)를 literature.py 0.1 로 읽어 봤다 — 참고문헌 2편(DOI 둘·PMID 하나)·주장 2개 모두 읽힘, 받을 목록 정상. 다시 올릴 필요 없다 |
| K19-2 ② 슬라이드 밖 금지 | deck 16.35 — 안으로 들이거나 옮기지 않고 알림 |
| K19-2 ③ 판정 근거 | deck 16.35 — `설명 판정: "…" — 그림 "…" 과 거리" · 넓이 %` |

## 2. 회신 항목별 답 (v2.39)

| 항목 | 반영 |
|---|---|
| 리뷰어 `260928_도구회신_LITERATURE수령시험_리뷰어_v1` ① 요약 문단 편향 | literature 0.2 — 찾을 말별 첫 자리. 리뷰어 쪽 요소별 행은 LITERATURE §1 에 |
| ② 없는 말이 안 보임 | literature 0.2 — "원문 전체에서 0회" 줄 |
| ③ `> 원고:` 값이 폴더 이름 | LITERATURE §1 한 줄 |
| `260928_도구회신_문헌Cowork시험_막힌곳_리뷰어_v1` ① PubMed 캡차 — doi.org 먼저 | literature 0.2 plan 순서·LITERATURE §2-2 |
| ②③ Windows 셸 없음·G:\ 연결 거절 | LITERATURE §0·§3 다시 — 셸은 선택, 받기·올리기·경로 (b) 가 기본 |
| `260928_도구회신_문헌경로b시험_병원폴더_리뷰어_v1` 경로 (b)·병원 폴더·PMC 캡차 | LITERATURE §0·§4 에 (b) 를 기본으로, `문헌작업` 폴더(Add folder 는 시험 전), PMC 는 "(안 되면)" |
| `260928_도구회신_구독문헌수동받기_관찰_리뷰어_v1` 규칙 1–5 | LITERATURE §2-3·4·5·8, check 명령 |
| 문헌 Cowork `260928_회신_문헌Cowork to리뷰어_…검증시험_v2`(to리뷰어) — 구독 논문 받는 길 (가) 사용자 / (나) 사용자가 봇 확인을 통과시키고 Cowork 재시도 | **(가)** — (나)는 같은 사이트에 자동 요청을 이어 가는 셈이라 약관·기관 차단 위험(코드 판단, 바꾸려면 사용자 결정). LITERATURE §0 3b |
| 같은 회신 — md 는 Cowork 가 Drive 로, PDF 는 크기 때문에 어렵다 | md 만 Cowork 가 Drive(`문헌 보관소`·`Claude 작업/문헌/{원고}`)로, PDF 는 사용자가 원고 단위로 한 번에 Drive inbox 로(§0 5단계) |
| 같은 회신 — Wiley 파일 이름이 저장 이름과 다름 | ingest·check 가 DOI(쪽마다 붙는 안내 줄에도 있다)·제목으로 짝짓는다. 안내 줄은 paper.md 에서 뺀다 |

## 3. 받을 파일

zip 두 개: `v2.39_GitHub.zip`(GitHub 에 전부), `v2.39_코드전용.zip`(코드 프로젝트 파일을 전부 지우고 5개). **v2.38 zip 은 올리지 않는다.**

<!-- sets:begin — release.py 가 만든다. 손으로 고치지 않는다 -->
### 저자 (7)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `claim_graph.py` | v15.8.1 | `dc3ac0780b61` | — |
| `test_claim_graph.py` | v15.8.1 | `bcfe1c1e42d6` | — |
| `CLAIM_GRAPH.md` | v15.8.1 | `ca0bd5652f32` | — |
| `verify_toolkit.py` | v1.3.4 | `e703af6d5418` | — |
| `test_verify_toolkit.py` | v1.3.4 | `aba65de39d87` | — |
| `TOOLS_MANIFEST.md` | v59 | `147b049be459` | ○ |
| `RELEASE.md` | v2.39 | — | 이 문서 |

### 발표 (11)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `claim_graph.py` | v15.8.1 | `dc3ac0780b61` | — |
| `test_claim_graph.py` | v15.8.1 | `bcfe1c1e42d6` | — |
| `CLAIM_GRAPH.md` | v15.8.1 | `ca0bd5652f32` | — |
| `deck_toolkit.py` | v16.35 | `db73b4fbf237` | — |
| `test_toolkit.py` | v16.35 | `494168937ccd` | — |
| `DECK_SPEC.md` | v16.35 | `72444f6dc5b7` | — |
| `handoff.py` | v2.0 | `642269d51cc5` | — |
| `test_handoff.py` | v2.0 | `3c660a5a654c` | — |
| `HANDOFF_FORMAT.md` | v2.0 | `577b9f35e9d9` | — |
| `TOOLS_MANIFEST.md` | v59 | `147b049be459` | ○ |
| `RELEASE.md` | v2.39 | — | 이 문서 |

### 리뷰어 (6)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `claim_graph.py` | v15.8.1 | `dc3ac0780b61` | — |
| `test_claim_graph.py` | v15.8.1 | `bcfe1c1e42d6` | — |
| `CLAIM_GRAPH.md` | v15.8.1 | `ca0bd5652f32` | — |
| `REVIEW_PROTOCOL.md` | v7.2 | `7f6e413d4d48` | — |
| `TOOLS_MANIFEST.md` | v59 | `147b049be459` | ○ |
| `RELEASE.md` | v2.39 | — | 이 문서 |

### 교과서 (5)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `textbook.py` | v0.5 | `5f916620c6c0` | — |
| `test_textbook.py` | v0.5 | `4b2da8dfcecb` | — |
| `TEXTBOOK.md` | v0.5 | `d441d67eea3e` | — |
| `TOOLS_MANIFEST.md` | v59 | `147b049be459` | ○ |
| `RELEASE.md` | v2.39 | — | 이 문서 |

### 문헌 (5)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `literature.py` | v0.2 | `53d931e6aa74` | ○ |
| `test_literature.py` | v0.2 | `d1c764f0d020` | ○ |
| `LITERATURE.md` | v0.2 | `9d1597710d78` | ○ |
| `TOOLS_MANIFEST.md` | v59 | `147b049be459` | ○ |
| `RELEASE.md` | v2.39 | — | 이 문서 |

### 코드 (25)
| 파일 | 판 | 해시 | 변경 |
|---|---|---|---|
| `claim_graph.py` | v15.8.1 | `dc3ac0780b61` | — |
| `test_claim_graph.py` | v15.8.1 | `bcfe1c1e42d6` | — |
| `CLAIM_GRAPH.md` | v15.8.1 | `ca0bd5652f32` | — |
| `deck_toolkit.py` | v16.35 | `db73b4fbf237` | — |
| `test_toolkit.py` | v16.35 | `494168937ccd` | — |
| `DECK_SPEC.md` | v16.35 | `72444f6dc5b7` | — |
| `verify_toolkit.py` | v1.3.4 | `e703af6d5418` | — |
| `test_verify_toolkit.py` | v1.3.4 | `aba65de39d87` | — |
| `handoff.py` | v2.0 | `642269d51cc5` | — |
| `test_handoff.py` | v2.0 | `3c660a5a654c` | — |
| `HANDOFF_FORMAT.md` | v2.0 | `577b9f35e9d9` | — |
| `textbook.py` | v0.5 | `5f916620c6c0` | — |
| `test_textbook.py` | v0.5 | `4b2da8dfcecb` | — |
| `TEXTBOOK.md` | v0.5 | `d441d67eea3e` | — |
| `literature.py` | v0.2 | `53d931e6aa74` | ○ |
| `test_literature.py` | v0.2 | `d1c764f0d020` | ○ |
| `LITERATURE.md` | v0.2 | `9d1597710d78` | ○ |
| `REVIEW_PROTOCOL.md` | v7.2 | `7f6e413d4d48` | — |
| `TOOLS_MANIFEST.md` | v59 | `147b049be459` | ○ |
| `CODE_PROJECT_README.md` | v5 | `fc373977d111` | — |
| `HISTORY.md` | — | `aa2c272f955b` | ○ |
| `release.py` | — | `4befd11f62f2` | — |
| `GITHUB_README.md` | — | `c81d29504e46` | — |
| `PRIVATE_TERMS.txt` | — | `6e8c2862cf5e` | — |
| `RELEASE.md` | v2.39 | — | 이 문서 |
<!-- sets:end -->

## 4. 각 프로젝트 대화창이 첫 세션에서 할 일

1. 리뷰어·문헌 Cowork: 시험 검증지시 v1 의 두 문헌이 `문헌작업` 에 있다 — Cowork 에 **check → ingest → locate → md 를 Drive 로** 를 맡기고(LITERATURE §0 4–5), 사용자는 두 PDF 를 Drive inbox 로. 리뷰어는 문헌목록·paper.md 로 판정해 전체 흐름을 한 번 끝까지.
2. 발표: v2.38 의 K19(아래 v2.38 부분) — v2.39 로 받는다.
3. 저자·교과서: 도구 변경 없음.

## 5. 검증하지 않은 것

- 클라우드 셸이 `문헌작업` 의 PDF 를 올려 ingest 하고 결과를 되쓰는 전 과정, md 를 Drive 로 올리는 것 — 다음 시험(Cowork 회신 v2 는 가능하다고 적었으나 아직 돌리지 않았다).
- 구독 접속(병원 IP)을 Cowork 가 쓸 수 있는지는 여전히 모른다 — 지금 규약은 쓰지 않는다(사용자가 받음).
- `check` 는 fixture 로만. 출판사 다운로드 표지(첫 쪽 앞에 붙는 쪽)가 있으면 DOI 가 앞 두 쪽에 없을 수 있다 — △ 로 나온다.

## v2.38 의 4·5절
 각 프로젝트 대화창이 첫 세션에서 할 일

1. 발표: v6 지시를 판만 올려(도구 v2.38) 그대로 다시 → 대본 v6. 28–32 는 제목 빠지고 이름표만 앞으로, 사용자가 보고 여전히 빽빽한 화면만 영상의학 나누기로.
2. 문헌·리뷰어: v2.37 대로(도구 변경 없음).
3. 그 밖의 프로젝트: 도구 변경 없음.

## 5. 검증하지 않은 것

- 인용·메모 판정은 글 모양 규칙이다 — 학술지 이름이 목록에 없고 해;권:쪽 모양도 아닌 인용은 설명으로 묶일 수 있다. 보고의 '설명 판정' 줄과 '인용·출처' 줄로 사용자가 본다.
- 우하단에 인용을 쌓는 자리가 원래 그 자리에 있던 그림·본문과 겹칠 수 있다 — 그림은 그 자리를 피하지만 본문 글상자는 크기 조정이 된 화면에서만 피한다.
