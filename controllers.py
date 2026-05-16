from flask import render_template, request, redirect, url_for, flash, session
from app import app
from models import User,Influencer,Sponsor,Campaign,CampaignRequest,db
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from datetime import datetime
import csv
from uuid import uuid4

import matplotlib.pyplot as plt
import os
from sqlalchemy import select, func
import numpy as np




def auth_required(func):
    @wraps(func)
    def inner(*args, **kwargs):
        if 'user_id' in session:
            return func(*args, **kwargs)
        else:
            flash('Please login to continue')
            return redirect(url_for('user_login'))
    return inner


def admin_req(func):
    @wraps(func)
    def inner(*args, **kwargs):
        if 'user_id' not in session:
            flash('You must login to continue')
            return redirect(url_for('user_login'))
        user=User.query.get(session.get('user_id'))
        if not user.role =='admin':
            flash('You are not Authorized')                                        
            return redirect(url_for('home'))
        return func(*args, **kwargs)
    return inner


def spon_req(func):
    @wraps(func)
    def inner(*args, **kwargs):
        if 'user_id' not in session:
            flash('You must login to continue')
            return redirect(url_for('user_login'))
        user=User.query.get(session.get('user_id'))
        if not user.role == 'sponsor':
            flash('You are not Authorized')
            return redirect(url_for('home'))
        return func(*args, **kwargs)
    return inner

def influ_requ(func):
    @wraps(func)
    def inner(*args, **kwargs):
        if 'user_id' not in session:
            msg='You must login to continue'
            return redirect(url_for('user_login'))
        user=User.query.get(session.get('user_id'))
        if not user.role == 'influencer':
            flash('You are not Authorized')
            return redirect(url_for('home'))
        return func(*args, **kwargs)
    return inner



def authenticate_user(username, password):
    user = User.query.filter_by(username=username).first()
    if user and check_password_hash(user.password_hash, password):
        return user
    return None


'login and register'



@app.route("/") #it refers base url 127.0.0.1:5000
def home():
    return render_template('login.html')



@app.route("/spon_regis", methods=["GET", "POST"])
def spon_regis():
    if request.method == "POST":
        industry = request.form.get("industry")
        username = request.form.get("username")
        password = request.form.get("pwd")
        if not industry or not password or not username:
            return render_template("spon_regis.html", msg="Please fill all the fields")
        elif not User.query.filter_by(username=username).first():
            new_user = User(username=username, password=password, role="sponsor")
            db.session.add(new_user)
            db.session.commit()
            new_sponsor = Sponsor(user_id=new_user.id, industry=industry,name=username)
            db.session.add(new_sponsor)
            db.session.commit()
            return render_template("user_login.html", msg="Account created successfully")
        else:
            return render_template("spon_regis.html", msg="Username already exists")
    return render_template("spon_regis.html", msg="")





@app.route("/influ_regis", methods=["GET", "POST"])
def influ_regis():
    if request.method == "POST":
        platform = request.form.get("platform")
        username = request.form.get("username")
        password = request.form.get("password")
        followers = request.form.get("followers")
        from models import User
        usr = User.query.filter_by(username=username).first()
        if  username=="" or  password=="" or platform=="":
            return render_template("influ_regis.html", msg="Please fill out all fields!")

        elif not usr:
            new_user = User(username=username, password=password, role="influencer")
            db.session.add(new_user)
            db.session.commit()
            new_influencer = Influencer(user_id=new_user.id,name=username, platform=platform,followers=followers)
            db.session.add(new_influencer)
            db.session.commit()
            
            return render_template("user_login.html", msg="Account created successfully")
        else:
            return render_template("influ_regis.html", msg="Username already exists")
    return render_template("influ_regis.html", msg="")



