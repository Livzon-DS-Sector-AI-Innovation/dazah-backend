"""ICH Q3C/Q3D 杂质识别服务"""

import json
import tempfile
from pathlib import Path
from typing import Any

try:
    from docx import Document
except ImportError:
    Document = None


# ICH Q3D 元素数据
Q3D_ELEMENTS_DATA = {
    "classes": {
        "Class 1": {
            "description": "人体毒性与环保关注元素",
            "elements": {
                "Cd": {"name": "镉", "oral_pde": 2, "parenteral_pde": 2, "inhalation_pde": 2},
                "Pb": {"name": "铅", "oral_pde": 5, "parenteral_pde": 5, "inhalation_pde": 5},
                "As": {"name": "砷", "oral_pde": 15, "parenteral_pde": 15, "inhalation_pde": 2},
                "Hg": {"name": "汞", "oral_pde": 30, "parenteral_pde": 30, "inhalation_pde": 15}
            }
        },
        "Class 2A": {
            "description": "人体毒性较低但环保关注元素",
            "elements": {
                "Co": {"name": "钴", "oral_pde": 47, "parenteral_pde": 47, "inhalation_pde": 5},
                "V": {"name": "钒", "oral_pde": 50, "parenteral_pde": 50, "inhalation_pde": 10},
                "Ni": {"name": "镍", "oral_pde": 200, "parenteral_pde": 200, "inhalation_pde": 5},
                "Tl": {"name": "铊", "oral_pde": 8, "parenteral_pde": 8, "inhalation_pde": 8}
            }
        },
        "Class 2B": {
            "description": "人体毒性较低元素",
            "elements": {
                "Ag": {"name": "银", "oral_pde": 150, "parenteral_pde": 150, "inhalation_pde": 150},
                "Au": {"name": "金", "oral_pde": 100, "parenteral_pde": 100, "inhalation_pde": 100},
                "Ir": {"name": "铱", "oral_pde": 100, "parenteral_pde": 100, "inhalation_pde": 100},
                "Os": {"name": "锇", "oral_pde": 100, "parenteral_pde": 100, "inhalation_pde": 100},
                "Pd": {"name": "钯", "oral_pde": 100, "parenteral_pde": 100, "inhalation_pde": 100},
                "Pt": {"name": "铂", "oral_pde": 100, "parenteral_pde": 100, "inhalation_pde": 100},
                "Rh": {"name": "铑", "oral_pde": 100, "parenteral_pde": 100, "inhalation_pde": 100},
                "Ru": {"name": "钌", "oral_pde": 100, "parenteral_pde": 100, "inhalation_pde": 100},
                "Se": {"name": "硒", "oral_pde": 120, "parenteral_pde": 120, "inhalation_pde": 120},
                "W": {"name": "钨", "oral_pde": 1000, "parenteral_pde": 1000, "inhalation_pde": 1000}
            }
        },
        "Class 3": {
            "description": "低毒性元素",
            "elements": {
                "Ba": {"name": "钡", "oral_pde": 1400, "parenteral_pde": 1400, "inhalation_pde": 1400},
                "Cr": {"name": "铬", "oral_pde": 1100, "parenteral_pde": 1100, "inhalation_pde": 1100},
                "Cu": {"name": "铜", "oral_pde": 1200, "parenteral_pde": 1200, "inhalation_pde": 1200},
                "Li": {"name": "锂", "oral_pde": 2500, "parenteral_pde": 2500, "inhalation_pde": 2500},
                "Mn": {"name": "锰", "oral_pde": 1200, "parenteral_pde": 1200, "inhalation_pde": 1200},
                "Mo": {"name": "钼", "oral_pde": 1500, "parenteral_pde": 1500, "inhalation_pde": 1500},
                "Sb": {"name": "锑", "oral_pde": 900, "parenteral_pde": 900, "inhalation_pde": 900},
                "Sn": {"name": "锡", "oral_pde": 6000, "parenteral_pde": 6000, "inhalation_pde": 6000}
            }
        }
    }
}

