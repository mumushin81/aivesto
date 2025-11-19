#!/usr/bin/env python
"""Midjourney Image Viewer 실행 스크립트"""
import os
import sys
from pathlib import Path

# 프로젝트 루트를 경로에 추가
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

if __name__ == "__main__":
    try:
        import uvicorn
        from src.midjourney.viewer import app
        
        # Railway는 PORT 환경 변수를 자동으로 제공
        port = int(os.environ.get("PORT", 8000))
        host = os.environ.get("HOST", "0.0.0.0")
        
        print(f"🚀 서버 시작 중...")
        print(f"📍 호스트: {host}")
        print(f"🔌 포트: {port}")
        print(f"🎨 Midjourney Image Gallery: http://{host}:{port}")
        print("=" * 50)
        
        # Railway 배포를 위한 설정
        uvicorn.run(
            app,
            host=host,
            port=port,
            log_level="info",
            access_log=True
        )
    except Exception as e:
        print(f"❌ 서버 시작 실패: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)

