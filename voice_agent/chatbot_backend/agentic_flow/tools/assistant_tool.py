# chatbot_backend/agentic_flow/tools/assistant_tool.py

from pydantic import BaseModel, Field

from monitoring.logger.logger import Logger

# Initialize logger
log = Logger()


class TradingAgent(BaseModel):
    """ROUTE HERE WHEN THE USER ASKS ABOUT TRADING-RELATED QUERIES, SUCH AS start or stop trading.
        THIS AGENT SPECIALIZES IN:
            - Managing online trading access

        SUPPORTED TOOLS:
            - Online Trading Activation/Deactivation

        EXAMPLES QUESTIONS:
            - "Start online trading for my account"
            - "Stop online trading for my account"
        """
    Instruction: str = Field(description="User's or Supervisor's request related to trading activities or trading access.")
    log.info("Trading Agent Call.")
        
class ReportAgent(BaseModel):
    """ROUTE HERE WHEN THE USER REQUESTS SPECIFIC FINANCIAL AND INVESTMENT REPORTS OR STATEMENTS, CONTRACT NOTE, FOR REVIEW OR DOWNLOAD.
    THIS AGENT SPECIALIZES IN:
        - Providing financial/investment reports such as Profit and Loss (P&L) statements, ledger report, Sauda details, contract note, brokerage reports, etc.
        - Retrieving tax-related documents like Income Tax Return (ITR) reports, Securities Transaction Tax (STT) certificates, and Tax Deduction at Source (TDS) certificates
        - Other reports like reports Digi CMR, Mutual Funds Registrar Transfer Agent (RTA) statements
        - Supporting document generation and download flows

    SUPPORTED TOOLS:
        - Ledger Report, Profit and Loss Statement
        - Brokerage Report reports Statement, Contract Note, Sauda Details
        - Income tax return (ITR), Securities Transaction Tax (STT) certificates, Tax Deduction at Source  aka TDS Certificate, Mutual Fund Order Status
        - Digital Client Master Report aka DIGI CMR, Registrar Transfer Agend aka RTA Statement of mutual fund account, Grandfathered profit and loss aka P&L

    EXAMPLES QUESTIONS:
        - “I want my profit/loss statement”
        - “Please send me my tax documents”
        - “Download my brokerage report”
        - Need my RTA statement”
        - “I need my mutual fund RTA statement”
        - "Show me my contract note summary"
        - "Fetch my sauda details"
        - "What are my recent trade transactions"
        - “provide my contract note”
    """
    Instuction: str = Field(description="User's or Supervisor's request for financial or investment reports.")
    log.info("Report Agent Call.")

class AccountAgent(BaseModel):
    """ROUTE HERE WHEN THE USER WANTS TO VIEW OR MANAGE ACCOUNT INFORMATION AND SETTINGS.

        THIS AGENT SPECIALIZES IN:
            - Retrieving client profile details and dashboard information
            - Checking account status or modification status
            - Accessing branch details
            - Handling dormant account reactivation requests
            - Providing account opening/modification resources for different personas
            - Accessing modification forms (offline and online)
            - Processing online modifications for trading account details

        SUPPORTED TOOLS:
            - View client details/profile data
            - Check account dashboard/summary
            - Track account modification status
            - Access branch information
            - Get dormant reactivation status
            - Retrieve account opening/modification forms for:
              (Individual, HUF, NRI, Partnership, Corporate, Trust)
            - Online modification of trading account details:
              (Email, Phone Number, Address, Bank Details, Nominee)

        EXAMPLES QUESTIONS:
            - "What's my account status?"
            - "Show me my client profile"
            - "I need my account details"
            - "Check my modification status"
            - "Get me account opening forms"
            - "How to reactivate my dormant account"
            - "What's my branch information?"
            - "Update my account type/segment"
            - "Change my email address"
            - "Update my phone number"
            - "I want to modify my bank details"
            - "How can I update my address?"
            - "Change my nominee details"
        """
    Instuction: str = Field(description="User's or Supervisor's request regarding account details or changes.")
    log.info("Account Agent Call.")

