from flask import session
from your_app.models import User

def get_current_user():
    user_id = session.get('user_id')
    if not user_id:
        return None  # Or redirect to login / handle anonymous users
    
    user = User.query.get(user_id)
    return user