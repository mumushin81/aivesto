"""Midjourney 이미지 뷰어 및 관리 웹 UI - 프롬프트별 그룹화"""
import os
from pathlib import Path
from typing import List, Optional, Dict
import logging

from fastapi import FastAPI, UploadFile, File, Form
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from .processor import crop_image_cross
from .storage import MidjourneyImageStorage
from .manager import PromptManager
from .client import generate_images_batch
from .prompt_generator import MidjourneyPromptGenerator, generate_midjourney_prompt

logger = logging.getLogger(__name__)

# FastAPI 앱 생성
app = FastAPI(title="Midjourney Image Gallery")

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 디렉토리 설정
BASE_DIR = Path(__file__).parent.parent.parent
IMAGES_DIR = BASE_DIR / "data" / "images"
CROPPED_DIR = BASE_DIR / "data" / "images" / "cropped"
IMAGES_DIR.mkdir(parents=True, exist_ok=True)
CROPPED_DIR.mkdir(parents=True, exist_ok=True)

# 정적 파일 서빙
app.mount("/images", StaticFiles(directory=str(IMAGES_DIR)), name="images")
app.mount("/cropped", StaticFiles(directory=str(CROPPED_DIR)), name="cropped")

# 관리자 초기화
prompt_manager = PromptManager()

try:
    supabase_manager = MidjourneyImageStorage()
    SUPABASE_ENABLED = True
    logger.info("Supabase 초기화 성공")
except Exception as e:
    logger.warning(f"Supabase 초기화 실패: {e}")
    supabase_manager = None
    SUPABASE_ENABLED = False


def process_and_save_image(
    image_path: str,
    prompt: str,
    image_urls: Optional[List[str]] = None
) -> Dict:
    """이미지 자동 크롭 및 저장"""
    try:
        # 무조건 크롭
        cropped_paths = crop_image_cross(image_path, str(CROPPED_DIR))
        
        # 프롬프트 매니저에 등록
        prompt_hash = prompt_manager.register_image(
            prompt=prompt,
            original_path=image_path,
            cropped_paths=cropped_paths,
            image_urls=image_urls,
            metadata={"auto_cropped": True}
        )
        
        # Supabase 업로드 (선택적)
        upload_result = None
        if SUPABASE_ENABLED:
            try:
                upload_result = supabase_manager.save_midjourney_image(
                    image_path=image_path,
                    prompt=prompt,
                    cropped_paths=cropped_paths,
                    metadata={"source": "web_upload"}
                )
            except Exception as e:
                logger.warning(f"Supabase 업로드 실패: {e}")
        
        return {
            "success": True,
            "prompt_hash": prompt_hash,
            "cropped_paths": cropped_paths,
            "upload_result": upload_result
        }
    except Exception as e:
        logger.error(f"이미지 처리 실패: {e}")
        return {"success": False, "error": str(e)}


