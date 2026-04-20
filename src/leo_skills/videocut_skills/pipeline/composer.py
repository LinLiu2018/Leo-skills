# -*- coding: utf-8 -*-
"""
composer.py - 视频合成模块

最终视频合成：
1. 根据删除点列表剪辑视频
2. 添加片头片尾
3. 应用调色
4. 烧录字幕
5. 输出 9:16 竖屏
"""

import os
import sys
import time
import subprocess
import logging
from pathlib import Path
from typing import List, Optional, Dict
from dataclasses import dataclass

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

logger = logging.getLogger(__name__)


@dataclass
class CutSegment:
    """需要删除的片段"""
    start: float
    end: float
    reason: str


class VideoComposer:
    """视频合成器"""

    def __init__(self, config: dict):
        self.config = config
        self.watch_folder = Path(config.get('pipeline', {}).get('watch_folder', 'D:/video_pipeline/watch'))
        self.output_folder = self.watch_folder / "output"
        self.temp_folder = self.watch_folder / "temp"
        self.templates_folder = self.watch_folder / "templates"

        # 确保输出目录存在
        self.output_folder.mkdir(parents=True, exist_ok=True)

        # 加载处理配置
        self.processing = config.get('processing', {})
        self.output_config = self.processing.get('output', {})
        self.subtitle_config = self.processing.get('subtitle', {})
        self.intro_config = self.processing.get('intro', {})
        self.outro_config = self.processing.get('outro', {})

    def compose(self,
                video_path: str,
                cut_segments: List[CutSegment],
                subtitle_path: Optional[str] = None,
                output_name: Optional[str] = None) -> str:
        """
        合成最终视频

        Args:
            video_path: 原始视频路径
            cut_segments: 需要删除的片段列表
            subtitle_path: 字幕文件路径 (SRT)
            output_name: 输出文件名（不含扩展名）

        Returns:
            输出视频的完整路径
        """
        video_path = Path(video_path)
        if output_name is None:
            output_name = video_path.stem

        logger.info(f"开始合成视频: {output_name}")

        # 步骤1: 根据删除点剪辑视频
        cut_video_path = self._cut_video(video_path, cut_segments)

        # 步骤2: 应用调色
        colored_video_path = self._apply_color_grade(cut_video_path, output_name)

        # 步骤3: 烧录字幕
        if subtitle_path and Path(subtitle_path).exists():
            subtitled_video_path = self._burn_subtitles(colored_video_path, subtitle_path, output_name)
        else:
            subtitled_video_path = colored_video_path

        # 步骤4: 添加片头片尾
        final_video_path = self._add_intro_outro(subtitled_video_path, output_name)

        # 步骤5: 转换为 9:16 竖屏
        final_path = self._convert_to_vertical(final_video_path, output_name)

        # 清理临时文件
        self._cleanup([cut_video_path, colored_video_path, subtitled_video_path, final_video_path])

        logger.info(f"视频合成完成: {final_path}")
        return final_path

    def _run_ffmpeg(self, args: List[str], timeout: int = 600) -> bool:
        """执行 FFmpeg 命令"""
        try:
            # 添加 -hide_banner 减少输出
            if 'ffmpeg' in args[0]:
                args = [a for a in args if a != '-hide_banner']
                args.insert(1, '-hide_banner')

            result = subprocess.run(
                args,
                capture_output=True,
                text=True,
                timeout=timeout,
                encoding='utf-8',
                errors='ignore'
            )

            if result.returncode != 0:
                logger.error(f"FFmpeg 错误: {result.stderr[-500:]}")
                return False

            return True

        except subprocess.TimeoutExpired:
            logger.error("FFmpeg 命令执行超时")
            return False
        except Exception as e:
            logger.error(f"FFmpeg 执行异常: {e}")
            return False

    def _cut_video(self, video_path: Path, cut_segments: List[CutSegment]) -> Path:
        """根据删除点剪辑视频"""
        output_path = self.temp_folder / f"{video_path.stem}_cut.mp4"

        if not cut_segments:
            # 没有需要删除的片段，直接复制
            import shutil
            shutil.copy2(video_path, output_path)
            return output_path

        # 计算保留片段（反向：删除片段的补集）
        keep_segments = self._compute_keep_segments(video_path, cut_segments)

        # 生成 FFmpeg filter_complex 脚本
        filter_script = self._generate_filter_script(keep_segments)

        # 保存 filter 脚本
        filter_file = self.temp_folder / f"{video_path.stem}_filter.txt"
        with open(filter_file, 'w', encoding='utf-8') as f:
            f.write(filter_script)

        # 构建 FFmpeg 命令
        cmd = [
            'ffmpeg', '-y',
            '-i', str(video_path),
            '-filter_complex_script', str(filter_file),
            '-map', '[outv]', '-map', '[outa]',
            '-c:v', 'libx264', '-crf', '18',
            '-c:a', 'aac',
            str(output_path)
        ]

        if self._run_ffmpeg(cmd):
            logger.info(f"视频剪辑完成: {output_path}")
            return output_path
        else:
            # FFmpeg 失败，返回原视频
            return video_path

    def _compute_keep_segments(self, video_path: Path, cut_segments: List[CutSegment]) -> List[tuple]:
        """计算保留片段（删除片段的补集）"""
        # 获取视频时长
        duration = self._get_duration(video_path)

        # 将删除片段按起始时间排序
        sorted_cuts = sorted(cut_segments, key=lambda x: x.start)

        keep_segments = []
        last_end = 0.0

        for cut in sorted_cuts:
            # 确保删除片段在有效范围内
            cut_start = max(cut.start, 0)
            cut_end = min(cut.end, duration)

            if cut_start > last_end:
                # 有一段需要保留
                keep_segments.append((last_end, cut_start))

            last_end = max(last_end, cut_end)

        # 添加最后一段（如果需要）
        if last_end < duration:
            keep_segments.append((last_end, duration))

        return keep_segments

    def _generate_filter_script(self, keep_segments: List[tuple]) -> str:
        """生成 FFmpeg filter_complex 脚本"""
        lines = []

        for i, (start, end) in enumerate(keep_segments):
            duration = end - start
            lines.append(f"[0:v]trim=start={start:.3f}:end={end:.3f},setpts=PTS-STARTPTS[v{i}];")
            lines.append(f"[0:a]atrim=start={start:.3f}:end={end:.3f},asetpts=PTS-STARTPTS[a{i}];")

        # concat
        v_inputs = ''.join(f'[v{i}]' for i in range(len(keep_segments)))
        a_inputs = ''.join(f'[a{i}]' for i in range(len(keep_segments)))
        n = len(keep_segments)
        lines.append(f"{v_inputs}{a_inputs}concat=n={n}:v=1:a=1[outv][outa]")

        return '\n'.join(lines)

    def _get_duration(self, video_path: Path) -> float:
        """获取视频时长"""
        import json
        cmd = [
            'ffprobe',
            '-v', 'error',
            '-show_entries', 'format=duration',
            '-of', 'json',
            str(video_path)
        ]

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            data = json.loads(result.stdout)
            return float(data['format']['duration'])
        except Exception:
            return 0.0

    def _apply_color_grade(self, video_path: Path, output_name: str) -> Path:
        """应用调色"""
        output_path = self.temp_folder / f"{output_name}_colored.mp4"

        # 获取调色预设
        preset_name = self.processing.get('color_preset', 'cinematic')
        presets = self.processing.get('color_presets', {})
        preset = presets.get(preset_name, {})

        if not preset:
            # 没有配置调色，直接复制
            import shutil
            shutil.copy2(video_path, output_path)
            return output_path

        # 构建 eq 滤镜参数
        eq_filter = (
            f"eq=saturation={preset.get('saturation', 1.0)}:"
            f"contrast={preset.get('contrast', 1.0)}:"
            f"brightness={preset.get('brightness', 0.0)}:"
            f"hue={preset.get('hue', 0.0)}"
        )

        cmd = [
            'ffmpeg', '-y',
            '-i', str(video_path),
            '-vf', eq_filter,
            '-c:a', 'copy',
            str(output_path)
        ]

        if self._run_ffmpeg(cmd):
            logger.info(f"调色完成: {output_path}")
            return output_path
        else:
            return video_path

    def _burn_subtitles(self, video_path: Path, subtitle_path: str, output_name: str) -> Path:
        """烧录字幕到视频"""
        output_path = self.temp_folder / f"{output_name}_subtitled.mp4"

        # 字幕样式
        font_size = self.subtitle_config.get('font_size', 28)
        font_color = self.subtitle_config.get('font_color', 'white')
        stroke_color = self.subtitle_config.get('stroke_color', 'black')
        stroke_width = self.subtitle_config.get('stroke_width', 2)

        # 构建 ass 字幕样式
        ass_style = (
            f"FontName=Arial,FontSize={font_size},"
            f"PrimaryColour=&H00{self._color_to_bgra(font_color)},"
            f"OutlineColour=&H00{self._color_to_bgra(stroke_color)},"
            f"Outline=2,Bold=0,Alignment=2"
        )

        # 转换 SRT 为 ASS（添加样式）
        ass_path = self.temp_folder / f"{output_name}.ass"
        self._convert_srt_to_ass(subtitle_path, ass_path, ass_style)

        # 烧录字幕
        cmd = [
            'ffmpeg', '-y',
            '-i', str(video_path),
            '-vf', f"ass={ass_path}",
            '-c:a', 'copy',
            str(output_path)
        ]

        if self._run_ffmpeg(cmd):
            logger.info(f"字幕烧录完成: {output_path}")
            return output_path
        else:
            return video_path

    def _color_to_bgra(self, color: str) -> str:
        """将颜色名转换为 BGR 十六进制"""
        colors = {
            'white': 'FFFFFF',
            'black': '000000',
            'yellow': 'FFFF00',
            'red': 'FF0000',
            'green': '00FF00',
            'blue': '0000FF',
        }
        hex_color = colors.get(color.lower(), 'FFFFFF')
        # ASS 使用 ABGR 格式
        return f"FFFFFF{hex_color[4:6]}{hex_color[2:4]}{hex_color[0:2]}"

    def _convert_srt_to_ass(self, srt_path: str, ass_path: Path, style: str):
        """将 SRT 字幕转换为 ASS 格式"""
        import re

        with open(srt_path, 'r', encoding='utf-8') as f:
            srt_content = f.read()

        # 简化转换：生成带样式的 ASS 文件头 + 字幕内容
        ass_header = f"""[Script Info]
Title: Generated by Leo AI System
ScriptType: v4.00+

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,{style}

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""

        # 解析 SRT 并转换为 ASS 格式
        ass_body = []
        pattern = re.compile(r'(\d+)\n(\d{2}:\d{2}:\d{2},\d{3}) --> (\d{2}:\d{2}:\d{2},\d{3})\n(.+?)(?=\n\n|\n*$)', re.DOTALL)

        for match in pattern.finditer(srt_content):
            index, start, end, text = match.groups()
            # 转换时间格式 (SRT: HH:MM:SS,mmm -> ASS: HH:MM:SS.xx)
            start_ass = start.replace(',', '.')
            end_ass = end.replace(',', '.')

            # 转义 ASS 特殊字符
            text = text.replace('\\', '\\\\').replace('{', '\\{').replace('}', '\\}')
            text = text.replace('\n', '\\N')

            ass_body.append(f"Dialogue: 0,{start_ass},{end_ass},Default,,0,0,0,,{text}")

        with open(ass_path, 'w', encoding='utf-8') as f:
            f.write(ass_header + '\n'.join(ass_body))

    def _add_intro_outro(self, video_path: Path, output_name: str) -> Path:
        """添加片头片尾"""
        intro_enabled = self.intro_config.get('enabled', False)
        outro_enabled = self.outro_config.get('enabled', False)

        if not intro_enabled and not outro_enabled:
            return video_path

        output_path = self.temp_folder / f"{output_name}_with_intro_outro.mp4"

        # 收集需要拼接的片段
        concat_list = self.temp_folder / f"{output_name}_concat.txt"

        with open(concat_list, 'w', encoding='utf-8') as f:
            # 片头
            if intro_enabled:
                intro_file = self.templates_folder / self.intro_config.get('file', 'intro_vertical.mp4')
                if intro_file.exists():
                    f.write(f"file '{intro_file}'\n")

            # 主体视频
            f.write(f"file '{video_path}'\n")

            # 片尾
            if outro_enabled:
                outro_file = self.templates_folder / self.outro_config.get('file', 'outro_vertical.mp4')
                if outro_file.exists():
                    f.write(f"file '{outro_file}'\n")

        cmd = [
            'ffmpeg', '-y',
            '-f', 'concat',
            '-safe', '0',
            '-i', str(concat_list),
            '-c', 'copy',
            str(output_path)
        ]

        if self._run_ffmpeg(cmd):
            logger.info(f"片头片尾添加完成: {output_path}")
            return output_path
        else:
            return video_path

    def _convert_to_vertical(self, video_path: Path, output_name: str) -> Path:
        """转换为 9:16 竖屏"""
        output_path = self.output_folder / f"{output_name}_vertical.mp4"

        # 获取目标分辨率
        resolution = self.output_config.get('resolution', '1080x1920')
        width, height = map(int, resolution.split('x'))

        # 方案：裁切中间部分（适用于横屏转竖屏）
        # 如果原视频是横屏 (16:9)，取中间部分
        # 原视频假设 1920x1080，裁切中间 1080x1920 区域

        cmd = [
            'ffmpeg', '-y',
            '-i', str(video_path),
            # 裁切中间部分并缩放到目标分辨率
            '-vf', f"crop=ih*9/16:ih,scale={width}:{height}",
            '-c:a', 'aac',
            '-b:a', self.output_config.get('audio_bitrate', '128k'),
            '-preset', self.output_config.get('preset', 'medium'),
            '-crf', str(self.output_config.get('crf', 20)),
            str(output_path)
        ]

        if self._run_ffmpeg(cmd):
            logger.info(f"竖屏转换完成: {output_path}")
            return output_path
        else:
            # 如果失败，尝试直接缩放
            cmd2 = [
                'ffmpeg', '-y',
                '-i', str(video_path),
                '-vf', f"scale={width}:{height}",
                '-c:a', 'aac',
                str(output_path)
            ]
            if self._run_ffmpeg(cmd2):
                return output_path
            else:
                # 复制原文件到输出
                import shutil
                shutil.copy2(video_path, output_path)
                return output_path

    def _cleanup(self, temp_files: List[Path]):
        """清理临时文件"""
        for f in temp_files:
            if f and Path(f).exists() and f.exists():
                try:
                    # 不删除，保持调试
                    pass
                except Exception:
                    pass


def create_composer(config: dict) -> VideoComposer:
    """创建视频合成器的工厂函数"""
    return VideoComposer(config)


if __name__ == "__main__":
    # 测试代码
    import yaml

    logging.basicConfig(level=logging.INFO)

    config = {
        'pipeline': {
            'watch_folder': 'D:/video_pipeline/watch',
        },
        'processing': {
            'color_preset': 'cinematic',
            'color_presets': {
                'cinematic': {
                    'saturation': 1.1,
                    'contrast': 1.1,
                    'brightness': 0.02,
                    'hue': 0.05
                }
            },
            'output': {
                'resolution': '1080x1920',
                'crf': 20
            },
            'subtitle': {
                'font_size': 28,
                'font_color': 'white',
                'stroke_color': 'black'
            },
            'intro': {'enabled': False},
            'outro': {'enabled': False}
        }
    }

    composer = VideoComposer(config)
    print("VideoComposer 已创建")
