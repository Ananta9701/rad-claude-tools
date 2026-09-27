# rad-claude-tools

영상의학 작업용 Claude 대화창들이 함께 쓰는 도구와 규약. 개인 작업용이며 공유·재사용을 위한 저장소가 아니다(라이선스 없음).

**이 저장소에는 도구 코드·규약·가짜 fixture 만 둔다.** 환자 정보, 덱·원고·넘김 문서, 교과서와 그 분할본, 사람 이름은 절대 올리지 않는다.
작업 기록(HISTORY)과 개인정보 거르기 목록은 코드 프로젝트에만 있다.

## 세션 시작 — 각 대화창

```bash
rm -rf /tmp/rct && git clone -q --depth 1 https://github.com/Ananta9701/rad-claude-tools /tmp/rct && \
python3 /tmp/rct/claim_graph.py selfcheck --dir /tmp/rct --role 발표 --tests --compare /mnt/project
```

- `--role` 은 그 대화창의 역할: `발표` · `저자` · `리뷰어` · `교과서`(Cowork 가 교과서 폴더에서 — `TEXTBOOK.md`).
- `git clone` 을 쓴다(v2.17~): 대화창·Cowork 클라우드 작업공간·Mac VM 셸 어디서나 되고, 받은 커밋 해시가 selfcheck 표에 남는다.
  (Cowork 클라우드 작업공간은 tarball 주소 `codeload…` 를 세션 권한 문제로 막는다 — 09-26 시험.)
- `--compare /mnt/project` 는 예비로 둔 프로젝트 파일과 판을 대조한다. Cowork 에서는 뺀다(없는 경로).
- 이후 도구는 `/tmp/rct` 에서 쓴다: `python3 /tmp/rct/deck_toolkit.py …`, 스크립트에서는 `sys.path.insert(0, '/tmp/rct')`.
- 결과 표(selfcheck)를 도구회신 §1 에 붙인다. 불일치가 있으면 작업 전에 사용자에게 알린다.

## 역할별로 쓰는 파일

| 파일 | 저자 | 발표 | 리뷰어 | 교과서 |
|---|:-:|:-:|:-:|:-:|
| claim_graph.py · test_claim_graph.py · CLAIM_GRAPH.md | ○ | ○ | ○ | |
| deck_toolkit.py · test_toolkit.py · DECK_SPEC.md | | ○ | | |
| verify_toolkit.py · test_verify_toolkit.py | ○ | | | |
| handoff.py · test_handoff.py · HANDOFF_FORMAT.md | | ○ | | |
| textbook.py · test_textbook.py · TEXTBOOK.md | | | | ○ |
| REVIEW_PROTOCOL.md | | | ○ | |
| TOOLS_MANIFEST.md · RELEASE.md | ○ | ○ | ○ | ○ |

판·해시의 기준은 `TOOLS_MANIFEST.md`, 이번 판에서 바뀐 것은 `RELEASE.md`.

**영상의학(넘김 문서를 쓰는 쪽)**: 넘김 문서 문법은 `HANDOFF_FORMAT.md` —
`https://raw.githubusercontent.com/Ananta9701/rad-claude-tools/main/HANDOFF_FORMAT.md`.
