from zerodb.models import Model, Field


class Counter(Model):
    name = Field()
    count = Field()

    def __repr__(self):
        return "<Counter %s %s>" % (self.name, self.count)

    def inc(self):
        self.count += 1


def make_app(db):
    num = len(db[Counter])
    if num < 1:
        c = Counter(name='root', count=0)
        db.add(c)
        import transaction
        transaction.commit()
    return db


class UserRegistration(Model):
    email = Field()
    created = Field()
    completed = Field()
    hashcode = Field()

    def __repr__(self):
        return "<UserRegistration %s>" % (self.username,)
