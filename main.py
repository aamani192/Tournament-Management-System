# import mysql.connector
import datetime
from datetime import date

from database import *
from flask import Flask, render_template, request, session,  send_file, Response
from secret import session_key
import random
from reportlab.pdfgen import canvas



app = Flask(__name__)
app.secret_key = session_key

@app.route('/', methods = ['GET', 'POST'])
#Returns Login Page
def login():
    return render_template("login.html")

@app.route('/logout')
#Allows user to log out
def logout():
    session.clear()

    return render_template("login.html")


@app.route('/submit', methods = ['GET', 'POST'])
def login_submissions():
    uname = request.form['username']
    password = request.form['password']
    if 'login' in request.form:
                user_details=check_account(uname) #Checks if user account exists
                if user_details:
                        session['uname'] = uname
                        correct_password=check_password(uname,password) #Checks if credentials are correct
                        if correct_password:
                            # x = datetime.datetime.now()
                            # y=x.strftime("%x")
                            date = datetime.datetime.now().date()
                            update_activity(uname,date) #Updates User Activity 
                            acc_type=user_details[1]
                            #The following redirect Users to the appropriate page based on their account type and approval status 
                            if acc_type == "admin":
                                return render_template("admin_homepage.html")
                            else:
                                approved=check_approval(uname)
                                if approved:
                                    if acc_type == "Organizer":
                                        return render_template("organizer_homepage.html")
                                    elif acc_type == "Participant":
                                        return render_template("participant_homepage.html")
                                else: 
                                    contact= get_email_admin()
                                    print (contact)
                                    return render_template("pending_approval.html",contact_email=contact)
                        else: 
                            return render_template("login.html",result="Incorrect Password")
                else:  
                      return render_template("login.html",result="Invalid Username")
                
    elif 'new_acc' in request.form:
        return render_template("signup.html") #Redirects User to Sign Up page 


@app.route('/new_user', methods = ['GET', 'POST'])
def success():
    #Retrieves the values entered by the User
    email = request.form['email']
    acc_type = request.form['acc_type']
    username = request.form['username']
    password = request.form['password']
    confirm_password = request.form['confirm_password']
    approval="no"
    if confirm_password==password:  #checks if the password is the same on both entries
            already_taken=create_account(email, acc_type, username, password,approval) #account is created only if the values match
            if already_taken: #Checks if the email address is already being used for another account  
                 return render_template("signup.html",result="User account already exists")
            else:
                 return render_template("login.html")
    else:  
        return render_template("signup.html",result="Passwords must match") #prompted to renter if they do not match


# The following redirect users to the appropriate home page based on their acoount type
@app.route('/admin_homepage', methods = ['GET', 'POST'])
def admin_homepage():
    return render_template("admin_homepage.html")

    
@app.route('/participant_homepage', methods = ['GET', 'POST'])
def participant_homepage():
    return render_template("participant_homepage.html")

@app.route('/organizer_homepage', methods = ['GET', 'POST'])
def organizer_homepage():
    return render_template("organizer_homepage.html")


@app.route('/admin_options', methods = ['GET', 'POST'])
#Redirects admin user to the appropriate page based on the option they select
def admin_options():
    if 'approve_new_organizers' in request.form:
        pending_organizers=approve_organizers() #Gets details of all organizers who require approval
        if pending_organizers: 
            return render_template("organizer_approval.html",result=pending_organizers)
        else: 
            return render_template("admin_message.html",result="No Organizer approvals pending")
    elif 'approve_new_participants' in request.form:
        pending_participants=approve_participants() #Gets details of all participants who require approval
        if pending_participants: 
            return render_template("participant_approval.html",result=pending_participants)
        else:
            return render_template("admin_message.html",result="No Participant approvals pending") 
    elif 'delete_inactive' in request.form:
         all_user=all_users() #Gets details of all participants and organizers
         return render_template("delete_inactive.html", result=all_user)
    
@app.route('/organizer_options', methods = ['GET', 'POST'])
#Redirects organizers to the appropriate page based on the option they select
def organizer_options():
    organizer=session.get('uname')
    if 'add_tournament' in request.form:
        return render_template("add_event.html" )
    elif 'manage_existing_tournaments' in request.form:
        organizer_events=all_organizer_events(organizer) #Gets details of all events organized by the user
        return render_template("manage_events.html", result=organizer_events)

@app.route('/manage_events', methods = ['GET', 'POST'])
def manage_events():
    organizer=session.get('uname')
    organizer_events=all_organizer_events(organizer) #Gets details of all events organized by the user 
    return render_template("manage_events.html", result=organizer_events)

    
