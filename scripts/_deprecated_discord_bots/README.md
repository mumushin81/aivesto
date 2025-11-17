# Deprecated Discord Bot Files

## Why These Files Were Moved Here

These files contained custom Discord bot implementations that caused issues:

### Problems Identified

1. **discord_midjourney_bot.py**
   - Used incorrect bot mention approach: `<@bot_id> /imagine`
   - Midjourney doesn't respond to this format
   - 60-second rate limiting was too aggressive
   - No response validation

2. **midjourney_interactions_bot.py**
   - Attempted to use Discord Interactions API incorrectly
   - Comment in code admits "likely won't work"
   - Discord bots cannot programmatically trigger other bots' slash commands
   - No error handling

3. **simple_midjourney_test.py**
   - Test file using the same broken approach
   - Created duplicate message spam in Discord

### Result

These implementations caused the same prompt to be sent multiple times to Discord, creating spam and failing to generate images.

### Correct Approach

Use the verified `magic_book` module instead:

```python
import sys
from pathlib import Path

# Add magic_book to path
magic_book_path = Path("/Users/jinxin/dev/magic_book")
sys.path.insert(0, str(magic_book_path))

# Use the proven implementation
from src.midjourney import generate_images_batch_and_save

results = generate_images_batch_and_save(
    prompts=["your prompt"],
    request_delay=2.0,
    auto_crop=True,
    save_locally=False,
    verbose=True
)
```

See `scripts/generate_with_magic_book.py` for a working example.

## Date Deprecated

2025-11-17

## Can These Be Restored?

No. These files use fundamentally incorrect approaches for interacting with Midjourney. The magic_book module should be used instead.
