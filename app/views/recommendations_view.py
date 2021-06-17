import uuid
from app import app, db
from app.views.authorization import token_required
from flask import jsonify, request
from flask.helpers import make_response
from app.model import User, AddedUser, Teammate

@app.route('/recommendations/follow/', methods=['POST'])
@token_required
def follow():
    user_id = request.args.get('user_id')
    data = request.get_json()
    followed_user_id = data.get('added_user_id')

    if not user_id or not data or not followed_user_id:
        make_response('Bad request', 400)

    added_users = AddedUser.query.filter_by(user_id=followed_user_id).all()

    # if both users follow each other add them as teammates
    if added_users:
        for u in added_users:
            if u.followed_user_id == user_id:
                
                # add teammate entry for both of the users
                follower_teammate = Teammate(id=str(uuid.uuid4()), user_id=user_id, teammate_id=followed_user_id)
                followed_teammate = Teammate(id=str(uuid.uuid4()), user_id=followed_user_id, teammate_id=user_id)

                # remove added_user entry from followed user's list
                added_user_entry = AddedUser.query.filter_by(followed_user_id=user_id).first()
                db.session.delete(added_user_entry)

                # add teammate entries to database
                db.session.add(follower_teammate)
                db.session.add(followed_teammate)
                db.session.commit()

                response = make_response('Users are now teammates', 200)
                response.headers['X-Teammates']='true'
                return response

    # if followed user didnt add current user before, add added_user entry to the database
    added_user = AddedUser(id=str(uuid.uuid4()), user_id=user_id, followed_user_id=followed_user_id)
    
    db.session.add(added_user)
    db.session.commit()

    response = make_response('Users are now teammates', 200)
    response.headers['X-Teammates']='false'
    return response
    

