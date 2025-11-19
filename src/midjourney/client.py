"""Midjourney Discord API 클라이언트"""
import os
import requests
import time
import re
from datetime import datetime
from typing import Optional, List, Dict, Union, Any
from dataclasses import dataclass
import hashlib
from pathlib import Path
from io import BytesIO

from . import config as Globals

# Discord API 상수는 config에서 가져옴
APPLICATION_ID = Globals.APPLICATION_ID
APPLICATION_DATA_VERSION = Globals.APPLICATION_DATA_VERSION
APPLICATION_DATA_ID = Globals.APPLICATION_DATA_ID
SESSION_ID = Globals.SESSION_ID


def upload_image_to_discord(image_path: Union[str, Path]) -> Optional[str]:
    """
    이미지를 Discord 채널에 업로드하고 URL을 반환합니다.
    
    Args:
        image_path: 업로드할 이미지 파일 경로
    
    Returns:
        업로드된 이미지 URL, 실패 시 None
    """
    image_path = Path(image_path)
    if not image_path.exists():
        print(f"✗ 이미지 파일을 찾을 수 없습니다: {image_path}")
        return None
    
    # 파일 확장자로 MIME 타입 결정
    ext = image_path.suffix.lower()
    mime_types = {
        '.png': 'image/png',
        '.jpg': 'image/jpeg',
        '.jpeg': 'image/jpeg',
        '.gif': 'image/gif',
        '.webp': 'image/webp'
    }
    content_type = mime_types.get(ext, 'image/png')
    
    header = {
        'authorization': Globals.SALAI_TOKEN
    }
    
    # Discord 채널에 이미지 업로드
    url = f"https://discord.com/api/v9/channels/{Globals.CHANNEL_ID_WONDER}/messages"
    
    try:
        # 파일을 읽어서 BytesIO로 업로드
        with open(image_path, 'rb') as f:
            file_content = BytesIO(f.read())
        
        files = {
            'file': (image_path.name, file_content, content_type)
        }
        payload = {
            'content': ''  # 빈 메시지로 이미지만 업로드
        }
        
        response = requests.post(
            url,
            headers=header,
            data=payload,
            files=files,
            timeout=30
        )
        
        if response.status_code == 200:
            message_data = response.json()
            # attachments에서 이미지 URL 추출
            if 'attachments' in message_data and message_data['attachments']:
                image_url = message_data['attachments'][0].get('url')
                print(f"✓ 이미지 업로드 성공: {image_url}")
                return image_url
            else:
                print("✗ 업로드 응답에 이미지 URL이 없습니다")
                return None
        else:
            print(f"✗ 이미지 업로드 실패: HTTP {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"✗ 이미지 업로드 중 오류: {e}")
        return None


def PassPromptToSelfBot(prompt: str, image_paths: Optional[List[Union[str, Path]]] = None):
    """
    Midjourney에 프롬프트를 전송합니다. 이미지 첨부를 지원합니다.
    
    Args:
        prompt: 이미지 생성 프롬프트
        image_paths: 참조 이미지 파일 경로 리스트 (선택사항)
    
    My way to find this version number is:
        Open discord in chrome browser and type F12 to open dev pannel
        Interact with Midjourney bot using the command you want
        Then go check dev pannel and select tab Network
        Search for "interactions" and click on filtered result named also as "interactions"
        Once you click on the result, it will display headers information. Then select Payload tab on the right side
        You can see all the information you want.
        Please notice that there are two places of version information in the PassPromptToSelfBot function, I suppose you need to update both.

        Image shows some keypoint from the above instruction.
    """
    # 이미지가 있으면 먼저 업로드하고 URL을 프롬프트에 추가
    image_urls = []
    if image_paths:
        for img_path in image_paths:
            img_url = upload_image_to_discord(img_path)
            if img_url:
                image_urls.append(img_url)
        
        # 이미지 URL을 프롬프트에 추가 (Midjourney는 이미지 URL을 프롬프트에 포함)
        if image_urls:
            # 각 이미지 URL을 프롬프트 앞에 추가
            image_refs = ' '.join(image_urls)
            prompt = f"{image_refs} {prompt}"
            print(f"✓ {len(image_urls)}개 이미지 참조 추가됨")
    
    payload = {"type": 2,
               "application_id": APPLICATION_ID,
               "guild_id": Globals.SERVER_ID,
               "channel_id": Globals.CHANNEL_ID_WONDER,
               "session_id": SESSION_ID,
               "analytics_location": "slash_ui",
               "data": {
                   "version": APPLICATION_DATA_VERSION,
                   "id": APPLICATION_DATA_ID,
                   "name": "imagine",
                   "type": 1,
                   "options": [{"type": 3, "name": "prompt", "value": prompt}],
                   "application_command": {
                       "id": APPLICATION_DATA_ID,
                       "type": 1,
                       "application_id": APPLICATION_ID,
                       "version": APPLICATION_DATA_VERSION,
                       "name": "imagine",
                       "description": "Create images with Midjourney",
                       "options": [{"type": 3, "name": "prompt",
                                    "description": "The prompt to imagine",
                                    "required": True}]
                   },
                   "attachments": []
               }}

    header = {
        'authorization': Globals.SALAI_TOKEN
    }
    response = requests.post(
        "https://discord.com/api/v9/interactions",
        json=payload,
        headers=header,
        timeout=30
    )
    print('PassPromptToSelfBot:', response)
    return response


def Upscale(index: int, messageId: str, messageHash: str):
    payload = {"type": 3,
               "guild_id": Globals.SERVER_ID,
               "channel_id": Globals.CHANNEL_ID_WONDER,
               "message_flags": 0,
               "message_id": messageId,
               "session_id": SESSION_ID,
               "application_id": APPLICATION_ID,
               "data": {"component_type": 2,
                        "custom_id": "MJ::JOB::upsample::{}::{}".format(index, messageHash)}
               }
    header = {
        'authorization': Globals.SALAI_TOKEN
    }
    response = requests.post(
        "https://discord.com/api/v9/interactions",
        json=payload,
        headers=header,
        timeout=30
    )
    print(response)
    return response


def MaxUpscale(messageId: str, messageHash: str):
    payload = {"type": 3,
               "guild_id": Globals.SERVER_ID,
               "channel_id": Globals.CHANNEL_ID_WONDER,
               "message_flags": 0,
               "message_id": messageId,
               "application_id": APPLICATION_ID,
               "session_id": SESSION_ID, "data":
                   {"component_type": 2, "custom_id": "MJ::JOB::upsample_max::1::{}::SOLO".format(messageHash)}}
    header = {
        'authorization': Globals.SALAI_TOKEN
    }
    response = requests.post(
        "https://discord.com/api/v9/interactions",
        json=payload,
        headers=header,
        timeout=30
    )
    return response


def Variation(index: int, messageId: str, messageHash: str):
    payload = {"type": 3, "guild_id": Globals.SERVER_ID,
               "channel_id": Globals.CHANNEL_ID_WONDER,
               "message_flags": 0,
               "message_id": messageId,
               "application_id": APPLICATION_ID,
               "session_id": SESSION_ID,
               "data": {"component_type": 2, "custom_id": "MJ::JOB::variation::{}::{}".format(index, messageHash)}}
    header = {
        'authorization': Globals.SALAI_TOKEN
    }
    response = requests.post(
        "https://discord.com/api/v9/interactions",
        json=payload,
        headers=header,
        timeout=30
    )
    return response


def get_channel_messages(limit: int = 10) -> List[Dict]:
    """
    Discord 채널의 최근 메시지를 가져옵니다.
    
    Args:
        limit: 가져올 메시지 개수 (최대 100)
    
    Returns:
        메시지 리스트
    """
    header = {
        'authorization': Globals.SALAI_TOKEN
    }
    url = (f"https://discord.com/api/v9/channels/"
           f"{Globals.CHANNEL_ID_WONDER}/messages?limit={limit}")
    response = requests.get(url, headers=header, timeout=30)
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"메시지 가져오기 실패: {response.status_code} - {response.text}")
        return []


