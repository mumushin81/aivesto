"""Midjourney 프롬프트 생성기 - LLM을 활용한 영문 프롬프트 작성"""
import os
import asyncio
from pathlib import Path
from typing import List, Optional, Dict, Union
import logging
import json
import re

from src.ai.api_client import LLMAPIClient, ModelType
from src.ai.chat_ai.glm_api import GLMClient, GLMRequest

logger = logging.getLogger(__name__)


class MidjourneyPromptGenerator:
    """타겟 문장과 배경 문장을 기반으로 Midjourney 프롬프트 생성"""
    
    def __init__(self, 
                 model: Optional[Union[ModelType, str]] = None,
                 guide_path: Optional[str] = None,
                 use_glm: bool = True):
        """
        Args:
            model: 사용할 LLM 모델 
                - None 또는 "glm" 또는 "glm-4.6": GLM 4.6 사용 (기본값, 비용 효율적)
                - ModelType.CLAUDE_HAIKU_4_5: Claude Haiku 4.5 사용 (옵션)
            guide_path: Midjourney 프롬프트 가이드 파일 경로
            use_glm: GLM 4.6 사용 여부 (기본값: True, model이 None일 때만 적용)
        """
        # 모델 설정: 기본값은 GLM 4.6
        if model is None:
            self.use_glm = True
            self.model = "GLM-4.6"
        elif isinstance(model, str) and (model.lower() == "glm" or model.lower() == "glm-4.6"):
            self.use_glm = True
            self.model = "GLM-4.6"
        elif isinstance(model, ModelType) and model == ModelType.CLAUDE_HAIKU_4_5:
            self.use_glm = False
            self.model = model
        else:
            # 기본값으로 GLM 4.6 사용
            self.use_glm = True
            self.model = "GLM-4.6"
            logger.warning(f"알 수 없는 모델: {model}, GLM 4.6을 기본값으로 사용합니다.")
        
        # 클라이언트 초기화
        if self.use_glm:
            self.glm_client = GLMClient()
            self.llm_client = None
        else:
            self.llm_client = LLMAPIClient(default_model=self.model)
            self.glm_client = None
        
        # 가이드 파일 경로 설정
        if guide_path is None:
            base_dir = Path(__file__).parent.parent.parent
            guide_path = str(base_dir / "docs" / "midjourney_prompt_guide.md")
        
        self.guide_path = Path(guide_path)
        self.prompt_guide = self._load_guide()
    
    def _load_guide(self) -> str:
        """Midjourney 프롬프트 가이드 로드"""
        try:
            if self.guide_path.exists():
                with open(self.guide_path, 'r', encoding='utf-8') as f:
                    return f.read()
            else:
                logger.warning(f"가이드 파일을 찾을 수 없습니다: {self.guide_path}")
                return ""
        except Exception as e:
            logger.error(f"가이드 파일 로드 실패: {e}")
            return ""
    
    def generate_prompt(
        self,
        target_sentence: str,
        context_sentences: Optional[List[str]] = None,
        aspect_ratio: str = "16:9",
        style: Optional[str] = None,
        additional_params: Optional[Dict[str, str]] = None
    ) -> Dict[str, str]:
        """
        타겟 문장과 배경 문장을 기반으로 Midjourney 프롬프트 생성
        
        Args:
            target_sentence: 타겟 문장 (이미지로 표현할 핵심 문장)
            context_sentences: 배경 문장 리스트 (맥락 제공)
            aspect_ratio: 이미지 비율 (기본값: "16:9")
            style: 스타일 힌트 (예: "cinematic", "photorealistic", "illustration")
            additional_params: 추가 파라미터 (예: {"chaos": "50", "stylize": "200"})
        
        Returns:
            {
                "prompt": "생성된 영문 프롬프트",
                "explanation": "프롬프트 설명",
                "keywords": ["추출된", "주요", "키워드"]
            }
        """
        # 시스템 프롬프트 구성
        system_prompt = self._build_system_prompt()
        
        # 사용자 프롬프트 구성
        user_prompt = self._build_user_prompt(
            target_sentence=target_sentence,
            context_sentences=context_sentences or [],
            aspect_ratio=aspect_ratio,
            style=style,
            additional_params=additional_params or {}
        )
        
        # LLM 호출
        try:
            if self.use_glm:
                # GLM 4.6 사용
                response = asyncio.run(self._generate_with_glm(user_prompt, system_prompt))
            else:
                # Claude Haiku 사용
                messages = [
                    {"role": "user", "content": user_prompt}
                ]
                response = self.llm_client.generate(
                    prompt=messages,
                    model=self.model,
                    max_tokens=1000,
                    temperature=0.7,  # 창의성을 위한 적절한 온도
                    system_prompt=system_prompt
                )
            
            # 응답 파싱
            result = self._parse_response(response)
            return result
            
        except Exception as e:
            logger.error(f"프롬프트 생성 실패: {e}")
            # 폴백: 기본 프롬프트 생성
            return self._generate_fallback_prompt(
                target_sentence, context_sentences, aspect_ratio, style, additional_params
            )
    
    async def _generate_with_glm(self, user_prompt: str, system_prompt: str) -> str:
        """GLM 4.6을 사용하여 텍스트 생성"""
        request = GLMRequest(
            prompt=user_prompt,
            model="GLM-4.6",
            system_prompt=system_prompt,
            temperature=0.7,
            max_tokens=1000
        )
        response = await self.glm_client.generate_completion(request)
        return response.data
    
    def _build_system_prompt(self) -> str:
        """시스템 프롬프트 구성 - 영문으로만 응답하도록 강제"""
        guide_section = self.prompt_guide[:3000] if self.prompt_guide else ""  # 가이드의 일부만 사용
        
        return f"""You are an expert Midjourney prompt engineer specializing in creating high-quality, professional English prompts for Midjourney image generation.

CRITICAL REQUIREMENT: You MUST ALWAYS generate prompts in ENGLISH ONLY, regardless of the input language. Even if the input is in Korean or any other language, translate it to English and create the prompt entirely in English.

{guide_section}

=== MIDJOURNEY PROMPT BEST PRACTICES ===

1. PROMPT STRUCTURE (Order matters!):
   [Subject/Character/Object] + [Action/Pose/State] + [Setting/Environment] + [Style/Artistic Direction] + [Lighting/Atmosphere] + [Composition/Camera] + [Technical Quality] + [Parameters]

2. ESSENTIAL KEYWORD CATEGORIES:

   SUBJECT:
   - Be specific: "young woman" not "person", "vintage car" not "car"
   - Include details: age, gender, clothing, expression, pose
   
   STYLE & ARTISTIC DIRECTION:
   - Art styles: photorealistic, cinematic, oil painting, watercolor, digital art, concept art, illustration
   - Genres: fantasy, sci-fi, cyberpunk, steampunk, noir, vintage, modern
   - Artistic movements: impressionist, surrealist, minimalist, baroque, art nouveau
   
   LIGHTING & ATMOSPHERE:
   - Natural: golden hour, sunset, sunrise, midday sun, overcast, moonlight, starlight
   - Artificial: neon lights, candlelight, firelight, studio lighting, dramatic lighting
   - Mood: warm, cool, dramatic, soft, harsh, ethereal, mysterious
   
   COMPOSITION & CAMERA:
   - Angles: close-up, medium shot, wide shot, aerial view, bird's eye view, worm's eye view
   - Framing: centered, rule of thirds, leading lines, symmetry, depth of field
   - Camera: 35mm, 50mm, 85mm, telephoto, wide-angle, macro
   - Focus: sharp focus, bokeh, shallow depth of field, everything in focus
   
   TECHNICAL QUALITY:
   - Resolution: 4K, 8K, ultra high definition, high resolution
   - Quality: detailed, intricate, sharp, crisp, professional, award-winning
   - Rendering: octane render, unreal engine, ray tracing, volumetric lighting

3. MIDJOURNEY PARAMETERS (Always include appropriate ones):
   - --ar [ratio]: Aspect ratio (16:9, 9:16, 1:1, 4:3, 3:2, etc.)
   - --v [version]: Model version (--v 6 for latest, --v 5.2, --v 5.1, etc.)
   - --stylize [0-1000]: Style strength (default 100, higher = more artistic)
   - --chaos [0-100]: Variation level (0-100, higher = more varied results)
   - --quality [.25/.5/1]: Quality setting (1 = default, higher = slower but better)
   - --seed [number]: For reproducibility
   - --no [word]: Negative prompt (e.g., --no blur, --no text)

CRITICAL: You MUST ALWAYS include --no text parameter in every prompt to prevent any text, words, letters, or written characters from appearing in the generated image. This is a mandatory requirement for all prompts.

4. KEYWORD SELECTION RULES:
   - Use concrete, visual words: "crimson sunset" not "beautiful time"
   - Be specific: "Victorian-era mansion" not "old house"
   - Include sensory details: "rustling leaves", "glossy surface", "rough texture"
   - Avoid abstract concepts: translate emotions to visual elements
   - Use professional photography/art terminology when appropriate

5. TRANSLATION STRATEGY:
   - When input is Korean: Translate meaning, not word-by-word
   - Preserve cultural context: "hanbok" → "traditional Korean hanbok dress"
   - Convert abstract concepts to visual descriptions
   - Maintain emotional tone through visual elements

=== OUTPUT REQUIREMENTS ===

CRITICAL: The output prompt MUST be 100% in English. No Korean, Chinese, or any other language characters allowed in the final prompt.

Output format (JSON only):
{{
    "prompt": "Complete Midjourney prompt in English ONLY - subject, style, lighting, composition, quality keywords, and parameters",
    "explanation": "Brief explanation in English of key visual elements and choices",
    "keywords": ["key", "visual", "keywords", "in", "english"]
}}

The prompt field must contain ONLY English words, proper Midjourney syntax, and parameters. Never include Korean characters or any non-English text in the prompt field."""
    
    def _build_user_prompt(
        self,
        target_sentence: str,
        context_sentences: List[str],
        aspect_ratio: str,
        style: Optional[str],
        additional_params: Dict[str, str]
    ) -> str:
        """사용자 프롬프트 구성 - 영문으로 작성"""
        prompt_parts = []
        
        prompt_parts.append("=== TASK: CREATE MIDJOURNEY PROMPT ===")
        prompt_parts.append("\nIMPORTANT: The input may be in Korean or other languages, but you MUST create the output prompt ENTIRELY in English.")
        prompt_parts.append("Translate the meaning and create a professional English Midjourney prompt.")
        
        prompt_parts.append("\n=== INPUT (May be in Korean) ===")
        prompt_parts.append(f"Target Sentence: {target_sentence}")
        
        if context_sentences:
            prompt_parts.append(f"\nContext Sentences (for mood/atmosphere):")
            for idx, ctx in enumerate(context_sentences, 1):
                prompt_parts.append(f"  {idx}. {ctx}")
        
        prompt_parts.append(f"\n=== REQUIREMENTS ===")
        prompt_parts.append(f"Aspect Ratio: {aspect_ratio}")
        
        if style:
            prompt_parts.append(f"Style Preference: {style}")
        
        if additional_params:
            prompt_parts.append(f"Additional Parameters: {additional_params}")
        
        prompt_parts.append("\n=== YOUR TASK ===")
        prompt_parts.append("1. Translate the Korean input to English (if needed)")
        prompt_parts.append("2. Extract all visual elements: subject, setting, mood, atmosphere")
        prompt_parts.append("3. Create a detailed Midjourney prompt following the structure:")
        prompt_parts.append("   [Subject/Object] + [Action/State] + [Setting] + [Style] + [Lighting] + [Composition] + [Quality] + [Parameters]")
        prompt_parts.append("4. Use specific, visual English keywords only")
        prompt_parts.append("5. Include appropriate Midjourney parameters (--ar, --v, --stylize, etc.)")
        prompt_parts.append("6. MANDATORY: Always include --no text parameter to prevent any text, words, or letters in the image")
        prompt_parts.append("\nCRITICAL: The output prompt MUST be 100% in English. No Korean characters allowed.")
        prompt_parts.append("CRITICAL: The output prompt MUST include --no text parameter to ensure no text appears in the image.")
        prompt_parts.append("\nRespond with JSON format only.")
        
        return "\n".join(prompt_parts)
    
    def _parse_response(self, response: str) -> Dict[str, str]:
        """LLM 응답 파싱 - 영문만 추출"""
        # JSON 추출 시도
        # 여러 패턴으로 시도
        json_patterns = [
            r'\{[^{}]*(?:"prompt"|"explanation"|"keywords")[^{}]*\}',  # 간단한 JSON
            r'\{.*?"prompt".*?\}',  # prompt 포함
            r'```json\s*(\{.*?\})\s*```',  # 코드 블록
            r'```\s*(\{.*?\})\s*```',  # 일반 코드 블록
        ]
        
        for pattern in json_patterns:
            json_match = re.search(pattern, response, re.DOTALL)
            if json_match:
                json_str = json_match.group(1) if json_match.lastindex else json_match.group()
                try:
                    result = json.loads(json_str)
                    prompt = result.get("prompt", "")
                    
                    # 한국어 제거 (혹시 모를 경우 대비)
                    prompt = self._remove_korean_from_prompt(prompt)
                    
                    # 텍스트 제외 파라미터 추가 (없으면 추가)
                    prompt = self._ensure_no_text_parameter(prompt)
                    
                    return {
                        "prompt": prompt,
                        "explanation": result.get("explanation", ""),
                        "keywords": result.get("keywords", [])
                    }
                except json.JSONDecodeError:
                    continue
        
        # JSON이 없으면 프롬프트만 추출
        # --ar 또는 --v로 시작하는 라인 찾기
        lines = response.strip().split('\n')
        prompt_lines = []
        found_prompt = False
        
        for line in lines:
            # 프롬프트 시작 감지
            if '--ar' in line or '--v' in line or 'prompt' in line.lower():
                found_prompt = True
            
            if found_prompt:
                # JSON 키 제거
                line = re.sub(r'^["\']?prompt["\']?\s*[:=]\s*["\']?', '', line)
                line = re.sub(r'["\']?\s*[,}]?\s*$', '', line)
                if line.strip():
                    prompt_lines.append(line.strip())
        
        # 프롬프트가 없으면 전체 응답 사용
        prompt = ' '.join(prompt_lines) if prompt_lines else response.strip()
        
        # 불필요한 문자 제거
        prompt = re.sub(r'^["\']', '', prompt)
        prompt = re.sub(r'["\']$', '', prompt)
        
        # 한국어 제거
        prompt = self._remove_korean_from_prompt(prompt)
        
        # 텍스트 제외 파라미터 추가 (없으면 추가)
        prompt = self._ensure_no_text_parameter(prompt)
        
        return {
            "prompt": prompt,
            "explanation": "Generated prompt based on input",
            "keywords": []
        }
    
    def _remove_korean_from_prompt(self, prompt: str) -> str:
        """프롬프트에서 한국어 문자 제거 (영문만 유지)"""
        # 한국어 문자 범위: \uac00-\ud7a3
        # 한글 자모: \u1100-\u11ff, \u3130-\u318f
        korean_pattern = r'[\uac00-\ud7a3\u1100-\u11ff\u3130-\u318f]+'
        
        # 한국어가 포함되어 있으면 경고하고 제거
        if re.search(korean_pattern, prompt):
            logger.warning("Korean characters detected in prompt. Removing Korean text.")
            # 한국어 부분을 제거하되, 주변 공백 정리
            prompt = re.sub(korean_pattern, '', prompt)
            prompt = re.sub(r'\s+', ' ', prompt).strip()
        
        return prompt
    
    def _ensure_no_text_parameter(self, prompt: str) -> str:
        """프롬프트에 --no text 파라미터가 없으면 추가"""
        # 이미 --no text, --no words, --no letters 등이 있는지 확인
        no_text_patterns = [
            r'--no\s+text',
            r'--no\s+words',
            r'--no\s+letters',
            r'--no\s+writing',
            r'--no\s+typography'
        ]
        
        has_no_text = any(re.search(pattern, prompt, re.IGNORECASE) for pattern in no_text_patterns)
        
        if not has_no_text:
            # 프롬프트 끝에 --no text 추가
            # 파라미터가 이미 있으면 그 앞에, 없으면 끝에 추가
            if '--' in prompt:
                # 마지막 파라미터 뒤에 추가
                prompt = prompt.rstrip() + ' --no text'
            else:
                # 파라미터가 없으면 끝에 추가
                prompt = prompt.rstrip() + ' --no text'
            logger.info("Added --no text parameter to prevent text in generated image")
        
        return prompt
    
    def _generate_fallback_prompt(
        self,
        target_sentence: str,
        context_sentences: List[str],
        aspect_ratio: str,
        style: Optional[str],
        additional_params: Dict[str, str]
    ) -> Dict[str, str]:
        """LLM 실패 시 기본 프롬프트 생성 - 영문으로만"""
        # 기본 스타일 추가
        if not style:
            style = "cinematic"
        
        # 한국어가 포함되어 있으면 간단한 영문 변환 시도
        # 실제로는 번역 API를 사용해야 하지만, 여기서는 기본 영문 프롬프트 생성
        # 한국어 문장이 포함되어 있으면 경고와 함께 기본 영문 프롬프트 생성
        
        # 기본 프롬프트 구성 (영문만)
        prompt_parts = [
            f"A {style} scene",
            "detailed, high quality, professional photography",
            "cinematic lighting, dramatic atmosphere",
            f"--ar {aspect_ratio}",
            "--v 6",
            "--stylize 100",
            "--no text"  # 텍스트 제외 (필수)
        ]
        
        # 추가 파라미터
        if additional_params:
            for key, value in additional_params.items():
                prompt_parts.append(f"--{key} {value}")
        
        prompt = ", ".join(prompt_parts)
        
        # 한국어가 포함되어 있으면 경고
        if any('\uac00' <= char <= '\ud7a3' for char in target_sentence):
            logger.warning("Korean text detected in fallback prompt. Using generic English prompt instead.")
            prompt = f"A {style} cinematic scene, detailed composition, professional photography, dramatic lighting, high quality, --ar {aspect_ratio}, --v 6, --stylize 100, --no text"
        
        # 텍스트 제외 파라미터 확인 (혹시 모를 경우 대비)
        prompt = self._ensure_no_text_parameter(prompt)
        
        return {
            "prompt": prompt,
            "explanation": "Fallback prompt generated using generic English keywords (translation may be needed)",
            "keywords": [style, "cinematic", "detailed", "high quality"]
        }
    
    def generate_batch_prompts(
        self,
        target_sentences: List[str],
        context_sentences_map: Optional[Dict[int, List[str]]] = None,
        aspect_ratio: str = "16:9",
        style: Optional[str] = None
    ) -> List[Dict[str, str]]:
        """
        여러 문장에 대한 프롬프트 배치 생성
        
        Args:
            target_sentences: 타겟 문장 리스트
            context_sentences_map: 인덱스별 배경 문장 맵 (선택적)
            aspect_ratio: 이미지 비율
            style: 스타일 힌트
        
        Returns:
            프롬프트 딕셔너리 리스트
        """
        results = []
        context_sentences_map = context_sentences_map or {}
        
        for idx, target in enumerate(target_sentences):
            context = context_sentences_map.get(idx, [])
            result = self.generate_prompt(
                target_sentence=target,
                context_sentences=context,
                aspect_ratio=aspect_ratio,
                style=style
            )
            results.append(result)
        
        return results


def generate_midjourney_prompt(
    target_sentence: str,
    context_sentences: Optional[List[str]] = None,
    aspect_ratio: str = "16:9",
    style: Optional[str] = None,
    model: Optional[Union[ModelType, str]] = None
) -> str:
    """
    간편한 프롬프트 생성 함수
    
    Args:
        target_sentence: 타겟 문장
        context_sentences: 배경 문장 리스트
        aspect_ratio: 이미지 비율
        style: 스타일 힌트
        model: 사용할 LLM 모델
            - None 또는 "glm": GLM 4.6 사용 (기본값, 비용 효율적)
            - ModelType.CLAUDE_HAIKU_4_5: Claude Haiku 4.5 사용 (옵션)
    
    Returns:
        생성된 Midjourney 프롬프트 문자열
    """
    generator = MidjourneyPromptGenerator(model=model)
    result = generator.generate_prompt(
        target_sentence=target_sentence,
        context_sentences=context_sentences,
        aspect_ratio=aspect_ratio,
        style=style
    )
    return result["prompt"]
