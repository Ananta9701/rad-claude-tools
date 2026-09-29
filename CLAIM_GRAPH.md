# 주장 의존 그래프 규약 (claim_graph.py) — 발표·저자·리뷰어 공용 v15.8.4

문서(슬라이드·원고·심사 회신)를 **주장 단위의 그래프**로 먼저 적고, 문서는 그 그래프의
표현으로 다룬다. 그래프가 원본(source)이고 문서는 뷰(view)다. 고칠 때는 그래프부터 고친다.

세 프로젝트가 같은 파일(`claim_graph.py`)과 같은 `claims.json` 규약을 쓴다.
다른 것은 자리(site)를 읽는 방법뿐이다.

| 프로젝트 | 자리 표기 | resolver |
|---|---|---|
| 발표 | `slide@ID`, `notes@ID` (권장, sldId 기준) / `slide:N`, `notes:N` (파일 번호 — PowerPoint 저장 시 깨짐, `mapcheck --to-sldid` 로 변환) | `deck_toolkit` 이 제공 (CLI 도 deck_toolkit 이 같은 명령을 가짐) |
| 저자 / 리뷰어 | `doc:find:<문구>` (권장), `doc:sec:<절 제목>`, `doc:tbl:N`, `doc:p:N` | `claim_graph.DocSource(docx|md|txt)` |

`doc:p:N` 은 문단 삽입에 밀린다. `doc:find:` 는 그 문구가 **한 문단에만** 있어야 하며
둘 이상이면 모호함 오류를 낸다 — 이것이 의도다. **`doc:tbl:N`·`doc:p:N` 의 N 은 1부터 센다**(v15.5 명시 —
0부터로 썼다가 실패한 사례).

`rebuttal` 역할(리뷰어가 저자가 안 쓴 한계를 적는 노드)은 sites·keys 를 비워 두는 것이 **의도된 조합**이다.
`mapcheck` 는 keys 가 비면 그 노드를 검사하지 않고, sites 가 없으면 자리 검사도 없다 — "원고에 없는 것"을
적는 노드이므로 원고에서 찾을 수 없는 것이 정상이다. 앞으로 "rebuttal 에도 sites 를 넣어라"는 검사를 추가하지 않는다.

---

## 1. 왜 "문서의 알고리즘화"가 아니라 "주장 그래프"인가

문서 전체를 논리식으로 바꾸는 것은 안 된다. 같은 뜻을 다른 말로 쓴 것을 코드가 모르고,
한 문장이 여러 주장을 담기도 하며, 논증 구조 자동 추출(argument mining)은 연구 단계다.
되는 것은 두 가지다.

1. **사람이 주장 10개 안팎을 그래프로 적는다** — 이 문서화가 곧 논리 구조이며 생각 정리다.
2. 그 뒤부터는 코드가 **기계적인 것**을 맡는다: 빠진 자리, 철회 잔재, 상류 변경의 하류 전파,
   검증 이후 무엇이 바뀌었는지.

`extract` 는 1 을 돕는 **초안**일 뿐이다. 이 덱에서 사람이 쓴 주장 10개 중 4개만 후보에
잡혔다(수치·인용이 있는 것만). 판독 논리("석회 위치가 tip 이면 류마티스성")처럼 숫자 없는
주장은 못 잡는다. 초안이 빈 파일보다 빠르다는 것이 전부다.

## 2. 가져온 개념

| 소프트웨어 | 여기 |
|---|---|
| 빌드 시스템(make/Bazel): 의존 DAG + 내용 해시, 바뀐 것과 하류만 재빌드 | `mapfreeze` / `mapstale` |
| 요구사항 추적(DOORS)의 suspect link: 상류가 바뀌면 사람이 풀 때까지 의심 | `mapstale` 의 [필수]/[참고], `mapfreeze` 로 해제 |
| 스프레드시트 재계산: 위상 순서, 순환 참조는 기본 오류 | `impact`, `mapgraph`, `anchor` |
| ADR: 결정을 지우지 않고 superseded 로 남김 | `status`, `supersedes` |
| 원본→생성물(single source of truth, docs-as-code) | `scaffold` — 그래프에서 문서 뼈대를 낸다 |

