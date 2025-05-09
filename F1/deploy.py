"""
This script is used to log into Prefect Cloud and create work pools for the deployment.
It uses the Prefect CLI to perform these actions.
"""

import os
import subprocess

from dotenv import load_dotenv

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
        subprocess.run(
            ["poetry", "run", "prefect", "work-pool", "inspect", "default-work-pool"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=True,
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


def main():
    """
    Main function to execute the deployment process.
    """
    log_into_prefect_cloud()
    print("Logged into Prefect Cloud successfully.")

    create_work_pools()
    print("Work pools created successfully.")


if __name__ == "__main__":
    main()
