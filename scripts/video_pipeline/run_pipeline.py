# -*- coding: utf-8 -*-
"""
run_pipeline.py - 视频自动剪辑流水线启动脚本

使用方法:
    python scripts/video_pipeline/run_pipeline.py --watch D:/video_pipeline/watch

开机自启动:
    将此脚本添加到启动目录或创建 Windows 计划任务
"""

import os
import sys
import argparse
import logging
from pathlib import Path

# 添加项目根目录到 Python 路径
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(PROJECT_ROOT / 'logs' / 'video_pipeline.log', encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)


def load_config():
    """加载流水线配置"""
    import yaml

    config_path = PROJECT_ROOT / 'src' / 'leo_skills' / 'videocut_skills' / 'pipeline' / 'config.yaml'

    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        logger.info(f"配置加载成功: {config_path}")
        return config
    except Exception as e:
        logger.error(f"配置加载失败: {e}")
        # 返回默认配置
        return {
            'pipeline': {
                'watch_folder': 'D:/video_pipeline/watch',
                'output_folder': 'D:/video_pipeline/output',
                'temp_folder': 'D:/video_pipeline/temp',
                'templates_folder': 'D:/video_pipeline/templates',
            },
            'processing': {
                'remove_filler_words': True,
                'remove_silence': True,
                'silence_threshold': '-40dB',
                'min_silence_duration': 0.5,
                'subtitle': {
                    'font_size': 28,
                    'font_color': 'white',
                    'stroke_color': 'black',
                    'stroke_width': 2,
                    'position': 'bottom',
                    'max_chars_per_line': 15
                },
                'color_preset': 'cinematic',
                'color_presets': {
                    'cinematic': {
                        'saturation': 1.1,
                        'contrast': 1.1,
                        'brightness': 0.02,
                        'hue': 0.05
                    },
                    'cool': {
                        'saturation': 0.95,
                        'contrast': 1.05,
                        'brightness': 0.0,
                        'hue': -0.05
                    },
                    'warm': {
                        'saturation': 1.15,
                        'contrast': 1.1,
                        'brightness': 0.03,
                        'hue': 0.08
                    },
                    'vibrant': {
                        'saturation': 1.3,
                        'contrast': 1.2,
                        'brightness': 0.02,
                        'hue': 0.0
                    }
                },
                'output': {
                    'resolution': '1080x1920',
                    'codec': 'libx264',
                    'crf': 20,
                    'audio_bitrate': '128k',
                    'preset': 'medium'
                },
                'intro': {
                    'enabled': True,
                    'file': 'intro_vertical.mp4'
                },
                'outro': {
                    'enabled': True,
                    'file': 'outro_vertical.mp4'
                },
                'asr': {
                    'engine': 'funasr',
                    'model': 'paraformer-zh',
                    'language': 'zh'
                }
            }
        }


def process_video(video_path: str, config: dict):
    """
    处理单个视频的完整流水线

    步骤：
    1. 预处理（提取音频、检测静音、口误）
    2. 合成（剪辑、调色、加字幕、片头片尾、输出竖屏）
    """
    from src.leo_skills.videocut_skills.pipeline.preprocessor import VideoPreprocessor, CutSegment
    from src.leo_skills.videocut_skills.pipeline.composer import VideoComposer

    logger.info(f"=" * 50)
    logger.info(f"开始处理视频: {video_path}")
    logger.info(f"=" * 50)

    try:
        # 步骤1: 预处理
        logger.info("[1/2] 预处理: 提取音频、检测静音和口误...")
        preprocessor = VideoPreprocessor(config)
        result = preprocessor.preprocess(video_path)

        logger.info(f"  - 视频时长: {result.duration:.1f}秒")
        logger.info(f"  - 检测到 {len(result.cut_segments)} 个需删除片段")

        # 步骤2: 合成最终视频
        logger.info("[2/2] 合成: 剪辑、调色、加字幕、片头片尾、输出竖屏...")
        composer = VideoComposer(config)
        output_path = composer.compose(
            video_path=result.video_path,
            cut_segments=result.cut_segments,
            subtitle_path=None,  # TODO: 如果有字幕文件路径
            output_name=Path(video_path).stem
        )

        logger.info(f"=" * 50)
        logger.info(f"✅ 处理完成!")
        logger.info(f"📁 输出文件: {output_path}")
        logger.info(f"=" * 50)

        return output_path

    except Exception as e:
        logger.error(f"处理视频时出错: {e}")
        import traceback
        traceback.print_exc()
        return None


def main():
    parser = argparse.ArgumentParser(description='视频自动剪辑流水线')
    parser.add_argument('--watch', '-w', type=str,
                        help='监控文件夹路径',
                        default='D:/video_pipeline/watch')
    parser.add_argument('--video', '-v', type=str,
                        help='处理单个视频文件（不启用监控）')
    parser.add_argument('--config', '-c', type=str,
                        help='配置文件路径')
    parser.add_argument('--list-templates', '-l', action='store_true',
                        help='列出可用的片头片尾模板')
    parser.add_argument('--init', action='store_true',
                        help='初始化监控文件夹结构')

    args = parser.parse_args()

    # 加载配置
    config = load_config()

    # 初始化文件夹结构
    if args.init:
        watch_folder = Path(args.watch)
        for subfolder in ['input', 'processing', 'output', 'temp', 'templates']:
            (watch_folder / subfolder).mkdir(parents=True, exist_ok=True)
        print(f"✅ 已创建监控文件夹结构: {watch_folder}")
        return

    # 列出模板
    if args.list_templates:
        templates_folder = Path(config['pipeline']['templates_folder'])
        if templates_folder.exists():
            print("📁 可用的片头片尾模板:")
            for f in templates_folder.glob('*'):
                print(f"  - {f.name}")
        else:
            print("模板文件夹不存在")
        return

    # 处理单个视频
    if args.video:
        config['pipeline']['watch_folder'] = args.watch
        process_video(args.video, config)
        return

    # 启动文件夹监控
    print("""
╔════════════════════════════════════════════════════════════╗
║          📺 视频自动剪辑流水线 SOP 启动                     ║
╠════════════════════════════════════════════════════════════╣
║  功能: 删减 + 字幕 + 调色 + 片头片尾 → 9:16 竖屏输出        ║
║  监控: {}                                  ║
╚════════════════════════════════════════════════════════════╝
    """.format(args.watch))

    from src.leo_skills.videocut_skills.pipeline.watcher import VideoFolderWatcher

    # 创建流水线处理函数
    def pipeline_handler(video_path: str):
        process_video(video_path, config)

    # 启动监控
    watcher = VideoFolderWatcher(args.watch, pipeline_handler)

    try:
        watcher.start()
        print("\n⏳ 等待新视频放入监控文件夹...")
        print("📁 监控文件夹:", Path(args.watch) / 'input')
        print("📤 输出文件夹:", Path(args.watch) / 'output')
        print("\n按 Ctrl+C 停止监控\n")

        # 保持运行
        import time
        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        print("\n\n🛑 停止监控...")
        watcher.stop()
        print("👋 已退出")


if __name__ == "__main__":
    main()
