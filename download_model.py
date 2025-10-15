#!/usr/bin/env python3
from rembg import new_session

# Download the u2net model for faster loading and lower RAM usage
session = new_session('u2net')
print("Model downloaded successfully")
