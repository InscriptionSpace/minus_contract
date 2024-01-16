
from brownie import accounts as a
from brownie import MinusCommittee, EtherBridge

def test_reg_change_operator():
    for i in MinusCommittee:
        MinusCommittee.remove(i)
    for i in EtherBridge:
        EtherBridge.remove(i)

    MinusCommittee.deploy({'from':a[0], 'gas_price': 875000000})
    EtherBridge.deploy(MinusCommittee[0], {'from':a[0], 'gas_price': 875000000})
    assert EtherBridge[0].owner() == MinusCommittee[0]

    ret = MinusCommittee[0].new_change_operator_proposal(EtherBridge[0], a[1], {'from':a[0], 'gas_price': 875000000})
    assert ret.return_value == 1
    # assert MinusCommittee[0].change_operator_proposal_votes(1, 0)
    assert MinusCommittee[0].change_operator_proposals(0)
    ret = MinusCommittee[0].vote_change_operator_proposal(1, {'from':a[0], 'gas_price': 875000000})

    # assert EtherBridge[0].operator() == a[0]
    assert EtherBridge[0].operator() == a[1]

def test_reg_change_operator_2_members():
    for i in MinusCommittee:
        MinusCommittee.remove(i)
    for i in EtherBridge:
        EtherBridge.remove(i)

    MinusCommittee.deploy({'from':a[0], 'gas_price': 875000000})
    MinusCommittee[0].add_member(a[1], {'from':a[0], 'gas_price': 875000000})
    assert MinusCommittee[0].committee(0) == a[0]
    assert MinusCommittee[0].committee(1) == a[1]

    EtherBridge.deploy(MinusCommittee[0], {'from':a[0], 'gas_price': 875000000})
    assert EtherBridge[0].owner() == MinusCommittee[0]

    ret = MinusCommittee[0].new_change_operator_proposal(EtherBridge[0], a[1], {'from':a[0], 'gas_price': 875000000})
    assert ret.return_value == 1
    assert MinusCommittee[0].change_operator_proposals(0)[0] == 1
    ret = MinusCommittee[0].vote_change_operator_proposal(1, {'from':a[0], 'gas_price': 875000000})
    # assert MinusCommittee[0].change_operator_proposal_votes(1, 0)
    # ret = MinusCommittee[0].vote_change_operator_proposal(1, {'from':a[0], 'gas_price': 875000000})

    # assert EtherBridge[0].operator() == a[0]
    assert EtherBridge[0].operator() == a[1]


def test_reg_change_operator_3_members():
    for i in MinusCommittee:
        MinusCommittee.remove(i)
    for i in EtherBridge:
        EtherBridge.remove(i)

    MinusCommittee.deploy({'from':a[0], 'gas_price': 875000000})
    MinusCommittee[0].add_member(a[1], {'from':a[0], 'gas_price': 875000000})
    assert MinusCommittee[0].committee(0) == a[0]
    assert MinusCommittee[0].committee(1) == a[1]

    MinusCommittee[0].add_member(a[2], {'from':a[0], 'gas_price': 875000000})
    MinusCommittee[0].add_member(a[2], {'from':a[1], 'gas_price': 875000000})
    assert MinusCommittee[0].committee(2) == a[2]

    EtherBridge.deploy(MinusCommittee[0], {'from':a[0], 'gas_price': 875000000})
    assert EtherBridge[0].owner() == MinusCommittee[0]

    ret = MinusCommittee[0].new_change_operator_proposal(EtherBridge[0], a[1], {'from':a[0], 'gas_price': 875000000})
    assert ret.return_value == 1
    assert MinusCommittee[0].change_operator_proposals(0)[0] == 1
    ret = MinusCommittee[0].vote_change_operator_proposal(1, {'from':a[1], 'gas_price': 875000000})
    assert MinusCommittee[0].change_operator_proposal_votes(1, 0)
    ret = MinusCommittee[0].vote_change_operator_proposal(1, {'from':a[2], 'gas_price': 875000000})

    # assert EtherBridge[0].operator() == a[0]
    assert EtherBridge[0].operator() == a[1]