@app.get("/", response_class=HTMLResponse)
async def viewer():
    """메인 갤러리 페이지 - 프롬프트별 그룹화"""
    groups = prompt_manager.get_prompt_groups()
    
    html = """
    <!DOCTYPE html>
    <html lang="ko">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>🎨 Midjourney Image Gallery</title>
        <script>
            // 즉시 테마 초기화 (깜빡임 방지)
            (function() {
                const savedTheme = localStorage.getItem('theme');
                const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
                const theme = savedTheme || (prefersDark ? 'dark' : 'light');
                document.documentElement.setAttribute('data-theme', theme);
            })();
        </script>
        <style>
            :root {
                --bg-primary: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                --bg-card: #ffffff;
                --bg-section: #f8f9fa;
                --text-primary: #333333;
                --text-secondary: #666666;
                --text-muted: #999999;
                --border-color: #dddddd;
                --border-light: #f0f0f0;
                --shadow: rgba(0,0,0,0.1);
                --shadow-hover: rgba(0,0,0,0.15);
                --image-card-bg: #f8f9fa;
                --selection-bg: #fff3cd;
                --success-bg: #d4edda;
                --success-text: #155724;
                --error-bg: #f8d7da;
                --error-text: #721c24;
                --info-bg: #d1ecf1;
                --info-text: #0c5460;
            }
            
            [data-theme="dark"] {
                --bg-primary: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
                --bg-card: #1e1e2e;
                --bg-section: #252538;
                --text-primary: #e0e0e0;
                --text-secondary: #b0b0b0;
                --text-muted: #808080;
                --border-color: #404040;
                --border-light: #2a2a3e;
                --shadow: rgba(0,0,0,0.3);
                --shadow-hover: rgba(0,0,0,0.5);
                --image-card-bg: #2a2a3e;
                --selection-bg: #3d3d2e;
                --success-bg: #1e3a2e;
                --success-text: #4ade80;
                --error-bg: #3a1e1e;
                --error-text: #f87171;
                --info-bg: #1e2a3a;
                --info-text: #60a5fa;
            }
            
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                background: var(--bg-primary);
                min-height: 100vh;
                padding: 20px;
                color: var(--text-primary);
                transition: background 0.3s ease, color 0.3s ease;
            }
            .container {
                max-width: 1600px;
                margin: 0 auto;
            }
            .theme-toggle {
                position: fixed;
                top: 20px;
                right: 20px;
                z-index: 1000;
                background: var(--bg-card);
                border: 2px solid var(--border-color);
                border-radius: 50%;
                width: 50px;
                height: 50px;
                display: flex;
                align-items: center;
                justify-content: center;
                cursor: pointer;
                font-size: 24px;
                box-shadow: 0 4px 8px var(--shadow);
                transition: all 0.3s ease;
            }
            .theme-toggle:hover {
                transform: scale(1.1);
                box-shadow: 0 6px 12px var(--shadow-hover);
            }
            header {
                background: var(--bg-card);
                padding: 30px;
                border-radius: 16px;
                margin-bottom: 30px;
                box-shadow: 0 8px 16px var(--shadow);
                transition: background 0.3s ease, box-shadow 0.3s ease;
            }
            h1 {
                color: var(--text-primary);
                margin-bottom: 15px;
                font-size: 32px;
                transition: color 0.3s ease;
            }
            .upload-section {
                background: var(--bg-section);
                padding: 20px;
                border-radius: 12px;
                margin-top: 20px;
                transition: background 0.3s ease;
            }
            .upload-section h3 {
                margin-bottom: 15px;
                color: var(--text-primary);
                transition: color 0.3s ease;
            }
            .upload-row {
                display: flex;
                gap: 15px;
                align-items: flex-end;
            }
            .upload-row input[type="text"],
            .upload-row input[type="file"],
            .upload-row select {
                flex: 1;
                padding: 12px;
                border: 2px solid var(--border-color);
                border-radius: 8px;
                font-size: 14px;
                background: var(--bg-card);
                color: var(--text-primary);
                transition: all 0.3s ease;
            }
            .upload-row input[type="text"]:focus,
            .upload-row input[type="file"]:focus,
            .upload-row select:focus {
                outline: none;
                border-color: #667eea;
            }
            .upload-row input[type="file"] {
                background: var(--bg-card);
            }
            .btn {
                padding: 12px 24px;
                border: none;
                border-radius: 8px;
                font-size: 14px;
                font-weight: 600;
                cursor: pointer;
                transition: all 0.3s;
                white-space: nowrap;
            }
            .btn-primary {
                background: #667eea;
                color: white;
            }
            .btn-primary:hover {
                background: #5568d3;
                transform: translateY(-2px);
                box-shadow: 0 4px 8px rgba(0,0,0,0.2);
            }
            .btn-danger {
                background: #e74c3c;
                color: white;
            }
            .btn-danger:hover {
                background: #c0392b;
            }
            .btn-warning {
                background: #f39c12;
                color: white;
            }
            .btn-warning:hover {
                background: #e67e22;
            }
            .btn-success {
                background: #27ae60;
                color: white;
            }
            .btn-success:hover {
                background: #229954;
            }
            .status {
                margin-top: 15px;
                padding: 12px;
                border-radius: 8px;
                display: none;
            }
            .status.success {
                background: var(--success-bg);
                color: var(--success-text);
                display: block;
                transition: background 0.3s ease, color 0.3s ease;
            }
            .status.error {
                background: var(--error-bg);
                color: var(--error-text);
                display: block;
                transition: background 0.3s ease, color 0.3s ease;
            }
            .status.info {
                background: var(--info-bg);
                color: var(--info-text);
                display: block;
                transition: background 0.3s ease, color 0.3s ease;
            }
            .prompt-group {
                background: var(--bg-card);
                border-radius: 16px;
                padding: 25px;
                margin-bottom: 30px;
                box-shadow: 0 8px 16px var(--shadow);
                transition: all 0.3s ease;
            }
            .prompt-group:hover {
                box-shadow: 0 12px 24px var(--shadow-hover);
            }
            .prompt-header {
                display: flex;
                justify-content: space-between;
                align-items: flex-start;
                margin-bottom: 20px;
                padding-bottom: 15px;
                border-bottom: 2px solid var(--border-light);
                transition: border-color 0.3s ease;
            }
            .prompt-text {
                flex: 1;
                font-size: 16px;
                color: var(--text-primary);
                line-height: 1.6;
                margin-right: 20px;
                transition: color 0.3s ease;
            }
            .prompt-actions {
                display: flex;
                gap: 10px;
                flex-shrink: 0;
            }
            .prompt-meta {
                font-size: 12px;
                color: var(--text-secondary);
                margin-top: 8px;
                transition: color 0.3s ease;
            }
            .images-grid {
                display: grid;
                grid-template-columns: repeat(4, 1fr);
                gap: 15px;
                margin-top: 20px;
            }
            .image-card {
                position: relative;
                background: var(--image-card-bg);
                border-radius: 12px;
                overflow: hidden;
                aspect-ratio: 1;
                cursor: pointer;
                transition: all 0.3s ease;
                border: 3px solid transparent;
            }
            .image-card:hover {
                transform: translateY(-5px);
                box-shadow: 0 8px 16px var(--shadow-hover);
            }
            .image-card.selected {
                border-color: #667eea;
                box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.3);
            }
            .image-card img {
                width: 100%;
                height: 100%;
                object-fit: cover;
                display: block;
            }
            .image-label {
                position: absolute;
                bottom: 0;
                left: 0;
                right: 0;
                background: linear-gradient(to top, rgba(0,0,0,0.7), transparent);
                color: white;
                padding: 8px;
                font-size: 11px;
                text-align: center;
            }
            .checkbox-overlay {
                position: absolute;
                top: 8px;
                left: 8px;
                width: 24px;
                height: 24px;
                background: var(--bg-card);
                border: 2px solid #667eea;
                border-radius: 4px;
                display: flex;
                align-items: center;
                justify-content: center;
                cursor: pointer;
                z-index: 10;
                transition: background 0.3s ease;
            }
            .checkbox-overlay.checked {
                background: #667eea;
            }
            .checkbox-overlay.checked::after {
                content: '✓';
                color: white;
                font-weight: bold;
            }
            .selection-actions {
                display: none;
                margin-top: 20px;
                padding: 15px;
                background: var(--selection-bg);
                border-radius: 8px;
                text-align: center;
                color: var(--text-primary);
                transition: background 0.3s ease, color 0.3s ease;
            }
            .selection-actions.active {
                display: block;
            }
            .modal {
                display: none;
                position: fixed;
                z-index: 1000;
                left: 0;
                top: 0;
                width: 100%;
                height: 100%;
                background: rgba(0,0,0,0.95);
                overflow: auto;
            }
            .modal-content {
                margin: 50px auto;
                display: block;
                max-width: 90%;
                max-height: 90vh;
                border-radius: 8px;
            }
            .close {
                position: absolute;
                top: 20px;
                right: 40px;
                color: #f1f1f1;
                font-size: 50px;
                font-weight: bold;
                cursor: pointer;
                z-index: 1001;
            }
            .empty-state {
                text-align: center;
                padding: 60px 20px;
                color: var(--text-secondary);
                transition: color 0.3s ease;
            }
            .empty-state h2 {
                margin-bottom: 10px;
                color: var(--text-muted);
                transition: color 0.3s ease;
            }
            label {
                color: var(--text-primary);
                transition: color 0.3s ease;
            }
            input[type="text"],
            input[type="file"],
            select {
                background: var(--bg-card);
                color: var(--text-primary);
                border-color: var(--border-color);
            }
            input[type="text"]::placeholder {
                color: var(--text-muted);
            }
        </style>
    </head>
    <body>
        <button class="theme-toggle" onclick="toggleTheme()" id="themeToggle" title="테마 전환">
            🌙
        </button>
        <div class="container">
            <header>
                <h1>🎨 Midjourney Image Gallery</h1>
                <p style="color: var(--text-secondary); margin-bottom: 20px;">
                    프롬프트별로 그룹화된 이미지를 관리하고 새로운 이미지를 생성하세요
                </p>
                
                <div class="upload-section">
                    <h3>🤖 프롬프트 생성 (GLM 4.6 기본값)</h3>
                    <div style="margin-bottom: 15px;">
                        <label style="display: block; margin-bottom: 5px; color: var(--text-primary); font-weight: 600;">문장 입력 (여러 문장은 줄바꿈으로 구분):</label>
                        <textarea id="koreanInput" placeholder="예: A lone figure stands by the ocean, reflecting on the past

또는 여러 문장을 줄바꿈으로 입력
Each sentence will generate a separate prompt" rows="4" style="width: 100%; padding: 12px; border: 2px solid var(--border-color); border-radius: 8px; font-size: 14px; background: var(--bg-card); color: var(--text-primary); font-family: inherit; resize: vertical;"></textarea>
                        <div style="margin-top: 5px; font-size: 12px; color: var(--text-secondary);">
                            💡 여러 문장을 입력하려면 문장마다 줄바꿈으로 구분하세요. 각 문장마다 프롬프트가 생성됩니다.
                        </div>
                    </div>
                    <div style="margin-bottom: 15px;">
                        <label style="display: block; margin-bottom: 5px; color: var(--text-primary); font-weight: 600;">배경 문장 (선택사항, 쉼표로 구분):</label>
                        <input type="text" id="contextInput" placeholder="예: 비 오는 저녁, 고요한 해변, 쓸쓸한 분위기" style="width: 100%; padding: 12px; border: 2px solid var(--border-color); border-radius: 8px; font-size: 14px; background: var(--bg-card); color: var(--text-primary);">
                    </div>
                    <div style="display: flex; gap: 15px; align-items: center; margin-bottom: 15px;">
                        <select id="aspectRatio" style="padding: 12px; border: 2px solid var(--border-color); border-radius: 8px; font-size: 14px; background: var(--bg-card); color: var(--text-primary);">
                            <option value="16:9">16:9 (가로)</option>
                            <option value="9:16">9:16 (세로)</option>
                            <option value="1:1">1:1 (정사각형)</option>
                        </select>
                        <input type="text" id="styleInput" placeholder="스타일 (예: cinematic, photorealistic)" style="flex: 1; padding: 12px; border: 2px solid var(--border-color); border-radius: 8px; font-size: 14px; background: var(--bg-card); color: var(--text-primary);">
                        <label style="display: flex; align-items: center; gap: 5px; cursor: pointer;">
                            <input type="checkbox" id="useHaiku" style="width: 18px; height: 18px;">
                            <span style="color: var(--text-secondary); font-size: 14px;">Haiku 사용 (옵션)</span>
                        </label>
                        <button class="btn btn-primary" onclick="generatePrompt()">프롬프트 생성</button>
                    </div>
                    <div id="generatedPrompt" style="display: none; margin-top: 15px; padding: 15px; background: var(--success-bg); border-radius: 8px; border-left: 4px solid #27ae60;">
                        <div style="margin-bottom: 10px;">
                            <strong style="color: var(--success-text);">생성된 프롬프트:</strong>
                            <span id="modelInfo" style="margin-left: 10px; font-size: 12px; color: var(--text-secondary);"></span>
                        </div>
                        <div id="promptText" style="background: var(--bg-card); padding: 12px; border-radius: 6px; margin-bottom: 10px; font-family: monospace; word-break: break-all; color: var(--text-primary); max-height: 400px; overflow-y: auto;"></div>
                        <div style="display: flex; gap: 10px;">
                            <button class="btn btn-success" onclick="useGeneratedPrompt()" id="usePromptBtn" style="display: none;">첫 번째 프롬프트로 이미지 생성</button>
                            <button class="btn btn-warning" onclick="copyPrompt()">프롬프트 복사</button>
                        </div>
                    </div>
                </div>
                
                <div class="upload-section" style="margin-top: 20px;">
                    <h3>📤 새 이미지 생성</h3>
                    <div class="upload-row">
                        <input type="text" id="promptInput" placeholder="이미지 생성 프롬프트를 입력하세요 (영문)" style="background: var(--bg-card); color: var(--text-primary); border-color: var(--border-color);">
                        <input type="file" id="fileInput" accept="image/*" multiple style="background: var(--bg-card); color: var(--text-primary); border-color: var(--border-color);">
                        <button class="btn btn-primary" onclick="uploadImages()">업로드</button>
                        <button class="btn btn-success" onclick="generateNewImages()">Midjourney 생성</button>
                    </div>
                    <div id="status" class="status"></div>
                </div>
            </header>
            
            <div id="gallery">
    """
    
    if not groups:
        html += """
                <div class="empty-state">
                    <h2>📭 이미지가 없습니다</h2>
                    <p>위에서 프롬프트를 입력하고 이미지를 생성하거나 업로드하세요</p>
                </div>
        """
    else:
        for group in groups:
            prompt_hash = group["prompt_hash"]
            prompt = group["prompt"]
            images = prompt_manager.get_images_by_prompt(prompt_hash)
            
            # 가장 최신 이미지의 크롭된 이미지들 사용
            if images:
                latest = images[-1]
                cropped_paths = latest.get("cropped_paths", [])
                
                html += f"""
                <div class="prompt-group" data-prompt-hash="{prompt_hash}">
                    <div class="prompt-header">
                        <div class="prompt-text">
                            <strong>프롬프트:</strong> {prompt}
                            <div class="prompt-meta">
                                생성일: {group['created_at'][:10]} | 이미지 세트: {len(images)}개
                            </div>
                        </div>
                        <div class="prompt-actions">
                            <button class="btn btn-warning" onclick="regeneratePrompt('{prompt_hash}')">
                                🔄 재생성
                            </button>
                            <button class="btn btn-danger" onclick="deletePromptGroup('{prompt_hash}')">
                                🗑️ 전체 삭제
                            </button>
                        </div>
                    </div>
                    
                    <div class="images-grid">
                """
                
                # 4개 크롭 이미지 표시
                positions = ['top_left', 'top_right', 'bottom_left', 'bottom_right']
                for idx, position in enumerate(positions):
                    # 크롭된 이미지 경로 찾기
                    cropped_file = None
                    for path in cropped_paths:
                        if position in Path(path).name:
                            cropped_file = Path(path).name
                            break
                    
                    if cropped_file:
                        img_path = f"/cropped/{cropped_file}"
                        html += f"""
                        <div class="image-card" 
                             data-prompt-hash="{prompt_hash}"
                             data-image-index="{len(images)-1}"
                             data-crop-position="{position}"
                             onclick="toggleSelect(this)">
                            <div class="checkbox-overlay" onclick="event.stopPropagation(); toggleSelect(this.parentElement)"></div>
                            <img src="{img_path}" alt="{position}" onclick="openModal('{img_path}')">
                            <div class="image-label">{position.replace('_', ' ').title()}</div>
                        </div>
                        """
                    else:
                        html += f"""
                        <div class="image-card" style="background: #e0e0e0; display: flex; align-items: center; justify-content: center; color: #999;">
                            이미지 없음
                        </div>
                        """
                
                html += """
                    </div>
                    
                    <div class="selection-actions" id="selection-actions-""" + prompt_hash + """">
                        <strong>선택된 이미지:</strong> <span id="selected-count-""" + prompt_hash + """">0</span>개
                        <button class="btn btn-danger" style="margin-left: 15px;" onclick="deleteSelected('""" + prompt_hash + """')">
                            선택한 것만 남기고 나머지 삭제
                        </button>
                    </div>
                </div>
                """
    
    html += """
            </div>
        </div>
        
        <div id="modal" class="modal" onclick="this.style.display='none'">
            <span class="close">&times;</span>
            <img class="modal-content" id="modalImg">
        </div>
        
        <script>
            // 테마 관리
            function initTheme() {
                const savedTheme = localStorage.getItem('theme');
                const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
                const theme = savedTheme || (prefersDark ? 'dark' : 'light');
                document.documentElement.setAttribute('data-theme', theme);
                updateThemeIcon(theme);
            }
            
            function toggleTheme() {
                let currentTheme = document.documentElement.getAttribute('data-theme');
                // data-theme이 없으면 기본값 'light'로 설정
                if (!currentTheme) {
                    currentTheme = 'light';
                }
                const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
                document.documentElement.setAttribute('data-theme', newTheme);
                localStorage.setItem('theme', newTheme);
                updateThemeIcon(newTheme);
                
                // 디버깅용 콘솔 로그 (개발 중에만)
                console.log('Theme toggled to:', newTheme);
            }
            
            function updateThemeIcon(theme) {
                const toggle = document.getElementById('themeToggle');
                if (toggle) {
                    toggle.textContent = theme === 'dark' ? '☀️' : '🌙';
                    toggle.title = theme === 'dark' ? '라이트 모드로 전환' : '다크 모드로 전환';
                }
            }
            
            // DOMContentLoaded 이벤트로 테마 초기화 보장
            if (document.readyState === 'loading') {
                document.addEventListener('DOMContentLoaded', initTheme);
            } else {
                initTheme();
            }
            
            // 시스템 테마 변경 감지
            window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', (e) => {
                if (!localStorage.getItem('theme')) {
                    const theme = e.matches ? 'dark' : 'light';
                    document.documentElement.setAttribute('data-theme', theme);
                    updateThemeIcon(theme);
                }
            });
            
            // 전역으로 toggleTheme 함수 노출 (onclick 이벤트용)
            window.toggleTheme = toggleTheme;
            
            let selectedImages = {};
            
            function showStatus(message, type = 'info') {
                const statusDiv = document.getElementById('status');
                statusDiv.className = 'status ' + type;
                statusDiv.textContent = message;
                setTimeout(() => {
                    statusDiv.style.display = 'none';
                }, 5000);
            }
            
            function toggleSelect(card) {
                const promptHash = card.dataset.promptHash;
                const imageIndex = card.dataset.imageIndex;
                const cropPosition = card.dataset.cropPosition;
                const key = promptHash + '_' + imageIndex + '_' + cropPosition;
                
                if (!selectedImages[promptHash]) {
                    selectedImages[promptHash] = new Set();
                }
                
                if (selectedImages[promptHash].has(key)) {
                    selectedImages[promptHash].delete(key);
                    card.classList.remove('selected');
                    card.querySelector('.checkbox-overlay').classList.remove('checked');
                } else {
                    selectedImages[promptHash].add(key);
                    card.classList.add('selected');
                    card.querySelector('.checkbox-overlay').classList.add('checked');
                }
                
                updateSelectionUI(promptHash);
            }
            
            function updateSelectionUI(promptHash) {
                const count = selectedImages[promptHash] ? selectedImages[promptHash].size : 0;
                const actionsDiv = document.getElementById('selection-actions-' + promptHash);
                const countSpan = document.getElementById('selected-count-' + promptHash);
                
                if (count > 0) {
                    actionsDiv.classList.add('active');
                    countSpan.textContent = count;
                } else {
                    actionsDiv.classList.remove('active');
                }
            }
            
            function openModal(src) {
                document.getElementById('modal').style.display = 'block';
                document.getElementById('modalImg').src = src;
            }
            
            document.querySelector('.close').onclick = function() {
                document.getElementById('modal').style.display = 'none';
            };
            
            async function uploadImages() {
                const fileInput = document.getElementById('fileInput');
                const promptInput = document.getElementById('promptInput');
                const files = fileInput.files;
                
                if (files.length === 0) {
                    showStatus('파일을 선택하세요.', 'error');
                    return;
                }
                
                const prompt = promptInput.value.trim() || 'Uploaded image';
                
                showStatus('업로드 및 처리 중...', 'info');
                
                const formData = new FormData();
                for (let file of files) {
                    formData.append('files', file);
                }
                formData.append('prompt', prompt);
                
                try {
                    const response = await fetch('/api/upload', {
                        method: 'POST',
                        body: formData
                    });
                    
                    const data = await response.json();
                    if (data.success) {
                        showStatus('성공! ' + data.cropped_count + '개 이미지가 크롭되었습니다.', 'success');
                        setTimeout(() => location.reload(), 1500);
                    } else {
                        showStatus('실패: ' + data.error, 'error');
                    }
                } catch (error) {
                    showStatus('오류: ' + error.message, 'error');
                }
            }
            
            let generatedPromptText = '';
            
            async function generatePrompt() {
                const koreanInput = document.getElementById('koreanInput');
                const contextInput = document.getElementById('contextInput');
                const aspectRatio = document.getElementById('aspectRatio').value;
                const styleInput = document.getElementById('styleInput');
                const useHaiku = document.getElementById('useHaiku').checked;
                
                const inputText = koreanInput.value.trim();
                if (!inputText) {
                    showStatus('문장을 입력하세요.', 'error');
                    return;
                }
                
                // 여러 문장 분리 (줄바꿈으로 구분)
                const sentences = inputText.split('\n')
                    .map(s => s.trim())
                    .filter(s => s.length > 0);
                
                if (sentences.length === 0) {
                    showStatus('유효한 문장을 입력하세요.', 'error');
                    return;
                }
                
                const contextSentences = contextInput.value.trim()
                    ? contextInput.value.split(',').map(s => s.trim()).filter(s => s)
                    : [];
                
                const style = styleInput.value.trim() || null;
                
                // 여러 문장인 경우 배치 처리
                if (sentences.length > 1) {
                    showStatus(sentences.length + '개 문장의 프롬프트 생성 중... (GLM 4.6 사용)', 'info');
                    
                    try {
                        const response = await fetch('/api/generate-prompt-batch', {
                            method: 'POST',
                            headers: {'Content-Type': 'application/json'},
                            body: JSON.stringify({
                                target_sentences: sentences,
                                context_sentences: contextSentences,
                                aspect_ratio: aspectRatio,
                                style: style,
                                use_haiku: useHaiku
                            })
                        });
                        
                        const data = await response.json();
                        if (data.success) {
                            // 여러 프롬프트를 표시
                            const promptsHtml = data.prompts.map((p, idx) => {
                                const sentencePreview = sentences[idx].substring(0, 50) + (sentences[idx].length > 50 ? '...' : '');
                                return '<div style="margin-bottom: 15px; padding: 10px; background: var(--bg-section); border-radius: 6px;">' +
                                    '<div style="font-size: 12px; color: var(--text-secondary); margin-bottom: 5px;">문장 ' + (idx + 1) + ': ' + sentencePreview + '</div>' +
                                    '<div style="font-family: monospace; word-break: break-all; color: var(--text-primary);">' + p.prompt + '</div>' +
                                    '</div>';
                            }).join('');
                            
                            document.getElementById('promptText').innerHTML = promptsHtml;
                            document.getElementById('modelInfo').textContent = '(모델: ' + data.model_used + ', ' + sentences.length + '개 프롬프트 생성됨)';
                            document.getElementById('generatedPrompt').style.display = 'block';
                            document.getElementById('usePromptBtn').style.display = 'inline-block';
                            generatedPromptText = data.prompts.map(p => p.prompt).join('\n\n');
                            showStatus(sentences.length + '개 프롬프트 생성 완료!', 'success');
                        } else {
                            showStatus('실패: ' + data.error, 'error');
                        }
                    } catch (error) {
                        showStatus('오류: ' + error.message, 'error');
                    }
                } else {
                    // 단일 문장 처리
                    showStatus('프롬프트 생성 중... (GLM 4.6 사용)', 'info');
                    
                    try {
                        const response = await fetch('/api/generate-prompt', {
                            method: 'POST',
                            headers: {'Content-Type': 'application/json'},
                            body: JSON.stringify({
                                target_sentence: sentences[0],
                                context_sentences: contextSentences,
                                aspect_ratio: aspectRatio,
                                style: style,
                                use_haiku: useHaiku
                            })
                        });
                        
                        const data = await response.json();
                        if (data.success) {
                            generatedPromptText = data.prompt;
                            document.getElementById('promptText').textContent = data.prompt;
                            document.getElementById('modelInfo').textContent = '(모델: ' + data.model_used + ')';
                            document.getElementById('generatedPrompt').style.display = 'block';
                            document.getElementById('usePromptBtn').style.display = 'inline-block';
                            document.getElementById('usePromptBtn').textContent = '이 프롬프트로 이미지 생성';
                            showStatus('프롬프트 생성 완료!', 'success');
                        } else {
                            showStatus('실패: ' + data.error, 'error');
                        }
                    } catch (error) {
                        showStatus('오류: ' + error.message, 'error');
                    }
                }
            }
            
            function useGeneratedPrompt() {
                if (!generatedPromptText) {
                    showStatus('생성된 프롬프트가 없습니다.', 'error');
                    return;
                }
                // 여러 프롬프트인 경우 첫 번째만 사용
                const firstPrompt = generatedPromptText.split('\n\n')[0];
                document.getElementById('promptInput').value = firstPrompt;
                showStatus('첫 번째 프롬프트가 입력란에 복사되었습니다.', 'success');
            }
            
            function copyPrompt() {
                if (!generatedPromptText) {
                    showStatus('생성된 프롬프트가 없습니다.', 'error');
                    return;
                }
                navigator.clipboard.writeText(generatedPromptText).then(() => {
                    showStatus('프롬프트가 클립보드에 복사되었습니다.', 'success');
                }).catch(() => {
                    showStatus('복사 실패. 수동으로 복사해주세요.', 'error');
                });
            }
            
            async function generateNewImages() {
                const promptInput = document.getElementById('promptInput');
                const prompt = promptInput.value.trim();
                
                if (!prompt) {
                    showStatus('프롬프트를 입력하세요.', 'error');
                    return;
                }
                
                if (!confirm('"' + prompt + '" 프롬프트로 이미지를 생성하시겠습니까?\\n\\n이 작업은 몇 분이 걸릴 수 있습니다.')) {
                    return;
                }
                
                showStatus('이미지 생성 중... 잠시만 기다려주세요. (최대 5분)', 'info');
                
                try {
                    const response = await fetch('/api/generate', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({prompts: [prompt]})
                    });
                    
                    const data = await response.json();
                    if (data.success) {
                        showStatus('이미지 생성 요청이 전송되었습니다. 완료되면 자동으로 새로고침됩니다.', 'success');
                        checkGenerationStatus(data.job_id);
                    } else {
                        showStatus('실패: ' + data.error, 'error');
                    }
                } catch (error) {
                    showStatus('오류: ' + error.message, 'error');
                }
            }
            
            async function checkGenerationStatus(jobId) {
                const maxAttempts = 60;
                let attempts = 0;
                
                const checkInterval = setInterval(async () => {
                    attempts++;
                    try {
                        const response = await fetch('/api/generate/status/' + jobId);
                        const data = await response.json();
                        
                        if (data.completed) {
                            clearInterval(checkInterval);
                            showStatus('이미지 생성 완료!', 'success');
                            setTimeout(() => location.reload(), 2000);
                        } else if (attempts >= maxAttempts) {
                            clearInterval(checkInterval);
                            showStatus('타임아웃: 페이지를 새로고침하여 확인하세요.', 'error');
                        }
                    } catch (error) {
                        console.error('Status check error:', error);
                    }
                }, 5000);
            }
            
            async function regeneratePrompt(promptHash) {
                let prompt = '';
                try {
                    const response = await fetch('/api/prompts');
                    const data = await response.json();
                    const promptGroup = data.prompts.find(p => p.prompt_hash === promptHash);
                    if (promptGroup) {
                        prompt = promptGroup.prompt;
                    } else {
                        showStatus('프롬프트를 찾을 수 없습니다.', 'error');
                        return;
                    }
                } catch (error) {
                    showStatus('프롬프트를 가져오는데 실패했습니다.', 'error');
                    return;
                }
                
                if (!confirm('"' + prompt + '" 프롬프트로 이미지를 다시 생성하시겠습니까?')) {
                    return;
                }
                
                showStatus('이미지 재생성 중...', 'info');
                
                try {
                    const response = await fetch('/api/generate', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({prompts: [prompt]})
                    });
                    
                    const data = await response.json();
                    if (data.success) {
                        showStatus('재생성 요청이 전송되었습니다.', 'success');
                        checkGenerationStatus(data.job_id);
                    } else {
                        showStatus('실패: ' + data.error, 'error');
                    }
                } catch (error) {
                    showStatus('오류: ' + error.message, 'error');
                }
            }
            
            async function deletePromptGroup(promptHash) {
                if (!confirm('이 프롬프트의 모든 이미지를 삭제하시겠습니까?')) {
                    return;
                }
                
                try {
                    const response = await fetch('/api/prompt/' + promptHash, {
                        method: 'DELETE'
                    });
                    
                    const data = await response.json();
                    if (data.success) {
                        showStatus('삭제 완료', 'success');
                        setTimeout(() => location.reload(), 1000);
                    } else {
                        showStatus('실패: ' + data.error, 'error');
                    }
                } catch (error) {
                    showStatus('오류: ' + error.message, 'error');
                }
            }
            
            async function deleteSelected(promptHash) {
                const selected = selectedImages[promptHash];
                if (!selected || selected.size === 0) {
                    showStatus('선택된 이미지가 없습니다.', 'error');
                    return;
                }
                
                if (!confirm('선택한 ' + selected.size + '개 이미지를 제외하고 나머지를 삭제하시겠습니까?')) {
                    return;
                }
                
                try {
                    const response = await fetch('/api/prompt/' + promptHash + '/select', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({
                            selected_keys: Array.from(selected)
                        })
                    });
                    
                    const data = await response.json();
                    if (data.success) {
                        showStatus('삭제 완료', 'success');
                        selectedImages[promptHash] = new Set();
                        setTimeout(() => location.reload(), 1000);
                    } else {
                        showStatus('실패: ' + data.error, 'error');
                    }
                } catch (error) {
                    showStatus('오류: ' + error.message, 'error');
                }
            }
        </script>
    </body>
    </html>
    """
    
    return html


