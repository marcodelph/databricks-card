import os
import time
import json
import asyncio
import uuid
import random
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

personas = {
    # Categoria Iniciante
    "3003": {"min_amount": 5, "max_amount": 25},
    # Categoria Economico
    "1001": {"min_amount": 10, "max_amount": 80},
    "1003": {"min_amount": 5, "max_amount": 50},
    # Categoria Regular
    "1002": {"min_amount": 80, "max_amount": 500},
    "1004": {"min_amount": 100, "max_amount": 600},
    # Categoria Gastador
    "2002": {"min_amount": 800, "max_amount": 2500},
    "2005": {"min_amount": 1000, "max_amount": 3500},
}
# Lista de IDs de usuário para sorteio
user_ids = list(personas.keys())

# Anomalia
# O usuário '1001' (Econômico) fará uma compra com o perfil do '2002' (Gastador)
ANOMALY_TARGET_USER = "1001"
ANOMALY_BEHAVIOR_SOURCE_USER = "2002"

async def run():
    producer = EventHubProducerClient.from_connection_string(
        conn_str=CONNECTION_STR,
        eventhub_name=EVENT_HUB_NAME
    )
    async with producer:
        while True:
            transaction = {}
            anomaly_type = "none"
            
            # Decide se a transação será uma anomalia injetada (3% de chance)
            if random.random() < 0.03:
                anomaly_type = "ANOMALIA CONTEXTUAL"
                user_id = ANOMALY_TARGET_USER
                source_persona = personas[ANOMALY_BEHAVIOR_SOURCE_USER]
                amount = round(random.uniform(source_persona["min_amount"], source_persona["max_amount"]), 2)
            else:
                # Gera uma transação normal baseada em uma das personas
                user_id = random.choice(user_ids)
                persona = personas[user_id]
                amount = round(random.uniform(persona["min_amount"], persona["max_amount"]), 2)

            transaction = {
                'transaction_id': str(uuid.uuid4()),
                'timestamp_utc': str(fake.iso8601()),
                'user_id': user_id,
                'card_number': fake.credit_card_number(),
                'amount_brl': amount,
                'merchant_name': fake.company(),
                'merchant_city': fake.city()
            }
            
            transaction_json = json.dumps(transaction)
            event_data_batch = await producer.create_batch()
            event_data_batch.add(EventData(transaction_json))
            await producer.send_batch(event_data_batch)
            
            if anomaly_type != "none":
                print(f"!!! {anomaly_type} GERADA !!! -> Usuário: {transaction['user_id']} | Valor: R$ {transaction['amount_brl']:.2f}")
            else:
                print(f"Transação normal enviada -> Usuário: {transaction['user_id']} | Valor: R$ {transaction['amount_brl']:.2f}")

            await asyncio.sleep(0.5)

if __name__ == "__main__":
    asyncio.run(run())