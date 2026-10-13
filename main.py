from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import PlainTextResponse
import pysrt
from deep_translator import MyMemoryTranslator
import io

app = FastAPI(title="Subtitle Translation API")

# Normalise common short language codes to MyMemory format
LANG_MAP = {
    "en": "en-GB",
    "ja": "ja-JP",
    "kn": "kn-IN",
    "hi": "hi-IN",
    "es": "es-ES",
    "fr": "fr-FR",
    "de": "de-DE",
    "ko": "ko-KR",
    "te": "te-IN",
    "ta": "ta-IN"
}

@app.get("/")
def home():
    return {"status": "online", "service": "Subtitle Translation API"}

@app.post("/translate-srt")
async def translate_srt(
    file: UploadFile = File(...),
    target_lang: str = Form("ja"),
    source_lang: str = Form("en")
):
    if not file.filename.endswith(".srt"):
        raise HTTPException(status_code=400, detail="Only .srt subtitle files are supported.")

    src = LANG_MAP.get(source_lang.lower(), source_lang)
    tgt = LANG_MAP.get(target_lang.lower(), target_lang)

    try:
        content = await file.read()
        srt_text = content.decode("utf-8", errors="ignore")
        subs = pysrt.from_string(srt_text)

        translator = MyMemoryTranslator(source=src, target=tgt)

        for sub in subs:
            if sub.text.strip():
                sub.text = translator.translate(sub.text)

        output = io.StringIO()
        subs.write_into(output)
        translated_srt_data = output.getvalue()

        return PlainTextResponse(
            content=translated_srt_data,
            media_type="text/plain",
            headers={
                "Content-Disposition": f"attachment; filename=translated_{file.filename}"
            }
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Translation failed: {str(e)}")