## 3. claims.json

```json
{
  "doc": "DOC_Manuscript_v37",
  "claims": [{
    "id": "cond-up",
    "statement": "병변 내부 지표 X 가 정상 조직보다 높다",
    "evidence": "Table 2, 0.80 vs 0.70, P = 0.004 (n = 40)",
    "role": "claim",
    "status": "accepted",
    "sites": ["doc:find:index X was higher", "doc:sec:Discussion"],
    "keys": ["higher index X", "increased index X"],
    "forbidden": ["index X was unchanged"],
    "supersedes": {"statement": "지표 X 차이는 유의하지 않다", "retracted": "2026-08-30"},
    "depends_on": [{"id": "fa-down", "type": "context", "weight": 0.3}],
    "anchor": false
  }]
}
```

| 항목 | 뜻 |
|---|---|
| `statement` | 한 문장 주장. 두 주장이면 둘로 쪼갠다 |
| `evidence` | 근거 위치와 수치, 표본 크기 |
| `role` | `main`(문서당 하나) / `evidence`(Results) / `claim`(Discussion 보조 주장) / `background`(Introduction) / `method` / `caveat`(Limitations) / `rebuttal` |
| `section` | 자유 문자열. 어느 절에서 왔는지 |
| `status` | `accepted` / `proposed`(근거 미확인) / `superseded`(철회, sites 불가) |
| `sites` | 이 주장이 실리는 자리 전부 |
| `keys` | 그 자리에 있어야 할 표현 (하나라도 있으면 통과). 3~4개 |
| `forbidden` | 있으면 안 되는 표현 — 철회한 옛 주장의 문구 |
| `supersedes` | 철회한 옛 주장 원문과 날짜 |
| `depends_on` | **"내가 저 주장에 기댄다"** 방향. `type` premise 1.0 / support 0.7 / caveat 0.5 / context 0.3. **caveat 도 같은 방향**: 한정되는 주장(evidence·claim)이 caveat 주장을 자기 depends_on 에 적는다 — "이 한계 아래에서 성립". v13 의 덱 그래프는 반대로 적혀 있어 v14 에서 고쳤다 |
| `confidence` | `high` 이 자료로 재현됨 / `mid` 자료가 방향은 지지 (기본값) / `low` 미검정·외부 근거·미해결. **주장 자체의 근거 강도.** 덱에서는 high=원전 절·문단 + 본 증례 영상 확인 / mid=원전 확인 / low=미확인·문헌 갈림 |
| `anchor` | 순환에 속한 주장 중 하나. 검토의 시작점=끝점 |
| `verified` | `mapfreeze` 가 쓴다. 손으로 쓰지 않는다 |

**v15: weight 는 type 기본값으로 고정한다.** premise 1.0 / support 0.7 / caveat 0.5 / context 0.3 — 손으로 0.9·0.6 을
넣지 않는다(넣으면 mapgraph [참고]). weight 는 "저것이 무너지면 나도 무너지는가"(의존 강도)만 뜻하고,
"저것이 얼마나 확실한가"는 그 주장의 `confidence` 에 적는다. 심사 회차 1~3 에서 철회·수위 조정된 주장은
전부 weight 높고 confidence 낮은 것이었다 — 그 조합을 mapgraph 가 **약한 고리**로 나열한다.
`impact` 는 confidence 를 전파에 쓰지 않고 표시만 한다.

## 3-1. mapgraph 가 잡는 것 (v14)

[필수] = 통과 못 함, [참고] = 사람이 볼 것.