class InformationCentreAgent(BaseModel):
    """ROUTE HERE WHEN THE USER ASKS ABOUT MARKET INFORMATION, CORPORATE ACTIONS, OR GENERAL ASSISTANCE.

        THIS AGENT SPECIALIZES IN THREE MAIN AREAS:
            1. CORPORATE ACTIONS & MARKET EVENTS
                - Timely updates on equity-related corporate actions
                - Information about IPOs, buybacks, splits, dividends
                - Market event announcements and implications
            
            2. MARKET RESEARCH & INSIGHTS
                - Access to research reports and market analysis
                - Industry insights and sectoral performance
                - Investment opportunity information
            
            3. GENERAL ASSISTANCE & FAQS
                - Explanation of regulations, policies, and procedures
                - Guidance on platform features and functionality
                - Common troubleshooting and how-to questions

        WHEN TO USE THIS AGENT:
            - User asks "How do I..." or "How to..." questions
            - User asks "Where do I..." or "Where to..." questions  
            - User asks "What are the steps..." or procedural questions
            - User mentions corporate actions, IPOs, buybacks, or market events
            - User requests research reports or market insights
            - User has general questions about processes or platform usage

        EXAMPLES QUESTIONS:
            - "Send me the latest market research"
            - "Tell me about upcoming IPOs"
            - "Which companies are doing buybacks?"
            - "How do I reset my password?"
            - "What is the process for account verification?"
            - "What are the current market trends?"
            - "What is SPEED-e of NSDL?"
            - "What is DIS?"
            - "Are existing client details mandatory to mention on given modification form?"
            - "Can a demat account be opened if a trading or commodity account exists?"
            - "Do i need to give documents if I am KRA registered?"
            - "What is Physical Settlement in EQ-Derivatives?"
            - "Why does the session get expired?"
        """
    Instruction: str = Field(description="User's or Supervisor's request for general information or assistance.")
    log.info("Information Centre Agent Call.")

class FundAgent(BaseModel):
    """ROUTE HERE WHEN THE USER ASKS ABOUT FUNDS, MARGIN, OR PAYMENT-RELATED STATUS.

        THIS AGENT SPECIALIZES IN:
            - Responding to questions about fund transfers or payout requests
            - Delivering margin availability, penalties, or shortfall summaries
            - Checking Mutual Fund order status

        SUPPORTED TOOLS:
            - Fund Transfer Status, Fund Payout Status
            - Available Margin Status, Margin Shortage Penalty Report
            - Mutual Fund Order Status

        EXAMPLES QUESTIONS:
            - "Check my payout status"
            - "How much margin is left?"
            - "Was I charged a margin penalty?"
            - "What's the status of my mutual fund order?"
            - "Has my SIP been processed?"
            - "Is my fund transfer complete?"
            - "Show me my available margin"
            - "Did I receive any margin shortage penalties?"
            - "When will my payout be processed?"
            - "Track my recent fund transfer"
            - "What's the status of my SIP purchase?"
            - "Check if my mutual fund redemption is complete"
            - "Show me my margin shortage report"
        """
    Instuction: str = Field(description="User's or Supervisor's request about funds, payouts, or margin status.")
    log.info("Fund Agent Call.")

class DPAgent(BaseModel):
    """
    ROUTE HERE IF THE USER REQUESTS HELP SPECIFICALLY WITH DP-RELATED ITEMS, INCLUDING DP STATEMENT, HOLDINGS, OR DPID.
    THIS AGENT SPECIALIZES IN:
        - DP transaction statement requests (typically related to demat account activity)
        - Queries asking for total holdings in demat account (not investment P&L)
        - Requests for DPID (Depository Participant ID)
        - DIS/DRF Status, Change Advisor Request, DIGI CMR Report
    KEY DIFFERENTIATORS:
        - Use when the user mentions "DP", "Demat"
        - Statements or reports **about holdings** in the **depository account** (not brokerage, tax, or P&L, or ITR )
    EXAMPLES QUESTIONS:
        - “Send me my DP statement”
        - “Download my dp holdings report”
        - “What is my DPID?”
        - “I want to check my securities in DP”
        - "give me my DIGI CMR report"
        - "What is my DRF status?"
        - "What is my DP holdings?"
        - "change my advisor request"
    """
    Instruction: str = Field(
        description="DP-specific user request focused on demat account holdings, statements, or DPID."
    )
    log.info("DP Agent Call.")

# Agents list
agents_tools = [ReportAgent, AccountAgent, InformationCentreAgent, FundAgent, TradingAgent, DPAgent ]