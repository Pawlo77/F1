"""
Module to test the deployment of the Prefect flow.
"""

from prefect import flow


@flow(name="test_deployment")
def main():
    """
    Simple test to check if the deployment is working.
    """
    print("Prefect is working!")
