# integrations/external_api_wrapper.py
import requests
from typing import Dict
import requests
from functools import wraps
from config.config import BASE_URL_CONFIG , env
from monitoring.logger.logger import Logger
from langfuse import observe
log = Logger()
from agentic_flow.utility import langfuse

# Error-Handling Decorator 
def api_error_handler(func):
    """
    A decorator to handle errors for API requests.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except requests.RequestException as e:
            log.error(f"Request error in {func.__name__}: {str(e)}")
            return {"error": str(e)}
        except Exception as e:
            log.error(f"Unexpected error in {func.__name__}: {str(e)}")
            return {"error": f"An unexpected error occurred: {str(e)}"}
    return wrapper


# @api_error_handler
# @observe(name="register_token")
# def get_register_token(params: dict) -> dict:
    

#     url = f"{BASE_URL_CONFIG}/RegisterToken"


#     headers = {
#         'Content-Type': 'application/json',
#     }


#     #payload = f"userid={params['user_id']}&sessionId=''&token={params['token']}&source=desktop&device=D&platform=test"
#     payload = {
#         "userId": params['user_id'],
#         "sessionId": "",
#         "token": params['token'],
#         "source": "desktop",
#         "device": "D",
#         "platform": "test"
#     }
#     response = requests.request("POST", url, headers=headers, json=payload)
#     return response.json()


# Client Details API Wrapper
@api_error_handler
@observe(name="client_details")
def get_client_details(params: dict) -> dict:
    """
    Retrieves client details based on the system generated parameters and authorization

    Args:
        client_id (str): Unique identifier of the client whose details are to be retrieved.
        user_id (str): Identifier of the user making the request. (user_id and clientid is the same and is the clientcode of the client)
        session_id (str): Unique session identifier for tracking the request context.
        role (str): Role of the user ('PARTNER', 'CLIENT') to determine access level.
        token (str): Authorization token used to validate the request.
    """

    url = f"{BASE_URL_CONFIG}/clientdetails"

    headers = {
        'sessionid': f"{params['session_id']}",
        'token': f"{params['token']}",
        'Content-Type': 'application/json',
        
    }

    #payload = f"userid={params['user_id']}&clientid={params['client_id']}&role={params['role']}"
    payload = {
        "userId": params['user_id'],
        "clientId": params['client_id'],
        "role": params['role']
        }

    
    response = requests.request("POST", url, headers=headers, json=payload)
    return response.json()

# Ledger Statement API wrapper 
@api_error_handler
@observe(name="Ledger_Statement")
def get_ledger_statement(params: dict) -> dict:
    """
    Retrieves ledger report of the client based on system-generated and user-selected parameters.

    Args:
        params (dict): Dictionary containing the following keys:
            - client_id (str)
            - user_id (str)
            - session_id (str)
            - role (str)
            - token (str)
            - exchange_seg (str): ('Combine|Voucher', 'Combine|Effective', 'MTF|Voucher', 'MTF|Effective', 'LAS|Voucher')
            - from_date (str): 'dd/mm/yyyy'
            - to_date (str): 'dd/mm/yyyy'
            - return_type (str): ('View & Download', 'Email')
    """

    url = f"{BASE_URL_CONFIG}/ledgerstatement"

    headers = {
        'sessionid': params['session_id'],
        'token': params['token'],
        'Content-Type': 'application/json'
    }
    payload = {
        "userId": params['user_id'],
        "clientId": params['client_id'],
        "role": params['role'],
        "from_Date": params['from_date'],
        "to_Date": params['to_date'],
        "exchange_Seg": params['exchange_seg'],
        "date_Type": params['date_type'],
        "return_Type": params['return_type']
    }
    log.info(f"Here is the payload data: {payload}")

    response = requests.post(url, headers=headers, json=payload)
    
    return response.json()

    
# Brokerage Statement API wrapper
@api_error_handler
@observe(name="Brokerage_Statement")
def get_brokerage_statement(params:dict) ->dict:
    
    """
    Retrieves brokerage report of the client based on system generated params and user selected params

    Args:
        client_id (str): Unique identifier of the client whose details are to be retrieved.
        user_id (str): Identifier of the user making the request. (user_id and clientid is the same and is the clientcode of the client)
        session_id (str): Unique session identifier for tracking the request context.
        role (str): Role of the user ('PARTNER', 'CLIENT') to determine access level.
        token (str): Authorization token used to validate the request.
        return_type(str) : The return type refers to view & download or Email. I.e it can only be 2 values  ('View & Download','Email')
    """
    url = f"{BASE_URL_CONFIG}/BrokerageDetails"

    headers = {
        'sessionid': f"{params['session_id']}",
        'token': f"{params['token']}",
        'Content-Type': 'application/json',
        
    }

    payload = {
        "userId": params['user_id'],
        "clientId": params['client_id'],
        "role": params['role'],
        "Return_Type": "Link"
    }

    response = requests.post(url, headers=headers, json=payload)
    log.info(f"{response} - BROKERAGE REPORT")
    return response.json()

# Profit and Loss Statement API wrapper
@api_error_handler
@observe(name="Profit_and_Loss_Statement")
def get_pnl_statement(params:dict)->dict:
    """
    Retrieves Profit and Loss Statement of the client based on system generated params and user selected params

    Args:
        client_id (str): Unique identifier of the client whose details are to be retrieved.
        user_id (str): Identifier of the user making the request. (user_id and clientid is the same and is the clientcode of the client)
        session_id (str): Unique session identifier for tracking the request context.
        role (str): Role of the user ('PARTNER', 'CLIENT') to determine access level.
        from_date(str) : from date can be given by the user in dd/mm/yyyy format or when options chosen from date range [3M,6M,Current Year, Previou Year]
                        from date is automatically set based on period range. 
        to_date(str) : to date will be the current date when the user / client will be interacting on
        token (str): Authorization token used to validate the request.
        return_type(str) : The return type refers to view & download or Email. I.e it can only be 2 values  ('View & Download','Email')
    """
    url = f"{BASE_URL_CONFIG}/capitalgainloss"

    headers = {
        'sessionid': f"{params['session_id']}",
        'token': f"{params['token']}",
        'Content-Type': 'application/json',
        
    }

    payload = {
        "userId": params['user_id'],
        "clientId": params['client_id'],
        "role": params['role'],
        "from_Date": params['from_date'],
        "to_Date": params['to_date'],
        "return_Type": params['return_type']
    }

    response = requests.post(url, headers=headers, json=payload)
    return response.json()

# ITR Statement Wrapper
@api_error_handler
@observe(name="ITR_Statement")
def get_itr_statement(params:dict)->dict:
    """
    Retrieves ITR Statement of the client based on system generated params and user selected params

    Args:
        client_id (str): Unique identifier of the client whose details are to be retrieved.
        user_id (str): Identifier of the user making the request. (user_id and clientid is the same and is the clientcode of the client)
        session_id (str): Unique session identifier for tracking the request context.
        role (str): Role of the user ('PARTNER', 'CLIENT') to determine access level.
        from_date(str) : from date can be given by the user in dd/mm/yyyy format or when options chosen from date range [3M,6M,Current Year, Previou Year]
                        from date is automatically set based on period range. 
        to_date(str) : to date will be the current date when the user / client will be interacting on
        token (str): Authorization token used to validate the request. """
    url = f"{BASE_URL_CONFIG}/ITRStatement"

    headers = {
        'sessionid': f"{params['session_id']}",
        'token': f"{params['token']}",
        'Content-Type': 'application/json',
        
    }

    payload = {
        "userId": params['user_id'],
        "clientId": params['client_id'],
        "role": params['role'],
        "from_Date": params['from_date'],
        "to_Date": params['to_date'],
        "Return_Type": params['return_type'],
        "StatementType": "ITR"
    }

    response = requests.request("POST", url, headers=headers, json=payload)
    return response.json()


@api_error_handler
@observe(name="MTF_LAS_Response")
def parse_mtf_response(params: dict) -> Dict:
    
    url = f"{BASE_URL_CONFIG}/CheckClientMTFLAS"

    headers = {
        'sessionid': params['session_id'],
        'token': params['token'],
        'Content-Type': 'application/json'
    }
    log.info(f"Here is the payload data: {params}")
    payload = {
        "UserId": params['user_id'],
        "ClientId": params['client_id'],
        "Role": params['role'],
        "Type": "MTF"
    }
    response = requests.post(url, headers=headers, json=payload)
    return response.json()


@api_error_handler
@observe(name="Clientwise_DPID")
def get_clientwise_dpid(params:dict)->Dict:
    """

    """
    url = f"{BASE_URL_CONFIG}/GetClientWiseDPId"

    headers = {
        'sessionid': f"{params['session_id']}",
        'token': f"{params['token']}",
        'Content-Type': 'application/json',
        
    }
    payload = {"userId": params['user_id'],
                "clientId": params['client_id'],
                "role": params['role']
    }

    response = requests.request("POST", url, headers=headers, json=payload)
    return response.json()

@api_error_handler
@observe(name="DP_Statement")
def get_dpstatement(params:dict) -> Dict:
    """
    
    """
    url = f"{BASE_URL_CONFIG}/DPStatement"

    headers = {
        'sessionid': f"{params['session_id']}",
        'token': f"{params['token']}",
        'Content-Type': 'application/json',
        
    }

    payload = {
        "userId": params['user_id'],
        "clientId": params['client_id'],
        "role": params['role'],
        "from_Date": params['from_date'],
        "to_Date": params['to_date'],
        "statementType": params['statement_type'],
        "dpId": params['dp_id'],
        "return_Type": params['return_type']
    }

    response = requests.request("POST", url, headers=headers, json=payload)
    return response.json()

@api_error_handler
@observe(name="Ledger_Summary")
def get_ledger_summary(params:dict) -> Dict:
    """
    
    """
    url = f"{BASE_URL_CONFIG}/LedgerBalanceSummary"

    headers = {
        'sessionid': f"{params['session_id']}",
        'token': f"{params['token']}",
        'Content-Type': 'application/json',
        
    }

    payload = {
        "userId": params['user_id'],
        "clientId": params['client_id'],
        "role": params['role']
    }
    response = requests.request("POST", url, headers=headers, json=payload)
    return response.json()

@api_error_handler
@observe(name="Segment_Additional_Link")
def get_segment_addition(params:dict) -> Dict:
    """
    
    """
    url = f"{BASE_URL_CONFIG}/SegmentAdditionalLink"

    headers = {
        'sessionid': f"{params['session_id']}",
        'token': f"{params['token']}",
        'Content-Type': 'application/json',
        
    }

    payload = {
        "userId": params['user_id'],
        "clientId": params['client_id'],
        "role": params['role'],
        "return_Type": "Link"
    }
    response = requests.request("POST", url, headers=headers, json=payload)
    return response.json()

@api_error_handler
@observe(name="Total_Holdings")
def get_totalholdings(params:dict) -> Dict:
    """
    
    """
    url = f"{BASE_URL_CONFIG}/CollateralHolding"

    headers = {
        'sessionid': f"{params['session_id']}",
        'token': f"{params['token']}",
        'Content-Type': 'application/json',

    }

    payload = {
        "userId": params['user_id'],
        "clientId": params['client_id'],
        "role": params['role'],
        "return_type": "Link"
    }
    response = requests.request("POST", url, headers=headers, json=payload)
    return response.json()

@api_error_handler
@observe(name="Valid_Client_Code")
def valid_clientcode(params:dict) -> dict:
    url = f"{BASE_URL_CONFIG}/ValidClientCode"
    
    
    headers = {
    'sessionid': f"{params['session_id']}",
    'token': f"{params['token']}",
    'Content-Type': 'application/json'
    }

    payload = {
        "userId": params['user_id'],
        "clientId": params['client_id'],
        "role": params['role']
    }

    response = requests.request("POST", url, headers=headers, json=payload)

    return response.json()

@api_error_handler
@observe(name="Branch_Details")
def get_branch_details(params:dict) -> Dict:
    url = f"{BASE_URL_CONFIG}/BranchDetails"

    headers = {
        'sessionid': f"{params['session_id']}",
        'token': f"{params['token']}",
        'Content-Type': 'application/json'
    }
    payload = {
        "userId": params['user_id'],
        "clientId": params['client_id'],
        "role": params['role']
    }
    response = requests.request("POST", url, headers=headers, json=payload)

    return response.json()

@api_error_handler
@observe(name="My_Dashboard")
def get_my_dashboard(params:dict) -> dict:
    url = f"{BASE_URL_CONFIG}/ClientView"
    headers = {
        'sessionid': f"{params['session_id']}",
        'token': f"{params['token']}",
        'Content-Type': 'application/json'
    }
    payload = {
        "userId": params['user_id'],
        "clientId": params['client_id'],
        "role": params['role']
    }
    response = requests.request("POST", url, headers=headers, json=payload)
    return response.json()


@api_error_handler
@observe(name="Available_Margin")
def get_available_margin(params:dict) -> dict:
    url = f"{BASE_URL_CONFIG}/MarginShortage"
    headers = {
        'sessionid': f"{params['session_id']}",
        'token': f"{params['token']}",
        'Content-Type': 'application/json'
    }
    payload = {
        "userId": params['user_id'],
        "clientId": params['client_id'],
        "role": params['role'],
        "Segment": "E"
    }
    response = requests.request("POST", url, headers=headers, json=payload)
    return response.json()


@api_error_handler
@observe(name="TDS_Certificate")
def get_tds_certificate(params:dict) -> dict:
    url = f"{BASE_URL_CONFIG}/GetSaticLinkOrFile"
    headers = {
        'sessionid': f"{params['session_id']}",
        'token': f"{params['token']}",
        'Content-Type': 'application/json'
    }
    payload = {
        "userId": params['user_id'],
        "clientId": params['client_id'],
        "role": params['role'],
        "linkType": "tdscertificate"
    }
    response = requests.request("POST", url, headers=headers, json=payload)
    return response.json()

@api_error_handler
@observe(name="STT_CTT_Certificate")
def get_stt_ctt_certificate (params:dict) -> dict:
    url = f"{BASE_URL_CONFIG}/STTCertificate"
    headers = {
        'sessionid': f"{params['session_id']}",
        'token': f"{params['token']}",
        'Content-Type': 'application/json'
    }
    payload = {
        "userId": params['user_id'],
        "clientId": params['client_id'],
        "role": params['role'],
        "from_Date": params['from_date'],
        "to_Date": params['to_date'],
        "Return_Type": "Link"
    }
    response = requests.request("POST", url, headers=headers, json=payload)
    return response.json()

@api_error_handler
@observe(name="Client_CMR_Report")
def get_digicmr_report(params:dict)-> dict:
    url = f"{BASE_URL_CONFIG}/ClientCMRReport"
    headers = {
        'sessionid': f"{params['session_id']}",
        'token': f"{params['token']}",
        'Content-Type': 'application/json'
    }

    payload = {
        "userId": params['user_id'],
        "clientId": params['client_id'],
        "role": params['role'],
        "dpId": params['dp_id'],
        "return_Type": params['return_type']
    }

    response = requests.request("POST", url, headers=headers, json=payload)
    return response.json()

@api_error_handler
@observe(name="Sauda_Details")
def get_sauda_details(params: dict) -> dict:
    url = f"{BASE_URL_CONFIG}/SaudaDetails"  

    headers = {
        'sessionid': f"{params['session_id']}",
        'token': f"{params['token']}",
        'Content-Type': 'application/json'
    }

    payload = {
        "userId": params['user_id'],
        "clientId": params['client_id'],
        "role": params['role'],
        "from_Date": params['from_date'],
        "to_Date": params['to_date'],
        "return_Type": params['return_type']
    }

    

    response = requests.request("POST", url, headers=headers, json=payload)
    return response.json()

@api_error_handler
@observe(name="Active_IPO")
def get_ipo(params: dict) -> dict:
    url = f"{BASE_URL_CONFIG}/ActiveIPO"

    headers = {
        'sessionid': f"{params['session_id']}",
        'token': f"{params['token']}",
        'Content-Type': 'application/json'
    }

    payload = {
        "userId": params['user_id'],
        "clientId": params['client_id'],
        "role": params['role']
    }

    response = requests.request("POST", url, headers=headers, json=payload)
    return response.json()


@api_error_handler
@observe(name="Market_Research")
def get_market_research(params:dict = None) -> dict:

    url = "https://www.motilaloswal.com/stock-research"
    data = {
            "message" : url
        }

    return data

@api_error_handler
@observe(name="FAQ")
def get_faq(params:dict = None) -> Dict:

    url = "https://www.motilaloswal.com/"
    data = {
            "message" : url
        }

    return data


@api_error_handler
@observe(name="eModification_Details")
def get_emodification(params:dict) -> dict:
    url = f"{BASE_URL_CONFIG}/eModificationDetails"
    headers = {
        'sessionid': f"{params['session_id']}",
        'token': f"{params['token']}",
        'Content-Type': 'application/json'
    }
    payload = {
        "userId": params['user_id'],
        "clientId": params['client_id'],
        "role": params['role'],
        "Type": params['type']
    }
    response = requests.request("POST", url, headers=headers, json=payload)
    return response.json()

@api_error_handler
@observe(name="Address_Physical_Form")
def get_address_physical_form(params:dict = None) -> Dict:

    url = "https://mofsl.co/pdf/ModificationFormVersion_1_8.pdf"
    data = {
            "message" : url
        }

    return data

@api_error_handler
@observe(name="Bank_Physical_Form")
def get_document_list_bank(params:dict = None) -> Dict:

    text = """List of docs for bank modification:
