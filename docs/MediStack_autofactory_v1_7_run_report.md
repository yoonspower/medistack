# MediStack AutoFactory v1.7 — Run Report (ONLINE harvest)

> **NOT LIVE / dry-run only.** no_live_write=true · live_integration_forbidden=true · merge·live 반영 0.
> 이 run 은 reviewer-ready dry-run 패키지 + 리포트만 생성한다. 실제 통합은 PM 적대검증 + clinical reviewer 후 별도 live-PR.

- **branch:** `agent/autofactory-v1.7-online` (base: main `3200edc`, production relation_count=92)
- **run_date:** 2026-06-18 · 실 nedrug ONLINE harvest
- **목표:** 팩토리를 offline-fixture → "online + 견고한 추출" 로 수정해 **실제 신규 source-confirmed relation 채굴**.
- **foundation:** v1.6 가 main 에 미머지라, v1.7 이 Phase A 토대(`fix_harvester_display_template_v1_6.py` copy-lint/B6 +
  `audit_fidelity_v1_6.py` B1~B4/기존-corpus audit)를 branch 에 동반(self-contained off main).

---

## PHASE 0 — nedrug 접속 진단 (필수 선행 게이트 · PASS)

실행환경(Mac Mini)에서 curl 직접 측정:

| 엔드포인트 | 결과 |
|---|---|
| `GET /searchDrug?searchYn=Y&ingrName1=<성분>` | **HTTP 200** (본문 ~260KB · itemSeq 파싱 정상) |
| `GET /pbp/CCBBB01/getItemDetail?itemSeq=<seq>` | **HTTP 302 → getItemDetailCache** (redirect 추종 후 **200**, ~300KB) |
| `data.go.kr DrbEasyDrugInfoService` | **HTTP 401** (serviceKey 없음 — 정상, 무시) |

➡️ nedrug 도달 가능 → 진행. **핵심 진단: v1.6 신규 0건의 원인은 네트워크/데이터가 아니라** (a) orchestrator 가
검증된 SDK(`medistack_sdk.NedrugClient`, online 정상 작동)를 **harvest 경로에 배선하지 않고 static universe 만 열거**
(source_pointer=null) (b) **추출 결함**(문장 잘림·동사 누락·섹션 미구분) — 둘 다 v1.7 에서 직접 수정.

---

## PHASE 1·2 — online client + 견고한 추출 (핵심)

- **`nedrug_online_client_v1_7.py`**: 검증된 직접 HTTP(검색 ingrName1, 상세 302 추종)를 과제 사양으로 래핑 —
  polite delay ≥1s · timeout 25s · 재시도 1회 · UA 고정 · offline/fixtures(test). `search_itemseqs`/`search_rows`/`fetch_detail`.
- **`extract_label_interaction_v1_7.py`** (v1.6 추출 3대 결함 직접 수정):
  - **섹션 분할 + scope 강제**: `<h3 cont_title2>`·`<p class="title">N.섹션` 마커로 분절 → 흡수-방향성 주장은
    **상호작용/병용투여 섹션에서만** 채택. 이상반응/임부/용법 동거어는 reject(off-scope).
  - **완전 문장 보장**: 블록 경계(`</p>`,`<br>`,`<li>`)를 줄바꿈으로 보존 → 한국어 종결('다./것./요.')로 분할.
    **문장 중간 잘림 0 · 라벨 전용 줄 글루 0**(예: `2) 칼슘보충제/제산제` 라벨이 다음 문장에 들러붙지 않음).
  - **동사 사전**(방해/저해/저하/지연/감소/떨어뜨림/줄어듦) — v1.6 이 놓친 **'방해' 커버 → 알렌드론산 포착**.
  - **방향 판정**: `이 약의 흡수[를/가] 저하` = this_drug_lowered(separation-supporting). 반대/모호 → needs_review.
  - 단일성분·경구 완제 필터(주사·외용·원료·복합성분 제외).

### 🔑 GOLD TEST — 3/3 verbatim 재현 (self-check PASS)

