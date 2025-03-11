from openai import OpenAI
import os
from dotenv import load_dotenv
import requests
import re
from PIL import Image
load_dotenv()
client = OpenAI(api_key=os.getenv("API_KEY"))
# print("----- standard request -----")
# completion = client.chat.completions.create(
#     model="gpt-4",
#     messages=[
#         {
#             "role": "user",
#             "content": "Say this is a test",
#         },
#     ],
# )
# print(completion.choices[0].message.content)

# # Streaming:
# print("----- streaming request -----")
# stream = client.chat.completions.create(
#     model="gpt-4",
#     messages=[
#         {
#             "role": "user",
#             "content": "How do I output all files in a directory using Python?",
#         },
#     ],
#     stream=True,
# )
# for chunk in stream:
#     if not chunk.choices:
#         continue

#     print(chunk.choices[0].delta.content, end="")
# print()

# # Response headers:
# print("----- custom response headers test -----")
# response = client.chat.completions.with_raw_response.create(
#     model="gpt-4",
#     messages=[
#         {
#             "role": "user",
#             "content": "Say this is a test",
#         }
#     ],
# )
# completion = response.parse()
# print(response.request_id)
# print(completion.choices[0].message.content)


print("---- image generation ----")

image = client.images.generate(
    prompt="Do a polish person eating soup next to the argentinian obelisk", model="dall-e-3")

url_pattern = r'https?://[^\s<"]+|mailto:[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'

urls = re.findall(url_pattern, str(image))
img_link = urls[0]
img_link = img_link[:-4]

print("Link retrieved is:")
print(img_link)
print()

print("retrieving image from web...")
data = requests.get(img_link).content

f = open("generated_picture.png", "wb")

f.write(data)
f.close()

img = Image.open('generated_picture.png')
img.show()
