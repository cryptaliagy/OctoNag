import requests
from configuration import repository_generator
from configuration import with_token
from configuration import github_graphql as url


def get_base_query_from_file(file):
    with open(file, 'r') as f:
        data = f.read()
    
    return data


def build_query(repositories=None, base_query=get_base_query_from_file('conf/base_query.gql')):
    query = "{"
    for owner, repository in repository_generator(repositories):
        query += base_query.format(org=owner, repo=repository)
    
    query += "}"
    return query


@with_token(service='Github')
def run_query(query, _token):
    headers = {'Authorization': f'Bearer {_token}'}
    result = requests.post(url, json={'query': query}, headers=headers)
    if result.status_code == 200:
        return result.json()
    else:
        raise Exception(f'Query failed with resulting code {result.status_code}')