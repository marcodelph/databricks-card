import os
import time
import json
import asyncio
import uuid
from faker import Faker
from dotenv import load_dotenv
from azure.eventhub.aio import EventHubProducerClient
from azure.eventhub import EventData

load_dotenv() 

CONNECTION_STR = os.getenv("EVENT_HUB_CONNECTION_STRING")
EVENT_HUB_NAME = "transactions"

if not CONNECTION_STR:
    raise ValueError("EVENT_HUB_CONNECTION_STRING não foi encontrada. Verifique seu arquivo .env")


fake = Faker('pt_BR')

async def run():
    producer = EventHubProducerClient.from_connection_string(
        conn_str=CONNECTION_STR,
        eventhub_name=EVENT_HUB_NAME
    )
    async with producer:
        while True:
            transaction = {
                'transaction_id': str(uuid.uuid4()),
                'timestamp_utc': str(fake.iso8601()),
                'user_id': fake.random_int(min=1000, max=9999),
                'card_number': fake.credit_card_number(),
                'amount_brl': round(fake.random_number(digits=4, fix_len=True) / 100, 2),
                'merchant_name': fake.company(),
                'merchant_city': fake.city()
            }

            transaction_json = json.dumps(transaction)
            
            event_data_batch = await producer.create_batch()
            event_data_batch.add(EventData(transaction_json))

            await producer.send_batch(event_data_batch)
            
            print(f"Transação enviada: {transaction['transaction_id']} | Valor: R$ {transaction['amount_brl']:.2f}")

            await asyncio.sleep(1)

if __name__ == "__main__":
    asyncio.run(run())