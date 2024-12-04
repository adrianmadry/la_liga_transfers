from stats_from_api import endpoint_validation, extract_data, get_api_response, gather_all_pages_data, fetch_data_from_api, get_players_stats, get_transfers_data, list_of_ints, get_teams_from_country
import unittest
from unittest.mock import patch, Mock, mock_open
from requests.exceptions import HTTPError, ReadTimeout, ConnectionError, MissingSchema, RequestException
import pandas as pd


class TestEndpointValidation(unittest.TestCase):
    def test_players_endpoint(self):
        endpoint = 'players'
        result = endpoint_validation(endpoint)
        expected_result = 'statistics'
        
        self.assertEqual(result, expected_result)

    def test_transfers_endpoint(self):
        endpoint = 'transfers'
        result = endpoint_validation(endpoint)
        expected_result = endpoint
        
        self.assertEqual(result, expected_result)
        
    def test_invalid_endoint(self):
        endpoint = 'something'
        
        with self.assertRaises(ValueError):
            endpoint_validation(endpoint)

class TestExtractData(unittest.TestCase):
    # Test when there's only one element inside the key(endpoint) list (literally func have to only remove list from record['transfers'] value)
    def test_one_elem_inside_key_list(self):
        dataset = [
            {'player': {'id': 25, 'name': 'Kowalski'},
             'transfers': [{'date': '2000-03-03', 'type': 'Free'}]},
             {'player': {'id': 8, 'name': 'Majski'},
             'transfers': [{'date': '2000-05-05', 'type': 'Free'}]}    
        ]
        endpoint = 'transfers'
        
        result = extract_data(dataset, endpoint)
        
        expected_result = [
            {'player': {'id': 25, 'name': 'Kowalski'},
             'transfers': {'date': '2000-03-03', 'type': 'Free'}},
            {'player': {'id': 8, 'name': 'Majski'},
             'transfers': {'date': '2000-05-05', 'type': 'Free'}}   
        ]
        
        self.assertEqual(result, expected_result)
    
    # Test when there are multiple elements inside the key list (create a new dict for eac )    
    def test_more_elem_inside_key_list(self):
        dataset = [
            {'player': {'id': 25, 'name': 'Kowalski'},
             'transfers': [{'date': '2000-03-03', 'type': 'Free'},
                           {'date': '2001-04-04', 'type': '2M'}]},
             {'player': {'id': 8, 'name': 'Majski'},
             'transfers': [{'date': '2000-05-05', 'type': 'Free'},
                           {'date': '2002-05-05', 'type': '2K'}]}    
        ]
        endpoint = 'transfers'
        result = extract_data(dataset, endpoint)
        expected_result = [
            {'player': {'id': 25, 'name': 'Kowalski'},
             'transfers': {'date': '2000-03-03', 'type': 'Free'}},
            {'player': {'id': 25, 'name': 'Kowalski'},
             'transfers': {'date': '2001-04-04', 'type': '2M'}},
            {'player': {'id': 8, 'name': 'Majski'},
             'transfers': {'date': '2000-05-05', 'type': 'Free'}},
            {'player': {'id': 8, 'name': 'Majski'},
             'transfers': {'date': '2002-05-05', 'type': '2K'}}    
        ]
        
        self.assertEqual(result, expected_result)
        
    # Test when th key list is empty  
    def test_empty_key_list(self):
        dataset = [
            {'player': {'id': 25, 'name': 'Kowalski'},
             'transfers': [{'date': '2000-03-03', 'type': 'Free'},
                           {'date': '2001-04-04', 'type': '2M'}]},
             {'player': {'id': 8, 'name': 'Majski'},
             'transfers': []}    
        ]
        endpoint = 'transfers'
        result = extract_data(dataset, endpoint)
        expected_result = [
            {'player': {'id': 25, 'name': 'Kowalski'},
             'transfers': {'date': '2000-03-03', 'type': 'Free'}},
            {'player': {'id': 25, 'name': 'Kowalski'},
             'transfers': {'date': '2001-04-04', 'type': '2M'}}      
        ]
        
        self.assertEqual(result, expected_result)
    
    
