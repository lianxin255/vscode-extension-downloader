<!--
 * @FilePath: README_zh.md
 * @Author: lianxin
 * @Date: 2025-06-09 11:05:30
 * @LastEditors: lianxin
 * @LastEditTime: 2025-06-09 11:06:41
 * Copyright (c) 2025 by lianxin, email: wsl1933467270@gamil.com, All Rights Reserved.
 * @Descripttion: 
-->
# VS Code 扩展下载器 [中文 | English](README.md)

此脚本用于下载 `extensions.txt` 文件中列出的 VS Code 扩展。

## 先决条件

- Python 3
- Pip (Python 包安装程序)

## 设置

1.  **克隆仓库或下载文件。**
2.  **安装依赖项：**
    ```bash
    pip install -r requirements.txt
    ```
3.  **填充 `extensions.txt`：**
    添加您要下载的 VS Code 扩展 ID，每行一个。例如：
    ```
    ms-python.python
    ritwickdey.liveserver
    ```
    您可以在 VS Code 应用市场找到扩展 ID。它通常采用 `发布者.扩展名` 的格式。

## 使用方法

从项目的根目录运行脚本：

```bash
python download_vsix.py
```

## 输出

-   **`.vsix` 文件：** 下载的扩展文件将保存在 `vsix_files/` 目录中。
-   **日志文件：** 下载过程的日志将创建在 `download_vsix.log`。

## 工作原理

脚本从 `extensions.txt` 中读取每个扩展 ID，构建 VS Code 应用市场的下载 URL，下载 `.vsix` 文件，并将其保存到 `vsix_files/` 目录中。它会将进度和任何错误记录到 `download_vsix.log`。