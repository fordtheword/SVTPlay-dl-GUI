"""Tests for the POST /api/open-folder endpoint"""
import os

import pytest

import app as app_module
from config import Config


@pytest.fixture
def client():
    app_module.app.config["TESTING"] = True
    with app_module.app.test_client() as client:
        yield client


@pytest.fixture
def opened_paths(monkeypatch):
    """Capture paths passed to os.startfile instead of opening Explorer"""
    opened = []
    monkeypatch.setattr(os, "startfile", lambda path: opened.append(path), raising=False)
    return opened


def test_open_folder_opens_requested_folder(client, opened_paths, tmp_path):
    response = client.post("/api/open-folder", json={"folder": str(tmp_path)})

    assert response.status_code == 200
    assert response.get_json()["success"] is True
    assert opened_paths == [str(tmp_path)]


def test_open_folder_defaults_to_download_dir(client, opened_paths):
    response = client.post("/api/open-folder", json={})

    assert response.status_code == 200
    assert response.get_json()["success"] is True
    assert opened_paths == [Config.DOWNLOAD_DIR]


def test_open_folder_returns_network_path_when_configured(client, opened_paths, monkeypatch):
    unc = r"\\192.168.1.72\torrents\downloads\svtplay"
    monkeypatch.setattr(Config, "NETWORK_DOWNLOAD_PATH", unc)

    response = client.post("/api/open-folder", json={})

    assert response.status_code == 200
    body = response.get_json()
    assert body["success"] is True
    assert body["mode"] == "network_path"
    assert body["network_path"] == unc
    assert opened_paths == []


def test_open_folder_opens_locally_when_no_network_path(client, opened_paths, tmp_path, monkeypatch):
    monkeypatch.setattr(Config, "NETWORK_DOWNLOAD_PATH", "")

    response = client.post("/api/open-folder", json={"folder": str(tmp_path)})

    assert response.get_json()["mode"] == "opened"
    assert opened_paths == [str(tmp_path)]


def test_open_folder_rejects_nonexistent_path(client, opened_paths):
    response = client.post("/api/open-folder", json={"folder": r"D:\finns\inte\alls"})

    assert response.status_code == 404
    body = response.get_json()
    assert body["success"] is False
    assert opened_paths == []
