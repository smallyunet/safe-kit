import pytest
import requests_mock

from safe_kit.service import SafeServiceClient
from safe_kit.types import SafeTransactionData


@pytest.fixture
def service():
    return SafeServiceClient("https://safe-transaction-mainnet.safe.global")


def test_get_service_info(service):
    with requests_mock.Mocker() as m:
        m.get(
            "https://safe-transaction-mainnet.safe.global/v1/about/",
            json={
                "name": "Safe Transaction Service",
                "version": "1.0.0",
                "api_version": "v1",
                "secure": True,
                "settings": {},
            },
        )
        info = service.get_service_info()
        assert info.name == "Safe Transaction Service"


def test_get_pending_transactions(service):
    safe_address = "0xSafeAddress"
    with requests_mock.Mocker() as m:
        m.get(
            f"https://safe-transaction-mainnet.safe.global/v1/safes/{safe_address}/multisig-transactions/?executed=false&trusted=true",
            json={
                "results": [
                    {
                        "safe": safe_address,
                        "to": "0xTo",
                        "value": "0",
                        "data": None,
                        "operation": 0,
                        "gasToken": "0x0000000000000000000000000000000000000000",
                        "safeTxGas": 0,
                        "baseGas": 0,
                        "gasPrice": "0",
                        "refundReceiver": "0x0000000000000000000000000000000000000000",
                        "nonce": 0,
                        "executionDate": None,
                        "submissionDate": "2023-01-01T00:00:00Z",
                        "modified": "2023-01-01T00:00:00Z",
                        "blockNumber": None,
                        "transactionHash": None,
                        "safeTxHash": "0xHash",
                        "executor": None,
                        "isExecuted": False,
                        "isSuccessful": None,
                        "ethGasPrice": None,
                        "maxFeePerGas": None,
                        "maxPriorityFeePerGas": None,
                        "gasUsed": None,
                        "fee": None,
                        "origin": None,
                        "dataDecoded": None,
                        "confirmationsRequired": 2,
                        "confirmations": [],
                        "trusted": True,
                        "signatures": None,
                    }
                ]
            },
        )
        txs = service.get_pending_transactions(safe_address)
        assert len(txs) == 1
        assert txs[0].safe_tx_hash == "0xHash"


def test_get_multisig_transactions(service):
    safe_address = "0xSafeAddress"
    with requests_mock.Mocker() as m:
        m.get(
            f"https://safe-transaction-mainnet.safe.global/v1/safes/{safe_address}/multisig-transactions/?executed=true&trusted=true&ordering=-nonce&limit=10&offset=0",
            json={
                "results": [
                    {
                        "safe": safe_address,
                        "to": "0xTo",
                        "value": "0",
                        "data": None,
                        "operation": 0,
                        "gasToken": "0x0000000000000000000000000000000000000000",
                        "safeTxGas": 0,
                        "baseGas": 0,
                        "gasPrice": "0",
                        "refundReceiver": "0x0000000000000000000000000000000000000000",
                        "nonce": 1,
                        "executionDate": "2023-01-02T00:00:00Z",
                        "submissionDate": "2023-01-01T00:00:00Z",
                        "modified": "2023-01-02T00:00:00Z",
                        "blockNumber": 12345,
                        "transactionHash": "0xTxHash",
                        "safeTxHash": "0xHash",
                        "executor": "0xExecutor",
                        "isExecuted": True,
                        "isSuccessful": True,
                        "ethGasPrice": "1000000000",
                        "maxFeePerGas": "1000000000",
                        "maxPriorityFeePerGas": "1000000000",
                        "gasUsed": 21000,
                        "fee": "21000000000000",
                        "origin": None,
                        "dataDecoded": None,
                        "confirmationsRequired": 2,
                        "confirmations": [],
                        "trusted": True,
                        "signatures": None,
                    }
                ]
            },
        )
        txs = service.get_multisig_transactions(
            safe_address,
            executed=True,
            trust=True,
            ordering="-nonce",
            limit=10,
            offset=0,
        )
        assert len(txs) == 1
        assert txs[0].safe_tx_hash == "0xHash"
        assert txs[0].is_executed is True


def test_propose_transaction(service):
    safe_address = "0xSafeAddress"
    tx_data = SafeTransactionData(
        to="0xTo",
        value=0,
        data="0x",
        operation=0,
        safe_tx_gas=0,
        base_gas=0,
        gas_price=0,
        gas_token="0x0000000000000000000000000000000000000000",
        refund_receiver="0x0000000000000000000000000000000000000000",
        nonce=1,
    )

    with requests_mock.Mocker() as m:
        m.post(
            f"https://safe-transaction-mainnet.safe.global/v1/safes/{safe_address}/multisig-transactions/",
            status_code=201,
        )
        service.propose_transaction(
            safe_address=safe_address,
            safe_tx_data=tx_data,
            safe_tx_hash="0xHash",
            sender_address="0xSender",
            signature="0xSig",
        )

        assert m.called
        assert m.last_request.json()["contractTransactionHash"] == "0xHash"


