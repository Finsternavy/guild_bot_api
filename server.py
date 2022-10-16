import json
from urllib import response
from flask import Flask, Response, abort, request
from config import database
from bson import ObjectId
from flask_cors import CORS, cross_origin
import os

app = Flask(__name__)
CORS(app)

def update_guild_stats():
    cursor = database.members.find({})
            
    guild_class_stats = {
        'title': 'guild_stats',
        'tanks': [],
        'healers': [],
        'DPS/Support': [],
        'true_tanks': 0,
        'primary_tanks': 0,
        'augmented_tanks': 0,
        'true_healers': 0,
        'primary_healers': 0,
        'augmented_healers': 0,
        'true_dps_support': 0,
        'primary_dps_support': 0,
        'augmented_dps_support': 0,
        'total_registered_forces': 0
    }


    for member in cursor:
        print(member)
        print("line 78")
        name_and_class = str(member['username']) + ' : ' + str(member['class'])
        
        
        # Compile stats based on current members of the guilds class and augments
        if str(member['primary_role']) == str(member['secondary_role']):
            if str(member['primary_role']) == 'tank':
                guild_class_stats['tanks'].append(name_and_class + ' (True Tank)')
                guild_class_stats['true_tanks'] += 1
                
            elif str(member['primary_role']) == 'healer':
                guild_class_stats['healers'].append(name_and_class + ' (True Healer)')
                guild_class_stats['true_healers'] += 1
                
            else:
                guild_class_stats['DPS/Support'].append(name_and_class + ' (True DPS / Support)')
                guild_class_stats['true_dps_support'] += 1
        
        else:
            if str(member['primary_role']) == 'tank':
                guild_class_stats['tanks'].append(name_and_class + ' (Primary Tank)')
                guild_class_stats['primary_tanks'] += 1
                
                if str(member['secondary_role']) == 'healer':
                    guild_class_stats['healers'].append(name_and_class + ' (Augmented Healer)')
                    guild_class_stats['augmented_healers'] += 1
                else:
                    guild_class_stats['DPS/Support'].append(name_and_class + ' (Primary DPS/Support)')
                    guild_class_stats['primary_dps_support'] += 1
                
            elif str(member['primary_role']) == 'healer':
                guild_class_stats['healers'].append(name_and_class + ' (Primary Healer)')
                guild_class_stats['primary_healers'] += 1
                
                if str(member['secondary_role']) == 'tank':
                    guild_class_stats['tanks'].append(name_and_class + ' (Augmented Tank)')
                    guild_class_stats['augmented_tanks'] += 1
                else:
                    guild_class_stats['DPS/Support'].append(name_and_class + ' (Primary DPS/Support)')
                    guild_class_stats['primary_dps_support'] += 1
                
            elif str(member['primary_role']) == 'DPS/Support':
                guild_class_stats['DPS/Support'].append(name_and_class + ' (Primary DPS/Support)')
                guild_class_stats['primary_dps_support'] += 1
                
                if str(member['secondary_role']) == 'tank':
                    guild_class_stats['DPS/Support'].append(name_and_class + ' (Augmented Tank')
                    guild_class_stats['augmented_tanks'] += 1
                    
                else:
                    guild_class_stats['healers'].append(name_and_class + ' (Augmented Healer)')
                    guild_class_stats['augmented_healers'] += 1
                                
                                
        guild_class_stats['total_registered_forces'] += 1
        
        # update database
        old_stats = database.guild_stats.find_one({'title': 'guild_stats'})
        
        if not old_stats:
            database.guild_stats.insert_one(guild_class_stats)
        else:
            database.guild_stats.find_one_and_replace({'title': 'guild_stats'}, guild_class_stats)


