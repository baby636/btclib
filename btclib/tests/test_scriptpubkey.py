#!/usr/bin/env python3

# Copyright (C) 2017-2020 The btclib developers
#
# This file is part of btclib. It is subject to the license terms in the
# LICENSE file found in the top-level directory of this distribution.
#
# No part of btclib including this file, may be copied, modified, propagated,
# or distributed except according to the terms contained in the LICENSE file.

import unittest

from btclib import base58address, bech32address
from btclib.base58address import b58address_from_h160, b58address_from_witness
from btclib.bech32address import b32address_from_witness
from btclib.network import p2pkh_prefix_from_network, p2sh_prefix_from_network
from btclib.script import decode, encode
from btclib.scriptpubkey import (address_from_scriptPubKey, nulldata, p2ms,
                                 p2pk, p2pkh, p2sh, p2wpkh, p2wsh,
                                 payload_from_pubkeys,
                                 payload_from_scriptPubKey,
                                 scriptPubKey_from_address,
                                 scriptPubKey_from_payload)
from btclib.utils import hash160, sha256


class TestScriptPubKey(unittest.TestCase):

    def test_p2pk(self):

        script_type = 'p2pk'

        # self-consistency
        pubkey = "04cc71eb30d653c0c3163990c47b976f3fb3f37cccdcbedb169a1dfef58bbfbfaff7d8a473e7e2e6d317b87bafe8bde97e3cf8f065dec022b51d11fcdd0d348ac4"
        payload = payload_from_pubkeys(pubkey)
        script = encode([payload, 'OP_CHECKSIG'])

        # straight to the scriptPubKey
        scriptPubKey = p2pk(pubkey)
        self.assertEqual(scriptPubKey.hex(), script.hex())

        # to the scriptPubKey in two steps (trhough payload)
        scriptPubKey = scriptPubKey_from_payload(script_type, payload)
        self.assertEqual(scriptPubKey.hex(), script.hex())
        
        # back from the scriptPubKey to the payload
        script_type2, payload2, m2 = payload_from_scriptPubKey(scriptPubKey)
        self.assertEqual(script_type, script_type2)
        self.assertEqual(0, m2)
        self.assertEqual(payload.hex(), payload2.hex())
        script_type2, payload2, m2 = payload_from_scriptPubKey(decode(script))
        self.assertEqual(script_type, script_type2)
        self.assertEqual(0, m2)
        self.assertEqual(payload.hex(), payload2.hex())

        # data -> payload in this case is invertible (no hash functions)
        self.assertEqual(payload.hex(), pubkey)

        # no address in this case

        # documented test case: https://learnmeabitcoin.com/guide/p2pk
        pubkey = "04 ae1a62fe09c5f51b13905f07f06b99a2f7159b2225f374cd378d71302fa28414 e7aab37397f554a7df5f142c21c1b7303b8a0626f1baded5c72a704f7e6cd84c"
        script = "4104ae1a62fe09c5f51b13905f07f06b99a2f7159b2225f374cd378d71302fa28414e7aab37397f554a7df5f142c21c1b7303b8a0626f1baded5c72a704f7e6cd84cac"
        scriptPubKey = p2pk(pubkey)
        self.assertEqual(scriptPubKey.hex(), script)

        # Invalid size: 33 bytes instead of 65
        pubkey = "03 ae1a62fe09c5f51b13905f07f06b99a2f7159b2225f374cd378d71302fa28414"
        self.assertRaises(ValueError, p2pk, pubkey)
        #p2pk(pubkey)

    def test_p2ms(self):

        script_type = 'p2ms'

        # self-consistency
        pubkey1 = "04cc71eb30d653c0c3163990c47b976f3fb3f37cccdcbedb169a1dfef58bbfbfaff7d8a473e7e2e6d317b87bafe8bde97e3cf8f065dec022b51d11fcdd0d348ac4"
        pubkey2 = "0461cbdcc5409fb4b4d42b51d33381354d80e550078cb532a34bfa2fcfdeb7d76519aecc62770f5b0e4ef8551946d8a540911abe3e7854a26f39f58b25c15342af"
        pubkeys = [pubkey1, pubkey2]
        lexicographic_sort = True
        payload = payload_from_pubkeys(pubkeys, lexicographic_sort)
        m = 1
        n = 2
        script = encode([m, pubkey2, pubkey1, n, 'OP_CHECKMULTISIG'])

        # straight to the scriptPubKey
        scriptPubKey = p2ms(m, pubkeys, lexicographic_sort)
        self.assertEqual(scriptPubKey.hex(), script.hex())

        # to the scriptPubKey in two steps (trhough payload)
        scriptPubKey = scriptPubKey_from_payload(script_type, payload, m)
        self.assertEqual(scriptPubKey.hex(), script.hex())
        
        # back from the scriptPubKey to the payload
        script_type2, payload2, m2 = payload_from_scriptPubKey(scriptPubKey)
        self.assertEqual(script_type, script_type2)
        self.assertEqual(m, m2)
        self.assertEqual(payload.hex(), payload2.hex())
        script_type2, payload2, m2 = payload_from_scriptPubKey(decode(script))
        self.assertEqual(script_type, script_type2)
        self.assertEqual(m, m2)
        self.assertEqual(payload.hex(), payload2.hex())

        # data -> payload in this case is invertible (no hash functions)
        self.assertEqual(payload.hex(), ''.join([pubkey2, pubkey1]))

        # no address in this case

        # documented test case: https://learnmeabitcoin.com/guide/p2ms
        pubkey1 = "04 cc71eb30d653c0c3163990c47b976f3fb3f37cccdcbedb169a1dfef58bbfbfaf f7d8a473e7e2e6d317b87bafe8bde97e3cf8f065dec022b51d11fcdd0d348ac4"
        pubkey2 = "04 61cbdcc5409fb4b4d42b51d33381354d80e550078cb532a34bfa2fcfdeb7d765 19aecc62770f5b0e4ef8551946d8a540911abe3e7854a26f39f58b25c15342af"
        pubkeys = [pubkey1, pubkey2]
        m = 1
        n = 2
        lexicographic_sort = False
        script = "514104cc71eb30d653c0c3163990c47b976f3fb3f37cccdcbedb169a1dfef58bbfbfaff7d8a473e7e2e6d317b87bafe8bde97e3cf8f065dec022b51d11fcdd0d348ac4410461cbdcc5409fb4b4d42b51d33381354d80e550078cb532a34bfa2fcfdeb7d76519aecc62770f5b0e4ef8551946d8a540911abe3e7854a26f39f58b25c15342af52ae"
        scriptPubKey = p2ms(1, pubkeys, lexicographic_sort)
        self.assertEqual(scriptPubKey.hex(), script)

        # Impossible m>n 3-of-2 multisignature
        self.assertRaises(ValueError, p2ms, 3, pubkeys)
        #p2ms(3, pubkeys)

        # Invalid m (0) for p2ms script
        self.assertRaises(ValueError, p2ms, 0, pubkeys)
        #p2ms(0, pubkeys)

        # Invalid size: 66 bytes instead of 65
        self.assertRaises(ValueError, p2ms, 1, [pubkey1+"00", pubkey2])
        #p2ms(1, [pubkey1+"00", pubkey2])

        # Invalid n (17) in 3-of-17 multisignature
        self.assertRaises(ValueError, p2ms, 3, [pubkey1]*17)
        #p2ms(3, [pubkey1]*17)

    def test_nulldata(self):

        script_type = 'nulldata'

        # self-consistency
        string = "time-stamped data"
        payload = string.encode()
        script = encode(['OP_RETURN', payload])

        # straight to the scriptPubKey
        scriptPubKey = nulldata(string)
        self.assertEqual(scriptPubKey.hex(), script.hex())

        # to the scriptPubKey in two steps (trhough payload)
        scriptPubKey = scriptPubKey_from_payload(script_type, payload)
        self.assertEqual(scriptPubKey.hex(), script.hex())

        # back from the scriptPubKey to the payload
        script_type2, payload2, m2 = payload_from_scriptPubKey(scriptPubKey)
        self.assertEqual(script_type, script_type2)
        self.assertEqual(0, m2)
        self.assertEqual(payload.hex(), payload2.hex())
        script_type2, payload2, m2 = payload_from_scriptPubKey(decode(script))
        self.assertEqual(script_type, script_type2)
        self.assertEqual(0, m2)
        self.assertEqual(payload.hex(), payload2.hex())

        # data -> payload in this case is invertible (no hash functions)
        self.assertEqual(payload.decode(), string)

        # no address in this case

        ### documented test cases: https://learnmeabitcoin.com/guide/nulldata
        string = "hello world"
        payload = string.encode()
        self.assertEqual(payload.hex(), "68656c6c6f20776f726c64")
        script = bytes.fromhex("6a0b68656c6c6f20776f726c64")
        scriptPubKey = nulldata(string)
        self.assertEqual(scriptPubKey.hex(), script.hex())
        scriptPubKey = scriptPubKey_from_payload(script_type, payload)
        self.assertEqual(scriptPubKey.hex(), script.hex())
        script_type2, payload2, m2 = payload_from_scriptPubKey(scriptPubKey)
        self.assertEqual(script_type, script_type2)
        self.assertEqual(0, m2)
        self.assertEqual(payload.hex(), payload2.hex())

        ### documented test cases: https://learnmeabitcoin.com/guide/nulldata
        string = "charley loves heidi"
        payload = string.encode()
        self.assertEqual(payload.hex(), "636861726c6579206c6f766573206865696469")
        script = bytes.fromhex("6a13636861726c6579206c6f766573206865696469")
        scriptPubKey = nulldata(string)
        self.assertEqual(scriptPubKey.hex(), script.hex())
        scriptPubKey = scriptPubKey_from_payload(script_type, payload)
        self.assertEqual(scriptPubKey.hex(), script.hex())
        script_type2, payload2, m2 = payload_from_scriptPubKey(scriptPubKey)
        self.assertEqual(script_type, script_type2)
        self.assertEqual(0, m2)
        self.assertEqual(payload.hex(), payload2.hex())

        ### documented test cases: https://learnmeabitcoin.com/guide/nulldata
        string = "家族も友達もみんなが笑顔の毎日がほしい"
        payload = string.encode()
        self.assertEqual(payload.hex(), "e5aeb6e6978fe38282e58f8be98194e38282e381bfe38293e381aae3818ce7ac91e9a194e381aee6af8ee697a5e3818ce381bbe38197e38184")
        script = bytes.fromhex("6a39e5aeb6e6978fe38282e58f8be98194e38282e381bfe38293e381aae3818ce7ac91e9a194e381aee6af8ee697a5e3818ce381bbe38197e38184")
        scriptPubKey = nulldata(string)
        self.assertEqual(scriptPubKey.hex(), script.hex())
        scriptPubKey = scriptPubKey_from_payload(script_type, payload)
        self.assertEqual(scriptPubKey.hex(), script.hex())
        script_type2, payload2, m2 = payload_from_scriptPubKey(scriptPubKey)
        self.assertEqual(script_type, script_type2)
        self.assertEqual(0, m2)
        self.assertEqual(payload.hex(), payload2.hex())

    def test_nulldata2 (self):

        script_type = 'nulldata'

        ### max length case
        byte = b'\x00'
        for length in (0, 1, 16, 17, 74, 75, 80):
            payload = byte*length
            script = encode(['OP_RETURN', payload])

            scriptPubKey = scriptPubKey_from_payload(script_type, payload)
            self.assertEqual(scriptPubKey.hex(), script.hex())

            # back from the scriptPubKey to the payload
            script_type2, payload2, m2 = payload_from_scriptPubKey(scriptPubKey)
            self.assertEqual(script_type, script_type2)
            self.assertEqual(0, m2)
            self.assertEqual(payload.hex(), payload2.hex())
            script_type2, payload2, m2 = payload_from_scriptPubKey(decode(script))
            self.assertEqual(script_type, script_type2)
            self.assertEqual(0, m2)
            self.assertEqual(payload.hex(), payload2.hex())


        ### Invalid data lenght (81 bytes) for nulldata scriptPubKey
        payload = '00'*81
        self.assertRaises(ValueError, scriptPubKey_from_payload, 'nulldata', payload)
        #scriptPubKey_from_payload('nulldata', payload)

    def test_p2pkh(self):

        script_type = 'p2pkh'

        # self-consistency
        pubkey = "04cc71eb30d653c0c3163990c47b976f3fb3f37cccdcbedb169a1dfef58bbfbfaff7d8a473e7e2e6d317b87bafe8bde97e3cf8f065dec022b51d11fcdd0d348ac4"
        payload = hash160(pubkey)
        script = encode(['OP_DUP', 'OP_HASH160', payload, 'OP_EQUALVERIFY', 'OP_CHECKSIG'])

        # straight to the scriptPubKey
        scriptPubKey = p2pkh(pubkey)
        self.assertEqual(scriptPubKey.hex(), script.hex())

        # to the scriptPubKey in two steps (trhough payload)
        scriptPubKey = scriptPubKey_from_payload(script_type, payload)
        self.assertEqual(scriptPubKey.hex(), script.hex())

        # back from the scriptPubKey to the payload
        script_type2, payload2, m2 = payload_from_scriptPubKey(scriptPubKey)
        self.assertEqual(script_type, script_type2)
        self.assertEqual(0, m2)
        self.assertEqual(payload.hex(), payload2.hex())
        script_type2, payload2, m2 = payload_from_scriptPubKey(decode(script))
        self.assertEqual(script_type, script_type2)
        self.assertEqual(0, m2)
        self.assertEqual(payload.hex(), payload2.hex())

        # data -> payload is not invertible (hash functions)

        # address
        network = 'mainnet'
        address = base58address.p2pkh(pubkey, None, network)
        address2 = address_from_scriptPubKey(scriptPubKey, network)
        self.assertEqual(address, address2)
        prefix = p2pkh_prefix_from_network(network)
        address2 = b58address_from_h160(prefix, payload)
        self.assertEqual(address, address2)

        scriptPubKey2, network2 = scriptPubKey_from_address(address)
        self.assertEqual(scriptPubKey2, scriptPubKey)
        self.assertEqual(network2, network)

        # documented test case: https://learnmeabitcoin.com/guide/p2pkh
        payload = "12ab8dc588ca9d5787dde7eb29569da63c3a238c"
        script = "76a91412ab8dc588ca9d5787dde7eb29569da63c3a238c88ac"
        scriptPubKey = scriptPubKey_from_payload(script_type, payload)
        self.assertEqual(scriptPubKey.hex(), script)
        network = 'mainnet'
        address = b"12higDjoCCNXSA95xZMWUdPvXNmkAduhWv"
        address2 = address_from_scriptPubKey(scriptPubKey, network)
        self.assertEqual(address, address2)
        scriptPubKey2, network2 = scriptPubKey_from_address(address)
        self.assertEqual(scriptPubKey2, scriptPubKey)
        self.assertEqual(network2, network)

        # Invalid size: 11 bytes instead of 20
        self.assertRaises(ValueError, scriptPubKey_from_payload, "00"*11, 'p2pkh')
        #p2pkh("00"*11)

    def test_p2sh(self):

        script_type = 'p2sh'

        # self-consistency
        pubkey = "02cc71eb30d653c0c3163990c47b976f3fb3f37cccdcbedb169a1dfef58bbfbfaf"
        pubkey_hash = hash160(pubkey)
        redeem_script = scriptPubKey_from_payload('p2pkh', pubkey_hash)
        payload = hash160(redeem_script)
        script = encode(['OP_HASH160', payload, 'OP_EQUAL'])

        # straight to the scriptPubKey
        scriptPubKey = p2sh(redeem_script)
        self.assertEqual(scriptPubKey.hex(), script.hex())

        # to the scriptPubKey in two steps (trhough payload)
        scriptPubKey = scriptPubKey_from_payload(script_type, payload)
        self.assertEqual(scriptPubKey.hex(), script.hex())

        # back from the scriptPubKey to the payload
        script_type2, payload2, m2 = payload_from_scriptPubKey(scriptPubKey)
        self.assertEqual(script_type, script_type2)
        self.assertEqual(0, m2)
        self.assertEqual(payload.hex(), payload2.hex())
        script_type2, payload2, m2 = payload_from_scriptPubKey(decode(script))
        self.assertEqual(script_type, script_type2)
        self.assertEqual(0, m2)
        self.assertEqual(payload.hex(), payload2.hex())

        # data -> payload is not invertible (hash functions)

        # address
        network = 'mainnet'
        address = base58address.p2sh(redeem_script, network)
        address2 = address_from_scriptPubKey(scriptPubKey, network)
        self.assertEqual(address, address2)
        prefix = p2sh_prefix_from_network(network)
        address2 = b58address_from_h160(prefix, payload)
        self.assertEqual(address, address2)

        scriptPubKey2, network2 = scriptPubKey_from_address(address)
        self.assertEqual(scriptPubKey2, scriptPubKey)
        self.assertEqual(network2, network)

        # documented test case: https://learnmeabitcoin.com/guide/p2sh
        payload = "748284390f9e263a4b766a75d0633c50426eb875"
        script = "a914748284390f9e263a4b766a75d0633c50426eb87587"
        scriptPubKey = scriptPubKey_from_payload(script_type, payload)
        self.assertEqual(scriptPubKey.hex(), script)
        network = 'mainnet'
        address = b"3CK4fEwbMP7heJarmU4eqA3sMbVJyEnU3V"
        address2 = address_from_scriptPubKey(scriptPubKey, network)
        self.assertEqual(address, address2)
        scriptPubKey2, network2 = scriptPubKey_from_address(address)
        self.assertEqual(scriptPubKey2, scriptPubKey)
        self.assertEqual(network2, network)

        # Invalid size: 21 bytes instead of 20
        self.assertRaises(ValueError, scriptPubKey_from_payload, "00"*21, 'p2sh')
        #scriptPubKey_from_payload("00"*21, 'p2sh')

    def test_p2wpkh(self):

        script_type = 'p2wpkh'

        # self-consistency
        pubkey = "02cc71eb30d653c0c3163990c47b976f3fb3f37cccdcbedb169a1dfef58bbfbfaf"
        payload = hash160(pubkey)
        script = encode([0, payload])

        # straight to the scriptPubKey
        scriptPubKey = p2wpkh(pubkey)
        self.assertEqual(scriptPubKey.hex(), script.hex())

        # to the scriptPubKey in two steps (trhough payload)
        scriptPubKey = scriptPubKey_from_payload(script_type, payload)
        self.assertEqual(scriptPubKey.hex(), script.hex())

        # back from the scriptPubKey to the payload
        script_type2, payload2, m2 = payload_from_scriptPubKey(scriptPubKey)
        self.assertEqual(script_type, script_type2)
        self.assertEqual(0, m2)
        self.assertEqual(payload.hex(), payload2.hex())
        script_type2, payload2, m2 = payload_from_scriptPubKey(decode(script))
        self.assertEqual(script_type, script_type2)
        self.assertEqual(0, m2)
        self.assertEqual(payload.hex(), payload2.hex())

        # data -> payload is not invertible (hash functions)

        # address
        network = 'mainnet'
        address = bech32address.p2wpkh(pubkey, network)
        address2 = address_from_scriptPubKey(scriptPubKey, network)
        self.assertEqual(address, address2)
        address2 = b32address_from_witness(0, payload, network)
        self.assertEqual(address, address2)

        scriptPubKey2, network2 = scriptPubKey_from_address(address)
        self.assertEqual(scriptPubKey2, scriptPubKey)
        self.assertEqual(network2, network)

    def test_p2wsh(self):

        script_type = 'p2wsh'

        # self-consistency
        pubkey = "02cc71eb30d653c0c3163990c47b976f3fb3f37cccdcbedb169a1dfef58bbfbfaf"
        pubkey_hash = hash160(pubkey)
        redeem_script = scriptPubKey_from_payload('p2pkh', pubkey_hash)
        payload = sha256(redeem_script)
        script = encode([0, payload])

        # straight to the scriptPubKey
        scriptPubKey = p2wsh(redeem_script)
        self.assertEqual(scriptPubKey.hex(), script.hex())

        # to the scriptPubKey in two steps (trhough payload)
        scriptPubKey = scriptPubKey_from_payload(script_type, payload)
        self.assertEqual(scriptPubKey.hex(), script.hex())

        # back from the scriptPubKey to the payload
        script_type2, payload2, m2 = payload_from_scriptPubKey(scriptPubKey)
        self.assertEqual(script_type, script_type2)
        self.assertEqual(0, m2)
        self.assertEqual(payload.hex(), payload2.hex())
        script_type2, payload2, m2 = payload_from_scriptPubKey(decode(script))
        self.assertEqual(script_type, script_type2)
        self.assertEqual(0, m2)
        self.assertEqual(payload.hex(), payload2.hex())

        # data -> payload is not invertible (hash functions)

        # address
        network = 'mainnet'
        address = bech32address.p2wsh(redeem_script, network)
        address2 = address_from_scriptPubKey(scriptPubKey, network)
        self.assertEqual(address, address2)
        address2 = b32address_from_witness(0, payload, network)
        self.assertEqual(address, address2)

        scriptPubKey2, network2 = scriptPubKey_from_address(address)
        self.assertEqual(scriptPubKey2, scriptPubKey)
        self.assertEqual(network2, network)

    def test_exceptions(self):

        # Invalid size: 11 bytes instead of 20
        self.assertRaises(ValueError, scriptPubKey_from_payload, "00"*11, 'p2wpkh')
        #scriptPubKey_from_payload("00"*11, 'p2wpkh')

        # Invalid size: 33 bytes instead of 32
        self.assertRaises(ValueError, scriptPubKey_from_payload, "00"*33, 'p2wsh')
        #scriptPubKey_from_payload("00"*33, 'p2wsh')

        # Unknown script
        script = [16, 20*b'\x00']
        self.assertRaises(ValueError, address_from_scriptPubKey, script)
        #address_from_scriptPubKey(script)

        # Unhandled witness version (16)
        addr = b32address_from_witness(16, 20*b'\x00')
        self.assertRaises(ValueError, scriptPubKey_from_address, addr)
        #scriptPubKey_from_address(addr)

    def test_CLT(self):

        network = 'mainnet'

        vault_pubkeys = [b'\x00'*33, b'\x11'*33, b'\x22'*33]
        recovery_pubkeys = [b'\x77'*33, b'\x88'*33, b'\x99'*33]
        redeem_script = encode([
            'OP_IF',
                2, *vault_pubkeys, 3, 'OP_CHECKMULTISIG',
            'OP_ELSE',
                500, 'OP_CHECKLOCKTIMEVERIFY', 'OP_DROP',
                2, *recovery_pubkeys, 3, 'OP_CHECKMULTISIG',
            'OP_ENDIF'
        ])
        payload = sha256(redeem_script)
        script = "00207b5310339c6001f75614daa5083839fa54d46165f6c56025cc54d397a85a5708"

        scriptPubKey = p2wsh(redeem_script)
        self.assertEqual(scriptPubKey.hex(), script)
        scriptPubKey = scriptPubKey_from_payload('p2wsh', payload)
        self.assertEqual(scriptPubKey.hex(), script)

        address = b"bc1q0df3qvuuvqqlw4s5m2jsswpelf2dgct97mzkqfwv2nfe02z62uyq7n4zjj"
        address2 = address_from_scriptPubKey(scriptPubKey, network)
        self.assertEqual(address, address2)
        address2 = bech32address.p2wsh(redeem_script, network)
        self.assertEqual(address, address2)
        address2 = b32address_from_witness(0, payload, network)
        self.assertEqual(address, address2)


if __name__ == "__main__":
    # execute only if run as a script
    unittest.main()  # pragma: no cover
