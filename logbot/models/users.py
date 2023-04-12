import datetime
from mongoengine import ( Document, StringField, EmailField, DateTimeField,)
from flask_bcrypt import generate_password_hash, check_password_hash


class Users(Document):
    """
    Template for a mongoengine document, which represents a user.
    Password is automatically hashed before saving.
    :param email: unique required email-string value
    :param password: required string value, longer than 6 characters
    :param name: option unique string username
    """
    user_id  = StringField(required=True,unique=True)
    email = EmailField(required=True, unique=True)
    password = StringField(required=True, min_length=6, regex=None)
    name = StringField(unique=False)
    timestamp = DateTimeField(default=datetime.datetime.utcnow)
    
    
    def __repr__(self):
        return '<User(name={self.name!r})>'.format(self=self)

    @classmethod
    def generate_pw_hash(cls, self):
        """
        Generate a hash for the password
        """
        self.password = generate_password_hash(password=self.password).decode('utf-8')
    
    #BCrypt for password hashing
    generate_pw_hash.__doc__ = generate_password_hash.__doc__

    @classmethod
    def check_pw_hash(cls, self, password: str) -> bool:
        """
        Check/Validate provided password hash
        """
        return check_password_hash(pw_hash=self.password, password=password)

    #BCrypt for password hashing
    check_pw_hash.__doc__ = check_password_hash.__doc__

    def save(self, *args, **kwargs):
        # Overwrite Document save method to generate password hash prior to saving
        if self._created:
            self.generate_pw_hash(self)
        super(Users, self).save(*args, **kwargs)
