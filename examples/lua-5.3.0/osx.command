cd "$(dirname $0)"

# Remove previous download
rm -rf src

# Download lua distribution
curl -L http://www.lua.org/ftp/lua-5.3.0.tar.gz | tar zx

# Rename downloaded folder to src
mv lua-5.3.0/src src
rm -rf lua-5.3.0

# Generate Lua project
cd ../../
python yap.py --source examples/lua-5.3.0/ --output examples/projects/lua.mac --name lua --platform MacOS