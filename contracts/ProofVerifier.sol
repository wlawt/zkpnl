// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract ProofVerifier {
    // Mapping to store proof hashes added by addresses
    mapping(address => bytes32) private proofHashes;

    // Event for logging proof hash addition
    event ProofHashAdded(address indexed user, bytes32 proofHash);

    // Add a proof hash for the sender
    function addProofHash(bytes32 proofHash) external {
        proofHashes[msg.sender] = proofHash;
        emit ProofHashAdded(msg.sender, proofHash);
    }

    // Verify if the given proof hash matches the stored one for the sender
    function verifyProofHash(bytes32 proofHash) external view returns (bool) {
        return proofHashes[msg.sender] == proofHash;
    }
}