# ICH Q3C 溶剂数据
Q3C_SOLVENTS_DATA = {
    "Class 1": {
        "description": "避免使用（致癌、致突变、生殖毒性）",
        "solvents": {
            "1,2-Dichloroethane": {"name_cn": "1,2-二氯乙烷", "limit_ppm": 5, "concern": "致癌"},
            "1,1-Dichloroethane": {"name_cn": "1,1-二氯乙烷", "limit_ppm": 1500, "concern": "致癌"},
            "1,1,1-Trichloroethane": {"name_cn": "1,1,1-三氯乙烷", "limit_ppm": 1500, "concern": "臭氧层破坏"},
            "Benzene": {"name_cn": "苯", "limit_ppm": 2, "concern": "致癌"},
            "Carbon Tetrachloride": {"name_cn": "四氯化碳", "limit_ppm": 4, "concern": "肝毒性和致癌"},
            "1,2-Dichloroethylene": {"name_cn": "1,2-二氯乙烯", "limit_ppm": 1500, "concern": "致癌"}
        }
    },
    "Class 2": {
        "description": "限制使用（非遗传毒性致癌、神经毒性、致畸）",
        "solvents": {
            "Acetonitrile": {"name_cn": "乙腈", "limit_ppm": 410, "pde_mg_day": 4.1},
            "Chlorobenzene": {"name_cn": "氯苯", "limit_ppm": 360, "pde_mg_day": 3.6},
            "Chloroform": {"name_cn": "氯仿", "limit_ppm": 60, "pde_mg_day": 0.6},
            "Cyclohexane": {"name_cn": "环己烷", "limit_ppm": 3880, "pde_mg_day": 38.8},
            "Dichloromethane": {"name_cn": "二氯甲烷", "limit_ppm": 600, "pde_mg_day": 6.0},
            "1,2-Dichloroethene": {"name_cn": "1,2-二氯乙烯", "limit_ppm": 1870, "pde_mg_day": 18.7},
            "N,N-Dimethylformamide": {"name_cn": "N,N-二甲基甲酰胺", "limit_ppm": 880, "pde_mg_day": 8.8},
            "N,N-Dimethylacetamide": {"name_cn": "N,N-二甲基乙酰胺", "limit_ppm": 1090, "pde_mg_day": 10.9},
            "1,4-Dioxane": {"name_cn": "1,4-二噁烷", "limit_ppm": 380, "pde_mg_day": 3.8},
            "Ethylene Glycol": {"name_cn": "乙二醇", "limit_ppm": 620, "pde_mg_day": 6.2},
            "Formamide": {"name_cn": "甲酰胺", "limit_ppm": 220, "pde_mg_day": 2.2},
            "Hexane": {"name_cn": "正己烷", "limit_ppm": 290, "pde_mg_day": 2.9},
            "Methanol": {"name_cn": "甲醇", "limit_ppm": 3000, "pde_mg_day": 30.0},
            "N-Methylpyrrolidone": {"name_cn": "N-甲基吡咯烷酮", "limit_ppm": 1530, "pde_mg_day": 15.3},
            "Pyridine": {"name_cn": "吡啶", "limit_ppm": 2000, "pde_mg_day": 20.0},
            "Sulfolane": {"name_cn": "环丁砜", "limit_ppm": 160, "pde_mg_day": 1.6},
            "Tetrahydrofuran": {"name_cn": "四氢呋喃", "limit_ppm": 720, "pde_mg_day": 7.2},
            "Toluene": {"name_cn": "甲苯", "limit_ppm": 890, "pde_mg_day": 8.9},
            "Xylene": {"name_cn": "二甲苯", "limit_ppm": 2170, "pde_mg_day": 21.7}
        }
    },
    "Class 3": {
        "description": "低毒性溶剂",
        "solvents": {
            "Acetic Acid": {"name_cn": "乙酸", "limit_ppm": 5000},
            "Acetone": {"name_cn": "丙酮", "limit_ppm": 5000},
            "Anisole": {"name_cn": "苯甲醚", "limit_ppm": 5000},
            "1-Butanol": {"name_cn": "1-丁醇", "limit_ppm": 5000},
            "2-Butanol": {"name_cn": "2-丁醇", "limit_ppm": 5000},
            "Butyl Acetate": {"name_cn": "乙酸丁酯", "limit_ppm": 5000},
            "tert-Butylmethyl Ether": {"name_cn": "叔丁基甲基醚", "limit_ppm": 5000},
            "Cumene": {"name_cn": "异丙苯", "limit_ppm": 5000},
            "Dimethyl Sulfoxide": {"name_cn": "二甲基亚砜", "limit_ppm": 5000},
            "Ethanol": {"name_cn": "乙醇", "limit_ppm": 5000},
            "Ethyl Acetate": {"name_cn": "乙酸乙酯", "limit_ppm": 5000},
            "Ethyl Ether": {"name_cn": "乙醚", "limit_ppm": 5000},
            "Ethyl Formate": {"name_cn": "甲酸乙酯", "limit_ppm": 5000},
            "Formic Acid": {"name_cn": "甲酸", "limit_ppm": 5000},
            "Heptane": {"name_cn": "庚烷", "limit_ppm": 5000},
            "Isobutyl Acetate": {"name_cn": "乙酸异丁酯", "limit_ppm": 5000},
            "Isopropyl Acetate": {"name_cn": "乙酸异丙酯", "limit_ppm": 5000},
            "Methyl Acetate": {"name_cn": "乙酸甲酯", "limit_ppm": 5000},
            "3-Methyl-1-butanol": {"name_cn": "3-甲基-1-丁醇", "limit_ppm": 5000},
            "Methyl Ethyl Ketone": {"name_cn": "甲基乙基酮", "limit_ppm": 5000},
            "Methyl Isobutyl Ketone": {"name_cn": "甲基异丁基酮", "limit_ppm": 5000},
            "2-Methyl-1-propanol": {"name_cn": "2-甲基-1-丙醇", "limit_ppm": 5000},
            "Pentane": {"name_cn": "戊烷", "limit_ppm": 5000},
            "1-Pentanol": {"name_cn": "1-戊醇", "limit_ppm": 5000},
            "1-Propyl Acetate": {"name_cn": "乙酸丙酯", "limit_ppm": 5000},
            "2-Propyl Acetate": {"name_cn": "乙酸异丙酯", "limit_ppm": 5000},
            "Water": {"name_cn": "水", "limit_ppm": 5000}
        }
    }
}


