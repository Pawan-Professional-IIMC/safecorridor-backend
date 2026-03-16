import os
from typing import Any

import httpx


SARVAM_TTS_API_URL = "https://api.sarvam.ai/text-to-speech"


async def synthesize_speech(
    text: str,
    target_language_code: str = "en-IN",
    speaker: str | None = "Shubh",
    pace: float | None = 1.0,
    speech_sample_rate: int | None = 24000,
    model: str | None = None,
    temperature: float | None = 0.6,
) -> dict[str, Any]:
    api_key = os.getenv("SARVAM_API_KEY")
    if not api_key:
        raise RuntimeError("Sarvam key is not configured.")

    cleaned_text = (text or "").strip()
    if not cleaned_text:
        raise ValueError("Text is required for text-to-speech.")

    payload = {
        "text": cleaned_text,
        "target_language_code": target_language_code,
        "speaker": speaker,
        "pace": pace,
        "speech_sample_rate": speech_sample_rate,
        "model": model or os.getenv("SARVAM_TTS_MODEL", "bulbul:v3"),
        "temperature": temperature,
    }
    payload = {key: value for key, value in payload.items() if value is not None}

    headers = {
        "api-subscription-key": api_key,
        "Content-Type": "application/json",
    }

    async with httpx.AsyncClient(timeout=45) as client:
        response = await client.post(SARVAM_TTS_API_URL, headers=headers, json=payload)
        response.raise_for_status()
        data = response.json()

    audios = data.get("audios") or []
    audio_base64 = audios[0] if audios else ""
    if not audio_base64:
        raise RuntimeError("Sarvam returned no audio data.")

    return {
        "request_id": data.get("request_id"),
        "audio_base64": audio_base64,
        "content_type": "audio/wav",
        "provider": "sarvam",
    }
