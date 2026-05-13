from fastapi import FastAPI
from pydantic import BaseModel
from google import genai

client = genai.Client(
    api_key="AIzaSyAmJdzHeW5xESmZu6q3el20imsuUcBe06g"
)

app = FastAPI()

class TextInput(BaseModel):
    text: str


@app.post("/summarize")
async def summarize_text(data: TextInput):

    try:

        prompt = f"""
        Summarize the following text in simple language:

        {data.text}
        """

        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt
        )

        return {
            "summary": response.text
        }

    except Exception as e:

        return {
            "error": str(e)
        }