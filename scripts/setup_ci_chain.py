import time
from pathlib import Path

from web3 import Web3

# Addresses expected by safe-kit tests (Gnosis Safe v1.3.0)
SAFE_SINGLETON_ADDRESS = "0xd9Db270c1B5E3Bd161E8c8503c55cEABeE709552"
SAFE_PROXY_FACTORY_ADDRESS = "0xa6B71E26C5e0845f74c812102Ca7114b6a896AB2"

# Bytecodes directory
BYTECODES_DIR = Path(__file__).parent / "bytecodes"


def load_bytecode(filename: str) -> str:
    """Load bytecode from a file in the bytecodes directory."""
    filepath = BYTECODES_DIR / filename
    if not filepath.exists():
        raise FileNotFoundError(f"Bytecode file not found: {filepath}")
    return filepath.read_text().strip()


def wait_for_node(w3, attempts=10, delay=1):
    for _ in range(attempts):
        if w3.is_connected():
            return True
        time.sleep(delay)
    return False


def deploy_contracts():
    print("Connecting to Anvil node...")
    w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:8545"))

    if not wait_for_node(w3):
        print("Error: Could not connect to Anvil node.")
        exit(1)

    print("Connected. Deploying contracts via anvil_setCode...")

    # Load bytecodes from files
    proxy_factory_bytecode = load_bytecode("proxy_factory.txt")
    safe_singleton_bytecode = load_bytecode("safe_singleton.txt")

    # Deploy Proxy Factory
    print(f"Setting code for Proxy Factory at {SAFE_PROXY_FACTORY_ADDRESS}")
    success = w3.provider.make_request(
        "anvil_setCode", [SAFE_PROXY_FACTORY_ADDRESS, proxy_factory_bytecode]
    )
    if not success:
        print("Failed to set code for Proxy Factory")
        exit(1)

    # Deploy Safe Singleton
    print(f"Setting code for Safe Singleton at {SAFE_SINGLETON_ADDRESS}")
    success = w3.provider.make_request(
        "anvil_setCode", [SAFE_SINGLETON_ADDRESS, safe_singleton_bytecode]
    )
    if not success:
        print("Failed to set code for Safe Singleton")
        exit(1)

    # Verify
    code_factory = w3.eth.get_code(SAFE_PROXY_FACTORY_ADDRESS)
    code_singleton = w3.eth.get_code(SAFE_SINGLETON_ADDRESS)

    if len(code_factory) > 2 and len(code_singleton) > 2:
        print("Contracts successfully deployed!")
    else:
        print("Error: Contract deployment failed verification.")
        print(f"Factory Code Length: {len(code_factory)}")
        print(f"Singleton Code Length: {len(code_singleton)}")
        exit(1)


if __name__ == "__main__":
    deploy_contracts()
