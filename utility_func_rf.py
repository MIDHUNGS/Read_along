import requests
import time
import datetime

import psycopg2

import constants_rf as cns


def convert_to_time(n): 
    return time.strftime("%M:%S", time.gmtime(n))


def carnegie_api_result(file, request_xml, url=cns.API_ENDPOINT_MUMBAI, payload=cns.PAYLOAD):
    payload["aaxml"] = request_xml
    response_url = requests.request("POST", url, data=payload)
    if response_url.status_code != 200:
        raise Exception("post request for url has response code: {}". \
                        format(response_url.status_code))
    requested_url = response_url.text 
    files = [("file", open(file, "rb"))]
    response_audio = requests.request("POST", requested_url, files=files)
    if response_audio.status_code != 200:
        raise Exception("post request for Audio processing has response code: {}" \
                        .format(response_audio.status_code))
    return response_audio.text


def carnegie_api_analysis_link(request_xml, url=cns.API_ENDPOINT_MUMBAI, payload=cns.PAYLOAD):
    payload["aaxml"] = request_xml
    response_url = requests.request("POST", url, data=payload)
    if response_url.status_code != 200:
        raise Exception("post request for url has response code: {}". \
                        format(response_url.status_code))
    requested_url = response_url.text
    return requested_url


def carnegie_api_analysis_result(file, url):
    files = [("file", open(file, "rb"))]
    response_audio = requests.request("POST", url, files=files)
    if response_audio.status_code != 200:
        raise Exception("post request for Audio processing has response code: {}" \
                        .format(response_audio.status_code))
    return response_audio.text


def create_conn(db_name, host, user, passwd, port):
    """
    Creates a connection pool for given postgres database with atleast one
    minimum connection.

    Parameters
    ----------
    db_name : str
        Database name to be connected
    host : str
        Host name where database is hosted
    user : str
        User name of the postgres database to be connected.
    passwd : str
        Password for user of the database
    port : int
        Port

    Returns
    -------
    psycopg2.extensions.connection
        Postgres connection.
    """
    try:
        conn = psycopg2.connect(database=db_name, host=host, port=port,
                                user=user, password=passwd)
        return conn
    except Exception as ex:
        return ["error", ex.__str__()]


def close_conn(conn):
    """
    Closes postgres connection.

    Parameters
    ----------
    conn : psycopg2.extensions.connection type
        Connection to be closed

    Returns
    -------
    None
        returns None if connection is closed. If some error comes, return that error.
    """
    try:
        res = conn.close()
        return res
    except Exception as ex:
        return ["error", ex.__str__()]


def insert_many(query_arg, params, conn=None, to_close=True):
    """
    Runs insert operation for given query.

    Parameters
    ----------
    query_arg : str
        Insert query to be executed.
    params : list type
        Other query parameters such as list of values to be inserted.
    conn : psycopg2.extensions.connection type, default None
        postgres connection of database on which insert query is to be executed
    to_close : bool, default true
        existing postgres connection to be closed or not.

    Returns
    -------
    None
        returns None if query executed without any error else error is retuned.
    """
    res = None
    try:
        if conn is None:
            conn = create_conn(cns.DATA_DBNAME, cns.DATA_HOST, cns.DATA_USER,
                               cns.DATA_DPASS, cns.DATA_PORT)
        cur = conn.cursor()
        res = cur.executemany(query_arg, params)
        conn.commit()
        cur.close()
        if to_close:
            close_conn(conn)
        return res
    except Exception as ex:
        print("error while inserting data")
        print(type(ex).__name__)
        return ex.__str__()


def run_select(query, conn=None, to_close=True):
    """
    Runs select operation for given query.

    Parameters
    ----------
    query : str
        Select query to be executed.
    db_type : str
        Postgres database on which the query is to be executed.
    try_count : int
        Number of times to try in case any error occured.

    Returns
    -------
    tuples
        returns select query data in tuples if query executed successfully
        else error is retuned.
    """
    try:
        if conn is None:
            conn = create_conn(cns.DATA_DBNAME, cns.DATA_HOST, cns.DATA_USER,
                               cns.DATA_DPASS, cns.DATA_PORT)
        cur = conn.cursor()
        cur.execute(query)
        q_data = cur.fetchall()
        cur.close()
        if to_close:
            close_conn(conn)
        return q_data
    except Exception as ex:
        return ex.__str__()


def insert_update_query(query, params=None, return_id=False):
    conn = create_conn(cns.DATA_DBNAME, cns.DATA_HOST, cns.DATA_USER,
                       cns.DATA_DPASS, cns.DATA_PORT)
    cur = conn.cursor()
    res = cur.execute(query, params)
    conn.commit()
    if return_id:
        res = cur.fetchall()
    cur.close()
    conn.close()
    return res


def get_timestamp(utc_date):
    DAY = 24*60*60
    timestamp = (utc_date.toordinal() - datetime.date(1970, 1, 1).toordinal()) * DAY
    timestamp = (utc_date - datetime.date(1970, 1, 1)).days * DAY
    return timestamp