@app.post("/api/upload")
async def upload_images(
    files: List[UploadFile] = File(...),
    prompt: str = Form(...)
):
    """이미지 업로드 및 자동 크롭"""
    try:
        uploaded_count = 0
        cropped_count = 0
        
        for file in files:
            # 파일 저장
            file_path = IMAGES_DIR / file.filename
            with open(file_path, "wb") as f:
                content = await file.read()
                f.write(content)
            
            # 자동 크롭 및 저장
            result = process_and_save_image(
                image_path=str(file_path),
                prompt=prompt,
                image_urls=None
            )
            
            if result["success"]:
                uploaded_count += 1
                cropped_count += len(result["cropped_paths"])
        
        return JSONResponse({
            "success": True,
            "uploaded_count": uploaded_count,
            "cropped_count": cropped_count
        })
    except Exception as e:
        logger.error(f"업로드 실패: {e}")
        return JSONResponse(
            {"success": False, "error": str(e)},
            status_code=500
        )


# 생성 작업 추적
generation_jobs: Dict[str, Dict] = {}


@app.post("/api/generate")
async def generate_images(prompts: Dict):
    """Midjourney 이미지 생성 요청"""
    import asyncio
    import uuid
    
    try:
        prompt_list = prompts.get("prompts", [])
        if not prompt_list:
            return JSONResponse(
                {"success": False, "error": "프롬프트가 필요합니다"},
                status_code=400
            )
        
        job_id = str(uuid.uuid4())
        
        # 백그라운드 작업 시작
        generation_jobs[job_id] = {
            "status": "processing",
            "prompts": prompt_list,
            "results": []
        }
        
        # 비동기로 이미지 생성 실행
        async def run_generation():
            try:
                results = generate_images_batch(
                    prompts=prompt_list,
                    download_dir=str(IMAGES_DIR),
                    request_delay=2.0,
                    timeout_per_image=300,
                    verbose=False,
                    auto_crop=True,
                    auto_upload=SUPABASE_ENABLED
                )
                
                # 각 결과 처리 및 저장
                for result in results:
                    if result.success and result.downloaded_paths:
                        for img_path in result.downloaded_paths:
                            process_and_save_image(
                                image_path=img_path,
                                prompt=result.prompt,
                                image_urls=result.image_urls
                            )
                
                generation_jobs[job_id]["status"] = "completed"
                generation_jobs[job_id]["results"] = [
                    {
                        "prompt": r.prompt,
                        "success": r.success,
                        "image_count": len(r.downloaded_paths)
                    }
                    for r in results
                ]
            except Exception as e:
                logger.error(f"생성 실패: {e}")
                generation_jobs[job_id]["status"] = "failed"
                generation_jobs[job_id]["error"] = str(e)
        
        # 백그라운드 작업 시작
        asyncio.create_task(run_generation())
        
        return JSONResponse({
            "success": True,
            "job_id": job_id,
            "message": "이미지 생성이 시작되었습니다"
        })
    except Exception as e:
        logger.error(f"생성 요청 실패: {e}")
        return JSONResponse(
            {"success": False, "error": str(e)},
            status_code=500
        )


