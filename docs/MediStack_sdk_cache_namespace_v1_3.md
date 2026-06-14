# MediStack SDK 캐시 mode 네임스페이스 (v1.3)

`medistack_sdk/nedrug_client.py` — offline(fixture) 캐시와 online(실 NEDRUG) 캐시가 섞이던
**캐시 오염 버그 수정** 기록.

## 1. 증상
harvester bot 의 첫 `--online` subset 런(2026-06-14)에서 `프레드니솔론·아세타졸아미드·펙소페나딘`이
실제 nedrug 라벨이 아니라 **합성 fixture 데이터(itemSeq 100001/100002/100006)** 로 판정되어
거짓 `source_confirmed` 가 나왔다. 실제 itemSeq(9자리)는 신규 후보 `이트라코나졸`(200401453) 하나뿐.

## 2. 근본 원인
`NedrugClient._get()` 의 조회 순서가
1. **cache hit** (offline/online 분기보다 먼저) → 2. offline=fixture → 3. network
인데, offline 모드가 fixture 를 읽으면서 **그 내용을 동일한 평면 `cache_dir` 에 기록**했다.
offline 과 online 이 같은 `cache_dir`(`data/harvest_queue/_sdk/cache`)을 공유했으므로:
- 이전 offline/dry-run 이 캐시를 합성 fixture 로 채움 →
- 이후 online 런이 같은 cache 키를 **cache-hit** 으로 먼저 잡아 합성값을 서빙.
(역방향도 성립: online 이 채운 실캐시를 offline 이 읽어버림.)

## 3. 수정
`cache_dir`/`raw_dir` 밑에 **mode 서브디렉토리**를 두어 물리 분리한다.

```
data/harvest_queue/_sdk/
  cache/
    offline/   ← fixture 기반 캐시(dry-run/test 전용)
    online/    ← 실 NEDRUG 응답 캐시
  raw/
    offline/   ← fixture 원문 덤프
    online/    ← 실 응답 원문 덤프
  calls.jsonl  ← 호출 로그(라인마다 mode 표기, 공유)
```

- `__init__`: `self._mode_tag = "offline" if offline else "online"`;
  `self._cache_dir = cache_dir/<mode>`, `self._raw_dir = raw_dir/<mode>`.
- `_get()`/`_save_raw()` 는 `self._cache_dir`/`self._raw_dir`(mode dir)만 사용.
- 결과:
  - **online 은 `online/` 만 읽음** → fixture 캐시를 절대 cache-hit 하지 않음.
  - **offline 은 `offline/` 에만 씀** → online 캐시를 오염시키지 않음.

caller 변경 불필요: 봇은 online/offline 모두 같은 base `cache_dir` 를 넘기고, SDK 가 mode 로 분기한다.
`cache_dir=None`(예: `verify_factory_sources.make_opener()`)이면 캐시 자체가 비활성(무영향).

## 4. 기존 캐시 마이그레이션 / cleanup
이전 버전이 남긴 **평면 캐시**(`_sdk/cache/*.html`, `_sdk/raw/*.html` — 서브디렉토리 없이 직접)는
신규 코드가 읽지 않으므로 **무해하지만 stale** 하다. 업그레이드 시 1회 정리 권장:

```bash
rm -rf data/harvest_queue/_sdk     # gitignored 런타임 — 안전하게 삭제, 다음 런이 mode dir 로 재생성
```

`data/harvest_queue/_sdk/` 는 `.gitignore` 대상이라 **커밋된 데이터에는 영향 없음**(로컬 런타임만).

## 5. 회귀 방지 테스트
`medistack_sdk/test_nedrug_client_dryrun.py`(네트워크 0, 주입 opener 사용):
- `test_offline_then_online_no_fixture_contamination`: offline 런 후 online 런이 같은 key 를
  **fixture 로 cache-hit 하지 않고 network 경유**해 실데이터를 돌려주는지 검증.
- `test_online_then_offline_separation`: online 런 후 offline 런이 **online 실캐시를 읽지 않고
  fixture** 를 쓰는지 검증.
- 두 테스트는 수정 전 SDK 에서 **재현(FAIL)**, 수정 후 **PASS**.

## 6. 안전 불변(변경 없음)
이 수정은 SDK 런타임 캐시 구조만 바꾼다. live/protected 데이터(export·full index·alias·src·
DATA_URL), 배포, relation 승격에 **변화 없음**. 봇은 여전히 큐만 생성하고 live 를 건드리지 않는다.
