pragma solidity ^0.5.2;

import 'openzeppelin-solidity/contracts/token/ERC20/ERC20.sol';
import 'openzeppelin-solidity/contracts/token/ERC20/ERC20Detailed.sol';
import 'openzeppelin-solidity/contracts/token/ERC20/TokenTimelock.sol';

contract Minglechain is ERC20, ERC20Detailed {
    string public constant NAME = "Minglechain Token";
    string public constant SYMBOL = "MC";
    uint8 public constant DECIMALS = 18;

    uint256 constant public EIOCAP      = 50 * 1000000 * (10 ** uint256(DECIMALS));
    uint256 constant public PRESALECAP  = 10 * 1000000 * (10 ** uint256(DECIMALS));
    uint256 constant public REFERRALCAP = 10 * 1000000 * (10 ** uint256(DECIMALS));
    uint256 [] public TEAMCAP          = [ 6 * 1000000 * (10 ** uint256(DECIMALS)),
                                           6 * 1000000 * (10 ** uint256(DECIMALS)),
                                           6 * 1000000 * (10 ** uint256(DECIMALS)),
                                           6 * 1000000 * (10 ** uint256(DECIMALS)),
                                           6 * 1000000 * (10 ** uint256(DECIMALS))
                                     ];

    address constant public EIO_ADDRESS = 0xa3C986AC574C58Ee85AeC38E56d233cED228baF0;
    address constant public PRESALE_ADDRESS = 0x7C1277009Fa4272a7C4A26DA267b867fcDc4Bc03;
    address constant public REFERRAL_ADDRESS = 0xe52b38542659CB8a17e28c0FC6fF367aBc8465c1;
    address constant public TEAM_ADDRESS = 0x4A2f6431354B58A93A22156410bA160D03E05D06;

     uint256 [] public TEAMLOCK_END = [
       1569888000, // 1 October 2019 0:00:00 GMT
       1601510400, // 1 October 2020 0:00:00 GMT
       1633046400, // 1 October 2021 0:00:00 GMT
       1664582400, // 1 October 2022 0:00:00 GMT
       1696118400  // 1 October 2023 0:00:00 GMT
     ];

    TokenTimelock [5] public TEAM_TIMELOCKS;

    constructor(
    )
    ERC20Detailed(NAME, SYMBOL, DECIMALS)
    public
    {
        // Default minted tokens:
        _mint(EIO_ADDRESS, EIOCAP);
        _mint(PRESALE_ADDRESS, PRESALECAP);
        _mint(REFERRAL_ADDRESS, REFERRALCAP);

        // Team tokens with a time lock before they are minted:
        TEAM_TIMELOCKS[0] = new TokenTimelock(this, TEAM_ADDRESS, TEAMLOCK_END[0]);
        TEAM_TIMELOCKS[1] = new TokenTimelock(this, TEAM_ADDRESS, TEAMLOCK_END[1]);
        TEAM_TIMELOCKS[2] = new TokenTimelock(this, TEAM_ADDRESS, TEAMLOCK_END[2]);
        TEAM_TIMELOCKS[3] = new TokenTimelock(this, TEAM_ADDRESS, TEAMLOCK_END[3]);
        TEAM_TIMELOCKS[4] = new TokenTimelock(this, TEAM_ADDRESS, TEAMLOCK_END[4]);

        _mint(address(TEAM_TIMELOCKS[0]), TEAMCAP[0]);
        _mint(address(TEAM_TIMELOCKS[1]), TEAMCAP[1]);
        _mint(address(TEAM_TIMELOCKS[2]), TEAMCAP[2]);
        _mint(address(TEAM_TIMELOCKS[3]), TEAMCAP[3]);
        _mint(address(TEAM_TIMELOCKS[4]), TEAMCAP[4]);
    }

    /**
     * @dev Burns a specific amount of tokens.
     * @param value The amount of token to be burned.
     */
    function burn(uint256 value) public {
        _burn(msg.sender, value);
    }

}
