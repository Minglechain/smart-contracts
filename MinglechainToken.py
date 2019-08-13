from ontology.interop.System.Storage import GetContext, Get, Put, Delete
from ontology.interop.System.Runtime import Notify, CheckWitness, GetTime
from ontology.interop.System.Action import RegisterAction
from ontology.builtins import concat
from ontology. libont import bytearray_reverse
from ontology.interop.Ontology.Runtime import Base58ToAddress
from ontology.interop.System.ExecutionEngine import GetExecutingScriptHash, GetScriptContainer
from ontology.interop.System.Transaction import GetTransactionHash

TransferEvent = RegisterAction("transfer", "from", "to", "amount")
ApprovalEvent = RegisterAction("approval", "owner", "spender", "amount")
ReleaseEvent = RegisterAction("release", "txHash")

NAME = 'Minglechain Token'
SYMBOL = 'MC'
DECIMALS = 6
FACTOR = 1000000 # 1 million
OWNER = Base58ToAddress("AVrN4QvcSLwtoXy925JmtAEebZ3wVDqcr9") # Same as Team
TOTAL_AMOUNT = 100000000
BALANCE_PREFIX = bytearray(b'\x01')
APPROVE_PREFIX = b'\x02'
SUPPLY_KEY = 'TotalSupply'

EIOCAP_AMOUNT      = 50000000
PRESALECAP_AMOUNT  = 10000000
REFERRALCAP_AMOUNT = 10000000
TEAMCAP_AMOUNT     = [ 6000000,
                       6000000,
                       6000000,
                       6000000,
                       6000000
                       ]
UNLOCK_HASH_PERFIX = "Unlock"

EIO_ADDRESS = Base58ToAddress("APT362oHqpVMMa7tKcPbQA6VoGUJ1i9uuk")
PRESALE_ADDRESS = Base58ToAddress("AGFxBrm8MwPrzYLW6fB7vSXumhZMcJeVxQ")
REFERRAL_ADDRESS = Base58ToAddress("AbNifuJegzS6UiHAtwcPi4xy93cbRpYv5D")
TEAM_ADDRESS = Base58ToAddress("AVrN4QvcSLwtoXy925JmtAEebZ3wVDqcr9")

TEAMLOCK_END = [ 1569888000, # 1 October 2019 0:00:00 GMT
                 1601510400, # 1 October 2020 0:00:00 GMT
                 1633046400, # 1 October 2021 0:00:00 GMT
                 1664582400, # 1 October 2022 0:00:00 GMT
                 1696118400  # 1 October 2023 0:00:00 GMT
                 ]

SELF_ADDRESS = GetExecutingScriptHash()

def Main(operation, args):
    """
    :param operation:
    :param args:
    :return:
    """
    # 'init' has to be invokded first after deploying the contract to store the necessary and important info in the blockchain
    if operation == 'init':
        return init()
    if operation == 'name':
        return name()
    if operation == 'symbol':
        return symbol()
    if operation == 'decimals':
        return decimals()
    if operation == 'totalSupply':
        return totalSupply()
    if operation == 'balanceOf':
        assert (len(args) == 1)
        acct = args[0]
        return balanceOf(acct)
    if operation == 'transfer':
        assert (len(args) == 3)
        from_acct = args[0]
        to_acct = args[1]
        amount = args[2]
        return transfer(from_acct,to_acct,amount)
    if operation == 'transferMulti':
        return transferMulti(args)
    if operation == 'transferFrom':
        assert (len(args) == 4)
        spender = args[0]
        from_acct = args[1]
        to_acct = args[2]
        amount = args[3]
        return transferFrom(spender,from_acct,to_acct,amount)
    if operation == 'approve':
        assert (len(args) == 3)
        owner  = args[0]
        spender = args[1]
        amount = args[2]
        return approve(owner,spender,amount)
    if operation == 'allowance':
        assert (len(args) == 2)
        owner = args[0]
        spender = args[1]
        return allowance(owner,spender)
    if operation == 'burn':
        assert (len(args) == 1)
        amount = args[0]
        return burn(amount)
    if operation == 'teamRelease':
        return teamRelease()
    if operation == "getReleaseHash":
        assert (len(args) == 1)
        timeLockEnd = args[0]
        return getReleaseHash(timeLockEnd)
    return False

def init():
    """
    initialize the contract, put some important info into the storage in the blockchain
    :return:
    """
    assert (len(OWNER) == 20)
    assert (not Get(GetContext(), SUPPLY_KEY))
    total = TOTAL_AMOUNT * FACTOR
    eoicap = EIOCAP_AMOUNT * FACTOR
    presalecap = PRESALECAP_AMOUNT * FACTOR
    referralcap = REFERRALCAP_AMOUNT * FACTOR

    Put(GetContext(), SUPPLY_KEY, total)
    Put(GetContext(), concat(BALANCE_PREFIX,EIO_ADDRESS), eoicap)
    Put(GetContext(), concat(BALANCE_PREFIX,PRESALE_ADDRESS), presalecap)
    Put(GetContext(), concat(BALANCE_PREFIX,REFERRAL_ADDRESS), referralcap)


    TransferEvent("", EIO_ADDRESS, eoicap)
    TransferEvent("", PRESALE_ADDRESS, presalecap)
    TransferEvent("", REFERRAL_ADDRESS, referralcap)

    # The locked token are temporarily locked within the contract while belonging to the contract
    lockedAmount = total - eoicap - presalecap - referralcap
    Put(GetContext(), concat(BALANCE_PREFIX, SELF_ADDRESS), lockedAmount)
    TransferEvent("", SELF_ADDRESS, lockedAmount)
    return True


