This is a caching proxy for Cloudflare Eth Gateway.

It builds upon Flask, that should be installed like this
```
pip install flask
```

To run it simply use
```
python3 api.py
```

Then you can use in your browser local requests of transaction data to Eth Gateway such as:
```
http://127.0.0.1:5000//block/<block_addr>/txs/<tx_id>
```
Where:
`<block_addr>` may be `latest`, `pending` or integer of block index

`<tx_id>` may be integer of transaction index or it's hash started with '0x'


All requests for blocks, which are up to last 20, will be cached in LRU way with size of 128.
