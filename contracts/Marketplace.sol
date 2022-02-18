// SPDX-License-Identifier: MIT

pragma solidity ^0.8;

import "OpenZeppelin/openzeppelin-contracts@4.4.2/contracts/access/AccessControl.sol";

contract Marketplace is AccessControl {
    bytes32 public constant LAWYER_ROLE = keccak256("LAWYER_ROLE");

    uint256 private _dealId;
    mapping(uint256 => Deal) public deals;

    enum DealStatus {
        Active,
        Completed,
        Cancelled
    }

    struct Deal {
        DealStatus status;
        address sender;
        address receiver;
        uint256 dealId;
        uint256 priceUSD;
        uint256 dateDue;
    }

    // -- Events --

    event NewDeal(
        address sender,
        address receiver,
        uint256 dealId,
        uint256 priceUSD,
        uint256 dateDue
    );

    event Cancel(uint256 dealId);

    // Constructor: Needs to pass a lawyer accounts during deployment
    constructor(address lawyer) {
        _setupRole(LAWYER_ROLE, lawyer);
    }

    // -- Functions ---

    function createNewDeal(
        address sender,
        address receiver,
        uint256 priceUSD,
        uint256 dateDue
    ) external {
        require(hasRole(LAWYER_ROLE, msg.sender), "Caller is not a lawyer");
        _dealId++;

        Deal memory deal = Deal(
            DealStatus.Active,
            sender,
            receiver,
            _dealId,
            priceUSD,
            dateDue
        );

        deals[_dealId] = deal;
        emit NewDeal(sender, receiver, _dealId, priceUSD, dateDue);
    }

    function showDeal(uint256 dealId) public view returns (Deal memory) {
        return deals[dealId];
    }

    function cancelDeal(uint256 dealId) public {
        Deal storage deal = deals[dealId];
        require(hasRole(LAWYER_ROLE, msg.sender), "Caller is not a lawyer");
        require(deal.status == DealStatus.Active, "Deal is no longer active");

        deal.status = DealStatus.Active;

        emit Cancel(dealId);
    }
}