@app.route("/user_login",methods=["GET","POST"]) #it refers base url+/login
def user_login():
    if request.method=="POST":
        from models import User
        username=request.form.get("username")
        password=request.form.get("pwd")
        usr = User.query.filter_by(username=username).first()
        if  username=="" or  password=="":
            return render_template("user_login.html",msg="plese fill out all feilds!")
        
        if usr and usr.role=="influencer":
            if password==usr.password:
                user_info=fetch_user_info(usr.id) #one user object
                session["role"]="influencer"
                session["user_id"]=user_info.id
                session["user_name"]=user_info.username
                return redirect(url_for('influ_dash'))
            return render_template("user_login.html",msg="incorrect password!!")
        
        elif usr and usr.role=="sponsor":
            if password==usr.password:
            # missing password check
                user_info=fetch_user_info(usr.id) #one user object
                session["role"]="sponsor"
                session["user_id"]=user_info.id
                session["user_name"]=user_info.username
                return redirect(url_for('spon_dash'))
            return render_template("user_login.html",msg="incorrect password!!")

        else:
            return render_template("user_login.html",msg="Invalid credentials!!")
    return render_template("user_login.html",msg="")


"login and register end"


@app.route("/admin_login",methods=["GET","POST"]) #it refers base url+/login
def admin_login():
    from models import User
    if request.method=="POST":
        username=request.form.get("username")
        password=request.form.get("pwd")  
        camp=User.query.filter_by(role="admin").first()
        if not camp:
            new_user = User(username="admin", password=123, role="admin")
            db.session.add(new_user)
            db.session.commit()
        usr=User.query.filter_by(username=username).first() #Get existig user matched
        if  username=="" or  password=="":
            return render_template("admin_login.html",msg="plese fill out all feilds!")
        
        
        if usr and usr.role=="admin":
            if password==usr.password:
                user_info=fetch_user_info(usr.id)
                session["user_id"]=user_info.id
                session["user_name"]=user_info.username
                session["role"]="admin"
                return redirect(url_for('admin_dash'))
            return render_template("admin_login.html",msg="Incorrect password!!")
        return render_template("admin_login.html",msg="admin does not exist")
    return render_template("admin_login.html",msg="")




#UDF for reading all general users
def fetch_users():
    user_list={}
    influ=User.query.filter_by(role="influencer").all()
    for user in influ:
        if user.id not in user_list.keys():
            user_list[user.id]=[user.username,len(user.campaigns)]
    spon=User.query.filter_by(role="sponsor").all()
    for user in spon:
        if user.id not in user_list.keys():
            user_list[user.id]=[user.username,len(user.campaigns),user.id]
    return user_list

def fetch_user_info(id):
    user_info=User.query.filter_by(id=id).first()
    return user_info


'campaign models'
#more routes here
@app.route("/campaign/add",methods=["GET","POST"])
@spon_req
def new_camp():
    if request.method=="POST":
        user_id=session.get('user_id')
        title=request.form.get("title")
        description=request.form.get("description")
        budget=request.form.get("budget")
        date=request.form.get("date")
        if not title or not description or not budget or not date:
            return render_template("spon_camp.html",id=user_id,msg="Please fill out all fields!")
        camp=Campaign(title=title,description=description,spon_id=user_id,budget=budget,end_date=date)
        db.session.add(camp)
        db.session.commit() #now we can use camp.id to get the id of the campaign
        return redirect(url_for("spon_camp"))




@app.route("/campaignreq/accept",methods=["GET","POST"])
@influ_requ
def campreq_accept():
    if request.method=="POST":
        user_id=session.get('user_id')
        cr_id=request.form.get("id")
        campaignreq = CampaignRequest.query.get(cr_id)
        if campaignreq:
            campaignreq.req_status_influ = 1
            db.session.add(campaignreq)
            db.session.commit()
            camp=campaignreq.campaign_id
            camp=Campaign.query.get(camp)
            camp.progress="accepted"
            db.session.add(camp)
            db.session.commit()
        return redirect(url_for("influ_dash"))
    




@app.route("/campaign/flag",methods=["GET","POST"])
def camp_flag():
    if request.method=="POST":
        cid=request.form.get("campid")
        campaign = Campaign.query.get(cid)
        if campaign:
            campaign.flagged = 1
            campaign.progress ="accepted"
            db.session.add(campaign)
            db.session.commit()
            return redirect(url_for("admin_find"))
        return redirect(url_for("admin_find"))
    
