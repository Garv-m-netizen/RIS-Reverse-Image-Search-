// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/**
 * @title HashRegistry
 * @dev Stores SHA-256 hashes of verified social media posts on Ethereum Sepolia testnet.
 * Provides immutable proof of verification, verifier address, and block timestamp.
 */
contract HashRegistry {

    struct Record {
        address verifier;
        uint256 timestamp;
        bool exists;
    }

    // Mapping from hash -> Record
    mapping(bytes32 => Record) private registry;

    // Event emitted when a new hash is registered
    event HashStored(address indexed verifier, bytes32 indexed hash, uint256 timestamp);

    /**
     * @notice Stores a bytes32 SHA-256 hash on-chain.
     * @param _hash The 32-byte hash to store.
     */
    function storeHash(bytes32 _hash) external {
        require(!registry[_hash].exists, "Hash already registered on-chain!");

        registry[_hash] = Record({
            verifier: msg.sender,
            timestamp: block.timestamp,
            exists: true
        });

        emit HashStored(msg.sender, _hash, block.timestamp);
    }

    /**
     * @notice Verifies if a given hash exists in the registry.
     * @param _hash The 32-byte hash to query.
     * @return True if stored, false otherwise.
     */
    function verifyHash(bytes32 _hash) external view returns (bool) {
        return registry[_hash].exists;
    }

    /**
     * @notice Retrieves the address of the verifier for a given hash.
     * @param _hash The 32-byte hash to query.
     * @return Address of the wallet that stored the hash.
     */
    function getVerifier(bytes32 _hash) external view returns (address) {
        require(registry[_hash].exists, "Hash not found in registry");
        return registry[_hash].verifier;
    }

    /**
     * @notice Retrieves the block timestamp when the hash was stored.
     * @param _hash The 32-byte hash to query.
     * @return Block timestamp (Unix epoch seconds).
     */
    function getTimestamp(bytes32 _hash) external view returns (uint256) {
        require(registry[_hash].exists, "Hash not found in registry");
        return registry[_hash].timestamp;
    }
}
