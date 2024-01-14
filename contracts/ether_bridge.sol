// SPDX-License-Identifier: MIT
// OpenZeppelin Contracts (last updated v5.0.0) (token/ERC20/IERC20.sol)

pragma solidity ^0.8.20;

contract EtherBridge {
    event LockEvent(address addr, uint256 value);
    event ReleaseEvent(address addr, uint256 value, bytes32 txhash);

    address public owner;
    address public operator;
    bool public live = true;

    constructor(address _owner) {
        owner = _owner;
        operator = msg.sender;
    }

    function change_owner(address new_owner) public {
        if (msg.sender == address(owner))
            owner = new_owner;
    }

    function change_operator(address new_operator) public {
        if (msg.sender == address(owner))
            operator = new_operator;
    }

    function shutdown() public {
        if (msg.sender == address(owner))
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

