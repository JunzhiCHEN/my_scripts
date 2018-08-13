#!/usr/bin/python
# -*- coding: UTF-8 -*-
import os
import json
import time
import uuid
import sys
import datetime as dt
from datetime import datetime
reload(sys)
sys.setdefaultencoding('utf-8')

from config_file import MYSQL_CONF_PATH, DB_STATUS, MD5_TOKEN, BELLE_HOST, FILE_HOST
os.environ['HILLINSIGHT_MYSQL_CONF'] = MYSQL_CONF_PATH
os.environ['SKY_SERVER_MYSQL_ENV'] = DB_STATUS
import hashlib
import requests
from db_conn import _mysql_config


db_hillapp = _mysql_config['hillapp']['slave']
def get_temp_light_app():
    sql = """
        select * from tmp_belle_light_app where status=1
    """

    result = db_hillapp.query(sql)
    app_list = []
    for one in result:
        app_info = {}
        app_info['light_app_id'] = one['app_id']
        app_info['light_app_name'] = one['name']
        app_info['bundle_id'] = 13
        if one['mob_logo']:
            app_info['avatar_path'] = FILE_HOST + one['mob_logo']
        elif one['pc_logo']:
            app_info['avatar_path'] = FILE_HOST + one['pc_logo']
        else:
            app_info['avatar_path'] = ""
        app_info['md5'] = generate_md5(app_info)
        app_list.append(app_info)
    return app_list

def generate_md5(dict_info):

    if not isinstance(dict_info, dict):
        return False
    d = sorted(dict_info.iteritems(), key=lambda k:k[0])
    md5_token = MD5_TOKEN
    for one in d:
        md5_token += str(one[1])

    md5 = hashlib.md5(md5_token.encode("utf-8")).hexdigest()
    return md5

def update_status(app_info):
    sql = "update tmp_belle_light_app set status=0 where status=1 and app_id=%d"  % app_info['light_app_id']
    result = db_hillapp.query(sql)
    return result

def bind_im(app_list):
    for one in app_list:
        print "-------------------bind im "
        print json.dumps(one)
        api_host = BELLE_HOST + '/api/im_service/light_app/add_light_app_bind'
        print "api: %s" % api_host
        response = requests.post(api_host, data=one)
        result = response.json()
        print "-------------------result"
        print result
        if result.get("error_code", -1) == 0:
            update_status(one)
        time.sleep(0.1)
    pass

if __name__ == '__main__':
    app_list= get_temp_light_app()
    bind_im(app_list)

    pass

