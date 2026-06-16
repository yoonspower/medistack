# MediStack — counterpart_category Policy (v1.3)

> relation 의 `counterpart_category` 가 무엇을 의미하고, UI/PM review artifact 에서 어떻게 다뤄야 하는지 정리.
> theme map expansion(프롬프트 8~9)에서 신규 category 2종(**acid_reducing_drug**, **fat_soluble_vitamin**)이
> 후보로 올라왔다. 본 문서는 **정책/검토용**이며 src/validator/export 를 바꾸지 않는다(live 통합은 별도 PR).
> seed 정의: `data/config/theme_map_seeds_v1_3.json` `meta.counterpart_category_policy`.

## 1. 배경 — counterpart_category 의 역할

대부분의 relation 은 `약물 × 영양소`(예: 레보티록신 × 철분). 이때 `nutrient` 슬롯이 실제 영양소라
`counterpart_category` 가 **없다(null/필드 생략)**. 그러나 `약물 × 약물`(antacid_interaction) 트랙에서는
`nutrient` 슬롯에 **약물**(예: "Al/Mg 함유 제산제(약물)")이 들어가므로, 이를 영양소로 오인하지 않게
`counterpart_category` 마커로 구분한다.

`src/js/guards.js getFacets` 현행 규칙: **`counterpart_category` 가 있는 relation 은 '영양소' facet 에서 제외**한다
(nutrient 슬롯이 영양소가 아니라는 가정). → 이 가정은 **약물 category 에는 맞지만, 영양소군 category 에는 틀리다**(§4).

## 2. category 카탈로그

| category | 종류 | 의미 | 영양소 facet | live 예시 |
|---|---|---|---|---|
| `null`(생략) | 영양소 | 단일 영양소 relation(철분·아연·칼슘 등). nutrient 슬롯=실제 영양소. | **포함** | id1~60(칼륨 포함), TM-CHEL-01-FE/ZN(준비) |
| `al_mg_antacid` | **약물** | Al/Mg **양이온 chelation** 전용(제산제). pH 무관, cation 결합. | **제외** | **id61** 이트라코나졸 × Al/Mg 제산제(live) · AT-FEX 펙소페나딘(준비) |
| `acid_reducing_drug` | **약물**(신규 권고) | 위산 **감소·중화** 약물(제산제·**H2·PPI**). **pH 의존** 흡수. | **제외** | TM-CEPH-AC-01/02(준비) |
| `fat_soluble_vitamin` | **영양소군**(신규 권고) | 지용성 비타민(A·D·E·K) **그룹**. 약물 아님. | **포함**(수정 필요·§4) | TM-LIP-01/02(준비) |

- **drug_categories** = {`acid_reducing_drug`, `al_mg_antacid`} → 영양소 facet 제외.
- **nutrient_categories** = {`fat_soluble_vitamin`, `null`} → 영양소 facet 포함.

## 3. al_mg_antacid vs acid_reducing_drug — 왜 분리하는가

| | al_mg_antacid (id61) | acid_reducing_drug (신규) |
|---|---|---|
| 기전 | Al/Mg **양이온 chelation**(직접 결합) | 위 **pH 상승**으로 약물 용해/흡수 저하 |
| 대상 약물 | Al/Mg 함유 제산제만 | 제산제 + **H2 차단제 + PPI** |
| 라벨 근거 | "수산화알루미늄/마그네슘…" | "위장 내 pH를 올리는 약물(제산제, H2-길항제)" / "위산을 감소시키는 다른 약물" |

→ **acid-reducer 를 al_mg_antacid 로 좁히면 안 된다**(H2/PPI 를 Al/Mg 로 표기 = 오정보).
이것이 신규 category 권고의 핵심 근거. (reviewer 가 통합 vs 분리 최종 확정 — reviewer package §3.)

## 4. UI/facet 에서의 노출 정책

- `null` 영양소 relation: 영양소 facet 에 **포함**(현행대로). 철분·아연·칼륨 등.
- **drug category**(`al_mg_antacid`·`acid_reducing_drug`): 영양소 facet **제외**(현행대로) — nutrient 슬롯이 약물.
  사용자에게 **'약물'** 로 명시(chip). Mg/철분 **영양제로 오인 금지**.
- **`fat_soluble_vitamin`**: 영양소군 → **영양소 facet 에 포함되어야** 한다. 그러나 현행 `getFacets` 는
  `counterpart_category` 있는 relation 을 일괄 제외하므로 **그대로 두면 지용성 비타민이 facet 에서 빠진다**.
  → live 통합 전 **src 수정 필요**: `getFacets` 가 nutrient_categories 는 포함, drug_categories 만 제외하도록 분기.
  (본 작업에서는 **하지 않음** — 별도 PR. dry-run 산출물·reviewer package §7 에 선행조건으로 문서화.)

## 5. 금지 (오용 방지)

- ❌ `acid_reducing_drug` 를 `al_mg_antacid` 로 축소 표기.
- ❌ 제산제/H2/PPI 약물을 **Mg(마그네슘) 영양제**로 표시.
- ❌ 비타민 K 를 **항응고(와파린/INR) 조절 정보**처럼 표시 — 흡수 정보로만.
- ❌ mineral relation(철분·아연)을 **제품/보충제 추천**처럼 표시.
- ❌ 근거(허가사항) 없이 새 category·relation family 발명, 계열 일반화.

## 6. 향후 live 통합 시 render/facet 검토사항 (별도 PR)

1. `getFacets`: nutrient_categories 포함 / drug_categories 제외 분기(§4).
2. `render.js`: `acid_reducing_drug` 전용 chip/kicker(제산제·H2/PPI 약물 표기) — 현 avoid_concomitant chip 은
   'Al/Mg 함유 제산제' 문구 고정이라 세팔로 acid-reducer 에 부적합.
3. v0.2 validator 검사 #15: `avoid_concomitant` 허용 category 에 `acid_reducing_drug` 추가(TM-CEPH-AC-02).

> **src 변경은 이번 작업에서 하지 않는다.** 위는 reviewer 결정 + 별도 PR 의 작업 목록이다.
