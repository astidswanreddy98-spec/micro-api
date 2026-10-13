from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import PlainTextResponse
import pysrt
from deep_translator import GoogleTranslator
import io

app = FastAPI(title="Subtitle Translation API")

@app.get("/")
def home():
    return {"status": "online", "service": "Subtitle Translation API"}

@app.post("/translate-srt")
async def translate_srt(
    file: UploadFile = File(...),
    target_lang: str = Form("en"),
    source_lang: str = Form("auto")
):
    if not file.filename.endswith(".srt"):
        raise HTTPException(status_code=400, detail="Only .srt subtitle files are supported.")

    try:
        content = await file.read()
        srt_text = content.decode("utf-8", errors="ignore")
        
        subs = pysrt.from_string(srt_text)
        translator = GoogleTranslator(source=source_lang, target=target_lang)

        # Collect non-empty texts to translate in a single batch request
        indices = [i for i, sub in enumerate(subs) if sub.text.strip()]
        texts_to_translate = [subs[i].text for i in indices]

        if texts_to_translate:
            # Batch call avoids rate limits
            translated_texts = translator.translate_batch(texts_to_translate)
            for idx, translated in zip(indices, translated_texts):
                subs[idx].text = translated

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