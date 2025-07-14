# agentic_flow/orchestrator/supervisor_langgraph.py

"""
Supervisor LangGraph Orchestrator

This module constructs the LangGraph-based orchestration logic for routing user input 
to the appropriate conversational agent using a Supervisor agent 
and a conditional state machine.

Each agent processes user state and produces responses based on its domain-specific logic.
"""

from typing import Dict, Any

from langgraph.graph import StateGraph
from langgraph.types import interrupt, Command

from config.config import ( REPORT_OPENAPI_SCHEMA_PATH, 
                            ACCOUNT_OPENAPI_SCHEMA_PATH, 
                            FUND_OPENAPI_SCHEMA_PATH, 
                            INFORMATION_CENTRE_OPENAPI_SCHEMA_PATH, 
                            TRADING_OPENAPI_SCHEMA_PATH,
                            PLAN_EXECUTE_OPENAPI_SCHEMA_PATH,
                            ACCOUNT_OPENAPI_STATIC_DATA,
                            INFORMATION_CENTRE_OPENAPI_STATIC_DATA
                            )

from agentic_flow.orchestrator.dynamic_router import (
    route_primary_assistant,
    report_dynamic_router,
    account_dynamic_router,
    fund_dynamic_router,
    information_dynamic_router,
    trading_dynamic_router,
    dp_dynamic_router)

from agentic_flow.orchestrator.human_in_loop_node import (
    report_human_node,
    account_human_node,
    fund_human_node,
    information_human_node,
    trading_human_node,
    dp_human_node)

from agentic_flow.orchestrator.final_response_node import (
    assistance_final_response_node,
    report_final_response_node,
    account_final_response_node,
    fund_final_response_node,
    trading_final_response_node,
    dp_final_response_node,
    information_final_response_node,
    )

from agentic_flow.orchestrator.leave_node import leave_node
from agentic_flow.orchestrator.tool_node import create_tool_node_with_fallback

from app.schemas.request_models import SupervisorState

from agentic_flow.orchestrator.supervisor_agent_v2 import Assistant, get_runnable_assistance
from agentic_flow.agents.api_agents.react_agent import ReactAgent, get_runnable_react
from agentic_flow.agents.faq_agent.information_center_agent import InformationCentreReactAgent, get_information_runnable_react
from agentic_flow.tools.react_tool import react_tools, information_centre_tools
from agentic_flow.utility import inject_tool_message, get_llm_model
from monitoring.logger.logger import Logger

# Initialize logger
log = Logger()
# Initialize the LLM model
model = get_llm_model()
log.info("ChatBedrockConverse model initialized successfully")

log.info("Rannnable Importing.")
# Create a runnable for the primary assistant
assistant_runnable = get_runnable_assistance(model)
# Create a runnable for the respective agent using their OpenAPI schema
report_runnable = get_runnable_react(model, REPORT_OPENAPI_SCHEMA_PATH)
account_runnable = get_runnable_react(model, ACCOUNT_OPENAPI_SCHEMA_PATH, ACCOUNT_OPENAPI_STATIC_DATA)
fund_runnable = get_runnable_react(model, FUND_OPENAPI_SCHEMA_PATH)
trading_runnable = get_runnable_react(model, TRADING_OPENAPI_SCHEMA_PATH)
information_runnable = get_information_runnable_react(model, INFORMATION_CENTRE_OPENAPI_SCHEMA_PATH, INFORMATION_CENTRE_OPENAPI_STATIC_DATA)
dp_runnable = get_runnable_react(model, PLAN_EXECUTE_OPENAPI_SCHEMA_PATH)

log.info("Rannnable for all agents created successfully.")

