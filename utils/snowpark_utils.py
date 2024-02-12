from snowflake.snowpark import Session
import os
from typing import Optional

# Class to store a singleton connection option
class SnowflakeConnection(object):
    _connection = None

    @property
    def connection(self) -> Optional[Session]:
        return type(self)._connection

    @connection.setter
    def connection(self, val):
        type(self)._connection = val

# Function to return a configured Snowpark session
def get_snowpark_session() -> Session:
    # if running in snowflake
    if SnowflakeConnection().connection:
        # Not sure what this does?
        session = SnowflakeConnection().connection
    # if running locally with a config file
    # TODO: Look for a creds.json style file. This should be the way all snowpark
    # related tools work IMO
    # if using snowsql config, like snowcli does
    elif os.path.exists(os.path.expanduser('~/.snowsql/config')):
        snowpark_config = get_snowsql_config()
        SnowflakeConnection().connection = Session.builder.configs(snowpark_config).create()
    # otherwise configure from environment variables
    elif "SNOWSQL_ACCOUNT" in os.environ:
        snowpark_config = {
            "account": os.environ["SNOWSQL_ACCOUNT"],
            "user": os.environ["SNOWSQL_USER"],
            "password": os.environ["SNOWSQL_PWD"],
            "role": os.environ["SNOWSQL_ROLE"],
            "warehouse": os.environ["SNOWSQL_WAREHOUSE"],
            "database": os.environ["SNOWSQL_DATABASE"],
            "schema": os.environ["SNOWSQL_SCHEMA"],
            "region":os.environ["SNOWSQL_REGION"]
        }
        SnowflakeConnection().connection = Session.builder.configs(snowpark_config).create()

    if SnowflakeConnection().connection:
        return SnowflakeConnection().connection  # type: ignore
    else:
        raise Exception("Unable to create a Snowpark session")


# Mimic the snowcli logic for getting config details, but skip the app.toml processing
# since this will be called outside the snowcli app context.
# TODO: It would be nice to get rid of this entirely and always use creds.json but
# need to update snowcli to make that happen
def get_snowsql_config(
    connection_name: str = 'dev',
    config_file_path: str = os.path.expanduser('~/.snowsql/config'),
) -> dict:
    import configparser

    snowsql_to_snowpark_config_mapping = {
        'account': 'account',
        'accountname': 'account',
        'username': 'user',
        'password': 'password',
        'rolename': 'role',
        'warehousename': 'warehouse',
        'dbname': 'database',
        'schemaname': 'schema'
    }
    try:
        config = configparser.ConfigParser(inline_comment_prefixes="#")
        connection_path = 'connections.' + connection_name

        config.read(config_file_path)
        session_config = config[connection_path]
        # Convert snowsql connection variable names to snowcli ones
        session_config_dict = {
            snowsql_to_snowpark_config_mapping[k]: v.strip('"')
            for k, v in session_config.items()
        }
        return session_config_dict
    except Exception:
        raise Exception(
            "Error getting snowsql config details"
        )
def get_snowsql_config():
    try:
        # Your existing code to read SnowSQL config
        # ...

        # Ensure the 'region' key is present or handle it gracefully
        snowsql_config = {}
        for k, v in snowsql_config_mapping.items():
            try:
                snowsql_config[v] = snowsql_config_mapping[k].strip('"')
            except KeyError:
                if k == 'region':
                    snowsql_config['region'] = 'your_default_region'
                else:
                    raise

        return snowsql_config
    except Exception as e:
        print(f"Error getting SnowSQL config details: {e}")
        raise

def get_snowpark_session():
    try:
        snowpark_config = get_snowsql_config()

        # Your existing code to create a Snowpark session
        # ...

    except Exception as e:
        print(f"Error creating Snowpark session: {e}")
        raise
