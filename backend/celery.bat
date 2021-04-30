setlocal
Set MONGODB_HOSTNAME="localhost"
Set MONGODB_DATABASE="omnidb"
Set MONGODB_USERNAME=""
Set MONGODB_PASSWORD=""
Set FLASK_ENV="development"
Set JWT_SECRET_KEY="omni-street-jwt-secret-key"
Set MODEL_PATH="Models/"
Set AI_API_KEY="c0opefv48v6rduk5oegg"
Set API_KEY="mB9dUbVRc7Qq7rvvGX5bbBsuTuq2f9Y6"
Set CELERY_BROKER_URL="redis://localhost:6379/0"
Set CELERY_RESULT_BACKEND="redis://localhost:6379/0"
Set RESET_TOKEN="3030207007026787"
Set FLASK_DEBUG=1
endlocal

celery --app=tasks.celery worker -E --loglevel=debug