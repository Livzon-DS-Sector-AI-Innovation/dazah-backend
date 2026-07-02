#!/usr/bin/env python3
"""Fix encoding issues in static_data/api.py"""

# Read the file with GBK encoding (what the content actually is)
with open('app/modules/quality/static_data/api.py', 'rb') as f:
    raw = f.read()

content = raw.decode('gbk')

# Define all the garbled patterns and their correct replacements
fixes = {
    # First line
    '忙篓隆氓聺聴': '模块',
    '猫路炉莽聰卤': '路由',
    'æ¨¡å\x9d\x97': '模块',
    'è·¯ç\x94±': '路由',
    'æ\x8f\x90ä¾\x9bä¸\x9aå\x8a¡é\x9d\x99æ\x80\x81æ\x95°æ\x8d®': '提供业务静态数据',
    'æ\x89\x80æ\x9c': '所有',
    'RESTful API': 'RESTful API',
    'æ\x8e¥å\x8f£ã\x80?': '接口',
    'å\x89\x8dç¼\x80': '前缀',
    
    # Tags and common phrases
    '盲赂職氓聤隆茅聺聶忙聙聛忙聲掳忙聧庐': '业务静态数据',
    '盲赂職氓聤隆茅聺聶忙聙聛忙聲掳忙聧庐': '业务静态数据',
    '盲赂職氓聤隆茅聺聶忙聙聛忙聲掳忙聧庐': '业务静态数据',
    '盲赂職氓聤隆茅聺聶忙聙聛忙聲掳忙聧庐': '业务静态数据',
    '盲赂職氓聤隆茅聺聶忙聙聛忙聲掳忙聧?': '业务静态数据',
    '盲赂職氓聤隆茅聺聶': '业务',
    '忙聙聛忙聲掳忙聧庐': '数据',
    
    # Chinese phrases
    '忙聤隆茅聺聶': '条件',
    '盲聙脣莽聰楼': '列表',
    '忙篓聹盲聙': '状态',
    '忙聰禄忙搂聹盲赂': '编码',
    '忙聛楼忙聹脣忙聧': '名称',
    '忙聙聡盲搂脣忙': '记录',
    '莽聰炉忙聹聹忙': '创建',
    '忙聙掳忙聧驴': '成功',
    '莽聛聹莽聰': '更新',
    '忙聰驴莽聰炉': '删除',
    '忙聧驴盲戮': '用户',
    '盲戮聰': '获取',
    '盲戮掳忙聧': '当前',
    '忙聛隆忙聧忙': '不存在',
    '忙篓隆氓聺聴': '模块',
}

for old, new in fixes.items():
    content = content.replace(old, new)

# Write back as UTF-8
with open('app/modules/quality/static_data/api.py', 'w', encoding='utf-8') as f:
    f.write(content)

print('Encoding fixed')

# Verify
with open('app/modules/quality/static_data/api.py', 'r', encoding='utf-8') as f:
    check = f.read()
    
# Try to import
import sys
sys.path.insert(0, '.')
try:
    # Just check if the file can be parsed
    compile(check, 'api.py', 'exec')
    print('Syntax OK')
except SyntaxError as e:
    print(f'Syntax error at line {e.lineno}: {e.msg}')
    print(f'Line content: {check.split(chr(10))[e.lineno-1][:100] if e.lineno else "N/A"}')