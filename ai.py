from google import genai
# import chromadb
# from chromadb.utils.embedding_functions import OpenCLIPEmbeddingFunction
# from chromadb.utils.data_loaders import ImageLoader
from pydantic import BaseModel
from dotenv import load_dotenv
import os
import datetime
import json

# # lm studio extension
# import base64
# from openai import OpenAI
from PIL import Image
# import json

load_dotenv()

# Configure Gemini 2.5 Flash-Lite
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = os.getenv("GEMINI_MODEL")
client = genai.Client(api_key=GEMINI_API_KEY)

# # Init ChromaDB (Local)
# chroma_client = chromadb.PersistentClient(path="./data/chroma")

# # Use OpenCLIP so Chroma can compare image vectors directly
# embedding_function = OpenCLIPEmbeddingFunction()
# image_loader = ImageLoader()

# collection = chroma_client.get_or_create_collection(
#     name="meal_history_vision",
#     embedding_function=embedding_function,
#     data_loader=image_loader
# )

# def delete_last_chroma_entry(user_id, image_path):
#     entry_id = f"meal_{user_id}_{hash(image_path)}"
#     collection.delete(ids=[entry_id])

# def reset_chroma_db():
#     all_ids = collection.get()['ids']
#     if all_ids:
#         collection.delete(ids=all_ids)

class MealAnalysis(BaseModel):
    food_name: str
    calories: int
    protein: int
    carbs: int
    fats: int

def analyze_meal(image_path, user_id):
    img = Image.open(image_path)

    # # 1. RAG Query
    # query_results = collection.query(
    #     query_texts=["recent meals"],
    #     n_results=5,
    #     where={"user_id": user_id},
    #     include=["documents", "distances"]
    # )

    # # 2. Threshold Logic & Diagnostic String
    # relevant_docs = []
    diag_lines = [f"🔍 *RAG Debug:*"]

    # if query_results['distances'][0]:
    #     for doc, dist in zip(query_results['documents'][0], query_results['distances'][0]):
    #         status = "✅" if dist < 0.4 else "❌"
    #         diag_lines.append(f"{status} Dist: {dist:.3f} | {doc[:20]}...")
    #         if dist < 0.4: relevant_docs.append(doc)
    # else:
    #     diag_lines.append("⏸️ No past memory found.")

    # context = f"Past meals: {relevant_docs}" if relevant_docs else "No relevant memory."

    # Gemini Call
    context = ""
    response = client.models.generate_content(
        model=GEMINI_MODEL,
        contents=[f"{context}\nAnalyze this image.", img],
        config={'response_mime_type': 'application/json', 'response_schema': MealAnalysis}
    )

    # Token Usage
    usage = response.usage_metadata
    diag_lines.append(f"📊 *Tokens:* P: {usage.prompt_token_count} | O: {usage.candidates_token_count}")

    # Store in Vector DB
    data = response.parsed
    # collection.add(
    #     documents=[f"{data.food_name} - {data.calories} kcal"],
    #     metadatas=[{"user_id": user_id}],
    #     ids=[f"meal_{user_id}_{hash(image_path)}"]
    # )

    return data.model_dump(), "\n".join(diag_lines)


### LM STUDIO extension
# client_lms = OpenAI(base_url="http://localhost:1234/v1", api_key="lm-studio")
# print('LM Studio client initialized')

# def encode_image(image_path):
#     with open(image_path, "rb") as image_file:
#         return base64.b64encode(image_file.read()).decode('utf-8')

# def analyze_meal_lmstudio(image_path, user_id):
#     # 1. RAG Query (Keep your existing ChromaDB logic)
#     print('analyze lm studio')
#     diag_lines = []
#     image = image_loader([image_path])
#     image_np = image[0]
#     query_results = collection.query(
#         query_images=[image_np],
#         n_results=1,
#         where={"user_id": user_id},
#         include=["metadatas", "distances"]
#     )

#     # 2. Threshold Check (0.2 is very tight similarity)
#     if query_results['distances'] and query_results['distances'][0]:
#         distance = query_results['distances'][0][0]
#         if distance < 0.2:
#             best_match = query_results['metadatas'][0][0]

#             # Reconstruct the data from metadata
#             data = {
#                 "food_name": best_match['food_name'],
#                 "calories": best_match['calories'],
#                 "protein": best_match['protein'],
#                 "carbs": best_match['carbs'],
#                 "fats": best_match['fats']
#             }

#             diag_lines.append(f"🎯 *Visual Match Found!*\n"
#                     f"Dist: {distance:.4f}\n"
#                     f"⚡ Speed: (No LLM used)")

#             return data, diag_lines


#     # LM Studio works best with explicit prompt instructions for JSON
#     prompt = f"""
#     Return ONLY a tidied JSON object with:
#         food_name: chicken rice,
#         calories: 500,
#         protein: 100,
#         carbs: 50,
#         fats: 20.
#     """
#     print('prompt ready')
#     # 3. Local Model Call
#     response = client_lms.chat.completions.create(
#         model="google/gemma-3-1b", # Example: Replace with your loaded Vision model
#         messages=[
#             {
#                 "role": "user",
#                 "content": [
#                     {"type": "text", "text": prompt},
#                 ],
#             }
#         ],
#         temperature=0.2,
#     )

#     # 4. Parsing the Response
#     # Local models might add markdown, so we reuse the clean_json_string logic
#     raw_text = response.choices[0].message.content
#     cleaned_text = raw_text.replace("```json", "").replace("```", "").strip()
#     data = json.loads(cleaned_text)
#     print(f'data: {data}')
#     usage = response.usage
#     diag_lines.append(f"📊 *Local Tokens:* P: {usage.prompt_tokens} | C: {usage.completion_tokens}")

#     collection.add(
#         uris=[image_path],
#         metadatas=[{
#             "user_id": user_id,
#             "food_name": data['food_name'],
#             "calories": int(data['calories']),
#             "protein": int(data['protein']),
#             "carbs": int(data['carbs']),
#             "fats": int(data['fats']),
#         }],
#         ids=[f"meal_{user_id}_{int(time.time())}"]
#     )

#     diag_lines.append(f"🔍 *New Meal Analyzed*\n"
#             f"📊 Tokens: {usage.total_tokens}\n"
#     )
#     return data, "\n".join(diag_lines)