@app.route('/participant_options', methods = ['GET', 'POST'])
#Redirects participants to the appropriate page based on the option they select
def participant_options():
    if 'available_tournaments' in request.form:
        participant=session.get('uname')
        all_events=view_available_events(participant) #Gets all events that the participant can register for 
        return render_template("all_events.html",result=all_events)
    elif 'your_tournaments' in request.form:
        participant=session.get('uname')
        teams=get_teams(participant) #Gets the team details for all the participant's teams
        events=[]
        for team in teams:
            event_id=get_event(team[0])
            if event_id!=None: 
                event_name=get_event_name(event_id[0]) #Gets the event names of all events the participant has registered for 
                if event_name!=None:
                    events.append(event_name) 
        return render_template("my_tournaments.html",result=events)
        
    
       
@app.route('/view_info', methods = ['GET', 'POST'])
#Redirects participants to the appropriate page according to the status of the event they have selected 
def view_info():
    event_id=request.form['event_id']
    captain=session.get('uname')
    cancelled=check_cancelled(event_id)
    if cancelled[0]==1:  #Checks if the event has been cancelled due to the removal of an organizer 
        return render_template("participant_message.html",result="Sorry! This tournament has been cancelled.")
    else:
        team_id=get_my_team_id(captain,event_id)
        active= team_active(team_id)
        if active[0]==0:  #Checks if the team has been removed from the event by the organizer 
            organizer_uname=get_organizer(event_id)
            organizer_email=get_organizer_email(organizer_uname)
            return render_template("participant_message.html",result="Sorry! Your team has been removed from this tournament. For any questions please contact:",message=organizer_email[0])
        else: 
            event_details=show_event_details(event_id) #Gets the event details 
            return render_template("my_event_details.html",result=event_details)

@app.route('/withdraw', methods = ['GET', 'POST'])
#Allows Participant to withdraw from an event has long as the fixture has not been created
def withdraw():
    captain=session.get('uname')
    event_id=request.form['event_id']
    fixture=check_fixture(event_id)
    if fixture== (1,): #Checks if the fixture has been created
        print ("in")
        organizer=get_organizer(event_id)
        email=get_email(organizer)
        return render_template("participant_message.html",result="Sorry! The Fixture has already been created. Please contact "+email)
    else: #Removes the team from the event 
        team_id=get_my_team_id(captain,event_id)
        withdraw_from_event(team_id)
        teams=get_teams(captain)
        events=[]
        for team in teams:
            event_id=get_event(team[0])
            if event_id!=None: 
                event_name=get_event_name(event_id[0])
                if event_name!=None:
                    events.append(event_name) 
        return render_template("my_tournaments.html",result=events)        



@app.route('/new_event', methods = ['GET', 'POST'])
#Creates New Tournament 
def new_event():
    uname = session.get('uname')
    event_name = request.form['event_name']
    sport = request.form['sport']
    venue= request.form['venue']
    date = request.form['date']
    max_players= request.form['max_players']
    price_per_player= request.form['price_per_player']
    additional= request.form['additional']
    availability=True 
    fixture_created=False
    cancelled=False
    create_tournament(event_name,sport,venue,date,max_players,price_per_player,additional,availability,uname,fixture_created,cancelled)
    return render_template("organizer_homepage.html")

#The following allow the user to approve and decline new users 

@app.route('/approve_new_organizer', methods = ['GET', 'POST'])
def approve_new_organizer():
    username=request.form['user_name']
    ftnApprove(username)
    pending_organizers=approve_organizers()
    return render_template("organizer_approval.html",result=pending_organizers)

@app.route('/decline_new_organizer', methods = ['GET', 'POST'])
def decline_new_organizer():
    username=request.form['user_name']
    ftnDecline(username)
    pending_organizers=approve_organizers()
    return render_template("organizer_approval.html",result=pending_organizers)


@app.route('/approve_new_participant', methods = ['GET', 'POST'])
def approve_new_participant():
    username=request.form['user_name']
    ftnApprove(username)
    pending_participants=approve_participants()
    return render_template("participant_approval.html",result=pending_participants)
 

@app.route('/decline_new_participant', methods = ['GET', 'POST'])
def decline_new_participant():
    username=request.form['user_name']
    ftnDecline(username)
    pending_participants=approve_participants()
    return render_template("participant_approval.html",result=pending_participants)

