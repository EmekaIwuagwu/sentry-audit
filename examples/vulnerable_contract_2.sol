// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

/**
 * VULNERABLE TOKEN CONTRACT - FOR TESTING ONLY
 * This contract contains DeFi-specific vulnerabilities
 * DO NOT USE IN PRODUCTION
 */

contract VulnerableToken {
    string public name = "Vulnerable Token";  // Should use bytes32 for gas efficiency
    string public symbol = "VULN";
    uint8 public decimals = 18;
    uint256 public totalSupply;

    mapping(address => uint256) public balanceOf;
    mapping(address => mapping(address => uint256)) public allowance;

    address public minter;
    bool public initialized;

    event Transfer(address indexed from, address indexed to, uint256 value);
    event Approval(address indexed owner, address indexed spender, uint256 value);

    // Vulnerability 1: Unprotected initialization function
    function initialize(address _minter) public {
        // Missing check for re-initialization!
        minter = _minter;
        initialized = true;
    }

    // Vulnerability 2: Missing access control on mint function
    function mint(address to, uint256 amount) public {
        // Anyone can mint tokens!
        totalSupply += amount;
        balanceOf[to] += amount;
        emit Transfer(address(0), to, amount);
    }

    // Vulnerability 3: Missing access control on burn
    function burn(address from, uint256 amount) public {
        balanceOf[from] -= amount;
        totalSupply -= amount;
        emit Transfer(from, address(0), amount);
    }

    function transfer(address to, uint256 amount) public returns (bool) {
        require(balanceOf[msg.sender] >= amount, "Insufficient balance");

        // Vulnerability 4: No check for zero address
        balanceOf[msg.sender] -= amount;
        balanceOf[to] += amount;

        emit Transfer(msg.sender, to, amount);
        return true;
    }

    function approve(address spender, uint256 amount) public returns (bool) {
        allowance[msg.sender][spender] = amount;
        emit Approval(msg.sender, spender, amount);
        return true;
    }

    function transferFrom(address from, address to, uint256 amount) public returns (bool) {
        require(balanceOf[from] >= amount, "Insufficient balance");
        require(allowance[from][msg.sender] >= amount, "Insufficient allowance");

        balanceOf[from] -= amount;
        balanceOf[to] += amount;
        allowance[from][msg.sender] -= amount;

        emit Transfer(from, to, amount);
        return true;
    }

    // Vulnerability 5: Inefficient loop without caching length
    function batchTransfer(address[] memory recipients, uint256[] memory amounts) public {
        for (uint256 i = 0; i < recipients.length; i++) {  // .length called every iteration
            transfer(recipients[i], amounts[i]);
        }
    }

    // Vulnerability 6: Unchecked block (disables overflow protection)
    function unsafeAdd(uint256 a, uint256 b) public pure returns (uint256) {
        unchecked {
            return a + b;  // Can overflow without reverting
        }
    }

    // Vulnerability 7: delegatecall to user-provided address
    function delegateExecute(address target, bytes memory data) public returns (bool) {
        // Extremely dangerous - allows arbitrary code execution with contract's context
        (bool success, ) = target.delegatecall(data);
        return success;
    }

    // Vulnerability 8: Block timestamp manipulation
    function timeBasedReward() public {
        // Using block.timestamp for critical logic
        if (block.timestamp % 10 == 0) {
            balanceOf[msg.sender] += 100 * 10**18;  // Miners can manipulate this
        }
    }
}
