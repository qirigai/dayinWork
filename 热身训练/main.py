from sanic import Sanic
from sanic.response import json
from pymongo import MongoClient


client = MongoClient('mongodb://localhost:27017/')
db = client['book']
collection = db['data']

app = Sanic('__name__')


@app.listener('before_server_start')
async def setup_db(app, loop):
    global collection
    collection = db['data']


@app.listener('after_server_stop')
async def close_db(app, loop):
    client.close()


@app.route('/GET', methods=['GET'])
async def get_data(request):
    data = []
    async for document in collection.find():
        data.append({
            'name': document['book'],
            'id': document['bookid'],
            'description': document['description']
        })
    return json(data)


@app.route('/create', methods=['POST'])
async def create_data(request):
    data = request.json
    document = {
        'book': data['name'],
        'bookid': data['id'],
        'description': data['description']
    }
    result = await collection.insert_one(document)
    return json({'message': 'Data created', 'document_id': str(result.inserted_id)})


@app.route('/update/<document_id>', methods=['PUT'])
async def update_data(request, document_id):
    data = request.json
    updated_document = {
        'book': data['name'],
        'bookid': data['id'],
        'description': data['description']
    }
    result = await collection.update_one({'_id': document_id}, {'$set': updated_document})
    if result.modified_count == 1:
        return json({'message': 'Data updated'})
    else:
        return json({'message': 'Data not found'})


@app.route('/delete/<document_id>', methods=['DELETE'])
async def delete_data(request, document_id):
    result = await collection.delete_one({'_id': document_id})
    if result.deleted_count == 1:
        return json({'message': 'Data deleted'})
    else:
        return json({'message': 'Data not found'})


@app.exception(Exception)
async def handle_exception(request, exception):
    return json({'error': str(exception)})


if __name__ == '__main__':
    app.run(host='localhost', port=8000)