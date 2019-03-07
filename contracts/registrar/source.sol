pragma solidity >=0.4.22 <0.6.0;

contract KYCContract {
    struct UserData {
        address addr;
        bool isUsed;
    }

    address private _owner;

    event OwnershipTransferred(address indexed previousOwner, address indexed newOwner);

    mapping( string => UserData ) data;

    constructor() public {
        _owner = msg.sender;
        emit OwnershipTransferred(address(0), _owner);
    }

    function add(string memory phone) public {
        require (data[phone].isUsed == false);
        data[phone] = UserData( { addr: msg.sender, isUsed: true } );
    }

    function del(string memory phone) public {
        require (data[phone].isUsed == true);
        delete data[phone];
    }

    function get(string memory phone) public view returns (address) {
        require (data[phone].isUsed == true);
        return data[phone].addr;
    }


    function owner() public view returns (address) {
        return _owner;
    }

    modifier onlyOwner() {
        require(isOwner());
        _;
    }

    function isOwner() public view returns (bool) {
        return msg.sender == _owner;
    }

    function renounceOwnership() public onlyOwner {
        emit OwnershipTransferred(_owner, address(0));
        _owner = address(0);
    }

    function transferOwnership(address newOwner) public onlyOwner {
        _transferOwnership(newOwner);
    }

    function _transferOwnership(address newOwner) internal {
        require(newOwner != address(0));
        emit OwnershipTransferred(_owner, newOwner);
        _owner = newOwner;
    }
}
