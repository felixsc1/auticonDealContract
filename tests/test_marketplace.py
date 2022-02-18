from brownie import Marketplace, accounts, Wei, exceptions
from scripts.helpful_scripts import get_account
from datetime import datetime
import pytest


def test_create_new_deal(deployed_marketplace):
    admin = get_account(index=0)
    lawyer = get_account(index=1)
    sender = get_account(index=2)
    receiver = get_account(index=3)
    price = Wei("100 ether")
    dtimestamp = datetime(2022, 12, 12, 20).timestamp()

    tx = deployed_marketplace.createNewDeal(
        sender, receiver, price, dtimestamp, {"from": lawyer})
    tx.wait(1)

    # event should have been emitted and assigned an ID:
    assert tx.events["NewDeal"]["dealId"] == 1

    # Non-lawyer account shouldn't be able to create deals.
    with pytest.raises(exceptions.VirtualMachineError):
        tx = deployed_marketplace.createNewDeal(
            sender, receiver, price, dtimestamp, {"from": admin})
        tx.wait(1)


def test_cancel_deal(deployed_marketplace):
    pass
