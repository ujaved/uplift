Simple matching engine for service providers
---------------------------------------------

A light-weight service for sorting, ranking, and displaying a list of skilled service providers. Providers have several attributes which are filterable.

Run service
--------------
Run the script `run.sh` to launch the service container. This takes one comamnd-line argument specifying the path of the .json data file. For example: `./run.sh $(pwd)/providers.json`
The script creates the image from the Dockerfile and lauches the container with the endpoint http://localhost:5000, returning the container ID.

REST API
---------------
---------------

The REST API has a single `GET` endpoint: `/providers` that searches a [tinydb](https://github.com/msiemens/tinydb) with queries built from the request parameters.
The response is of the form
`
{
  content: [], // all retrieved records will go in this array
  page: 1, // current page
  total_results: 100 // total number of items
}
`

Pagination
-----------

The API provides pagination, as determined by the request:

`curl -G http://localhost:5000/providers --data-urlencode 'page=1' --data-urlencode 'results_per_page=10' | json_pp`


Sorting
--------

Results can be sorted by providing the sort key/s and direction, with sorting order from left to right:

`curl -G http://127.0.0.1:5000/providers --data-urlencode 'sort=rating:desc,first_name:asc,query_count'  | json_pp`

The above query will return all records sorted first by the provider rating by descending order, then alphabetically on the first name, and finally with providers who have been returned fewer times (in the current session) towards the front of the list.

Filtering
----------

Results can be filtered by providing the filter keys and conditions as query parameters:

`curl -G http://127.0.0.1:5000/providers --data-urlencode 'page=1' --data-urlencode 'results_per_page=5' --data-urlencode 'country=China' --data-urlencode 'sex=Male' --data-urlencode 'active=true'  | json_pp`

The above query will return the top five Chinese active male providers. Note that `=` provides exact string, boolean and numeric matches, with duplicate keys ignored.

Comparison operators can also be used for numeric and string fields. The following query will result in all active Chinese male providers having rating at least 8.0: 

`curl -G http://127.0.0.1:5000/providers --data-urlencode 'country=China' --data-urlencode 'sex=Male' --data-urlencode 'active=true' --data-urlencode 'rating=gte:8'  | json_pp`

For the two list fields `primary_skills` and `secondary_skill`, `any` and `all` comparisons are provided:

`curl -G http://127.0.0.1:5000/providers --data-urlencode 'primary_skills=all:messaging frameworks, css' --data-urlencode 'secondary_skill=any:APIs, batch processing'  | json_pp`



Unit Testing
--------------
Run the script `run_tests.sh` to run unit tests.
Unit tests are contained in the file `tst/server.py` and use the `pytest` framework


Possible Extensions
---------------------

1. Currently the database is recreated from the providers file every time the container spins up. The database location is the current directory. To provide persistence, we could have a dedicated, permanent db instance. Furthermore, at
container startup time, only the record ids that don't currently exist in the db should be added.

2. To keep count of how many times a record is returned, we currently maintain an in-memory map. This means that the counts are lost everytime the container is killed. This count could be persisted as an additional db field.

3. Filtering could be improved by providing a range operator.

4. String matching could be based on a regular expression.

5. List fields could be automatically detected in the schema. 