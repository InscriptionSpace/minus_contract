
import bitcoin
import bitcoin.rpc

proxy = bitcoin.rpc.Proxy()
block = proxy.getblock(proxy.getblockhash(0))

block.vtx[0].vin[0].serialize()
