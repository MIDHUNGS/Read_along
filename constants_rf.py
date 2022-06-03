import os
from dotenv import load_dotenv

load_dotenv("/var/www/realtime-feedback/.env")

ENV_VAR = os.environ
# WORKING_DIR_CH = "/var/www/realtime-feedback"
WORKING_DIR_CH = "./"
#API_ENDPOINT = ENV_VAR.get("py_cm_api_endpoint")
API_ENDPOINT_MUMBAI = ENV_VAR.get("py_cm_api_endpoint_mumbai")
PAYLOAD = {
    "requester": ENV_VAR.get("py_cm_requester"),
    "requesterID": ENV_VAR.get("py_cm_requesterID"),
    "SecretKey": ENV_VAR.get("py_cm_SecretKey"),
    "userID": "NCK",
    "requesterInfo": "S2M",
    "requesterSeqNum": "12",
    "audiotype": "wav",
    "mode": "Adult,Child"
}

# REALTIME_RESULT_DIR = "/var/www/realtime-feedback/api_results"
REALTIME_RESULT_DIR = "./api_results"

# DB Constants
DATA_DBNAME = ENV_VAR.get("py_flive_dbname")
DATA_HOST = ENV_VAR.get("py_flive_host")
DATA_USER = ENV_VAR.get("py_flive_user")
DATA_PORT = ENV_VAR.get("py_flive_port")
DATA_DPASS = ENV_VAR.get("py_flive_dpass")
