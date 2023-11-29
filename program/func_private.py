from datetime import datetime, timedelta
from func_utils import format_number
import time
import json

from pprint import pprint

# Get existing open positions
def is_open_positions(client, market):

  # Protect API
  time.sleep(0.2)

  # Get positions
  all_positions = client.private.get_positions(
    market=market,
    status="OPEN"
  )

  # Determine if open
  if len(all_positions.data["positions"]) > 0:
    return True
  else:
    return False
  
# Check order status
def check_order_status(client, order_id):
  order = client.private.get_order_by_id(order_id)
  if order.data:
    if "order" in order.data.keys():
      return order.data["order"]["status"]
  return "FAILED"

def get_account_response(client):
  account_response = client.private.get_account().data['account']['openPositions']
  return account_response
  
# Place market order
def place_market_order(client, market, side, size, price, reduce_only):
  try:
    # Get Position Id
    account_response = client.private.get_account()
    position_id = account_response.data["account"]["positionId"]

    # Get expiration time
    server_time = client.public.get_time()
    expiration = datetime.fromisoformat(server_time.data["iso"].replace("Z", '+00:00')) + timedelta(seconds=120)

    # Place an order
    placed_order = client.private.create_order(
      position_id=position_id, # required for creating the order signature
      market=market,
      side=side,
      order_type="MARKET",
      post_only=False,
      size=size,
      price=price,
      limit_fee='0.015',
      expiration_epoch_seconds=expiration.timestamp(),
      time_in_force="FOK", 
      reduce_only=reduce_only
    )

    print(placed_order.data)
    # Return result
    return placed_order.data
  
  except Exception as e:
    print("Error occurred:", e)
    # traceback.print_exc()

    
# Abort all open position
def abort_all_positions(client):
  # Cancel all orders
  client.private.cancel_all_orders()

  # Protect API
  time.sleep(0.5)

  # Get markets for reference of tick size
  markets = client.public.get_markets().data

  # Protect API
  time.sleep(0.5)

  # Get all open positions
  positions = client.private.get_positions(status="OPEN")
  all_positions = positions.data['positions']

  # Handle open positions
  close_orders = []
  if len(all_positions) > 0:

    for position in all_positions:

      # Determine market
      market = position['market']

      # Determine Side
      side = 'BUY'
      if position['side'] == 'LONG':
        side = 'SELL'

      # Get price
      price = float(position['entryPrice'])
      accept_price = price * 1.7 if side == 'BUY' else price * 0.3
      tick_size = float(markets['markets'][market]['tickSize'])

      accept_price = format_number(accept_price, tick_size)
      accept_price = round(accept_price / tick_size) * tick_size
      accept_price = '{:.2f}'.format(accept_price)  # Format the price to two decimal places

      # Place order to close
      order = place_market_order(
        client,
        market,
        side,
        position['sumOpen'],
        accept_price,
        True
      )

      # Append the result
      close_orders.append(order)

      # Override json file with empty list
      bot_agents = []
      with open('bot_agents.json', 'w') as f:
        json.dump(bot_agents, f)

      # # Protect API
      time.sleep(0.2)

      # Return closed orders
      return close_orders
