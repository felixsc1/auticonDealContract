// SPDX-License-Identifier: MIT

pragma solidity ^0.8;

import "OpenZeppelin/openzeppelin-contracts@4.4.2/contracts/access/AccessControl.sol";
import "OpenZeppelin/openzeppelin-contracts@4.4.2/contracts/token/ERC20/IERC20.sol";
import "smartcontractkit/chainlink@1.0.1/contracts/src/v0.8/interfaces/AggregatorV3Interface.sol";

contract Marketplace is AccessControl {
    bytes32 public constant LAWYER_ROLE = keccak256("LAWYER_ROLE");
    bytes32 public constant ADMIN_ROLE = keccak256("ADMIN_ROLE");

    struct Token {
        address token;
        address pricefeed;
    }
    mapping(string => Token) public tokens;

    enum DealStatus {
        Open,
        Paid,
        Completed,
        Cancelled
    }

    struct Deal {
        DealStatus status;
        address sender;
        address receiver;
        uint256 dealId;
        uint256 priceUSD;
        string symbol;
        uint256 paidTokens;
        uint256 dateDue;
    }

    uint256 private _dealId;
    mapping(uint256 => Deal) public deals;

    // -- Events --

    event NewDeal(
        address sender,
        address receiver,
        uint256 dealId,
        uint256 priceUSD,
        string symbol,
        uint256 dateDue
    );

    event Cancel(uint256 dealId);

    event Payment(
        address sender,
        uint256 dealId,
        string symbol,
        uint256 amount
    );

    event Complete(uint256 dealId);

    // Constructor: A lawyer account is specified during deployment
    constructor(address lawyer) {
        _setupRole(LAWYER_ROLE, lawyer);
        _setupRole(ADMIN_ROLE, msg.sender);
    }

    // -- User Functions ---

    function createNewDeal(
        address sender,
        address receiver,
        uint256 priceUSD,
        string memory symbol,
        uint256 dateDue
    ) external onlyRole(LAWYER_ROLE) {
        require(isTokenAllowed(symbol), "This token is not accepted");
        _dealId++;

        Deal memory deal = Deal(
            DealStatus.Open,
            sender,
            receiver,
            _dealId,
            priceUSD,
            symbol,
            0,
            dateDue
        );

        deals[_dealId] = deal;
        emit NewDeal(sender, receiver, _dealId, priceUSD, symbol, dateDue);
    }

    function showDeal(uint256 dealId) public view returns (Deal memory) {
        return deals[dealId];
    }

    function cancelDeal(uint256 dealId) public onlyRole(LAWYER_ROLE) {
        Deal storage deal = deals[dealId];

        if (deal.status == DealStatus.Open) {
            deal.status = DealStatus.Cancelled;
        } else if (deal.status == DealStatus.Paid) {
            // refund sender (for the cases of ETH or ERC20 payment)
            if (
                keccak256(abi.encodePacked(deal.symbol)) ==
                keccak256(abi.encodePacked("ETH"))
            ) {
                payable(deal.sender).transfer(deal.paidTokens);
            } else {
                IERC20(tokens[deal.symbol].token).transferFrom(
                    address(this),
                    deal.sender,
                    deal.paidTokens
                );
            }
        }

        deal.status = DealStatus.Cancelled;
        emit Cancel(dealId);
    }

    function payDeal(uint256 dealId) public payable {
        Deal storage deal = deals[dealId];
        require(deal.status == DealStatus.Open, "Deal is no longer active");
        require(
            block.timestamp <= deal.dateDue,
            "Time window for payment has passed"
        );
        // in case user enters the wrong ID, he shouldn't accidentally pay "wrong" deal.
        require(
            msg.sender == deal.sender,
            "Must be paid by the buyer of the deal"
        );

        uint256 amount = USDtoToken(deal.symbol, deal.priceUSD);

        // in case of payment with ETH, web3.js needs to set appropriate msg.value
        if (
            keccak256(abi.encodePacked(deal.symbol)) ==
            keccak256(abi.encodePacked("ETH"))
        ) {
            require(msg.value >= amount);
            // reimburse excess amount
            payable(msg.sender).transfer(msg.value - amount);
        } else {
            IERC20(tokens[deal.symbol].token).transferFrom(
                msg.sender,
                address(this),
                amount
            );
        }

        deal.status = DealStatus.Paid;
        deal.paidTokens = amount; // keeping track of tokens at time of payment.
        emit Payment(deal.sender, dealId, deal.symbol, amount);
    }

    function finalizeDeal(uint256 dealId) public onlyRole(LAWYER_ROLE) {
        Deal storage deal = deals[dealId];
        // prevent accidental finalization of unpaid deals
        require(
            deal.status == DealStatus.Paid,
            "Deal has not been paid or is not active"
        );

        // note: token value may have changed between payment and finalization.
        IERC20(tokens[deal.symbol].token).transfer(
            deal.receiver,
            deal.paidTokens
        );

        deal.status = DealStatus.Completed;
        emit Complete(dealId);
    }

    //  -- Token Management Functions --

    function addToken(
        string memory symbol,
        address token,
        address pricefeed
    ) public onlyRole(ADMIN_ROLE) {
        tokens[symbol] = Token(token, pricefeed);
    }

    function isTokenAllowed(string memory symbol) public view returns (bool) {
        return tokens[symbol].token != address(0);
    }

    function USDtoToken(string memory symbol, uint256 usdamount)
        public
        view
        returns (uint256)
    {
        require(isTokenAllowed(symbol), "This token is not accepted");

        AggregatorV3Interface priceFeed = AggregatorV3Interface(
            tokens[symbol].pricefeed
        );
        (, int256 price, , , ) = priceFeed.latestRoundData();
        uint256 decimals = uint256(priceFeed.decimals()); // needed in a calculation below
        return ((usdamount / uint256(price)) * (10**decimals));
    }

    // fallback function to make contract able to receive ETH:
    receive() external payable {}
}
