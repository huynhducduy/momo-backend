def Merchant(data):
    return {
        "id": data[0],
        "name": data[1],
        "address": data[2],
        "price_range": data[3],
        "category_id": data[4],
    }
