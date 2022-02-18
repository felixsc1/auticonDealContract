import pytest
from brownie import accounts, Marketplace
from scripts.helpful_scripts import get_account


@pytest.fixture
def deployed_marketplace():
    deployer = get_account(index=0)
    lawyer = get_account(index=1)

    marketplace = Marketplace.deploy(lawyer, {"from": deployer})
    return marketplace
