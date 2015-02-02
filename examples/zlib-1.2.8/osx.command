cd "$(dirname $0)"

# Download source distribution
curl -L http://zlib.net/zlib-1.2.8.tar.gz | tar zx

# Rename
mv zlib-1.2.8 src

# Generate project
cd ../../
python yap.py --source examples/zlib-1.2.8/ --output examples/projects/zlib.mac --name zlib --platform MacOS