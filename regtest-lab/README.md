# Bitcoin Core - regtest lab session

Please install and run Bitcoin Core for your platform, following the instructions provided in
[windows.md](https://github.com/dginst/BitcoinBlockchainTechnology/blob/master/regtest-lab/windows.md),
[linux.md](https://github.com/dginst/BitcoinBlockchainTechnology/blob/master/regtest-lab/linux.md), or
[mac-os.md](https://github.com/dginst/BitcoinBlockchainTechnology/blob/master/regtest-lab/mac-os.md).

In general any command line must starts with `bitcoin-cli -regtest [...]` to use the regtest daemon process. In the GUI console environment `bitcoin-cli -regtest` is already assumed and just `[...]` must be typed. 

* to connect to one peculiar node of the network  
   ```
   bitcoin-cli -regtest addnode “ipaddress-to-be-comunicated-in-class” “add”
   ```
* to generate 101 blocks  
   ```
   bitcoin-cli -regtest generate 101
   ```
* stop the daemon (and the GUI) with the command
  ```
  bitcoin-cli -regtest stop
  ```

For a [full command list](https://bitcoincore.org/en/doc/0.17.0/):
   ```
   bitcoin-cli help
   ```

For help about a peculiar command (e.g. [generate](https://bitcoincore.org/en/doc/0.17.0/rpc/generating/generate/)):
   ```
   bitcoin-cli generate
   ```


To go beyond the short lab class, please see <https://github.com/dginst/Learning-Bitcoin-from-the-Command-Line>