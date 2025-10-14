#!/usr/bin/env python3
from rembg import new_session

# Download the model during build
session = new_session('isnet-general-use')
print("Model downloaded successfully")
