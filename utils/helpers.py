import logging
from typing import Optional, Dict, Any
from pathlib import Path
import json

# 로깅 설정
def setup_logging(log_level: str = "INFO") -> None:
    """로깅 설정을 초기화합니다."""
    logging.basicConfig(
        level=getattr(logging, log_level),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

def validate_url(url: str) -> bool:
    """인스타그램 URL이 유효한지 검증합니다."""
    return "instagram.com/p/" in url or "instagram.com/reel/" in url

def save_results(results: Dict[str, Any], output_path: Optional[Path] = None) -> None:
    """분석 결과를 JSON 파일로 저장합니다."""
    if output_path is None:
        output_path = Path("results.json")
    
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

def format_results(results: Dict[str, Any]) -> str:
    """분석 결과를 보기 좋게 포맷팅합니다."""
    formatted = []
    formatted.append("=== 분석 결과 ===")
    
    if "keywords" in results:
        formatted.append("\n��요 키워드:")
        formatted.append(", ".join(results["keywords"]))
    
    if "summary" in results:
        formatted.append("\n내용 요약:")
        formatted.append(results["summary"])
    
    if "sentiment" in results:
        formatted.append("\n감정 분석:")
        formatted.append(f"- {results['sentiment']}")
    
    if "content_relevance" in results:
        formatted.append("\n컨텐츠 일치성:")
        formatted.append(f"- {results['content_relevance']}")
    
    return "\n".join(formatted)

def create_directory_if_not_exists(directory: Path) -> None:
    """디렉토리가 존재하지 않으면 생성합니다."""
    if not directory.exists():
        directory.mkdir(parents=True)
