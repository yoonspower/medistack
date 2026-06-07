# MediStack v0.2 — Phase 3 릴리스(QA/배포 전환) 계획서

작성 기준일: 2026-06-07 / 단계: **계획만 (DATA_URL 변경·deploy 전환·push 모두 미실행)**
전제 상태: `v0.2-dev` 브랜치, commit `6574198`. v0.2 relations 30건(신규 21~31 편입), v0.1 봉인, 라이브=v0.1(`yoonspower.github.io/medistack`). validator v0.1 PASS 12/12 · v0.2 PASS 15/15.

목표: 라이브 앱이 fetch하는 데이터를 v0.1 → **v0.2(30건)** 로 전환하고, 배포 게이트가 라이브 데이터(v0.2)를 검증하도록 바꾼다. v0.1 JSON은 **삭제하지 않고 아카이브 보존**(traceability·롤백용).

불변(전환 중에도): v0.1 JSON 직접수정 금지 / published·clinical_reviewed 봉인 / excluded 15행 미노출 / 제품·제휴 UI 금지 / 칼륨 행 안전표시 / disclaimers.common fail-safe / **validator PASS 없으면 배포 금지**.

---

## 1. v0.2 DATA_URL 전환 절차
- 대상: `src/js/data.js` 3행.
  - before: `const DATA_URL = './data/medistack_v0.1_beta_export.json';`
  - after:  `const DATA_URL = './data/medistack_v0.2_beta_export.json';`
- 이 한 줄이 라이브 데이터 소스를 결정(앱은 데이터 버전 독립). v0.1 파일은 그대로 둠.
- 변경 후 로컬에서 `python3 -m http.server 8000` → http://localhost:8000 으로 §3~7 QA 수행.

## 2. deploy.yml 검증 대상 v0.2 전환 절차
- 대상: `.github/workflows/deploy.yml` 의 `validate` job.
- 현재: "Validate v0.1 export contract" 단계만 존재(라이브=v0.1 게이트).
- 변경: 라이브가 v0.2가 되므로 **v0.2 검증을 게이트로 추가**. v0.1은 아카이브 무결성용으로 **함께 검증(둘 다 PASS여야 deploy)**.
  ```yaml
  - name: Validate v0.1 export contract (archived integrity)
    run: python3 scripts/validate_medistack_v0_1_export.py data/medistack_v0.1_beta_export.json
  - name: Validate v0.2 export contract (live)
    run: python3 scripts/validate_medistack_v0_2_export.py data/medistack_v0.2_beta_export.json
  ```
- `validate.yml`(PR 전용)은 이미 v0.1+v0.2 둘 다 검증 → **변경 불필요**.
- deploy job(`upload-pages-artifact path: "."`)은 repo 전체 업로드라 변경 불필요. Actions 버전(checkout@v5/setup-python@v6/configure-pages@v5/upload-pages-artifact@v3/deploy-pages@v4)도 현행 유지.

## 3. v0.2 QA 체크리스트 (로컬 = v0.2 DATA_URL 상태에서)
- [ ] 앱 부팅, 콘솔 에러 0 (`browse console --errors` localhost 항목 없음)
- [ ] 목록 카드 **30건** 렌더 / listhead 카운트 정상
- [ ] disclaimers.common 모든 상세에 표시(fail-safe)
- [ ] published/clinical_reviewed 뱃지·문구 미출현, 제품/구매 UI 미출현
- [ ] 데이터-0건 empty_state 문구와 검색-무매치 문구가 분리 동작(무매치가 "안전"으로 안 읽힘)
- [ ] v0.1·v0.2 validator 둘 다 PASS, v0.1 봉인 md5 불변

