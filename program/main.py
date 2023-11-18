from func_connections import connect_dydx

if __name__ == '__main__':
  
  try:
    print('Connecting to client...')
    client = connect_dydx()
  except Exception as e:
    print('Error connecting to client: ', e)
    # send_message(f'Failed to connect to client {e}')
    exit(1)