"""
Deploys Prefect flows to Prefect Cloud using a configuration file and GitHub credentials.
This script automates the deployment process by logging into Prefect Cloud,
creating a GitHub block, creating work pools, and deploying flows based
on the provided configuration.
"""

import os
import subprocess

import requests
import yaml
from dotenv import load_dotenv
from prefect import flow
from prefect.runner.storage import GitRepository
from prefect_github import GitHubCredentials

load_dotenv()

GITHUB_BLOCK_NAME: str = "github-credentials"
os.environ["PREFECT_API_URL"] = "https://api.prefect.cloud"


def _validate_github_token(token: str) -> bool:
    """
    Validate the GitHub token by making a request to the GitHub API.
    Args:
        token (str): The GitHub token to validate.
    Returns:
        bool: True if the token is valid, False otherwise.
    """
    response = requests.get(
        "https://api.github.com/user",
        headers={"Authorization": f"token {token}"},
        timeout=10,
    )
    return response.ok


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


def create_github_block():
    """
    Create a GitHub block using the GitHub token from environment variables.
    """

    # Get the GitHub token from environment variables
    repo_token: str = os.getenv("REPO_TOKEN")
    if not repo_token:
        raise ValueError("Missing REPO_TOKEN in environment variables")
    if not _validate_github_token(repo_token):
        raise ValueError("Invalid REPO_TOKEN")

    # Create a GitHub block
    github_credentials_block = GitHubCredentials(token=repo_token)
    github_credentials_block.save(name=GITHUB_BLOCK_NAME, overwrite=True)


def create_work_pools():
    """
    Create work pools for the deployment.
    """

    try:
        with subprocess.Popen(
            [
                "poetry",
                "run",
                "prefect",
                "work-pool",
                "delete",
                "default-work-pool",
            ],
            stdin=subprocess.PIPE,
        ) as process:
            process.communicate(input=b"y\n")
    except subprocess.CalledProcessError:
        pass

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
            "prefect:managed",
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


def deploy_flows(config_path: str):
    """
    Deploy flows using the configuration file.
    Args:
        config_path (str): The path to the configuration file.
    """
    with open(config_path, "r", encoding="utf-8") as file:
        config = yaml.safe_load(file)

    if not isinstance(config, list):
        raise ValueError("Configuration file must contain a list of flows.")

    repo_url: str = os.getenv("REPO_URL")
    if not repo_url:
        raise ValueError("Missing REPO_URL in environment variables")
    source = GitRepository(
        url=repo_url,
        credentials=GitHubCredentials.load(GITHUB_BLOCK_NAME),
    )

    for flow_config in config:
        if not isinstance(flow_config, dict):
            raise ValueError(
                "Each flow in the configuration file must be a dictionary."
            )
        flow_name = flow_config.get("name")
        if not flow_name:
            raise ValueError("Each flow must have a 'name' key.")
        flow_entrypoint = flow_config.get("entrypoint")
        if not flow_entrypoint:
            raise ValueError("Each flow must have a 'entrypoint' key.")

        # Deploy the flow
        cron = flow_config.get("cron")
        flow.from_source(source=source, entrypoint=flow_entrypoint).deploy(
            name=flow_name,
            cron=cron,
            work_pool_name="default-work-pool",
        )


def main():
    """
    Main function to execute the deployment process.
    """
    log_into_prefect_cloud()
    print("Logged into Prefect Cloud successfully.")

    create_github_block()
    print("GitHub block created successfully.")

    create_work_pools()
    print("Work pools created successfully.")

    deploy_flows(config_path="flows.yaml")
    print("Flows deployed successfully.")


if __name__ == "__main__":
    main()
