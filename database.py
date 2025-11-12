import mysql.connector
from secret import db_details
from flask import render_template
db = mysql.connector.connect(**db_details)

cursor=db.cursor()

#Creates New User account
def create_account(email, acc_type,username, password,approval):
    try:
        cursor.execute(f'SELECT * FROM user_accounts WHERE email = \'{str(email)}\'')
        existing_user = cursor.fetchone()
        if existing_user:
            already_taken="true"
            return already_taken
        else:
            cursor.execute(f'Insert into user_accounts (email, acc_type, username, password, approval) values(\'{str(email)}\', \'{str(acc_type)}\', \'{str(username)}\', \'{str(password)}\', \'{str(approval)}\')')
            db.commit()
    except mysql.connector.Error as e:
        print("Failed to complete Database Operation {}".format(e))
        return "Database Operation failed...Try later"    
 
#Checks if a user acccount with a given username exists already
def check_account(uname):
    try:          
        user_details=[]
        cursor.execute(f'SELECT email, acc_type, username, password FROM user_accounts WHERE username= %s', (uname,))
        user_details = cursor.fetchone()
        return user_details
    except mysql.connector.Error as e:
        print("Failed to complete Database Operation {}".format(e))
        return "Database Operation failed...Try later"     



#Checks if the user's password is correct
def check_password(uname,password):
    try:
        check_password=[]
        cursor.execute(f'SELECT password FROM user_accounts WHERE username= %s', (uname,))
        check_password_tuple = cursor.fetchone()
        check_password=check_password_tuple[0]
        if password==check_password:
            return check_password
    except mysql.connector.Error as e:
        print("Failed to complete Database Operation {}".format(e))
        return "Database Operation failed...Try later" 
    
#Returns the user's account type
def check_usertype(username):
    try:
        cursor.execute(f'SELECT acc_type FROM user_accounts WHERE username= %s', (username,))
        usertype = cursor.fetchone()
        return usertype
    except mysql.connector.Error as e:
        print("Failed to complete Database Operation {}".format(e))
        return "Database Operation failed...Try later"    

#Used to check if an event has been cancelled 
def check_active(event):
    try:
        cursor.execute(f'SELECT cancelled FROM events WHERE cancelled= %s', (event,))
        usertype = cursor.fetchone()
        return usertype
    except mysql.connector.Error as e:
        print("Failed to complete Database Operation {}".format(e))
        return "Database Operation failed...Try later"     

#Used to check if a team is active 
def team_active(team_id):
    try:
        cursor.execute(f'SELECT active FROM team_event WHERE team_id = %s', (team_id,))
        active= cursor.fetchone()
        return active
    except mysql.connector.Error as e:
        print("Failed to complete Database Operation {}".format(e))
        return "Database Operation failed...Try later" 

#Returns the teams registered for a given event 
def check_teams(event_id):
    try:
        cursor.execute(f'SELECT team_id FROM team_event WHERE event_id= %s', (event_id,))
        teams = cursor.fetchall()
        return teams
    except mysql.connector.Error as e:
        print("Failed to complete Database Operation {}".format(e))
        return "Database Operation failed...Try later" 

#Updates the event details         
def edit_info(event_id, event_name, sport, venue, date,  max_players, price_per_player, additional):
    try:
        formatted_date = date.split()[0]
        cursor.execute('''
        UPDATE events 
        SET 
            event_name = %s, 
            sport = %s, 
            venue = %s, 
            date = %s, 
            max_players = %s, 
            price_per_player = %s, 
            additional = %s 
        WHERE 
            event_id = %s
    ''', (event_name, sport, venue, formatted_date, max_players, price_per_player, additional, event_id))
    except mysql.connector.Error as e:
        print("Failed to complete Database Operation {}".format(e))
        return "Database Operation failed...Try later"    

#Updates the date on which the user was last active       
def update_activity(uname,date):
    try:
        cursor.execute('UPDATE user_accounts SET activity = %s WHERE username = %s', (date, uname))
        db.commit()
    except mysql.connector.Error as e:
        print("Failed to complete Database Operation {}".format(e))
        return "Database Operation failed...Try later"      

