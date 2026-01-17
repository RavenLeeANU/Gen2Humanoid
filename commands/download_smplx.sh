#!/usr/bin/env bash
set -e

SMPLX_DIR="ckpts/smplx"
ARCHIVE_NAME="SMPLX_v1.1.zip"

echo "[INFO] Preparing SMPL-X directory..."
mkdir -p "${SMPLX_DIR}"

echo
echo "============================================================"
echo " SMPL-X MODEL DOWNLOAD INSTRUCTIONS"
echo "============================================================"
echo
echo "1. Go to: https://smpl-x.is.tue.mpg.de/"
echo "2. Register / Login"
echo "3. Download: SMPL-X v1.1 (ZIP)"
echo "4. Place the downloaded file here:"
echo
echo "   ${SMPLX_DIR}/${ARCHIVE_NAME}"
echo
echo "============================================================"
echo

if [ ! -f "${SMPLX_DIR}/${ARCHIVE_NAME}" ]; then
    echo "[ERROR] ${ARCHIVE_NAME} not found."
    exit 1
fi

echo "[INFO] Extracting SMPL-X..."
unzip -o "${SMPLX_DIR}/${ARCHIVE_NAME}" -d "${SMPLX_DIR}"

echo "[INFO] Organizing files..."

# 常见官方结构兼容
if [ -d "${SMPLX_DIR}/models" ]; then
    echo "[INFO] models directory exists."
else
    mkdir -p "${SMPLX_DIR}/models"
    find "${SMPLX_DIR}" -name "*.npz" -exec mv {} "${SMPLX_DIR}/models/" \;
fi

echo "[INFO] SMPL-X setup completed successfully."
