# Midjourney 모듈 사용 가이드

프로젝트의 다른 파일에서 쉽게 사용할 수 있는 편리한 API 함수들입니다.

## 빠른 시작

```python
from src.midjourney import (
    generate_and_save_image,
    save_image_from_url,
    delete_image,
    get_image,
    list_images
)

# 이미지 생성 및 저장 (한 번에!)
result = generate_and_save_image("a beautiful sunset")
print(result['image_id'])
```

## 주요 함수

### 1. 이미지 생성 및 저장

#### `generate_and_save_image()`
이미지를 생성하고 Supabase에 자동으로 저장합니다.

```python
from src.midjourney import generate_and_save_image

result = generate_and_save_image(
    prompt="a beautiful sunset over the ocean, cinematic --ar 16:9",
    wait_for_completion=True,  # 완성까지 대기
    timeout=300,  # 최대 5분 대기
    auto_crop=True,  # 자동으로 4장 크롭
    verbose=True
)

if result and result.get('success'):
    print(f"원본 ID: {result['image_id']}")
    print(f"크롭 ID: {result['cropped_image_ids']}")
    print(f"공개 URL: {result['original_url']}")
```

**참조 이미지와 함께 생성:**
```python
result = generate_and_save_image(
    prompt="create a similar style image",
    image_paths=["reference.png"],  # 참조 이미지 경로
    auto_crop=True
)
```

#### `generate_images_batch_and_save()`
여러 프롬프트를 배치로 생성하고 저장합니다.

```python
from src.midjourney import generate_images_batch_and_save

results = generate_images_batch_and_save(
    prompts=[
        "a beautiful sunset",
        "a futuristic city",
        "a peaceful forest"
    ],
    auto_crop=True,
    save_locally=False  # Supabase에만 저장
)

for result in results:
    if result.success:
        print(f"✓ {result.prompt}: {result.supabase_image_ids}")
```

### 2. 이미지 저장

#### `save_image_from_url()`
이미지 URL에서 직접 다운로드하여 저장합니다.

```python
from src.midjourney import save_image_from_url

result = save_image_from_url(
    image_url="https://cdn.discordapp.com/attachments/...",
    prompt="saved from url",
    auto_crop=True  # 자동 크롭
)

if result:
    print(f"저장 완료: {result['image_id']}")
```

#### `upload_reference_image()`
참조 이미지를 Discord에 업로드합니다.

```python
from src.midjourney import upload_reference_image

url = upload_reference_image("reference.png")
if url:
    print(f"업로드 완료: {url}")
```

### 3. 이미지 조회

#### `list_images()`
이미지 목록을 가져옵니다.

```python
from src.midjourney import list_images

# 최근 원본 이미지 50개
images = list_images(limit=50, original_only=True)

# 특정 프롬프트의 이미지
images = list_images(prompt="a beautiful sunset")

for image in images:
    print(f"{image['image_id']}: {image['prompt'][:50]}...")
```

#### `get_image()`
특정 이미지 정보를 가져옵니다.

```python
from src.midjourney import get_image

image = get_image("image_id_123")
if image:
    print(f"URL: {image['public_url']}")
    print(f"크기: {image['width']}x{image['height']}")
```

#### `get_image_group()`
원본 이미지와 모든 크롭 이미지를 함께 가져옵니다.

```python
from src.midjourney import get_image_group

group = get_image_group("original_image_id")
if group:
    print(f"원본: {group['original']['public_url']}")
    print(f"크롭 이미지 {len(group['cropped'])}개:")
    for crop in group['cropped']:
        print(f"  - {crop['crop_position']}: {crop['public_url']}")
```

### 4. 이미지 삭제

#### `delete_image()`
이미지를 삭제합니다.

```python
from src.midjourney import delete_image

# 개별 이미지만 삭제 (크롭 이미지 중 하나)
delete_image("crop_image_id", delete_all=False)

# 전체 삭제 (원본 + 모든 크롭 이미지)
delete_image("original_image_id", delete_all=True)
```

#### `delete_images_by_prompt()`
특정 프롬프트의 모든 이미지를 삭제합니다.

```python
from src.midjourney import delete_images_by_prompt

count = delete_images_by_prompt(
    prompt="a beautiful sunset",
    delete_all=True  # 원본 + 모든 크롭 삭제
)
print(f"{count}개 이미지 그룹 삭제 완료")
```

## 완전한 예제

```python
from src.midjourney import (
    generate_and_save_image,
    get_image_group,
    delete_image
)

# 1. 이미지 생성 및 저장
result = generate_and_save_image(
    prompt="a beautiful sunset, cinematic --ar 16:9",
    auto_crop=True
)

if result and result.get('success'):
    original_id = result['image_id']
    
    # 2. 이미지 그룹 조회
    group = get_image_group(original_id)
    if group:
        print(f"원본: {group['original']['public_url']}")
        for crop in group['cropped']:
            print(f"크롭 {crop['crop_number']}: {crop['public_url']}")
    
    # 3. 개별 크롭 이미지 삭제
    if group and group['cropped']:
        crop_id = group['cropped'][0]['image_id']
        delete_image(crop_id, delete_all=False)
        print("크롭 이미지 1개 삭제 완료")
    
    # 4. 전체 삭제
    # delete_image(original_id, delete_all=True)
```

## 저장 구조

모든 이미지는 Supabase에 다음과 같이 저장됩니다:

```
원본 이미지:
- Storage: originals/{image_id}/image.png
- DB: image_type='original'

크롭 이미지 (4장):
- Storage: cropped/{image_id}/1.png, 2.png, 3.png, 4.png
- DB: image_type='cropped', parent_image_id={원본ID}, crop_number=1,2,3,4
```

## 주의사항

1. **경로 문제**: 프로젝트 루트에서 실행하거나 `sys.path`에 프로젝트 루트를 추가하세요.
2. **Supabase 설정**: Supabase 연결 정보가 올바르게 설정되어 있어야 합니다.
3. **Discord 토큰**: `src/midjourney/config.py`에 Discord 토큰이 설정되어 있어야 합니다.

## 고급 사용법

더 세밀한 제어가 필요한 경우:

```python
from src.midjourney import MidjourneyImageStorage
from src.midjourney.client import generate_images_batch

# 직접 Storage 클래스 사용
storage = MidjourneyImageStorage()
result = storage.save_midjourney_image_from_url(...)

# 배치 생성 세부 제어
results = generate_images_batch(
    prompts=["..."],
    auto_upload=True,
    save_locally=False,
    request_delay=2.0
)
```

## 문제 해결

### Import 오류
```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from src.midjourney import ...
```

### Supabase 연결 오류
- Supabase 설정 파일 확인
- 환경 변수 확인
- 네트워크 연결 확인

## 더 많은 예제

`examples/midjourney_api_example.py` 파일을 참고하세요.

