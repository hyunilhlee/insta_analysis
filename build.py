import os
import shutil
from pathlib import Path

def build():
    """정적 파일 빌드"""
    # 빌드 디렉토리 생성
    build_dir = Path("build")
    if build_dir.exists():
        shutil.rmtree(build_dir)
    build_dir.mkdir()

    # 정적 파일 복사
    shutil.copytree("templates", build_dir / "templates")
    shutil.copytree("static", build_dir / "static", dirs_exist_ok=True)

    # index.html을 루트로 이동
    shutil.move(str(build_dir / "templates" / "index.html"), str(build_dir / "index.html"))

    print("빌드 완료!")

if __name__ == "__main__":
    build() 