| 판정 | 내용 |
|---|---|
| 필수 | depends_on 의 id 가 없음 / type·status·role 값 오류 / weight 범위 밖 / id 중복 |
| 필수 | 순환인데 anchor 가 정확히 하나가 아님 |
| 필수 | superseded 인데 sites 가 남아 있음 |
| 필수 | `supersedes` 가 있는데 `forbidden` 이 비어 있음 — 옛 문구가 그대로 통과하는 구멍. 옛 statement 에서 뽑은 후보 어구를 같이 낸다 |
| 참고 | forbidden 이 있는데 supersedes 기록이 없음 |
| 참고 | role=main 이 문서당 하나가 아님 |
| 참고 | role=main/claim 인데 premise 간선이 없음 — 검정 없는 해석이 결론 자리에 앉았는지 |
| 참고 | role=evidence 인데 caveat 간선이 없음 — 한계가 하나도 안 걸린 근거 |
| 참고 | extract 가 만든 proposed 후보가 확정되지 않음 |
| 참고 | **약한 고리**: premise/support 간선의 상류가 confidence=low. weight 내림차순 |
| 참고 | 간선 weight 가 type 기본값이 아님 |
| 참고 (`mapcheck --nums`) | evidence 의 수치 토큰이 sites 어디에도 없음. 소수·%·4자리 이상은 항상, 1~3자리 정수는 n=·±·vs·/ 문맥일 때만(참고문헌 번호 제외). 표기 차이(0.541 vs 0.54)는 잡고 반올림 판단은 사람. **`--nums` 는 "evidence 에 적은 수치가 원고 자리에 실제로 있는가"만 본다** — 리뷰어 그래프처럼 evidence 에 재현값·외부 수치를 함께 적는 용법에서는 참고 건수가 높게 나오는 것이 정상이며 결함이 아니다(v15.4.3; 리뷰어 56 주장 중 35건 실례). 원고 인용 수치만 검증하려면 그 수치만 evidence 에 두고 재현값은 note 등 다른 필드에 둔다 |

## 4. 명령

pptx 는 `deck_toolkit.py <명령> deck.pptx --claims ...`, docx/md 는 `claim_graph.py <명령> doc ...`.

