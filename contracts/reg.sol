// SPDX-License-Identifier: MIT
// OpenZeppelin Contracts (last updated v5.0.0) (token/ERC20/IERC20.sol)

pragma solidity ^0.8.20;


interface IBridge {
    function change_operator(address new_operator) external;
}

contract SymbolReg {
    address[] public committee;
    mapping(address=>address[]) public member_add_proposals;
    mapping(address=>address[]) public member_remove_proposals;

    uint proposal_no_counter = 0;

    struct Symbol {
        uint no;
        bytes sym;
        address addr;
    }
    Symbol[] public symbol_proposals;
    mapping(uint=>address[]) public symbol_proposal_votes;
    mapping(bytes=>address) public symbols;

    struct Code {
        uint no;
        bytes op;
        bytes code;
    }
    Code[] public code_proposals;
    mapping(uint=>address[]) public code_proposal_votes;
    mapping(string=>bytes) public codes;

    struct ChangeOperator {
        uint no;
        address bridge;
        address operator;
    }
    mapping(uint=>address[]) public change_operator_proposal_votes;
    ChangeOperator[] public change_operator_proposals;

    constructor() {
        committee.push(msg.sender);
    }
    //fallback() external payable{}

    function new_symbol_proposal(bytes calldata symbol, address addr) public {
        bool auth = false;
        for (uint p = 0; p < committee.length; p++) {
            if (committee[p] == msg.sender) {
                auth = true;
            }
        }
        require(auth, "A member can propose to change operator");

        proposal_no_counter += 1;
        symbol_proposals.push(Symbol(proposal_no_counter, symbol, addr));
    }
    function vote_symbol_proposal(bytes calldata symbol, address addr) public {
        bool auth = false;
        for (uint p = 0; p < committee.length; p++) {
            if (committee[p] == msg.sender) {
                auth = true;
            }
        }
        require(auth, "A member can propose to change operator");

        symbols[symbol] = addr;
    }

    function new_code_proposal(bytes calldata op, bytes calldata code) public {
        bool auth = false;
        for (uint p = 0; p < committee.length; p++) {
            if (committee[p] == msg.sender) {
                auth = true;
            }
        }
        require(auth, "A member can propose to change operator");

        proposal_no_counter += 1;
        code_proposals.push(Code(proposal_no_counter, op, code));
    }
    function vote_code_proposal(bytes calldata op, address addr) public {
        bool auth = false;
        for (uint p = 0; p < committee.length; p++) {
            if (committee[p] == msg.sender) {
                auth = true;
            }
        }
        require(auth, "A member can propose to change operator");


    }

    function new_change_operator_proposal(address bridge, address operator) public returns(uint) {
        bool auth = false;
        for (uint p = 0; p < committee.length; p++) {
            if (committee[p] == msg.sender) {
                auth = true;
            }
        }
        require(auth, "A member can propose to change operator");

        proposal_no_counter += 1;
        change_operator_proposals.push(ChangeOperator(proposal_no_counter, bridge, operator));
        return proposal_no_counter;
    }
    function vote_change_operator_proposal(uint no) public {
        bool auth = false;
        for (uint p = 0; p < committee.length; p++) {
            if (committee[p] == msg.sender) {
                auth = true;
            }
        }
        require(auth, "A member can vote to change operator");

        for (uint p = 0; p < change_operator_proposals.length; p++) {
            if (change_operator_proposals[p].no == no) {
                for (uint q = 0; q < change_operator_proposal_votes[no].length; q++) {
                    return;
                }
            }
        }
        change_operator_proposal_votes[no].push(msg.sender);

        if(change_operator_proposal_votes[no].length >= committee.length * 2 / 3){
            for (uint p = 0; p < change_operator_proposals.length; p++) {
                if (change_operator_proposals[p].no == no){
                    address bridge = change_operator_proposals[p].bridge;
                    address operator = change_operator_proposals[p].operator;
                    IBridge(bridge).change_operator(operator);

                    if (p + 1 != change_operator_proposals.length){
                        change_operator_proposals[p] = change_operator_proposals[change_operator_proposals.length-1];
                    }
                    change_operator_proposals.pop();

                    //TODO: clean up change_operator_proposal_votes[no]
                    for (uint q = 0; q < change_operator_proposal_votes[no].length; q++) {
                        change_operator_proposal_votes[no].pop();
                    }
                    delete change_operator_proposal_votes[no];

                    return;
                }
            }
        }
    }

    function add_member(address member) public {
        bool auth = false;
        for (uint p = 0; p < committee.length; p++) {
            if (committee[p] == msg.sender) {
                auth = true;
            }
        }
        require(auth, "A member can proposal add member");

        for (uint p = 0; p < member_add_proposals[member].length; p++) {
            if (member_add_proposals[member][p] == msg.sender) {
                return;
            }
        }
        member_add_proposals[member].push(msg.sender);
        if (member_add_proposals[member].length == committee.length) {
            committee.push(member);

            //TODO: clean up member_add_proposals[member]
            for (uint p = 0; p < member_add_proposals[member].length; p++) {
                member_add_proposals[member].pop();
            }
        }
    }

    function remove_member(address member) public {
        bool auth = false;
        int index = -1;
        for (uint p = 0; p < committee.length; p++) {
            if (committee[p] == msg.sender) {
                auth = true;
            }
            if (committee[p] == member) {
                index = int(p);
            }
        }
        require(auth, "A member can proposal remove member");
        require(index > -1, "Member not in committee");

        for (uint p = 0; p < member_remove_proposals[member].length; p++) {
            if (member_remove_proposals[member][p] == msg.sender) {
                return;
            }
        }
        member_remove_proposals[member].push(msg.sender);

        if(member_remove_proposals[member].length >= committee.length * 2 / 3){
            if (uint(index) + 1 != committee.length){
                committee[uint(index)] = committee[committee.length-1];
            }
            committee.pop();

            //TODO: clean up member_remove_proposals[member]
            for (uint p = 0; p < member_remove_proposals[member].length; p++) {
                member_remove_proposals[member].pop();
            }
            delete member_remove_proposals[member];
        }
    }

    function count_members() public view returns(uint) {
        return committee.length;
    }
}