@app.get("/api/generate/status/{job_id}")
async def get_generation_status(job_id: str):
    """생성 작업 상태 확인"""
    if job_id not in generation_jobs:
        return JSONResponse(
            {"success": False, "error": "작업을 찾을 수 없습니다"},
            status_code=404
        )
    
    job = generation_jobs[job_id]
    return JSONResponse({
        "completed": job["status"] in ["completed", "failed"],
        "status": job["status"],
        "results": job.get("results", []),
        "error": job.get("error")
    })


@app.delete("/api/prompt/{prompt_hash}")
async def delete_prompt_group(prompt_hash: str):
    """프롬프트 그룹 전체 삭제"""
    try:
        images = prompt_manager.get_images_by_prompt(prompt_hash)
        
        # 파일 삭제
        for image_data in images:
            # 원본 삭제
            original_path = Path(image_data["original_path"])
            if original_path.exists():
                original_path.unlink()
            
            # 크롭된 이미지 삭제
            for cropped_path in image_data.get("cropped_paths", []):
                cropped_file = Path(cropped_path)
                if cropped_file.exists():
                    cropped_file.unlink()
        
        # 메타데이터에서 삭제
        prompt_manager.delete_prompt_group(prompt_hash)
        
        return JSONResponse({"success": True})
    except Exception as e:
        logger.error(f"삭제 실패: {e}")
        return JSONResponse(
            {"success": False, "error": str(e)},
            status_code=500
        )


