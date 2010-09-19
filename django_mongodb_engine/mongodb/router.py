
class MongoDBRouter(object):
    """A router to control all database operations on models in
    the myapp application"""
    def __init__(self):
        from django.conf import settings
        self.managed_apps = [app.split('.')[-1] for app in getattr(settings, "MONGODB_MANAGED_APPS", [])]
        self.managed_models = getattr(settings, "MONGODB_MANAGED_MODELS", [])
        self.mongodb_database = None
        self.mongodb_databases = []
        
        for name, databaseopt in settings.DATABASES.items():
            if databaseopt["ENGINE"]=='django_mongodb_engine.mongodb':
                if databaseopt.get("IS_DEFAULT", False) and not self.mongodb_database:
                    self.mongodb_database = name
                elif databaseopt.get("IS_DEFAULT", False) and self.mongodb_database:
                    raise RuntimeError("There can be just one mongodb default db")
                
                self.mongodb_databases.append(name)
                
        if self.mongodb_database is None and not self.mongodb_databases:
            raise RuntimeError("A mongodb database must be set")
        self.mongodb_database = self.mongodb_databases[0]

    def db_for_read(self, model, **hints):
        "Point all operations on mongodb models to a mongodb database"
        if model._meta.app_label in self.managed_apps:
            return self.mongodb_database
        key = "%s.%s"%(model._meta.app_label, model._meta.module_name)
        if key in self.managed_models:
            return self.mongodb_database
        return None

    def db_for_write(self, model, **hints):
        "Point all operations on mongodb models to a mongodb database"
        if model._meta.app_label in self.managed_apps:
            return self.mongodb_database
        key = "%s.%s"%(model._meta.app_label, model._meta.module_name)
        if key in self.managed_models:
            return self.mongodb_database
        return None

    def allow_relation(self, obj1, obj2, **hints):
        "Allow any relation if a model in myapp is involved"

        #key1 = "%s.%s"%(obj1._meta.app_label, obj1._meta.module_name)
        key2 = "%s.%s"%(obj2._meta.app_label, obj2._meta.module_name)

        # obj2 is the model instance so, mongo_serializer should take care
        # of the related object. We keep trac of the obj1 db so, don't worry
        # about the multi-database management
        if obj2._meta.app_label in self.managed_apps or key2 in self.managed_models:
            return True

        return None

    def allow_syncdb(self, db, model):
        "Make sure that a mongodb model appears on a mongodb database"
        key = "%s.%s"%(model._meta.app_label, model._meta.module_name)
        if db in self.mongodb_databases:
            return model._meta.app_label  in self.managed_apps or key in self.managed_models
        elif model._meta.app_label in self.managed_apps or key in self.managed_models:
            if db in self.mongodb_databases:
                return True
            else:
                return False
        return None

    def valid_for_db_engine(self, driver, model):
        "Make sure that a model is valid for a database provider"
        if driver!="mongodb":
            return None
        if model._meta.app_label in self.managed_apps:
            return True
        key = "%s.%s"%(model._meta.app_label, model._meta.module_name)
        if key in self.managed_models:
            return True
        return None
        
