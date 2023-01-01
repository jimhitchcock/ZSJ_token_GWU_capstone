pragma solidity ^0.5.7;

import "https://github.com/OpenZeppelin/openzeppelin-contracts/blob/release-v2.5.0/contracts/token/ERC721/ERC721Full.sol";

contract PropertyRegistry is ERC721Full {
    constructor() public ERC721Full("PropertyRegistryToken", "ZJS") {}

    struct propertywork {
        string name;
        string propertyOwner;
        uint256 propertyValue;
    }

    mapping(uint256 => propertywork) public propertyCollection;

    event Appraisal(uint256 token_id, uint256 propertyappraisalValue, string reportURI);

    function registerpropertywork(
        address owner,
        string memory name,
        string memory propertyOwner,
        uint256 initialPropertyValue,
        string memory tokenURI
    ) public returns (uint256) {
        uint256 tokenId = totalSupply();

        _mint(owner, tokenId);
        _setTokenURI(tokenId, tokenURI);

        propertyCollection[tokenId] = propertywork(name, propertyOwner, initialPropertyValue);

        return tokenId;
    }
}