def test_confirm_transaction(service):
    safe_tx_hash = "0xHash"
    with requests_mock.Mocker() as m:
        m.post(
            f"https://safe-transaction-mainnet.safe.global/v1/multisig-transactions/{safe_tx_hash}/confirmations/",
            status_code=201,
        )
        service.confirm_transaction(safe_tx_hash, "0xSig")
        assert m.called
        assert m.last_request.json()["signature"] == "0xSig"


def test_get_transaction(service):
    safe_tx_hash = "0xHash"
    with requests_mock.Mocker() as m:
        m.get(
            f"https://safe-transaction-mainnet.safe.global/v1/multisig-transactions/{safe_tx_hash}/",
            json={
                "safe": "0xSafe",
                "to": "0xTo",
                "value": "0",
                "data": None,
                "operation": 0,
                "gasToken": "0x0000000000000000000000000000000000000000",
                "safeTxGas": 0,
                "baseGas": 0,
                "gasPrice": "0",
                "refundReceiver": "0x0000000000000000000000000000000000000000",
                "nonce": 0,
                "executionDate": None,
                "submissionDate": "2023-01-01T00:00:00Z",
                "modified": "2023-01-01T00:00:00Z",
                "blockNumber": None,
                "transactionHash": None,
                "safeTxHash": safe_tx_hash,
                "executor": None,
                "isExecuted": False,
                "isSuccessful": None,
                "ethGasPrice": None,
                "maxFeePerGas": None,
                "maxPriorityFeePerGas": None,
                "gasUsed": None,
                "fee": None,
                "origin": None,
                "dataDecoded": None,
                "confirmationsRequired": 2,
                "confirmations": [],
                "trusted": True,
                "signatures": None,
            },
        )
        tx = service.get_transaction(safe_tx_hash)
        assert tx.safe_tx_hash == safe_tx_hash


def test_get_safes_by_owner(service):
    owner_address = "0xOwner"
    with requests_mock.Mocker() as m:
        m.get(
            f"https://safe-transaction-mainnet.safe.global/v1/owners/{owner_address}/safes/",
            json={"safes": ["0xSafe1", "0xSafe2"]},
        )
        safes = service.get_safes_by_owner(owner_address)
        assert safes == ["0xSafe1", "0xSafe2"]


def test_get_balances(service):
    safe_address = "0xSafe"
    with requests_mock.Mocker() as m:
        m.get(
            f"https://safe-transaction-mainnet.safe.global/v1/safes/{safe_address}/balances/?trusted=false&exclude_spam=true",
            json=[
                {
                    "tokenAddress": None,
                    "token": None,
                    "balance": "1000000000000000000",
                },
                {
                    "tokenAddress": "0xToken",
                    "token": {"name": "Token", "symbol": "TKN", "decimals": 18},
                    "balance": "5000000000000000000",
                },
            ],
        )
        balances = service.get_balances(safe_address)
        assert len(balances) == 2
        assert balances[0].token_address is None
        assert balances[0].balance == "1000000000000000000"
        assert balances[1].token_address == "0xToken"


def test_get_safe_info(service):
    safe_address = "0xSafeAddress"
    with requests_mock.Mocker() as m:
        m.get(
            f"https://safe-transaction-mainnet.safe.global/v1/safes/{safe_address}/",
            json={
                "address": safe_address,
                "nonce": 5,
                "threshold": 2,
                "owners": ["0xOwner1", "0xOwner2", "0xOwner3"],
                "masterCopy": "0xMasterCopy",
                "modules": ["0xModule1"],
                "fallbackHandler": "0xFallbackHandler",
                "guard": "0x0000000000000000000000000000000000000000",
                "version": "1.3.0",
            },
        )
        info = service.get_safe_info(safe_address)
        assert info.address == safe_address
        assert info.nonce == 5
        assert info.threshold == 2
        assert len(info.owners) == 3
        assert info.version == "1.3.0"


def test_get_creation_info(service):
    safe_address = "0xSafeAddress"
    with requests_mock.Mocker() as m:
        m.get(
            f"https://safe-transaction-mainnet.safe.global/v1/safes/{safe_address}/creation/",
            json={
                "created": "2023-01-01T00:00:00Z",
                "creator": "0xCreator",
                "transactionHash": "0xTxHash",
                "factoryAddress": "0xFactory",
                "masterCopy": "0xMasterCopy",
                "setupData": "0xSetupData",
            },
        )
        creation = service.get_creation_info(safe_address)
        assert creation.creator == "0xCreator"
        assert creation.transaction_hash == "0xTxHash"
        assert creation.factory_address == "0xFactory"


