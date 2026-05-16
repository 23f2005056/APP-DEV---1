# Influencer Engagement & Sponsorship Coordination Platform

## Overview
The Influencer Engagement & Sponsorship Coordination Platform is a full-stack web application that connects Sponsors and Influencers for managing advertising campaigns and sponsorship collaborations. Sponsors can create campaigns, search for influencers, and send ad requests, while influencers can discover campaigns, negotiate sponsorships, and manage collaborations.

---

## Features

### Admin
- Monitor users, campaigns, and ad requests
- View platform statistics
- Flag inappropriate users or campaigns

### Sponsors
- Create, edit, and delete campaigns
- Search influencers based on niche and reach
- Send and manage ad requests
- Track campaign progress

### Influencers
- View public campaigns
- Accept or reject ad requests
- Negotiate sponsorship payment
- Update public profile

---

## Tech Stack

### Backend
- Python
- Flask
- Flask-SQLAlchemy
- SQLite

### Frontend
- HTML5
- CSS3
- Bootstrap
- Jinja2 Templates

### Additional Tools
- JavaScript

---

## Project Structure

```bash
project-root/
│
├── app.py / main.py
├── models.py
├── requirements.txt
├── static/
│   ├── css/
│   ├── js/
│   └── images/
│
├── templates/
│   ├── admin/
│   ├── sponsor/
│   ├── influencer/
│   └── campaign/
│
└── README.md




---

## Execution Steps

### Create Virtual Environment

```bash
python -m venv env
```

### Activate Virtual Environment

#### Windows
```bash
env\Scripts\activate
```

#### Linux / Mac
```bash
source env/bin/activate
```

### Install Required Dependencies

```bash
pip install -r requirements.txt
```

### Run the Application

```bash
python app.py
```

---
