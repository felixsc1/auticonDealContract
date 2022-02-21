from brownie import Marketplace, accounts, Wei, exceptions
from scripts.helpful_scripts import get_account
from datetime import datetime
import pytest


def test_create_new_deal(deployed_marketplace):
    marketplace, auticoin = deployed_marketplace
    admin, lawyer, sender, receiver = accounts[0:4]

    price = Wei("1000 ether")
    dtimestamp = datetime(2022, 12, 12, 20).timestamp()

    tx = marketplace.createNewDeal(
        sender, receiver, price, "AC", dtimestamp, {"from": lawyer})
    tx.wait(1)

    # event should have been emitted and assigned an ID:
    assert tx.events["NewDeal"]["dealId"] == 1

    # Non-lawyer account shouldn't be able to create deals.
    with pytest.raises(exceptions.VirtualMachineError):
        tx = marketplace.createNewDeal(
            sender, receiver, price, "AC", dtimestamp, {"from": admin})
        tx.wait(1)


def test_pay_deal(deployed_marketplace):
    """
    Test if a sender can successfully pay a deal with an ERC20 token.
    This also tests if the price conversion is correctly done (deal created in USD, but paid with auticoin)
    """
    # same arrangement as before
    marketplace, auticoin = deployed_marketplace
    admin, lawyer, sender, receiver = accounts[0:4]
    price = Wei("1000 ether")
    dtimestamp = datetime(2022, 12, 12, 20).timestamp()
    tx = marketplace.createNewDeal(
        sender, receiver, price, "AC", dtimestamp, {"from": lawyer})
    tx.wait(1)

    # 1 AC = 2000$ thus we transfer 0.5 AC to the sender
    balance = Wei("0.5 ether")
    auticoin.transfer(sender, balance, {"from": admin})
    auticoin.approve(marketplace.address, balance, {"from": sender})
    assert marketplace.payDeal(1, {"from": sender})

    # check if the deals struct has been updated with the paid amount (6th value, see contract)
    assert marketplace.deals(1)[6] == balance


def test_finalize_deal(deployed_marketplace):
    # arrangement is everything from before
    marketplace, auticoin = deployed_marketplace
    admin, lawyer, sender, receiver = accounts[0:4]
    price = Wei("1000 ether")
    dtimestamp = datetime(2022, 12, 12, 20).timestamp()
    tx = marketplace.createNewDeal(
        sender, receiver, price, "AC", dtimestamp, {"from": lawyer})
    tx.wait(1)
    balance = Wei("0.5 ether")
    auticoin.transfer(sender, balance, {"from": admin})
    auticoin.approve(marketplace.address, balance, {"from": sender})
    marketplace.payDeal(1, {"from": sender})

    # Now lawyer account should be able to call the finalize function
    assert marketplace.finalizeDeal(1, {"from": lawyer})
    # receiver should have received the payment from the contract
    assert auticoin.balanceOf(receiver) == balance
