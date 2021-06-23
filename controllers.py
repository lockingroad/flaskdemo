from models import User, db


class UsersDao():
    def create_user(self, name, pswd):
        new_user = User(name=name, pswd=pswd)
        db.session.add(new_user)
        db.session.commit()
        return new_user

    def update_user(self, user):
        modified_user = User.query.get(user.id)
        modified_user.name = user.name
        modified_user.pswd = user.pswd
        modified_user.like = user.like
        modified_user.dislike = user.dislike
        db.session.commit()
        return modified_user

    def delete_user(self, user):
        delete_user = User.query.get(user.id)
        db.session.delete(delete_user)
        db.session.commit()
        return True

    def list_user(self):
        return User.query.all()

    def get_user(self, name):
        return User.query.filter_by(name=name).first()
