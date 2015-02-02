cd "$(dirname $0)"

# Remove previous download
rm -rf src

# Download source distribution
curl -L http://curl.haxx.se/download/curl-7.40.0.tar.gz | tar zx

# Rename downloaded folder to src
mv curl-7.40.0/lib src
mv curl-7.40.0/include include

rm -rf curl-7.40.0

cp config-mac.h include/curl_config.h

# Generate project
cd ../../
python yap.py --source examples/curl-7.40.0/ --output examples/projects/curl.mac --name curl --platform MacOS