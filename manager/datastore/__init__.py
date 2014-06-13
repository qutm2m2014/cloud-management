from flask.ext.sqlalchemy import SQLAlchemy
from sqlalchemy import not_
import datetime
from flask import json
import uuid

db = SQLAlchemy()


class DateBaseModel():
    dt_created = db.Column('dt_created', db.DateTime, default=datetime.datetime.utcnow(), nullable=False)
    dt_updated = db.Column('dt_updated', db.DateTime, default=datetime.datetime.utcnow(), onupdate=datetime.datetime.utcnow(), nullable=False)


class BaseModel(db.Model):
    """Abstract Base Model
    """

    __abstract__ = True
    _overwrite_columns = True

    def __init__(self, **kwargs):
        self._set_columns(**kwargs)

    def _set_columns(self, **kwargs):
        for key in self.__table__.columns.keys():
            if key in kwargs and (self._overwrite_columns or not getattr(self, key)):
                setattr(self, key, kwargs[key])
        for rel in self.__mapper__.relationships.keys():
            if rel in kwargs:
                if self.__mapper__.relationships[rel].uselist:
                    valid_ids = []
                    query = getattr(self, rel)
                    cls = self.__mapper__.relationships[rel].argument()
                    if 'id' in kwargs[rel]:
                        query.filter_by(id=kwargs[rel]['id']).update(kwargs[rel])
                        valid_ids.append(kwargs[rel]['id'])
                    else:
                        col = cls()
                        col.set_columns(**kwargs[rel])
                        query.append(col)
                        db.session.flush()
                        valid_ids.append(col.id)

                    # delete related rows that were not in kwargs[rel]
                    query.filter(not_(cls.id.in_(valid_ids))).delete()

                else:
                    col = getattr(self, rel)
                    col.set_columns(**kwargs[rel])

    def set_columns(self, **kwargs):
        self._set_columns(**kwargs)
        if 'dt_updated' in self.__table__.columns:
            self.dt_updated = datetime.utcnow()

    def __repr__(self):
        if 'id' in self.__table__.columns.keys():
            return '%s(%s)' % (self.__class__.__name__, self.id)
        data = {}
        for key in self.__table__.columns.keys():
            val = getattr(self, key)
            if type(val) is datetime:
                val = val.strftime('%Y-%m-%dT%H:%M:%SZ')
            data[key] = val
        return json.dumps(data)

    def to_dict(self, show=[], hide=[], path=None, replace={}):

        data = {}
        if not path:
            path = self.__tablename__.lower()

            def prepend_path(item):
                item = item.lower()
                if item.split('.', 1)[0] == path:
                    return item
                if len(item) == 0:
                    return item
                if item[0] != '.':
                    item = '.%s' % item
                item = '%s%s' % (path, item)
                return item
            show[:] = [prepend_path(x) for x in show]
            hide[:] = [prepend_path(x) for x in hide]

        # Display table attributes
        for key in self.__table__.columns.keys():
            check = '%s.%s' % (path, key)
            if check not in hide and (key == 'id' or check in show):
                value = getattr(self, key)
                if hasattr(value, 'isoformat'):
                    value = value.isoformat()
                elif isinstance(value, datetime.datetime) or isinstance(value, datetime.date):
                    value = value.strftime('%Y-%m-%dT%H:%M:%S')
                elif isinstance(value, uuid.UUID):
                    print "UUID"
                    value = value.hex
                data[key] = value

        # Display relationships
        for key in self.__mapper__.relationships.keys():
            check = '%s.%s' % (path, key)
            if check not in hide and check in show:
                if self.__mapper__.relationships[key].uselist:
                    data[key] = []
                    for item in getattr(self, key):
                        data[key].append(item.to_dict(
                            show=list(show),
                            hide=list(hide),
                            path=('%s.%s' % (path, key.lower())),
                        ))
                else:
                    data[key] = getattr(self, key)

        for key in replace.keys():
            data[key] = replace[key]

        return data
