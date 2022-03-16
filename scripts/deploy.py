from scripts.helpful_scripts import get_account
from brownie import Marketplace, accounts, config


def deploy():
    # deploying to testnet, using a secondary account of mine as lawyer
    admin = get_account()
    lawyer = accounts.add(config["wallets"]["second_acc"])
    marketplace = Marketplace.deploy(
        lawyer, {"from": admin}, publish_source=True)


def add_token():
    admin = get_account()
    marketplace = Marketplace[-1]
    # for test purposes use the MATIC price feed and auticoin token.
    marketplace.addToken("AC", "0x9D417F0febDB1Dbd3ad6788241c1F946b58ddd4a",
                         "0x7794ee502922e2b723432DDD852B3C30A911F021", {"from": admin})


def main():
    # deploy()
    add_token()