@app.route("/sponsor/flag",methods=["GET","POST"])
def spon_flag():
    id=request.form.get("id")
    if request.method=="POST":
        id=request.form.get("id")
        campaign = Sponsor.query.get(id)
        if campaign:
            campaign.flagged = 1
            db.session.add(campaign)
            db.session.commit()
        return redirect(url_for("admin_find"))


@app.route("/influencer/flag",methods=["GET","POST"])
def influ_flag():
    if request.method=="POST":
        id=request.form.get("id")
        campaign = Influencer.query.get(id)
        if campaign:
            campaign.flagged = 1
            db.session.add(campaign)
            db.session.commit()
            return redirect(url_for("admin_find"))







@app.route("/influencerreq/accept",methods=["GET","POST"])
def sponreq_accept():
    if request.method=="POST":
        user_id=session.get('user_id')
        cr_id=request.form.get("id")
        campaignreq = CampaignRequest.query.get(cr_id)
        if campaignreq:
            campaignreq.req_status_spon = 1
            db.session.add(campaignreq)
            db.session.commit()
            cid=campaignreq.campaign_id
            campaign = Campaign.query.get(cid)
            campaign.progress ="accepted"
            db.session.add(campaign)
            db.session.commit()
            return redirect(url_for("spon_dash"))
        else:
            return "campaign request id not found"
    return redirect(url_for("spon_dash"))
        




@app.route("/influencerreq/delete",methods=["GET","POST"])
def sponreq_delete():
    if request.method=="POST":
        user_id=session.get('user_id')
        cr_id=request.form.get("id")
        campaignreq = CampaignRequest.query.get(cr_id)
        if campaignreq:
            campaignreq.req_status_spon = 0
            db.session.delete(campaignreq)
            db.session.commit()
            return redirect(url_for("spon_dash"))
        else:
            return "campaign request id not found"
    return redirect(url_for("spon_dash"))
        







@app.route("/campaign/edit",methods=["GET","POST"])
@spon_req
def edit_camp():
    if request.method=="POST":
        user_id=session.get('user_id')
        campid=request.form.get("id")
        new_title=request.form.get("title")
        new_description=request.form.get("description")
        new_budget=request.form.get("budget")
        new_date=request.form.get("date")
        if not new_title or not new_description or not new_budget or not new_date:
            return render_template("spon_camp.html",id=user_id,msg="fields cannot be empty!")
        campaign = Campaign.query.filter_by(id=campid).first()
        campaign.title = new_title
        campaign.description=new_description
        campaign.budget=new_budget
        campaign.end_date=new_date
        db.session.commit()
        user_info=fetch_user_info(user_id)
    return redirect(url_for('spon_camp'))
    
@app.route("/campaign/delete",methods=["GET","POST"])
# @spon_req
def delete_camp():
    if request.method=="POST":
        user_id=session.get('user_id')
        campid=request.form.get("id")
        campaign = Campaign.query.filter_by(id=campid).first()
        db.session.delete(campaign)
        db.session.commit()
        user_info=fetch_user_info(user_id)
        return redirect(url_for("spon_camp"))
    
@app.route("/campaignreq/delete",methods=["GET","POST"])
# @spon_req
def delete_camp_req():
    if request.method=="POST":
        user_id=session.get('user_id')
        campid=request.form.get("id")
        campaign = CampaignRequest.query.filter_by(id=campid).first()
        db.session.delete(campaign)
        db.session.commit()
        user_info=fetch_user_info(user_id)
        return redirect(url_for("influ_dash"))





@app.route("/influencer/request",methods=["GET","POST"])
# @spon_req
def req_influ():
    if request.method=="POST":
        user_id=session.get('user_id')
        uname=session.get('user_name')
        campid=request.form.get("campid")
        nte=request.form.get("note")
        print(nte)
        influid=request.form.get("influid")
        sponid=request.form.get("sponid")
        title=request.form.get('title')
        desciption=request.form.get("des")
        if not Campaign.query.get(campid):
            msg = "campaign is not valid"
            return redirect(url_for("spon_find"))
        campaign=CampaignRequest(note=nte,spon_id=sponid,influ_id=influid,campaign_id=campid,description=desciption,title=title,req_status_influ=0,influ_name=uname)
        db.session.add(campaign)
        db.session.commit()
        user_info=fetch_user_info(user_id)
        return redirect(url_for("spon_camp"))
    

