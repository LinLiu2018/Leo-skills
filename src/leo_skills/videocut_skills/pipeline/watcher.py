# -*- coding: utf-8 -*-
"""
watcher.py - 文件夹监控模块

监控指定文件夹，新视频放入后自动触发处理流水线
"""

import os
import sys
import time
import shutil
import logging
from pathlib import Path
from typing import Optional, Callable
from queue import Queue
from threading import Thread

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

try:
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler, FileCreatedEvent, FileMovedEvent
except ImportError:
    print("请安装 watchdog: pip install watchdog")
    raise

logger = logging.getLogger(__name__)


class VideoFolderHandler(FileSystemEventHandler):
    """视频文件夹事件处理器"""

    VIDEO_EXTENSIONS = {'.mp4', '.mov', '.mkv', '.avi', '.flv', '.wmv', '.webm'}

    def __init__(self, pipeline, watch_folder: str):
        super().__init__()
        self.pipeline = pipeline
        self.watch_folder = Path(watch_folder)
        self.input_folder = self.watch_folder / "input"
        self.processing_folder = self.watch_folder / "processing"
        self._ensure_folders()

    def _ensure_folders(self):
        """确保必要的文件夹存在"""
        self.input_folder.mkdir(parents=True, exist_ok=True)
        self.processing_folder.mkdir(parents=True, exist_ok=True)

    def _is_video(self, path: str) -> bool:
        """检查文件是否为视频"""
        ext = Path(path).suffix.lower()
        return ext in self.VIDEO_EXTENSIONS

    def _move_to_processing(self, video_path: str) -> str:
        """移动视频到处理文件夹"""
        video_path = Path(video_path)
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        new_name = f"{timestamp}_{video_path.name}"
        dest_path = self.processing_folder / new_name

        # 复制文件到 processing 目录
        shutil.copy2(video_path, dest_path)
        logger.info(f"已复制视频到处理目录: {dest_path}")

        return str(dest_path)

    def on_created(self, event):
        """文件创建事件"""
        if event.is_directory:
            return

        if self._is_video(event.src_path):
            logger.info(f"检测到新视频: {event.src_path}")
            # 移动到 processing 并触发流水线
            processing_path = self._move_to_processing(event.src_path)
            self.pipeline.enqueue(processing_path)

    def on_moved(self, event):
        """文件移动事件（有些软件会先创建再移动）"""
        if event.is_directory:
            return

        if isinstance(event, FileMovedEvent):
            if self._is_video(event.dest_path):
                logger.info(f"检测到新视频(移动): {event.dest_path}")
                processing_path = self._move_to_processing(event.dest_path)
                self.pipeline.enqueue(processing_path)


class VideoFolderWatcher:
    """视频文件夹监控器"""

    def __init__(self, watch_folder: str, pipeline: Optional[Callable] = None):
        self.watch_folder = Path(watch_folder)
        self.pipeline = pipeline
        self.observer: Optional[Observer] = None
        self.processing_queue: Queue = Queue()
        self.processing_thread: Optional[Thread] = None
        self._running = False

    def _ensure_folders(self):
        """确保监控文件夹结构完整"""
        folders = ["input", "processing", "output", "temp", "templates"]
        for folder in folders:
            (self.watch_folder / folder).mkdir(parents=True, exist_ok=True)
        logger.info(f"已确保文件夹结构: {self.watch_folder}")

    def start(self):
        """启动文件夹监控"""
        self._ensure_folders()
        self._running = True

        # 启动处理线程
        self.processing_thread = Thread(target=self._process_queue, daemon=True)
        self.processing_thread.start()

        # 启动观察者
        event_handler = VideoFolderHandler(self, str(self.watch_folder))
        self.observer = Observer()
        self.observer.schedule(event_handler, str(self.watch_folder / "input"), recursive=False)
        self.observer.start()

        logger.info(f"文件夹监控已启动: {self.watch_folder / 'input'}")
        print(f"📁 监控文件夹: {self.watch_folder / 'input'}")
        print("⏳ 等待新视频...")

    def stop(self):
        """停止文件夹监控"""
        self._running = False
        if self.observer:
            self.observer.stop()
            self.observer.join()
        logger.info("文件夹监控已停止")

    def enqueue(self, video_path: str):
        """将视频加入处理队列"""
        self.processing_queue.put(video_path)
        logger.info(f"视频已加入队列: {video_path}")

    def _process_queue(self):
        """处理队列中的视频"""
        while self._running:
            try:
                if not self.processing_queue.empty():
                    video_path = self.processing_queue.get(timeout=1)
                    if self.pipeline:
                        logger.info(f"开始处理: {video_path}")
                        self.pipeline(video_path)
                else:
                    time.sleep(0.5)
            except Exception as e:
                logger.error(f"处理视频时出错: {e}")
                import traceback
                traceback.print_exc()

    def run(self):
        """阻塞运行监控"""
        try:
            self.start()
            while self._running:
                time.sleep(1)
        except KeyboardInterrupt:
            self.stop()


def create_watcher(watch_folder: str, pipeline: Optional[Callable] = None) -> VideoFolderWatcher:
    """创建文件夹监控器的工厂函数"""
    return VideoFolderWatcher(watch_folder, pipeline)


if __name__ == "__main__":
    # 测试代码
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    def test_pipeline(video_path):
        print(f"🎬 测试流水线收到视频: {video_path}")

    watcher = create_watcher("D:/video_pipeline/watch", test_pipeline)
    watcher.run()
