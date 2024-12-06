# 运行 main_gui.py
Start-Process -FilePath "python" -ArgumentList "server/main_gui.py"

# 等待 1 秒
Start-Sleep -Seconds 1

# 运行 client.py
Start-Process -FilePath "python" -ArgumentList "client/client.py"