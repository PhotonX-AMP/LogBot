from flask import  request,  Response, abort
from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
# project resources
from models.users import Users
from models.document import LogFile
from models.chat_history import Chat_History
import json
from utils.errors import user_not_found, resource_already_exists


class GenSumm(Resource):
    @staticmethod
    @jwt_required()
    def post() -> Response:
        
        authorized: bool = Users.objects.get(id=get_jwt_identity())
        if authorized:
            user_details= json.loads(Users.objects.get(id=get_jwt_identity()).to_json())

            print(user_details['user_id'])
            if not request.json:
                abort(415)
            data = request.get_json()
            doc_details = json.loads(LogFile.objects.get(document_id=data.get('document_id')).to_json())
            print(data["summarygen"])
            if data["summarygen"] == "True":
                LogFile.objects(document_id=data.get('document_id')).update_one(set__document_summary="new summary generated")
                data_load_chat = {"user_id": [], "chat_id":[],"query":[],"response":[], 'document_id' : []}
                data_load_chat['user_id'] = user_details['user_id']
                data_load_chat['chat_id']= doc_details['chat_id']
                data_load_chat['query'] = "generate summary"
                data_load_chat['response'] = 'Successfully generated summary for the file'
                data_load_chat['document_id'] = doc_details['document_id']
                chat_load = Chat_History(**data_load_chat)
                chat_load.save()
            query = []
            response = []
            timestamp_sort = []
            for chat in Chat_History.objects(user_id = user_details['user_id']):
                chat_details = (json.loads((chat).to_json()))
                query.append(chat_details['query'])
                response.append( chat_details['response'])
                timestamp_sort.append( chat_details['timestamp'])
            doc_name = []
            doc_summary = []
            doc_tag = []
            doc_timestamp = []
            for doc in LogFile.objects(user_id = user_details['user_id']):
                doc_details = (json.loads((doc).to_json()))
                doc_name.append(doc_details['document_name'])
                doc_summary.append(doc_details['document_summary'])
                doc_tag.append(doc_details['document_tag'])
                doc_timestamp.append(doc_details['timestamp'])
            session_response = { 
                                    'chathistory': {'query':query,
                                'response':response,
                                'timestamp' :timestamp_sort
                    },
                'docdetails':{
                    'document_id': doc_details['document_id'],
                    'document_name': doc_details['document_name'],
                    'doc_summaries': doc_details['document_summary'],
                    'doc_tag': doc_details['document_tag'],
                    'doc_timestamp' : doc_details['timestamp'] }
                } 
        return Response(json.dumps(session_response), 200)
    