def extract_image_urls_from_message(message: Dict) -> List[str]:
    """
    Discord 메시지에서 이미지 URL을 추출합니다.
    
    Args:
        message: Discord 메시지 객체
    
    Returns:
        이미지 URL 리스트
    """
    image_urls = []
    
    # 1. attachments에서 이미지 URL 추출
    if 'attachments' in message and message['attachments']:
        for attachment in message['attachments']:
            if attachment.get('content_type', '').startswith('image/'):
                image_urls.append(attachment.get('url'))
            elif attachment.get('url'):
                # 확장자로 이미지인지 확인
                url = attachment.get('url')
                ext_list = ['.png', '.jpg', '.jpeg', '.gif', '.webp']
                if any(url.lower().endswith(ext) for ext in ext_list):
                    image_urls.append(url)
    
    # 2. embeds에서 이미지 URL 추출
    if 'embeds' in message and message['embeds']:
        for embed in message['embeds']:
            if 'image' in embed and 'url' in embed['image']:
                image_urls.append(embed['image']['url'])
            if 'thumbnail' in embed and 'url' in embed['thumbnail']:
                image_urls.append(embed['thumbnail']['url'])
    
    # 3. 메시지 내용에서 이미지 URL 추출 (Midjourney는 보통 CDN URL을 포함)
    if 'content' in message and message['content']:
        # Discord CDN URL 패턴 찾기
        cdn_pattern = (
            r'https://cdn\.discordapp\.com/attachments/'
            r'\d+/\d+/[^\s\)]+\.(?:png|jpg|jpeg|gif|webp)'
        )
        urls = re.findall(cdn_pattern, message['content'])
        image_urls.extend(urls)

        # Midjourney 이미지 URL 패턴 찾기
        mj_pattern = r'https://[^\s\)]+\.(?:png|jpg|jpeg|gif|webp)'
        mj_urls = re.findall(mj_pattern, message['content'])
        image_urls.extend(mj_urls)
    
    return list(set(image_urls))  # 중복 제거


