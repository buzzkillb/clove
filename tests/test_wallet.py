from unittest.mock import patch

from bitcoin.base58 import decode, encode
from bitcoin.core.key import CPubKey
from bitcoin.wallet import CBitcoinSecret
from ecdsa import SECP256k1, SigningKey
from ecdsa.util import PRNG
from pytest import mark, raises

from clove.network import Ethereum
from clove.network.bitcoin import Bitcoin
from clove.network.bitcoin.wallet import BitcoinWallet
from clove.network.ethereum.wallet import EthereumWallet


def test_password_encryption():
    wallet = BitcoinWallet()
    private_key = wallet.get_private_key()
    encrypted_private_key = BitcoinWallet.encrypt_private_key(
        private_key=private_key, password='test_password'
    )
    decrypted_private_key = BitcoinWallet.decrypt_private_key(
        encrypted_private_key=encrypted_private_key, password='test_password'
    )
    assert decrypted_private_key == private_key
    assert encrypted_private_key != private_key


@mark.parametrize('wallet', [
    BitcoinWallet(),
    BitcoinWallet(private_key='KxhniiXPCdBBpJmQnYPHmutKJq42Wm3yPY6AAKxvDPnTt8KA8BJF'),
    BitcoinWallet(
        encrypted_private_key=b'3bktZ1EG4dvKOilVbveJo8WoScrVJqGOfhjULdfooL'
                              b'CN7Il5Bu4CCA0HBP1k7iPZWyfohxiSdwJ3CpgHijIL2zb1THA=',
        password='test_password_xyz'
    )
])
def test_bitcoin_wallet(wallet):
    assert isinstance(wallet.private_key, CBitcoinSecret)
    assert isinstance(wallet.public_key, CPubKey)
    assert isinstance(wallet.address, str)
    assert isinstance(wallet.get_private_key(), str)
    assert wallet.public_key == wallet.get_public_key()
    assert wallet.private_key.pub == wallet.public_key


def test_bitcoin_wallet_not_initialized_if_key_provided_whilst_password_not():
    with raises(
        TypeError,
        message="__init__() missing 'password' argument, since 'encrypted_private_key' argument was provided"
    ):
        BitcoinWallet(encrypted_private_key=b'C0RZlLtnrtozbxEHhTVZM')


def test_bitcoin_wallet_address_correct():
    address = Bitcoin.get_wallet().address
    assert address.startswith('1')
    assert encode(decode(address)) == address


@mark.parametrize('kwargs', [
        dict(),
        dict(private_key='KxhniiXPCdBBpJmQnYPHmutKJq42Wm3yPY6AAKxvDPnTt8KA8BJF'),
        dict(
            encrypted_private_key=b'3bktZ1EG4dvKOilVbveJo8WoScrVJqGOfhjULdfooL'
                                  b'CN7Il5Bu4CCA0HBP1k7iPZWyfohxiSdwJ3CpgHijIL2zb1THA=',
            password='test_password_xyz'
        )
])
def test_get_bitcoin_wallet_via_network(kwargs):
    wallet = Bitcoin.get_wallet(**kwargs)
    assert isinstance(wallet, BitcoinWallet)


def test_get_new_bitcoin_wallet_via_network():
    wallet = Bitcoin.get_new_wallet()
    assert isinstance(wallet, BitcoinWallet)


def test_wallet_ethereum():
    private_key = '34fff148b3d00c1e8b3a016c7859e1616dc0edcfc3ea1ef7c96a7c4487fbeb26'
    wallet = EthereumWallet(private_key)

    assert wallet.private_key == private_key
    assert wallet.address == '0x76cF367Efb63E037E3dfd0352DAc15e501f72DeA'


def test_get_new_ethereum_wallet_via_network():
    private_key = '34fff148b3d00c1e8b3a016c7859e1616dc0edcfc3ea1ef7c96a7c4487fbeb26'
    wallet = Ethereum.get_wallet(private_key)
    assert isinstance(wallet, EthereumWallet)


@patch(
    'ecdsa.SigningKey.generate',
    return_value=SigningKey.generate(
        curve=SECP256k1, entropy=PRNG("test")
    )
)
def test_get_new_ethereum_wallet_wo_priv_key_provided(mocked_priv_key):
    expected_address = '0xfc843077A275A4caFEF00D88BE0B296b334D613B'

    wallet = Ethereum.get_wallet()
    assert isinstance(wallet, EthereumWallet)
    assert wallet.address == expected_address
