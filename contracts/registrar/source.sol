pragma solidity >=0.4.22 <0.6.0;
// pragma experimental ABIEncoderV2;

contract KYCContract {
    struct UserData {
        address addr;
        bool isUsed;
    }

    struct UserPhones {
        string phone;
        bool isUsed;
    }

    struct ApprovementWaiting {
        bool isUsed;
        uint256 arrayIndex;
    }

    struct User {
        address addr;
        string phone;
        bool isUsed;
    }

    address public owner;

    mapping( string => UserData ) data;
    mapping( address => UserPhones ) dataPhones;

    mapping( address => ApprovementWaiting ) waitingDeletion;
    mapping( address => ApprovementWaiting ) waitingAddition;

    User[] public addWaitingPhones;
    User[] public delWaitingPhones;

    constructor() public {
        owner = msg.sender;
    }

    function add(string memory phone) public returns (bool) {
        if (data[phone].isUsed || waitingAddition[msg.sender].isUsed) {
            return false;
        }
        addWaitingPhones.push(User({ addr: msg.sender, phone: phone, isUsed: true }));
        waitingAddition[msg.sender] = ApprovementWaiting({ arrayIndex: addWaitingPhones.length - 1, isUsed: true });
        return true;
    }

    function del() public returns (bool) {
        address snd = msg.sender;
        if (waitingAddition[snd].isUsed ||
            waitingDeletion[snd].isUsed ||
            !dataPhones[snd].isUsed) {
            return false;
        }
        delWaitingPhones.push(User({ addr: snd, phone: dataPhones[snd].phone, isUsed: true }));
        waitingDeletion[snd] = ApprovementWaiting( { arrayIndex: addWaitingPhones.length - 1, isUsed: true } );
        return true;
    }

    function cancel() public returns (bool) {
        address addr = msg.sender;
        bool res = false;
        if(waitingAddition[addr].isUsed) {
            uint256 id = waitingAddition[addr].arrayIndex;
            delete waitingAddition[addr];
            delete addWaitingPhones[id];
            fixAddWaitingPhones(id);
            res = true;
        }
        if (waitingDeletion[addr].isUsed) {
            uint256 id = waitingDeletion[addr].arrayIndex;
            delete waitingDeletion[addr];
            delete delWaitingPhones[id];
            fixDelWaitingPhones(id);
            res = true;
        }
        return res;
    }

    function approve(address addr) public returns (bool) {
        bool res = false;
        if(waitingAddition[addr].isUsed) {
            uint256 id = waitingAddition[addr].arrayIndex;
            string memory phone = addWaitingPhones[id].phone;
            data[phone] = UserData({ addr: addr, isUsed: true });
            dataPhones[addr] = UserPhones({ phone: phone, isUsed: true });
            delete waitingAddition[addr];
            delete addWaitingPhones[id];
            fixAddWaitingPhones(id);
            res = true;
        }
        if (waitingDeletion[addr].isUsed) {
            uint256 id = waitingDeletion[addr].arrayIndex;
            string memory phone = delWaitingPhones[id].phone;
            delete data[phone];
            delete dataPhones[addr];
            delete waitingDeletion[addr];
            delete delWaitingPhones[id];
            fixDelWaitingPhones(id);
            res = true;
        }
        return res;
    }


    function fixAddWaitingPhones(uint256 id) public {
        if(addWaitingPhones.length > 1) {
            addWaitingPhones[id] = addWaitingPhones[addWaitingPhones.length - 1];
        }
        addWaitingPhones.length -= addWaitingPhones.length == 0 ? 0 : 1;
    }

    function fixDelWaitingPhones(uint256 id) public {
        if(delWaitingPhones.length > 1) {
            delWaitingPhones[id] = delWaitingPhones[delWaitingPhones.length - 1];
        }
        delWaitingPhones.length -= delWaitingPhones.length == 0 ? 0 : 1;
    }


    function get(string memory phone) public view returns (address) {
        if (!data[phone].isUsed) {
            return address(0x0);
        }
        return data[phone].addr;
    }

    function getByAddr(address addr) public view returns (string memory) {
        if (!dataPhones[addr].isUsed) {
            return "";
        }
        return dataPhones[addr].phone;
    }


    modifier onlyOwner() {
        require(isOwner());
        _;
    }

    function isOwner() public view returns (bool) {
        return msg.sender == owner;
    }

    function renounceOwnership() public onlyOwner {
        owner = address(0);
    }

    function transferOwnership(address newOwner) public onlyOwner {
        _transferOwnership(newOwner);
    }

    function _transferOwnership(address newOwner) internal {
        require(newOwner != address(0));
        owner = newOwner;
    }
}