def find_initial_job_message(
    prompt: str,
    request_timestamp: float,
    timeout: int = 10
) -> Optional[str]:
    """
    요청 후 즉시 생성되는 Midjourney의 "진행 중" 메시지를 찾습니다.
    이 메시지 ID를 추적하면 정확한 이미지를 찾을 수 있습니다.
    
    Args:
        prompt: 요청한 프롬프트
        request_timestamp: 요청 전송 시간 (Unix timestamp)
        timeout: 최대 대기 시간 (초)
    
    Returns:
        "진행 중" 메시지 ID, 찾지 못하면 None
    """
    start_time = time.time()
    prompt_lower = prompt.lower()
    prompt_keywords = set(prompt_lower.split())
    
    while time.time() - start_time < timeout:
        messages = get_channel_messages(limit=5)
        
        if not messages:
            time.sleep(0.5)
            continue
        
        for message in messages:
            # 요청 시간 이전의 메시지는 무시
            # Discord timestamp는 ISO 8601 문자열 또는 Unix timestamp일 수 있음
            msg_ts = message.get('timestamp', '')
            if isinstance(msg_ts, str):
                # ISO 8601 형식인 경우 파싱
                try:
                    dt = datetime.fromisoformat(msg_ts.replace('Z', '+00:00'))
                    message_timestamp = dt.timestamp()
                except:
                    message_timestamp = 0
            else:
                message_timestamp = float(msg_ts)
            
            if message_timestamp < request_timestamp:
                continue
            
            author_id = message.get('author', {}).get('id')
            if author_id == Globals.MID_JOURNEY_ID:
                content = message.get('content', '').lower()
                
                # "진행 중" 메시지 특징:
                # 1. 프롬프트를 포함하고 있음
                # 2. 이미지가 아직 없음 (attachments가 없거나 진행 중 표시)
                # 3. "imagine" 또는 프롬프트의 주요 키워드 포함
                
                has_prompt_match = any(
                    keyword in content
                    for keyword in prompt_keywords
                    if len(keyword) > 4
                )
                
                # 진행 중 메시지 확인 (이미지가 없거나 "waiting" 등의 키워드)
                is_processing = (
                    'waiting' in content or
                    'imagine' in content or
                    len(extract_image_urls_from_message(message)) == 0
                )
                
                if has_prompt_match and is_processing:
                    print(f"  ✓ 진행 중 메시지 발견: {message['id']}")
                    print(f"    내용: {content[:80]}...")
                    return message['id']
        
        time.sleep(0.5)
    
    print(f"  ⚠ 진행 중 메시지를 찾지 못했습니다 (타임아웃: {timeout}초)")
    return None