@app.route("/campaign/com",methods=["GET","POST"])
# @spon_req
def camp_comple():
    if request.method=="POST":
        user_id=session.get('user_id')
        uname=session.get('user_name')
        cid=request.form.get("id")
        proof=request.form.get('description')
        if not CampaignRequest.query.get(cid):
            msg = "campaign is not valid"
            return redirect(url_for("influ_dash"))
        campaign = CampaignRequest.query.filter_by(id=cid).first()
        campaign.completed = 1
        campaign.chart = proof
        db.session.add(campaign)
        db.session.commit()
        campid=campaign.campaign_id
        camp=Campaign.query.filter_by(id=campid).first()
        camp.progress ="completed"
        camp.proof=proof
        db.session.add(camp)
        db.session.commit()
        user_info=fetch_user_info(user_id)
        return redirect(url_for("influ_dash"))


@app.route("/campaign/comver",methods=["GET","POST"])
# @spon_req
def camp_comple_ver():
    if request.method=="POST":
        user_id=session.get('user_id')
        crid=request.form.get("id")
        campid=request.form.get("id")
        proof=request.form.get('description')
        if not CampaignRequest.query.get(crid):
            msg = "campaign is not valid"
            return redirect(url_for("spon_dash"))
        campaign = CampaignRequest.query.filter_by(id=crid).first()
        campaign.completion_confirmed = 1
        db.session.add(campaign)
        db.session.commit()
        campid=campaign.campaign_id
        camp=Campaign.query.filter_by(id=campid).first()
        camp.progress ="Verified"
        db.session.add(camp)
        db.session.commit()
        user_info=fetch_user_info(user_id)
        return redirect(url_for("spon_dash"))
    

@app.route("/campaign/comverr",methods=["GET","POST"])
# @spon_req
def camp_comple_verr():
    if request.method=="POST":
        user_id=session.get('user_id')
        crid=request.form.get("id")
        campid=request.form.get("id")
        proof=request.form.get('description')
        if not CampaignRequest.query.get(crid):
            msg = "campaign is not valid"
            return redirect(url_for("spon_dash"))
        campaign = CampaignRequest.query.filter_by(id=crid).first()
        campaign.completed = 0
        db.session.add(campaign)
        db.session.commit()
        campid=campaign.campaign_id
        camp=Campaign.query.filter_by(id=campid).first()
        camp.progress ="accepted"
        db.session.add(camp)
        db.session.commit()
        user_info=fetch_user_info(user_id)
        return redirect(url_for("spon_dash"))


@app.route("/cam/rem",methods=["GET","POST"])
# @spon_req
def del_cam():
    id=request.form.get("id")
    camp =Campaign.query.get(id)
    print(camp)
    if camp:
        db.session.delete(camp)
        db.session.commit()
    campa = CampaignRequest.query.filter( CampaignRequest.campaign_id == id).all()
    if campa:
        for camp in campa:
            db.session.delete(camp)
            db.session.commit()
    return redirect(url_for("admin_dash"))



@app.route("/spon/rem",methods=["GET","POST"])
# @spon_req
def del_spon():
    sid=request.form.get("id")
    camp =Sponsor.query.filter(Sponsor.user_id==sid).first()
    db.session.delete(camp)
    db.session.commit()
    campai=User.query.filter(User.id==sid).first()
    db.session.delete(campai)
    db.session.commit()
    campa = CampaignRequest.query.filter( CampaignRequest.spon_id == sid).all()
    if campa:
        for cam in campa:
            db.session.delete(cam)
            db.session.commit()
    ca =Campaign.query.filter(Campaign.spon_id==sid).all()
    if ca:
        for c in ca:
            db.session.delete(c)
            db.session.commit()
    return redirect(url_for("admin_dash"))