#Makes a given team inactive once the organizer removes them from an event
def make_inactive(team_id):
    try:
        active=0
        cursor.execute('UPDATE team_event SET active = %s WHERE team_id = %s', (active, team_id))
        db.commit()
    except mysql.connector.Error as e:
        print("Failed to complete Database Operation {}".format(e))
        return "Database Operation failed...Try later"     
     
     
#Checks if the user account has been approved by the admin user 
def check_approval(uname):
    try:
        approved=[]
        cursor.execute(f'SELECT approval FROM user_accounts WHERE username= %s', (uname,))
        approved_tuple = cursor.fetchone()
        approved=approved_tuple[0]
        if approved=="yes":
             return approved 
    except mysql.connector.Error as e:
        print("Failed to complete Database Operation {}".format(e))
        return "Database Operation failed...Try later"              
             
#Returns the details of all organizer accounts that require approval
def approve_organizers():
    try:
        cursor.execute('SELECT email, username FROM user_accounts WHERE approval="no" and acc_type="organizer"')
        pending_organizers=cursor.fetchall()
        return pending_organizers
    except mysql.connector.Error as e:
        print("Failed to complete Database Operation {}".format(e))
        return "Database Operation failed...Try later"    

#Returns the details of all participant accounts that require approval
def approve_participants():
    try:
        cursor.execute('SELECT email,username FROM user_accounts WHERE approval="no" and acc_type="participant"')
        pending_participants=cursor.fetchall()
        return pending_participants
    except mysql.connector.Error as e:
        print("Failed to complete Database Operation {}".format(e))
        return "Database Operation failed...Try later" 
    
#Returns the username of all participants and organizers and the date they were last active 
def all_users():
    try:
        cursor.execute('SELECT username,activity FROM user_accounts WHERE approval="yes" and acc_type<>"admin"')
        all_users=cursor.fetchall()
        return all_users
    except mysql.connector.Error as e:
        print("Failed to complete Database Operation {}".format(e))
        return "Database Operation failed...Try later"    

#Deletes user accounts
def ftn_delete_user(username):
    try:
        cursor.execute('DELETE FROM user_accounts WHERE username = %s', ( username,))
        db.commit()
    except mysql.connector.Error as e:
        print("Failed to complete Database Operation {}".format(e))
        return "Database Operation failed...Try later" 

#Removes players from a given team
def remove_players(team):
    try:
        cursor.execute('DELETE FROM team_player WHERE team_id = %s', ( team,))
        db.commit()
    except mysql.connector.Error as e:
        print("Failed to complete Database Operation {}".format(e))
        return "Database Operation failed...Try later"     

#Removes a team that is registered for an event 
def remove_event(team):
    try:
        cursor.execute('DELETE FROM team_event WHERE team_id = %s', ( team,))
        db.commit()
    except mysql.connector.Error as e:
        print("Failed to complete Database Operation {}".format(e))
        return "Database Operation failed...Try later"     

#Deletes team infomation
def remove_team(team):
    try:
        cursor.execute('DELETE FROM team_master WHERE team_id = %s', ( team,))
        db.commit()
    except mysql.connector.Error as e:
        print("Failed to complete Database Operation {}".format(e))
        return "Database Operation failed...Try later"     

#Deletes events organized by a particular organizer 
def ftn_delete_events(username):
    try:
        cursor.execute('DELETE FROM events WHERE organizer = %s', ( username,))
        db.commit()
    except mysql.connector.Error as e:
        print("Failed to complete Database Operation {}".format(e))
        return "Database Operation failed...Try later" 
#Cancels a given event 
def cancel_event(event_id):
    try:
        cursor.execute('UPDATE events SET cancelled = %s WHERE event_id = %s', (True,event_id,))
        db.commit()
    except mysql.connector.Error as e:
        print("Failed to complete Database Operation {}".format(e))
        return "Database Operation failed...Try later" 

