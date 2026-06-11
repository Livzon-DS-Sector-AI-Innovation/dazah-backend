"""ICH Q3C/Q3D 杂质识别服务 - 完整版"""

import json
import re
import tempfile
from pathlib import Path
from typing import Any

try:
    from docx import Document
except ImportError:
    Document = None


# 数据目录
DATA_DIR = Path(__file__).parent / "data"


def load_q3d_elements() -> dict:
    """加载 Q3D 元素数据库"""
    q3d_path = DATA_DIR / "q3d_elements.json"
    if q3d_path.exists():
        with open(q3d_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def load_q3c_solvents() -> dict:
    """加载 Q3C 溶剂数据库"""
    q3c_path = DATA_DIR / "ich-q3c-full.json"
    if q3c_path.exists():
        with open(q3c_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def load_solvent_synonyms() -> dict:
    """加载溶剂同义词数据库"""
    syn_path = DATA_DIR / "solvent-synonyms.json"
    if syn_path.exists():
        with open(syn_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


# 加载数据
Q3D_DATA = load_q3d_elements()
Q3C_DATA = load_q3c_solvents()
SOLVENT_SYNONYMS = load_solvent_synonyms()


def extract_text_from_docx(file_content: bytes) -> str:
    """从 DOCX 文件提取文本"""
    if Document is None:
        raise ImportError("python-docx not installed")
    
    with tempfile.NamedTemporaryFile(suffix=".docx", delete=False) as tmp:
        tmp.write(file_content)
        tmp_path = tmp.name
    
    try:
        doc = Document(tmp_path)
        paragraphs = [p.text.strip() for p in doc.paragraphs if p.text.strip()]
        return "\n".join(paragraphs)
    finally:
        Path(tmp_path).unlink(missing_ok=True)


def parse_process_steps(text: str) -> list[dict]:
    """解析工艺步骤
    
    支持的格式：
    - 步骤1: ...
    - Step 1: ...
    - 1. ...
    - (1) ...
    """
    steps = []
    
    # 尝试多种步骤格式
    patterns = [
        r'(?:步骤|Step)\s*(\d+)[：:]\s*(.+?)(?=(?:步骤|Step)\s*\d+[：:]|$)',
        r'(\d+)[.、]\s*(.+?)(?=\d+[.、]|$)',
        r'\((\d+)\)\s*(.+?)(?=\(\d+\)|$)',
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, text, re.DOTALL | re.IGNORECASE)
        if matches:
            for step_num, step_content in matches:
                steps.append({
                    "step_number": int(step_num),
                    "content": step_content.strip(),
                })
            break
    
    # 如果没有匹配到步骤格式，将整个文本作为一个步骤
    if not steps:
        steps.append({
            "step_number": 1,
            "content": text,
        })
    
    return steps


def remove_concentration_prefix(solvent_name: str) -> str:
    """去除浓度前缀
    
    例如：
    - 95%乙醇 → 乙醇
    - 无水乙醇 → 乙醇
    - Absolute ethanol → ethanol
    """
    # 去除百分比前缀
    solvent_name = re.sub(r'^\d+%?\s*', '', solvent_name)
    
    # 去除浓度描述
    prefixes = ['无水', '绝对', 'Absolute', 'Anhydrous', '干燥']
    for prefix in prefixes:
        if solvent_name.startswith(prefix):
            solvent_name = solvent_name[len(prefix):].strip()
    
    return solvent_name.strip()


def get_element_data(symbol: str) -> dict:
    """获取元素数据"""
    for class_name, class_data in Q3D_DATA.get("classes", {}).items():
        elements = class_data.get("elements", {})
        if symbol in elements:
            return {"class": class_name, **elements[symbol]}
    return {}


def get_all_mandatory_elements() -> dict:
    """获取所有必须评估的元素（Class 1, 2A, 3）"""
    mandatory = {}
    for class_name, class_data in Q3D_DATA.get("classes", {}).items():
        if class_name in ("Class 1", "Class 2A", "Class 3"):
            for symbol, data in class_data.get("elements", {}).items():
                if class_name in ("Class 1", "Class 2A"):
                    oral_assess = parenteral_assess = inhalation_assess = cutaneous_assess = True
                else:  # Class 3
                    oral_assess = False
                    parenteral_assess = data.get("parenteral_assess", True)
                    inhalation_assess = data.get("inhalation_assess", True)
                    cutaneous_assess = data.get("cutaneous_assess", False)
                
                mandatory[symbol] = {
                    "source": "起始物料、辅料、工艺用水或设备中的潜在杂质",
                    "intentionally_added": False,
                    "assessment_required": True,
                    "q3d_class": class_name,
                    "oral_pde": data.get("oral_pde"),
                    "parenteral_pde": data.get("parenteral_pde"),
                    "inhalation_pde": data.get("inhalation_pde"),
                    "cutaneous_pde": data.get("cutaneous_pde"),
                    "ctcl": data.get("ctcl"),
                    "oral_assess": oral_assess,
                    "parenteral_assess": parenteral_assess,
                    "inhalation_assess": inhalation_assess,
                    "cutaneous_assess": cutaneous_assess,
                    "notes": data.get("notes", ""),
                }
    return mandatory


def build_solvent_index() -> dict:
    """构建溶剂搜索索引"""
    index = {}
    
    classes_data = Q3C_DATA.get("classes", {})
    
    # 添加 ICH 分类的溶剂
    for class_name in ["class1", "class2", "class3"]:
        class_solvents = classes_data.get(class_name, {})
        if isinstance(class_solvents, dict):
            solvent_list = class_solvents.get("solvents", [])
        else:
            solvent_list = class_solvents
        
        for solvent in solvent_list:
            if isinstance(solvent, str):
                canonical = solvent.lower().strip()
                index[canonical] = {
                    "canonical": solvent,
                    "class": "Class 3" if class_name == "class3" else class_name.replace("class", "Class "),
                    "pde": None,
                    "limit": "5000",
                    "aliases": [canonical]
                }
            else:
                canonical = solvent["name"].lower().strip()
                class_display = "Class 1" if class_name == "class1" else "Class 2"
                index[canonical] = {
                    "canonical": solvent["name"],
                    "class": class_display,
                    "pde": solvent.get("pde_mg_day") or solvent.get("pde"),
                    "limit": solvent.get("ppm") or solvent.get("limit"),
                    "aliases": [canonical]
                }
    
    # 添加同义词
    for canonical, alias_list in SOLVENT_SYNONYMS.items():
        canonical_lower = canonical.lower()
        
        if canonical_lower in index:
            for alias in alias_list:
                alias_lower = alias.lower()
                index[canonical_lower]["aliases"].append(alias_lower)
                if alias_lower not in index:
                    index[alias_lower] = index[canonical_lower]
    
    return index


# 元素关键词映射
ELEMENT_KEYWORDS = {
    "钯": "Pd", "pd": "Pd", "palladium": "Pd",
    "铂": "Pt", "pt": "Pt", "platinum": "Pt",
    "铑": "Rh", "rh": "Rh", "rhodium": "Rh",
    "钌": "Ru", "ru": "Ru", "ruthenium": "Ru",
    "铱": "Ir", "ir": "Ir", "iridium": "Ir",
    "锇": "Os", "os": "Os", "osmium": "Os",
    "金": "Au", "au": "Au", "gold": "Au",
    "银": "Ag", "ag": "Ag", "silver": "Ag",
    "镍": "Ni", "ni": "Ni", "nickel": "Ni",
    "钴": "Co", "co": "Co", "cobalt": "Co",
    "钒": "V", "v": "V", "vanadium": "V",
    "钨": "W", "w": "W", "tungsten": "W",
    "硒": "Se", "se": "Se", "selenium": "Se",
    "镉": "Cd", "cd": "Cd", "cadmium": "Cd",
    "铅": "Pb", "pb": "Pb", "lead": "Pb",
    "砷": "As", "as": "As", "arsenic": "As",
    "汞": "Hg", "hg": "Hg", "mercury": "Hg",
    "铊": "Tl", "tl": "Tl", "thallium": "Tl",
    "钡": "Ba", "ba": "Ba", "barium": "Ba",
    "铬": "Cr", "cr": "Cr", "chromium": "Cr",
    "铜": "Cu", "cu": "Cu", "copper": "Cu",
    "锂": "Li", "li": "Li", "lithium": "Li",
    "锰": "Mn", "mn": "Mn", "manganese": "Mn",
    "钼": "Mo", "mo": "Mo", "molybdenum": "Mo",
    "锑": "Sb", "sb": "Sb", "antimony": "Sb",
    "锡": "Sn", "sn": "Sn", "tin": "Sn",
    "锌": "Zn", "zn": "Zn", "zinc": "Zn",
    "铝": "Al", "al": "Al", "aluminum": "Al",
    "铁": "Fe", "fe": "Fe", "iron": "Fe",
    "镁": "Mg", "mg": "Mg", "magnesium": "Mg",
    "钙": "Ca", "ca": "Ca", "calcium": "Ca",
    "钾": "K", "k": "K", "potassium": "K",
    "钠": "Na", "na": "Na", "sodium": "Na",
}


def identify_elements_from_text(text: str) -> list[dict]:
    """从文本识别元素"""
    elements_found = {}
    text_lower = text.lower()
    
    # 获取所有必须评估的元素
    mandatory = get_all_mandatory_elements()
    
    # 首先添加所有必须评估的元素
    for symbol, data in mandatory.items():
        elements_found[symbol] = data.copy()
    
    # 从文本中查找元素
    for keyword, symbol in ELEMENT_KEYWORDS.items():
        if keyword.lower() in text_lower:
            if symbol in elements_found:
                elements_found[symbol]["found_in_text"] = True
            else:
                elem_data = get_element_data(symbol)
                if elem_data:
                    elements_found[symbol] = {
                        "source": f"在工艺文本中检测到（{keyword}）",
                        "intentionally_added": True,
                        "assessment_required": True,
                        "q3d_class": elem_data.get("class"),
                        "oral_pde": elem_data.get("oral_pde"),
                        "parenteral_pde": elem_data.get("parenteral_pde"),
                        "inhalation_pde": elem_data.get("inhalation_pde"),
                        "cutaneous_pde": elem_data.get("cutaneous_pde"),
                        "ctcl": elem_data.get("ctcl"),
                        "oral_assess": True,
                        "parenteral_assess": True,
                        "inhalation_assess": True,
                        "cutaneous_assess": True,
                        "notes": elem_data.get("notes", ""),
                        "found_in_text": True,
                    }
    
    return list(elements_found.values())


def identify_solvents_from_text(text: str) -> list[dict]:
    """从文本识别溶剂（支持浓度前缀）"""
    solvents_found = {}
    text_lower = text.lower()
    solvent_index = build_solvent_index()
    
    # 常见溶剂关键词映射
    solvent_keywords = {
        "甲醇": "methanol", "meoh": "methanol", "methanol": "methanol",
        "乙醇": "ethanol", "etoh": "ethanol", "ethanol": "ethanol", "酒精": "ethanol",
        "丙酮": "acetone", "acetone": "acetone",
        "乙腈": "acetonitrile", "acetonitrile": "acetonitrile",
        "二氯甲烷": "dichloromethane", "dichloromethane": "dichloromethane", "dcm": "dichloromethane",
        "氯仿": "chloroform", "chloroform": "chloroform",
        "四氢呋喃": "tetrahydrofuran", "tetrahydrofuran": "tetrahydrofuran", "thf": "tetrahydrofuran",
        "甲苯": "toluene", "toluene": "toluene",
        "二甲苯": "xylene", "xylene": "xylene",
        "乙酸乙酯": "ethyl acetate", "ethyl acetate": "ethyl acetate",
        "正己烷": "hexane", "hexane": "hexane",
        "庚烷": "heptane", "heptane": "heptane",
        "戊烷": "pentane", "pentane": "pentane",
        "环己烷": "cyclohexane", "cyclohexane": "cyclohexane",
        "苯": "benzene", "benzene": "benzene",
        "吡啶": "pyridine", "pyridine": "pyridine",
        "dmf": "n,n-dimethylformamide", "n,n-二甲基甲酰胺": "n,n-dimethylformamide",
        "dmso": "dimethyl sulfoxide", "二甲基亚砜": "dimethyl sulfoxide",
        "水": "water", "water": "water",
        "乙酸": "acetic acid", "acetic acid": "acetic acid",
        "异丙醇": "isopropanol", "isopropanol": "isopropanol", "ipa": "isopropanol",
        "正丁醇": "butanol", "butanol": "butanol",
        "乙醚": "diethyl ether", "diethyl ether": "diethyl ether",
        "石油醚": "petroleum ether", "petroleum ether": "petroleum ether",
        "丙醇": "propanol", "propanol": "propanol",
        "异丁醇": "isobutanol", "isobutanol": "isobutanol",
        "叔丁醇": "tert-butanol", "tert-butanol": "tert-butanol",
        "二氧六环": "1,4-dioxane", "1,4-dioxane": "1,4-dioxane", "dioxane": "1,4-dioxane",
        "nmp": "n-methylpyrrolidone", "n-甲基吡咯烷酮": "n-methylpyrrolidone",
    }
    
    # 从文本中查找溶剂（支持浓度前缀）
    for keyword, solvent_name in solvent_keywords.items():
        # 支持带浓度前缀的匹配
        pattern = rf'(?:\d+%|无水|绝对)?\s*{re.escape(keyword)}'
        if re.search(pattern, text_lower):
            if solvent_name in solvent_index:
                solvent_data = solvent_index[solvent_name]
                solvents_found[solvent_data["canonical"]] = {
                    "name_en": solvent_data["canonical"],
                    "name_cn": get_solvent_cn(solvent_data["canonical"]),
                    "class": solvent_data["class"],
                    "limit_ppm": solvent_data.get("limit"),
                    "pde_mg_day": solvent_data.get("pde"),
                    "found_in_text": True,
                }
    
    # 也检查同义词索引
    for name, data in solvent_index.items():
        # 支持带浓度前缀的匹配
        pattern = rf'(?:\d+%|无水|绝对)?\s*{re.escape(name)}'
        if re.search(pattern, text_lower) and data["canonical"] not in solvents_found:
            solvents_found[data["canonical"]] = {
                "name_en": data["canonical"],
                "name_cn": get_solvent_cn(data["canonical"]),
                "class": data["class"],
                "limit_ppm": data.get("limit"),
                "pde_mg_day": data.get("pde"),
                "found_in_text": True,
            }
    
    return list(solvents_found.values())


def get_solvent_cn(name_en: str) -> str:
    """获取溶剂中文名"""
    cn_map = {
        "Benzene": "苯", "Carbon Tetrachloride": "四氯化碳",
        "1,2-Dichloroethane": "1,2-二氯乙烷", "1,1-Dichloroethane": "1,1-二氯乙烷",
        "1,1,1-Trichloroethane": "1,1,1-三氯乙烷", "1,2-Dichloroethylene": "1,2-二氯乙烯",
        "Acetonitrile": "乙腈", "Chlorobenzene": "氯苯", "Chloroform": "氯仿",
        "Cyclohexane": "环己烷", "Dichloromethane": "二氯甲烷",
        "1,2-Dichloroethene": "1,2-二氯乙烯", "N,N-Dimethylformamide": "N,N-二甲基甲酰胺",
        "1,4-Dioxane": "1,4-二氧六环", "Ethylene Glycol": "乙二醇",
        "Formamide": "甲酰胺", "Hexane": "正己烷", "Methanol": "甲醇",
        "2-Ethoxyethanol": "2-乙氧基乙醇", "Ethoxydiglycol": "乙氧基二甘醇",
        "Cyclopentyl Methyl Ether": "环戊基甲基醚",
        "N,N-Dimethylacetamide": "N,N-二甲基乙酰胺", "Dimethyl Sulfoxide": "二甲基亚砜",
        "Ethyl Acetate": "乙酸乙酯", "Ethyl Ether": "乙醚", "Heptane": "庚烷",
        "Isobutanol": "异丁醇", "Isopropanol": "异丙醇", "Methyl Acetate": "乙酸甲酯",
        "Methyl Ethyl Ketone": "甲基乙基酮", "Methyl Isobutyl Ketone": "甲基异丁基酮",
        "2-Methyl-1-Propanol": "2-甲基-1-丙醇", "Nitromethane": "硝基甲烷",
        "Pentane": "戊烷", "1-Pentanol": "1-戊醇", "Propanol": "丙醇",
        "Pyridine": "吡啶", "Sulfolane": "环丁砜", "Tetrahydrofuran": "四氢呋喃",
        "Toluene": "甲苯", "1,1,2-Trichloroethylene": "1,1,2-三氯乙烯",
        "Xylene": "二甲苯", "Cumene": "异丙苯", "Dimethylacetamide": "二甲基乙酰胺",
        "Diethylene Glycol": "二乙二醇", "Diisopropyl Ether": "二异丙醚",
        "Ethylbenzene": "乙苯", "Ethylene Glycol Monobutyl Ether": "乙二醇单丁醚",
        "Hexanes": "己烷", "Isobutyl Acetate": "乙酸异丁酯",
        "Isopentyl Acetate": "乙酸异戊酯", "Methylethylcyclohexane": "甲基乙基环己烷",
        "Methylcyclohexane": "甲基环己烷", "Mineral Spirits": "矿物油精",
        "N-Propyl Acetate": "乙酸正丙酯", "n-Butanol": "正丁醇",
        "n-Butyl Acetate": "乙酸正丁酯", "n-Heptane": "正庚烷",
        "n-Hexane": "正己烷", "n-Pentane": "正戊烷", "Petroleum Benzine": "石油醚",
        "Petroleum Ether": "石油醚", "Propyl Acetate": "乙酸丙酯",
        "Stoddard Solvent": "斯托达德溶剂", "tert-Butanol": "叔丁醇",
        "tert-Butyl Acetate": "乙酸叔丁酯", "Tetrahydronaphthalene": "四氢化萘",
        "Water": "水", "Acetic Acid": "乙酸", "Ethanol": "乙醇",
        "2-Propanol": "异丙醇", "1-Butanol": "正丁醇", "2-Butanol": "仲丁醇",
        "1-Propanol": "丙醇", "2-Methoxyethanol": "2-甲氧基乙醇",
        "Methyl Isopropyl Ketone": "甲基异丙基酮",
    }
    return cn_map.get(name_en, name_en)


def assess_compliance(elements: list[dict], route: str = "oral") -> list[dict]:
    """根据给药途径评估合规性"""
    for elem in elements:
        route_assess_key = f"{route}_assess"
        if route == "oral":
            elem["needs_assessment"] = elem.get("oral_assess", False)
            elem["pde_for_route"] = elem.get("oral_pde")
        elif route == "parenteral":
            elem["needs_assessment"] = elem.get("parenteral_assess", True)
            elem["pde_for_route"] = elem.get("parenteral_pde")
        elif route == "inhalation":
            elem["needs_assessment"] = elem.get("inhalation_assess", True)
            elem["pde_for_route"] = elem.get("inhalation_pde")
        elif route == "cutaneous":
            elem["needs_assessment"] = elem.get("cutaneous_assess", False)
            elem["pde_for_route"] = elem.get("cutaneous_pde")
            # 检查 CTCL
            if elem.get("ctcl"):
                elem["ctcl_applicable"] = True
        
        # 控制阈值 = 30% PDE
        pde = elem.get("pde_for_route")
        if pde:
            elem["control_threshold"] = pde * 0.3
    
    return elements


def generate_q3d_report(elements: list[dict], route: str = "oral") -> str:
    """生成 ICH Q3D 合规报告"""
    report = []
    report.append("# ICH Q3D 元素杂质评估报告")
    report.append("")
    report.append(f"**给药途径**: {route}")
    report.append(f"**评估日期**: {Path().cwd()}")
    report.append("")
    
    # 统计
    needs_assess = [e for e in elements if e.get("needs_assessment")]
    class_1 = [e for e in needs_assess if e.get("q3d_class") == "Class 1"]
    class_2a = [e for e in needs_assess if e.get("q3d_class") == "Class 2A"]
    class_2b = [e for e in needs_assess if e.get("q3d_class") == "Class 2B"]
    class_3 = [e for e in needs_assess if e.get("q3d_class") == "Class 3"]
    
    report.append("## 评估摘要")
    report.append("")
    report.append(f"- 需要评估的元素总数: **{len(needs_assess)}**")
    report.append(f"- Class 1 元素: **{len(class_1)}**")
    report.append(f"- Class 2A 元素: **{len(class_2a)}**")
    report.append(f"- Class 2B 元素: **{len(class_2b)}**")
    report.append(f"- Class 3 元素: **{len(class_3)}**")
    report.append("")
    
    if needs_assess:
        report.append("## 需要评估的元素")
        report.append("")
        report.append("| 元素 | 分类 | PDE (μg/天) | 控制阈值 (μg/天) | 来源 |")
        report.append("|------|------|-------------|------------------|------|")
        
        for elem in needs_assess:
            pde = elem.get("pde_for_route", "-")
            threshold = elem.get("control_threshold", "-")
            report.append(f"| {elem['symbol']} | {elem['q3d_class']} | {pde} | {threshold} | {elem.get('source', '-')} |")
        
        report.append("")
    
    report.append("## 评估建议")
    report.append("")
    report.append("1. 对于 Class 1 和 Class 2A 元素，必须评估所有潜在来源")
    report.append("2. 控制阈值 = 30% PDE，低于此值通常无需额外控制")
    report.append("3. 如元素含量超过控制阈值，需制定控制策略")
    report.append("")
    
    report.append("## 参考文献")
    report.append("")
    report.append("- ICH Q3D(R2) 元素杂质指导原则（2022年4月）")
    
    return "\n".join(report)


def generate_q3c_report(solvents: list[dict]) -> str:
    """生成 ICH Q3C 合规报告"""
    report = []
    report.append("# ICH Q3C 溶剂残留评估报告")
    report.append("")
    
    # 统计
    class_1 = [s for s in solvents if s.get("class") == "Class 1"]
    class_2 = [s for s in solvents if s.get("class") == "Class 2"]
    class_3 = [s for s in solvents if s.get("class") == "Class 3"]
    
    report.append("## 评估摘要")
    report.append("")
    report.append(f"- 识别溶剂总数: **{len(solvents)}**")
    report.append(f"- Class 1 溶剂（避免使用）: **{len(class_1)}**")
    report.append(f"- Class 2 溶剂（限制使用）: **{len(class_2)}**")
    report.append(f"- Class 3 溶剂（低毒）: **{len(class_3)}**")
    report.append("")
    
    if class_1:
        report.append("## ⚠️ Class 1 溶剂（必须避免）")
        report.append("")
        for s in class_1:
            report.append(f"- **{s['name_cn']}** ({s['name_en']}): 限度 {s.get('limit_ppm', '-')} ppm")
        report.append("")
    
    if class_2:
        report.append("## Class 2 溶剂（限制使用）")
        report.append("")
        report.append("| 溶剂 | PDE (mg/天) | 限度 (ppm) |")
        report.append("|------|-------------|------------|")
        for s in class_2:
            report.append(f"| {s['name_cn']} | {s.get('pde_mg_day', '-')} | {s.get('limit_ppm', '-')} |")
        report.append("")
    
    if class_3:
        report.append("## Class 3 溶剂（低毒）")
        report.append("")
        report.append("Class 3 溶剂毒性低，通常按 GMP 或其他质量标准控制即可。")
        report.append("")
        for s in class_3:
            report.append(f"- {s['name_cn']} ({s['name_en']})")
        report.append("")
    
    report.append("## 评估建议")
    report.append("")
    report.append("1. Class 1 溶剂应避免使用，如必须使用需提供充分理由")
    report.append("2. Class 2 溶剂应限制使用，确保低于限度")
    report.append("3. Class 3 溶剂按 GMP 要求控制")
    report.append("")
    
    report.append("## 参考文献")
    report.append("")
    report.append("- ICH Q3C(R9) 溶剂残留指导原则（2024年1月）")
    
    return "\n".join(report)


def analyze_ich_q3d(file_content: bytes, route: str = "oral") -> dict:
    """分析 ICH Q3D 元素杂质"""
    text = extract_text_from_docx(file_content)
    steps = parse_process_steps(text)
    elements = identify_elements_from_text(text)
    
    # 合规评估
    elements = assess_compliance(elements, route)
    
    # 生成报告
    report = generate_q3d_report(elements, route)
    
    # 统计
    summary = {
        "class_1": 0, "class_2a": 0, "class_2b": 0, "class_3": 0, "other": 0,
    }
    for elem in elements:
        cls = elem.get("q3d_class", "")
        if cls == "Class 1":
            summary["class_1"] += 1
        elif cls == "Class 2A":
            summary["class_2a"] += 1
        elif cls == "Class 2B":
            summary["class_2b"] += 1
        elif cls == "Class 3":
            summary["class_3"] += 1
        elif cls == "Other":
            summary["other"] += 1
    
    return {
        "type": "Q3D",
        "text_length": len(text),
        "steps_count": len(steps),
        "route": route,
        "elements_found": elements,
        "total_elements": len(elements),
        "needs_assessment": len([e for e in elements if e.get("needs_assessment")]),
        "summary": summary,
        "report": report,
    }


def analyze_ich_q3c(file_content: bytes) -> dict:
    """分析 ICH Q3C 溶剂残留"""
    text = extract_text_from_docx(file_content)
    steps = parse_process_steps(text)
    solvents = identify_solvents_from_text(text)
    
    # 生成报告
    report = generate_q3c_report(solvents)
    
    # 统计
    summary = {
        "class_1": 0, "class_2": 0, "class_3": 0, "unknown": 0,
    }
    for solv in solvents:
        cls = solv.get("class", "")
        if cls == "Class 1":
            summary["class_1"] += 1
        elif cls == "Class 2":
            summary["class_2"] += 1
        elif cls == "Class 3":
            summary["class_3"] += 1
        else:
            summary["unknown"] += 1
    
    return {
        "type": "Q3C",
        "text_length": len(text),
        "steps_count": len(steps),
        "solvents_found": solvents,
        "total_solvents": len(solvents),
        "summary": summary,
        "report": report,
    }


# ==================== LLM 集成版本 ====================

async def analyze_ich_q3d_with_llm(file_content: bytes, route: str = "oral") -> dict:
    """使用 LLM 分析 ICH Q3D 元素杂质"""
    from app.modules.research.llm_service import extract_elements_with_llm
    
    text = extract_text_from_docx(file_content)
    steps = parse_process_steps(text)
    
    # 使用 LLM 提取元素
    llm_elements = await extract_elements_with_llm(text)
    
    # 合并 LLM 结果和关键词匹配结果
    elements = identify_elements_from_text(text)
    
    # 处理 LLM 识别的元素
    for llm_elem in llm_elements:
        symbol = llm_elem.get("symbol", "")
        if not symbol:
            continue
        
        # 查找是否已存在
        existing = next((e for e in elements if e["symbol"] == symbol), None)
        if existing:
            # 更新来源信息
            if llm_elem.get("source"):
                existing["source"] = llm_elem["source"]
            existing["intentionally_added"] = llm_elem.get("intentionally_added", False)
            existing["found_in_text"] = True
        else:
            # 添加新元素
            elem_data = get_element_data(symbol)
            if elem_data:
                elements.append({
                    "symbol": symbol,
                    "source": llm_elem.get("source", "LLM 识别"),
                    "intentionally_added": llm_elem.get("intentionally_added", False),
                    "assessment_required": True,
                    "q3d_class": elem_data.get("class"),
                    "oral_pde": elem_data.get("oral_pde"),
                    "parenteral_pde": elem_data.get("parenteral_pde"),
                    "inhalation_pde": elem_data.get("inhalation_pde"),
                    "cutaneous_pde": elem_data.get("cutaneous_pde"),
                    "ctcl": elem_data.get("ctcl"),
                    "oral_assess": True,
                    "parenteral_assess": True,
                    "inhalation_assess": True,
                    "cutaneous_assess": True,
                    "notes": elem_data.get("notes", ""),
                    "found_in_text": True,
                })
    
    # 合规评估
    elements = assess_compliance(elements, route)
    
    # 生成报告
    report = generate_q3d_report(elements, route)
    
    # 统计
    summary = {
        "class_1": 0, "class_2a": 0, "class_2b": 0, "class_3": 0, "other": 0,
    }
    for elem in elements:
        cls = elem.get("q3d_class", "")
        if cls == "Class 1":
            summary["class_1"] += 1
        elif cls == "Class 2A":
            summary["class_2a"] += 1
        elif cls == "Class 2B":
            summary["class_2b"] += 1
        elif cls == "Class 3":
            summary["class_3"] += 1
        elif cls == "Other":
            summary["other"] += 1
    
    return {
        "type": "Q3D",
        "text_length": len(text),
        "steps_count": len(steps),
        "route": route,
        "elements_found": elements,
        "total_elements": len(elements),
        "needs_assessment": len([e for e in elements if e.get("needs_assessment")]),
        "summary": summary,
        "report": report,
        "llm_used": True,
        "llm_elements_count": len(llm_elements),
    }


async def analyze_ich_q3c_with_llm(file_content: bytes) -> dict:
    """使用 LLM 分析 ICH Q3C 溶剂残留"""
    from app.modules.research.llm_service import extract_solvents_with_llm
    
    text = extract_text_from_docx(file_content)
    steps = parse_process_steps(text)
    
    # 使用 LLM 提取溶剂
    llm_solvents = await extract_solvents_with_llm(text)
    
    # 合并 LLM 结果和关键词匹配结果
    solvents = identify_solvents_from_text(text)
    solvent_index = build_solvent_index()
    
    # 处理 LLM 识别的溶剂
    for llm_solv in llm_solvents:
        name = llm_solv.get("name", "")
        if not name:
            continue
        
        # 去除浓度前缀
        name = remove_concentration_prefix(name)
        name_lower = name.lower()
        
        # 查找是否已存在
        existing = next((s for s in solvents if s["name_en"].lower() == name_lower or s["name_cn"] == name), None)
        if existing:
            # 更新用途信息
            if llm_solv.get("purpose"):
                existing["purpose"] = llm_solv["purpose"]
            existing["found_in_text"] = True
        else:
            # 尝试在索引中查找
            if name_lower in solvent_index:
                solvent_data = solvent_index[name_lower]
                solvents.append({
                    "name_en": solvent_data["canonical"],
                    "name_cn": get_solvent_cn(solvent_data["canonical"]),
                    "class": solvent_data["class"],
                    "limit_ppm": solvent_data.get("limit"),
                    "pde_mg_day": solvent_data.get("pde"),
                    "purpose": llm_solv.get("purpose", ""),
                    "found_in_text": True,
                })
    
    # 生成报告
    report = generate_q3c_report(solvents)
    
    # 统计
    summary = {
        "class_1": 0, "class_2": 0, "class_3": 0, "unknown": 0,
    }
    for solv in solvents:
        cls = solv.get("class", "")
        if cls == "Class 1":
            summary["class_1"] += 1
        elif cls == "Class 2":
            summary["class_2"] += 1
        elif cls == "Class 3":
            summary["class_3"] += 1
        else:
            summary["unknown"] += 1
    
    return {
        "type": "Q3C",
        "text_length": len(text),
        "steps_count": len(steps),
        "solvents_found": solvents,
        "total_solvents": len(solvents),
        "summary": summary,
        "report": report,
        "llm_used": True,
        "llm_solvents_count": len(llm_solvents),
    }
