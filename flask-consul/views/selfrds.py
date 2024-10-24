import os
from flask import Blueprint
from flask_restful import reqparse, Resource, Api
import sys,traceback
sys.path.append("..")
from units import token_auth,selfrds_manager
from werkzeug.datastructures import FileStorage
from units import upload
from units.config_log import *
blueprint = Blueprint('selfrds',__name__)
api = Api(blueprint)

parser = reqparse.RequestParser()
parser.add_argument('vendor',type=str)
parser.add_argument('account',type=str)
parser.add_argument('region',type=str)
parser.add_argument('group',type=str)
parser.add_argument('name',type=str)
parser.add_argument('ip',type=str)
parser.add_argument('port',type=str)
parser.add_argument('os',type=str)
parser.add_argument('del_dict',type=dict)
parser.add_argument('up_dict',type=dict)
parser.add_argument('file',type=FileStorage, location="files", help="File is wrong.")

class Upload(Resource):
    @token_auth.auth.login_required
    def post(self):
        file = parser.parse_args().get("file")
        try:
            filename = file.filename
            file_extension = os.path.splitext(filename)[1].lower()
            try:
                file_data = file.read()
                if file_extension == '.xlsx':
                    return upload.read_execl(file_data,'selfrds')
                elif file_extension == '.csv':
                    return upload.read_csv(file_data,'selfrds')
            except Exception as e:
                logger.error(f"【selfrds】文件后缀名错误，请导入xlsx或csv格式,{e}\n{traceback.format_exc()}")
                return {"code": 50000, "data": f"文件后缀名错误，请导入xlsx或csv格式！"}
        except Exception as e:
            logger.error(f"【selfrds】导入失败,{e}\n{traceback.format_exc()}")
            return {"code": 50000, "data": f"导入失败！"}

class GetAllList(Resource):
    @token_auth.auth.login_required
    def get(self):
        args = parser.parse_args()
        return selfrds_manager.get_all_list(args['vendor'],args['account'],args['region'],args['group'])

class SelfrdsApi(Resource):
    decorators = [token_auth.auth.login_required]
    def get(self):
        return selfrds_manager.get_service()
    def post(self):
        args = parser.parse_args()
        logger.info(f'=======\n{args}')
        return selfrds_manager.add_service(args['vendor'],args['account'],args['region'],
                                            args['group'],args['name'],args['ip'],args['port'],args['os'])
    def put(self):
        args = parser.parse_args()
        del_dict = args['del_dict']
        up_dict = args['up_dict']
        resp_del = selfrds_manager.del_service(del_dict['vendor'],del_dict['account'],
                                                del_dict['region'],del_dict['group'],del_dict['name'])
        resp_add = selfrds_manager.add_service(up_dict['vendor'],up_dict['account'],up_dict['region'],
                                                up_dict['group'],up_dict['name'],up_dict['ip'],
                                                up_dict['port'],up_dict['os'])
        if resp_del["code"] == 20000 and resp_add["code"] == 20000:
            return {"code": 20000, "data": f"更新成功！"}
        else:
            return {"code": 50000, "data": f"更新失败！"}
    def delete(self):
        args = parser.parse_args()
        return selfrds_manager.del_service(args['vendor'],args['account'],args['region'],args['group'],args['name'])

api.add_resource(GetAllList,'/api/selfrds/alllist')
api.add_resource(SelfrdsApi, '/api/selfrds/service')
api.add_resource(Upload,'/api/selfrds/upload')
