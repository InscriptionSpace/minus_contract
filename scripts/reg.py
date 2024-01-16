
from brownie import MinusCommittee
from brownie import accounts as a

def main():
    MinusCommittee.deploy({'from':a[0], 'gas_price': 875000000})
    # MinusCommittee.at('0x5FbDB2315678afecb367f032d93F642f64180aa3')

    MinusCommittee[0].add_member(a[1], {'from':a[0], 'gas_price': 875000000})
    print(MinusCommittee[0].count_members())
    # MinusCommittee[0].remove_member(a[0], {'from':a[0], 'gas_price': 875000000})
    # print(MinusCommittee[0].count_members())

    MinusCommittee[0].add_member(a[2], {'from':a[0], 'gas_price': 875000000})
    print(MinusCommittee[0].count_members())
    MinusCommittee[0].add_member(a[2], {'from':a[1], 'gas_price': 875000000})
    print(MinusCommittee[0].count_members())

    # print(MinusCommittee[0].member_add_proposals(a[1], 0))
    # print(MinusCommittee[0].member_add_proposals(a[2], 0))
    # print(MinusCommittee[0].member_add_proposals(a[2], 1))
    
    MinusCommittee[0].new_symbol_proposal(b'HUB2', MinusCommittee[0], {'from':a[1], 'gas_price': 875000000})
    print(MinusCommittee[0].symbol_proposals(2))