## 4. 검색/필터 30건 기준 QA
- [ ] 검색 "토라" → 2건(토라세미드×칼륨/마그네슘=#/r/30·31)
- [ ] 검색 "오플" → 3건(오플록사신 21~23), "미노" → 3건(26~28)
- [ ] 영양소 필터 "칼륨" 단독 → **3건(#/r/17·19·30)**
- [ ] 영양소 "마그네슘" 필터 → 신규 23·25·28·31 포함 카운트 정상
- [ ] 액션 필터 separation / monitoring 교집합(AND) 정확
- [ ] facet이 데이터에서 동적 도출(하드코딩 아님) — 30건 기준 영양소/액션 목록 자동 반영
- [ ] "필터 초기화" → 30건 복원
- [ ] 필터/검색이 relations 소스만 사용 → excluded 15행·원시데이터 미진입

## 5. 신규 11건 상세 화면 QA (각 #/r/{id})
- [ ] 21·22·23 오플록사신×칼슘/철분/마그네슘 — separation 문구, 출처 pointer(itemSeq 198600307) 표시
- [ ] 24·25 목시플록사신×철분/마그네슘 — pointer(201402438 + 대표 제네릭/교차확인 註) 표시
- [ ] 26·27·28 미노사이클린×칼슘/철분/마그네슘 — pointer(198501028) 표시
- [ ] 29 알렌드론산×칼슘 — pointer(200009061 + 교차확인 註) 표시
- [ ] 30·31 토라세미드×칼륨/마그네슘 — monitoring 문구, pointer(200611522 + 교차확인 註) 표시
- [ ] 11건 모두 disclaimers.common 표시 / 제품·구매 UI 없음 / 의료단정·복용지시 문구 없음

## 6. 칼륨 행 [17, 19, 30] 안전 표시 QA
- [ ] 세 행 모두 상세에서 potassium_notice("칼륨은 임의로 보충하면 위험… (제품 예시 미제공)") 표시
- [ ] product_link_allowed=false → 제품 링크/제품 예시/구매 버튼 **전무**
- [ ] 신규 30(토라세미드×칼륨)도 기존 17/19와 동일 안전 프레임
- [ ] 칼륨 고지는 `potassium_safety_card===true` 플래그 기준 동작(nutrient 문자열 매칭 아님)

## 7. excluded 15행 미노출 QA
- [ ] `#/r/15` 직접 진입 → error/안전 상태(상세 미렌더), 정상 데이터로 오인 안 됨
- [ ] 목록·검색·필터 어디서도 15행(에스오메프라졸×B12) 카드 미출현
- [ ] getRenderableRelations 경유로 excluded_v0_1 절대 진입 불가 재확인

## 8. v0.1 rollback 방법
라이브는 정적 사이트이므로 롤백 = "DATA_URL/게이트를 v0.1로 되돌려 재배포". v0.1 JSON·validator는 repo에 그대로 있으므로 즉시 가능.
- 방법 A (권장, 빠름): `src/js/data.js`의 DATA_URL을 v0.1로 되돌리고 (deploy.yml validate도 v0.1만으로 되돌릴 필요는 없음 — 둘 다 PASS면 무방) main push → 재배포.
- 방법 B: 문제 커밋을 `git revert <hash>` 후 main push → 재배포.
- 방법 C: 직전 정상 커밋으로 `actions/deploy-pages` 재실행(원하는 커밋에서 workflow_dispatch).
- 데이터 자체는 불변 보존이라 롤백해도 v0.2 파일 유지(다음 시도 가능). 롤백 후 라이브에서 v0.1 19건 표시 확인.

## 9. 배포 전/후 검증 순서
**배포 전(로컬·CI):**
1. `git status` — 의도한 파일만 변경(data.js, deploy.yml)
2. v0.1 validator PASS / v0.2 validator PASS / v0.1 봉인 md5 불변
3. 로컬 서버에서 §3~7 전 항목 그린
4. (PR 경로면) validate.yml CI 그린 확인

**배포 후(라이브 `yoonspower.github.io/medistack`):**
1. Actions deploy 워크플로우 success 확인(validate→deploy)
2. 라이브 목록 30건 / 콘솔 에러 0
3. 검색 "토라"=2, 칼륨 필터=3(#/r/17·19·30)
4. 신규 11건 상세 1~2개 표본 + 칼륨 30 안전표시
5. `#/r/15` 미노출 재확인
6. Pages 전파 지연 대비 200 응답 폴링 후 캐시 강제새로고침

## 10. push / PR 전략
- 현재 작업은 `v0.2-dev` 브랜치(미push). 배포 트리거는 **main push**(deploy.yml).
- 권장: **PR 경로** `v0.2-dev` → `main`.
  1. Phase 3 변경(data.js DATA_URL, deploy.yml validate v0.2) 커밋을 v0.2-dev에 추가
  2. `v0.2-dev` push → GitHub에서 PR 생성 → validate.yml(PR, v0.1+v0.2) CI 그린 확인
  3. PR 머지 시 main push → deploy.yml(validate v0.1+v0.2 → deploy) 자동 배포
  4. §9 배포 후 검증
- push/머지/배포는 **각 단계 PM 판정 후** 실행. 본 계획서는 실행 아님.
- 한 PR에 데이터(이미 편입됨)·DATA_URL·deploy.yml을 함께 묶어 "v0.2 라이브 전환" 단일 변경으로 관리.

---

## 실행 체크포인트 요약 (PM 판정 게이트)
1. (계획 승인) → 2. data.js DATA_URL v0.2 + deploy.yml v0.2 게이트 변경·로컬 QA → 3. PM 판정 → 4. v0.2-dev push + PR + CI 그린 → 5. PM 판정 → 6. 머지=배포 → 7. 라이브 검증 보고 → 8. 이상 시 §8 롤백.

> 안전 원칙(불변): 원문에 없으면 노출 금지 / 원문보다 강하면 금지 / 복용량·제품추천이면 금지 / 칼륨 제품링크 금지 / clinical 검수 전 published 금지.
