# MediStack v1.4 — live PR rollback plan

> NO-LIVE-WRITE PLAN — 본 문서는 실제 live PR 통합 이후를 위한 rollback 절차서. 이번 커밋에는 통합/rollback 실행 0.

## 권장 PR/브랜치 방식
- wave 1건 = 1 PR = 1 squash/merge commit. wave 단위 revert 가능하도록 **wave별 단일 commit** 유지.
- 통합 직전 `git tag pre-livepr-<wave>` (또는 wave 브랜치) 로 복귀점 고정.

## wave별 rollback 기준 (아래 중 하나라도 해당 시 즉시 revert)
| 트리거 | 판정 | 조치 |
|---|---|---|
| relation_count mismatch | `validate_live_pr_readiness --post-merge` 가 `직전 count + delta` 와 불일치 | revert |
| validator fail | v0.2 export validator / readiness validator FAIL | revert |
| forbidden phrase 검출 | `validate_forbidden_phrases_v1_2.py` 에서 금지 표현 | revert |
| DATA_URL 변경 | `src/js/data.js` 가 v0.2 외 경로 | revert + data.js 복구 |
| published/clinical/reviewed_by 변동 | meta.published=true / clinical_reviewed=true / relation 에 reviewed_by | revert |
| product UI / schedule 변동 | 제품·구매·제휴 필드/UI 또는 schedule 활성 | revert |
| live/data HTTP fail | 배포 후 live·data·index·app.js 가 200 아님 | revert + 재배포 |

## Git revert 방식
```
git revert <merge_commit>          # wave 단일 commit 되돌리기 (권장)
# 또는 복귀점 태그로:
git reset --hard pre-livepr-<wave> # 로컬에서만, push 전 검증용
```
- 절대 `data/medistack_v0.1_beta_export.json`·aliases·full index 를 손대지 않는다(봉인/보호).
- relation id 는 append 였으므로 revert 시 해당 신규 id 가 사라지고 count 가 직전값으로 복귀(중간 id 재사용 금지).

## post-rollback 검증
1. `python3 scripts/validate_medistack_v0_2_export.py data/medistack_v0.2_beta_export.json`
2. `python3 scripts/validate_live_pr_readiness_v1_4.py` (pack 드리프트 0)
3. `python3 scripts/validate_live_pr_readiness_v1_4.py --post-merge --wave <wave>` (count 복귀 확인)
4. 보호 hash 재확인 (v0.1/v0.2/aliases/full index)
5. live/data/index/app.js HTTP 200 재확인
6. published=false·clinical_reviewed=false·reviewed_by 공란·schedule 비활성·제품 UI 0 재확인
