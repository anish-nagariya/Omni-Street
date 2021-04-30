setx MONGODB_HOSTNAME "localhost"
setx MONGODB_DATABASE "omnidb"
setx MONGODB_USERNAME ""
setx MONGODB_PASSWORD ""
setx FLASK_ENV "development"
setx JWT_SECRET_KEY "omni-street-jwt-secret-key"
setx MODEL_PATH "Models/"
setx AI_API_KEY "c0opefv48v6rduk5oegg"
setx API_KEY "mB9dUbVRc7Qq7rvvGX5bbBsuTuq2f9Y6"
setx CELERY_BROKER_URL "redis://localhost:6379/0"
setx CELERY_RESULT_BACKEND "redis://localhost:6379/0"
setx RESET_TOKEN "3030207007026787"
setx FLASK_DEBUG 1

celery --app=tasks.celery worker -E --loglevel=debug