def extract_text_from_docx(file_content: bytes) -> str:
    """从 DOCX 文件提取文本"""
    if Document is None:
        raise ImportError("python-docx 未安装")
    
    with tempfile.NamedTemporaryFile(suffix='.docx', delete=False) as tmp:
        tmp.write(file_content)
        tmp_path = tmp.name
    
    try:
        doc = Document(tmp_path)
        paragraphs = [p.text.strip() for p in doc.paragraphs if p.text.strip()]
        return "\n".join(paragraphs)
    finally:
        Path(tmp_path).unlink()


def identify_elements_from_text(text: str) -> list[dict[str, Any]]:
    """从文本识别可能存在的元素杂质（简化版，实际应调用 LLM）"""
    elements_found = []
    
    # 常见元素关键词映射
    element_keywords = {
        "钯": "Pd", "Pd": "Pd", "palladium": "Pd",
        "铂": "Pt", "Pt": "Pt", "platinum": "Pt",
        "钌": "Ru", "Ru": "Ru", "ruthenium": "Ru",
        "铑": "Rh", "Rh": "Rh", "rhodium": "Rh",
        "铱": "Ir", "Ir": "Ir", "iridium": "Ir",
        "镍": "Ni", "Ni": "Ni", "nickel": "Ni",
        "钴": "Co", "Co": "Co", "cobalt": "Co",
        "钨": "W", "W": "W", "tungsten": "W",
        "银": "Ag", "Ag": "Ag", "silver": "Ag",
        "金": "Au", "Au": "Au", "gold": "Au",
        "铜": "Cu", "Cu": "Cu", "copper": "Cu",
        "铁": "Fe", "Fe": "Fe", "iron": "Fe",
        "锰": "Mn", "Mn": "Mn", "manganese": "Mn",
        "铬": "Cr", "Cr": "Cr", "chromium": "Cr",
        "钼": "Mo", "Mo": "Mo", "molybdenum": "Mo",
        "钒": "V", "V": "V", "vanadium": "V",
        "锌": "Zn", "Zn": "Zn", "zinc": "Zn",
        "锡": "Sn", "Sn": "Sn", "tin": "Sn",
        "铅": "Pb", "Pb": "Pb", "lead": "Pb",
        "汞": "Hg", "Hg": "Hg", "mercury": "Hg",
        "镉": "Cd", "Cd": "Cd", "cadmium": "Cd",
        "砷": "As", "As": "As", "arsenic": "As",
    }
    
    text_lower = text.lower()
    
    for keyword, symbol in element_keywords.items():
        if keyword.lower() in text_lower:
            # 获取元素数据
            element_data = None
            q3d_class = None
            
            for cls_name, cls_data in Q3D_ELEMENTS_DATA["classes"].items():
                if symbol in cls_data["elements"]:
                    element_data = cls_data["elements"][symbol]
                    q3d_class = cls_name
                    break
            
            if element_data:
                elements_found.append({
                    "symbol": symbol,
                    "name": element_data.get("name", symbol),
                    "class": q3d_class,
                    "oral_pde": element_data.get("oral_pde"),
                    "parenteral_pde": element_data.get("parenteral_pde"),
                    "inhalation_pde": element_data.get("inhalation_pde"),
                    "found_in_text": True
                })
    
    return elements_found


