<div align="center">
    <img src="./misc/abstract.jpg" style="width: 350px">
    <h1>StarkNet Account Abstraction</h1>
</div>

### Exercises

|Topic|Code|
|---|---|
|hello account world!|[hello](contracts/hello)|
|signature handling|[signature](contracts/signature)|
|multiple contract calls|[multicall](contracts/multicall)|
|multiple signatures|[multisig](contracts/multisig)|
|account abstraction concepts|[abstraction](contracts/abstraction)|

## Setup

```bash
# assumes you're using python3.7
python3.7 -m venv ~/cairo_venv
source ~/cairo_venv/bin/activate
pip3 install --upgrade starknet.py
pip3 install --upgrade pytest pytest-asyncio
pip3 install --upgrade cairo-lang

# libraries for abstraction demo
git clone git@github.com:starkware-libs/cairo-examples.git ~/cairo_venv/lib/python3.7/site-packages/cairo_examples
find ~/cairo_venv/lib/python3.7/site-packages/cairo_examples/secp -type f -exec sed -i -e 's/from big/from cairo_examples.secp.big/g' {} \;
find ~/cairo_venv/lib/python3.7/site-packages/cairo_examples/secp -type f -exec sed -i -e 's/from secp/from cairo_examples.secp.secp/g' {} \;

# set environment variables
export STARKNET_NETWORK=alpha-goerli
export VALIDATOR_ADDRESS=0x0613847a0c5f8f0d11d7e6d2493aeab4a79ce9867bb3fad9842c936f2b044478
```

This tutorial utilizes [starknet.py](https://github.com/software-mansion/starknet.py). Each exercises comes with a helper python script for mission statements, contract deployments and [validator](./contracts/validator) interactions. Deploying contracts can take some time, so we have added a cache of deployed addresses at `contracts/account.json`. If you have made a change to your contract and which to deploy fresh simply delete the line from the accounts file, or set the `ACCOUNT_CACHE` environment variable to false.

The contract stubs and helper scripts will be mising crucial information for you to figure out. The excercises will get increasingly harder as we go. If you hit a roadblock the first place to look is the deployed validator contract and what it is checking for.

***!!!DON'T CHEAT!!!***

...but if you need help you can reference the [Open Zeppelin](https://github.com/OpenZeppelin/cairo-contracts/tree/main/src/openzeppelin/account) account contracts or `tests/<TOPIC>` branch of this repository.

## Walk Through

Accounts on StarkNet are deployed via an [Account Abstraction](https://perama-v.github.io/cairo/account-abstraction) model.

TL;DR:

***accounts on StarkNet are simply contracts***

The one caveat for account contract deployments is they must have a canonical entrypoint denoted with the selector `__execute__`

***...and that's it!***

Lets deploy and test the simplest account contract we can:

```bash
cd contracts/hello
python3 hello.py
```

The job of the account contract is to execute arbitrary business logic on behalf of a sepcific entity. This is why we see a similar pattern for most execute functions:

```bash
    # the contract address we which to execute our transaction on
    contract_address : felt
    
    # the entry point of that contract we wish to call
    selector : felt

    # different contracts will require varying lengths of calldata
    # so we pass these as an array
    calldata_len : felt
    calldata : felt*
```

### [Signatures](./contracts/signatures)

The StarkNet Account model differs from Ethereum [EOAs](https://ethereum.org/en/developers/docs/accounts/#externally-owned-accounts-and-key-pairs) in that there is no hard requirement for the account to be managed by a public/private key pair.

Account abstraction cares more about `who`(i.e. the contract address) rather than `how`(i.e. the signature).

This leaves the ECDSA signature scheme up to the developer and typically implemented using the [pedersen hash](https://docs.starknet.io/docs/Hashing/hash-functions) and native curve for signing:

```bash
cd contracts/signature
python3 signature_1.py
```

The `signature_1` contract itself has not concept of a public/private keypair. All the ECDSA signing was done "off-chain" and yet with Account abstraction we are still able to have a functioning account with a populated signature.

Let's couple the signing logic closer wtih the account:

***HINT: we have not yet implemented a [nonce](https://ethereum.org/en/developers/docs/accounts/#an-account-examined)***

```bash
cd contracts/signature
python3 signature_2.py
```

Although we are free to populate the signature field how we please, the StarkNet OS has a specific method for hashing [transaction data](https://docs.starknet.io/docs/Blocks/transactions#transaction-hash-1).

As this transaction hash encompasses all the relevant `tx_info` it is helpful to use this as the message_hash for account contracts to sign. The account owner is thereby acknowledging all of the relevant transaction information by signing:

```bash
cd contracts/signature
python3 signature_3.py
```

### [MultiCall](./contracts/multicall)

Now that we have implemented the vanilla ECDSA signing mechanisms lets see what account abstraction can really do.

A `multicall` aggregates the results from multiple contract calls. This reduces the number of seperate API Client or JSON-RPC requests that need to be sent. In addition it acts as an `atomic` invocation where all values are returned for the same block

There are many implementations of multicall that allow the caller flexibility in how they distribute and batch their transactions.

Let's implement a multicall account for StarkNet:

```bash
cd contracts/multicall
python3 multicall.py
```

### [MultiSig](./contracts/multisig)

A `multisig` or multiple signature wallet allows you to share security accross multiple signinging entities. You can think of them like bank vaults in that they require more than one key to unlock, or in this case authorize a transaction.

Multisigs are popular amongst DAOs and decentralized infrastructure because they reduces the need to depend on only a handful of actors.

The amount of signing keys that belong to the account and the ammount of keys required to authorize a transaction are purely implementation details.

Lets implement a `2/3 multisig` account(i.e. 2 signatures are required out of a total 3 signers for a transaction to be executed):

```bash
cd contracts/multisig
python3 multisig.py
```

### [Abstraction](./contracts/abstraction)

Since StarkNet accounts are simply accounts we can implement any signing mechanism we wish. Companies like [Web3Auth](https://medium.com/toruslabs/sign-in-with-starkware-711d48f2dbbd) are using this to create `Sign-In` architectures using your StarkNet account.

Discussions on novel account architecutres are popping up more and [more](https://vitalik.ca/general/2022/01/26/soulbound.html), and it looks to be an increasingly important tool the developer toolkit.

For an example of a unique account architecture we will build a contract that implements it's signatures scheme with the secp256k1 curve and sha256 instead of our native StarkNet curve:

```bash
cd contracts/abstraction
python3 abstraction.py
```