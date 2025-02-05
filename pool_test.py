import pytest
from pool import Exchange

@pytest.fixture
def pool():
    return Exchange(token0_name="Sigma",
                token1_name="Ligma",
                name="Sigma/Ligma",
                symbol="Skibidi"
                )

def test_add_liquidity(pool):
    pool._add_liquidity(1000, 1000)
    assert pool.reserve0 == 1000 and pool.reserve1 == 1000, "Error adding to the pool"

    pool._add_liquidity(20, 30)
    assert pool.reserve0 == 1020 and pool.reserve1 == 1020, "Error adding to the pool"

def test_add_liquidity2(pool):
    pool._add_liquidity(1000, 100)
    assert pool.reserve0 == 1000 and pool.reserve1 == 100, "Error adding to the pool"

    pool._add_liquidity(200, 30)
    assert pool.reserve0 == 1200 and pool.reserve1 == 100 + 100 * 200 / 1000, "Error adding to the pool"

def test_get_amount_out(pool):
    pool._add_liquidity(1000, 1000)
    assert pool.get_amount_out(20) == (20 * 1000) / (1000 + 20), "Smth wrong with get_amount_out"


def test_trading(pool):
    pool._add_liquidity(1000, 1000)
    pool.swapExactTokensForTokens(20, 10)
    assert pool.reserve0 == 1020 and pool.reserve1 == 1000 - (20 * 1000) / (1000 + 20), "Smth wrong with get_amount_out or saving new reserve values"

