void OnTick() {
   string signal="";
      
   //symbol, period, 20 candles, deviation 2, no shift, close price, candle
   double MiddleBB=iBands(_Symbol, _Period, 20, 2, 0, PRICE_CLOSE, MODE_MAIN, 1);
   double LowerBB=iBands(_Symbol, _Period, 20, 2, 0, PRICE_CLOSE, MODE_LOWER, 1);
   double UpperBB=iBands(_Symbol, _Period, 20, 2, 0, PRICE_CLOSE, MODE_UPPER, 1);
      
   //same but candle before
   double PrevMiddleBB=iBands(_Symbol, _Period, 20, 2, 0, PRICE_CLOSE, MODE_MAIN, 2);
   double PrevLowerBB=iBands(_Symbol, _Period, 20, 2, 0, PRICE_CLOSE, MODE_LOWER, 2);
   double PrevUpperBB=iBands(_Symbol, _Period, 20, 2, 0, PRICE_CLOSE, MODE_UPPER, 2);
      
   //calculate the RSI value
   double RSIValue = iRSI(_Symbol, _Period, 14, PRICE_CLOSE, 0); 
      
   if (CountPositions(0) == 0 && Low[2] < PrevLowerBB && Low[1] > LowerBB && RSIValue<30) {
      signal="buy";
      OrderSend(_Symbol, OP_BUY, 0.01, Ask, 3, Ask-0.005, Ask+0.001, NULL, 0, 0, Green);
   }
      
   if (CountPositions(1) == 0 && High[2] > PrevUpperBB && High[1] < UpperBB && RSIValue>70) {
      signal="sell";
      OrderSend(_Symbol, OP_SELL, 0.01, Bid, 3, Bid+0.005, Bid-0.001, NULL, 0, 0, Red);
   }
            
   Comment("Signal: ", signal);
}
  
int CountPositions(int state) {
   //local variable for buy positions
   int nbr_buy = 0;
   int nbr_sell = 0;
      
   //go through all open positions
   for (int i=OrdersTotal()-1; i >= 0; i--) {
      //select an open trade
      OrderSelect(i, SELECT_BY_POS, MODE_TRADES);
      //get the currency pair
      string CurrencyPair = OrderSymbol();
      //check if the symbol matches the currency pair
      if (OrderType() == OP_BUY)
         nbr_buy = nbr_buy + 1;
      if (OrderType() == OP_SELL)
         nbr_sell = nbr_sell + 1;
   }
   if (state == 0)
      return nbr_buy;
   if (state == 1)
      return nbr_sell;
}