def match_prompt_to_message(
    prompt: str,
    message_content: str,
    threshold: float = 0.2
) -> tuple[bool, float]:
    """
    프롬프트와 메시지 내용을 비교하여 일치하는지 확인합니다.
    앞뒤 글자 매칭도 포함합니다.
    
    Args:
        prompt: 원본 프롬프트
        message_content: Discord 메시지 내용
        threshold: 일치도 임계값
    
    Returns:
        (일치 여부, 일치도)
    """
    prompt_lower = prompt.lower().strip()
    content_lower = message_content.lower().strip()
    
    # 1. 키워드 기반 매칭
    prompt_keywords = set(prompt_lower.split())
    message_keywords = set(content_lower.split())
    common_keywords = prompt_keywords & message_keywords
    keyword_match_ratio = len(common_keywords) / max(len(prompt_keywords), 1)
    
    # 2. 주요 단어 매칭 (4글자 이상)
    important_words = [
        word for word in prompt_keywords
        if len(word) > 4
    ]
    matched_important = sum(
        1 for word in important_words
        if word in content_lower
    )
    important_match_ratio = (
        matched_important / max(len(important_words), 1)
        if important_words else 0
    )
    
    # 3. 앞뒤 글자 매칭 (프롬프트의 시작과 끝 부분)
    # 프롬프트의 앞 20자와 뒤 20자 추출
    prompt_start = prompt_lower[:20].strip()
    prompt_end = prompt_lower[-20:].strip() if len(prompt_lower) > 20 else prompt_lower
    
    start_match = prompt_start in content_lower if len(prompt_start) > 5 else False
    end_match = prompt_end in content_lower if len(prompt_end) > 5 else False
    
    # 4. 부분 문자열 매칭 (프롬프트의 연속된 부분이 메시지에 포함되는지)
    # 프롬프트를 단어 단위로 나누고, 연속된 3-5개 단어가 메시지에 포함되는지 확인
    prompt_words = prompt_lower.split()
    max_sequence_match = 0
    if len(prompt_words) >= 3:
        for i in range(len(prompt_words) - 2):
            for seq_len in [3, 4, 5]:
                if i + seq_len <= len(prompt_words):
                    sequence = ' '.join(prompt_words[i:i+seq_len])
                    if sequence in content_lower:
                        max_sequence_match = max(max_sequence_match, seq_len)
    
    sequence_match_ratio = max_sequence_match / max(len(prompt_words), 1)
    
    # 5. 종합 일치도 계산
    # 가중 평균: 키워드 40%, 주요 단어 30%, 앞뒤 매칭 20%, 연속 매칭 10%
    overall_match = (
        keyword_match_ratio * 0.4 +
        important_match_ratio * 0.3 +
        (1.0 if (start_match or end_match) else 0.0) * 0.2 +
        sequence_match_ratio * 0.1
    )
    
    # 일치 여부 판단
    is_match = (
        overall_match >= threshold or
        (important_match_ratio >= 0.3 and len(important_words) > 0) or
        (start_match and end_match) or
        max_sequence_match >= 4
    )
    
    return is_match, overall_match


def wait_for_image_completion(
    prompt: str,
    request_timestamp: float,
    job_message_id: Optional[str] = None,
    before_message_id: Optional[str] = None,
    timeout: int = 300,
    check_interval: int = 5
) -> Optional[List[str]]:
    """
    Midjourney 이미지 생성이 완료될 때까지 대기하고 이미지 URL을 반환합니다.
    
    Args:
        prompt: 요청한 프롬프트 (이미지 구분용)
        request_timestamp: 요청 전송 시간 (Unix timestamp)
        job_message_id: 요청 후 생성된 "진행 중" 메시지 ID (가장 정확함)
        before_message_id: 요청 전의 마지막 메시지 ID (fallback)
        timeout: 최대 대기 시간 (초)
        check_interval: 메시지 확인 간격 (초)
    
    Returns:
        완성된 이미지 URL 리스트, 타임아웃 시 None
    """
    start_time = time.time()
    last_checked_message_id = before_message_id
    
    # 프롬프트에서 주요 키워드 추출 (비교용)
    prompt_keywords = set(prompt.lower().split())
    
    print(f"  요청 시간: {time.strftime('%H:%M:%S', time.localtime(request_timestamp))}")
    if job_message_id:
        print(f"  진행 중 메시지 ID: {job_message_id}")
    if before_message_id:
        print(f"  요청 전 마지막 메시지 ID: {before_message_id}")
    print(f"  프롬프트 키워드: {', '.join(list(prompt_keywords)[:5])}...")
    
    while time.time() - start_time < timeout:
        messages = get_channel_messages(limit=10)
        
        if not messages:
            time.sleep(check_interval)
            continue
        
        # 가장 최근 메시지부터 확인
        for message in messages:
            message_id = message['id']
            # Discord timestamp는 ISO 8601 문자열 또는 Unix timestamp일 수 있음
            msg_ts = message.get('timestamp', '')
            if isinstance(msg_ts, str):
                # ISO 8601 형식인 경우 파싱
                try:
                    dt = datetime.fromisoformat(msg_ts.replace('Z', '+00:00'))
                    message_timestamp = dt.timestamp()
                except:
                    message_timestamp = 0
            else:
                message_timestamp = float(msg_ts)
            
            # 요청 시간 이전의 메시지는 건너뛰기
            if message_timestamp < request_timestamp:
                continue
            
            # 요청 전 메시지는 건너뛰기
            if before_message_id and message_id == before_message_id:
                break
            
            # 이미 확인한 메시지는 건너뛰기
            if last_checked_message_id and message_id == last_checked_message_id:
                break
            
            # Midjourney 봇이 보낸 메시지인지 확인
            author_id = message.get('author', {}).get('id')
            if author_id == Globals.MID_JOURNEY_ID:
                # 이미지가 포함된 메시지인지 확인
                image_urls = extract_image_urls_from_message(message)
                
                if image_urls:
                    # 프롬프트가 일치하는지 확인 (개선된 매칭 함수 사용)
                    content = message.get('content', '')
                    is_match, match_ratio = match_prompt_to_message(prompt, content)
                    
                    # 일치 조건:
                    # 1. 프롬프트 매칭이 성공하거나
                    # 2. job_message_id가 있고 메시지가 그 이후에 생성됨
                    # 3. 요청 시간 이후의 메시지
                    final_match = (
                        is_match or
                        (job_message_id and message_timestamp > request_timestamp)
                    ) and message_timestamp > request_timestamp
                    
                    if final_match:
                        print(f"\n✓ 이미지 발견! 메시지 ID: {message_id}")
                        print(f"  발견된 이미지 URL 개수: {len(image_urls)}")
                        print(f"  프롬프트 일치도: {match_ratio:.1%}")
                        print(f"  메시지 시간: {time.strftime('%H:%M:%S', time.localtime(message_timestamp))}")
                        print(f"  메시지 내용: {content[:100]}...")
                        return image_urls
                    else:
                        print(f"  ⚠ 메시지 {message_id}는 프롬프트와 일치하지 않음 (일치도: {match_ratio:.1%})")
        
        # 마지막 확인한 메시지 ID 저장
        if messages:
            last_checked_message_id = messages[0]['id']
        
        elapsed = int(time.time() - start_time)
        if elapsed % 10 == 0:  # 10초마다 진행 상황 출력
            print(f"  대기 중... ({elapsed}초 경과)")
        
        time.sleep(check_interval)
    
    print(f"\n타임아웃: {timeout}초 내에 이미지를 찾지 못했습니다.")
    return None


