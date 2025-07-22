from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json

# Create the SQLAlchemy instance
db = SQLAlchemy()

class User(db.Model):
    """Represents a user in the database."""
    __tablename__ = 'users'
    user_id = db.Column(db.String, primary_key=True)
    profile_data = db.Column(db.JSON)

def create_user(profile):
    """Creates a new user in the database."""
    profile['interaction_history']['last_interaction'] = datetime.utcnow().isoformat()
    new_user = User(user_id=profile['user_id'], profile_data=profile)
    db.session.add(new_user)
    db.session.commit()

def get_user(user_id):
    """Retrieves a user's profile from the database."""
    user = User.query.get(user_id)
    if user:
        return user.profile_data
    return None

def update_user(user_id, profile):
    """Updates an existing user's profile."""
    user = User.query.get(user_id)
    if user:
        profile['interaction_history']['last_interaction'] = datetime.utcnow().isoformat()
        profile['interaction_history']['total_interactions'] = profile['interaction_history'].get('total_interactions', 0) + 1
        user.profile_data = profile
        db.session.commit()