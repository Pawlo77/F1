# All models need to be imported to register them in the metadata
# pylint: disable=wildcard-import,unused-wildcard-import

"""
This script is used to log into Prefect Cloud and create work pools for the deployment.
It uses the Prefect CLI to perform these actions.
"""

import os
import subprocess

import sqlalchemy
from dotenv import load_dotenv
from prefect_github import GitHubCredentials
from prefect_sqlalchemy import ConnectionComponents, SqlAlchemyConnector, SyncDriver
from sqlalchemy import text

# import all models from the project
from src.f1.flows.f1_attendance.models import *  # noqa: F401,F403
from src.f1.flows.f1db.models import *  # noqa: F401,F403
from src.f1.flows.flows_utils import Base, load_default_sqlalchemy_connection
from src.f1.flows.racing_circuits.models import *  # noqa: F401,F403

load_dotenv()


def log_into_prefect_cloud():
    """
    Log into Prefect Cloud using the API key from environment variables.
    """

    # Get the Prefect Cloud API key from environment variables
    prefect_cloud_api_key: str = os.getenv("PREFECT_CLOUD_API_KEY")
    if not prefect_cloud_api_key:
        raise ValueError("Missing PREFECT_CLOUD_API_KEY in environment variables")
    prefect_cloud_workspace: str = os.getenv("PREFECT_CLOUD_WORKSPACE")
    if not prefect_cloud_workspace:
        raise ValueError("Missing PREFECT_CLOUD_WORKSPACE in environment variables")

    # Log out of Prefect Cloud if already logged in
    try:
        subprocess.run(
            ["poetry", "run", "prefect", "cloud", "logout"],
            check=True,
        )
    except subprocess.CalledProcessError:
        pass  # Ignore if not logged in

    # Log into Prefect Cloud
    subprocess.run(
        [
            "poetry",
            "run",
            "prefect",
            "cloud",
            "login",
            "--key",
            prefect_cloud_api_key,
            "--workspace",
            prefect_cloud_workspace,
        ],
        check=True,
    )


def create_work_pools():
    """
    Create work pools for the deployment.
    """

    if (
        subprocess.run(  # pylint: disable=subprocess-run-check
            ["poetry", "run", "prefect", "work-pool", "inspect", "default-work-pool"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        ).returncode
        != 0
    ):
        subprocess.run(
            [
                "poetry",
                "run",
                "prefect",
                "work-pool",
                "create",
                "--overwrite",
                "default-work-pool",
                "--type",
                # "prefect:managed",
                "process",
                "--set-as-default",
            ],
            check=True,
        )
        subprocess.run(
            [
                "poetry",
                "run",
                "prefect",
                "work-pool",
                "update",
                "--concurrency-limit",
                "10",
                "--description",
                "This is the default work pool for the deployment.",
                "default-work-pool",
            ],
            check=True,
        )


def create_blocks():
    """
    Create blocks for the deployment.
    """
    token = os.getenv("REPO_TOKEN")
    if not token:
        raise ValueError("Missing REPO_TOKEN in environment variables")

    # Create GitHub credentials block
    github_block = GitHubCredentials(token=token)
    github_block.save("f1-github-credentials", overwrite=True)

    username = os.getenv("DB_USERNAME")
    password = os.getenv("DB_PASSWORD")
    host = os.getenv("DB_HOST")
    port = os.getenv("DB_PORT")
    database = os.getenv("DB_DATABASE")
    if not all([username, password, host, port, database]):
        raise ValueError(
            "Missing one or more required environment variables: "
            "DB_USERNAME, DB_PASSWORD, DB_HOST, DB_PORT, DB_DATABASE"
        )

    # Create SQLAlchemy connector block
    # Create the database if it does not exist

    # Connect to the master database to check for the existence of the target database
    master_connection_str = (
        f"mssql+pyodbc://{username}:{password}@{host}:{port}/master?"
        "driver=ODBC+Driver+18+for+SQL+Server&encrypt=yes&"
        "trustServerCertificate=yes&connectionTimeout=15"
    )
    master_engine = sqlalchemy.create_engine(master_connection_str)
    with master_engine.connect() as conn:
        conn.execution_options(isolation_level="AUTOCOMMIT").execute(
            text(
                f"IF DB_ID('{database}') IS NULL BEGIN CREATE DATABASE [{database}] END"
            )
        )

    sqlalchemy_block = SqlAlchemyConnector(
        connection_info=ConnectionComponents(
            driver=SyncDriver.MSSQL_PYODBC,
            username=username,
            password=password,
            host=host,
            port=port,
            database=database,
            query={
                "driver": "ODBC Driver 18 for SQL Server",
                "encrypt": "yes",
                "trustServerCertificate": "yes",
                "connectionTimeout": "15",
            },
        )
    )
    sqlalchemy_block.save("f1-mssql-azure", overwrite=True)


def create_sqlalchemy_objects():
    """
    Create a SQLAlchemy connection using the default connector.
    """
    with load_default_sqlalchemy_connection() as conn:
        schemas = [
            {"name": "web", "create": "web"},
            {"name": "f1db", "create": "f1db"},
        ]

        for schema in schemas:
            print(f"Creating schema: {schema['name']} as {schema['create']}")
            create_schema_query = text(f"""
                IF NOT EXISTS (SELECT * FROM sys.schemas WHERE name = '{schema["name"]}')
                BEGIN
                    EXEC('CREATE SCHEMA [{schema["create"]}]')
                    COMMIT;
                END
            """)  # nosec
            conn.execute(create_schema_query)

        engine = conn.engine
        print("Creating tables in the database...")
        # Base.metadata.drop_all(engine)
        Base.metadata.create_all(engine)


def main():
    """
    Main function to execute the deployment process.
    """
    if "PREFECT_CLOUD_API_KEY" in os.environ:  # pylint: disable=magic-value-comparison
        log_into_prefect_cloud()
        print("Logged into Prefect Cloud successfully.")

    create_work_pools()
    print("Work pools created successfully.")

    create_blocks()
    print("Blocks created successfully.")

    create_sqlalchemy_objects()
    print("SQLAlchemy objects created successfully.")
    print("Registered tables in metadata:")
    for table_name in Base.metadata.tables.keys():
        print(f"- {table_name}")


if __name__ == "__main__":
    main()
