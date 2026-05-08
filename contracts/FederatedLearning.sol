pragma solidity ^0.6.6;

contract FederatedLearning {

    struct ModelUpdate {
        string  providerHash;   // SHA-256 of provider address (privacy)
        string  weightHash;     // SHA-256 of model weights
        uint256 nSamples;
        uint256 timestamp;
        uint256 round;
    }

    ModelUpdate[] public updates;
    uint256 public currentRound;
    string  public globalModelHash;
    address public admin;

    event ModelUpdateLogged(string weightHash, uint256 round, uint256 timestamp);
    event GlobalModelAggregated(string globalHash, uint256 round, uint256 timestamp);

    constructor() public {
        admin        = msg.sender;
        currentRound = 1;
    }

    function logModelUpdate(
        string memory providerHash,
        string memory weightHash,
        uint256 nSamples
    ) public {
        updates.push(ModelUpdate(providerHash, weightHash, nSamples, now, currentRound));
        emit ModelUpdateLogged(weightHash, currentRound, now);
    }

    function setGlobalModel(string memory globalHash) public {
        globalModelHash = globalHash;
        emit GlobalModelAggregated(globalHash, currentRound, now);
        currentRound++;
    }

    function getUpdateCount() public view returns (uint256) {
        return updates.length;
    }

    function getUpdate(uint256 index)
        public view
        returns (string memory, string memory, uint256, uint256, uint256)
    {
        ModelUpdate memory u = updates[index];
        return (u.providerHash, u.weightHash, u.nSamples, u.timestamp, u.round);
    }
}
