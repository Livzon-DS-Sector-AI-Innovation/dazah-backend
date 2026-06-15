#!/usr/bin/env python3
"""
PDF解析器 - 从CDE补充资料通知函中提取信息
"""

import re
import json
from typing import List, Dict, Optional

try:
    import pdfplumber
    PDFPLUMBER_AVAILABLE = True
except ImportError:
    PDFPLUMBER_AVAILABLE = False

class PDFParser:
    def __init__(self, pdf_path):
        self.pdf_path = pdf_path
        self.text = ""
        self.questions = []
        self.metadata = {}
    
    def extract_text(self):
        """提取PDF文本"""
        # 优先使用pdfplumber
        if PDFPLUMBER_AVAILABLE:
            try:
                with pdfplumber.open(self.pdf_path) as pdf:
                    for page in pdf.pages:
                        self.text += page.extract_text() + "\n"
                return self.text
            except Exception as e:
                print(f"pdfplumber error: {e}")
        
        # 回退到PyPDF2
        try:
            import PyPDF2
            with open(self.pdf_path, 'rb') as f:
                pdf_reader = PyPDF2.PdfReader(f)
                for page in pdf_reader.pages:
                    self.text += page.extract_text() + "\n"
        except Exception as e:
            print(f"PyPDF2 error: {e}")
        
        return self.text
    
    def extract_metadata(self):
        """提取药品元数据"""
        text = self.text or self.extract_text()
        
        # 提取药品名称
        drug_patterns = [
            r'药品名称[：:]\s*([^\n]+)',
            r'产品名称[：:]\s*([^\n]+)',
            r'品种名称[：:]\s*([^\n]+)',
            r'原料药[：:]\s*([^\n]+)',
        ]
        for pattern in drug_patterns:
            match = re.search(pattern, text)
            if match:
                self.metadata['drug_name'] = match.group(1).strip()
                break
        
        # 提取受理号
        acceptance_patterns = [
            r'受理号[：:]\s*([A-Z]{2,4}\d{7,10})',
            r'受理编号[：:]\s*([A-Z]{2,4}\d{7,10})',
            r'CYHS\d+',
            r'CXHS\d+',
        ]
        for pattern in acceptance_patterns:
            match = re.search(pattern, text)
            if match:
                self.metadata['acceptance_no'] = match.group(0).strip()
                break
        
        # 提取登记号
        registration_patterns = [
            r'登记号[：:]\s*(Y\d{10,12})',
            r'原辅包登记号[：:]\s*(Y\d{10,12})',
            r'Y\d{10,12}',
        ]
        for pattern in registration_patterns:
            match = re.search(pattern, text)
            if match:
                self.metadata['registration_no'] = match.group(0).strip()
                break
        
        # 提取申请人
        company_patterns = [
            r'申请人[：:]\s*([^\n]+)',
            r'申请单位[：:]\s*([^\n]+)',
            r'企业名称[：:]\s*([^\n]+)',
            r'单位名称[：:]\s*([^\n]+)',
        ]
        for pattern in company_patterns:
            match = re.search(pattern, text)
            if match:
                self.metadata['company'] = match.group(1).strip()
                break
        
        return self.metadata
    
    def extract_questions(self):
        """提取所有问题"""
        text = self.text or self.extract_text()
        
        if not text:
            return []
        
        questions = []
        
        # 更灵活的匹配 - 允许跨行
        # 一级标题: 数字+顿号，标题可能在下一行或同行
        level1_pattern = r'(?:^|\n)\s*(\d+)[、]\s*\n?([^\n]*(?:\n(?![\d一二三四五六七八九十]+[、])[^\n]*)*)'
        level1_matches = list(re.finditer(level1_pattern, text, re.MULTILINE))
        
        # 如果没找到阿拉伯数字格式，尝试中文数字格式
        if not level1_matches:
            level1_pattern = r'([一二三四五六七八九十]+)[、\.\s]+([^一二三四五六七八九十（(]+?)(?=(?:[一二三四五六七八九十]+)[、\.\s]|\Z)'
            level1_matches = list(re.finditer(level1_pattern, text))
        
        for i, l1_match in enumerate(level1_matches):
            l1_num = l1_match.group(1)
            l1_title = l1_match.group(2).strip().replace('\n', ' ')
            l1_start = l1_match.start()
            l1_end = level1_matches[i+1].start() if i+1 < len(level1_matches) else len(text)
            l1_text = text[l1_start:l1_end]
            
            # 在此一级标题下找二级标题（支持（1）（2）格式，允许跨行）
            level2_pattern = r'[（\(](\d+)[）\)]\s*\n?([^\n]*(?:\n(?![（\(]\d+[）\)])[^\n]*)*)'
            level2_matches = list(re.finditer(level2_pattern, l1_text, re.MULTILINE))
            
            # 如果没找到，尝试中文数字格式
            if not level2_matches:
                level2_pattern = r'[（\(]([一二三四五六七八九十]+)[）\)]([^（(]+?)(?=(?:[（\(](?:[一二三四五六七八九十]+)[）\)])|$)'
                level2_matches = list(re.finditer(level2_pattern, l1_text))
            
            if level2_matches:
                for j, l2_match in enumerate(level2_matches):
                    l2_num = l2_match.group(1)
                    l2_title = l2_match.group(2).strip().replace('\n', ' ')
                    l2_start = l2_match.start()
                    l2_end = level2_matches[j+1].start() if j+1 < len(level2_matches) else len(l1_text)
                    l2_text = l1_text[l2_start:l2_end]
                    
                    # 找三级标题（① ② 等，允许跨行）
                    level3_pattern = r'([①②③④⑤⑥⑦⑧⑨⑩])[、\.\s]*\n?([^\n]*(?:\n(?![①②③④⑤⑥⑦⑧⑨⑩])[\n]?[^\n]*)*)'
                    level3_matches = list(re.finditer(level3_pattern, l2_text, re.MULTILINE))
                    
                    # 如果没找到圆圈数字，尝试阿拉伯数字格式
                    if not level3_matches:
                        level3_pattern = r'(\d+)[\.\s]+([^\n]+?)(?=(?:\d+[\.\s])|\Z)'
                        level3_matches = list(re.finditer(level3_pattern, l2_text))
                    
                    if level3_matches:
                        for k, l3_match in enumerate(level3_matches):
                            l3_num = l3_match.group(1)
                            l3_title = l3_match.group(2).strip().replace('\n', ' ')
                            
                            questions.append({
                                'level': 3,
                                'l1_num': l1_num,
                                'l2_num': l2_num,
                                'l3_num': l3_num,
                                'title': l3_title,
                                'full_text': f"{l1_num}、{l1_title} - （{l2_num}）{l2_title} - {l3_num} {l3_title}"
                            })
                    else:
                        # 没有三级标题，直接用二级
                        questions.append({
                            'level': 2,
                            'l1_num': l1_num,
                            'l2_num': l2_num,
                            'title': l2_title,
                            'full_text': f"{l1_num}、{l1_title} - （{l2_num}）{l2_title}"
                        })
            else:
                # 没有二级标题，直接用一级
                questions.append({
                    'level': 1,
                    'l1_num': l1_num,
                    'title': l1_title,
                    'full_text': f"{l1_num}、{l1_title}"
                })
        
        self.questions = questions
        return questions
    
    def get_numbered_questions(self):
        """获取带编号的问题列表"""
        if not self.questions:
            self.extract_questions()
        
        numbered = []
        counter = 1
        
        for q in self.questions:
            if q['level'] == 1:
                numbered.append({
                    'number': f"{counter}、",
                    'title': q['title'],
                    'level': 1,
                    'original': q
                })
                counter += 1
            elif q['level'] == 2:
                numbered.append({
                    'number': f"（{q['l2_num']}）",
                    'title': q['title'],
                    'level': 2,
                    'original': q
                })
            elif q['level'] == 3:
                l3_display = q['l3_num'] if '①' <= q['l3_num'] <= '⑩' else f"{q['l3_num']}."
                numbered.append({
                    'number': l3_display,
                    'title': q['title'],
                    'level': 3,
                    'original': q
                })
        
        return numbered
    
    def parse(self):
        """完整解析"""
        self.extract_text()
        self.extract_metadata()
        self.extract_questions()
        
        return {
            'metadata': self.metadata,
            'questions': self.questions,
            'question_count': len(self.questions)
        }


def parse_cde_notice(pdf_path):
    """便捷函数：解析CDE通知函"""
    parser = PDFParser(pdf_path)
    return parser.parse()


if __name__ == '__main__':
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python3 pdf_parser.py <cde_notice_pdf_path>")
        sys.exit(1)
    
    pdf_path = sys.argv[1]
    result = parse_cde_notice(pdf_path)
    
    print(json.dumps(result, indent=2, ensure_ascii=False))
