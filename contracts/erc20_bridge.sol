
pragma solidity 0.8.23;

contract Erc20Bridge {
    event LockEvent(address addr, uint256 value);

    //mapping(address=>uint256) public values;
    uint256 public total;
    address public erc20_addr;
    address public owner;
    address public operator;
    bool public live = true;

    constructor(address contract_addr) {
        erc20_addr = contract_addr;
        owner = msg.sender;
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

    function lock() public {
        //require(msg.value > 0, "Must send some Ether to lock the value");
        //total += msg.value;
        //emit LockEvent(msg.sender, msg.value);
    }

    function release(address payable recipient, uint256 amount) public {
        require(msg.sender == operator, "Only operator can release");
        require(total >= amount, "No enough locked value to send");
        //recipient.transfer(amount);
        //values[recipient] = 0;
        total -= amount;
    }

}

