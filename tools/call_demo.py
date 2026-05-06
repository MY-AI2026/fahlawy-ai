#!/usr/bin/env python3
"""
Mariam demo call — runs entirely from your laptop. No server, no tunnel.

Two modes:
  - default:    Twilio Polly.Hala-Neural (Egyptian neural voice). No external
                file upload. Works as long as Twilio credentials are valid.
  - elevenlabs: Generate ElevenLabs MP3, upload to catbox.moe, then call.
                Higher voice quality. Requires ELEVENLABS_API_KEY.

Setup once:
    pip install twilio httpx

Run:
    export TWILIO_ACCOUNT_SID=ACxxxx
    export TWILIO_API_KEY=SKxxxx
    export TWILIO_API_SECRET=xxxx
    export TWILIO_FROM=+14642669684           # your Twilio number
    # optional, for higher-quality voice:
    export ELEVENLABS_API_KEY=sk_xxxx
    export ELEVENLABS_VOICE_ID=EXAVITQu4vr4xnSDxMaL

    python tools/call_demo.py +96555552180
    # or, force ElevenLabs:
    python tools/call_demo.py +96555552180 --voice elevenlabs
"""
from __future__ import annotations

import argparse
import os
import sys
from xml.sax.saxutils import escape

import httpx


PITCH = (
    "السلام عليكم، صباح الخير. معاك مريم من شركة أوركيد ديفلوبمنتس للتطوير العقاري. "
    "ممكن آخد من حضرتك دقيقتين بس؟ "
    "عندنا عرض حصري النهاردة على شقة سكنية في كمبوند أوركيد بارك بقلب التجمع الخامس. "
    "مية خمسة وستين متر، تلات غرف نوم، متشطبة سوبر لوكس، واستلام فوري. "
    "السعر كاش سبعة مليون، أو تقسيط على تمن سنين بدون فوايد، بمقدم عشرة بالمية بس. "
    "الكمبوند فيه أربع حمامات سباحة، جيم، كلوب هاوس، أمن أربعة وعشرين ساعة، ومدرسة دولية، "
    "وموقعه قريب من الجامعة الأمريكية وسيتي ستارز التجمع. "
    "أنا متاحة أرتبلك معاينة بكرة الساعة ستة مساءً، أو الخميس الساعة أربعة عصراً. "
    "أنهي ميعاد يناسب حضرتك أكتر؟ "
    "متشكرة جداً لوقت حضرتك. هنتواصل معاك على نفس الرقم لتأكيد المعاينة. يومك سعيد."
)


def must(name: str) -> str:
    v = os.environ.get(name)
    if not v:
        sys.exit(f"❌ Missing env var: {name}")
    return v


def build_polly_twiml(text: str) -> str:
    """Inline TwiML using Polly.Hala-Neural (Egyptian Arabic neural voice)."""
    safe = escape(text)
    return (
        '<?xml version="1.0" encoding="UTF-8"?>'
        "<Response>"
        "<Pause length=\"1\"/>"
        f'<Say voice="Polly.Hala-Neural" language="ar-EG">{safe}</Say>'
        "<Pause length=\"1\"/>"
        "</Response>"
    )


def generate_elevenlabs_mp3(text: str) -> bytes:
    api_key = must("ELEVENLABS_API_KEY")
    voice_id = os.environ.get("ELEVENLABS_VOICE_ID", "EXAVITQu4vr4xnSDxMaL")
    print(f"🎤 Generating ElevenLabs audio (voice={voice_id})...")
    r = httpx.post(
        f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
        "?output_format=mp3_44100_128",
        headers={
            "xi-api-key": api_key,
            "Accept": "audio/mpeg",
            "Content-Type": "application/json",
        },
        json={
            "text": text,
            "model_id": "eleven_multilingual_v2",
            "voice_settings": {
                "stability": 0.45,
                "similarity_boost": 0.85,
                "style": 0.55,
                "use_speaker_boost": True,
            },
            "language_code": "ar",
        },
        timeout=90.0,
    )
    if r.status_code != 200:
        sys.exit(f"❌ ElevenLabs error {r.status_code}: {r.text[:300]}")
    print(f"✅ Got {len(r.content)} bytes of MP3")
    return r.content


def upload_to_catbox(mp3: bytes) -> str:
    """Upload MP3 to catbox.moe (no auth, public, persistent)."""
    print("📤 Uploading to catbox.moe ...")
    files = {"fileToUpload": ("mariam.mp3", mp3, "audio/mpeg")}
    data = {"reqtype": "fileupload"}
    r = httpx.post(
        "https://catbox.moe/user/api.php",
        data=data,
        files=files,
        timeout=60.0,
    )
    if r.status_code != 200 or not r.text.startswith("https://"):
        sys.exit(f"❌ catbox upload failed: HTTP {r.status_code} body={r.text[:200]}")
    print(f"✅ Hosted at: {r.text.strip()}")
    return r.text.strip()


def build_play_twiml(audio_url: str) -> str:
    return (
        '<?xml version="1.0" encoding="UTF-8"?>'
        "<Response>"
        "<Pause length=\"1\"/>"
        f"<Play>{escape(audio_url)}</Play>"
        "<Pause length=\"1\"/>"
        "</Response>"
    )


def make_call(to_number: str, twiml: str) -> str:
    sid = must("TWILIO_ACCOUNT_SID")
    api_key = must("TWILIO_API_KEY")
    api_secret = must("TWILIO_API_SECRET")
    from_number = must("TWILIO_FROM")

    print(f"📞 Calling {to_number} from {from_number} ...")
    r = httpx.post(
        f"https://api.twilio.com/2010-04-01/Accounts/{sid}/Calls.json",
        auth=(api_key, api_secret),
        data={"To": to_number, "From": from_number, "Twiml": twiml},
        headers={"X-Twilio-Account-Sid": sid},
        timeout=30.0,
    )
    if r.status_code not in (200, 201):
        sys.exit(f"❌ Twilio error {r.status_code}: {r.text[:500]}")
    body = r.json()
    print(f"✅ Call placed — SID={body.get('sid')} status={body.get('status')}")
    return body.get("sid", "")


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("to_number", help="Recipient in E.164 format, e.g. +96555552180")
    p.add_argument(
        "--voice",
        choices=("polly", "elevenlabs"),
        default="polly",
        help="polly = Twilio Polly.Hala-Neural (default, no upload). "
        "elevenlabs = generate MP3 + upload to catbox.moe.",
    )
    args = p.parse_args()

    if args.voice == "elevenlabs":
        mp3 = generate_elevenlabs_mp3(PITCH)
        audio_url = upload_to_catbox(mp3)
        twiml = build_play_twiml(audio_url)
    else:
        twiml = build_polly_twiml(PITCH)

    if len(twiml) > 4000:
        sys.exit(
            f"❌ Inline TwiML too large ({len(twiml)} > 4000 chars). "
            "Shorten the pitch or switch to elevenlabs mode."
        )

    make_call(args.to_number, twiml)
    print("🎉 Done — pick up the phone!")


if __name__ == "__main__":
    main()