class TestListOfInts(unittest.TestCase):
    
    # Single range input
    def test_range_input(self):
        input_list = [range(1, 7)]
        result = list_of_ints(input_list)
        expected_result = [1, 2, 3, 4, 5, 6]
        self.assertEqual(result, expected_result)
    
    # Single int input
    def test_int_input(self):
        input_list = [3]
        result = list_of_ints(input_list)
        expected_result = [3]
        self.assertEqual(result, expected_result)
    
    # Combination of int and range
    def test_combined_input(self):
        input_list = [range(1,3), 44, -1, range(-3, 2)]
        result = list_of_ints(input_list)
        expected_result = [1, 2, 44, -1, -3, -2, -1, 0, 1]
        self.assertEqual(result, expected_result)  
        
    # Empty input list
    def test_empty_input(self):
        input_list = []
        result = list_of_ints(input_list)
        expected_result = []
        self.assertEqual(result, expected_result)
    
    # Invalid dtype input    
    def test_invalid_input(self):
        input_list = [range(1, 4), "string", 5]
        with self.assertRaises(ValueError):
            list_of_ints(input_list)
    

class TestGetApiResponse(unittest.TestCase):

    @patch('stats_from_api.requests.get')
    def test_positive_response(self, mock_get):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'foo': {'abc': 'xyz'}}
        
        mock_get.return_value = mock_response
        result = get_api_response('http://example.com/api', {'user': 'key'}, {'param': 'value'})
        self.assertEqual(result, mock_response.json.return_value)

    @patch('stats_from_api.requests.get')
    def test_http_err(self, mock_get): 
        # Simulate HTTP error during requests.get
        mock_get.side_effect = HTTPError("404 Client Error: Not Found for url: http://example.com/api")
        
        with self.assertRaises(HTTPError) as context:
            get_api_response('http://example.com/api', {}, {})

        self.assertEqual(str(context.exception), "404 Client Error: Not Found for url: http://example.com/api")
        
    @patch('stats_from_api.requests.get')
    def test_timeout_err(self, mock_get):
        # Simulate timeout error during requests.get
        mock_get.side_effect = ReadTimeout("Connection timed out")
        
        with self.assertRaises(ReadTimeout) as context:
            get_api_response('http://example.com/api', {}, {})

        self.assertEqual(str(context.exception), "Connection timed out")
        
    @patch('stats_from_api.requests.get')
    def test_connection_err(self, mock_get):
        # Simulate connection error during requests.get
        mock_get.side_effect = ConnectionError("Connection error occurred")
        
        with self.assertRaises(ConnectionError) as context:
            get_api_response('http://example.com/api', {}, {})

        self.assertEqual(str(context.exception), "Connection error occurred")
        
    
    @patch('stats_from_api.requests.get')
    def test_miss_schema_err(self, mock_get):
        # Simulate missing schema error during requests.get
        mock_get.side_effect = MissingSchema("Invalid URL 'example.com/api': No scheme supplied. Perhaps you meant http://example.com/api?")
        
        with self.assertRaises(MissingSchema) as context:
            get_api_response('example.com/api', {}, {})

        self.assertEqual(str(context.exception), "Invalid URL 'example.com/api': No scheme supplied. Perhaps you meant http://example.com/api?")
           
    @patch('stats_from_api.requests.get')
    def test_req_exc_err(self, mock_get):
        # Simulate missing schema error during requests.get
        mock_get.side_effect = RequestException("An unexpected error occurred:")
        
        with self.assertRaises(RequestException) as context:
            get_api_response('example.com/api', {}, {})

        self.assertEqual(str(context.exception), "An unexpected error occurred:")
        
    @patch('stats_from_api.requests.get')
    def test_exception_err(self, mock_get):
        # Create mock object (response)
        mock_response = Mock()
        mock_response.status_code = 400
        
        mock_get.return_value = mock_response
        
        with self.assertRaises(Exception) as context:
            get_api_response('http://example.com/api', {}, {})
        
        self.assertEqual(str(context.exception), "Unexpected status code 400")

