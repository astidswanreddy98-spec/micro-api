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

        # Collect dialogues
        dialogues = [sub.text for sub in subs]

        if dialogues:
            # Join all dialogues into ONE single string using a delimiter
            delimiter = " \n<<<>>>\n "
            joined_text = delimiter.join(dialogues)

            # Make exactly ONE HTTP translation request
            translator = GoogleTranslator(source=source_lang, target=target_lang)
            translated_blob = translator.translate(joined_text)

            # Split back into lines
            translated_lines = translated_blob.split("<<<>>>")

            # Assign back to subtitles
            for i, line in enumerate(translated_lines):
                if i < len(subs):
                    subs[i].text = line.strip()

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