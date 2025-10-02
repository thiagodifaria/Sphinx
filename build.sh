echo "Building Sphinx executable..."

echo "Installing PyInstaller in Poetry environment..."
poetry add --group dev pyinstaller

echo "Cleaning previous builds..."
rm -rf build dist

echo "Building executable with Poetry..."
poetry run pyinstaller sphinx.spec

if [ $? -eq 0 ]; then
    echo ""
    echo "Build successful!"
    echo "Executable location: dist/sphinx or dist/sphinx.exe"
    echo ""
else
    echo ""
    echo "Build failed!"
    exit 1
fi