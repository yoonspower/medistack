"""
medistack_sdk — MediStack 외부 데이터 접근 SDK.

모든 외부(식약처 nedrug) 조회는 이 패키지의 NedrugClient 를 통해서만 수행한다.
스크립트에서 직접 requests/urllib 로 NEDRUG URL 을 흩뿌리지 않는다.

SDK 역할: 데이터 조회 · 캐시 · 원문 저장 · 표준화 · 오류/timeout 관리 · 호출 로그.
SDK 역할 아님(금지): source_confirmed 최종 확정 · live relation 생성 · 배포 · live 데이터 수정.
판정은 detector / source_confirm_gate / PM review queue 단계에서만 수행한다.
"""
from .nedrug_client import NedrugClient, SearchRow, ItemDetail

__all__ = ["NedrugClient", "SearchRow", "ItemDetail"]
