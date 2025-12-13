import pytest
import requests_mock

from safe_kit.service import SafeServiceClient
from safe_kit.types import SafeTransactionData


@pytest.fixture
def service():
    return SafeServiceClient("https://safe-transaction-mainnet.safe.global")

def test_get_service_info(service):
    with requests_mock.Mocker() as m:
        m.get("https://safe-transaction-mainnet.safe.global/v1/about/", json={
            "name": "Safe Transaction Service",
            "version": "1.0.0",
            "api_version": "v1",
            "secure": True,
            "settings": {}
        })
        info = service.get_service_info()
        assert info.name == "Safe Transaction Service"

def test_get_pending_transactions(service):
    safe_address = "0xSafeAddress"
    with requests_mock.Mocker() as m:
        m.get(
            f"https://safe-transaction-mainnet.safe.global/v1/safes/{safe_address}/multisig-transactions/?executed=false&trusted=true",
            json={"results": [{
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
                "signatures": None
            }]}
        )
        txs = service.get_pending_transactions(safe_address)
        assert len(txs) == 1
        assert txs[0].safe_tx_hash == "0xHash"

def test_get_multisig_transactions(service):
    safe_address = "0xSafeAddress"
    with requests_mock.Mocker() as m:
        m.get(
            f"https://safe-transaction-mainnet.safe.global/v1/safes/{safe_address}/multisig-transactions/?executed=true&trusted=true&ordering=-nonce&limit=10&offset=0",
            json={"results": [{
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
                "signatures": None
            }]}
        )
        txs = service.get_multisig_transactions(
            safe_address,
            executed=True,
            trust=True,
            ordering="-nonce",
            limit=10,
            offset=0
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
        nonce=1
    )
    
    with requests_mock.Mocker() as m:
        m.post(
            f"https://safe-transaction-mainnet.safe.global/v1/safes/{safe_address}/multisig-transactions/",
            status_code=201
        )
        service.propose_transaction(
            safe_address=safe_address,
            safe_tx_data=tx_data,
            safe_tx_hash="0xHash",
            sender_address="0xSender",
            signature="0xSig"
        )
        
        assert m.called
        assert m.last_request.json()["contractTransactionHash"] == "0xHash"

def test_confirm_transaction(service):
    safe_tx_hash = "0xHash"
    with requests_mock.Mocker() as m:
        m.post(
            f"https://safe-transaction-mainnet.safe.global/v1/multisig-transactions/{safe_tx_hash}/confirmations/",
            status_code=201
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
