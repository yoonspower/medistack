# MediStack v0.2 — 배포 전환 직전 Pre-Release Checklist

작성 기준일: 2026-06-07 / 성격: **배포 직전 go/no-go 게이트** (실행 명령 + 기대값)
기준 커밋: `v0.2-dev` `2f1c2cf` (Phase 3 계획 문서화까지 완료) / 라이브=v0.1 / 미push
짝 문서: `docs/MediStack_v0.2_phase3_release_plan.md`

> 사용법: 위에서 아래로 한 번에 실행. 한 항목이라도 기대값과 다르면 **STOP → PM 보고**. 모든 ✅ 후에만 §12 PM 승인 게이트로.
> 본 체크리스트는 검증 절차서다. DATA_URL/deploy.yml 변경·push는 §12 승인 후 별도 실행.

---

## A. 변경 전 현행 상태 검증 (라이브=v0.1, 작업트리 clean)

### 1. v0.2 데이터 30건 최종 확인
```bash
python3 -c "import json;d=json.load(open('data/medistack_v0.2_beta_export.json'));r=d['relations'];ids=[x['id'] for x in r];print('len',len(r),'meta',d['meta']['relation_count'],'dups',sorted({i for i in ids if ids.count(i)>1}),'ids',ids)"
```
- [ ] 기대: `len 30 meta 30 dups []` / ids = 1~14,16~31 (15 없음, 21~31 신규 11건)

### 2. v0.1 봉인 확인
```bash
git show HEAD:data/medistack_v0.1_beta_export.json | md5 ; md5 -q data/medistack_v0.1_beta_export.json
```
- [ ] 기대: 두 값 동일 = `f0e22d0b6afe8aa924e9fa6a4382b193` (v0.1 무수정)

### 3. validator v0.1 / v0.2 PASS
```bash
python3 scripts/validate_medistack_v0_1_export.py data/medistack_v0.1_beta_export.json | grep RESULT
python3 scripts/validate_medistack_v0_2_export.py data/medistack_v0.2_beta_export.json | grep RESULT
```
- [ ] 기대: v0.1 `PASS (12/12)` · v0.2 `PASS (15/15)`

### 4. DATA_URL 전환 대상 확인 (아직 v0.1이어야)
```bash
grep "DATA_URL =" src/js/data.js
```
- [ ] 현재값 `'./data/medistack_v0.1_beta_export.json'` 확인 → 전환 대상: `'./data/medistack_v0.2_beta_export.json'` (src/js/data.js 3행)

### 5. deploy.yml 검증 대상 전환 대상 확인 (아직 v0.1 게이트여야)
```bash
grep "validate_medistack" .github/workflows/deploy.yml
```
- [ ] 현재 deploy.yml validate job = v0.1만 → 전환 대상: v0.2 검증 단계 추가(v0.1 아카이브 무결성 + v0.2 라이브, 둘 다 PASS 게이트). `validate.yml`(PR)은 이미 v0.1+v0.2 → 변경 없음.

---

## B. v0.2 로컬 QA (DATA_URL을 v0.2로 임시 전환한 상태에서 수행 → QA 후 §A4 상태로 원복 가능)

전제: `python3 -m http.server 8000` 구동, `src/js/data.js` DATA_URL을 v0.2로 임시 변경(또는 전환 커밋 후).

