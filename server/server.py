from typing import Dict
from typing import List
from typing import Tuple
from flask import Flask, jsonify, request
import os
import json
from collections import defaultdict
from tinydb import TinyDB, Query


def skill_test_any(v: List[str], skills_to_search: Tuple[str]) -> bool:
    val = set([x.lower().strip() for x in v])
    for s in skills_to_search:
        if s.lower().strip() in val:
            return True
    return False


def skill_test_all(v: List[str], skills_to_search: Tuple[str]) -> bool:
    val = set([x.lower().strip() for x in v])
    for s in skills_to_search:
        if s.lower().strip() not in val:
            return False
    return True


def build_query(params: Dict) -> Query:
    q = Query().noop()
    for k, v in params.items():
        qu = (Query()[k] == v)
        if isinstance(v, str) and ':' in v:
            fields = v.split(":")
            if fields[0].lower() == 'gt':
                try:
                    qu = (Query()[k] > float(fields[1]))
                except:
                    qu = (Query()[k] > fields[1])
            elif fields[0].lower() == 'gte':
                try:
                    qu = (Query()[k] >= float(fields[1]))
                except:
                    qu = (Query()[k] >= fields[1])
            elif fields[0].lower() == 'lt':
                try:
                    qu = (Query()[k] < float(fields[1]))
                except:
                    qu = (Query()[k] < fields[1])
            elif fields[0].lower() == 'lte':
                try:
                    qu = (Query()[k] <= float(fields[1]))
                except:
                    qu = (Query()[k] <= fields[1])
            elif fields[0].lower() == 'any':
                if k == 'primary_skills' or k == 'secondary_skill':
                    skills_to_search = tuple(fields[1].split(','))
                    qu = Query()[k].test(skill_test_any, skills_to_search)
            elif fields[0].lower() == 'all':
                if k == 'primary_skills' or k == 'secondary_skill':
                    skills_to_search = tuple(fields[1].split(','))
                    qu = Query()[k].test(skill_test_all, skills_to_search)
        q &= qu
    return q


def process_query_params(params: Dict) -> Tuple[int, int, List]:
    for k in params:
        if params[k].lower() == 'true':
            params[k] = True
        elif params[k].lower() == 'false':
            params[k] = False

        try:
            params[k] = float(params[k])
        except:
            pass

    page = 1
    results_per_page = -1
    if 'page' in params:
        page = int(params['page'])
        params.pop('page')

    if 'results_per_page' in params:
        results_per_page = int(params['results_per_page'])
        params.pop('results_per_page')

    sort_keys = []
    if 'sort' in params:
        sort_keys = [k.split(":") for k in params['sort'].split(",")]
        params.pop('sort')

    return (page, results_per_page, sort_keys)

def sort_results(results: List, sort_keys: List[Tuple[str,str]]):
    for k in sort_keys[::-1]:
        results.sort(key=lambda x: x[k[0]],
                 reverse=True if len(k) > 1 and k[1] == 'desc' else False)


app = Flask(__name__)
db_fname = "db.json"

try:
    os.remove(db_fname)
except OSError:
    pass

db = TinyDB(db_fname)

if os.getenv("PROVIDERS_FILEPATH"):
    with open(os.getenv("PROVIDERS_FILEPATH"), "r") as f:
        data = json.load(f)
    for entry in data:
        db.insert(entry)

record_counts = defaultdict(lambda: 0)


@app.route('/providers', methods=['GET'])
def providers():
    params = request.args.to_dict()
    page, results_per_page, sort_keys = process_query_params(params)

    q = build_query(params)
    res = db.search(q)
    total_results = len(res)

    for r in res:
        record_counts[r['id']] += 1
        r['query_count'] = record_counts[r['id']]

    sort_results(res, sort_keys)

    if results_per_page == -1:
        results_per_page = len(res)
    offset = (page - 1)*results_per_page
    res = res[offset:offset+results_per_page]

    response = {"content": res, "page": page, "total_results": total_results}
    return jsonify(response)
