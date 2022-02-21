# Crypto Deals Market

1. A contract where a lawyer account can create "*Deals*".
A deal consists of:
 - a sender address.
 - a receiver address.
 - a price (in USD that the sender agrees to pay to the receiver).
 - the token that is used for payment.
 - a date (uint timestamp until which the sender has to pay).

2. The buyer of the deal (=sender) can execute the payment with the payDeal() function.
- The agreed USD price will be converted to the token amount at time of payment.
- Payments are made to the contract (escrow system).

3. The lawyer can then decide to finalize the deal, which transfers the tokens to the receiver, or cancel it, transferring the tokens back to the sender.

The admin account can add new tokens and price feeds to the contract that can then be used in deals, but cannot create/cancel/finalize deals.