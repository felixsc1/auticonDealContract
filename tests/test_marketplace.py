from brownie import accounts, Wei, exceptions, chain
from scripts.helpful_scripts import get_account
from datetime import datetime
import pytest
# import sha3


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
    dtimestamp = int(datetime(2022, 12, 12, 20).timestamp())
    tx = marketplace.createNewDeal(
        sender, receiver, price, "AC", dtimestamp, {"from": lawyer})
    tx.wait(1)

    # 1 AC = 2000$ thus we transfer 0.5 AC to the sender
    balance = Wei("0.5 ether")
    auticoin.transfer(sender, balance, {"from": admin})
    auticoin.approve(marketplace.address, balance, {"from": sender})
    tx = marketplace.payDeal(1, {"from": sender})
    tx.wait(1)

    # check if the deals struct has been updated with the paid amount (6th value, see contract)
    assert marketplace.deals(1)[6] == balance


def test_payment_datelimit(deployed_marketplace):
    # test if everything is working as expected with block timestamps

    marketplace, auticoin = deployed_marketplace
    admin, lawyer, sender, receiver = accounts[0:4]
    price = Wei("1000 ether")
    dtimestamp = int(datetime(2022, 12, 12, 20).timestamp())
    tx = marketplace.createNewDeal(
        sender, receiver, price, "AC", dtimestamp, {"from": lawyer})
    tx.wait(1)

    balance = Wei("0.5 ether")
    auticoin.transfer(sender, balance, {"from": admin})
    auticoin.approve(marketplace.address, balance, {"from": sender})

    # check if payment is declined when deadline has passed
    chain.sleep(365*24*60*60)
    with pytest.raises(exceptions.VirtualMachineError):
        marketplace.payDeal(1, {"from": sender})


def test_finalize_deal(deployed_marketplace):
    # arrangement is everything from before
    marketplace, auticoin = deployed_marketplace
    admin, lawyer, sender, receiver = accounts[0:4]
    price = Wei("1000 ether")
    dtimestamp = datetime(2022, 12, 12, 20).timestamp()
    tx = marketplace.createNewDeal(
        sender, receiver, price, "AC", dtimestamp, {"from": lawyer})
    balance = Wei("0.5 ether")
    auticoin.transfer(sender, balance, {"from": admin})
    auticoin.approve(marketplace.address, balance, {"from": sender})
    marketplace.payDeal(1, {"from": sender})

    # Now lawyer account should be able to call the finalize function
    assert marketplace.finalizeDeal(1, {"from": lawyer})
    # receiver should have received the payment from the contract
    assert auticoin.balanceOf(receiver) == balance


def test_pay_and_cancel_with_ETH(deployed_marketplace):
    """
    Above functions use ERC20 for payment, test if payment and refund logic works for ETH.
    """
    marketplace, auticoin = deployed_marketplace
    admin, lawyer, sender, receiver = accounts[0:4]
    price = Wei("100 ether")
    dtimestamp = datetime(2022, 12, 12, 20).timestamp()
    tx = marketplace.createNewDeal(
        sender, receiver, price, "ETH", dtimestamp, {"from": lawyer})
    marketplace.payDeal(1, {"from": sender, "value": price})


# def test_grant_role(deployed_marketplace):
#     """
#     just curious if admin could grant lawyer roles to others. might be security risk.
#     """
#     marketplace, auticoin = deployed_marketplace
#     admin, lawyer, fake_lawyer = accounts[0:3]
#     k = sha3.keccak_256()
#     k.update('LAWYER_ROLE')
#     lawyer_role = k.hexdigest()
#     marketplace.grantRole(lawyer_role, fake_lawyer, {"from": admin})
