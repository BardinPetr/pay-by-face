pragma solidity >=0.4.22 <0.6.0;

contract PaymentContract {
    event CertificateWithdrew(bytes32 indexed id);
    event CertificateCreated(bytes32 indexed id);
    event CertificateUsed(bytes32 indexed id);
    event CertificateWithdrewAll();
    event CertificateUsageFailed();

    struct Gift {
        uint expire_date;
        uint senders_id;
        uint amount;
        uint id;
        address sender;
        bool isCreated;
    }

    mapping(address => bytes32[]) public senders;
    mapping(bytes32 => Gift) public gifts;

    uint gifts_cnt = 0;

    constructor() public {
    }

    function create(uint expire_date) public payable returns (bool) {
        require(expire_date > now, "Expiration date is invalid");
        uint id = (++senders[msg.sender].length);
        Gift memory gift = Gift({ sender: msg.sender, amount: msg.value, expire_date: expire_date, isCreated: true, id: gifts_cnt++, senders_id: id});
        bytes32 hash = hash_gift(gift);
        senders[msg.sender][id - 1] = hash;
        gifts[hash] = gift;
        emit CertificateCreated(hash);
        return true;
    }

    function use(bytes32 hash) public {
        require(can_use(hash), "Cert can't be used");
        Gift memory gift = gifts[hash];
        if(msg.sender.send(gift.amount)){
            delete_gift(hash);
            emit CertificateUsed(hash);
            return;
        }
        emit CertificateUsageFailed();
    }

    function get(bytes32 hash) public view returns (uint) {
        return gifts[hash].expire_date;
    }

    function withdraw() public {
        require(can_withdraw());
        for(uint i = 0; i < senders[msg.sender].length; i++){
            Gift memory g = gifts[senders[msg.sender][i]];
            if(now > g.expire_date) {
                bytes32 hash = hash_gift(g);
                if(msg.sender.send(g.amount)){
                    delete_gift(hash);
                    emit CertificateWithdrew(hash);
                }
            }
        }
        emit CertificateWithdrewAll();
    }

    function can_use(bytes32 hash) public view returns (bool) {
        Gift memory gift = gifts[hash];
        return gift.isCreated && (now < gift.expire_date);
    }

    function can_withdraw() public view returns (bool) {
        bool res = false;
        if (senders[msg.sender].length > 0) {
            for(uint i = 0; i < senders[msg.sender].length; i++){
                Gift memory g = gifts[senders[msg.sender][i]];
                if(now > g.expire_date) {
                    res = true;
                    break;
                }
            }
        }
        return res;
    }

    function delete_gift(bytes32 hash) private {
        Gift memory gift = gifts[hash];
        require(gift.isCreated);
        if(senders[gift.sender].length > 1) {
            senders[gift.sender][gift.senders_id] = senders[gift.sender][senders[gift.sender].length - 1];
            gifts[senders[gift.sender][gift.senders_id]].senders_id = senders[gift.sender].length - 1;
        }
        senders[gift.sender].length -= senders[gift.sender].length == 0 ? 0 : 1;
        delete gifts[hash];
    }

    function hash_gift(Gift memory gift) private pure returns (bytes32) {
        return keccak256(abi.encodePacked(gift.id, gift.sender, gift.expire_date, gift.amount));
    }
}