1] Bank Proof like Bank Statement / bank passbook for latest 3 months.
2] Cancelled cheque acceptable ( If client is giving original cancelled cheque with his/her name printed on it there is no need for client signature )"""
    data = {
            "message" : text
        }

    return data

@api_error_handler
@observe(name="Address_Physical_Form")
def get_document_list_address(params:dict = None) -> Dict:

    text = """1] Passport/Voters Identity Card
2] Bank Account Statement/Passbook – for latest 3 months
3] Latest utility bills like telephone/electricity/gas bill
4] driving license
"""
    data = {
            "message" : text
        }

    return data

@api_error_handler
@observe(name="Upcoming_BSE")
def get_upcoming_bse(params:dict = None) -> Dict:

    url = "https://www.bseindia.com/markets/PublicIssues/AcqIssueDetail.aspx?expandable=3&Type=2"
    data = {
            "message" : url
        }

    return data

@api_error_handler
@observe(name="Upcoming_NSE")
def get_upcoming_nse(params:dict = None) -> Dict:

    url = "https://www.nseindia.com/live_market/content/live_watch/tender_offer/tender_offer.htm"
    data = {
            "message" : url
        }

    return data

@api_error_handler
@observe(name="MF_Order_Status")
def get_mf_status (params:dict) -> dict:
    url = f"{BASE_URL_CONFIG}/MF_ORDERSTATUS"
    headers = {
        'sessionid': f"{params['session_id']}",
        'token': f"{params['token']}",
        'Content-Type': 'application/json'
    }
    payload = {
        "userId": params['user_id'],
        "clientId": params['client_id'],
        "role": params['role'],
        "OrderType": params['order_type']
    }
    response = requests.request("POST", url, headers=headers, json=payload)
    return response.json()

@api_error_handler
@observe(name="Fund_Payout_Status")
def get_fund_payout_status(params:dict) -> dict:
    url = f"{BASE_URL_CONFIG}/CordysFundPayoutStatus"
    headers = {
        'sessionid': f"{params['session_id']}",
        'token': f"{params['token']}",
        'Content-Type': 'application/json'
    }
    payload = {
        "userId": params['user_id'],
        "clientId": params['client_id'],
        "role": params['role']
    }
    response = requests.request("POST", url, headers=headers, json=payload)
    return response.json()

@api_error_handler
@observe(name="Account_Status_Partner")
def get_account_status_partner(params:dict) -> dict:
    url = f"{BASE_URL_CONFIG}/AccountStatusReq"
    headers = {
        'sessionid': f"{params['session_id']}",
        'token': f"{params['token']}",
        'Content-Type': 'application/json'
    }
    payload = {
        "userId": params['user_id'],
        "clientId": params['client_id'],
        "role": params['role'],
        "PanOrNumber": params['pan_or_number']
    }
    response = requests.request("POST", url, headers=headers, json=payload)
    return response.json()

@api_error_handler
@observe(name="Margin_Shortage_Penalty")
def get_margin_shortage(params:dict) -> dict:
    url = f"{BASE_URL_CONFIG}/MarginShortagePenalty"
    headers = {
        'sessionid': f"{params['session_id']}",
        'token': f"{params['token']}",
        'Content-Type': 'application/json'
    }
    payload = {
        "userId": params['user_id'],
        "clientId": params['client_id'],
        "role": params['role'],
        "from_Date": params['from_date'],
        "to_Date": params['to_date'],
        "Return_Type": "Link"
    }
    response = requests.request("POST", url, headers=headers, json=payload)
    return response.json()

@api_error_handler
@observe(name="RTA_Statement")
def get_rta_statement(params:dict) -> dict:
    url = f"{BASE_URL_CONFIG}/getSOAMFLink"
    headers = {
        'sessionid': f"{params['session_id']}",
        'token': f"{params['token']}",
        'Content-Type': 'application/json'
    }
    payload = {
        "userId": params['user_id'],
        "clientId": params['client_id'],
        "role": params['role']
    }
    response = requests.request("POST", url, headers=headers, json=payload)
    return response.json()

@api_error_handler
@observe(name="Funds_Transfer_Status")
def get_fund_transfer_status(params:dict) -> dict:
    url = f"{BASE_URL_CONFIG}/FundsTransfer"
    headers = {
        'sessionid': f"{params['session_id']}",
        'token': f"{params['token']}",
        'Content-Type': 'application/json'
    }
    payload = {
        "userId": params['user_id'],
        "clientId": params['client_id'],
        "role": params['role']
    }
    response = requests.request("POST", url, headers=headers, json=payload)
    return response.json()

@api_error_handler
@observe(name="Funds_Transfer_Link")
def fund_transfer_link(params:dict) -> dict:
    url = f"{BASE_URL_CONFIG}/FundsTransferLink"
    headers = {
        'sessionid': f"{params['session_id']}",
        'token': f"{params['token']}",
        'Content-Type': 'application/json'
    }
    payload = {
        "userId": params['user_id'],
        "clientId": params['client_id'],
        "role": params['role'],
        "encclientCode":"",
        "encSessionNo": ""
    }
    response = requests.request("POST", url, headers=headers, json=payload)
    return response.json()

@api_error_handler
@observe(name="New_Account_Opening_Individual")
def get_new_account_opening_individual(params: dict) -> Dict:
    account_urls = {
        "ind_online": "https://www.motilaloswal.com/open-demat-account",
        "ind_physical_checklist": "https://ftp.motilaloswal.com/emailer/CSE/CHECKLIST_FOR_INDIVIDUAL_ACCOUNT.pdf",
        "ind_physical_form": "https://onlinetrade.motilaloswal.com/emailers/Customer_service/Form/Sample_fill_of_individual_form.pdf",
        "ind_physical_document": "https://onlinetrade.motilaloswal.com/emailers/Customer_service/Form/MO_KYC_punching.pdf",
        "huf_checklist": "https://onlinetrade.motilaloswal.com/emailers/Customer_service/Form/Checklist_for_HUF_account.pdf",
        "huf_sample": "https://onlinetrade.motilaloswal.com/emailers/Customer_service/Form/HUF_sample_form_version_5-1.pdf",
        "nri_checklist": "https://onlinetrade.motilaloswal.com/emailers/Customer_service/Form/Checklist_NRI.pdf",
        "nri_sample": "https://onlinetrade.motilaloswal.com/emailers/Customer_service/Form/NRI_sample_form.pdf",
        "partnership_checklist": "https://onlinetrade.motilaloswal.com/emailers/Customer_service/Form/Checklist_for_individual_account.pdf",
        "partnership_sample": "https://onlinetrade.motilaloswal.com/emailers/Customer_service/Form/Partnership_sample_form_version_5-1.pdf",
        "corporate_checklist": "https://onlinetrade.motilaloswal.com/emailers/Customer_service/Form/Checklist_for_corporate_account.pdf",
        "corporate_sample": "https://onlinetrade.motilaloswal.com/emailers/Customer_service/Form/Company_sample_form_version_5-1.pdf",
        "registered_trust_checklist": "https://onlinetrade.motilaloswal.com/emailers/Customer_service/Form/Checklist_for_registered_trust_account.pdf",
        "registered_trust_sample": "https://onlinetrade.motilaloswal.com/emailers/Customer_service/Form/Registered_society_sample_form_version_5-1.pdf",
        "non_registered_trust_checklist": "https://onlinetrade.motilaloswal.com/emailers/Customer_service/Form/Checklist_for_unregistered_trust_account.pdf",
        "non_registered_trust_sample": "https://onlinetrade.motilaloswal.com/emailers/Customer_service/Form/Unregistered_trust_sample_form_version_5-1.pdf",
        "reactivation_checklist": "https://onlinetrade.motilaloswal.com/emailers/Customer_service/Form/Checklist_for_individual_account.pdf",
        "reactivation_sample": "https://onlinetrade.motilaloswal.com/emailers/Customer_service/Form/Sample_fill_of_individual_form.pdf",
        "reactivation_dormant": "https://ftp.motilaloswal.com/emailer/CSE/Dormant%20physical.zip",
    }

    if params['account_type'] == 'new_form_request':
        return {
            "message": (
                "Dear Sir/Madam\nYou can punch New Form Request through\n"
                "Bizops > Request > Account Opening > Forms Request"
            )
        }

    url = account_urls.get(params['account_type'])
    if url:
        return {"message": url}
    else:
        return {"message": "Invalid account_type specified."}
    
@api_error_handler
@observe(name="Stop_Online_Trade")
def get_stop_online_trade(params:dict) -> dict:
    url = f"{BASE_URL_CONFIG}/Onlinetradestartstop"
    headers = {
        'sessionid': f"{params['session_id']}",
        'token': f"{params['token']}",
        'Content-Type': 'application/json'
    }
    payload = {
        "userId": params['user_id'],
        "clientId": params['client_id'],
        "role": params['role'],
        "Option": "1"
    }
    response = requests.request("POST", url, headers=headers, json=payload)
    return response.json()

@api_error_handler
@observe(name="Start_Online_Trade")
def get_start_online_trade(params:dict) -> dict:
    url = f"{BASE_URL_CONFIG}/Onlinetradestartstop"
    headers = {
        'sessionid': f"{params['session_id']}",
        'token': f"{params['token']}",
        'Content-Type': 'application/json'
    }
    payload = {
        "userId": params['user_id'],
        "clientId": params['client_id'],
        "role": params['role'],
        "Option": "2"
    }
    response = requests.request("POST", url, headers=headers, json=payload)
    return response.json()


@api_error_handler
@observe(name="Grandfather_PnL")
def get_grandfather_pnl(params:dict) -> dict:
    url = f"{BASE_URL_CONFIG}/GrandFatherGainLossDetailsReport"
    headers = {
        'sessionid': f"{params['session_id']}",
        'token': f"{params['token']}",
        'Content-Type': 'application/json'
    }
    payload = {
        "userId": params['user_id'],
        "clientId": params['client_id'],
        "role": params['role'],
        "from_Date": params['from_date'],
        "to_Date": params['to_date'],
        "return_Type": "Link"
    }
    response = requests.request("POST", url, headers=headers, json=payload)
    return response.json()


@api_error_handler
@observe(name="Account_Modification_Status_Online")
def get_account_modification_status_online(params:dict) -> dict:
    url = f"{BASE_URL_CONFIG}/AccountStatusReq"
    headers = {
        'sessionid': f"{params['session_id']}",
        'token': f"{params['token']}",
        'Content-Type': 'application/json'
    }
    payload = {
        "userId": params['user_id'],
        "clientId": params['client_id'],
        "role": params['role'],
        "PanOrNumber": ""
    }
    response = requests.request("POST", url, headers=headers, json=payload)
    return response.json()


@api_error_handler
@observe(name="Account_Modification_Status_Physical")
def get_account_modification_status_physical(params:dict = None) -> Dict:

    url = "https://www.motilaloswal.com/"
    data = {
            "message" : url
        }

    return data

@api_error_handler
@observe(name="Contract_Note")
def get_contract_note(params:dict) -> dict:
    url = f"{BASE_URL_CONFIG}/ContractNote"
    headers = {
        'sessionid': f"{params['session_id']}",
        'token': f"{params['token']}",
        'Content-Type': 'application/json'
    }
    payload = {
        "userId": params['user_id'],
        "clientId": params['client_id'],
        "role": params['role'],
        "from_Date": "",
        "to_Date": "",
        "return_Type":"link"
    }
    response = requests.request("POST", url, headers=headers, json=payload)
    return response.json()


@api_error_handler
@observe(name="Disbursement_DRF_Status")
def get_dis_drf_status(params:dict) -> dict:
    url = f"{BASE_URL_CONFIG}/DPRequestStatus"
    headers = {
        'sessionid': f"{params['session_id']}",
        'token': f"{params['token']}",
        'Content-Type': 'application/json'
    }
    payload = {
        "userId": params['user_id'],
        "clientId": params['client_id'],
        "role": params['role'],
        "requestType": params['request_type']
    }
    response = requests.request("POST", url, headers=headers, json=payload)
    return response.json()



@api_error_handler
@observe(name="Change_Advisor_Request")
def get_change_advisor_request(params:dict) -> dict:
    url = f"{BASE_URL_CONFIG}/StoreRMChangeRequest"
    headers = {
        'sessionid': f"{params['session_id']}",
        'token': f"{params['token']}",
        'Content-Type': 'application/json'
    }
    payload = {
        "userId": params['user_id'],
        "clientId": params['client_id'],
        "role": params['role'],
        "segment": params['segment'],
        "type": params['type'],
        "reason":params['reason']
    }
    response = requests.request("POST", url, headers=headers, json=payload)
    return response.json()

