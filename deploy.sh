#!/bin/bash

# 1. Definir rutas (Ajusta 'oscar' si es necesario)
SOURCE_BIN="/home/oscar/Projects/mg-photos/target/armv7-linux-androideabi/release/mg-photos"
WINDOWS_ADB_DIR="/mnt/c/Users/O1spe/Desktop/platform-tools"
ADB_EXE="$WINDOWS_ADB_DIR/adb.exe"

echo "🚀 Iniciando despliegue corregido..."

# 2. Copiar el binario a la carpeta de Windows
cp "$SOURCE_BIN" "$WINDOWS_ADB_DIR/"

# 3. Traducir la ruta para que adb.exe la entienda
WIN_PATH=$(wslpath -w "$WINDOWS_ADB_DIR/mg-photos")

# 4. Subir el binario
"$ADB_EXE" push "$WIN_PATH" /data/local/tmp/

if [ $? -eq 0 ]; then
    echo "✅ Binario subido correctamente."
    "$ADB_EXE" shell "chmod 755 /data/local/tmp/mg-photos"
    echo "✅ Permisos otorgados."
    echo "🎯 Ejecútalo con: adb shell /data/local/tmp/mg-photos"
else
    echo "❌ Error al subir el binario. Revisa la conexión ADB."
fi