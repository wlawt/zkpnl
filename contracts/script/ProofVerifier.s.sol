// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "forge-std/Script.sol";
import "../src/ProofVerifier.sol";

contract DeployProofVerifier is Script {
    function run() external {
        vm.startBroadcast();
        new ProofVerifier();
        vm.stopBroadcast();
    }
}