@app.post("/api/prompt/{prompt_hash}/select")
async def keep_selected_images(prompt_hash: str, selection: Dict):
    """선택한 이미지만 남기고 나머지 삭제"""
    try:
        selected_keys = selection.get("selected_keys", [])
        images = prompt_manager.get_images_by_prompt(prompt_hash)
        
        # 선택된 이미지 인덱스 추출
        selected_indices = set()
        for key in selected_keys:
            # key 형식: promptHash_imageIndex_cropPosition
            parts = key.split('_')
            if len(parts) >= 2:
                try:
                    image_index = int(parts[1])
                    selected_indices.add(image_index)
                except:
                    pass
        
        # 선택되지 않은 이미지 삭제
        deleted_count = 0
        for idx in range(len(images) - 1, -1, -1):  # 역순으로 삭제
            if idx not in selected_indices:
                image_data = images[idx]
                
                # 원본 삭제
                original_path = Path(image_data["original_path"])
                if original_path.exists():
                    original_path.unlink()
                
                # 크롭된 이미지 삭제
                for cropped_path in image_data.get("cropped_paths", []):
                    cropped_file = Path(cropped_path)
                    if cropped_file.exists():
                        cropped_file.unlink()
                
                # 메타데이터에서 삭제
                prompt_manager.delete_image(prompt_hash, idx)
                deleted_count += 1
        
        return JSONResponse({
            "success": True,
            "deleted_count": deleted_count,
            "kept_count": len(selected_indices)
        })
    except Exception as e:
        logger.error(f"선택 삭제 실패: {e}")
        return JSONResponse(
            {"success": False, "error": str(e)},
            status_code=500
        )


