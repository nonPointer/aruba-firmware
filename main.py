#!/usr/bin/env python3
import base64
import json
from datetime import datetime

from graphqlclient import GraphQLClient

client = GraphQLClient('https://asp.arubanetworks.com/graphql/')

query = '''
query FileIndexList($after: String, $first: Int, $filterBy: FileIndexFilterByInput, $orderBy: [FileIndexOrderBy!]) {
    entities: fileIndexes(after: $after, first: $first, filterBy: $filterBy, orderBy: $orderBy) {
        edges { node { fileName } }
        totalCount
    }
}
'''


def get_files():
    records = -1
    step = 100
    order_by = ["RELEVANCE", "RELEASEDATE_DESC"]
    filter_by = {
        "active": True,
        "visible": True,
        "releaseDate_lte": datetime.now().isoformat() + 'Z',
        "fileTypes": ["SOFTWARE"],
        "products": ["Aruba Access Points"],
        "fileContents": ["Software"],
        "softwareReleaseTypes": ["Standard"]
    }
    while True:
        result = json.loads(client.execute(query, variables={
            "after": base64.b64encode(b"arrayconnection:%d" % records).decode(),
            "first": step,
            "orderBy": order_by,
            "filterBy": filter_by,
        }))
        entities = result['data']['entities']
        total_count = entities['totalCount']
        records += step
        for edge in entities['edges']:
            yield edge['node']['fileName']
        if records >= total_count:
            return


def main():
    for name in get_files():
        print('https://d2vxf1j0rhr3p0.cloudfront.net/fwfiles/%s' % name)


if __name__ == '__main__':
    main()