@app.post("/api/update/members")
def update_members():
    
    member_list = request.get_json()
    
    if member_list:
        print(member_list)
        
        try:
            cursor = database.members.find({})
            print("Current members list:")
            
            current_db_usernames = []
            current_users = []
            
            #build list of username currently in the database
            if cursor:
                print("building database member list...")
                for member in cursor:
                    current_db_usernames.append(str(member['username']).lower())
                    print('line 33:')
                    print(member['username'])
                    
            print('building member list...')
            # build a list of usernames from the current members list received from discord
            for member in member_list:
                current_users.append(str(member['username']).lower())
            
            # delete old members that are no longer in the guild
            if current_db_usernames:
                for member in current_db_usernames:
                    if str(member) not in current_users:
                        database.members.find_one_and_delete({'username' : str(member)})
                    
            # add new member if not present in the list
            for member in member_list:
                if str(member['username']) not in current_db_usernames:
                    database.members.insert_one(member)
                    print(member)
                
            print(member_list)
            
            update_guild_stats()
                
            return json.dumps("Updates completed")
        
        except Exception as e:
            print(e)
            
    return json.dumps("Member data did not load properly.  Did you trying turning if off and back on again?")


        
@app.get("/api/guild/class-breakdown")
def get_guild_class_breakdown():
    
    cursor = database.guild_stats.find({})
    guild_stats = {}
    
    # get the current guild stats and adjust the ID for passing via json
    for stats in cursor:
        stats['_id'] = str(stats['_id'])
        guild_stats = stats

    return json.dumps(guild_stats)
    


@app.get("/api/guild/tanks")
def get_tanks():
    
    cursor = database.guild_stats.find({})
    
    tanks = {}
    
    for stats in cursor:
        stats['_id'] = str(stats['_id'])
        tanks = stats['tanks']
    
    return json.dumps(tanks)


        
@app.post("/api/set-user-class")
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
            primary = str(classes[int(primary_index)])
            augment = str(classes[int(augment_index)])
            primary_role = ''
            secondary_role = ''
            if primary == 'tank':
                primary_role = 'tank'
            elif primary == 'cleric':
                primary_role = 'healer'
            else:
                primary_role = 'DPS/Support'
            
            if augment == 'tank':
                secondary_role = 'tank'
            elif augment == 'cleric':
                secondary_role = 'healer'
            else:
                secondary_role = 'DPS/Support'
                
            updated_user = database.members.find_one_and_update({'username' : user_data['username']}, {'$set': {'class': str(user_data['class']), 'primary': str(primary), 'augment': str(augment), 'primary_role': str(primary_role), 'secondary_role': str(secondary_role)}})
            
            print(updated_user['primary_role'])
            
            # format data to be returned to discord for testing purposes
            return_data = 'Success! Your class has been updated to ' + str(user_data['class']).upper() + '.'
        
        update_guild_stats()
        
        return json.dumps(return_data)
        
    except Exception as e:
        print(e)
        
@app.get('/api/get-user-class/<username>')
def get_user_class(username):
    
    user = database.members.find_one({'username': str(username)})
    
    response_string = ''
    
    if not user:
        response_string = "That user does not exist.  Please check the spelling and try again."
        return json.dumps(response_string)
        
    if user['class']:
        response_string = user['username'] + " - Class: " + str(user['class']).upper() + " (Primary: " + str(user['primary']).upper() + ', Augment: ' + str(user['augment']).upper() + ')'
        return json.dumps(response_string)
    
    else:
        username = str(user['username'])
        response_string = username + " has not set a class yet."
        return json.dumps(response_string)
    

@app.post('/api/clear-user-class/<username>')
def clear_user_class(username):
    
    user = database.members.find_one({'username': str(username)})
    
    if not user:
        response_string = 'User does not exist.  Please check the spelling and try again.'
        
    if user['class']:
        user['class'] = ''
        user['primary'] = ''
        user['augment'] = ''
        database.members.find_one_and_update({'username': str(username)}, {'$set': {'class': '', 'primary': '', 'augment': ''}})
        response_string = 'Class cleared successfully!'
        return json.dumps(response_string)

app.run(debug=True)