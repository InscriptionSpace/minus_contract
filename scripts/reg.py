
from brownie import SymbolReg
from brownie import accounts as a

def main():
    SymbolReg.deploy({'from':a[0], 'gas_price': 875000000})
    # SymbolReg.at('0x5FbDB2315678afecb367f032d93F642f64180aa3')

    SymbolReg[0].add_member(a[1], {'from':a[0], 'gas_price': 875000000})
    print(SymbolReg[0].count_members())
    # SymbolReg[0].remove_member(a[0], {'from':a[0], 'gas_price': 875000000})
    # print(SymbolReg[0].count_members())

    SymbolReg[0].add_member(a[2], {'from':a[0], 'gas_price': 875000000})
    print(SymbolReg[0].count_members())
    SymbolReg[0].add_member(a[2], {'from':a[1], 'gas_price': 875000000})
    print(SymbolReg[0].count_members())

    # print(SymbolReg[0].member_add_proposals(a[1], 0))
    # print(SymbolReg[0].member_add_proposals(a[2], 0))
    # print(SymbolReg[0].member_add_proposals(a[2], 1))
    
    SymbolReg[0].new_symbol_proposal(b'HUB2', SymbolReg[0], {'from':a[1], 'gas_price': 875000000})
    print(SymbolReg[0].symbol_proposals(2))
