from .settings import DB_ALIAS

CMS_APP_LABEL = 'cms'


class CMSRouter(object):
    def db_for_read(self, model, **hints):
        # print '>>>', model
        if model._meta.app_label == CMS_APP_LABEL:
            return DB_ALIAS
        return None

    def db_for_write(self, model, **hints):
        if model._meta.app_label == CMS_APP_LABEL:
            return DB_ALIAS
        return None

    def allow_relation(self, obj1, obj2, **hints):
        if obj1._meta.app_label == CMS_APP_LABEL or \
           obj2._meta.app_label == CMS_APP_LABEL:
           return True
        return None

    def allow_migrate(self, db, model):
        # print db, model
        if db == DB_ALIAS:
            # print model._meta.app_label == CMS_APP_LABEL
            return model._meta.app_label == CMS_APP_LABEL
        elif model._meta.app_label == CMS_APP_LABEL:
            return False
        return None