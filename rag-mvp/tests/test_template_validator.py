"""AG-001: 商户知识模板校验器测试（TDD - 先写失败测试）。"""

from src.agent.template_validator import validate_merchant_template, ValidationResult


class TestTemplateValidator:
    """商户知识模板校验测试集。"""

    FULL_TEMPLATE = (
        "# 商品信息\n鲜花、蛋糕、水果\n"
        "# 门店信息\n北京市朝阳区 XX 路 1 号\n"
        "# 配送规则\n市区 3 公里内免费配送\n"
        "# 售后政策\n签收后 24 小时内可退\n"
    )

    def test_valid_template_passes(self):
        """包含全部 4 个 section 的文本校验通过。"""
        result = validate_merchant_template(self.FULL_TEMPLATE)
        assert isinstance(result, ValidationResult)
        assert result.valid is True
        assert result.missing_sections == []
        assert result.errors == []

    def test_missing_one_section_returns_error(self):
        """缺少一个 section 时返回该 section 名称。"""
        text = (
            "# 商品信息\n鲜花\n"
            "# 门店信息\n北京\n"
            "# 配送规则\n同城配送\n"
            # 缺 售后政策
        )
        result = validate_merchant_template(text)
        assert result.valid is False
        assert "售后政策" in result.missing_sections
        assert len(result.missing_sections) == 1

    def test_missing_multiple_sections_returns_all(self):
        """缺少多个 section 时全部返回。"""
        text = "# 商品信息\n商品列表\n"
        result = validate_merchant_template(text)
        assert result.valid is False
        assert set(result.missing_sections) == {"门店信息", "配送规则", "售后政策"}

    def test_empty_text_returns_all_missing(self):
        """空字符串返回全部 4 个缺失 section。"""
        result = validate_merchant_template("")
        assert result.valid is False
        assert len(result.missing_sections) == 4
        assert set(result.missing_sections) == {"商品信息", "门店信息", "配送规则", "售后政策"}

    def test_errors_are_machine_readable(self):
        """错误列表中每个元素包含 code 和 section 字段，满足机器可读。"""
        result = validate_merchant_template("")
        assert len(result.errors) == 4
        for error in result.errors:
            assert "code" in error
            assert "section" in error
            assert error["code"] == "MISSING_SECTION"
