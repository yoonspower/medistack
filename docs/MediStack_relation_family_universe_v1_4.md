# MediStack — Relation Family Universe (v1.4)

> 대량 후보 생성용 family 정의. **source-check 후보 생성 전용** — 계열 일반화로 draft/live 만들지 않는다.
> 정본 JSON `data/review/relation_family_universe_v1_4.json` · family **11**개. live 승격 0.

## F1 — Fluoroquinolone × metal cation (absorption/separation)
- drugs(20): 시프로플록사신, 레보플록사신, 목시플록사신, 오플록사신, 노르플록사신, 페플록사신, 로메플록사신, 발로플록사신, 자보플록사신, 프룰리플록사신, 게미플록사신, 스파르플록사신, 가티플록사신, 토수플록사신, 플루메퀸, 에녹사신, 플레록사신, 루플록사신, 가레녹사신, 시노플록사신
- counterparts: 철분, 칼슘, 마그네슘, 아연, Al/Mg 함유 제산제(약물)
- risk_class: **known_safe** · priority_default: P0 · source_check: True
- note: 퀴놀론 다가 양이온 킬레이트 — 라벨에 '2시간 전후/간격' 명시 흔함. live 다수 존재→dedup 분리.

## F2 — Tetracycline × metal cation (absorption/separation)
- drugs(7): 독시사이클린, 미노사이클린, 테트라사이클린, 옥시테트라사이클린, 데메클로사이클린, 메타사이클린, 티게사이클린
- counterparts: 철분, 칼슘, 마그네슘, 아연, Al/Mg 함유 제산제(약물)
- risk_class: **known_safe** · priority_default: P0 · source_check: True
- note: 테트라사이클린계 양이온 킬레이트. 티게사이클린=주사(경구 완제 없음 가능).

## F3 — Bisphosphonate × mineral (absorption/separation)
- drugs(9): 알렌드론산, 리세드론산, 이반드론산, 에티드론산, 클로드론산, 파미드론산, 졸레드론산, 미노드론산, 인카드론산
- counterparts: 칼슘, 철분, 마그네슘, Al/Mg 함유 제산제(약물)
- risk_class: **known_safe** · priority_default: P1 · source_check: True
- note: 다가 양이온·칼슘 함유 식품/제산제가 흡수 저하 → 기상 직후 물. 주사제(파미/졸레)=경구 없음.

## F4 — Thyroid hormone × mineral/antacid (absorption)
- drugs(2): 레보티록신, 리오티로닌
- counterparts: 마그네슘, Al/Mg 함유 제산제(약물)
- risk_class: **known_safe** · priority_default: P1 · source_check: True
- note: Fe·Ca 는 이미 live. Mg/제산제 흡수 영향은 라벨 직접근거 확인 필요.

## F5 — Iron-chelator / chelation (non-penicillamine)
- drugs(4): 트리엔틴, 데페라시록스, 데페리프론, 데페록사민
- counterparts: 철분, 아연, 칼슘
- risk_class: **high_risk** · priority_default: HOLD · source_check: False
- note: 철 과부하 치료제 — 미네랄 상호작용이 치료 목적과 얽힘. reviewer 전 hold(보충 권유 오인 위험).

## F6 — Acid-reducer (H2/PPI) × Fe/B12/antacid
- drugs(10): 파모티딘, 시메티딘, 니자티딘, 라푸티딘, 록사티딘, 오메프라졸, 에스오메프라졸, 란소프라졸, 판토프라졸, 라베프라졸
- counterparts: 철분, 비타민B12
- risk_class: **monitoring** · priority_default: P1 · source_check: True
- note: 만성 위산 감소 → Fe/B12 흡수 영향(라벨 직접근거 약할 수 있음). 산분비억제제 자신은 pH-흡수의존 아님→antacid counterpart 제외. PPI×Mg/B12 다수 live→dedup.

## F7 — Bile-acid sequestrant × fat-soluble vitamin/folate
- drugs(2): 콜레세벨람, 콜레스티폴
- counterparts: 지용성 비타민(A·D·E·K), 엽산
- risk_class: **known_safe** · priority_default: P1 · source_check: True
- note: 콜레스티라민·오르리스타트는 theme map pending. 콜레세벨람은 결합 선택성↑로 미기재 가능.

## F8 — Electrolyte monitoring (diuretic/steroid/laxative) × K/Mg/Na
- drugs(10): 아세타졸아미드, 아조세미드, 부메타니드, 에타크린산, 스피로노락톤, 덱사메타손, 베타메타손, 센나, 비사코딜, 수산화마그네슘
- counterparts: 칼륨, 마그네슘, 나트륨
- risk_class: **mixed** · priority_default: P2 · source_check: False
- note: loop/탄산탈수효소억제=depletion 가능. K-sparing(스피로노락톤)=상승 방향→depletion 금지(REJECT).

## F9 — Chronic-use depletion (antiepileptic/sulfasalazine/MTX) × folate/vitD
- drugs(11): 페니토인, 카르바마제핀, 발프로산, 페노바르비탈, 프리미돈, 옥스카르바제핀, 라모트리진, 토피라메이트, 조니사미드, 설파살라진, 트리메토프림
- counterparts: 엽산, 비타민D, 비타민B12
- risk_class: **mixed** · priority_default: P2 · source_check: True
- note: 항전간제(효소유도) 만성투여=엽산/비타민D 저하 라벨 가능. MTX/피리메타민=항엽산·종양/면역 고위험→F11 HOLD(여기 제외).

## F10 — Azole antifungal × antacid (pH-dependent absorption)
- drugs(3): 케토코나졸, 포사코나졸, 이트라코나졸
- counterparts: Al/Mg 함유 제산제(약물)
- risk_class: **known_safe** · priority_default: P1 · source_check: True
- note: 이트라코나졸×Al/Mg 제산제는 live(id61). 케토/포사코나졸은 라벨 직접근거 확인.

## F11 — Exclusion / high-risk ledger (REJECT_PRECHECK / HOLD)
- drugs(8): 와파린, 사이클로스포린, 타크로리무스, 메토트렉세이트, 피리메타민, 레날리도마이드, 이소니아지드, 레보도파
- counterparts: 엽산, 비타민B6, 칼륨
- risk_class: **high_risk** · priority_default: HOLD · source_check: False
- note: warfarin×vitK(antagonism)·이식/면역억제·항암·임신·정신과 고위험. reviewer 전 제외(계열 일반화 금지).

## 제외/고위험 원칙
- warfarin×비타민K(antagonism)·이식/면역억제·항암·임신·정신과 고위험 = reviewer 전 제외.
- K-sparing(스피로노락톤 등)×칼륨 = 상승 방향 → depletion 카드 절대 금지(REJECT_PRECHECK).
- 세파계×철분·미유통 다이유레틱 = 확정 reject/no_domestic(재후보화 금지).
- 계열 일반화 금지: family 는 후보 생성용일 뿐, draft 는 약물별 라벨 직접근거(verbatim)만.
