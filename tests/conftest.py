import pytest
from brownie import accounts, Marketplace, AutiCoin
from scripts.helpful_scripts import get_account, get_contract


@pytest.fixture
def deployed_marketplace():
    # deploy marketplace and add auticoin as payment token
    deployer = get_account(index=0)
    lawyer = get_account(index=1)

    auticoin = AutiCoin.deploy({"from": deployer})
    price_feed = get_contract(
        "mock_price_feed")  # Will just return 2000$ value
    marketplace = Marketplace.deploy(lawyer, {"from": deployer})
    marketplace.addToken("AC", auticoin.address,
                         price_feed.address, {"from": deployer})
    return marketplace, auticoin