class TestGatherAllPagesData(unittest.TestCase):
    
    def test_single_page(self):
        
        data = {"get": "endpoint",
                "parameters": {'sth': 1},
                "paging": {'current': 1, 'total': 1}, 
                "response": [{"foo": 1}, {"xyz": 2}]
                }
        url = ''
        api_headers = {}
        queryparams={}
        
        result = gather_all_pages_data(data, url, api_headers, queryparams)
        expected_result = [{"foo": 1}, {"xyz": 2}]
      
        self.assertEqual(result, expected_result)

    @patch('stats_from_api.get_api_response')
    @patch('time.sleep', Mock())
    def test_more_pages(self, mock_api_resp):
        
        data = {"get": "endpoint",
                "parameters": {'sth': 1},
                "paging": {'current': 1, 'total': 3}, 
                "response": [{"foo": 1}, {"xyz": 2}]
                }
        url = ''
        api_headers = {}
        queryparams={}
        
        # Define mock responses for each page
        mock_responses = [
        {"paging": {'current': 1, 'total': 3},
         'response': [{"k1": "data_value_page_1"}]},
        {"paging": {'current': 2, 'total': 3},
         'response': [{"k2": "data_value_page_2"}]},
        {"paging": {'current': 3, 'total': 3},
         'response': [{"k3": "data_value_page_3"}]}
        ]
        
        # Set side effect to return diif response for each call
        mock_api_resp.side_effect = mock_responses
        
        result = gather_all_pages_data(data, url, api_headers, queryparams)
        
        expected_result = [{"k1": "data_value_page_1"},
                           {"k2": "data_value_page_2"},
                           {"k3": "data_value_page_3"}]
      
        self.assertEqual(result, expected_result)
        
    def test_empty_response(self):
        
        data = {"get": "endpoint",
                "parameters": {'sth': 1},
                "paging": {'current': 1, 'total': 1}, 
                "response": []
                }
        url = ''
        api_headers = {}
        queryparams={}
        
        result = gather_all_pages_data(data, url, api_headers, queryparams)
        expected_result = []
      
        self.assertEqual(result, expected_result)
    
class TestFetchDataFromApi(unittest.TestCase):
    
    # Test when given endpoint isn't "teams"
    @patch('stats_from_api.get_api_response')
    @patch('stats_from_api.gather_all_pages_data')
    @patch('stats_from_api.extract_data')
    def test_fetch_data_from_api(self, mock_extract, mock_gather, mock_get):
        url = ''
        endpoint = 'endpoint'
        api_headers = {}
        queryparams={}
        data = {"get": "some",
                "parameters": {'sth': 1},
                "paging": {'current': 1, 'total': 1}, 
                "response": [{"foo": 1}, {"xyz": 2}]
                }
        all_pages_data = [{"foo": 1}, {"xyz": 2}]
        extracted_data = [{"foo": 1}, {"xyz": 2}]
        
        mock_get.return_value = data
        mock_gather.return_value = all_pages_data
        mock_extract.return_value = extracted_data
        
        result_df = fetch_data_from_api(url, endpoint, api_headers, queryparams)
        expected_df = pd.json_normalize(extracted_data)
        
        pd.testing.assert_frame_equal(result_df, expected_df)
        
             
    # Test when given endpoint is "teams"
    @patch('stats_from_api.get_api_response')
    @patch('stats_from_api.gather_all_pages_data')
    def test_fetch_data_from_api_teams_endpoint(self, mock_gather, mock_get):
        url = ''
        endpoint = 'teams'
        api_headers = {}
        queryparams={}
        data = {"get": "some",
                "parameters": {'sth': 1},
                "paging": {'current': 1, 'total': 1}, 
                "response": [{"foo": 1}, {"xyz": 2}]
                }
        all_pages_data = [{"foo": 1}, {"xyz": 2}]
        
        mock_get.return_value = data
        mock_gather.return_value = all_pages_data
        
        result_df = fetch_data_from_api(url, endpoint, api_headers, queryparams)
        expected_df = pd.json_normalize(all_pages_data)
        
        pd.testing.assert_frame_equal(result_df, expected_df)

        
