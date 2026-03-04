"""
五大需求提取器 - 测试脚本
测试核心模块的功能
"""
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import pytest  # noqa: E402
from unittest.mock import patch, MagicMock  # noqa: E402

from src.core.extractor import NeedsExtractor  # noqa: E402
from src.core.file_handler import extract_text  # noqa: E402


class TestNeedsExtractorParseResponse:
    """测试 _parse_response 方法"""

    def setup_method(self):
        with patch.object(NeedsExtractor, '__init__', lambda self: None):
            self.extractor = NeedsExtractor()
            self.extractor.config = MagicMock()
            self.extractor.session = MagicMock()

    def test_parse_valid_json(self):
        response = '{"融资": "需要A轮融资。", "产业": "", "技术": "需要算力支持。", "人才": "", "媒体": ""}'
        result = self.extractor._parse_response(response)
        assert result["融资"] == "需要A轮融资。"
        assert result["技术"] == "需要算力支持。"
        assert result["产业"] == ""

    def test_parse_json_wrapped_in_text(self):
        response = '以下是提取结果：\n{"融资": "需要融资。", "产业": "", "技术": "", "人才": "", "媒体": ""}\n请参考。'
        result = self.extractor._parse_response(response)
        assert result["融资"] == "需要融资。"

    def test_parse_invalid_json(self):
        response = "这不是JSON格式的内容"
        result = self.extractor._parse_response(response)
        assert result == {}


class TestPostProcessNeeds:
    """测试 _post_process_needs 方法"""

    def setup_method(self):
        with patch.object(NeedsExtractor, '__init__', lambda self: None):
            self.extractor = NeedsExtractor()
            self.extractor.config = MagicMock()
            self.extractor.session = MagicMock()

    def test_remove_number_prefix(self):
        needs = {"融资": "1. 需要融资。"}
        result = self.extractor._post_process_needs(needs)
        assert result["融资"] == "需要融资。"

    def test_remove_circle_number_prefix(self):
        needs = {"融资": "① 需要融资。"}
        result = self.extractor._post_process_needs(needs)
        assert result["融资"] == "需要融资。"

    def test_add_period_if_missing(self):
        needs = {"融资": "需要融资"}
        result = self.extractor._post_process_needs(needs)
        assert result["融资"] == "需要融资。"

    def test_empty_string_unchanged(self):
        needs = {"融资": ""}
        result = self.extractor._post_process_needs(needs)
        assert result["融资"] == ""

    def test_non_string_value(self):
        needs = {"融资": None}
        result = self.extractor._post_process_needs(needs)
        assert result["融资"] == ""


class TestExtractText:
    """测试文件文本提取"""

    def test_extract_txt(self, tmp_path):
        txt_file = tmp_path / "test.txt"
        txt_file.write_text("这是一段测试文本内容", encoding="utf-8")
        result = extract_text(str(txt_file))
        assert "测试文本" in result

    def test_unsupported_format(self, tmp_path):
        bad_file = tmp_path / "test.xyz"
        bad_file.write_text("content")
        with pytest.raises(Exception, match="不支持的文件格式"):
            extract_text(str(bad_file))


class TestFastAPI:
    """测试 FastAPI 端点"""

    @pytest.fixture(autouse=True)
    def setup_client(self):
        from fastapi.testclient import TestClient
        from src.api.app_fastapi import app
        self.client = TestClient(app)

    def test_root(self):
        resp = self.client.get("/")
        assert resp.status_code == 200
        data = resp.json()
        assert data["service"] == "五大需求提取器"
        assert data["status"] == "running"

    def test_health(self):
        resp = self.client.get("/health")
        assert resp.status_code == 200
        assert resp.json()["status"] == "ok"

    def test_extract_empty_content(self):
        resp = self.client.post("/extract", json={"content": ""})
        assert resp.status_code == 400
        data = resp.json()
        assert data["code"] == "400"
        assert data["msg"] == "内容为空"

    def test_extract_whitespace_content(self):
        resp = self.client.post("/extract", json={"content": "   "})
        assert resp.status_code == 400

    def test_extract_files_nonexistent(self):
        resp = self.client.post("/extract/files", json={
            "Inquire_Excel": "/nonexistent/file.xlsx",
            "product_Id": "1",
            "product_Code": "X",
            "productDoc": "doc",
        })
        assert resp.status_code == 404
        assert "文件不存在" in resp.json()["msg"]
