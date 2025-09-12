import pytest
from tally.blockchain import Block, make_genesis_block

def test_block_hash_consistency():
    block = Block(1, '0'*64, [], 1710000001, 0)
    hash1 = block.compute_hash()
    hash2 = block.compute_hash()
    assert hash1 == hash2

def test_genesis_block():
    genesis = make_genesis_block()
    assert genesis.index == 0
    assert genesis.prev_hash == '0' * 64