def create_langgraph_supervisor() -> StateGraph:
    """
    Creates and returns a LangGraph-based state machine for managing 
    conversational flow between supervisor and registered agents.

    Returns:
        StateGraph: A compiled LangGraph object with routing and agent logic.
    """
    log.info("Graph State define Initiated.")
    graph_builder = StateGraph(SupervisorState)
    log.info("Graph State define Successfull.")

    # ---------------------------- 
    log.info("Defining nodes in the graph.")

    # ----------------------------
    # Register Nodes in Graph
    # ----------------------------

    # Registering the agents and their tools
    log.info("Registering agents and tools in the graph.")
    # supervisor assitance node and tool node
    graph_builder.add_node("supervisor", Assistant(assistant_runnable))
    # graph_builder.add_node("supervisor_tools", create_tool_node_with_fallback(primary_assistant_tools))

    # Report Agent and its tools
    graph_builder.add_node("ReportAgent", ReactAgent(report_runnable))
    graph_builder.add_node("ReportAgent_tools", create_tool_node_with_fallback(react_tools))

    # Account Agent and its tools
    graph_builder.add_node("AccountAgent", ReactAgent(account_runnable))
    graph_builder.add_node("AccountAgent_tools", create_tool_node_with_fallback(react_tools))

    # Fund Agent and its tools
    graph_builder.add_node("FundAgent", ReactAgent(fund_runnable))
    graph_builder.add_node("FundAgent_tools", create_tool_node_with_fallback(react_tools))

    # Trading Agent and its tools
    graph_builder.add_node("TradingAgent", ReactAgent(trading_runnable))
    graph_builder.add_node("TradingAgent_tools", create_tool_node_with_fallback(react_tools))

    # Infromation Centre Agent and its tools
    graph_builder.add_node("InformationCentreAgent", InformationCentreReactAgent(information_runnable))
    graph_builder.add_node("InformationAgent_tools", create_tool_node_with_fallback(information_centre_tools))

    # DP Agent and its tools
    graph_builder.add_node("DPAgent", ReactAgent(dp_runnable))
    graph_builder.add_node("DPAgent_tools", create_tool_node_with_fallback(react_tools))

    # Human Nodes for each agent
    graph_builder.add_node("report_human_node", report_human_node)
    graph_builder.add_node("account_human_node", account_human_node)
    graph_builder.add_node("fund_human_node", fund_human_node)
    graph_builder.add_node("trading_human_node", trading_human_node)
    graph_builder.add_node("information_human_node", information_human_node)
    graph_builder.add_node("dp_human_node", dp_human_node)
    # Leave Node for returning to the main assistant
    graph_builder.add_node("leave_node", leave_node)

    # Final response node for FAQ handling
    graph_builder.add_node("information_final_response_node", information_final_response_node)
    # Final response node for assistance check
    graph_builder.add_node("assistance_final_response_node", assistance_final_response_node)
    # Final response node for API responses
    graph_builder.add_node("report_final_response_node", report_final_response_node)
    graph_builder.add_node("account_final_response_node", account_final_response_node)
    graph_builder.add_node("fund_final_response_node", fund_final_response_node)
    graph_builder.add_node("trading_final_response_node", trading_final_response_node)
    graph_builder.add_node("dp_final_response_node", dp_final_response_node)

    # ----------------------------
    # Graph Edges & Transitions
    # ----------------------------
    log.info("Adding edges to the graph.")
    # Add edges for the Supervisor Agent
    graph_builder.add_conditional_edges("supervisor", route_primary_assistant)
    # graph_builder.add_edge("supervisor_tools", "supervisor")

    # Add edges for the Report Agent
    graph_builder.add_conditional_edges("ReportAgent", report_dynamic_router)
    graph_builder.add_edge("ReportAgent_tools", "ReportAgent")
    graph_builder.add_edge("report_human_node", "ReportAgent")

    # Add edges for the Account Agent
    graph_builder.add_conditional_edges("AccountAgent", account_dynamic_router)
    graph_builder.add_edge("AccountAgent_tools", "AccountAgent")
    graph_builder.add_edge("account_human_node", "AccountAgent")

    # Add edges for the Fund Agent
    graph_builder.add_conditional_edges("FundAgent", fund_dynamic_router)
    graph_builder.add_edge("FundAgent_tools", "FundAgent")
    graph_builder.add_edge("fund_human_node", "FundAgent")

    # Add edges for the Trading Agent
    graph_builder.add_conditional_edges("TradingAgent", trading_dynamic_router)
    graph_builder.add_edge("TradingAgent_tools", "TradingAgent")
    graph_builder.add_edge("trading_human_node", "TradingAgent")

    # Add edges for the Information Centre Agent
    graph_builder.add_conditional_edges("InformationCentreAgent", information_dynamic_router)
    graph_builder.add_edge("InformationAgent_tools", "InformationCentreAgent")
    graph_builder.add_edge("information_human_node", "InformationCentreAgent")

    # Add edges for the DP Agent
    graph_builder.add_conditional_edges("DPAgent", dp_dynamic_router)
    graph_builder.add_edge("DPAgent_tools", "DPAgent")
    graph_builder.add_edge("dp_human_node", "DPAgent")

    # Add edges for the Leave Node
    graph_builder.add_edge("leave_node", "supervisor")
    
    # ----------------------------
    # Entry Point
    # ----------------------------

    graph_builder.set_entry_point("supervisor")
    log.info("LangGraph Supervisor created successfully.")

    return graph_builder
