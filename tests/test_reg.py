
from brownie import accounts as a
from brownie import SymbolReg, EtherBridge

def test_reg_change_operator():
    SymbolReg.deploy({'from':a[0], 'gas_price': 875000000})
    # SymbolReg[0].add_member(a[1], {'from':a[0], 'gas_price': 875000000})
    EtherBridge.deploy(SymbolReg[0], {'from':a[0], 'gas_price': 875000000})
    assert EtherBridge[0].owner() == SymbolReg[0]

    ret = SymbolReg[0].new_change_operator_proposal(EtherBridge[0], a[1], {'from':a[0], 'gas_price': 875000000})
    assert ret.return_value == 1
    # assert SymbolReg[0].change_operator_proposal_votes(1, 0)
    assert SymbolReg[0].change_operator_proposals(0)
    ret = SymbolReg[0].vote_change_operator_proposal(1, {'from':a[0], 'gas_price': 875000000})

    # assert EtherBridge[0].operator() == a[0]
    assert EtherBridge[0].operator() == a[1]