| 명령 | 언제 | 무엇 |
|---|---|---|
| `extract doc -o draft.json` | 새 문서, 관계도 없음 | 수치·인용·방향어·대조어 문장을 후보로. status=proposed, origin=extract |
| `mapgraph --claims` | 관계도를 쓰거나 고친 직후 | 없는 id, 순환(anchor), superseded 잔여 자리, 검토 순서 |
| `scaffold --claims` | 문서를 쓰기 전 | 자리 순으로 "여기에 실릴 주장" 목록 — 이 순서로 쓴다 |
| `selfcheck [--dir /mnt/project] [--tests]` | **세션 시작** | 세트 3단계 확인(manifest 판·파일별 판·해시) + 테스트 + 프로젝트 파일 분류 (a)(b)(c). 출력 표를 도구회신 §1 에 그대로 붙인다(v15.6). `②′` 행은 세트 해시를 RELEASE §3 표와도 대조한다(v15.6.1). 세 프로젝트 모두 이 파일이 있어서 여기에 둔다. **GitHub 에서 받은 전체 세트는 `--role 발표|저자|리뷰어` 로**(v15.7) — 추정하지 않고 그 역할의 파일만 보며, 안 쓰는 도구는 삭제 후보로 올리지 않는다. `--compare /mnt/project` 는 예비로 둔 프로젝트 파일과 판·해시를 대조한다. `git clone` 으로 받은 폴더면 받은 커밋 해시를 표에 적는다(v15.8) |
| `impact --claims <id> [--sites]` | 주장을 뒤집기로 결정 | 다시 볼 하류 주장과 자리. `--sites` 면 [필수] 자리만 한 줄에 하나(v15.5, 목록 대조용) |
| `mapcheck doc --claims [--nums] [--nums-sep "|"]` | 자리를 다 고친 뒤 | keys/forbidden 대조 + 그래프 검사. `--nums` 면 evidence 수치가 자리에 있는지도. `--nums-sep` 은 evidence 에서 그 구분자 **앞쪽만** 검사(v15.5) — "원고 값 | 재현 값" 용법용, 구분자는 사용자가 선언한다 (교정용, 심사 형식 지적의 대부분이 이 유형) |
| `mapfreeze doc --claims -o` | 검증을 **실제로** 마친 뒤 | 해시 기록 = "확인했다" 선언 |
| `mapstale doc --claims` | 그 뒤 어떤 편집이든 한 뒤 | [변경] 주장, [필수]/[참고] 하류, 기록 없는 새 주장. v15.5: freeze 가 `verified.keys` 해시를 함께 적어 **keys 만 바꾼 그래프도 [변경]**(구판 freeze 는 그 해시가 없어 검사 안 함). 출력 끝에 "실제로 바뀐 주장의 자리(직접)"를 하류 전파와 구분해 낸다 |
| `mapdiff a.json b.json --labels 저자 리뷰어 [--pairs a1=b1,…]` | 독립으로 쓴 두 그래프 대조 | sites·keys 겹침으로 짝지어 (a) 양쪽 (b) 한쪽만 (c) 다른 쪽만, 간선 type·weight 차이, caveat 부착 차이. 간선·caveat 차이 줄의 **`?` 접두는 상대 그래프에 짝이 없는 노드 id** 를 뜻한다(v15.4.3 문서화) — 예 `?within-participant-design` 은 그 노드가 (b)/(c) 목록에 있다는 신호이므로 먼저 `--pairs` 로 짝을 확인한다. v15.4: role 계열(claim/evidence/caveat/…)이 다르면 짝짓지 않음. **명명만 다른 주장은 자동으로 못 잡는다** — (b)(c)가 크면 사람이 짝을 만들어 `--pairs`로 넘긴다. **반대 방향 오류도 있다**(v15.4.4): 의미상 대응하는 두 주장의 role 을 서로 다르게 쓰면(한쪽 main, 다른 쪽 claim) 같은 계열이라 짝지어져 (a) 에 들어가고, 그 상대의 진짜 짝은 (c) 에 남는다 — (a) 목록도 id 쌍을 눈으로 보고 어긋난 쌍은 `--pairs` 로 고정한다(실물: 저자 `group-a-b-distinct`(main) ↔ 리뷰어 `claim-mechanism-x`(claim)) — 문자열 `a1=b1,a2=b2`, json 파일 `{"a_id": "b_id"}`, 또는 한 줄에 `a_id=b_id` 인 텍스트 파일(v15.4.1). **1:N 짝**은 같은 a_id 를 반복(`s10=nested,s10=delta-r2`) 또는 json 값을 리스트로 — 한쪽이 한 노드로 묶은 것을 다른 쪽이 둘로 나눈 경우(v15.5), 출력에 `nested+delta-r2` 로 표시 |
| `remap-refs --claims X.json --map refmap.json -o Y.json [--force]` | 참고문헌 재번호 뒤 | `verify_toolkit renumber` 가 낸 매핑으로 statement·evidence 의 `[n-m]`·keys 의 `refs n-m` 치환. `mapcheck` 는 `refs n-m` key 를 리터럴이 아니라 인용번호로 보고 자리의 대괄호 인용(`[26-28]`·`[26–28]`·`[24,26-28]`)을 펼쳐 대조한다(v15.4.2) — **그래프의 `doc` 이 가리키는 판의 번호 체계에 맞는 매핑만** 적용할 것. keys 의 순수 숫자("42", "29-31")는 **어떤 옵션으로도 건드리지 않는다**(v15.4.1 — 실물에서 참여자 수 42 가 바뀔 뻔함) — 인용번호 key 는 `refs 29-31` 로 쓸 것. 적용한 매핑을 상위 `refs_maps_applied` 에 기록하고 같은 매핑을 두 번 적용하려 하면 중단(`--force` 로 강행). **손으로 재번호한 그래프에는 표지가 없으므로 돌리지 말 것** — 돌리면 한 단계 더 밀린다. verified 있는 주장이 바뀌면 mapfreeze 재실행 경고 |

