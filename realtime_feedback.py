from distutils.log import debug
import uuid
import json
from scipy.io import wavfile
from pathlib import Path
import datetime
from flask import send_file
from flask import Flask, render_template, request
from flask_cors import CORS, cross_origin

import constants_rf as cns
import utility_func_rf as utils
import cm_processing as cmp


app = Flask(__name__)
CORS(app, support_credentials=True)

@app.route('/', methods=['POST', 'GET'])
def index():
    
    global session_id
    session_id = str(uuid.uuid4())
    return render_template('index.html')

@app.route('/epub-read.html', methods=['POST', 'GET'])
def epub_read():
    print('(.)(.)')
    global session_id
    session_id = str(uuid.uuid4())
    return render_template('epub-read.html')

# @app.route('/save_audio/<filename>', methods = ['POST'])
# def api_saveaudio(filename):
#     cur_ts = round(datetime.datetime.now().timestamp())
#     # cur_ts = utils.get_timestamp(curtime)
#     filepath = '{}/audio_rec/{}_{}.wav'.format(cns.WORKING_DIR_CH, filename, cur_ts)
#     print(filepath)
#     f = open(filepath, 'wb')
#     f.write(request.data)
#     f.close()
#     return filepath


@app.route('/audio/All_About_Eggs/<filename>', methods = ['GET'])
def get_text3(filename):
    
    current_path: Path = Path(__file__).parent.resolve()
    filepath = str(current_path) + '\\static\\audio\\'+filename
    f = open(filepath, 'r')
    ff=f.read()
    return ff

@app.route('/audio/<bookname>/Text/<filename>', methods = ['GET'])
def get_textw(bookname,filename):
    
    current_path: Path = Path(__file__).parent.resolve()
    filepath = str(current_path) + '\\static\\audio\\'+bookname+'\\Text\\'+filename
    print(filepath)
    f = open(filepath, 'r')
    ff=f.read()
    return ff

@app.route('/audio/<bookname>/Test/<filename>', methods = ['GET'])
def get_audioc(bookname,filename):
    
    current_path: Path = Path(__file__).parent.resolve()
    filepath = '\\static\\audio\\'+bookname+'\\'+filename
    return filepath


# @app.route('/audio/All_About_Eggs/hello2.txt', methods = ['GET'])
# def get_text():
#     print('8888888888888888888888888888888888888888888')
#     current_path: Path = Path(__file__).parent.resolve()
#     filepath = str(current_path) + '\\static\\audio\\hello2.txt'
#     f = open(filepath, 'r')
#     ff=f.read()
#     return ff

@app.route('/audio/All_About_Eggs/hello.txt', methods = ['GET'])
def get_textt():
    
    current_path: Path = Path(__file__).parent.resolve()
    filepath = str(current_path) + '\\static\\audio\\hello.txt'
    f = open(filepath, 'r')
    ff=f.read()
    return ff


@app.route('/audio/All_About_Eggs/sentence2.wav', methods = ['GET'])
def get_audio():
    
    current_path: Path = Path(__file__).parent.resolve()
    filepath = str(current_path) + '\\audio\\All_About_Eggs\\sentence2.wav'
    path_to_file = filepath

    return send_file(
         path_to_file, 
         mimetype="audio/wav", 
         as_attachment=True, 
         download_name="sentence2.wav")



@app.route("/hello")
def hello():
    return "Hello, Welcome to GeeksForGeeks"

