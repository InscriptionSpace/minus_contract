
from brownie import accounts as a
from brownie import MinusCommittee, EtherBridge

def test_symbol():
    for i in MinusCommittee:
        MinusCommittee.remove(i)
    for i in EtherBridge:
        EtherBridge.remove(i)

    MinusCommittee.deploy({'from':a[0], 'gas_price': 875000000})
    EtherBridge.deploy(MinusCommittee[0], {'from':a[0], 'gas_price': 875000000})
    assert EtherBridge[0].committee() == MinusCommittee[0]

    ret = MinusCommittee[0].new_symbol_proposal(b'ETH', EtherBridge[0], {'from':a[0], 'gas_price': 875000000})
    assert ret.return_value == 1
    # assert MinusCommittee[0].change_operator_proposal_votes(1, 0)
    assert MinusCommittee[0].symbol_proposals(0)
    ret = MinusCommittee[0].vote_symbol_proposal(1, {'from':a[0], 'gas_price': 875000000})

    # assert MinusCommittee[0].code_proposal_votes(1, 0) == a[0]
