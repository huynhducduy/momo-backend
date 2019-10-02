def Store(data, level=0):
    store = {
        "id": data[0],
        "name": data[1],
        "address": data[2],
        "long": data[3],
        "lat": data[4],
        "merchant_id": data[5],
    }
    if level > 0:
        store['merchant'] = {
            "id": data[6],
            "name": data[7],
            "address": data[8],
            "category_id": data[9]
        }
    if level > 1:
        store['merchant']['category'] = {
            "id": data[10],
            "name": data[11]
        }
    return store
