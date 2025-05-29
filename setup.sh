#!/bin/bash

echo "Installing Python dependencies..."
pip3 install -r requirements.txt

echo "Downloading Mars terrain data... (≈ 11GB)"
echo "This may take a while..."
curl -o Mars_HRSC_MOLA_BlendDEM_Global_200mp_v2.tif https://asc-pds-services.s3.us-west-2.amazonaws.com/mosaic/Mars/HRSC_MOLA_Blend/Mars_HRSC_MOLA_BlendDEM_Global_200mp_v2.tif

echo "Setup complete. You can now run the simulator with:"
echo "python3 main.py"
