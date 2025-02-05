class Exchange:
    """
        Exchange is how unisqap calls the liquidity pools
    """

    def __init__(self, token0_name: str, token1_name: str, name: str, symbol: str) -> None:
        self.token0 = token0_name
        self.token1 = token1_name
        self.reserve0 = 0
        self.reserve1 = 0
        self.fee = 0

        self.name = name
        self.symbol = symbol
        self.liquidity_providers = {}
        self.total_supply = 0

    def quote(self, amount0, reserve0, reserve1):
        """
            Given some amount of an asset and pair reserve, returns an equivalent the other asset (i.e. keeps the ratio reserve0/reserve1 the same
            
            Maths behind:
            r0/r1 = (r0 + x)/(r1 + y)
            y = ((r0 + x) * r1)/r0 - r1 = r1 + (r1 * x)/r0 - r1 = (r1 * x)/r0
        """
        assert amount0 > 0, "UniswapV2Library: INSUFFICIENT_AMOUNT"
        assert reserve0 > 0 and reserve1 > 0, "UniswapV2Library: INSUFFICIENT_LIQUIDITY"
        return (amount0 * reserve1) / reserve0


    def _add_liquidity(self, balance0, balance1):
        """
            You always need to add liquidity to both types of coins
        """
        if self.reserve0 == 0 and self.reserve1 == 0:
            # initializing pools
            amount0 = balance0
            amount1 = balance1
        else:
            balance1Optimal = self.quote(balance0, self.reserve0, self.reserve1)
            if balance1Optimal <= balance1:
                amount0 = balance0
                amount1 = balance1Optimal
            else:
                balance0Optimal = self.quote(balance1, self.reserve1, self.reserve0)
                assert balance0Optimal <= balance0
                amount0 = balance0Optimal
                amount1 = balance1
        
        self.reserve0 += amount0
        self.reserve1 += amount1

    def get_amount_out(self, amount_in):
        """
            Given an input amount of an asset and pair reserve, returns the maximum output amount of the other asset
            
            (reserve0 + amount_in_with_fee) * (reserve1 - amount_out) = reserve1 * reserve0

            Math behind:
            r0 * r1 = (r0 * x) * (r1 - y)
            x - amount input
            y - amount out
            r1 - y = (r0 * r1) / (r0 * x)
            y = r1 - (r0 * r1) / (r0 + x) = (r1 * r0 + r1 * x - r0 * r1) / (r0 + x) = (r1 * x) / (r0 + x)
                => y = (r1 * x) / (r0 + x)  [multiply by 1000 or other amount to adjust for fees]
        """
        assert amount_in > 0, "UniswapV2Library: INSUFFICIENT_INPUT_AMOUNT"
        assert self.reserve0 > 0 and self.reserve1 > 0, "UniswapV2Library: INSUFFICIENT_LIQUIDITY"

        amount_in_with_fee = amount_in * 1000 # 997 if fee 0.3%
        numerator = amount_in_with_fee * self.reserve1
        denominator = self.reserve0 * 1000 + amount_in_with_fee
        amount_out = numerator / denominator

        return amount_out

    def swapExactTokensForTokens(self, amount0_in, amount1_out_min):
        amount0_out = 0
        amount1_out = self.get_amount_out(amount0_in)
        assert amount1_out >= amount1_out_min, "UniswapV2Router: INSUFFICIENT_OUTPUT_AMOUNT"

        assert amount1_out > 0, "UniswapV2: INSUFFICIENT_OUTPUT_AMOUNT"
        assert amount0_out < self.reserve0 and amount1_out < self.reserve1, "UniswapV2: INSUFFICIENT_LIQUIDITY"

        balance0 = self.reserve0 + amount0_in - amount0_out
        balance1 = self.reserve1 - amount1_out
        balance0_adjusted = balance0 * 1000
        balance1_adjusted = balance1 * 1000
        # print(amount1_out)
        # print(f"{balance0_adjusted} {balance1_adjusted} {self.reserve0} {self.reserve1}") 
        assert balance0_adjusted * balance1_adjusted == self.reserve0 * self.reserve1 * 1000**2, "UniswapV2: K"

        self.reserve0 = balance0
        self.reserve1 = balance1

        return amount1_out
