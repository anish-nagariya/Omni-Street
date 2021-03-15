# OmniZero-Stock-Prediction

Stock Prediction UI for OMNI Zero Project

## Prerequisites

Install the following before build.

1. Docker - <https://docs.docker.com/docker-for-windows/install/>
2. Python - <https://www.python.org/downloads/>
3. MongoDBCompass - <https://www.mongodb.com/try/download/compass>
4. node.js - <https://nodejs.org/en/download/>

## To build and run in development

Open **cmd** and navigate to project root folder. Use the following command

```cmd
docker-compose up --build -d
```

Navigate to <http://localhost:3000/> to check Angular App
Navigate to <http://localhost:5000/api> to check API
Use MongoDBCompass with the following connection string <mongodb://admin:password@localhost:27017/omnidb?authSource=admin&readPreference=primary&appname=MongoDB%20Compass&ssl=false>

## To build and run in production

Open **cmd** and navigate to project root folder. Use the following command

```cmd
docker-compose -f docker-compose.prod.yml up --build -d
```

Navigate to <http://localhost/> to check Angular App
Navigate to <http://localhost/api> to check Angular App

### Initial Commands to have MongoDB accept the api server

1. First, open the mongodb container in a new interactive shell.

```cmd
docker exec -it mongo bash
```

2. Login to the MongoDB root user account. Enter the admin password when prompted.

```cmd
mongo -u admin -p
```

3. Tell MongoDB which database we want to use.

```cmd
use omnidb
```

4. Create a non-root user with read & write permissions in the omnidb database.

```cmd
db.createUser({user: 'apiuser', pwd: 'apipassword', roles: [{role: 'readWrite', db: 'omnidb'}]})
```
