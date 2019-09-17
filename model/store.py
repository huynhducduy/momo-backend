def Store(data):
    return {
        "id": data[0],
        "name": data[1],
        "address": data[2],
        "long": data[3],
        "lat": data[4],
        "merchant_id": data[5],
    }
