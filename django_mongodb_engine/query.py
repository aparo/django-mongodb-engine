from djangotoolbox.fields import AbstractIterableField, EmbeddedModelField

class A(object):
    def __init__(self, op, value):
        self.op = op
        self.val = value

    def as_q(self, field):
        if isinstance(field, (AbstractIterableField, EmbeddedModelField)):
            return "%s.%s" % (field.attname, self.op), self.val
        else:
            raise TypeError("Can not use A() queries on %s" % field.__class__.__name__)