@app.get("/api/prompts")
async def list_prompts():
    """프롬프트 목록 API"""
    groups = prompt_manager.get_prompt_groups()
    return JSONResponse({"prompts": groups})


@app.post("/api/generate-prompt")
async def generate_prompt(request: Dict):
    """문장을 Midjourney 프롬프트로 변환 (GLM 4.6 사용)"""
    try:
        target_sentence = request.get("target_sentence", "")
        context_sentences = request.get("context_sentences", [])
        aspect_ratio = request.get("aspect_ratio", "16:9")
        style = request.get("style")
        use_haiku = request.get("use_haiku", False)  # 옵션: Haiku 사용 여부
        
        if not target_sentence:
            return JSONResponse(
                {"success": False, "error": "문장이 필요합니다"},
                status_code=400
            )
        
        # 모델 선택: 기본값은 GLM 4.6, 옵션으로 Haiku 사용 가능
        from src.ai.api_client import ModelType
        model = ModelType.CLAUDE_HAIKU_4_5 if use_haiku else None
        
        # 프롬프트 생성 (GLM 4.6 기본값)
        generator = MidjourneyPromptGenerator(model=model)
        result = generator.generate_prompt(
            target_sentence=target_sentence,
            context_sentences=context_sentences,
            aspect_ratio=aspect_ratio,
            style=style
        )
        
        return JSONResponse({
            "success": True,
            "prompt": result.get("prompt", ""),
            "explanation": result.get("explanation", ""),
            "keywords": result.get("keywords", []),
            "model_used": "GLM-4.6" if not use_haiku else "Claude-Haiku-4.5"
        })
        
    except Exception as e:
        logger.error(f"프롬프트 생성 실패: {e}")
        return JSONResponse(
            {"success": False, "error": str(e)},
            status_code=500
        )


