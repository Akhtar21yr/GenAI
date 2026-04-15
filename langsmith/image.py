from google import genai
from PIL import Image
from io import BytesIO
import os
from dotenv import load_dotenv

load_dotenv()

api_key=os.getenv('GEMINI_API_KEY')

client = genai.Client(api_key=api_key)

response = client.models.generate_content(
    model="gemini-2.5-flash-image",
    contents="Generate an image of man wroking on laptop in room"
)

for part in response.candidates[0].content.parts:
    if part.inline_data:
        image = Image.open(BytesIO(part.inline_data.data))
        image.save("output.png")
        image.show()