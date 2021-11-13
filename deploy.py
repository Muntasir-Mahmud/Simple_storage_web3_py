import json

from solcx import compile_standard, install_solc

with open("./SimpleStorage.sol", "r") as file:
    simple_storage_file = file.read()

install_solc("0.6.0")

# Compile Our solidity
compile_sol = compile_standard(
    {
        "language": "Solidity",
        "sources": {"SimpleSrorage.sol": {"content": simple_storage_file}},
        "settings": {
            "outputSelection": {
                "*": {"*": ["abi", "metadata", "evm.bytecode", "evm.sourceMap"]}
            }
        },
    },
    solc_version="0.6.0",
)

with open("compiled-code.json", "w") as file:
    json.dump(compile_sol, file)


# get Bytecode
bytecode = compile_sol["contracts"]["SimpleStorage.sol"]["SimpleStorage"]["evm"][
    "bytecode"
]["object"]

# get ABI
abi = compile_sol["contracts"]["SimpleStorage.sol"]["SimpleStorage"]["abi"]