def identify_solvents_from_text(text: str) -> list[dict[str, Any]]:
    """从文本识别溶剂（简化版，实际应调用 LLM）"""
    solvents_found = []
    
    # 常见溶剂关键词映射
    solvent_keywords = {
        "甲醇": "Methanol", "methanol": "Methanol", "meoh": "Methanol",
        "乙醇": "Ethanol", "ethanol": "Ethanol", "etoh": "Ethanol", "酒精": "Ethanol",
        "丙酮": "Acetone", "acetone": "Acetone",
        "乙腈": "Acetonitrile", "acetonitrile": "Acetonitrile",
        "二氯甲烷": "Dichloromethane", "dichloromethane": "Dichloromethane", "dcm": "Dichloromethane",
        "氯仿": "Chloroform", "chloroform": "Chloroform",
        "四氢呋喃": "Tetrahydrofuran", "tetrahydrofuran": "Tetrahydrofuran", "thf": "Tetrahydrofuran",
        "甲苯": "Toluene", "toluene": "Toluene",
        "二甲苯": "Xylene", "xylene": "Xylene",
        "乙酸乙酯": "Ethyl Acetate", "ethyl acetate": "Ethyl Acetate",
        "正己烷": "Hexane", "hexane": "Hexane",
        "庚烷": "Heptane", "heptane": "Heptane",
        "戊烷": "Pentane", "pentane": "Pentane",
        "环己烷": "Cyclohexane", "cyclohexane": "Cyclohexane",
        "苯": "Benzene", "benzene": "Benzene",
        "吡啶": "Pyridine", "pyridine": "Pyridine",
        "dmf": "N,N-Dimethylformamide", "n,n-二甲基甲酰胺": "N,N-Dimethylformamide",
        "dmso": "Dimethyl Sulfoxide", "二甲基亚砜": "Dimethyl Sulfoxide",
        "水": "Water", "water": "Water",
    }
    
    text_lower = text.lower()
    
    for keyword, solvent_name in solvent_keywords.items():
        if keyword.lower() in text_lower:
            # 获取溶剂数据
            solvent_data = None
            q3c_class = None
            
            for cls_name, cls_data in Q3C_SOLVENTS_DATA.items():
                if solvent_name in cls_data["solvents"]:
                    solvent_data = cls_data["solvents"][solvent_name]
                    q3c_class = cls_name
                    break
            
            if solvent_data:
                solvents_found.append({
                    "name_en": solvent_name,
                    "name_cn": solvent_data.get("name_cn", solvent_name),
                    "class": q3c_class,
                    "limit_ppm": solvent_data.get("limit_ppm"),
                    "pde_mg_day": solvent_data.get("pde_mg_day"),
                    "concern": solvent_data.get("concern"),
                    "found_in_text": True
                })
    
    return solvents_found


def analyze_ich_q3d(file_content: bytes) -> dict[str, Any]:
    """分析 ICH Q3D 元素杂质"""
    text = extract_text_from_docx(file_content)
    elements = identify_elements_from_text(text)
    
    return {
        "type": "Q3D",
        "text_length": len(text),
        "elements_found": elements,
        "total_elements": len(elements),
        "summary": {
            "class_1": len([e for e in elements if e["class"] == "Class 1"]),
            "class_2a": len([e for e in elements if e["class"] == "Class 2A"]),
            "class_2b": len([e for e in elements if e["class"] == "Class 2B"]),
            "class_3": len([e for e in elements if e["class"] == "Class 3"]),
        }
    }


def analyze_ich_q3c(file_content: bytes) -> dict[str, Any]:
    """分析 ICH Q3C 溶剂残留"""
    text = extract_text_from_docx(file_content)
    solvents = identify_solvents_from_text(text)
    
    return {
        "type": "Q3C",
        "text_length": len(text),
        "solvents_found": solvents,
        "total_solvents": len(solvents),
        "summary": {
            "class_1": len([s for s in solvents if s["class"] == "Class 1"]),
            "class_2": len([s for s in solvents if s["class"] == "Class 2"]),
            "class_3": len([s for s in solvents if s["class"] == "Class 3"]),
        }
    }
