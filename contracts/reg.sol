
pragma solidity 0.8.23;

contract SymbolReg {
    address[] public committee;
    mapping(address=>address[]) public member_add_proposals;
    mapping(address=>address[]) public member_remove_proposals;

    struct Symbol {
        uint no;
        bytes sym;
        address addr;
    }

    struct Code {
        uint no;
        bytes op;
        bytes code;
    }

    uint proposal_no_counter = 0;
    Symbol[] public symbol_proposals;
    mapping(uint=>address[]) public symbol_proposal_votes;
    Code[] public code_proposals;
    mapping(uint=>address[]) public code_proposal_votes;

    mapping(bytes=>address) public symbols;
    mapping(string=>bytes) public codes;

    constructor() {
        committee.push(msg.sender);
    }
    fallback() external payable{}

    function new_symbol_proposal(bytes calldata symbol, address addr) public {
        proposal_no_counter += 1;
        symbol_proposals.push(Symbol(proposal_no_counter, symbol, addr));
    }
    function vote_code_proposal(bytes calldata symbol, address addr) public {
        symbols[symbol] = addr;
    }

    function new_code_proposal(string calldata op, bytes calldata code) public {
        proposal_no_counter += 1;
        codes[op] = code;
    }
    function vote_symbol_proposal(bytes calldata symbol, address addr) public {
        symbols[symbol] = addr;
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
            if (uint(index) + 1 == committee.length){
                committee.pop();
            }else{
                committee[uint(index)] = committee[committee.length-1];
                committee.pop();
            }

            //TODO: clean up member_remove_proposals[member]
            for (uint p = 0; p < member_remove_proposals[member].length; p++) {
                member_remove_proposals[member].pop();
            }
        }
    }

    function count_members() public view returns(uint) {
        return committee.length;
    }
}