@dataclass
class ImageGenerationResult:
    """이미지 생성 결과를 담는 데이터 클래스"""
    prompt: str
    success: bool
    image_urls: List[str]
    downloaded_paths: List[str]  # 하위 호환성을 위해 유지
    supabase_image_ids: List[str]  # Supabase에 저장된 이미지 ID 리스트
    supabase_urls: List[str]  # Supabase 공개 URL 리스트
    error: Optional[str] = None
    request_timestamp: Optional[float] = None
    job_message_id: Optional[str] = None


def save_image_to_supabase(
    image_url: str,
    prompt: str,
    storage_manager: Optional[Any] = None,
    cropped_paths: Optional[List[str]] = None,
    metadata: Optional[Dict] = None,
    verbose: bool = True,
    auto_crop: bool = True
) -> Optional[Dict[str, Any]]:
    """
    이미지 URL에서 이미지를 다운로드하여 Supabase에 저장합니다.
    
    Args:
        image_url: 이미지 URL
        prompt: 생성 프롬프트
        storage_manager: MidjourneyImageStorage 인스턴스 (None이면 자동 생성)
        cropped_paths: 크롭된 이미지 경로 리스트 (선택사항)
        metadata: 추가 메타데이터
        verbose: 상세 로그 출력 여부
    
    Returns:
        저장 결과 딕셔너리 (성공 시), 실패 시 None
    """
    try:
        if storage_manager is None:
            from .storage import MidjourneyImageStorage
            storage_manager = MidjourneyImageStorage()
        
        result = storage_manager.save_midjourney_image_from_url(
            image_url=image_url,
            prompt=prompt,
            cropped_paths=cropped_paths,
            metadata=metadata,
            auto_crop=auto_crop
        )
        
        if result.get('success'):
            if verbose:
                print(f"✓ Supabase 저장 완료: {result.get('image_id')}")
                print(f"  공개 URL: {result.get('original_url')}")
            return result
        else:
            if verbose:
                print(f"✗ Supabase 저장 실패: {result.get('error')}")
            return None
            
    except Exception as e:
        if verbose:
            print(f"✗ Supabase 저장 중 오류: {e}")
        return None


