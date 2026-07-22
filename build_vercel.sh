#!/bin/bash
# Move a pasta web_ui diretamente para dist (pasta que a Vercel exige no preset Vite)
# Isso evita copiar centenas de megabytes e terminar em timeout.
mv web_ui dist
