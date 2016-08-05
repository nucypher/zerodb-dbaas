from zerodb.models import Model, Field


def make_app(db):
    num = len(db[Counter])
    if num < 1:
        c = Counter(name='root', count=0)
        db.add(c)
        import transaction
        transaction.commit()
    return db


class UserRegistration(Model):
    email = Field()      # str
    created = Field()    # datetime
    activated = Field()  # datetime
    hashcode = Field()   # str
    # also have password_hash (not indexed)

    def __repr__(self):
        return "<UserRegistration %s>" % (self.email,)
