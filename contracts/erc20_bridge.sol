// SPDX-License-Identifier: MIT
// OpenZeppelin Contracts (last updated v5.0.0) (token/ERC20/IERC20.sol)

pragma solidity 0.8.23;

import "./IERC20.sol";

contract Erc20Bridge {
    event LockEvent(address addr, uint256 value);

    uint256 public total;
    address public erc20_addr;
    address public owner;
    address public operator;
    bool public live = true;

    constructor(address _owner, address contract_addr) {
        erc20_addr = contract_addr;
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

    function lock(uint256 amount) public {
        require(amount > 0, "Must send token to lock the value");
        IERC20(erc20_addr).transferFrom(msg.sender, address(this), amount);
        total += amount;
        emit LockEvent(msg.sender, amount);
    }

    function release(address payable recipient, uint256 amount) public {
        require(msg.sender == operator, "Only operator can release");
        require(total >= amount, "No enough locked value to send");
        IERC20(erc20_addr).transfer(recipient, amount);
        total -= amount;
    }

}

