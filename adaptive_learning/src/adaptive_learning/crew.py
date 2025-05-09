from crewai import Agent, Task , Crew, Process, LLM
from crewai.project import CrewBase, agent, task, crew
import os
from dotenv import load_dotenv
from crewai_tools import BraveSearchTool

# Load environment variables
load_dotenv()

# LLM Object from crewai package
llm = LLM(model="gemini-2.0-flash-001",api_key=os.getenv("GEMINI_API_KEY"))

exa_api_key = os.getenv("EXA_API_KEY")
brave_api = os.getenv("BRAVE_API_KEY")


# Verify Gemini API key
google_api_key = os.getenv("GEMINI_API_KEY")
if not google_api_key:
    raise ValueError("GEMINI_API_KEY not found in environment variables")
os.environ["GEMINI_API_KEY"] = google_api_key


# Initialize the tool for internet searching capabilities
brave_search_tool = BraveSearchTool(country="US",n_results=5)


@CrewBase
class recom_agent_team:
    """recommendation agent crew"""
    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"

    @agent
    def educational_researcher(self) -> Agent:
        return Agent(config=self.agents_config["educational_researcher"],allow_delegation=False,tools=[brave_search_tool],llm=llm) # type: ignore[index]
    
    @task
    def research_task(self) -> Task:
        return Task(
            config=self.tasks_config['research_task'], # type: ignore[index]
            output_file='resources/response.json', llm = llm # This is the file that will be contain the final report.
        )
    
    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=False,
            planning=True,
            llm=llm,
            memory=True
        )