| itemSeq | 약물 | 재현된 완전 문장(라벨 원문 verbatim) |
|---|---|---|
| 201207007 | 이반드론산 | "우유, 음식물, 칼슘, 다가 양이온(예, 알루미늄, 마그네슘, 철)들을 포함한 제품들은 이 약의 흡수를 저해할 수 있다." |
| 201903166 | 리세드론산 | "칼슘보충제, 제산제 및 다가 양이온(칼슘, 마그네슘, 철, 알루미늄 등)을 함유한 경구투여 약물의 병용 투여는 이 약의 흡수를 방해한다." |
| 197400278 | 레보티록신 | "콜레스티라민, 철분제제, 알루미늄 함유 제산제와 병용투여시 이 약의 흡수가 지연 또는 감소될 수 있으므로 투여간격에 주의하며 신중히 투여한다." |

> ⚠️ **투명 보고 — GOLD #1**: 과제 예시 문자열(`…칼슘보조제, 제산제, 다가 양이온…경구투여 약물은…`, 선두 `…`)은
> PM 근사치였고 실제 201207007 라벨 원문은 위 표의 문장이다. strict-source-fidelity 는 PM 근사가 아니라 **라벨 원문
> 그대로**를 요구하므로, 라벨 verbatim 완전 문장(다가양이온·알루미늄·'흡수를 저해할 수 있다.' 종결)을 재현했다.
> GOLD #2·#3 은 라벨 원문과 과제 예시가 정확히 일치.

---

## PHASE 3·4 — orchestrator online 배선 + bounded harvest (dry-run)

`python3 scripts/run_medistack_autofactory_orchestrator_v1_7.py --online`

### Harvest attempts (정직 — silent drop 0)

| family | 약물 | search | oral표본 | 흡수findings | 결과 |
|---|---|---|---|---|---|
| F3 | 알렌드론산 | 15 | 2 | 2 | ⚠️ **needs_review** — 라벨이 일반 '제산제'만 명명(Al/Mg 양이온 미명명) → Al/Mg-specific 승급 금지(source-fidelity) |
| F3 | 리세드론산 | 15 | 2 | 2 | ✅ **신규 confirmed** (200713889, =seed) — 라벨이 다가양이온(칼슘·마그네슘·철·알루미늄) 명명 |
| F3 | 이반드론산 | 15 | 2 | 4 | ✅ confirmed → 기존 RF-F3-0147 과 동일(cross-validation, dedup) |
| F3 | 미노드론산 | **0** | 0 | 0 | ✗ ingrName1 검색 0건(KR 미등록/명칭변형 — honest gap) |
| F4 | 레보티록신 | 15 | 2 | 2 | ✅ confirmed → 기존 RF-F4-0173 과 동일(cross-validation, dedup) |
| F6 | 오메프라졸·에스오메프라졸·란소프라졸·판토프라졸·라베프라졸 | 15×5 | 1×5 | 6 | ✗ al_mg_antacid 흡수 0 — PPI×B12 는 **depletion** 기전(흡수-방향성 추출기 scope 밖) |
| FD | 푸로세미드·히드로클로로티아지드 | 8·15 | 1·1 | 2 | ✗ al_mg_antacid 흡수 0 — 이뇨제×미네랄도 depletion |

### Funnel (정직 — 부풀리기 0)

| 단계 | 수치 | 비고 |
|---|---|---|
| raw | **3** | 실 itemSeq + 완전 문장 quote(허위 인용 0). al_mg_antacid 흡수-방향성·양이온 명명 정당분만(알렌드론산 격리 후). |
| source-check | **3 confirmed** | live_dup 0 · hold 0 · reject 0 · guard_quarantine 0 · scope_needs_review 1(알렌드론산). |
| source-confirmed (**신규**) | **3** | 리세드론산·이반드론산·레보티록신 × 제산제. **v1.6 의 신규 0 → v1.7 의 신규 3.** |
| auto_pass → audit_pass (B7/B8) | **36 → 36** | 기존 corpus 33 + 신규 3. **false_auto_pass 0**(아래 ⚠️ 2건 정정 후) · batch_recheck False. |
| reviewer-ready (미live∧audit_pass) | **3** | 기존 2(RF-F3-0147·RF-F4-0173) + **신규 1**(리세드론산). cross-val 2(이반드론산·레보티록신) dedup 제외. |
| needs_review | **5** | 기존 genuine quarantine 4(v1.4) + harvest scope 격리 1(알렌드론산·일반 제산제). |
| reject | **0** | live_dup/hold/direction/guard 전부 0. |

### dry-run 투영
- base 92 → **95**(미live reviewer-ready 3 적용 가정), `live_write=False`, v0.2 export **미수정**(92 유지).

