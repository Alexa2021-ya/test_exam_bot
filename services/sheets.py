from gspread import Client, service_account
import re


def client_init_json() -> Client:
    return service_account()


def get_sht_by_id(client: Client, sht_key):
    return client.open_by_key(sht_key)


def get_data(sht_key) -> list[list]:
    client = client_init_json()
    sht = get_sht_by_id(client, sht_key)

    worksheet = sht.sheet1
    data = worksheet.get_all_values()

    return data