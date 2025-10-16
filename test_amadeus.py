from amadeus import Client

client = Client(
    client_id='DcWlSGNyMqJqmPdzEYHbuuH6dCaZTIBs',
    client_secret='DI394JIvwoEfln5D',
    hostname='test'
)

try:
    response = client.reference_data.locations.get(keyword='NYC', subType='CITY')
    print("✅ Success!")
    print(f"Found {len(response.data)} locations")
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()