@app.route("/influ/rem",methods=["GET","POST"])
# @spon_req
def del_influ():
    iid=request.form.get("id")
    camp =Influencer.query.filter(Influencer.user_id==iid).first()
    db.session.delete(camp)
    db.session.commit()
    campai=User.query.filter_by(id=iid).first()
    db.session.delete(campai)
    db.session.commit()
    campa = CampaignRequest.query.filter( CampaignRequest.influ_id == iid).all()
    if campa:
        for camp in campa:
            db.session.delete(camp)
            db.session.commit()
        ca = Campaign.query.filter( Campaign.id == camp.campaign_id).all()
        if ca:
            for c in ca:
                db.session.delete(c)
                db.session.commit()
    return redirect(url_for("admin_dash"))




@app.route("/sponsor/request",methods=["GET","POST"])
# @spon_req
def req_spon():
    if request.method=="POST":
        user_id=session.get('user_id')
        campid=request.form.get("campid")
        uname=session.get('user_name')
        influid=request.form.get("influid")
        ttle=request.form.get('title')
        fol=request.form.get('fol')
        note=request.form.get('note')
        desciption=request.form.get("description")
        buget=request.form.get('budget')
        if not Campaign.query.get(campid):
            msg = "campaign is not valid"
            return redirect(url_for("spon_find"))
        campaign = Campaign.query.get(campid)
        # Get the spon_id from the campaign
        spo_id = campaign.spon_id if campaign else None
        campaign=CampaignRequest(spon_id=spo_id,note=note,influ_id=influid,campaign_id=campid,description=desciption,title=ttle,budget=buget,req_status_spon=0,req_status_influ=1,influ_name=uname,influ_followers=fol)
        db.session.add(campaign)
        db.session.commit()
        user_info=fetch_user_info(user_id)
        return redirect(url_for("influ_find"))




# @app.route("/campaign/request",methods=["GET","POST"])
# def edit_cam0():
#     if request.method=="POST":
#         user_id=session.get('user_id')

#         db.session.commit()
#         user_info=fetch_user_info(user_id)
#         return redirect(url_for(spon_camp))




@app.route('/logout')
@auth_required
def logout():
    session.pop('user_id')
    session.pop('user_name')
    session.pop('role')
    return redirect(url_for('home'))



@app.route('/influ_dash')
@influ_requ
def influ_dash():
    infid = Influencer.query.filter_by(user_id=session['user_id']).first()
    campa = CampaignRequest.query.filter(CampaignRequest.influ_id ==session['user_id'], CampaignRequest.completed == 1,CampaignRequest.completion_confirmed == 1).all()
    comcampaigns = CampaignRequest.query.filter(CampaignRequest.influ_id ==session['user_id'], CampaignRequest.req_status_influ == 1, CampaignRequest.completed == 1,CampaignRequest.completion_confirmed == 0).all()
    campaigns = CampaignRequest.query.filter(CampaignRequest.influ_id ==session['user_id'], CampaignRequest.req_status_influ == 1, CampaignRequest.completed == 0).all()
    reuests=CampaignRequest.query.filter(CampaignRequest.influ_id ==session['user_id'], CampaignRequest.req_status_influ == 0).all()
    return render_template('influ_dash.html',camp=campa,comcamp=comcampaigns, campaigns=campaigns, requests=reuests,username=session['user_name'],id=session['user_id'])

@app.route('/influ_find')
@influ_requ
def influ_find():
    query=request.args.get('search')
    username=session.get('user_name')
    uid=session.get('user_id')
    print(uid)
    followe = Influencer.query.filter_by(user_id=uid).first()
    print(followe)
    follower=followe.followers
    # Get all campaigns
    all_campaigns = Campaign.query.filter(Campaign.progress == "Pending").all()
   # Get other campaigns
    other_campaigns = CampaignRequest.query.filter(CampaignRequest.influ_id == session.get('user_id')).all()
    # Extract the IDs of other campaigns
    other_campaign_ids = {campaign.campaign_id for campaign in other_campaigns}
    # Filter out other campaigns from all campaigns
    filtered_campaigns = [campaign for campaign in all_campaigns if campaign.id not in other_campaign_ids]
    if query:
        all_campaigns = Campaign.query.filter(Campaign.title.contains(query)).all()
        other_campaigns = CampaignRequest.query.filter(CampaignRequest.influ_id == session.get('user_id')).all()
        other_campaign_ids = {campaign.campaign_id for campaign in other_campaigns}
        filtered_campaigns = [campaign for campaign in all_campaigns if campaign.id not in other_campaign_ids]
    return render_template('influ_find.html', campaigns=filtered_campaigns,id=uid,uname=username,fol=follower)


