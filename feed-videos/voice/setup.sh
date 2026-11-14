#!/bin/bash
# One-time setup per session: builds espeak-ng (pronunciation) and fetches the Kokoro voice model from GitHub.
set -e
Q=${QOTD_HOME:-/home/claude/qotd}; mkdir -p $Q/vendor && cd $Q/vendor
if [ ! -x espeak/bin/espeak-ng ]; then
  [ -d espeak-ng ] || git clone -q --depth 1 https://github.com/espeak-ng/espeak-ng
  cmake -S espeak-ng -B espeak-ng/build -DCMAKE_BUILD_TYPE=Release -DUSE_MBROLA=OFF -DUSE_LIBSONIC=OFF \
    -DUSE_LIBPCAUDIO=OFF -DUSE_ASYNC=OFF -DCMAKE_INSTALL_PREFIX=$Q/vendor/espeak > /dev/null
  cmake --build espeak-ng/build -j8 > /dev/null 2>&1 && cmake --install espeak-ng/build > /dev/null 2>&1
fi
[ -d kokoro-onnx ] || git clone -q --depth 1 https://github.com/thewh1teagle/kokoro-onnx
for f in kokoro-v1.0.onnx voices-v1.0.bin; do
  [ -s $f ] || curl -sSL -o $f https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/$f
done
python3 -c "import onnxruntime, numpy, PIL" && which ffmpeg > /dev/null && echo "QOTD setup OK"