@app.post("/api/generate-prompt-batch")
async def generate_prompt_batch(request: Dict):
    """여러 문장을 배치로 Midjourney 프롬프트로 변환 (GLM 4.6 사용)"""
    try:
        target_sentences = request.get("target_sentences", [])
        context_sentences = request.get("context_sentences", [])
        aspect_ratio = request.get("aspect_ratio", "16:9")
        style = request.get("style")
        use_haiku = request.get("use_haiku", False)
        
        if not target_sentences or len(target_sentences) == 0:
            return JSONResponse(
                {"success": False, "error": "문장이 필요합니다"},
                status_code=400
            )
        
        # 모델 선택
        from src.ai.api_client import ModelType
        model = ModelType.CLAUDE_HAIKU_4_5 if use_haiku else None
        
        # 배치 프롬프트 생성
        generator = MidjourneyPromptGenerator(model=model)
        results = generator.generate_batch_prompts(
            target_sentences=target_sentences,
            context_sentences_map={i: context_sentences for i in range(len(target_sentences))} if context_sentences else None,
            aspect_ratio=aspect_ratio,
            style=style
        )
        
        prompts = [
            {
                "prompt": r.get("prompt", ""),
                "explanation": r.get("explanation", ""),
                "keywords": r.get("keywords", [])
            }
            for r in results
        ]
        
        return JSONResponse({
            "success": True,
            "prompts": prompts,
            "model_used": "GLM-4.6" if not use_haiku else "Claude-Haiku-4.5"
        })
        
    except Exception as e:
        logger.error(f"배치 프롬프트 생성 실패: {e}")
        return JSONResponse(
            {"success": False, "error": str(e)},
            status_code=500
        )


if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)

