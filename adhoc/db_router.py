from .settings import DB_ALIAS

ADHOC_APP_LABEL = 'adhoc'


class AdhocRouter(object):
    """Routes all adhoc_* tables to the database referenced by ADHOC_DB_ALIAS,
       so that adhoc content can be kept in a separate database."""
    
    def db_for_read(self, model, **hints):
        if model._meta.app_label == ADHOC_APP_LABEL:
            return DB_ALIAS
        return None

    def db_for_write(self, model, **hints):
        if model._meta.app_label == ADHOC_APP_LABEL:
            return DB_ALIAS
        return None

    def allow_relation(self, obj1, obj2, **hints):
        if obj1._meta.app_label == ADHOC_APP_LABEL or \
           obj2._meta.app_label == ADHOC_APP_LABEL:
           return True
        return None

    def allow_migrate(self, db, model):
        if db == DB_ALIAS:
            return model._meta.app_label == ADHOC_APP_LABEL
        elif model._meta.app_label == ADHOC_APP_LABEL:
            return False
        return None
