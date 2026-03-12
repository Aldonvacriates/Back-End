class DevelopmentConfig:
    SQLALCHEMY_DATABASE_URI = "mysql+mysqlconnector://root:Lolita1!@localhost/library_db"
    DEBUG = True
    RATELIMIT_STORAGE_URI = "memory://"

class TestingConfig:
    pass

class ProductionConfig:
    pass
