# depletion 추출기 v1.8 dry-run 보고 (2026-06-20)

- 큐 depletion source_check_candidate: **16건**
- raw 상세 fetch: 7 (cap 300)
- **reviewer-ready: 6** · needs_review: 0 · reject: 10
- false_auto_pass: 0 · 🔑 칼륨 invariant: OK

## reviewer-ready
- `D-CORT-03` 메틸프레드니솔론 × 칼륨 (itemSeq 199800324, kcard=True, ev=moderate) — 3. 부작용
    - quote: 체액ㆍ전해질 : 부종, 나트륨저류, 칼륨손실, 체액저류, 저칼륨성 알칼리혈증, 감수성 환자에 있어서 울혈성 심부전, 고혈압 등이 나타날 수 있다.
- `D-CORT-04` 덱사메타손 × 칼륨 (itemSeq 196300064, kcard=True, ev=moderate) — 3. 부작용
    - quote: 체액ㆍ전해질 : 부종, 고혈압, 혈압상승, 저칼륨성 알칼리혈증, 나트륨저류, 체액저류, 종양용해증후군 등이 나타날 수 있다.
- `D-CORT-05` 히드로코르티손 × 칼륨 (itemSeq 200703172, kcard=True, ev=moderate) — 3. 부작용
    - quote: 체액ㆍ전해질 : 부종, 혈압상승, 칼륨손실, 저칼륨성 알칼리혈증, 나트륨 저류, 체액 저류, 감수성 환자에 있어서 울혈성 심부전 등이 나타날 수 있다.
- `D-CORT-06` 플루드로코르티손 × 칼륨 (itemSeq 199907231, kcard=True, ev=moderate) — 4. 일반적주의
    - quote: 상용량 및 고용량의 히드로코르티손 또는 코르티손으로 혈압상승, 염 및 수분의 저류를 일으킬 수 있으며, 칼륨의 배설을 증가시킨다.
- `D-CA-01` 아세타졸아미드 × 칼륨 (itemSeq 201403403, kcard=True, ev=moderate) — 4. 이상반응
    - quote: 대사 : 때때로 저칼륨혈증, 저나트륨혈증을 포함한 대사성 산증 등의 전해질평형실조, 장기치료로 인한 골연화증, 고혈당/저혈당이 나타날 수 있다.
- `D-LOOP-04` 아조세미드 × 칼륨 (itemSeq 199001306, kcard=True, ev=moderate) — 3. 부작용
    - quote: 대사 : 때때로 저칼륨혈증, 저나트륨혈증, 저염소혈증성 알칼리증 등의 전해질평형실조, 고뇨산혈증, BUN·혈청크레아티닌의 상승, 드물게 고혈당이 나타날 수 있으므로 충분히 관찰하고 이상이 인정되는 경우는 감량 또는 휴약 등 적절한 처치를 한다.

## reject (사유별)
- `D-CORT-01` 프레드니솔론 × 칼륨 — no_single_oral_exact(주성분 정확매칭 경구 0)
- `D-LOOP-01` 부메타니드 × 칼륨 — not_reachable(국내 미유통/검색0)
- `D-LOOP-02` 부메타니드 × 마그네슘 — not_reachable(국내 미유통/검색0)
- `D-LOOP-03` 피레타니드 × 칼륨 — not_reachable(국내 미유통/검색0)
- `D-LOOP-05` 아조세미드 × 마그네슘 — no_마그네슘_deficiency_in_label(라벨 마그네슘 결핍 명시 없음/임부·상호작용 only)
- `D-THZ-01` 메토라존 × 칼륨 — not_reachable(국내 미유통/검색0)
- `D-THZ-02` 메토라존 × 마그네슘 — not_reachable(국내 미유통/검색0)
- `D-THZ-03` 트리클로르메티아지드 × 칼륨 — not_reachable(국내 미유통/검색0)
- `D-THZ-04` 트리클로르메티아지드 × 마그네슘 — not_reachable(국내 미유통/검색0)
- `D-THZ-05` 벤드로플루메티아지드 × 칼륨 — not_reachable(국내 미유통/검색0)
