# -*- coding: utf-8 -*-
"""
preprocessor.py - 视频预处理模块

提取音频、检测口误和静音段，为后续剪辑做准备
"""

import os
import sys
import time
import subprocess
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

logger = logging.getLogger(__name__)


@dataclass
class CutSegment:
    """需要删除的片段"""
    start: float
    end: float
    reason: str  # "filler_word", "silence", "stutter"


@dataclass
class PreprocessResult:
    """预处理结果"""
    video_path: str
    audio_path: str
    duration: float
    has_audio: bool
    cut_segments: List[CutSegment]
    transcript: List[dict]  # Whisper/FunASR 转录结果


class VideoPreprocessor:
    """视频预处理器"""

    def __init__(self, config: dict):
        self.config = config
        self.temp_folder = Path(config.get('pipeline', {}).get('temp_folder', 'D:/video_pipeline/temp'))
        self.temp_folder.mkdir(parents=True, exist_ok=True)

    def preprocess(self, video_path: str) -> PreprocessResult:
        """
        预处理视频

        步骤：
        1. 提取音频（16kHz 单声道）
        2. 检测静音片段
        3. 语音识别（口误检测）
        4. 返回需要删除的片段列表
        """
        video_path = Path(video_path)
        logger.info(f"开始预处理: {video_path}")

        # 步骤1: 提取音频
        audio_path = self._extract_audio(video_path)

        # 步骤2: 获取视频信息
        duration = self._get_duration(video_path)
        has_audio = self._check_audio(video_path)

        # 步骤3: 检测静音
        silence_segments = self._detect_silence(audio_path)

        # 步骤4: 语音识别转录
        transcript = self._transcribe(audio_path)

        # 步骤5: 识别口误/填充词
        filler_segments = self._detect_filler_words(transcript)

        # 合并所有需要删除的片段
        all_cuts = silence_segments + filler_segments

        result = PreprocessResult(
            video_path=str(video_path),
            audio_path=str(audio_path),
            duration=duration,
            has_audio=has_audio,
            cut_segments=all_cuts,
            transcript=transcript
        )

        logger.info(f"预处理完成，检测到 {len(all_cuts)} 个需删除片段")
        return result

    def _run_ffmpeg(self, args: List[str], timeout: int = 300) -> Tuple[bool, str, str]:
        """执行 FFmpeg 命令"""
        try:
            result = subprocess.run(
                args,
                capture_output=True,
                text=True,
                timeout=timeout,
                encoding='utf-8',
                errors='ignore'
            )
            return result.returncode == 0, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            return False, "", "命令执行超时"
        except Exception as e:
            return False, "", str(e)

    def _extract_audio(self, video_path: Path) -> Path:
        """提取音频为 16kHz 单声道 WAV"""
        audio_path = self.temp_folder / f"{video_path.stem}_audio.wav"

        if audio_path.exists():
            logger.info(f"音频已存在: {audio_path}")
            return audio_path

        # FFmpeg 提取音频命令
        cmd = [
            'ffmpeg', '-y',
            '-i', str(video_path),
            '-vn',  # 不要视频
            '-acodec', 'pcm_s16le',  # 16-bit PCM
            '-ar', '16000',  # 16kHz 采样率
            '-ac', '1',  # 单声道
            str(audio_path)
        ]

        success, stdout, stderr = self._run_ffmpeg(cmd)
        if success:
            logger.info(f"音频提取成功: {audio_path}")
        else:
            logger.error(f"音频提取失败: {stderr}")

        return audio_path

    def _get_duration(self, video_path: Path) -> float:
        """获取视频时长（秒）"""
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
        except Exception as e:
            logger.error(f"获取视频时长失败: {e}")
            return 0.0

    def _check_audio(self, video_path: Path) -> bool:
        """检查视频是否有音频轨道"""
        cmd = [
            'ffprobe',
            '-v', 'error',
            '-show_entries', 'stream=codec_type',
            '-of', 'json',
            str(video_path)
        ]

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            data = json.loads(result.stdout)
            for stream in data.get('streams', []):
                if stream.get('codec_type') == 'audio':
                    return True
            return False
        except Exception:
            return False

    def _detect_silence(self, audio_path: Path, threshold: str = "-40dB", min_duration: float = 0.5) -> List[CutSegment]:
        """检测静音片段"""
        silence_segments = []

        # 使用 FFmpeg 的 silencedetect 滤镜
        cmd = [
            'ffmpeg', '-y',
            '-i', str(audio_path),
            '-af', f'silencedetect=noise={threshold}:d={min_duration}',
            '-f', 'null',
            '-'
        ]

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            output = result.stderr

            # 解析静音检测结果
            import re
            # 查找 silence_start 和 silence_end
            starts = re.findall(r'silence_start: ([\d.]+)', output)
            ends = re.findall(r'silence_end: ([\d.]+)', output)

            for i, (start, end) in enumerate(zip(starts, ends)):
                silence_segments.append(CutSegment(
                    start=float(start),
                    end=float(end),
                    reason="silence"
                ))

            logger.info(f"检测到 {len(silence_segments)} 个静音片段")

        except Exception as e:
            logger.error(f"静音检测失败: {e}")

        return silence_segments

    def _transcribe(self, audio_path: Path) -> List[dict]:
        """语音识别转录"""
        transcript = []

        # 优先使用 FunASR
        asr_engine = self.config.get('processing', {}).get('asr', {}).get('engine', 'funasr')

        if asr_engine == 'funasr':
            transcript = self._transcribe_funasr(audio_path)
        else:
            transcript = self._transcribe_whisper(audio_path)

        return transcript

    def _transcribe_funasr(self, audio_path: Path) -> List[dict]:
        """使用 FunASR 转录"""
        try:
            from funasr import FunASR

            model = FunASR()
            result = model.generate(
                str(audio_path),
                model='paraformer-zh',
                batch_size_s=300
            )

            # 解析结果
            if isinstance(result, list) and len(result) > 0:
                # FunASR 返回格式处理
                transcript = []
                for item in result:
                    if isinstance(item, dict):
                        text = item.get('text', '')
                        time_offset = item.get('time_offset', 0.0)

                        # 简化处理：每个句子作为一个片段
                        if text.strip():
                            transcript.append({
                                'text': text.strip(),
                                'start': time_offset,
                                'end': time_offset + 3.0,  # 估算时长
                            })
                return transcript

        except ImportError:
            logger.warning("FunASR 未安装，将使用 Whisper")
        except Exception as e:
            logger.error(f"FunASR 转录失败: {e}")

        return self._transcribe_whisper(audio_path)

    def _transcribe_whisper(self, audio_path: Path) -> List[dict]:
        """使用 OpenAI Whisper 转录"""
        try:
            import whisper
            import numpy as np

            model = whisper.load_model("medium")
            result = model.transcribe(str(audio_path), language="zh")

            transcript = []
            for segment in result.get('segments', []):
                transcript.append({
                    'text': segment['text'].strip(),
                    'start': segment['start'],
                    'end': segment['end'],
                })

            logger.info(f"Whisper 转录完成: {len(transcript)} 个片段")
            return transcript

        except ImportError:
            logger.error("Whisper 未安装，请运行: pip install openai-whisper")
            return []
        except Exception as e:
            logger.error(f"Whisper 转录失败: {e}")
            return []

    def _detect_filler_words(self, transcript: List[dict]) -> List[CutSegment]:
        """检测填充词/口误"""
        filler_segments = []

        # 填充词列表
        filler_words = {'嗯', '啊', '呃', '哦', '这个', '那个', '就是说', '然后', '然后呢',
                        'umm', 'uh', 'uhm', 'ah', 'er', 'like', 'you know'}

        for i, segment in enumerate(transcript):
            text = segment.get('text', '')

            # 检测纯填充词片段（如"嗯"、"啊"等单独成句）
            if text.strip() in filler_words:
                filler_segments.append(CutSegment(
                    start=segment['start'],
                    end=segment['end'],
                    reason="filler_word"
                ))

        logger.info(f"检测到 {len(filler_segments)} 个填充词片段")
        return filler_segments


def create_preprocessor(config: dict) -> VideoPreprocessor:
    """创建预处理器的工厂函数"""
    return VideoPreprocessor(config)


if __name__ == "__main__":
    # 测试代码
    import yaml

    logging.basicConfig(level=logging.INFO)

    config = {
        'pipeline': {
            'temp_folder': 'D:/video_pipeline/temp'
        },
        'processing': {
            'asr': {
                'engine': 'whisper'
            }
        }
    }

    preprocessor = VideoPreprocessor(config)
    print("VideoPreprocessor 已创建")
