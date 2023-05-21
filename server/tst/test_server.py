import server
from tinydb import Query


def test_skill_test_any():
    db_record = ['Error Tolerance', 'Algorithms']
    assert server.skill_test_any(db_record, ['error Tolerance   '])
    assert not server.skill_test_any(db_record, ['algorithm'])


def test_skill_test_all():
    db_record = ['Error Tolerance', 'Algorithms']
    assert server.skill_test_all(
        db_record, ['error Tolerance   ', 'algorithms'])
    assert not server.skill_test_all(db_record, ['algorithms', 'errors'])


def test_process_query_params():
    params = {'A': 'True', 'B': 'false', 'sort': 'rating:desc,first_name:asc,query_count',
              'page': '2', 'results_per_page': '10'}
    page, results_per_page, sort_keys = server.process_query_params(params)
    assert params == {'A': True, 'B': False}
    assert sort_keys == [['rating', 'desc'], [
        'first_name', 'asc'], ['query_count']]
    assert page == 2
    assert results_per_page == 10


def test_build_query():
    assert server.build_query({}) == Query().noop()
    assert server.build_query({'country': 'China', 'sex': 'Male', 'active': True, 'rating': 'gte:8'}) == (
        Query().noop() & (Query().country == 'China') & (Query().sex == 'Male') & (Query().active == 1.0) & (Query().rating >= 8.0))
    assert server.build_query({'country': 'China', 'sex': 'Male', 'active': True, 'rating': 'lt:5', 'primary_skills': 'all:a,b'}) == (
        Query().noop() & (Query().country == 'China') & (Query().sex == 'Male') & (Query().active == 1.0) & (Query().rating < 5) & (Query().primary_skills.test(server.skill_test_all, ('a', 'b'))))


def test_sort_results():
    results = [{'a': 'female', 'b': 'male', 'c': 7},
               {'a': 'female', 'b': 'amale', 'c': 5}]
    server.sort_results(results, [['b', 'asc'], ['c', 'desc']])
    assert results == [{'a': 'female', 'b': 'amale', 'c': 5}, {
        'a': 'female', 'b': 'male', 'c': 7}]
