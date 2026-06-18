$env:PGPASSWORD='postgres'
Write-Host "测试连接..."
& 'C:\Users\admin\scoop\apps\postgresql\current\bin\psql.exe' -U postgres -h 127.0.0.1 -p 5432 -d dahzah -c 'SELECT 1;'
