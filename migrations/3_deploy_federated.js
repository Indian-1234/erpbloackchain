const FederatedLearning = artifacts.require("FederatedLearning");
const fs = require("fs");
const path = require("path");

module.exports = function (deployer) {
  deployer.deploy(FederatedLearning).then(() => {
    const info = {
      address: FederatedLearning.address,
      abi:     FederatedLearning.abi,
    };
    fs.writeFileSync(
      path.join(__dirname, "../data/fl_contract.json"),
      JSON.stringify(info, null, 2)
    );
    console.log("FederatedLearning deployed at:", FederatedLearning.address);
    console.log("Contract info saved to data/fl_contract.json");
  });
};
