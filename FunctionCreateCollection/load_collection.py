def load(name, numbers, collection_type, year, manufacturer):
    number_array = []
    for line in numbers.splitlines():
        number = (line.strip().split('.')[0]).replace(' ', '')
        text = (line.strip().split('.')[1]).strip(' ')
        number_array.append(dict({'number': number, 'text': text}))

    return {
        'id': name,
        'name':  name, 
        'numbers': number_array,
        'type': collection_type,
        'year': year,
        'manufacturer': manufacturer
    }