def test_get_collectibles(service):
    safe_address = "0xSafeAddress"
    with requests_mock.Mocker() as m:
        m.get(
            f"https://safe-transaction-mainnet.safe.global/v1/safes/{safe_address}/collectibles/?trusted=false&exclude_spam=true",
            json=[
                {
                    "address": "0xNFTContract",
                    "tokenName": "Cool NFT",
                    "tokenSymbol": "CNFT",
                    "logoUri": "https://example.com/logo.png",
                    "id": "1",
                    "uri": "https://example.com/token/1",
                    "name": "Cool NFT #1",
                    "description": "A very cool NFT",
                    "imageUri": "https://example.com/image.png",
                    "metadata": {"trait": "rare"},
                }
            ],
        )
        collectibles = service.get_collectibles(safe_address)
        assert len(collectibles) == 1
        assert collectibles[0].token_name == "Cool NFT"
        assert collectibles[0].id == "1"


def test_get_delegates(service):
    safe_address = "0xSafeAddress"
    with requests_mock.Mocker() as m:
        m.get(
            f"https://safe-transaction-mainnet.safe.global/v1/delegates/?safe={safe_address}",
            json={
                "results": [
                    {
                        "safe": safe_address,
                        "delegate": "0xDelegate",
                        "delegator": "0xDelegator",
                        "label": "My Delegate",
                    }
                ]
            },
        )
        delegates = service.get_delegates(safe_address)
        assert len(delegates) == 1
        assert delegates[0].delegate == "0xDelegate"
        assert delegates[0].label == "My Delegate"


def test_add_delegate(service):
    safe_address = "0xSafeAddress"
    with requests_mock.Mocker() as m:
        m.post(
            "https://safe-transaction-mainnet.safe.global/v1/delegates/",
            status_code=201,
        )
        service.add_delegate(
            safe_address=safe_address,
            delegate_address="0xDelegate",
            delegator="0xDelegator",
            label="My Delegate",
            signature="0xSig",
        )
        assert m.called
        assert m.last_request.json()["delegate"] == "0xDelegate"
        assert m.last_request.json()["label"] == "My Delegate"


def test_remove_delegate(service):
    delegate_address = "0xDelegate"
    with requests_mock.Mocker() as m:
        m.delete(
            f"https://safe-transaction-mainnet.safe.global/v1/delegates/{delegate_address}/",
            status_code=204,
        )
        service.remove_delegate(
            delegate_address=delegate_address,
            delegator="0xDelegator",
            signature="0xSig",
        )
        assert m.called
        assert m.last_request.json()["delegator"] == "0xDelegator"


def test_get_tokens(service):
    with requests_mock.Mocker() as m:
        m.get(
            "https://safe-transaction-mainnet.safe.global/v1/tokens/",
            json={
                "results": [
                    {
                        "address": "0xToken1",
                        "name": "Token 1",
                        "symbol": "TKN1",
                        "decimals": 18,
                        "logoUri": "https://example.com/logo1.png",
                    },
                    {
                        "address": "0xToken2",
                        "name": "Token 2",
                        "symbol": "TKN2",
                        "decimals": 6,
                        "logoUri": None,
                    },
                ]
            },
        )
        tokens = service.get_tokens()
        assert len(tokens) == 2
        assert tokens[0].address == "0xToken1"
        assert tokens[0].name == "Token 1"
        assert tokens[0].decimals == 18
        assert tokens[1].logo_uri is None


def test_get_token(service):
    token_address = "0xToken"
    with requests_mock.Mocker() as m:
        m.get(
            f"https://safe-transaction-mainnet.safe.global/v1/tokens/{token_address}/",
            json={
                "address": token_address,
                "name": "Token",
                "symbol": "TKN",
                "decimals": 18,
                "logoUri": "https://example.com/logo.png",
            },
        )
        token = service.get_token(token_address)
        assert token.address == token_address
        assert token.symbol == "TKN"
        assert token.decimals == 18


def test_decode_data(service):
    data = "0x123456"
    with requests_mock.Mocker() as m:
        m.post(
            "https://safe-transaction-mainnet.safe.global/v1/data-decoder/",
            json={
                "method": "transfer",
                "parameters": [
                    {"name": "to", "type": "address", "value": "0xRecipient"},
                    {"name": "value", "type": "uint256", "value": "100"},
                ],
            },
        )
        decoded = service.decode_data(data)
        assert decoded.method == "transfer"
        assert len(decoded.parameters) == 2
        assert decoded.parameters[0]["value"] == "0xRecipient"
