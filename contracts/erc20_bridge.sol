// SPDX-License-Identifier: MIT

pragma solidity 0.8.23;

import "./IERC20.sol";

contract Erc20Bridge {
    event LockEvent(address addr, uint256 value);

    uint256 public total;
    address public erc20_addr;
    address public committee;
    address public operator;
    bool public live = true;

    constructor(address _committee, address contract_addr) {
        erc20_addr = contract_addr;
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

    function lock(uint256 amount) public {
        require(amount > 0, "Must send token to lock the value");
        IERC20(erc20_addr).transferFrom(msg.sender, address(this), amount);
        total += amount;
        emit LockEvent(msg.sender, amount);
    }

    function release(address payable recipient, uint256 amount, bytes32 txhash) public {
        require(msg.sender == operator, "Only operator can release");
        require(total >= amount, "No enough locked value to send");
        IERC20(erc20_addr).transfer(recipient, amount);
        total -= amount;
    }

}