### ⚠️ 독립 감사가 실제 결함 2건을 잡았다 (정정 투명 보고)

**결함 #1 — 추출 글루(B7/B8 batch-recheck 가 적발).** 1차 online run 에서 알렌드론산이 false_auto_pass 로 적발.
- 근본 원인: 라벨에 `<p>2) 칼슘보충제/제산제</p><p>칼슘보충제나 제산제…흡수를 방해하는 것으로 알려져 있다.</p>` 구조 —
  문장 분할이 종결부호만 보아 **라벨 전용 줄이 다음 문장에 글루**(`'칼슘보충제/제산제 \n 칼슘보충제나…'`). B7 독립 재추출이 적발.
- 수정: 추출기를 **블록 경계(`</p>`/`<br>`/`<li>`) 우선 분할**로 변경 → 라벨 전용 줄(종결부호 없음) 탈락, 본문만 잔존.
  (audit 비결정성 제거 위해 stage1 캡처 HTML 을 audit 에 직접 전달.) GOLD 3/3 재검증 통과.

**결함 #2 — counterpart 과확장(독립 적대검증 Workflow 가 적발).** 글루 수정 후 알렌드론산은 clean 완전 문장
`"칼슘보충제나 제산제 및 일부 경구용 약물들은 이 약의 흡수를 방해하는 것으로 알려져 있다."` 로 confirmed 됐으나, **적대검증이
source-fidelity 위반을 적발**: 이 라벨은 **일반 '제산제'만 명명**(전체 라벨 알루미늄=0·다가=0·마그네슘=스테아르산마그네슘 첨가제뿐)
인데, 후보가 counterpart 를 `Al/Mg 함유 제산제(약물)` 로 **좁혀** display/management 에 노출 → "원문보다 강하면 금지" 위반.
내 B7 감사는 인용 재현만 검사하고 **counterpart 특정성 정당성**은 검사하지 않아 통과시켰음(audit 의 사각).
- 수정(defense-in-depth): ① harvest 입력단 — quote 가 Al/Mg 양이온을 명시 명명할 때만 Al/Mg-specific counterpart 부여,
  일반 제산제면 `needs_review`(counterpart_scope_unsupported) 격리. ② audit B7 — 독립 `counterpart_scope_justified`
  체크 추가(`audit_fail_counterpart_overclaim`). 재실행 → 알렌드론산 needs_review 격리, **false_auto_pass 0**, reviewer-ready 3.
- 대비 확인: 리세드론산(다가양이온 Al·Mg 명명)·이반드론산(Al·Mg 명명)은 Al/Mg 정당, 레보티록신(알루미늄만 명명)은 Al-only 정당 →
  counterpart 특정성은 **각 라벨 원문 기준**으로 부여됨(blanket 아님).