def name():
    """
    :return: name of the token
    """
    return NAME


def symbol():
    """
    :return: symbol of the token
    """
    return SYMBOL


def decimals():
    """
    :return: the decimals of the token
    """
    return DECIMALS


def totalSupply():
    """
    :return: the total supply of the token
    """
    return Get(GetContext(), SUPPLY_KEY)


def balanceOf(account):
    """
    :param account:
    :return: the token balance of account
    """
    assert (len(account) == 20)
    return Get(GetContext(), concat(BALANCE_PREFIX,account))


def transfer(from_acct, to_acct, amount):
    """
    Transfer amount of tokens from from_acct to to_acct
    :param from_acct: the account from which the amount of tokens will be transferred
    :param to_acct: the account to which the amount of tokens will be transferred
    :param amount: the amount of the tokens to be transferred, >= 0
    :return: True means success, False or raising exception means failure.
    """
    assert (len(to_acct) == 20 and len(from_acct) == 20)
    assert (amount >= 0)
    assert (CheckWitness(from_acct))
    assert (_transfer(from_acct, to_acct, amount))
    return True

def _transfer(_from, _to, _amount):
    fromKey = concat(BALANCE_PREFIX, _from)
    fromBalance = Get(GetContext(), fromKey)
    assert (_amount <= fromBalance)
    if _amount == fromBalance:
        Delete(GetContext(), concat(BALANCE_PREFIX, _from))
    else:
        Put(GetContext(), fromKey, fromBalance - _amount)
    Put(GetContext(), concat(BALANCE_PREFIX, _to), balanceOf(_to) + _amount)
    TransferEvent(_from, _to, _amount)
    return True


def transferMulti(args):
    """
    :param args: the parameter is an array, containing element like [from, to, amount]
    :return: True means success, False or raising exception means failure.
    """
    for p in args:
        assert (len(p) == 3)
        assert (transfer(p[0], p[1], p[2]))
    return True


def approve(owner,spender,amount):
    """
    owner allow spender to spend amount of token from owner account
    Note here, the amount should be less than the balance of owner right now.
    :param owner:
    :param spender:
    :param amount: amount>=0
    :return: True means success, False or raising exception means failure.
    """
    assert (len(spender) == 20 and len(owner) == 20)
    assert (amount >=0 and amount <= balanceOf((owner)))
    assert (CheckWitness(owner))
    approveKey = concat(concat(APPROVE_PREFIX,owner),spender)
    Put(GetContext(), approveKey, amount)
    ApprovalEvent(owner, spender, amount)
    return True


def transferFrom(spender,from_acct,to_acct,amount):
    """
    spender spends amount of tokens on the behalf of from_acct, spender makes a transaction of amount of tokens
    from from_acct to to_acct
    :param spender:
    :param from_acct:
    :param to_acct:
    :param amount:
    :return:
    """
    assert (len(spender) == 20 and len(from_acct) == 20 and len(to_acct) == 20)
    assert (CheckWitness(spender))

    fromKey = concat(BALANCE_PREFIX, from_acct)
    fromBalance = Get(GetContext(), fromKey)
    assert (amount <= fromBalance and amount >= 0)
    approveKey = concat(concat(APPROVE_PREFIX, from_acct), spender)
    approvedAmount = Get(GetContext(), approveKey)
    toKey = concat(BALANCE_PREFIX, to_acct)
    assert (amount <= approvedAmount)
    if amount == approvedAmount:
        Delete(GetContext(), approveKey)
        Put(GetContext(), fromKey, fromBalance - amount)
    else:
        Put(GetContext(), approveKey, approvedAmount - amount)
        Put(GetContext(), fromKey, fromBalance - amount)

    toBalance = Get(GetContext(), toKey)
    Put(GetContext(), toKey, toBalance + amount)
    TransferEvent(from_acct, to_acct, amount)
    return True


def allowance(owner,spender):
    """
    check how many token the spender is allowed to spend from owner account
    :param owner: token owner
    :param spender:  token spender
    :return: the allowed amount of tokens
    """
    key = concat(concat(APPROVE_PREFIX, owner), spender)
    return Get(GetContext(), key)

def burn(amount):
    """
    Burns the amount of Minglechain token from the owner's address.
    :param _amount: MC amount to burn.
    """
    # only owner can burn the token
    assert (CheckWitness(OWNER))
    ownerBalance = balanceOf(OWNER)
    total = totalSupply()
    assert (total >= amount and ownerBalance >= amount and amount >= 0)
    newTotal = total - amount
    # update total supply
    Put(GetContext(), SUPPLY_KEY, newTotal)
    # update the owner's balance
    Put(GetContext(), concat(BALANCE_PREFIX, OWNER), ownerBalance - amount)
    TransferEvent(OWNER, "", amount)
    return True


def teamRelease():
    assert (CheckWitness(OWNER))
    now = GetTime()

    index = 0
    tryRelease = True
    while tryRelease == True and index < len(TEAMLOCK_END):
        if now > TEAMLOCK_END[index]:
            if not getReleaseHash(TEAMLOCK_END[index]):
                # Release token to team
                assert (_transfer(SELF_ADDRESS, TEAM_ADDRESS, TEAMCAP_AMOUNT[index] * FACTOR))
                txHash = bytearray_reverse(GetTransactionHash(GetScriptContainer()))
                Put(GetContext(), concat(UNLOCK_HASH_PERFIX, TEAMLOCK_END[index]), txHash)
                ReleaseEvent(txHash)
            index += 1
        else:
            tryRelease = False

    return True


def getReleaseHash(teamLockEnd):
    return Get(GetContext(), concat(UNLOCK_HASH_PERFIX, teamLockEnd))