@app.route('/delete_user', methods = ['GET', 'POST'])
#Allows the admin to delete users 
def delete_user():
    username=request.form['user_name']
    user_type=check_usertype(username)
    if user_type[0]=="Organizer":
        event_ids=get_event_ids(username)
        for event_id in event_ids:
            cancel_event(event_id[0]) #Cancels any upcoming organizer events  
        ftn_delete_user(username)
    else:
        today = date.today()
        get_teams(username)
        events=check_participant_events(username)
        participant_has_active=0
        for event in events: 
            event_date=get_event_date(event[0])
            if event_date[0]>today: #Checks if the participant is registered for an upcoming event 
                participant_has_active=1
        if participant_has_active==1:
            return render_template("admin_message.html",result="You cannot deactivate this account. They are currently registered for an event")
        else: #deletes participant 
            teams=get_my_teams(username)
            for team in teams:
                remove_players(team[0])
                remove_event(team[0])
                remove_team(team[0])
            ftn_delete_user(username)
    all_user=all_users()
    return render_template("delete_inactive.html",result=all_user)



@app.route('/register_for_event', methods = ['GET', 'POST'])
#Shows the event details for a selected event that the participant can register for 
def register_for_event():
    event_id=request.form['event_selection']
    event_details=show_event_details(event_id)
    max_players=get_max_players(event_id)
    session['max_players'] = max_players
    session['event_id'] = event_id
    return render_template("display_event_details.html",result=event_details)

@app.route('/register_for_new_event', methods = ['GET', 'POST'])
#Accepts team information from the participant 
def register_for_new_event():
    return render_template("accept_team_details.html")

@app.route('/register_team', methods = ['GET', 'POST'])
#Retrieves the data entered by the participant to create a new team for the event 
def register_team():
    team_name=request.form['team_name']
    num_team_players=request.form['num_team_players']
    max_players=session.get('max_players')
    captain=session.get('uname')
    if int(num_team_players)>int(max_players): #Checks if the number of players exceed the maximum limit
        return render_template("accept_team_details.html",result="The Maximum number of players is "+str(max_players) ) 
    create_team(team_name,num_team_players,captain)
    team_id=get_team_id()
    session['team_id']=team_id
    session['num_team_players']=num_team_players
    event_id=session.get('event_id')    
    all_players=view_available_players(event_id)
    team_id=team_id[0]
    paid=0
    active=1
    add_team_to_event(team_id,event_id,paid,captain,active)
    return render_template("select_players.html",result=all_players)

@app.route('/add_new_player', methods = ['GET', 'POST'])
#Allows the user to enter new player information
def add_new_player():
    return render_template("player_info.html")

@app.route('/create_player', methods = ['GET', 'POST'])
#Retrieves new player information and adds a new player 
def create_player():
    event_id=session.get('event_id') 
    player_name=request.form['player_name']
    player_phone_number=request.form['player_phone_number']
    new_player(player_name,player_phone_number)
    all_players=view_available_players(event_id)
    return render_template("select_players.html",result=all_players)


@app.route('/select_event', methods = ['GET', 'POST'])
#Allows the organizer to select an event that they are organizing 
def select_event():
    event_id=request.form['select_event']
    session['event_id_selection'] = event_id
    event_info=show_event_details(event_id)
    return render_template("display_organizer_event_details.html", result=event_info)

@app.route('/show_event', methods = ['GET', 'POST'])
#Allows the organizer to return to the details of the tournament they have selected 
def show_event():
    event_id=session.get('event_id_selection')
    event_info=show_event_details(event_id)
    return render_template("display_organizer_event_details.html", result=event_info)

@app.route('/view_teams', methods = ['GET', 'POST'])
#Allows the organizer to select an event and view the teams that have registered 
#Also displays the payment status for each team and the availability status of the event
def view_teams():
    event_id=session.get('event_id_selection')
    availability_status = get_availability_status(event_id)
    team_ids=get_teams_for_event(event_id)
    teams=get_team_names(team_ids)
    payments=[]
    for team in team_ids:
        paid=check_paid(team[0])
        payments.append(paid)
    return render_template("manage_this_event.html",result=teams,payment_info=payments,availability_status=availability_status)

@app.route('/remove_team', methods = ['GET', 'POST'])
#Allows organizers to remove teams as long as they have not paid already 
def remove_team():
    team_id=request.form['team_selection']
    event_id=session.get('event_id_selection')
    paid_confirm= check_paid(team_id)
    availability_status = get_availability_status(event_id)
    print(paid_confirm)
    if paid_confirm=="Pending": #If they have not paid their team is removed
        remove_players(team_id)
        make_inactive(team_id)
        team_ids=get_teams_for_event(event_id)
        teams=get_team_names(team_ids)
        payments=[]
        for team in team_ids:
            paid=check_paid(team[0])
            payments.append(paid)
        return render_template("manage_this_event.html",result=teams,payment_info=payments, availability_status=availability_status)        
    else: #The organizer is shown a message stating that the team has already paid
        return render_template("organizer_message.html", result="This team has already paid")