@app.route('/reading_fluency', methods = ['POST'])
def reading_fluency():
    request_data = request.get_json()
    try:
        audio_path = request_data['audio_path']
        target_phrase = request_data['target_phrase']
        process_id = request_data['process_id']
        session_id = request_data['session_id']
        grade = request_data['grade']
    except Exception as ex:
        error_metrics, status_code = invalid_input(request_data, ex)
        return {'data': error_metrics}, status_code

    try:
        q_ins_user = "insert into cm_passage_reading_input (session_id, process_id, " \
                     "target_phrase, audio_path, status, grade) values ('{}', '{}', '{}', " \
                     "'{}', '{}', '{}') returning id"
        q_ins_user = q_ins_user.format(session_id, process_id, target_phrase, audio_path,
                                       "Processing", grade)
        input_id = utils.insert_update_query(q_ins_user, return_id=True)[0][0]
        cm_api_called = False
        response_link = cmp.get_fluency_analysis_link(ref_text=target_phrase)
        cm_api_called = response_link["cm_api_called"]
        if "ErrorMessage" in response_link:
            raise Exception(response_link["ErrorMessage"])
        api_result = cmp.get_fluency_analysis_result(file=audio_path,
                                                     response_link=response_link["request_link"])
        metrics = cmp.extract_metrics_from_xml_fluency(result_data=api_result)
        cmp.check_audio_quality(result_dict=metrics.copy())
        metrics["process_id"] = process_id
        metrics["session_id"] = process_id
        metrics["wg_id"] = str(metrics["id"])

        metrics["status"] = "Processed"
        req_keys = ["session_id", "process_id", "marked_text", "status"]
        result_metrics = {key: metrics[key] for key in req_keys}
        result_metrics["noise"] = metrics["bgpow"]

        q_up_status = "update cm_passage_reading_input set status = 'Processed', " \
                      "cm_api_called = '{}' where id = {}"
        utils.insert_update_query(q_up_status.format(cm_api_called, input_id))
        insert_metrics_data(metrics, audio_path, grade, input_id)
        status_code = 200
    except Exception as ex:
        q_up_status = "update cm_passage_reading_input set status = 'Failed', " \
                      "cm_api_called = '{}' where id = {}"
        utils.insert_update_query(q_up_status.format(cm_api_called, input_id))
        error_type = ["'nonetype' has no object attribute 'text'", "'nonetype' object has no attribute 'text'"]
        if ex.__str__().lower() in error_type:
            exception_message = "No audio detected"
        else:
            exception_message = ex.__str__()
        result_metrics = {"status": "Error",
                          "ExceptionType": type(ex).__name__,
                          "ExceptionMessage": exception_message}
        status_code = 500
    return {'data': result_metrics}, status_code

def invalid_input(request_data, ex):
    if request_data is None:
        parameter_name = "audio_path"
    else:
        parameter_name = ex.__str__()
    exception_message = "You're missing one of mandatory parameter. " \
                        "Parameter Name: {}".format(parameter_name)
    error_metrics = {"Status": "Error",
                     "ExceptionType": "InvalidInput",
                     "ExceptionMessage": exception_message}
    status_code = 400
    return error_metrics, status_code

def insert_metrics_data(result_metrics, audio_path, grade, input_id):
    if result_metrics["status"] == "Processed":
        q_ins_metrics = "insert into cm_passage_reading_metrics (cm_pr_input_id, session_id, " \
                        "process_id, wg_id, target_phrase, audio_file, marked_text, " \
                        "score, audio_quality_vol, audio_quality_status, noise, " \
                        "identified_speaker, grade) values ({}, '{}', '{}', '{}', " \
                        "'{}', '{}', '{}', {}, {}, {}, {}, '{}', '{}')"
        q_ins_metrics = q_ins_metrics.format(input_id, result_metrics["session_id"], result_metrics["process_id"],
                                       result_metrics["wg_id"], result_metrics["target_phrase"],
                                       audio_path, result_metrics["marked_text"],
                                       result_metrics["score"], result_metrics["audio_quality_vol"],
                                       result_metrics["audio_status"], result_metrics["bgpow"],
                                       result_metrics["identified_speaker"], grade)
        res = utils.insert_update_query(q_ins_metrics)
    else:
        res = None
    return res

if __name__ == "__main__":
    app.run(host='0.0.0.0')