class TestGetPlayerStats(unittest.TestCase):
    
    @patch('stats_from_api.fetch_data_from_api')
    @patch('pandas.DataFrame.to_csv')
    def test_get_players_stats(self, mock_to_csv, mock_fetch):
        url = ''
        api_key = 'key'
        start_season = 2018
        end_season = 2020
        league_id = 1
        
        mock_df = pd.DataFrame({
            'Name': ['Alan', 'John', 'Leo'],
            'Club': ['NYC', 'LA', 'SA'],
            'Score': [2.5, 5.1, 3.8]
        })
           
        mock_fetch.return_value = mock_df
        
        get_players_stats(url, api_key, start_season, end_season, league_id)
        
        expected_calls_to_csv = [
            unittest.mock.call(f'./data/stats_from_season_2018.csv', encoding='utf-8-sig'),
            unittest.mock.call(f'./data/stats_from_season_2019.csv', encoding='utf-8-sig'),
            unittest.mock.call(f'./data/stats_from_season_2020.csv', encoding='utf-8-sig')
        ]
        
        mock_to_csv.assert_has_calls(expected_calls_to_csv)
        
        
    @patch('stats_from_api.fetch_data_from_api')
    @patch('pandas.DataFrame.to_csv')
    def test_get_players_stats_csv_err(self, mock_to_csv, mock_fetch):
        url = ''
        api_key = 'key'
        start_season = 2018
        end_season = 2020
        league_id = 1
        
        mock_df = pd.DataFrame({
            'Name': ['Alan', 'John', 'Leo'],
            'Club': ['NYC', 'LA', 'SA'],
            'Score': [2.5, 5.1, 3.8]
        })
           
        mock_fetch.return_value = mock_df
        
        mock_to_csv.side_effect = Exception("CSV writing error")
        with self.assertRaises(Exception):
            get_players_stats(url, api_key, start_season, end_season, league_id)
            
        mock_to_csv.assert_called()
    
class TestGettransfersData(unittest.TestCase):
    
    # --- Test if 'open' clause has been called correct number of times ---
    @patch('stats_from_api.fetch_data_from_api')
    @patch('stats_from_api.list_of_ints')
    def test_get_transfer_data(self, mock_list_of_ints, mock_fetch):
        url = ''
        api_key = 'key'
        teams_ids = [1, 2, range(5,7), 25]
        
        mock_df = pd.DataFrame({
            'Name': ['Alan', 'John', 'Leo'],
            'Club': ['NYC', 'LA', 'SA'],
            'Score': [2.5, 5.1, 3.8]
        })
        mock_fetch.return_value = mock_df
        mock_list_of_ints.return_value = [1, 2, 5, 6, 25]
        
        with patch('builtins.open', mock_open()) as mock_open_file:
            get_transfers_data(url, api_key, teams_ids)
            
            self.assertEqual(mock_open_file.call_count, 5)
            
class TestGetTeamsFromCountry(unittest.TestCase):
    
    @patch('stats_from_api.fetch_data_from_api')
    @patch('pandas.DataFrame.to_csv')
    def test_get_teams_from_country(self, mock_to_csv, mock_fetch):
        url = ''
        api_key = 'key'
        country = "Poland"
        
        mock_df = pd.DataFrame({
            'Name': ['Alan', 'John', 'Leo'],
            'Club': ['NYC', 'LA', 'SA'],
            'Score': [2.5, 5.1, 3.8]
        })
           
        mock_fetch.return_value = mock_df
        
        get_teams_from_country(url, api_key, country)
        
        expected_calls_to_csv = [unittest.mock.call(f'./data/teams_from_Poland.csv', encoding='utf-8-sig')]
          
        mock_to_csv.assert_has_calls(expected_calls_to_csv)
        
    @patch('stats_from_api.fetch_data_from_api')
    @patch('pandas.DataFrame.to_csv')
    def test_get_teams_from_country_csv_err(self, mock_to_csv, mock_fetch):
        url = ''
        api_key = 'key'
        country = "Poland"
        
        mock_df = pd.DataFrame({
            'Name': ['Alan', 'John', 'Leo'],
            'Club': ['NYC', 'LA', 'SA'],
            'Score': [2.5, 5.1, 3.8]
        })
           
        mock_fetch.return_value = mock_df
        
        mock_to_csv.side_effect = Exception("CSV writing error")
        with self.assertRaises(Exception):
            get_teams_from_country(url, api_key, country)
            
        mock_to_csv.assert_called()
            
            
              
if __name__ == "__main__":
    unittest.main()
