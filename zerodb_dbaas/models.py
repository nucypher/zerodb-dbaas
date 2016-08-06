from zerodb.models import Model, Field


def make_app(db):
    return db


class UserRegistration(Model):
    email = Field()      # str
    created = Field()    # datetime
    activated = Field()  # datetime
    hashcode = Field()   # str
    # also have password_hash (not indexed)

    def __repr__(self):
        return "<UserRegistration %s>" % (self.email,)
