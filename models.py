from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True, index=True)
    pswd = db.Column(db.String(64))
    like = db.Column(db.String(64))
    state = db.Column(db.String(64))
    dislike = db.Column(db.String(64))

    def __repr__(self):
        return 'User:%s' % self.name


class NewUser(db.Model):
    __tablename__ = 'newusers'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True, index=True)
    pswd = db.Column(db.String(64))
    like = db.Column(db.String(64))
    state = db.Column(db.String(64))
    dislike = db.Column(db.String(64))

    def __repr__(self):
        return 'User:%s' % self.name


class Address(db.Model):
    __tablename__ = 'address'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    user = db.relationship("User", backref="address_of_company")
    name = db.Column(db.String(64))

    def to_json(self):
        dict = self.__dict__

        if "_sa_instance_state" in dict:
            del dict["_sa_instance_state"]
        return dict


class NoFAddress(db.Model):
    __tablename__ = 'nofaddress'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    name = db.Column(db.String(64))

    def to_json(self):
        dict = self.__dict__

        if "_sa_instance_state" in dict:
            del dict["_sa_instance_state"]
        return dict
