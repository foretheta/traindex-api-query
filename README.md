# traindex-api-query
Basic query to access Traindex API

Please make sure to provide your Traindex API key to the line 8 in the script file.

There are two ways to make the query to Traindex API.

1. Use traindex_query.py if you want to input the string query inside the script file.
2. Use traindex_query.py if the string query is stored in a text file named `source.txt`

There are two methods to make the API call in each file.
- `get_full_output` method will save all the items in the API output to csv file.
- `get_filtered_output_by_date` will filter out the items match the requirement in the first line (as in the sample).  
Ex: Published before 2014-09-30