def download_image(image_url: str, save_path: str) -> bool:
    """
    이미지 URL에서 이미지를 로컬 파일 시스템에 다운로드합니다.
    (하위 호환성을 위해 유지, 권장: save_image_to_supabase 사용)
    
    Args:
        image_url: 이미지 URL
        save_path: 저장할 파일 경로
    
    Returns:
        성공 여부
    """
    try:
        header = {
            'authorization': Globals.SALAI_TOKEN
        }
        response = requests.get(
            image_url, headers=header, stream=True, timeout=30
        )
        
        if response.status_code == 200:
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            with open(save_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            file_size = os.path.getsize(save_path)
            abs_path = os.path.abspath(save_path)
            print(f"✓ 다운로드 완료: {abs_path} ({file_size:,} bytes)")
            return True
        else:
            print(f"✗ 다운로드 실패: HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ 다운로드 중 오류: {e}")
        return False


def generate_images_batch(
    prompts: List[str],
    image_paths_per_prompt: Optional[
        List[Optional[List[Union[str, Path]]]]
    ] = None,
    download_dir: Optional[str] = None,
    request_delay: float = 2.0,
    timeout_per_image: int = 300,
    check_interval: int = 5,
    verbose: bool = True,
    auto_crop: bool = True,
    auto_upload: bool = True,  # 기본값을 True로 변경 (Supabase 저장)
    save_locally: bool = False  # 로컬 저장은 선택사항
) -> List[ImageGenerationResult]:
    """
    여러 프롬프트를 배치로 요청하고 각각의 이미지를 정확히 추적하여 다운로드합니다.
    이미지 첨부를 지원합니다.
    
    Args:
        prompts: 이미지 생성 프롬프트 리스트
        image_paths_per_prompt: 각 프롬프트에 대한 참조 이미지 경로 리스트
            (None이면 이미지 없음, 길이는 prompts와 같아야 함)
        download_dir: 이미지 다운로드 디렉토리 (None이면 data/images 사용)
        request_delay: 각 요청 사이의 대기 시간 (초)
        timeout_per_image: 각 이미지당 최대 대기 시간 (초)
        check_interval: 메시지 확인 간격 (초)
        verbose: 상세 로그 출력 여부
        auto_crop: 자동 크롭 여부
        auto_upload: 자동 Supabase 업로드 여부 (기본값: True)
        save_locally: 로컬 파일 시스템에도 저장할지 여부 (기본값: False)
    
    Returns:
        ImageGenerationResult 리스트 (각 프롬프트별 결과)
    
    Example:
        # 이미지 없이 배치 생성
        results = generate_images_batch(["prompt1", "prompt2"])
        
        # 일부만 이미지 첨부
        results = generate_images_batch(
            prompts=["prompt1", "prompt2", "prompt3"],
            image_paths_per_prompt=[
                ["img1.png"],  # prompt1에 이미지 첨부
                None,          # prompt2는 이미지 없음
                ["img2.png", "img3.jpg"]  # prompt3에 여러 이미지 첨부
            ]
        )
    """
    if not prompts:
        return []
    
    # 이미지 경로 리스트 검증 및 정규화
    if image_paths_per_prompt is None:
        image_paths_per_prompt = [None] * len(prompts)
    elif len(image_paths_per_prompt) != len(prompts):
        raise ValueError(
            f"image_paths_per_prompt 길이({len(image_paths_per_prompt)})가 "
            f"prompts 길이({len(prompts)})와 일치하지 않습니다"
        )
    
    # 이미지 경로를 Path 객체로 변환
    normalized_image_paths = []
    for img_paths in image_paths_per_prompt:
        if img_paths is None:
            normalized_image_paths.append(None)
        else:
            normalized_image_paths.append([Path(p) for p in img_paths])
    
    # 다운로드 디렉토리 설정
    if download_dir is None:
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        download_dir = os.path.join(base_dir, "data", "images")
    os.makedirs(download_dir, exist_ok=True)
    
    # 요청 전의 마지막 메시지 ID 가져오기
    if verbose:
        print("=" * 60)
        print(f"배치 이미지 생성 시작: {len(prompts)}개 프롬프트")
        image_count = sum(
            1 for paths in normalized_image_paths if paths is not None
        )
        if image_count > 0:
            print(f"  ({image_count}개 프롬프트에 이미지 첨부)")
        print("=" * 60)
    
    before_messages = get_channel_messages(limit=1)
    initial_before_message_id = (
        before_messages[0]['id'] if before_messages else None
    )
    
    # 각 요청에 대한 정보 저장
    request_info: List[Dict] = []
    
    # 1단계: 모든 프롬프트 요청 전송
    if verbose:
        print("\n[1단계] 이미지 생성 요청 전송 중...")
    
    for idx, prompt in enumerate(prompts, 1):
        image_paths = normalized_image_paths[idx - 1]
        
        if verbose:
            print(f"\n[{idx}/{len(prompts)}] 프롬프트 요청 중...")
            print(f"  프롬프트: {prompt[:80]}...")
            if image_paths:
                print(f"  참조 이미지: {len(image_paths)}개")
        
        request_timestamp = time.time()
        response = PassPromptToSelfBot(prompt, image_paths=image_paths)
        
        if response.status_code == 204:
            # 진행 중 메시지 찾기
            job_message_id = find_initial_job_message(
                prompt=prompt,
                request_timestamp=request_timestamp,
                timeout=10
            )
            
            request_info.append({
                'prompt': prompt,
                'index': idx - 1,
                'request_timestamp': request_timestamp,
                'job_message_id': job_message_id,
                'before_message_id': initial_before_message_id,
                'completed': False
            })
            
            if verbose:
                print(f"  ✓ 요청 성공 (시간: {time.strftime('%H:%M:%S', time.localtime(request_timestamp))})")
        else:
            request_info.append({
                'prompt': prompt,
                'index': idx - 1,
                'request_timestamp': request_timestamp,
                'job_message_id': None,
                'before_message_id': initial_before_message_id,
                'completed': False,
                'error': f"HTTP {response.status_code}"
            })
            if verbose:
                print(f"  ✗ 요청 실패: HTTP {response.status_code}")
        
        # 다음 요청 전 대기 (마지막 요청 제외)
        if idx < len(prompts):
            time.sleep(request_delay)
    
    # 2단계: 완성된 이미지 추적 및 다운로드
    if verbose:
        print(f"\n[2단계] 이미지 완성 대기 중... (최대 {timeout_per_image}초/이미지)")
        print("  (순서대로 완성되지 않을 수 있으므로 모든 요청을 모니터링합니다)\n")
    
    results: List[ImageGenerationResult] = []
    completed_count = 0
    start_time = time.time()
    last_checked_message_id = initial_before_message_id
    
    # 자동 크롭 및 업로드를 위한 모듈 임포트
    prompt_manager = None
    storage_manager = None
    crop_image_cross = None
    
    if auto_crop or auto_upload or save_locally:
        from .manager import PromptManager
        prompt_manager = PromptManager()
        
        if auto_upload:
            try:
                from .storage import MidjourneyImageStorage
                storage_manager = MidjourneyImageStorage()
            except Exception as e:
                if verbose:
                    print(f"  ⚠ Supabase 초기화 실패: {e}")
                storage_manager = None
        
        if auto_crop and save_locally:
            try:
                from .processor import crop_image_cross
            except ImportError:
                crop_image_cross = None
    
    # 모든 요청이 완료될 때까지 반복
    while completed_count < len(request_info):
        # 타임아웃 확인
        elapsed = time.time() - start_time
        max_timeout = timeout_per_image * len(request_info)
        if elapsed > max_timeout:
            if verbose:
                print(f"\n⚠ 타임아웃: {max_timeout}초 경과")
            break
        
        # Discord 채널 메시지 확인
        messages = get_channel_messages(limit=20)
        
        if not messages:
            time.sleep(check_interval)
            continue
        
        # 각 메시지 확인
        for message in messages:
            message_id = message['id']
            
            # 이미 확인한 메시지는 건너뛰기
            if last_checked_message_id and message_id == last_checked_message_id:
                break
            
            # Midjourney 봇 메시지인지 확인
            author_id = message.get('author', {}).get('id')
            if author_id != Globals.MID_JOURNEY_ID:
                continue
            
            # 이미지가 포함된 메시지인지 확인
            image_urls = extract_image_urls_from_message(message)
            if not image_urls:
                continue
            
            # 메시지 타임스탬프 파싱
            msg_ts = message.get('timestamp', '')
            if isinstance(msg_ts, str):
                try:
                    dt = datetime.fromisoformat(msg_ts.replace('Z', '+00:00'))
                    message_timestamp = dt.timestamp()
                except:
                    continue
            else:
                message_timestamp = float(msg_ts)
            
            # 각 요청과 매칭 시도
            content = message.get('content', '')
            for req_info in request_info:
                if req_info['completed']:
                    continue
                
                # 요청 시간 이후의 메시지인지 확인
                if message_timestamp < req_info['request_timestamp']:
                    continue
                
                # 프롬프트 매칭 확인
                is_match, match_ratio = match_prompt_to_message(
                    req_info['prompt'],
                    content
                )
                
                # 일치하는 경우
                if is_match or (
                    req_info['job_message_id'] and
                    message_timestamp > req_info['request_timestamp']
                ):
                    if verbose:
                        print(f"\n✓ [{req_info['index']+1}/{len(prompts)}] 이미지 발견!")
                        print(f"  프롬프트: {req_info['prompt'][:60]}...")
                        print(f"  일치도: {match_ratio:.1%}")
                        print(f"  이미지 URL 개수: {len(image_urls)}")
                    
                    # 이미지 Supabase 저장 (기본)
                    downloaded_paths = []
                    supabase_image_ids = []
                    supabase_urls = []
                    cropped_paths_for_storage = []
                    
                    for img_idx, img_url in enumerate(image_urls, 1):
                        # 로컬 저장 (선택사항)
                        local_path = None
                        if save_locally:
                            prompt_hash = hashlib.md5(
                                req_info['prompt'].encode()
                            ).hexdigest()[:8]
                            
                            ext = '.png'
                            if '.jpg' in img_url.lower() or '.jpeg' in img_url.lower():
                                ext = '.jpg'
                            elif '.gif' in img_url.lower():
                                ext = '.gif'
                            elif '.webp' in img_url.lower():
                                ext = '.webp'
                            
                            filename = f"midjourney_{req_info['index']}_{prompt_hash}_{img_idx}{ext}"
                            download_path = os.path.join(download_dir, filename)
                            
                            if download_image(img_url, download_path):
                                downloaded_paths.append(download_path)
                                local_path = download_path
                                
                                # 자동 크롭 (로컬 저장 시에만)
                                if auto_crop and crop_image_cross:
                                    try:
                                        cropped_dir = os.path.join(download_dir, "cropped")
                                        os.makedirs(cropped_dir, exist_ok=True)
                                        cropped_paths_for_storage = crop_image_cross(
                                            download_path, cropped_dir
                                        )
                                    except Exception as e:
                                        if verbose:
                                            print(f"  ⚠ 크롭 실패 {filename}: {e}")
                        
                        # Supabase 저장 (기본)
                        if auto_upload:
                            try:
                                upload_result = save_image_to_supabase(
                                    image_url=img_url,
                                    prompt=req_info['prompt'],
                                    storage_manager=storage_manager,
                                    cropped_paths=None,  # Supabase에서 자동 크롭
                                    metadata={
                                        "source": "midjourney_batch",
                                        "request_timestamp": req_info['request_timestamp'],
                                        "image_index": img_idx
                                    },
                                    verbose=verbose,
                                    auto_crop=True  # Supabase 저장 시 항상 크롭
                                )
                                
                                if upload_result and upload_result.get('success'):
                                    # 원본 이미지 ID 추가
                                    original_id = upload_result.get('image_id')
                                    supabase_image_ids.append(original_id)
                                    supabase_urls.append(upload_result.get('original_url'))
                                    
                                    # 크롭된 이미지 ID들도 추가
                                    cropped_ids = upload_result.get('cropped_image_ids', [])
                                    supabase_image_ids.extend(cropped_ids)
                                    
                                    # 크롭된 이미지 URL들도 추가
                                    cropped_urls_list = upload_result.get('cropped_urls', [])
                                    for crop_info in cropped_urls_list:
                                        if isinstance(crop_info, dict) and crop_info.get('url'):
                                            supabase_urls.append(crop_info['url'])
                                    
                                    # 프롬프트 매니저에 등록 (Supabase URL 사용)
                                    if prompt_manager:
                                        try:
                                            prompt_manager.register_image(
                                                prompt=req_info['prompt'],
                                                original_path=local_path or upload_result.get('original_url'),
                                                cropped_paths=cropped_paths_for_storage or [],
                                                image_urls=[img_url],
                                                metadata={
                                                    "source": "midjourney_batch",
                                                    "request_timestamp": req_info['request_timestamp'],
                                                    "supabase_image_id": upload_result.get('image_id'),
                                                    "supabase_url": upload_result.get('original_url')
                                                }
                                            )
                                        except Exception as e:
                                            if verbose:
                                                print(f"  ⚠ 프롬프트 매니저 등록 실패: {e}")
                            except Exception as e:
                                if verbose:
                                    print(f"  ⚠ Supabase 저장 실패: {e}")
                    
                    # 결과 저장
                    result = ImageGenerationResult(
                        prompt=req_info['prompt'],
                        success=True,
                        image_urls=image_urls,
                        downloaded_paths=downloaded_paths,
                        supabase_image_ids=supabase_image_ids,
                        supabase_urls=supabase_urls,
                        request_timestamp=req_info['request_timestamp'],
                        job_message_id=req_info['job_message_id']
                    )
                    results.append(result)
                    req_info['completed'] = True
                    completed_count += 1
                    
                    if verbose:
                        print(f"  ✓ 다운로드 완료: {len(downloaded_paths)}개 파일")
                    break
        
        # 마지막 확인한 메시지 ID 저장
        if messages:
            last_checked_message_id = messages[0]['id']
        
        # 진행 상황 출력
        if verbose and int(time.time() - start_time) % 10 == 0:
            elapsed = int(time.time() - start_time)
            print(f"  진행 중... ({completed_count}/{len(request_info)} 완료, {elapsed}초 경과)")
        
        time.sleep(check_interval)
    
    # 완료되지 않은 요청 처리
    for req_info in request_info:
        if not req_info['completed']:
            result = ImageGenerationResult(
                prompt=req_info['prompt'],
                success=False,
                image_urls=[],
                downloaded_paths=[],
                supabase_image_ids=[],
                supabase_urls=[],
                error=req_info.get('error', '타임아웃'),
                request_timestamp=req_info['request_timestamp'],
                job_message_id=req_info['job_message_id']
            )
            results.append(result)
    
    # 인덱스 순서대로 정렬
    results.sort(key=lambda x: next(
        (i for i, req in enumerate(request_info) if req['prompt'] == x.prompt),
        len(request_info)
    ))
    
    if verbose:
        print(f"\n{'='*60}")
        print(f"배치 완료: {completed_count}/{len(prompts)} 성공")
        print(f"{'='*60}\n")
    
    return results

