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
        db_members = database.members.find({})
        print("Current members list:")
        
        current_db_usernames = []
        current_users = []
        
        #build list of username currently in the database
        if db_members:
            for member in db_members:
                current_db_usernames.append(member['username'])
                print(member['username'])
                
        # build a list of usernames from the current members list received from discord       
        for member in member_list:
            current_users.append(member['username'])
        
        for member in current_db_usernames:
            if member not in current_users:
                database.members.find_one_and_delete({'username' : str(member)})
                
        
        # add new member if not present in the list
        for member in member_list:
            if member['username'] != 'None':
                if member['username'] not in current_db_usernames:
                    # member['_id'] = str(member['_id'])
                    database.members.insert_one(member)
                    print(member)
            
        print(member_list)
            
        return json.dumps("Complete")
    except Exception as e:
        print(e)
        
        
@app.post("/api/update/member")
def update_member():
    
    classes = ['fighter', 'tank', 'rogue', 'ranger', 'mage', 'summoner', 'cleric', 'bard']
    subclasses = ['weapon master', 'dreadnought', 'shadowblade', 'hunter', 'spellsword', 'bladecaller', 'highsword', 'bladedancer',
        'knight', 'guardian', 'nightshield', 'warden', 'spellshield', 'keeper', 'paladin', 'argent',
        'duelist', 'shadow guardian', 'assassin', 'predator', 'nightspell', 'shadow lord', 'cultist', 'charlatan',
        'strider', 'sentinel', 'scout', 'hawkeye', 'scion', 'falconer', 'soulbow', 'bowsinger',
        'battle mage', 'spellstone', 'shadow caster', 'spellhunter', 'archwizard', 'warlock', 'acolyte', 'sorcerer',
        'wild blade', 'brood warden', 'shadowmancer', 'beastmaster', 'spellmancer', 'conjurer', 'necromancer', 'enchanter',
        'templar', 'apostle', 'shadow disciple', 'protector', 'oracle', 'shaman', 'high priest', 'scryer',
        'tellsword', 'siren', 'trickster', 'song warden', 'magician', 'songcaller', 'soul weaver', 'minstrel']
    
    index = 0
    use_index = 0

    try:
        user_data = request.get_json()
        
        if str(user_data['class']).lower() not in subclasses:
            return json.dumps("Class not found. Please check your spelling and try again.")
        
        user_from_db = database.members.find_one({"username" : str(user_data['username'])})
        
        for subclass in subclasses:
            if subclass.lower() == str(user_data['class']).lower():
                use_index = index
                break
            else:
                index += 1
        print(use_index)
        
        augment_index = int(use_index % 8)
        primary_index = int((use_index - augment_index) / 8)
        
        return_data = ''
        # set the users class, primary and augment data
        if user_from_db:
            updated_user = database.members.find_one_and_update({'username' : user_data['username']}, {'$set': {'class': str(user_data['class']), 'primary': str(classes[int(primary_index)]), 'augment': str(classes[int(augment_index)])}})
            
            # format data to be returned to discord
            return_data = str(updated_user['username'] + ':  Class: ' + str(updated_user['class']).upper() + ' Primary: ' + str(updated_user['primary']).upper() + ' Augment: ' + str(updated_user['augment']).upper())
        
        return json.dumps('Success! Your class has been updated.')
        
    except Exception as e:
        print(e)

app.run(debug=True)