#Checks if a given event has been cancelled 
def check_cancelled(event_id):
    try:
        cursor.execute('SELECT cancelled FROM events WHERE event_id = %s', (event_id,))
        cancel=cursor.fetchone()
        return cancel
    except mysql.connector.Error as e:
        print("Failed to complete Database Operation {}".format(e))
        return "Database Operation failed...Try later" 
#Returns whether the fixture has been created or not 
def check_fixture(event_id):
    try:
        cursor.execute('SELECT fixture_created FROM events WHERE event_id = %s', (event_id,))
        fixture=cursor.fetchone()
        return fixture
    except mysql.connector.Error as e:
        print("Failed to complete Database Operation {}".format(e))
        return "Database Operation failed...Try later" 
 # returns unique event IDS from the events table and the team_event table 
def check_participant_events(username):
    try:
        cursor.execute('''
            SELECT DISTINCT e.event_id
            FROM events e
            LEFT JOIN team_event te ON e.event_id = te.event_id
            WHERE captain = %s AND e.cancelled=0
        ''', (username,))
        available_tournaments = cursor.fetchall()
        return available_tournaments
    except mysql.connector.Error as e:
        print("Failed to complete Database Operation {}".format(e))
        return "Database Operation failed...Try later" 
#Returns the name of the organizer for a given event 
def get_organizer(event_id):
    try:
        cursor.execute('SELECT organizer FROM events WHERE event_id = %s', (event_id,))
        organizer=cursor.fetchone()
        return organizer[0]
    except mysql.connector.Error as e:
        print("Failed to complete Database Operation {}".format(e))
        return "Database Operation failed...Try later" 
#Returns the availability status of a given event
def get_availability_status(event_id):
    try:
        cursor.execute('SELECT availability FROM events WHERE event_id = %s', (event_id,))
        availability_status=cursor.fetchone()
        return availability_status[0]
    except mysql.connector.Error as e:
        print("Failed to complete Database Operation {}".format(e))
        return "Database Operation failed...Try later" 

#Returns the payment status of a given team
def get_payment_status(team_id):
    try:
        cursor.execute('SELECT paid FROM team_event WHERE team_id = %s', (team_id,))
        payment_status=cursor.fetchone()
        return payment_status[0]
    except mysql.connector.Error as e:
        print("Failed to complete Database Operation {}".format(e))
        return "Database Operation failed...Try later" 

# The following methods are used to return the email address of a desired user
def get_organizer_email(event_id):
    try:
        cursor.execute('SELECT email FROM user_accounts WHERE username = %s', (event_id,))
        organizer=cursor.fetchone()
        return organizer
    except mysql.connector.Error as e:
        print("Failed to complete Database Operation {}".format(e))
        return "Database Operation failed...Try later" 

def get_email(organizer):
    try:
        cursor.execute('SELECT email FROM user_accounts WHERE username = %s', (organizer,))
        email=cursor.fetchone()
        return email[0]
    except mysql.connector.Error as e:
        print("Failed to complete Database Operation {}".format(e))
        return "Database Operation failed...Try later" 

def get_email_admin():
    try:
        cursor.execute('SELECT email FROM user_accounts WHERE acc_type = %s', ("admin",))
        email=cursor.fetchone()
        return email[0]
    except mysql.connector.Error as e:
        print("Failed to complete Database Operation {}".format(e))
        return "Database Operation failed...Try later" 

#Creates a new Event 
def create_tournament(event_name, sport, venue, date, max_players, price_per_player, additional, availability, uname, fixture_created, cancelled):
    try:
        formatted_date = date.split()[0]
        query = '''
            INSERT INTO events 
            (event_name, sport, venue, date, max_players, price_per_player, additional, availability, organizer, fixture_created, cancelled) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        '''
        cursor.execute(query, (
            str(event_name), str(sport), str(venue), str(formatted_date),
            int(max_players),int(price_per_player), str(additional),
            int(availability), str(uname), int(fixture_created), int(cancelled)
        ))
        db.commit()
    except mysql.connector.Error as e:
        print("Failed to complete Database Operation {}".format(e))
        return "Database Operation failed...Try later" 

