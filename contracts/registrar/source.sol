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

    event RegistrationRequest(address indexed sender);
    event UnregistrationRequest(address indexed sender);

    event RegistrationCanceled(address indexed sender);
    event UnregistrationCanceled(address indexed sender);

    event RegistrationConfirmed(address indexed sender);
    event UnregistrationConfirmed(address indexed sender);

    constructor() public {
        owner = msg.sender;
    }

    function add(string memory phone) public returns (bool) {
        require (!data[phone].isUsed && !waitingAddition[msg.sender].isUsed && matches(phone));
        addWaitingPhones.push(User({ addr: msg.sender, phone: phone, isUsed: true }));
        waitingAddition[msg.sender] = ApprovementWaiting({ arrayIndex: addWaitingPhones.length - 1, isUsed: true });
        emit RegistrationRequest(msg.sender);
        return true;
    }

    function dlt() public returns (bool) {
        address snd = msg.sender;
        require (!waitingAddition[snd].isUsed &&
            !waitingDeletion[snd].isUsed &&
            dataPhones[snd].isUsed);
        delWaitingPhones.push(User({ addr: snd, phone: dataPhones[snd].phone, isUsed: true }));
        waitingDeletion[snd] = ApprovementWaiting( { arrayIndex: delWaitingPhones.length - 1, isUsed: true } );
        emit UnregistrationRequest(msg.sender);
        return true;
    }

    function isInAddPending() public view returns (bool) {
        return waitingAddition[msg.sender].isUsed;
    }

    function isInDelPending() public view returns (bool) {
        return waitingDeletion[msg.sender].isUsed;
    }


    function isInAddPendingA(address addr) public view returns (bool) {
        return waitingAddition[addr].isUsed;
    }

    function isInDelPendingA(address addr) public view returns (bool) {
        return waitingDeletion[addr].isUsed;
    }


    function getWaitingAdditionCnt() public view returns (uint256){
        return addWaitingPhones.length;
    }

    function getWaitingDeletionCnt() public view returns (uint256){
        return delWaitingPhones.length;
    }


    function cancel() public {
        address addr = msg.sender;
        bool a = isInAddPending();
        bool b = isInDelPending();
        require(a || b);
        if(a) {
            uint256 id = waitingAddition[addr].arrayIndex;
            delete waitingAddition[addr];
            delete addWaitingPhones[id];
            fixAddWaitingPhones(id);
            emit RegistrationCanceled(msg.sender);
        }
        if (b) {
            uint256 id1 = waitingDeletion[addr].arrayIndex;
            delete delWaitingPhones[id1];
            delete waitingDeletion[addr];
            fixDelWaitingPhones(id1);
            emit UnregistrationCanceled(msg.sender);
        }
    }

    function approve(address addr) public onlyOwner {
        bool a = isInAddPendingA(addr);
        bool b = isInDelPendingA(addr);
        require(a || b);
        if(a) {
            uint256 id = waitingAddition[addr].arrayIndex;
            string memory phone = addWaitingPhones[id].phone;
            data[phone] = UserData({ addr: addr, isUsed: true });
            dataPhones[addr] = UserPhones({ phone: phone, isUsed: true });
            delete waitingAddition[addr];
            delete addWaitingPhones[id];
            fixAddWaitingPhones(id);
            emit RegistrationConfirmed(addr);
        }
        if (b) {
            uint256 id1 = waitingDeletion[addr].arrayIndex;
            string memory phone1 = delWaitingPhones[id1].phone;
            delete data[phone1];
            delete dataPhones[addr];
            delete waitingDeletion[addr];
            delete delWaitingPhones[id1];
            fixDelWaitingPhones(id1);
            emit UnregistrationConfirmed(addr);
        }
    }


    function fixAddWaitingPhones(uint256 id) public {
        if(addWaitingPhones.length > 1) {
            addWaitingPhones[id] = addWaitingPhones[addWaitingPhones.length - 1];
            waitingAddition[addWaitingPhones[id].addr].arrayIndex = id;
        }
        addWaitingPhones.length -= addWaitingPhones.length == 0 ? 0 : 1;
    }

    function fixDelWaitingPhones(uint256 id) public {
        if(delWaitingPhones.length > 1) {
            delWaitingPhones[id] = delWaitingPhones[delWaitingPhones.length - 1];
            waitingDeletion[delWaitingPhones[id].addr].arrayIndex = id;
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
        require(newOwner != owner);
        owner = newOwner;
    }

    // I don't know what that shit is this but it will not work without it
    function sending_point() pure public {
        return;
    }

    // AUTOGENERATED BY https://github.com/gnidan/solregex
    struct State {
        bool accepts;
        function (byte) pure internal returns (State memory) func;
    }

    string public constant regex = "\\+[1234567890]{11}";

    function s0(byte c) pure internal returns (State memory) {
    c = c;
    return State(false, s0);
    }

    function s1(byte c) pure internal returns (State memory) {
    if (c == 43) {
      return State(false, s2);
    }

    return State(false, s0);
    }

    function s2(byte c) pure internal returns (State memory) {
    if (c == 48 || c == 49 || c == 50 || c == 51 || c == 52 || c == 53 || c == 54 || c == 55 || c == 56 || c == 57) {
      return State(false, s3);
    }

    return State(false, s0);
    }

    function s3(byte c) pure internal returns (State memory) {
    if (c == 48 || c == 49 || c == 50 || c == 51 || c == 52 || c == 53 || c == 54 || c == 55 || c == 56 || c == 57) {
      return State(false, s4);
    }

    return State(false, s0);
    }

    function s4(byte c) pure internal returns (State memory) {
    if (c == 48 || c == 49 || c == 50 || c == 51 || c == 52 || c == 53 || c == 54 || c == 55 || c == 56 || c == 57) {
      return State(false, s5);
    }

    return State(false, s0);
    }

    function s5(byte c) pure internal returns (State memory) {
    if (c == 48 || c == 49 || c == 50 || c == 51 || c == 52 || c == 53 || c == 54 || c == 55 || c == 56 || c == 57) {
      return State(false, s6);
    }

    return State(false, s0);
    }

    function s6(byte c) pure internal returns (State memory) {
    if (c == 48 || c == 49 || c == 50 || c == 51 || c == 52 || c == 53 || c == 54 || c == 55 || c == 56 || c == 57) {
      return State(false, s7);
    }

    return State(false, s0);
    }

    function s7(byte c) pure internal returns (State memory) {
    if (c == 48 || c == 49 || c == 50 || c == 51 || c == 52 || c == 53 || c == 54 || c == 55 || c == 56 || c == 57) {
      return State(false, s8);
    }

    return State(false, s0);
    }

    function s8(byte c) pure internal returns (State memory) {
    if (c == 48 || c == 49 || c == 50 || c == 51 || c == 52 || c == 53 || c == 54 || c == 55 || c == 56 || c == 57) {
      return State(false, s9);
    }

    return State(false, s0);
    }

    function s9(byte c) pure internal returns (State memory) {
    if (c == 48 || c == 49 || c == 50 || c == 51 || c == 52 || c == 53 || c == 54 || c == 55 || c == 56 || c == 57) {
      return State(false, s10);
    }

    return State(false, s0);
    }

    function s10(byte c) pure internal returns (State memory) {
    if (c == 48 || c == 49 || c == 50 || c == 51 || c == 52 || c == 53 || c == 54 || c == 55 || c == 56 || c == 57) {
      return State(false, s11);
    }

    return State(false, s0);
    }

    function s11(byte c) pure internal returns (State memory) {
    if (c == 48 || c == 49 || c == 50 || c == 51 || c == 52 || c == 53 || c == 54 || c == 55 || c == 56 || c == 57) {
      return State(false, s12);
    }

    return State(false, s0);
    }

    function s12(byte c) pure internal returns (State memory) {
    if (c == 48 || c == 49 || c == 50 || c == 51 || c == 52 || c == 53 || c == 54 || c == 55 || c == 56 || c == 57) {
      return State(true, s13);
    }

    return State(false, s0);
    }

    function s13(byte c) pure internal returns (State memory) {
    // silence unused var warning
    c = c;

    return State(false, s0);
    }

    function matches(string memory input) public pure returns (bool) {
    State memory cur = State(false, s1);

    for (uint i = 0; i < bytes(input).length; i++) {
      byte c = bytes(input)[i];

      cur = cur.func(c);
    }

    return cur.accepts;
    }
}