@app.route('/edit_info', methods = ['GET', 'POST'])
#Allows the organizer to edit event information as long as no teams have registereed
def edit():
    event_id=session.get('event_id_selection')
    teams=check_teams(event_id)
    if teams:
        return render_template("organizer_message.html", result="This tournament already has participants who have registered")
    else: 
        return render_template("edit_info.html")
        
@app.route('/confirm_edit', methods = ['GET', 'POST'])
#Retrieves the edited event information and updates the event 
def confirm_edit():
    event_id=session.get('event_id_selection')
    event_name = request.form['event_name']
    sport = request.form['sport']
    venue= request.form['venue']
    date = request.form['date']
    max_players= request.form['max_players']
    price_per_player= request.form['price_per_player']
    additional= request.form['additional']
    edit_info(event_id,event_name,sport,venue,date,max_players,price_per_player,additional)
    event_info=show_event_details(event_id)
    return render_template("display_organizer_event_details.html", result=event_info)

    

@app.route('/add_player_to_team', methods = ['GET', 'POST'])
#Adds the selected player to the participant's team
def add_player_to_team ():
    player_list=request.form.getlist("player_list")
    num_team_players=session.get('num_team_players')
    event_id=session.get('event_id_selection')
    if (len(player_list)!=int(num_team_players)):

        all_players=view_available_players(event_id)
        if num_team_players==1:
            alert="Select "+ num_team_players+" player"
        else:
            alert="Select "+ num_team_players+" players"
        return render_template("select_players.html",message=alert,result=all_players)
    else: 
        team_id=session.get('team_id')[0] 
        player_to_team(player_list,team_id)
        return render_template("participant_homepage.html")
    
@app.route('/view_team_details', methods = ['GET', 'POST'])
#Allows the organizer to view the players in a specifc team with their details, along with the payment status of the team
def view_team_details():
    team_id=request.form['team_selection']
    payment_status=get_payment_status(team_id)
    session['team_id_selection'] = team_id
    team=get_team_details(team_id)
    player_ids=get_player_ids(team_id)
    player_details=get_player_names(player_ids)    
    return render_template("display_team_details.html",team_info=team,player_info=player_details,payment_status=payment_status)

@app.route('/update_payment', methods = ['GET', 'POST'])
#Allows the user to change the payment status of a selected team 
def update_payment():
    team_id=session.get('team_id_selection')
    event_id=session.get('event_id_selection')  
    payment_status = int(request.form.get('payment_status', 0))
    availability_status = get_availability_status(event_id)
    update_payment_status(team_id, payment_status)
    team_ids=get_teams_for_event(event_id)
    teams=get_team_names(team_ids)
    payments=[]
    for team in team_ids:
        paid=check_paid(team[0])
        payments.append(paid)
    return render_template("manage_this_event.html",result=teams,payment_info=payments, availability_status=availability_status)


@app.route('/update_availability', methods = ['GET', 'POST'])
#Allows the user to change the availability status of a selected event
def update_availability():
    event_id = session.get('event_id_selection')
    availability_status = int(request.form.get('availability_status', 0))
    update_availability_status(event_id, availability_status)
    organizer=session.get('uname')
    organizer_events=all_organizer_events(organizer)
    return render_template("manage_events.html", result=organizer_events)

@app.route('/fixture', methods = ['GET', 'POST'])
#Generates a PDF showing the fixture 
def fixture():
    event_id=session.get('event_id_selection')
    update_fixture_created(event_id)  #changes status so participants can no longer withdraw without contacting the organizer
    event_name= get_event_name_for_title(event_id)
    team_ids=get_teams_for_event(event_id)
    teams=get_team_names(team_ids)
    num_teams = len(teams) #total number of registered teams
    # Randomly shuffle the teams
    random.shuffle(teams)
    # Pair up teams 
    pairings = [(teams[i], teams[i + 1]) if i + 1 < num_teams else (teams[i],) for i in range(0, num_teams, 2)] #pairs teams together 
    file_path = "My_Fixture.pdf"
    pdf_canvas = canvas.Canvas(file_path)
    pdf_canvas.setTitle("My  PDF")
    pdf_canvas.setFont("Times-Bold", 16)
    pdf_canvas.drawString(250, 750, event_name[0]) #Displays tournament Name on the PDF 
    pdf_canvas.setFont("Helvetica", 12)
    y_position = 700 
    #displays each match on the PDF
    for match in pairings: 
        if len(match) == 2:
            pdf_canvas.drawString(100, y_position, f"{match[0][1]} vs {match[1][1]}")
        elif len(match) == 1:
            pdf_canvas.drawString(100, y_position, f"{match[0][1]}")

        y_position -= 50  
    # Save the PDF to the specified file path
    pdf_canvas.save()
    # Returns File
    return send_file(file_path, as_attachment=True)

    
if __name__ == '__main__':
 
    app.run(debug=True)