## 5. 작업 순서

**제출 전 체크리스트 (v15.4, 도구회신 #15).** `mapcheck` 통과는 freeze 가 아니다. `mapcheck` 는 "자리가 존재하고 keys 가 있는가"만 보고,
내용 변경은 `mapfreeze` 로 기록된 해시를 `mapstale` 이 비교할 때만 잡힌다. 제출·심사 전달 순서:
`mapgraph` → `mapcheck --nums` → `mapfreeze -o` → `mapstale` "바뀐 것 없음" → 그 파일을 낸다. 이 순서를 건너뛴 그래프는 심사에서 mapstale [변경]이 수십 건 뜬다(회차 4 실례 33건).

**anchor 규칙 (v15.4, 도구회신 #5·#10).** `doc:find:` 는 anchor 문구를 **포함한 문단 전체**를 자리로 잡고 `mapfreeze` 는 그 문단 전체를 해시한다.
따라서 freeze 된 그래프라면 anchor 뒤쪽 문장이 붕괴·삭제돼도 `mapstale` 에 [변경]으로 잡힌다. 못 잡는 것은 `mapcheck` 다 —
mapcheck 는 존재 검사이므로 anchor 만 살아 있으면 통과한다. 수치 없는 서술 주장은 `--nums` 도 도움이 안 되므로,
anchor 는 주장의 **핵심 서술이 담긴 절**을 잡고(문단 첫 구절만 잡지 말 것), 편집 후 검사는 mapcheck 가 아니라 mapstale 로 한다.

**doc / deck 키 (v15.4, 도구회신 #14).** 원고 그래프의 상위 키는 `doc`, 덱 그래프는 `deck`. `mapfreeze` 는 상위 키(`version`·`protocol` 등)를 전부 보존하고
`doc` 을 freeze 대상 문서명(경로·`__N_`·확장자 제거, §3 예시와 같은 형식)으로 갱신하며, 원고 그래프에 stale `deck` 이 있으면 제거하고 경고한다. `mapstale` 은 그래프의 `doc` 과 대상 파일명이 다르면 경고한다.

새 문서: `extract` → 초안을 사람이 확정(지우고·합치고·keys 넣고·depends_on 그리기) →
`mapgraph` → `scaffold` 순서로 문서 작성 → `mapcheck` → `mapfreeze`.

기존 문서 수정: claims.json 을 먼저 고친다(옛 statement 를 `supersedes` 로, 옛 문구를
`forbidden` 으로) → `impact <id>` → 그 자리를 고친다 → `mapcheck` → `mapfreeze`.
그 뒤에는 `mapstale` 이 "바뀐 것 없음"이면 다시 검증하지 않는다.

**필드 규칙이 바뀌면 freeze 를 다시 한다.** `verified` 해시는 statement·evidence·자리 텍스트만 본다. confidence·weight·
간선·**keys** 를 고친 것은 `mapstale` 에 안 잡히므로(freeze 뒤 keys 만 바꾼 그래프는 mapstale 0 이면서 mapcheck 실패가 가능 — 두 명령을 항상 같이 돌린다), 규약 판이 올라가 그런 필드를 손댔으면 `mapgraph` → `mapfreeze` 를 다시 돌린다.

리뷰어 프로젝트: 원고를 **독립으로** 읽어 자기 claims.json 을 쓴다(REVIEW_PROTOCOL §7). 저자 그래프와
세 가지가 다르다 — evidence 에는 원고 값이 아니라 재현 값을 적고(재현 안 되면 proposed), 저자가 쓰지 않은
한계를 `rebuttal` 역할로 추가하며, 결론 문장마다 evidence 로 가는 premise 간선이 없으면 "근거 초과" 지적이다.
2차 조정에서 `mapdiff 저자.json 리뷰어.json` 이 (a)(b)(c) 표를 낸다. "반영했다" 항목은 해당 주장의 `sites`
를 `mapcheck` 로, 수치는 `locate` 로 확인한다.

## 5-2. 블라인드 규칙 — 회신 문서를 둘로 나눈다

2026-09-08 에 발표 프로젝트의 회신(도구 설명 + 원고 구조 판단이 한 문서)이 리뷰어 프로젝트에 1차 심사 전에
들어갔다. 원인은 문서 분리를 안 한 것이다. 앞으로:

- **도구 회신**(규약·코드·테스트·파일 배치)과 **내용 회신**(특정 원고의 주장·약한 고리·자리 목록)을 별도 파일로 낸다.
  내용 회신 파일명에 원고 버전을 넣는다(`..._{원고}_v44_...`). 도구 회신에는 원고의 주장 id·statement 를 예시로도 싣지 않는다.
- 리뷰어 프로젝트에는 도구 회신·claim_graph.py·CLAIM_GRAPH.md·test_claim_graph.py 만 올린다. 저자 측 claims.json·
  원문_주장대조·내용 회신은 **그 회차 1차 회신 이후** 대화 업로드로만 연다.
- 규약·코드 진본은 **코드 프로젝트**(2026-09-08 릴리스 v1 이후; 그 전에는 발표 프로젝트). 저자·발표·리뷰어 사본은 코드 프로젝트가 릴리스 노트로 배포하고, 각 프로젝트는 `TOOLS_MANIFEST` 의 해시와 대조한다.
- **파일명으로 걸러진다**: 내용 회신 `{YYMMDD}_내용회신_{원고}_v{N}_{주제}_v{M}.md`, 도구 회신 `{YYMMDD}_도구회신_{주제}_v{M}.md`.
  리뷰어 프로젝트는 `내용회신` 이 들어간 파일을 1차 회신 전에 열지 않는다 — 내용을 읽지 않고도 판단된다.
- 프로젝트별 파일 소속표는 `TOOLS_MANIFEST` §2 (도구 파일). 원고·회신 등 비도구 파일의 소속은 각 프로젝트 지침.

## 5-1. 논문을 그래프로 읽는 절차 (IMRaD)

논문은 구조가 정해져 있어 역할이 절에서 거의 그대로 나온다. 읽는 순서는 절 순서가 아니라 **주장 순서**다.

1. **Abstract Conclusion + Discussion 첫 문단 + 마지막 결론 문단**에서 `main` 하나를 뽑는다. 둘이면 하나로 합치거나 하나를 `claim` 으로 내린다
2. **Results** 의 수치 있는 문장을 `evidence` 로. 표(`doc:tbl:N`)를 자리로 같이 건다. statement 에 수치·효과크기·P 를 넣는다
3. **Discussion** 의 해석 문장을 `claim` 으로. 각 `claim` 이 어느 `evidence` 에 기대는지 `premise/support` 로 긋는다
4. **Introduction** 의 문헌 전제를 `background` 로. `claim` 이 그것에 기대면 `context` 또는 `premise`
5. **Methods** 에서 설계 결정(paired 비교, covariate, 역치 정의, 표본)을 `method` 로. 결과가 그 설계에 기대면 `context`
6. **Limitations** 의 문장 하나하나를 `caveat` 로. 한정되는 `evidence`/`claim` 쪽 depends_on 에 `caveat` 간선을 적는다. **한계가 어디에도 걸리지 않으면 그 한계는 문서 안에서 아무것도 좁히지 않는 것**이고, 어떤 근거에 한계가 하나도 안 걸리면 그 근거는 의심해 볼 자리다
7. `mapgraph` 로 검토 순서를 뽑고, `main` 에서 위로 거슬러 **가장 약한 고리**(weight 높은데 caveat 이 걸린 전제)를 본다

한 원고(v44)에서 이 절차로 37개 주장, 43개 간선이 나왔다(v13 기준 초안; 저자 확정본 v3 는 39·60). `extract` 는 188개 후보를 내어 그중 27개가
사람 주장과 겹쳤다 — 재현율은 쓸 만하지만 후보 5개 중 4개는 버려야 한다.

다시 읽을 필요가 없어지는가: **부분적으로.** `mapstale` 은 바뀐 자리와 그 하류를 가리키므로 전체를 다시 읽지
않아도 된다. 그러나 statement 는 사람이 쓴 요약이라, 자리 텍스트가 바뀌면 그 자리는 사람이 다시 읽고
statement 를 고쳐야 한다. 줄어드는 것은 "전체 재독"이지 "재독"이 아니다.

## 6. 순환

서로 기대는 주장은 대개 순환 논증이라 `mapgraph` 가 오류로 낸다. 정말 상호 지지라면
한 쪽에 `anchor: true` 를 둔다. anchor 가 순환 안쪽으로 기대는 간선을 끊어 anchor 에서
시작해 한 바퀴 돌고 anchor 에서 끝난다. anchor 가 없거나 둘 이상이면 통과하지 않는다.

## 7. 한계

- 화살표는 사람이 그린다. 빠뜨린 관계는 도구가 모른다. 자리 누락은 `mapcheck` 의
  [참고]로 잡지만 주장 사이의 빠진 화살표는 못 잡는다
- `keys`/`forbidden` 은 문자열 일치다
- 해시는 오타 수정에도 [변경]으로 뜬다. 위양성을 감수한 설계다. 단 v15.2 부터 대괄호 인용번호([12], [15,16], [29-31])는 빼고 잰다 — 참고문헌 재번호는 주장을 바꾸지 않는다
- `extract` 는 초안이다. 덱 4/10, 원고 27/37(후보 188개). 숫자 없는 해석·배경·방법 문장은 잘 못 잡는다
- `mapfreeze` 를 확인 없이 돌리면 이 장치 전체가 무의미하다

## 8. 테스트

`test_claim_graph.py` 가 claim_graph.py 단독 테스트(개수는 manifest §1, `python3 test_claim_graph.py` 로 pytest 없이 돈다 — 표준 라이브러리 + python-docx 만). 저자·리뷰어 프로젝트에도 넣는다.
발표 프로젝트의 `test_toolkit.py` 는 이것을 import 해 함께 돈다(개수는 manifest §1). `claim_graph.py` 는 코드 프로젝트에서만 고치고, 세 프로젝트 사본은 릴리스로 교체한다.

변경 이력은 코드 프로젝트 `HISTORY.md`. v15.6.1 (2026-09-23): selfcheck 가 테스트를 `PYTHONDONTWRITEBYTECODE=1` 로 띄우고 RELEASE §3 과 교차 대조(②′). 테스트 수는 manifest §1 이 진본(release.py 가 센다). v15.6 (2026-09-23): `selfcheck` 신설 — 세션 시작 확인을 한 명령으로. 테스트 33개. v15.5.2 (2026-09-22): mapgraph 가 keys∩forbidden 을 경고(발표 T2 — 자리 통과·금지 실패가 동시에 나면 statement 가 낡은 것). 테스트 32개. v15.5.1: 덱 사이트 `slide@ID` 문법 문서화(코드는 deck_toolkit 16.7). v15.5 (2026-09-13): `--nums-sep`, 1:N `--pairs`, `verified.keys` 해시, mapstale 직접/하류 구분, `impact --sites`, `doc:tbl` 1-based·rebuttal 의도 명시.

v15 에서 `confidence` 와 `mapcheck --nums` 채택 (저자 프로젝트 도구회신 `260908_도구회신_confidence채택_v1` 근거).
