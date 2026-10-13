from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import PlainTextResponse
import pysrt
from deep_translator import MyMemoryTranslator
import io

app = FastAPI(title="Subtitle Translation API")

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

    try:
        content = await file.read()
        srt_text = content.decode("utf-8", errors="ignore")
        subs = pysrt.from_string(srt_text)

        # MyMemory works reliably on cloud hosts without IP blocks
        translator = MyMemoryTranslator(source=source_lang, target=target_lang)

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