from adaptive_learning.crew import recom_agent_team, llm
from adaptive_learning.tools.custom_tool import LearningResourceUploader
from dotenv import load_dotenv
import os
import datetime

# Load environment variables
load_dotenv()
# print("GOOGLE_API_KEY:", os.getenv("GOOGLE_API_KEY"))  # Debug print

def log_conversation(message: str):
    """Append message to conversation log with timestamp."""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open("logs/conversation_log.txt", "a") as f:
        f.write(f"[{timestamp}] {message}\n")

def run():
    print("Welcome to the Educational assistant. I'm here to support you.")
    print("Type 'exit' to end the conversation.\n")
    log_conversation("Here we go.")
    
    path = 'C:/Users/elect/Desktop/POC - recommendation agent -/adaptive_learning/resources/response.json'

    # Assurez-vous que le chemin vers le fichier JSON est correct
    uploader = LearningResourceUploader(path)  # Ajustez le chemin si nécessaire
    
    conversation_history = []
        
    while True:
        user_input = input("You: ")
        log_conversation(f"You: {user_input}")
        if user_input.lower() == "exit":
            print("Keep learning to be the best of yourself!")
            log_conversation("Chatbot ended.")
            break
        
        conversation_history.append(f"User: {user_input}")
        inputs = {
            "user_input": user_input,
            "conversation_history": "\n".join(conversation_history[-5:])
        }
        
        # Utilisez find_similar_query au lieu de find_similar_resources
        similar_query = uploader.find_similar_query(new_query=user_input)
        
        if similar_query is None:
            crew = recom_agent_team()
            result = crew.crew().kickoff(inputs=inputs)
            
            print(f"Bot: {result}\n")
            log_conversation(f"Bot: {result}")
            
            # Utilisez la fonction en dehors de la classe
            from adaptive_learning.tools.custom_tool import convert_to_valid_json
            convert_to_valid_json("resources/response.json")
            
            # Rechargez le fichier JSON pour refléter les modifications
            uploader = LearningResourceUploader('resources/response.json')
            uploader.upload_all(user_query=user_input)
        
        else:
            # Formatage des ressources similaires pour l'affichage
            formatted_resources = []
            for idx, resource in enumerate(similar_query):
                formatted_resources.append(f"\n--- Ressource {idx+1} ---")
                formatted_resources.append(f"Source: {resource.get('source_link', 'N/A')}")
                formatted_resources.append(f"Type: {resource.get('content_type', 'N/A')}")
                formatted_resources.append(f"Niveau: {resource.get('difficulty_level', 'N/A')}")
                formatted_resources.append(f"Description: {resource.get('description', 'N/A')}")
                formatted_resources.append(f"Pertinence: {resource.get('relevance', 'N/A')}")
            
            response = "\n".join(formatted_resources)
            print(f"Bot: Voici des ressources similaires à votre requête:{response}\n")
            log_conversation(f"Bot: Ressources similaires trouvées")

