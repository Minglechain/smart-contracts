import { increaseTimeTo, duration } from './helpers/increaseTime';
import latestTime from './helpers/latestTime';
import EVMRevert from './helpers/EVMRevert';

const BigNumber = web3.BigNumber;

const Minglechain = artifacts.require('Minglechain');
const TokenTimelock = artifacts.require('./TokenTimelock');

require('chai')
  .use(require('chai-as-promised'))
  .use(require('chai-bignumber')(BigNumber))
  .should();

contract('Minglechain', accounts => {
  const _name = 'Minglechain Token';
  const _symbol = 'MC';
  const _decimals = 18;

  const _totalSupply = 100 * 1000000;

  const _eiocap      = 50 * 1000000;
  const _presalecap  = 10 * 1000000;
  const _referralcap = 10 * 1000000;
  const _team0cap    =  6 * 1000000;

  const _eiocapAddress = '0xa3C986AC574C58Ee85AeC38E56d233cED228baF0';
  const _presalecapAddress = '0x7C1277009Fa4272a7C4A26DA267b867fcDc4Bc03';
  const _referralcapAddress = '0xe52b38542659CB8a17e28c0FC6fF367aBc8465c1';
  const _teamAddress = '0x4A2f6431354B58A93A22156410bA160D03E05D06';

  const _releaseTime1 = 1569888001;

  beforeEach(async function () {
    this.token = await Minglechain.new();
  });

  describe('token attributes', function() {
    it('has the correct name', async function() {
      const name = await this.token.name();
      name.should.equal(_name);
    });

    it('has the correct symbol', async function() {
      const symbol = await this.token.symbol();
      symbol.should.equal(_symbol);
    });

    it('has the correct decimals', async function() {
      let decimals = await this.token.decimals();
      decimals = decimals.toNumber();
      decimals.should.equal(_decimals);
    });
  });

    describe('check fixed supplies', function() {
        it('has the correct total', async function() {
          let totalSupply = await this.token.totalSupply();
          totalSupply = totalSupply.toString().slice(0, -(_decimals));
          totalSupply.should.equal(_totalSupply.toString());
        });
        it('has the correct eiocap', async function() {
          let eiocap = await this.token.balanceOf(_eiocapAddress);
          eiocap = eiocap.toString().slice(0, -(_decimals));
          eiocap.should.equal(_eiocap.toString());
        });
        it('has the correct presalecap', async function() {
          let presalecap = await this.token.balanceOf(_presalecapAddress);
          presalecap = presalecap.toString().slice(0, -(_decimals));
          presalecap.should.equal(_presalecap.toString());
        });
        it('has the correct referralcap', async function() {
          let referralcap = await this.token.balanceOf(_referralcapAddress);
          referralcap = referralcap.toString().slice(0, -(_decimals));
          referralcap.should.equal(_referralcap.toString());
        });
    });

    describe('check team supplies', function() {
        it('reject release at first moment', async function() {
          let TeamLocAddress0 = await this.token.TEAM_TIMELOCKS(0);
          const Team0TimeLock = await TokenTimelock.at(TeamLocAddress0);
          let result = await Team0TimeLock.release().should.be.rejectedWith(EVMRevert);
        });

        it('allow release on 2nd of October 2019', async function() {
          await increaseTimeTo(_releaseTime1);
          let TeamLocAddress0 = await this.token.TEAM_TIMELOCKS(0);
          const Team0TimeLock = await TokenTimelock.at(TeamLocAddress0);
          let releaseTime = await Team0TimeLock.releaseTime();
          await Team0TimeLock.release().should.be.fulfilled;

          let team0cap = await this.token.balanceOf(_teamAddress);
          team0cap = team0cap.toString().slice(0, -(_decimals));
          team0cap.should.equal(_team0cap.toString());
        });

    });

});
