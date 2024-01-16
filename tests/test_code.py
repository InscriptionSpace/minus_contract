
from brownie import accounts as a
from brownie import MinusCommittee, EtherBridge

def test_code():
    for i in MinusCommittee:
        MinusCommittee.remove(i)
    for i in EtherBridge:
        EtherBridge.remove(i)

    MinusCommittee.deploy({'from':a[0], 'gas_price': 875000000})
    EtherBridge.deploy(MinusCommittee[0], {'from':a[0], 'gas_price': 875000000})
    assert EtherBridge[0].committee() == MinusCommittee[0]

    ret = MinusCommittee[0].new_code_proposal(b'test', b'test', {'from':a[0], 'gas_price': 875000000})
    assert ret.return_value == 1
    # assert MinusCommittee[0].change_operator_proposal_votes(1, 0)
    assert MinusCommittee[0].code_proposals(0)
    ret = MinusCommittee[0].vote_code_proposal(1, {'from':a[0], 'gas_price': 875000000})

    assert MinusCommittee[0].code_proposal_votes(1, 0) == a[0]