#Changes the fixture created status once the organizer creates the fixture 
def update_fixture_created(event_id):
    try:
        fixture_created = True
        cursor.execute('UPDATE events SET fixture_created = %s WHERE event_id = %s', (fixture_created,event_id))
        db.commit()
    except mysql.connector.Error as e:
        print("Failed to complete Database Operation {}".format(e))
        return "Database Operation failed...Try later" 

#Approves New users 
def ftnApprove(uname):
    try:
        approval = "yes"
        cursor.execute('UPDATE user_accounts SET approval = %s WHERE username = %s', (approval, uname))
        db.commit()
    except mysql.connector.Error as e:
        print("Failed to complete Database Operation {}".format(e))
        return "Database Operation failed...Try later" 

#Deletes user accounts which have been rejected by the admin user
def ftnDecline(uname):
    try:
        cursor.execute('DELETE FROM user_accounts WHERE username = %s', ( uname,))
        db.commit()
    except mysql.connector.Error as e:
        print("Failed to complete Database Operation {}".format(e))
        return "Database Operation failed...Try later" 

#Returns the event details of events organized by a particular organizer 
def all_organizer_events(organizer):
    try:
        cursor.execute('SELECT event_id, event_name FROM events WHERE organizer = %s', (organizer,))
        view_organizer_events_=cursor.fetchall()
        return view_organizer_events_
    except mysql.connector.Error as e:
        print("Failed to complete Database Operation {}".format(e))
        return "Database Operation failed...Try later" 


def view_available_events(participant):
    try:
    #The query returns event details of available events that the participant can register for
    #The subquery returns event IDs of events that the participant has already registered for 
        cursor.execute('''
            SELECT DISTINCT e.event_id, e.event_name, e.sport 
            FROM events e
            LEFT JOIN team_event te ON e.event_id = te.event_id
            WHERE e.availability = 1 AND e.cancelled = 0
            AND e.event_id NOT IN (        
                SELECT event_id FROM team_event WHERE captain = %s
            )
        ''', (participant,))

        available_events = cursor.fetchall()
        return available_events
    except mysql.connector.Error as e:
        print("Failed to complete Database Operation {}".format(e))
        return "Database Operation failed...Try later" 


#Returns details of all players who are not part of any team that has registered for a given event 
def view_available_players(event_id):
    try:
        cursor.execute('''
            SELECT DISTINCT p.player_id, p.player_name, p.phone_number
            FROM players p
            WHERE p.player_id NOT IN (
                SELECT DISTINCT tp.player_id
                FROM team_player tp
                JOIN team_event te ON te.team_id = tp.team_id
                WHERE te.event_id = %s
            )
        ''', (event_id,))
        
        available_players = cursor.fetchall()
        return available_players
    except mysql.connector.Error as e:
        print("Failed to complete Database Operation {}".format(e))
        return "Database Operation failed...Try later" 

#Returns the details of a given event
def show_event_details(event_id):
    try:
        cursor.execute('SELECT event_id, event_name, sport, date, venue, max_players, price_per_player, additional,organizer FROM events WHERE event_id = %s', (event_id,))
        event_details=cursor.fetchone()
        return event_details
    except mysql.connector.Error as e:
        print("Failed to complete Database Operation {}".format(e))
        return "Database Operation failed...Try later" 

#Returns all teams that the participant is part of 
def get_my_teams(participant):
    try:
        cursor.execute('SELECT DISTINCT team_id FROM team_master WHERE captain= %s', (participant,))
        teams=cursor.fetchall()
        return teams
    except mysql.connector.Error as e:
        print("Failed to complete Database Operation {}".format(e))
        return "Database Operation failed...Try later" 
     
#Creates a new team
def create_team(team_name,num_team_players,captain):
    try:
        cursor.execute(f'Insert into team_master (team_name,num_of_players,captain) values(\'{str(team_name)}\', \'{int(num_team_players)}\',\'{str(captain)}\')')
        db.commit()
    except mysql.connector.Error as e:
        print("Failed to complete Database Operation {}".format(e))
        return "Database Operation failed...Try later" 

