#!/bin/bash

if [ $# -eq 0 ]; then
    echo "location not provided for the providers file"
    exit 1
fi

echo "providers file: $1"

echo "building docker image"
docker build -t up-image .
 
container_id=`docker run --rm -d -p 5000:5000 --mount type=bind,src=$1,dst=$1 -e PROVIDERS_FILEPATH=$1 up-image`
echo "Launched API container on http://localhost:5000 with container id: $container_id"
