import uuid

from bs4 import BeautifulSoup

import utility_func_rf as utils
import constants_rf as cns


def get_fluency_analysis_link(ref_text, payload=cns.PAYLOAD):
    request_xml = '<AARequest AAReqID="{}">' \
                      '<analysis analysisType="ReadingFluency" pinpoint="TRUE">' \
                          '<text>{}</text>' \
                      '</analysis>' \
                  '</AARequest>'
    request_xml = request_xml.format(ref_text, ref_text)
    try:
        request_link = utils.carnegie_api_analysis_link(request_xml, url=cns.API_ENDPOINT_MUMBAI,
                                                        payload=payload)
        data = {"request_link": request_link, "cm_api_called": True}
    except Exception as ex:
        request_link = None
        error = ex.__str__()
        data = {"request_link": request_link, "cm_api_called": "Error", "ErrorMessage": error}
    return data


def get_fluency_analysis_result(file, response_link, payload=cns.PAYLOAD):
    try:
        result_xml = utils.carnegie_api_analysis_result(file, response_link)
        idd = uuid.uuid4()
        file_name = "{}/word_game_rf_{}.txt".format(cns.REALTIME_RESULT_DIR, idd)
        with open(file_name, "w") as outfile:
            outfile.write(result_xml)
            outfile.close()
        data = {"id": idd, "xml_result": result_xml}
    except Exception as ex:
        result_xml = None
        error = ex.__str__()
        data = {"xml_result": result_xml, "ErrorMessage": error}
    return data


def extract_metrics_from_xml_fluency(result_data):
    if result_data["xml_result"] is None:
        if "ErrorMessage" in result_data:
            raise Exception(result_data["ErrorMessage"])
        else:
            raise Exception("Invalid xml data provided")
    response_xml = BeautifulSoup(result_data["xml_result"], "xml")
    row = {}
    row["id"] = result_data["id"]
    row["identified_speaker"] = response_xml.find("validate").get("SelectedAAModelName")
    row["score"] = float(response_xml.find("score").text)
    row["target_phrase"] = response_xml.find("targetText").text
    marked_text = str(response_xml.find("markedText"))
    marked_text = marked_text.replace('<markedText>', '<p style="font-size: 24px">')
    marked_text = marked_text.replace('<font', '<span')
    marked_text = marked_text.replace('</font>', '</span>')
    marked_text = marked_text.replace(' style="background-color:yellow"', '')
    row["marked_text"] = marked_text
    audio_qual_ele = response_xml.find("audioQuality")
    row["audio_status"] = float(audio_qual_ele.get("status"))
    row["audio_quality_vol"] = float(audio_qual_ele.get("vol"))
    row["bgpow"] = float(audio_qual_ele.find("comment").get("bgpow"))
    return row


def check_audio_quality(result_dict):
    if result_dict["audio_quality_vol"] < 0.15:
        raise Exception("Audio volume is too low. Please provide an audio with higher volume.")
#    elif result_dict["audio_quality_vol"] > 1:
#        raise Exception("Audio volume is too high. Please provide an audio with lower volume.")
    else:
        None

    if result_dict["bgpow"] > 40:
        raise Exception("There is lot of background noise. Please try again.")
    return None