#Creates a new player
def new_player(player_name, player_phone_number):
    try:
        cursor.execute(f'Insert into players (player_name,phone_number) values(\'{str(player_name)}\', \'{int(player_phone_number)}\')')
        db.commit()
    except mysql.connector.Error as e:
        print("Failed to complete Database Operation {}".format(e))
        return "Database Operation failed...Try later" 

#Returns the team ID of the most recently created team
def get_team_id():
    try:
        cursor.execute('SELECT team_id FROM team_master ORDER BY team_id DESC LIMIT 1')
        team_id = cursor.fetchone()
        return team_id
    except mysql.connector.Error as e:
        print("Failed to complete Database Operation {}".format(e))
        return "Database Operation failed...Try later" 
#Returns the team ID of the participant's team for a specifc event
def get_my_team_id(captain,event_id):
    try:
        cursor.execute('SELECT team_id FROM team_event WHERE captain= %s AND event_id=%s', (captain,event_id))
        team_id = cursor.fetchone()
        return team_id[0]
    except mysql.connector.Error as e:
        print("Failed to complete Database Operation {}".format(e))
        return "Database Operation failed...Try later" 

#The following methods get the event names of all events the participant has registered for 
def get_teams(participant):
    try:
        cursor.execute('SELECT DISTINCT team_id FROM team_master WHERE captain= %s', (participant,))
        teams = cursor.fetchall()
        return teams
    except mysql.connector.Error as e:
        print("Failed to complete Database Operation {}".format(e))
        return "Database Operation failed...Try later" 

def get_event(team_id):
    try:
        cursor.execute('SELECT DISTINCT event_id FROM team_event WHERE team_id= %s', (team_id,))
        event_id = cursor.fetchone()
        if event_id is not None:
            return event_id
    except mysql.connector.Error as e:
        print("Failed to complete Database Operation {}".format(e))
        return "Database Operation failed...Try later" 
def get_event_name(event_id):
    try:
        cursor.execute('SELECT DISTINCT event_name,event_id, fixture_created FROM events WHERE event_id= %s', (event_id,))
        event_data= cursor.fetchone()
        if event_data is not None:
            event_name = event_data
            return event_name
    except mysql.connector.Error as e:
        print("Failed to complete Database Operation {}".format(e))
        return "Database Operation failed...Try later"    
#Returns the date of a given event
def get_event_date(event_id):
    try:
        cursor.execute('SELECT DISTINCT date FROM events WHERE event_id= %s', (event_id,))
        event_id = cursor.fetchone()
        return event_id
    except mysql.connector.Error as e:
        print("Failed to complete Database Operation {}".format(e))
        return "Database Operation failed...Try later" 

#Returns the name of a given event    
def get_event_name_for_title(event_id):
    try:
        cursor.execute('SELECT event_name FROM events WHERE event_id= %s', (event_id,))
        event_data= cursor.fetchone()
        return event_data
    except mysql.connector.Error as e:
        print("Failed to complete Database Operation {}".format(e))
        return "Database Operation failed...Try later" 

#Returns the event IDs of all events organized by a particular organizer
def get_event_ids(username):
    try:
        cursor.execute('SELECT event_id FROM events WHERE organizer= %s', (username,))
        event_ids= cursor.fetchall()
        return event_ids
    except mysql.connector.Error as e:
        print("Failed to complete Database Operation {}".format(e))
        return "Database Operation failed...Try later" 

#Adds players to a specified team
def player_to_team(player_list,team_id):
    try:
        for player in player_list:
            cursor.execute(f'Insert into team_player (player_id,team_id) values(\'{int(player)}\', \'{int(team_id)}\')')
        db.commit()       
    except mysql.connector.Error as e:
        print("Failed to complete Database Operation {}".format(e))
        return "Database Operation failed...Try later" 

#Returns the maximum number of players allowed per team for a given event 
def get_max_players(event_id):
    try:
        max_players=[]
        cursor.execute(f'SELECT max_players FROM events WHERE event_id= %s', (event_id,))
        max_players_tuple = cursor.fetchone()
        max_players=max_players_tuple[0]
        return max_players
    except mysql.connector.Error as e:
        print("Failed to complete Database Operation {}".format(e))
        return "Database Operation failed...Try later" 

