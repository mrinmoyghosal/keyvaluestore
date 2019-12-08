import json


def test_get_keys_by_id_return_404_if_key_notfound(test_client):
    response = test_client.get('api/keys/blah')
    assert response.status_code == 404


def test_get_return_400_for_bad_filter_regex(test_client):
    response = test_client.get('api/keys/blah?filter=*')
    assert response.status_code == 400


def test_get_return_404_if_nokeys_found(test_client):
    response = test_client.get('api/keys')
    assert response.status_code == 404


def test_get_return_key_values_as_expected(test_client):
    data = {'batman': 'robin', 'joker': 'batman'}
    response = test_client.put('api/keys', data=json.dumps(data))
    assert response.status_code == 200
    response = test_client.get('api/keys')
    assert response.get_json() == data
    response = test_client.get('api/keys/batman')
    assert response.get_json() == {'batman': 'robin'}


def test_get_work_as_expected_for_valid_regex(test_client):
    response = test_client.get('api/keys?filter=bat*')
    assert response.get_json() == {'batman': 'robin'}


def test_head_return_404_if_key_not_found(test_client):
    response = test_client.get('api/keys/robin')
    assert response.status_code == 404


def test_head_return_200_if_keys_found(test_client):
    response = test_client.get('api/keys/batman')
    assert response.status_code == 200


def test_delete_return_404_if_key_notfound(test_client):
    response = test_client.delete('api/keys/robin')
    assert response.status_code == 404


def test_delete_work_expected_if_specificed_by_id(test_client):
    response = test_client.delete('api/keys/batman')
    assert response.status_code == 200
    response = test_client.get('api/keys/batman')
    assert response.status_code == 404


def test_delete_delete_all_keyvalues_if_no_id_specified(test_client):
    response = test_client.delete('api/keys')
    assert response.status_code == 200
    response = test_client.get('api/keys')
    assert response.status_code == 404


def test_expiry_works_as_expected(test_client):
    data = {'batman': 'robin', 'joker': 'batman'}
    response = test_client.put('api/keys?expiry=30', data=json.dumps(data))
    assert response.status_code == 200
