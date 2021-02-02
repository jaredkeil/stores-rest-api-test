from models.store import StoreModel
from models.item import ItemModel
from tests.base_test import BaseTest
import json


class StoreTest(BaseTest):
    def test_create_store(self):
        with self.app() as client:
            with self.app_context():
                response = client.post('/store/test_store')

                self.assertEqual(response.status_code, 201)
                self.assertIsNotNone(StoreModel.find_by_name('test_store'))
                self.assertDictEqual(json.loads(response.data), {'name': 'test_store', 'items': []})

    def test_create_duplicate_store(self):
        with self.app() as client:
            with self.app_context():
                client.post('/store/test_store')
                response = client.post('/store/test_store')

                self.assertEqual(response.status_code, 400)
                self.assertDictEqual(json.loads(response.data),
                                     {'message': "A store with name 'test_store' already exists."})

    def test_delete_store(self):
        with self.app() as client:
            with self.app_context():
                self.assertIsNone(StoreModel.find_by_name('test_store'))

                client.post('/store/test_store')
                self.assertIsNotNone(StoreModel.find_by_name('test_store'))

                response = client.delete('/store/test_store')
                self.assertEqual(response.status_code, 204)
                self.assertIsNone(StoreModel.find_by_name('test_store'))

    def test_find_store(self):
        with self.app() as client:
            with self.app_context():
                client.post('/store/test_store')

                response = client.get('/store/test_store')

                self.assertEqual(response.status_code, 200)
                self.assertDictEqual(json.loads(response.data), {'name': 'test_store', 'items': []})

    def test_store_not_found(self):
        with self.app() as client:
            with self.app_context():
                self.assertIsNone(StoreModel.find_by_name('test_store'))

                response = client.get('/store/test_store')

                self.assertEqual(response.status_code, 404)
                self.assertDictEqual(json.loads(response.data), {'message': 'Store not found'})

    def test_store_found_with_items(self):
        with self.app() as client:
            with self.app_context():
                client.post('/store/test_store')

                ItemModel('item1', 19.99, 1).save_to_db()
                ItemModel('item2', 16.50, 1).save_to_db()

                response = client.get('/store/test_store')

                expected = {
                    'name': 'test_store',
                    'items': [
                        {'name': 'item1',
                         'price': 19.99,
                         'store_id': 1},
                        {'name': 'item2',
                         'price': 16.50,
                         'store_id': 1},
                    ]
                }
                self.assertEqual(response.status_code, 200)
                self.assertDictEqual(json.loads(response.data), expected)

    def test_store_list(self):
        with self.app() as client:
            with self.app_context():
                client.post('/store/abc')
                client.post('/store/xyz')

                response = client.get('/stores')

                expected = {
                    'stores': [
                        {
                            'name': 'abc',
                            'items': []
                        },
                        {
                            'name': 'xyz',
                            'items': []
                        }
                    ]
                }

                self.assertEqual(response.status_code, 200)
                self.assertDictEqual(json.loads(response.data), expected)


    def test_store_list_with_items(self):
        with self.app() as client:
            with self.app_context():
                client.post('/store/abc')
                client.post('/store/xyz')

                ItemModel('item1', 19.99, 1).save_to_db()
                ItemModel('item2', 16.50, 2).save_to_db()

                response = client.get('/stores')

                expected = {
                    'stores': [
                        {
                            'name': 'abc',
                            'items': [{'name': 'item1', 'price': 19.99, 'store_id': 1}]
                        },
                        {
                            'name': 'xyz',
                            'items': [{'name': 'item2', 'price': 16.50, 'store_id': 2}]
                        }
                    ]
                }

                self.assertEqual(response.status_code, 200)
                self.assertDictEqual(json.loads(response.data), expected)