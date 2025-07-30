from typing import List, Dict, Any
from typing_extensions import TypedDict
from datetime import datetime, timezone

from langgraph.graph import StateGraph, END, START
from knowledge_graph.business.ba_knowledge_service import BAKnowledgeService
from utils.prompt_loading import prompt_loader
from langchain.chat_models import ChatOpenAI
from langchain_core.prompts import PromptTemplate

class BAKnowledgeState(TypedDict, total=False):
    query: str
    context_window: int
    timestamp: str
    context: Any
    status: str
    response: str
    memory: List[Dict[str, str]]
    metadata: Dict[str, Any]

class BAKnowledgeWorkflowBuilder:
    """Chịu trách nhiệm xây dựng và compile workflow graph."""

    def __init__(self, kg_service: BAKnowledgeService, system_prompt: str, llm: ChatOpenAI = None):
        self.kg_service    = kg_service
        self.system_prompt = system_prompt
        self.llm = llm

    def build(self) -> StateGraph:
        graph = StateGraph(state_schema=BAKnowledgeState)

        async def init_mem(state: BAKnowledgeState) -> BAKnowledgeState:
            if "memory" not in state:
                state["memory"] = []
            return state

        async def retrieve(state: BAKnowledgeState) -> BAKnowledgeState:
            print(f"Retrieving knowledge for query: {state['query']}")
            results = await self.kg_service.search_business_knowledge(state["query"])
            state["context"] = results
            return state

        async def generate(state: BAKnowledgeState) -> BAKnowledgeState:
            if not state.get("context"):
                state["status"] = "no_results"
                return state
            
            prompt_template = PromptTemplate.from_template(self.system_prompt)
            prompt = prompt_template.invoke({"question": state["query"], "context": state["context"]})
            print("Prompt is : ", prompt)
            llm_result = await self.llm.ainvoke(prompt)
            state["response"] = llm_result.content.strip()
            print(f"Generated response: {state['response']}")
            return state

        async def update_mem(state: BAKnowledgeState) -> BAKnowledgeState:
            state["memory"].append({"role": "user",      "content": state["query"]})
            state["memory"].append({"role": "assistant", "content": state["response"]})
            return state

        async def format_output(state: BAKnowledgeState) -> BAKnowledgeState:
            if state.get("status") == "no_results":
                return {
                    "status": "no_results",
                    "response": "Không tìm thấy thông tin phù hợp.",
                    "metadata": {
                        "query":       state["query"],
                        "processed_at": datetime.now(timezone.utc).isoformat()
                    }
                }
            confidence = 0.5
            sources    = []  
            state["status"] = "success"
            state["metadata"] = {
                "confidence":   confidence,
                "processed_at": datetime.now(timezone.utc).isoformat(),
                "sources":      sources
            }
            return state

        # Đăng ký nodes và edges
        graph.add_node("init_mem",    init_mem)
        graph.add_node("retrieve",    retrieve)
        graph.add_node("generate",    generate)
        graph.add_node("update_mem",  update_mem)
        graph.add_node("format",      format_output)

        graph.add_edge(START,         "init_mem")
        graph.add_edge("init_mem",    "retrieve")
        graph.add_edge("retrieve",    "generate")
        graph.add_edge("generate",    "update_mem")
        graph.add_edge("update_mem",  "format")
        graph.add_edge("format",      END)

        return graph.compile()