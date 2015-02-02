cd "$(dirname $0)"

# Remove previous download
rm -rf src include

# Download source distribution
curl -L http://download.savannah.gnu.org/releases/freetype/freetype-2.5.5.tar.gz | tar zx

# Rename downloaded folder to src
mv freetype-2.5.5/src src
mv freetype-2.5.5/include include

rm -rf freetype-2.5.5

# Generate Lua project
cd ../../
python yap.py --source examples/freetype-2.5.5/ --output examples/projects/freetype.mac --name freetype --platform MacOS