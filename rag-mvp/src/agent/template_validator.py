"""AG-001: 商户知识模板与校验"""

from dataclasses import dataclass, field
from typing import List, Dict


REQUIRED_SECTIONS = ["商品信息", "门店信息", "配送规则", "售后政策"]


@dataclass
class ValidationResult:
    valid: bool
    missing_sections: List[str] = field(default_factory=list)
    errors: List[Dict[str, str]] = field(default_factory=list)


def validate_merchant_template(text: str) -> ValidationResult:
    """
    校验商户知识模板文本。检查是否包含所有必备的 section。
    
    Args:
        text (str): 模板文本内容
        
    Returns:
        ValidationResult: 包含校验结果及缺失信息的对象
    """
    missing_sections = []
    errors = []
    
    for section in REQUIRED_SECTIONS:
        # 简单匹配：检查文本中是否包含 section 名称
        if section not in text:
            missing_sections.append(section)
            errors.append({
                "code": "MISSING_SECTION",
                "section": section
            })
            
    return ValidationResult(
        valid=len(missing_sections) == 0,
        missing_sections=missing_sections,
        errors=errors
    )
