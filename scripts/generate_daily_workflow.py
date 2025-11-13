#!/usr/bin/env python3
"""
일일 워크플로우 프롬프트 생성 스크립트
뉴스 분석을 위한 프롬프트를 자동 생성
"""

import sys
import os
from pathlib import Path
from loguru import logger

sys.path.insert(0, str(Path(__file__).parent.parent))

from database.supabase_client import SupabaseClient
from analyzers.prompt_generator import PromptGenerator

def generate_workflow(output_dir: str = "prompts"):
    """일일 워크플로우 생성"""

    # 출력 디렉토리 생성
    os.makedirs(output_dir, exist_ok=True)

    db = SupabaseClient()
    generator = PromptGenerator(db)

    # 워크플로우 프롬프트 생성
    workflow_file = generator.generate_daily_workflow_prompt(output_dir)

    if workflow_file:
        print(f"\n✅ Generated daily workflow\n")
        print(f"📁 Workflow file: {workflow_file}")
        print(f"\n🔄 Next steps:")
        print(f"1. Read the workflow: cat {workflow_file}")
        print(f"2. Follow the instructions in the file")
        print(f"\n⏱️  Estimated time: 30-60 minutes")
        print(f"💰 Cost: $0 (Free!)\n")
    else:
        print("\n⚠️  No unanalyzed news found.")
        print("Run news collection first: python main.py --mode collect\n")

if __name__ == "__main__":
    output_dir = sys.argv[1] if len(sys.argv) > 1 else "prompts"
    generate_workflow(output_dir)
