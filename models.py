from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash,check_password_hash
db = SQLAlchemy()

'''
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(20), nullable=False)

    def check_password(self, password):
        return check_password_hash(self.passhash, password)
    
    influencers = db.relationship('Influencer', back_populates='user', uselist=False)
    sponsors = db.relationship('Sponsor', back_populates='user', uselist=False)
    campaigns = db.relationship('Campaign', back_populates='user')
    'campaign_requests = db.relationship('CampaignRequest', back_populates='user')'

class Influencer(db.Model):
    __tablename__ = 'influencers'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True, nullable=False)
    name=user_id = db.Column(db.String(30), db.ForeignKey('users.username'), unique=True, nullable=False)
    platform = db.Column(db.String(50),nullable=False)
    followers = db.Column(db.Integer)

    user = db.relationship('User', back_populates='influencers')
    'campaigns = db.relationship('Campaign', back_populates='Influencer')'
    'campaign_requests = db.relationship('CampaignRequest', back_populates='influencer')'
    campaigns = db.relationship('Campaign', back_populates='influencer')  # Ensure relationship name matches the foreign key




class Influencer(db.Model):
    __tablename__ = 'influencers'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)  # Changed from referencing users.username to a separate string column
    platform = db.Column(db.String(50), nullable=False)
    followers = db.Column(db.Integer)

    user = db.relationship('User', back_populates='influencers')
    campaigns = db.relationship('Campaign', back_populates='influencer')  # Ensure relationship name matches the foreign key






class Sponsor(db.Model):
    __tablename__ = 'sponsors'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True, nullable=False)
    industry = db.Column(db.String(100),nullable=False)

    user = db.relationship('User', back_populates='sponsors')
    campaigns = db.relationship('Campaign', back_populates='sponsor')
    'campaign_requests = db.relationship('CampaignRequest', back_populates='sponsor')'

class Campaign(db.Model):
    __tablename__ = 'campaigns'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(30), nullable=False)
    description = db.Column(db.String(300),nullable=False)
    end_date = db.Column(db.DateTime, nullable=False) 
    budget = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    influ_id = db.Column(db.Integer, db.ForeignKey('influencers.id'), nullable=True)  # Added foreign key to influencers
    spon_id = db.Column(db.Integer, db.ForeignKey('sponsors.id'), nullable=True)
    flagged = db.Column(db.Boolean, nullable=False, default=False)
    progress = db.Column(db.String(20), nullable=False, default='Pending')
    flag = db.Column(db.Integer, nullable=False, default=0)

    user = db.relationship('User', back_populates='campaigns')
    Influencer = db.relationship('Influencer', back_populates='campaigns')
    sponsor = db.relationship('Sponsor', back_populates='campaigns')
    'campaign_requests = db.relationship('CampaignRequest', back_populates='campaign')'

class CampaignRequest(db.Model):
    __tablename__ = 'campaign_requests'
    id = db.Column(db.Integer, primary_key=True)
    campaign_id = db.Column(db.Integer, db.ForeignKey('campaigns.id'), nullable=False)
    influ_id = db.Column(db.Integer, db.ForeignKey('influencers.id'), nullable=False)
    spon_id = db.Column(db.Integer, db.ForeignKey('sponsors.id'), nullable=False)
    budget = db.Column(db.Float, nullable=False)
    title = db.Column(db.String(32), nullable=False)
    status = db.Column(db.String(80), nullable=False)
    completed = db.Column(db.Boolean, nullable=False, default=False)
    completion_confirmed = db.Column(db.Boolean, nullable=False, default=False)
    rating_done = db.Column(db.Boolean, nullable=False, default=False)

    'campaign = db.relationship('Campaign', back_populates='campaign_requests')'
   ' influencer = db.relationship('Influencer', back_populates='campaign_requests')'
    'sponsor = db.relationship('Sponsor', back_populates='campaign_requests')'
    'user = db.relationship('User', back_populates='campaign_requests')'

'''

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(20), nullable=False)
    
    #campaigns = db.relationship('Campaign', back_populates='user')

class Influencer(db.Model):
    __tablename__ = 'influencers'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True, nullable=False)
    name = db.Column(db.String(100))  # A separate string column, not a foreign key to 'username'
    platform = db.Column(db.String(50), nullable=False)
    followers = db.Column(db.Integer)
    flagged = db.Column(db.Boolean,default=False)

class Sponsor(db.Model):
    __tablename__ = 'sponsors'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True, nullable=False)
    industry = db.Column(db.String(100), nullable=False)
    name = db.Column(db.String(100))
    flagged = db.Column(db.Boolean,default=False)
    #campaigns = db.relationship('Campaign', backref='spon_id')

class Campaign(db.Model):
    __tablename__ = 'campaigns'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(30), nullable=False)
    description = db.Column(db.String(300), nullable=False)
    end_date = db.Column(db.String, nullable=False)
    budget = db.Column(db.Integer, nullable=False)
    spon_id = db.Column(db.Integer, db.ForeignKey('sponsors.id'), nullable=False)
    # influ_id = db.Column(db.Integer) #db not updated yet
    proof=db.Column(db.String)
    flagged = db.Column(db.Boolean, nullable=False, default=False)
    progress = db.Column(db.String(20), nullable=False, default='Pending')



class CampaignRequest(db.Model):
    __tablename__ = 'campaign_requests'
    id = db.Column(db.Integer, primary_key=True)
    campaign_id = db.Column(db.Integer, db.ForeignKey('campaigns.id'), nullable=False)
    influ_id = db.Column(db.Integer, db.ForeignKey('influencers.id'))
    spon_id = db.Column(db.Integer, db.ForeignKey('sponsors.id'), nullable=False)
    req_status_influ = db.Column(db.Boolean)
    req_status_spon = db.Column(db.Boolean)
    budget = db.Column(db.Integer, nullable=True)
    end_date = db.Column(db.String, nullable=True)
    influ_name = db.Column(db.String)
    influ_followers = db.Column(db.Integer)
    note = db.Column(db.String)
    
    completed = db.Column(db.Boolean, nullable=False, default=False)
    completion_confirmed = db.Column(db.Boolean, nullable=False, default=False)
    title=db.Column(db.String)
    description=db.Column(db.String)
    chart=db.Column(db.String)
