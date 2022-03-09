#!/usr/bin/env python3
import base64
import json
import os
from datetime import datetime

from graphqlclient import GraphQLClient

client = GraphQLClient("https://asp.arubanetworks.com/graphql/")

query = """
query FileIndexList($after: String, $first: Int, $filterBy: FileIndexFilterByInput, $orderBy: [FileIndexOrderBy!]) {
    entities: fileIndexes(after: $after, first: $first, filterBy: $filterBy, orderBy: $orderBy) {
        edges { node { fileName checksumMd5 } }
        totalCount
    }
}
"""


def get_files():
    records = -1
    step = 100
    filter_by = {
        "active": True,
        "visible": True,
        "releaseDate_lte": datetime.now().isoformat() + "Z",
        "fileTypes": ["SOFTWARE"],
        "products": ["Aruba Access Points"],
        "fileContents": ["Software"],
        "softwareReleaseTypes": ["Standard"],
    }
    while True:
        variables = {
            "after": base64.b64encode(b"arrayconnection:%d" % records).decode(),
            "first": step,
            "orderBy": ["RELEVANCE", "RELEASEDATE_DESC"],
            "filterBy": filter_by,
        }
        result = json.loads(client.execute(query, variables))
        entities = result["data"]["entities"]
        total_count = entities["totalCount"]
        records += step
        for edge in entities["edges"]:
            yield edge["node"]
        if records >= total_count:
            break
        print("Progress: %3.2f%%" % ((records / total_count) * 100))
    print("Progress: 100.00%")


def main():
    input_file = "firmware.txt"
    with open(input_file, "w") as fp:
        fp.write("#!aria2c -i\n")
        for name in get_files():
            lines = [
                "https://d2vxf1j0rhr3p0.cloudfront.net/fwfiles/%(fileName)s" % name,
                "continue=true",
                "remote-time=true",
                "split=32",
                "max-tries=0",
                "max-connection-per-server=16",
                "min-split-size=2M",
                "checksum=md5=%(checksumMd5)s" % name,
                "out=aruba-firmware/%(fileName)s" % name,
            ]
            fp.write("\n\t".join(lines))
            fp.write("\n")
            fp.flush()
    os.chmod(input_file, 0o755)


if __name__ == "__main__":
    main()
