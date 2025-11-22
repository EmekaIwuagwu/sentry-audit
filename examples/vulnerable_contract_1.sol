// SPDX-License-Identifier: MIT
pragma solidity ^0.7.6;

/**
 * VULNERABLE CONTRACT - FOR TESTING ONLY
 * This contract intentionally contains multiple security vulnerabilities
 * DO NOT USE IN PRODUCTION
 */

contract VulnerableBank {
    mapping(address => uint256) public balances;
    address public owner;

    constructor() {
        owner = msg.sender;
    }

    // Vulnerability 1: Missing access control on critical function
    function setOwner(address newOwner) public {
        owner = newOwner;
    }

    // Vulnerability 2: Reentrancy vulnerability
    function withdraw(uint256 amount) public {
        require(balances[msg.sender] >= amount, "Insufficient balance");

        // External call BEFORE state change (vulnerable to reentrancy)
        (bool success, ) = msg.sender.call{value: amount}("");
        require(success, "Transfer failed");

        // State change AFTER external call (too late!)
        balances[msg.sender] -= amount;
    }

    // Vulnerability 3: tx.origin for authentication
    function adminWithdraw(uint256 amount) public {
        require(tx.origin == owner, "Not owner");
        payable(owner).transfer(amount);
    }

    // Vulnerability 4: Integer overflow (Solidity < 0.8.0)
    function deposit() public payable {
        balances[msg.sender] += msg.value;  // Can overflow without SafeMath
    }

    // Vulnerability 5: Unchecked external call
    function transfer(address payable recipient, uint256 amount) public {
        require(balances[msg.sender] >= amount, "Insufficient balance");

        balances[msg.sender] -= amount;
        // Return value not checked!
        recipient.send(amount);
    }

    // Vulnerability 6: Public function that should be external
    function getBalance(address account) public view returns (uint256) {
        return balances[account];
    }

    // Vulnerability 7: Inefficient storage in loop
    function sumBalances(address[] memory accounts) public view returns (uint256) {
        uint256 total = 0;
        for (uint256 i = 0; i < accounts.length; i++) {
            // Storage access in loop
            total += balances[accounts[i]];
        }
        return total;
    }

    // Vulnerability 8: Redundant initialization
    uint256 public totalSupply = 0;  // Unnecessary, defaults to 0
    bool public paused = false;      // Unnecessary, defaults to false

    // Allow contract to receive ETH
    receive() external payable {
        balances[msg.sender] += msg.value;
    }
}