### 6. v0.2 로컬 QA 목록
- [ ] 목록 카드 **30건** 렌더, listhead 카운트 정상
- [ ] 콘솔 에러 0 (localhost 기준)
- [ ] published/clinical 뱃지·제품/구매 UI 미출현
- [ ] 검색 "토라"→2건 / "오플"→3건 / "미노"→3건
- [ ] 영양소 "칼륨" 필터→3건(#/r/17·19·30) / "마그네슘" 필터 카운트 정상
- [ ] 액션 separation/monitoring AND 교집합 정확, facet 동적도출
- [ ] "필터 초기화"→30건 복원
- [ ] 검색-무매치 문구 ↔ 데이터-0건 empty_state 문구 분리(무매치가 "안전"으로 안 읽힘)

### 7. 신규 11건 상세 QA (`#/r/{id}`)
- [ ] 21·22·23 오플록사신×칼슘/철분/마그네슘 (separation, itemSeq 198600307)
- [ ] 24·25 목시플록사신×철분/마그네슘 (separation, 201402438)
- [ ] 26·27·28 미노사이클린×칼슘/철분/마그네슘 (separation, 198501028)
- [ ] 29 알렌드론산×칼슘 (separation, 200009061)
- [ ] 30·31 토라세미드×칼륨/마그네슘 (monitoring, 200611522)
- [ ] 11건 전부: disclaimers.common 표시 / 출처 pointer 표시 / 제품·구매 UI 없음 / 의료단정·복용지시 문구 없음

### 8. 칼륨 [17, 19, 30] 안전고지 QA
- [ ] 세 상세 모두 potassium_notice("칼륨은 임의로 보충하면 위험… (제품 예시 미제공)") 표시
- [ ] product_link_allowed=false → 제품 링크/예시/구매 버튼 전무
- [ ] 신규 30(토라세미드×칼륨)이 기존 17/19와 동일 안전 프레임
- [ ] 플래그(`potassium_safety_card===true`) 기준 동작(nutrient 문자열 매칭 아님)

### 9. excluded 15행 미노출 QA
- [ ] `#/r/15` 직접 진입 → error/안전 상태(상세 미렌더, 정상 데이터 오인 없음)
- [ ] 목록·검색·필터 어디서도 15행(에스오메프라졸×B12) 미출현

### (QA 종료 시) DATA_URL 임시변경했으면 원복
```bash
git checkout -- src/js/data.js   # 임시 v0.2 테스트였을 경우만
```

---

## C. 롤백 / 배포 후 검증 / 승인

### 10. rollback 명령 (라이브=정적, v0.1 즉시 복귀 가능)
```bash
# A: DATA_URL을 v0.1로 되돌려 재배포
#   src/js/data.js 3행 → './data/medistack_v0.1_beta_export.json' 후 main push
# B: 문제 커밋 되돌리기
git revert <bad_commit_hash>      # 후 main push → 재배포
# C: 이전 정상 커밋에서 배포 재실행 (GitHub Actions → deploy-pages → workflow_dispatch, 해당 ref)
```
- v0.1 JSON·validator는 repo 보존이라 롤백 즉시 가능. v0.2 파일은 불변보존(다음 시도 가능). 롤백 후 라이브에서 v0.1 19건 표시 확인.

### 11. 배포 후 라이브 URL 확인 항목 (`https://yoonspower.github.io/medistack/`)
- [ ] GitHub Actions deploy 워크플로우 success (validate→deploy)
- [ ] `curl -s -o /dev/null -w "%{http_code}" https://yoonspower.github.io/medistack/` → 200
- [ ] 라이브 목록 **30건** / 콘솔 에러 0
- [ ] 검색 "토라"→2건 / 칼륨 필터→3건(#/r/17·19·30) / 초기화→30건
- [ ] 신규 표본 상세(예: #/r/21, #/r/29) + 칼륨 #/r/30 안전표시
- [ ] `#/r/15` 미노출 재확인
- [ ] Pages 캐시 전파 지연 대비 재폴링 + 강제 새로고침

### 12. 최종 PM 승인 필요 지점 (게이트)
1. **§A 전 항목 ✅ 보고 → PM 승인** (현행 무결성 확인)
2. DATA_URL v0.2 + deploy.yml v0.2 게이트 **2파일 변경 + §B 로컬 QA ✅ 보고 → PM 승인**
3. `v0.2-dev` **push + PR 생성 + PR CI(validate.yml v0.1+v0.2) 그린 보고 → PM 승인**
4. **PR 머지(=main push=배포) → PM 승인** 후 실행
5. **§11 배포 후 라이브 검증 ✅ 보고** → 이상 시 §10 롤백
- 각 게이트는 직전 단계 보고·승인 없이는 진행 금지. 본 체크리스트 작성 시점엔 DATA_URL/deploy.yml/push 모두 미실행 유지.

---

> 안전 원칙(불변): 원문에 없으면 노출 금지 / 원문보다 강하면 금지 / 복용량·제품추천이면 금지 / 칼륨 제품링크 금지 / clinical 검수 전 published 금지 / validator PASS 없으면 배포 금지.
