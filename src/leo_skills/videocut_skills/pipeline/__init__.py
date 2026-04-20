# -*- coding: utf-8 -*-
"""
video_pipeline - 视频自动剪辑流水线

SOP 化的视频自动处理流水线，支持：
- 文件夹监控自动触发
- 删减 + 字幕 + 调色 + 片头片尾
- 输出 9:16 竖屏成品
"""

from .watcher import VideoFolderWatcher
from .preprocessor import VideoPreprocessor
from .composer import VideoComposer

__all__ = ["VideoFolderWatcher", "VideoPreprocessor", "VideoComposer"]
