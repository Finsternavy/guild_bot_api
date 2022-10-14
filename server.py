import json
from urllib import response
from flask import Flask, Response, abort, request
from config import database
from bson import ObjectId
from flask_cors import CORS, cross_origin
import os

app = Flask(__name__)
CORS(app)


@app.post("/api/update/members")
def update_members():
    try:
        member_list = request.get_json()
        # member_list = member_list[1:]
        # print(member_list)
        # print(member_list.type)
        # new_list = []
        # for i in range(len(member_list)):
        #     print(i)
        #     new_list.append(member_list[i])
            
            
        # print(new_list)
        
        # cursor = database.members.find({})
        # members = []
        # if cursor:
        #     for member in cursor: 
        #         members.append(member)
        # # remove members who are no longer a part of the guild
        # if members:
        #     for member in members:
        #         if not member['username'] in member_list:
        #             database.members.find_one_and_delete({"username": member['username']})

        # for i in len(member_list):
        #     found = False
        #     for y in members:
        #         if y['username'] == member_list[i]:
        #             new_list.remove(i, 1)
                
        # new_members_list = jsonify(members)
        # database.members.drop()
        
        # new_members = [*set(members)]
        
        
        for member in member_list:
            database.members.insert_one(member)
            print(member)
            
        print(member_list)
            
        return json.dumps("Complete")
    except Exception as e:
        print(e)

app.run(debug=True)