@app.route('/spon_dash')
@spon_req
def spon_dash():
    user_id=session.get('user_name')
    comcampaigns = CampaignRequest.query.filter(CampaignRequest.spon_id == session['user_id'], CampaignRequest.completed == 1,CampaignRequest.completion_confirmed == 0).all()
    campa = Campaign.query.filter(Campaign.spon_id == session['user_id'],Campaign.progress == 'Verified').all()
    campaigns = Campaign.query.filter(Campaign.spon_id == session['user_id'],Campaign.progress == 'accepted').all()
    campaign =  Campaign.query.filter(Campaign.spon_id == session['user_id'],Campaign.progress == 'Pending').all()
    requests_by_spon_id = CampaignRequest.query.filter(CampaignRequest.spon_id == session['user_id']).all()
    requests_by_status = CampaignRequest.query.filter(CampaignRequest.req_status_spon == 0).all()
    intersected_requests = [req for req in requests_by_spon_id if req in requests_by_status]
    return render_template('spon_dash.html',camp=campa,comcamp=comcampaigns,username=user_id, accepted_campaigns=campaigns,active_campaigns=campaign, new_requests=intersected_requests)

@app.route('/spon_find')
@spon_req
def spon_find():
    query=request.args.get('search')
    username=session.get('user_name')
    uid=session.get('user_id')
    other_campaigns = Campaign.query.filter(Campaign.spon_id != session.get('user_id')).all()
    if query:
        other_campaigns = Campaign.query.filter(Campaign.title.contains(query)).all()
    influ=Influencer.query.all()
    return render_template('spon_find.html', campaigns=other_campaigns, influencer=influ,uname=username,id=uid)

@app.route('/spon_find_inlfu')
@spon_req
def spon_find_influ():
    title=request.args.get('tit')
    cid=request.args.get('id')
    des=request.args.get('des')
    username=session.get('user_name')
    id=session.get('user_id')
    influ=Influencer.query.all()
    return render_template('spon_find_influ.html',des=des,  influencer=influ,uname=username,uid=id,tit=title,capid=cid)

@app.route('/spon_camp')
def spon_camp():
    query=request.args.get('search')
    user_id=session.get('user_id')
    other_campaigns = Campaign.query.filter(Campaign.spon_id == session.get('user_id')).all()
    if query:
        other_campaigns = Campaign.query.filter(Campaign.title.contains(query)).all()
    return render_template('spon_camp.html', campaigns=other_campaigns)

@app.route('/admin_dash')
def admin_dash():
    user=session.get('user_name')
    camps = Campaign.query.filter_by(flagged=0).all()
    campaign = Campaign.query.filter_by(flagged=1).all()
    influ = Influencer.query.filter_by(flagged=1).all()
    Sponso = Sponsor.query.filter_by(flagged=1).all()
    return render_template('admin_dash.html',name=user, campaigns=camps, flaggedinflu=influ,flaggedspon=Sponso,flaggedcamp=campaign)

@app.route('/admin_find')
@admin_req
def admin_find():
    user=session.get('user_name')
    campaigns = Campaign.query.filter_by(flagged=0).all()
    influ=Influencer.query.filter_by(flagged=0).all()
    spon=Sponsor.query.filter_by(flagged=0).all()
    return render_template('admin_find.html',name=user, campaigns=campaigns,influencer=influ,sponsor=spon)










































































ROOT_DIR = os.path.realpath(os.path.join(os.path.abspath(os.path.dirname(__file__)), '../static/img'))


