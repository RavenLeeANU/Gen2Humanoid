#!/usr/bin/env bash
set -e

############################
# Config
############################

# Choose motion model: "standard" or "lite"
T2M_VARIANT=${T2M_VARIANT:-standard}

# Whether to download optional Text2MotionPrompter (true / false)
DOWNLOAD_PROMPTER=${DOWNLOAD_PROMPTER:-false}

# Base checkpoint directory
CKPTS_DIR="ckpts"

############################
# Helpers
############################

echo_info() {
    echo "[INFO] $1"
}

echo_error() {
    echo "[ERROR] $1" >&2
}

require_cmd() {
    command -v "$1" >/dev/null 2>&1 || {
        echo_error "Required command not found: $1"
        exit 1
    }
}

############################
# Checks
############################

require_cmd huggingface-cli

mkdir -p "${CKPTS_DIR}"

############################
# 1. Download T2M Model
############################

echo_info "Downloading Motion Generation Model (${T2M_VARIANT})..."

case "${T2M_VARIANT}" in
    standard)
        huggingface-cli download \
            tencent/HY-Motion-1.0 \
            --include "HY-Motion-1.0/*" \
            --local-dir "${CKPTS_DIR}/tencent"
        ;;
    lite)
        huggingface-cli download \
            tencent/HY-Motion-1.0 \
            --include "HY-Motion-1.0-Lite/*" \
            --local-dir "${CKPTS_DIR}/tencent"
        ;;
    *)
        echo_error "Unknown T2M_VARIANT: ${T2M_VARIANT}"
        echo_error "Use 'standard' or 'lite'"
        exit 1
        ;;
esac

############################
# 2. Download Text Encoders
############################

echo_info "Downloading CLIP text encoder..."
huggingface-cli download \
    openai/clip-vit-large-patch14 \
    --local-dir "${CKPTS_DIR}/clip-vit-large-patch14"

echo_info "Downloading Qwen text encoder..."
huggingface-cli download \
    Qwen/Qwen3-8B \
    --local-dir "${CKPTS_DIR}/Qwen3-8B"

############################
# 3. Optional: Prompt Rewriter
############################

if [ "${DOWNLOAD_PROMPTER}" = "true" ]; then
    echo_info "Downloading Text2MotionPrompter..."
    huggingface-cli download \
        Text2MotionPrompter/Text2MotionPrompter \
        --local-dir "${CKPTS_DIR}/Text2MotionPrompter"
else
    echo_info "Skipping Text2MotionPrompter (optional)"
fi

############################
# Done
############################

echo_info "All downloads completed successfully."
echo_info "If using local models, remember to set:"
echo_info "  export USE_HF_MODELS=0"
