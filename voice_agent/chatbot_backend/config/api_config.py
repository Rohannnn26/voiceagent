# chatbot_backend/config/api_config.py

"""
Configuration file for API endpoint-to-function mappings.
Each entry maps an API name to a tuple of:
- The function to call
- The list of required parameters
"""

from integrations.external_api_wrapper import (
    get_ledger_statement,
    get_client_details,
    get_brokerage_statement,
    get_itr_statement,
    get_pnl_statement,
    get_dpstatement,
    fund_transfer_link,
    get_clientwise_dpid,
    get_totalholdings,
    get_available_margin,
    get_my_dashboard,
    get_tds_certificate,
    get_stt_ctt_certificate,
    get_branch_details,
    get_market_research,
    get_emodification,
    get_address_physical_form,
    get_document_list_bank,
    get_document_list_address,
    get_upcoming_bse,
    get_upcoming_nse,
    get_mf_status,
    get_fund_payout_status,
    get_account_status_partner,
    get_margin_shortage,
    get_rta_statement,
    get_faq,
    get_fund_transfer_status,
    get_new_account_opening_individual,
    get_stop_online_trade,
    get_start_online_trade,
    get_grandfather_pnl,
    parse_mtf_response,
    get_digicmr_report,
    get_ipo,
    get_sauda_details,
    get_account_modification_status_online,
    get_account_modification_status_physical,
    get_contract_note,
    get_dis_drf_status,
    get_ledger_summary,
    get_segment_addition
)

PRIMARY_API_MAP = {
    "my_details": (
        get_client_details,
        ["user_id", "client_id", "role", "token", "session_id"],
    ),
    "ledger_report": (
        get_ledger_statement,
        ["user_id", "client_id", "role", "token", "session_id", "from_date", "to_date", "exchange_seg", "date_type", "return_type"],
    ),
    "brokerage_report": (
        get_brokerage_statement,
        ["user_id", "client_id", "role", "token", "session_id"],
    ),
    "itr_statement": (
        get_itr_statement,
        ["user_id", "client_id", "role", "token", "session_id", "from_date", "to_date","return_type"],
    ),
    "profit_and_loss_statement": (
        get_pnl_statement,
        ["user_id", "client_id", "role", "token", "session_id", "from_date", "to_date", "return_type"],
    ),
    "total_holdings": (
        get_totalholdings,
        ["user_id", "client_id", "role", "token", "session_id"],
    ),
    "dp_statement": (
        get_dpstatement,
        ["user_id", "client_id", "role", "token", "session_id", "from_date", "to_date", "statement_type", "dp_id", "return_type"],
    ),
    "available_margin": (
        get_available_margin,
        ["user_id", "client_id", "role", "token", "session_id"],
    ),
    "my_dashboard": (
        get_my_dashboard,
        ["user_id", "client_id", "role", "token", "session_id"],
    ),
    "tds_certificate": (
        get_tds_certificate,
        ["user_id", "client_id", "role", "token", "session_id"],
    ),
    "stt_ctt_certificate": (
        get_stt_ctt_certificate,
        ["user_id", "client_id", "role", "token", "session_id","from_date", "to_date"],
    ),
    "advisor": (
        get_branch_details,
        ["user_id", "client_id", "role","token", "session_id"],
    ),
    "markets_research_client": (
        get_market_research,
        [],
    ),
    "markets_research_partner": (
        get_market_research,
        [],
    ),
    "emodification": (
        get_emodification,
        ["user_id", "client_id", "role", "token", "session_id","type"],
    ),
    "address_physical_form": (
        get_address_physical_form,
        [],
    ),
    "document_list_bank": (
        get_document_list_bank,
        [],
    ),
    "document_list_address": (
        get_document_list_address,
        [],
    ),
    "upcoming_bse": (
        get_upcoming_bse,
        [],
    ),
    "upcoming_nse": (
        get_upcoming_nse,
        [],
    ),
    "mf_status": (
        get_mf_status,
        ["user_id", "client_id", "role", "token", "session_id","order_type"],
    ),
    "fund_payout_status": (
        get_fund_payout_status,
        ["user_id", "client_id", "role", "token", "session_id"],
    ),
    "account_status_partner": (
        get_account_status_partner,
        ["user_id", "client_id", "role", "token", "session_id","PanOrNumber"],
    ),
    "margin_shortage": (
        get_margin_shortage,
        ["user_id", "client_id", "role", "token", "session_id","from_date", "to_date"],
    ),
    "rta_statement": (
        get_rta_statement,
        ["user_id", "client_id", "role", "token", "session_id"],
    ),
    "faq": (
        get_faq,
        [],
    ),
    "fund_transfer_status": (
        get_fund_transfer_status,
        ["user_id", "client_id", "role", "token", "session_id"],
    ),
    "new_account_opening": (
        get_new_account_opening_individual,
        ["account_type"],
    ),
    "stop_online_trade": (
        get_stop_online_trade,
        ["user_id", "client_id", "role","token", "session_id"],
    ),
    "start_online_trade": (
        get_start_online_trade,
        ["user_id", "client_id", "role","token", "session_id"],
    ),
    "grandfather_pnl": (
        get_grandfather_pnl,
        ["user_id", "client_id", "role", "token", "session_id","from_date", "to_date"],
    ),
    "sauda_details" : (
        get_sauda_details,
        ["user_id", "client_id", "role", "token", "session_id","from_date", "to_date", "return_type"]
    ),
    "ipo" :(
        get_ipo,
        ["user_id", "client_id", "role", "token", "session_id"]
    ),
    "digi_cmr":(
        get_digicmr_report,
        ["user_id", "client_id", "role", "token", "session_id","dp_id", "return_type"]
    ),
    "acount_modification_status_online": (
        get_account_modification_status_online,
        ["user_id", "client_id", "role", "token", "session_id"]
    ),
    "acount_modification_status_physical": (
        get_account_modification_status_physical,
        []
    ),
    "contract_note": (
        get_contract_note,
        ["user_id", "client_id", "role", "token", "session_id","from_date", "to_date", "return_type"],
    ),
    "dis_drf_status": (
        get_dis_drf_status,
        ["user_id", "client_id", "role", "token", "session_id", "request_type"]
    ),
    "ledger_summary": (
        get_ledger_summary,
        ["user_id", "client_id", "role", "token", "session_id"]
    ),
    "segment_addition": (
        get_segment_addition,  
        ["user_id", "client_id", "role", "token", "session_id"]
    ),
    "fund_transfer_link": (
        fund_transfer_link,
        ["user_id", "client_id", "role", "token", "session_id"],
    ),
    "dormant_status": (
        get_emodification,
        ["user_id", "client_id", "role", "token", "session_id","type"]
    )
    

}

MID_STAGE_API_MAP = {
    "MTF": (
        parse_mtf_response,
        ["user_id", "client_id", "role", "token", "session_id"],
    ),
    "dp_holdings": (
        get_clientwise_dpid,
        ["user_id", "client_id", "role", "token", "session_id"],
    ),

    "digi_cmr":(
        get_clientwise_dpid,
        ["user_id", "client_id", "role", "token", "session_id"]
    ),
    "transaction_statement": (
        get_clientwise_dpid,
        ["user_id", "client_id", "role", "token", "session_id"],
    ),
}
