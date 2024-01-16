// SPDX-License-Identifier: MIT

pragma solidity ^0.8.20;

contract EtherBridge {
    event LockEvent(address addr, uint256 value);
    event ReleaseEvent(address addr, uint256 value, bytes32 txhash);

    address public committee;
    address public operator;
    bool public live = true;

    constructor(address _committee) {
        committee = _committee;
        operator = msg.sender;
    }

    function change_committee(address new_committee) public {
        if (msg.sender == address(committee))
            committee = new_committee;
    }

    function change_operator(address new_operator) public {
        if (msg.sender == address(committee))
            operator = new_operator;
    }

    function shutdown() public {
        if (msg.sender == address(committee))
            live = false;
    }

    function lock() public payable {
        require(msg.value > 0, "Must send some Ether to lock the value");
        emit LockEvent(msg.sender, msg.value);
    }

    function release(address payable recipient, uint256 amount, bytes32 txhash) public {
        require(msg.sender == operator, "Only operator can release");
        require(address(this).balance >= amount, "No enough locked value to send");
        emit ReleaseEvent(recipient, amount, txhash);
    }

}

