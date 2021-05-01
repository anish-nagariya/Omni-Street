// use shell command to save env variable to a temporary file, then return the contents.
// source: https://stackoverflow.com/questions/39444467/how-to-pass-environment-variable-to-mongo-script/60192758#60192758
function getEnvVariable(envVar, defaultValue) {
    var command = run("sh", "-c", `printenv --null ${ envVar } >/tmp/${ envVar }.txt`);
    // note: 'printenv --null' prevents adding line break to value
    if (command != 0) return defaultValue;
    return cat(`/tmp/${ envVar }.txt`)
  }

var dbName = getEnvVariable('MONGO_INITDB_DATABASE', 'omnidb');
db = db.getSiblingDB(dbName);
db.createUser({user: 'apiuser', pwd: 'apipassword', roles: [{role: 'readWrite', db: 'omnidb'}]});
