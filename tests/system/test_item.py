import json
from models.item import ItemModel
from models.store import StoreModel
from models.user import UserModel
from tests.base_test import BaseTest


class ItemTest(BaseTest):
    def setUp(self):
        super(ItemTest, self).setUp()
        with self.app() as client:
            with self.app_context():
                UserModel('test', '1234').save_to_db()
                auth_response = client.post('/auth',
                                            data=json.dumps({'username': 'test', 'password': '1234'}),
                                            headers={'Content-Type': 'application/json'})
                auth_token = json.loads(auth_response.data)['access_token']
                self.access_token = f'JWT {auth_token}'

    def test_create_item(self):
        with self.app() as client:
            with self.app_context():
                StoreModel('test_store').save_to_db()
                resp = client.post('/item/test', data={'price': 19.99, 'store_id': 1})

                self.assertEqual(201, resp.status_code)
                self.assertDictEqual({'name': 'test', 'price': 19.99, 'store_id': 1}, json.loads(resp.data))

    def test_create_duplicate_item(self):
        with self.app() as client:
            with self.app_context():
                StoreModel('test_store').save_to_db()
                ItemModel('test', 19.99, 1).save_to_db()

                resp = client.post('/item/test', data={'price': 19.99, 'store_id': 1})

                self.assertEqual(400, resp.status_code)

    def test_item_no_auth(self):
        with self.app() as client:
            with self.app_context():
                resp = client.get('/item/test')
                self.assertEqual(401, resp.status_code) # note the missing headers

    def test_item_not_found(self):
        with self.app() as client:
            with self.app_context():
                resp = client.get('/item/test', headers={'Authorization': self.access_token})

                self.assertEqual(404, resp.status_code)
                self.assertDictEqual({'message': 'Item not found'}, json.loads(resp.data))

    def test_get_item(self):
        with self.app() as client:
            with self.app_context():
                StoreModel('test_store').save_to_db()
                ItemModel('test', 19.99, 1).save_to_db()

                resp = client.get('/item/test', headers={'Authorization': self.access_token})

                self.assertEqual(200, resp.status_code)
                self.assertDictEqual({'name': 'test', 'price': 19.99, 'store_id': 1}, json.loads(resp.data))

    def test_delete_item(self):
        with self.app() as client:
            with self.app_context():
                StoreModel('test_store').save_to_db()
                ItemModel('test', 19.99, 1).save_to_db()

                resp = client.delete('/item/test')

                self.assertEqual(200, resp.status_code)
                self.assertDictEqual({'message': 'Item deleted'}, json.loads(resp.data))

    def test_put_new_item(self):
        with self.app() as client:
            with self.app_context():
                StoreModel('test_store').save_to_db()

                resp = client.put('/item/test', data={'price': 19.99, 'store_id': 1})
                self.assertEqual(200, resp.status_code)
                self.assertDictEqual({'name': 'test', 'price': 19.99, 'store_id': 1}, json.loads(resp.data))

    def test_put_update_item(self):
        with self.app() as client:
            with self.app_context():
                StoreModel('test_store').save_to_db()
                ItemModel('test', 19.99, 1).save_to_db()

                resp = client.put('/item/test', data={'price': 5.99, 'store_id': 1})
                self.assertEqual(200, resp.status_code)
                self.assertDictEqual({'name': 'test', 'price': 5.99, 'store_id': 1}, json.loads(resp.data))

    def test_item_list(self):
        with self.app() as client:
            with self.app_context():
                StoreModel('test_store').save_to_db()
                ItemModel('test', 19.99, 1).save_to_db()

                resp = client.get('/items')
                self.assertEqual(200, resp.status_code)
                self.assertDictEqual({'items': [{'name': 'test', 'price': 19.99, 'store_id': 1}]},
                                     json.loads(resp.data))