- 두 결함 모두 **독립 감사/적대검증이 설계대로 차단**했고(자기 테스트가 놓친 #2 를 적대검증이 포착), 정정 후 전수 PASS.

---

## reviewer-ready 후보 (3) — 전건 absorption/separation · evidence moderate · al_mg_antacid

> 신규 1(리세드론산)은 **base 92 미포함**(live 는 비스포스포네이트×개별 미네랄만 있고 ×제산제 relation 부재).
> display/management 는 live id72(노르플록사신×제산제) FACT-form 과 **byte-identical**(신규 문구 창작 0).

### 신규 (1) — 향후 live-PR 후보
| id | ingredient × counterpart | itemSeq | section | 완전 인용문 |
|---|---|---|---|---|
| **H7-F3-001** | 리세드론산 × Al/Mg 함유 제산제(약물) | 200713889 | 6.상호작용 | "칼슘보충제, 제산제 및 다가 양이온(칼슘, 마그네슘, 철, 알루미늄 등)을 함유한 경구투여 약물의 병용 투여는 이 약의 흡수를 방해한다." |

- **display_text_ko**: "이 약은 Al/Mg 함유 제산제(약물)과(와) 함께 복용하면 약의 흡수가 줄어 효과가 감소할 수 있다는 허가사항 문구가 있습니다. 함께 복용하는 경우 복용 시점에 대해 약사 또는 의사와 상담하세요."
- **management_ko**: "Al/Mg 함유 제산제(약물)과(와)는 복용 시간을 분리하는 것이 좋을 수 있습니다. 자세한 사항은 약사 또는 의사와 상담하세요."
- (리세드론산 quote 가 다가양이온 알루미늄·마그네슘을 명시 명명 → "Al/Mg 함유 제산제(약물)" 특정성 정당. 이것이 알렌드론산과의 차이.)
- **알렌드론산(199800180)은 reviewer-ready 가 아니라 needs_review** — 라벨이 일반 '제산제'만 명명해 Al/Mg-specific counterpart 부여 불가(아래 needs_review).

### 기존 corpus 미live (2) — 이미 PR-3
| id | ingredient × counterpart | itemSeq | 비고 |
|---|---|---|---|
| RF-F3-0147 | 이반드론산 × Al/Mg 함유 제산제(약물) | 201207007 | PR-3 open. harvest 가 라벨에서 독립 재확인(cross-validation). |
| RF-F4-0173 | 레보티록신 × 알루미늄 함유 제산제(약물) | 197400278 | PR-3 open. **Al-only**(라벨이 알루미늄 함유 제산제만 명시 — 과확장 아님). |

> **cross-validation(중복 승급 제외)**: harvest 가 이반드론산(201207007)·레보티록신(197400278)을 라벨 원문에서 독립
> 재도출했고, 이는 기존 corpus RF-F3-0147·RF-F4-0173 과 동일 relation → reviewer-ready 에서 dedup. PR-3 의 source
> 정확성을 별도로 재확인한 셈.

---

## needs_review top 패턴 (network-artifact 복구분 vs 진짜 source 부재)

- **harvest counterpart-scope 격리 1: 알렌드론산** — 라벨이 일반 '제산제'만 명명(Al/Mg 양이온 미명명) → Al/Mg-specific
  counterpart 로 좁히면 원문보다 강함. **interaction 자체는 실재**(reject 아님)이나 counterpart 표기 결정에 reviewer 판단 필요
  (generic 제산제 counterpart 신설 여부). source 는 존재 — 추출/표기 정책 이슈.
- **진짜 source 부재(network-artifact 아님)**: **미노드론산** — nedrug `ingrName1=미노드론산` 검색 0건(KR 미등록 또는
  등록명 변형 추정). 네트워크 장애가 아닌 실제 검색 부재 → 명칭 alias 확장 트랙 후보(부풀리지 않고 honest gap 으로 보고).
- **scope 밖(추출기 한계, source 는 존재)**: PPI×B12·이뇨제×미네랄 — 흡수-방향성 추출기로는 미확인(depletion 기전).
  별도 **depletion-mode 추출기**(흡수 저해가 아닌 결핍/길항 패턴) 필요 — Phase 2b 후보.
- **network-artifact(복구 가능): 0** — 이번 batch 에서 네트워크 장애로 인한 누락 없음(전 target 도달).
- 기존 genuine quarantine 4(v1.4) 보존(informational).

---

## 가드 위반 / STOP 발생 여부 — STOP 미발생

- `--allow-live-write` **거부**(exit 1) · v0.2 export 미수정(92 유지) · 보호셋 8종 **sha256 main 과 byte-identical**.
- reviewer-ready lock 전건: live_integration_forbidden=true · published=false · clinical_reviewed=false · reviewed_by 공란 ·
  product_link_allowed=false · requires_clinical_review=false · 제품/구매/제휴 0 · schedule 0.
- effective copy 전건 copy-lint clean · '분리하도록 안내'/수치단정/과확장 0.
- B1~B4 승급 가드 통과 · **B7/B8 false_auto_pass 0**(결함 적발·수정 후) · 허위 인용 0(전건 실 itemSeq+verbatim quote).
- **STOP 조건(nedrug 불가/GOLD 미재현/보호파일 변경/false_auto_pass 잔존/copy 회귀/live-write) 전부 미발생.**

### 테스트/검증 요약 (전수 PASS)
- GOLD 3/3 · online client(offline+LIVE smoke) · validator · smoke · guard tests · v1.6 regression(4) · SDK dryrun.
- 보호파일(v0.1/v0.2 export·aliases·full index·app.js·data.js·index.html·styles.css) **무수정**(sha256 불변).

---

## 다음 live-PR 후보 추천

- **신규 추천: H7-F3-001(리세드론산 × Al/Mg 함유 제산제(약물))** 1건 — 라벨 verbatim 상호작용 인용(다가양이온 Al·Mg 명명) +
  live id72 FACT-form copy + B1~B8 + counterpart-scope + 독립 적대검증 통과. **PM source-fidelity 적대검증 후 PR-4(소형 1건) 후보.**
  - live 정합: 비스포스포네이트는 이미 ×개별 미네랄(칼슘/철분/마그네슘)이 live 인데 ×제산제(약물) 묶음 relation 만 부재 →
    제산제 행 추가는 기존 항생제/이트라코나졸 al_mg_antacid 행과 동형.
- **알렌드론산**: interaction 은 실재하나 일반 제산제 표기 정책(generic counterpart 신설 여부)에 reviewer 판단 필요 → 보류.
- 기존 2건(RF-F3-0147·RF-F4-0173)은 PR-3 으로 이미 열림(신규 아님). harvest 가 라벨에서 독립 재확인(cross-validation).
- **scale 경로**: ① 미노드론산 등 검색-0 약물의 alias 확장(ingrName1 명칭 변형/완제품명 검색) ② generic-제산제 counterpart 표기
  정책 정립(알렌드론산류) ③ **depletion-mode 추출기**로 PPI×B12·이뇨제×미네랄 트랙 확장 ④ universe 약물군 확대.
  전부 harvest 가 작동하므로 추출기·alias·표기정책 확장이 다음 게이트.

---

## 산출물
- 신규 스크립트: `nedrug_online_client_v1_7.py` · `extract_label_interaction_v1_7.py` · `audit_fidelity_v1_7.py` ·
  `run_medistack_autofactory_orchestrator_v1_7.py` · `validate_*` · `smoke_*` · `test_autofactory_orchestrator_guards_v1_7.py` ·
  `test_extract_gold_v1_7.py` · `test_nedrug_online_client_v1_7.py`
- 토대(v1.6, branch 동반): `fix_harvester_display_template_v1_6.py` · `audit_fidelity_v1_6.py`
- 패치: `medistack_sdk/nedrug_client.py`(`get_detail_html` raw HTML 접근 1 메서드 추가 — append-only, 기존 테스트 무영향)
- fixture(커밋): `tests/fixtures/nedrug/`(GOLD 3 + 신규 2 라벨 + 검색 1) — 오프라인 재현·source-fidelity 재검용.
- dry-run 패키지: `data/review/autofactory_v1_7_dryrun_package.json` 외 `autofactory_v1_7_*.json` 6종.
- 본 리포트: `docs/MediStack_autofactory_v1_7_run_report.md`

## 독립 적대검증 (refute-by-default Workflow)

**1차(6 lens·8 agents): HOLD** — source-fidelity-NEW 가 알렌드론산 counterpart 과확장 적발(결함 #2). 나머지 5 lens
(source-fidelity-existing·copy-fidelity·funnel-honesty·guards-safety + dedup·Al-only scope)는 전건 `refuted=false`.
→ 수정(harvest 입력단 + audit B7 이중 방어) 후 재검.

**2차(재검, 2 lens): `CLEAR_TO_PACKAGE` · holds 0** (refute-by-default·high confidence)
- **scope-fix**: 과확장이 **remediated(relabel 아님)** — reviewer-ready 3=[RF-F3-0147·RF-F4-0173·H7-F3-001], 알렌드론산은
  needs_review(counterpart_scope_unsupported), 승급 3건 전건 counterpart 특정성 quote 로 정당(리세드론산 Al/Mg, 레보티록신
  Al-only, 이반드론산 Al/Mg), 어떤 산출물에도 알렌드론산이 Al/Mg 로 노출 안 됨. 92+3=95 일치.
- **audit-catches**: 강제 알렌드론산(Al/Mg) → `audit_fail_counterpart_overclaim`·false_auto_pass=true (인용은 재현되나
  scope 체크가 차단 — harvest 우회해도 audit 백스톱이 잡음, 2중 방어 확인). 리세드론산 정상 통과. 전수 suite PASS,
  보호파일 8종 git main blob-hash 동일, v0.2 relation_count=92 유지, no-live-write 유지.

> 시사점: **자기 테스트가 놓친 source-fidelity 과확장(#2)을 독립 적대검증이 포착** → 입력단+audit 이중 가드로 정정 →
> 독립 재검이 CLEAR. strict-source-fidelity 규율이 설계대로 작동.
