# Cobo WaaS 2 Demo

This project demonstrates how to use Cobo's WaaS 2 APIs/SDKs to build a basic wallet application.

## Setup

1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Copy `.env.example` to `.env` and fill in your Cobo API credentials
4. Run the application: `cd app && uvicorn main:app --reload`

## API Endpoints

- GET /api/wallets: List all wallets
- GET /api/wallets/{wallet_id}/balance: Get wallet balance
- GET /api/wallets/{wallet_id}/transactions: Get wallet transactions
- POST /api/wallets/{wallet_id}/deposit: Deposit to wallet
- POST /api/wallets/{wallet_id}/withdraw: Withdraw from wallet
- POST /api/webhook: Handle webhook events

## Resources

- [Cobo WaaS 2 API References](https://www.cobo.com/developers/v2/api-references/)
- [Cobo WaaS 2 Guides](https://www.cobo.com/developers/v2/guides/overview/introduction)
- [Cobo WaaS SDKs](https://www.cobo.com/developers/v2/developer-tools/)
- [Cobo Portal Product Manual](https://manuals.cobo.com/en/portal/introduction)