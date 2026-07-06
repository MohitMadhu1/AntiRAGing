from langgraph.graph import StateGraph, START, END
from .state import OnboardingState
from .architecture import run_architecture_agent
from .code_intelligence import run_code_intelligence_agent_async
from .docs_reconciliation import run_docs_agent
from .assembler import assemble_final_guide_async

def create_onboarding_graph():
    graph = StateGraph(OnboardingState)
    
    # Add nodes
    # We use the async versions for I/O bound tasks
    graph.add_node("architecture", run_architecture_agent)
    graph.add_node("code_intel", run_code_intelligence_agent_async)
    graph.add_node("docs", run_docs_agent)
    graph.add_node("assemble", assemble_final_guide_async)
    
    # Edges
    # Start -> parallel (arch, code_intel)
    graph.add_edge(START, "architecture")
    graph.add_edge(START, "code_intel")
    
    # Both must complete before docs can run, but in LangGraph we need to handle fan-in carefully
    # A simple way without custom reducers is to route sequentially or use a fan-in node
    # Since docs agent only depends on arch for now (based on prompt), we can run:
    # START -> code_intel -> END
    # START -> architecture -> docs -> assemble -> END
    # But assemble needs both.
    
    # For MVP simplicity, let's execute them sequentially in a chain to avoid complex state reducers
    # 1. architecture -> 2. code_intel -> 3. docs -> 4. assemble
    
    # Let's rebuild the graph sequentially for robustness
    sequential_graph = StateGraph(OnboardingState)
    sequential_graph.add_node("architecture", run_architecture_agent)
    sequential_graph.add_node("code_intel", run_code_intelligence_agent_async)
    sequential_graph.add_node("docs", run_docs_agent)
    sequential_graph.add_node("assemble", assemble_final_guide_async)
    
    sequential_graph.add_edge(START, "architecture")
    sequential_graph.add_edge("architecture", "code_intel")
    sequential_graph.add_edge("code_intel", "docs")
    sequential_graph.add_edge("docs", "assemble")
    sequential_graph.add_edge("assemble", END)
    
    return sequential_graph.compile()
