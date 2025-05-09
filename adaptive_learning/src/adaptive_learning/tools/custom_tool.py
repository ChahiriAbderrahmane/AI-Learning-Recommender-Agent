import json
import os
from typing import Optional, List
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer
from supabase import create_client, Client
import re
from typing import Optional
class LearningResourceUploader:
    def __init__(self, json_path: Optional[str] = None):
        load_dotenv()
        self.model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
        
        self.supabase_url = os.getenv("SUPERBASE_URL")  # e.g., https://xyzcompany.supabase.co
        self.supabase_key = os.getenv("SUPERBASE_KEY")  # anon or service role key
        self.supabase: Client = create_client(self.supabase_url, self.supabase_key)
        
        self.json_path = json_path
        self.resources = self.load_json() if json_path else []
    
    def load_json(self):
        try:
            with open(self.json_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"❌ Erreur de chargement JSON: {e}")
            return []
    
    def generate_embedding(self, text: str):
        return self.model.encode(text).tolist()
    
    def upload_all(self, user_query: str):
        # Use the resources list directly
        resource_list = self.resources

        for item in resource_list:
            try:
                # Convert item to dict if it's a string
                if isinstance(item, str):
                    item = json.loads(item)
                    
                embedding = self.generate_embedding(user_query)

                record = {
                    "user_query": user_query,
                    "embedding": embedding,
                    "source_link": item["source_link"],
                    "content_type": item["content_type"],
                    "difficulty_level": item["difficulty_level"],
                    "description": item["description"],
                    "relevance": item["relevance"]
                }

                response = self.supabase.table("learning_resources").insert(record).execute()
                if hasattr(response, 'error') and response.error:
                    print("❌ Insertion échouée:", response.error)
                else:
                    print("✅ Ressource insérée:", item["source_link"])

            except Exception as e:
                print(f"❌ Erreur lors de l'insertion d'une ressource: {e}")


    def find_similar_query(self, new_query: str, threshold: float = 0.95) -> Optional[List[dict]]:
        query_embedding = self.generate_embedding(new_query)
        
        # Recherche avec opérateur de distance vectorielle <#>
        response = self.supabase.rpc("match_learning_resources", {
                    "match_count": 5,  # Increased to get more potential matches
                    "match_threshold": threshold,
                    "query_embedding": query_embedding
                }).execute()
        
        if hasattr(response, 'error') and response.error:
            print("❌ Erreur de requête Supabase :", response.error)
            return None
        
        data = response.data
        if not data or len(data) == 0 or data[0].get("embedding") is None:
            print("❌ Aucune ressource trouvée dans la base de données.")
            return None

        # Filter results to ensure they are relevant to the query topic with at least 2 matching terms
        query_terms = new_query.lower().split()
        relevant_results = []
        for result in data:
            desc_terms = result.get('description', '').lower()
            query_terms_found = result.get('user_query', '').lower()
            matching_terms = sum(1 for term in query_terms if term in desc_terms or term in query_terms_found)
            if matching_terms >= 3:
                relevant_results.append(result)

        return relevant_results[:2] if relevant_results else None

def convert_to_valid_json(file_path: str) -> Optional[dict]:
    # Lire le contenu brut du fichier
    with open(file_path, "r", encoding="utf-8") as f:
        raw_content = f.read()

    # Extraire le bloc JSON depuis le markdown
    match = re.search(r"```json(.*?)```", raw_content, re.DOTALL)
    if not match:
        print("❌ Aucun bloc JSON trouvé dans le fichier.")
        return None

    json_str = match.group(1).strip()

    # Tenter de parser le JSON
    try:
        data = json.loads(json_str)
    except json.JSONDecodeError as e:
        print("❌ JSON invalide :", e)
        return None

    # Réécrire le fichier avec le JSON propre
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

    print("✅ Le fichier a été converti en JSON valide.")
    return data
