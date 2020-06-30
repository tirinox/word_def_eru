#!/bin/sh
git pull && ./build && ./run && docker ps | grep word-def