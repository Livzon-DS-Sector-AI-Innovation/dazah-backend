$env:PGPASSWORD='postgres'
Write-Host "所有数据库..."
& 'C:\Users\admin\scoop\apps\postgresql\current\bin\psql.exe' -U postgres -h localhost -c '\l'