#Registers a new team for a given event 
def add_team_to_event(team_id,event_id,paid,captain,active):
    try:
        cursor.execute(f'INSERT INTO team_event (team_id, event_id, paid, captain, active) VALUES ({int(team_id)}, {int(event_id)}, {int(paid)}, \'{str(captain)}\', {int(active)})')
        db.commit() 
    except mysql.connector.Error as e:
        print("Failed to complete Database Operation {}".format(e))
        return "Database Operation failed...Try later" 

#The following methods return the names of the teams that have registered for an event 
def get_teams_for_event(event_id):
    try:
        cursor.execute(f'SELECT team_id FROM team_event WHERE event_id= %s and active=1', (event_id,))
        teams=cursor.fetchall()
        return teams
    except mysql.connector.Error as e:
        print("Failed to complete Database Operation {}".format(e))
        return "Database Operation failed...Try later" 

def get_team_names(team_ids):
    try:
        teams=[]
        for team_id in team_ids:
                cursor.execute(f'SELECT team_id,team_name FROM team_master WHERE team_id= %s', (team_id[0],))
                team=cursor.fetchone()
                if team: 
                    teams.append(team)
        return teams    
    except mysql.connector.Error as e:
        print("Failed to complete Database Operation {}".format(e))
        return "Database Operation failed...Try later" 

#Returns the Payment status of a given team
def check_paid(team):
    try:
        cursor.execute(f'SELECT paid FROM team_event WHERE team_id= %s', (team,))
        payment=cursor.fetchone()
        if payment==(0,):
            return ("Pending")
        elif payment==(1,):
            return ("Complete")
        else:
            return("Error")
    except mysql.connector.Error as e:
        print("Failed to complete Database Operation {}".format(e))
        return "Database Operation failed...Try later" 
    
#Updates payment status for a given team
def update_payment_status(team_id,payment):
    try:
        cursor.execute('UPDATE team_event SET paid = %s WHERE team_id= %s', (payment, team_id))
        db.commit()
    except mysql.connector.Error as e:
        print("Failed to complete Database Operation {}".format(e))
        return "Database Operation failed...Try later" 

#Updates availability status for a given event
def update_availability_status(event_id,availability):
    try:
        cursor.execute('UPDATE events SET availability = %s WHERE event_id= %s', (availability, event_id))
        db.commit()
    except mysql.connector.Error as e:
        print("Failed to complete Database Operation {}".format(e))
        return "Database Operation failed...Try later" 

#Returns the details of a specifc team
def get_team_details(team_id):
    try:
        cursor.execute(f'SELECT team_name,num_of_players FROM team_master WHERE team_id= %s', (team_id,))
        team_info=cursor.fetchone()
        return team_info
    except mysql.connector.Error as e:
        print("Failed to complete Database Operation {}".format(e))
        return "Database Operation failed...Try later" 
    
#Returns the player IDs of the members in a given team
def get_player_ids(team_id):
    try:
        cursor.execute(f'SELECT player_id FROM team_player WHERE team_id= %s', (team_id,))
        player_ids=cursor.fetchall()
        return player_ids
    except mysql.connector.Error as e:
        print("Failed to complete Database Operation {}".format(e))
        return "Database Operation failed...Try later" 

#Returns the player names that correspond to the player IDs of the members in a team
def get_player_names(player_ids):
    try:
        players=[]
        for player_id in player_ids:
                cursor.execute(f'SELECT player_name,phone_number FROM players WHERE player_id= %s', (player_id[0],))
                player=cursor.fetchone()
                if player: 
                    players.append(player)
        return players                  
    except mysql.connector.Error as e:
        print("Failed to complete Database Operation {}".format(e))
        return "Database Operation failed...Try later" 

#Removes a team from an event 
def withdraw_from_event(team_id):
    try:
        cursor.execute('DELETE FROM team_event WHERE team_id = %s', ( team_id,))
        db.commit()
    except mysql.connector.Error as e:
        print("Failed to complete Database Operation {}".format(e))
        return "Database Operation failed...Try later"      



              