# Plot for Platform vs Number of Followers
def platform_vs_followers_plot():
    platform_followers = db.session.execute(
        select(Influencer.platform, func.sum(Influencer.followers).label('total_followers'))
        .group_by(Influencer.platform)
    ).all()
    
    platforms = [str(t.platform) for t in platform_followers]
    total_followers = [t.total_followers for t in platform_followers]

    print(platforms)
    print(total_followers)
    print(platform_followers)
    print(os.path.join(ROOT_DIR, 'platform_vs_followers.png'))
    total_followers=np.array(total_followers)
    plt.figure(figsize=(10, 6))
    plt.ylabel('Platforms')
    plt.xlabel('Total Followers')
    plt.barh(platforms, total_followers, color='skyblue')
    img_dir = os.path.join(os.path.abspath(os.path.dirname(__file__)), '../static/img')
    plt.savefig('static/img/platform_vs_followers.png')



# Plot for Number of Influencers vs Number of Sponsors
def influencers_vs_sponsors_plot():
    roles_count = db.session.execute(
        select(User.role, func.count(User.id).label('count'))
        .group_by(User.role)
    ).all()
    
    roles = [str(t.role) for t in roles_count]  # Capitalize roles for better display
    counts = [t.count for t in roles_count]

    print(roles)
    print(counts)
    print(roles_count)
    
    plt.figure(figsize=(8, 6))
    plt.ylabel('Role')
    plt.xlabel('Number of Users')
    plt.barh(roles, counts, color='lightcoral')
    img_dir = os.path.join(os.path.abspath(os.path.dirname(__file__)), '../static/img')
    plt.savefig( 'static/img/influencers_vs_sponsors.png')

# Plot for Top 5 Campaigns Based on Budget
def top_campaigns_by_budget_plot():
    top_campaigns = db.session.execute(
        select(Campaign.title, Campaign.budget)
        .order_by(Campaign.budget.desc())
        .limit(5)
    ).all()
    
    titles = [t.title for t in top_campaigns]
    budgets = [t.budget for t in top_campaigns]
    
    plt.figure(figsize=(10, 6))
    plt.ylabel('Campaign Titles')
    plt.xlabel('Budget')
    plt.barh(titles, budgets, color='seagreen')
    img_dir = os.path.join(os.path.abspath(os.path.dirname(__file__)), '../static/img')
    plt.savefig( 'static/img/top_campaigns_by_budget.png')




@app.route('/summary')
def summary():
    platform_vs_followers_plot()  # Plot for Platform vs Number of Followers
    influencers_vs_sponsors_plot()  # Plot for Number of Influencers vs Number of Sponsors
    top_campaigns_by_budget_plot()  # Plot for Top 5 Campaigns Based on Budget
    
    return render_template('admin/summary.html')





















'''
@app.route("/campaignreq/flag/<int:id>", methods=["POST"])
def flag_campaign(id):
    title = request.form.get("title")
    reason = request.form.get("reason")

    if not title or not reason:
        return render_template("spon_camp.html", id=id, msg="Please fill out all fields!")

    # Here, you would add code to process the flagging, e.g., saving the reason to the database.
    # Example:
    flag_entry = (title=title, reason=reason, campaign_id=id)
    db.session.add(flag_entry)
    db.session.commit()

    # Return to the same page or redirect as needed
    return render_template("spon_camp.html", id=id, msg="Campaign flagged successfully!")
'''


'''


@app.route('/campaigns/add')
@sponsor_required
def add_Campaigns():
    return render_template('campaigns/add.html',user=User.query.get(session['user']))

@app.route('/campaigns/add', methods=['POST'])
@sponsor_required
def add_campaigns_post():
    name=request.form.get('name')
    budget=request.form.get('budget')
    title =request.form.get('title')
    niche=request.form.get('niche')
    descripton= request.form.get('descript')
    if name==''or budget=='' or descripton=='' or title=='' or niche=='' :
        flash('Please fill out all fields')
        return redirect(url_for('add_campaigns'))
    name = Campaign(name=name)
    db.session.add(name)
    budget = Campaign(budget=budget)
    db.session.add(budget)
    title = Campaign(title=title)
    db.session.add(title)
    niche = Campaign(niche=niche)
    db.session.add(niche)
    description = Campaign(description=descripton)
    db.session.add(description)
    db.session.commit()
    flash('Campaign created successfully')
    return redirect(url_for('sponsorcampaigns'))

    



'''