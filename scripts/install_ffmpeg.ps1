# FFmpeg 安装脚本
# 创建目录
if (!(Test-Path 'D:\FFmpeg\bin')) {
    New-Item -ItemType Directory -Path 'D:\FFmpeg\bin' -Force
}

# 检查是否已下载
if (!(Test-Path 'D:\ffmpeg.zip')) {
    Write-Host '正在下载 FFmpeg...'
    Invoke-WebRequest -Uri 'https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip' -OutFile 'D:\ffmpeg.zip'
}

# 解压
Write-Host '正在解压...'
Add-Type -AssemblyName System.IO.Compression.FileSystem
$zip = [System.IO.Compression.ZipFile]::OpenRead('D:\ffmpeg.zip')
foreach ($entry in $zip.Entries) {
    if ($entry.Name -match '\.exe$') {
        $destPath = 'D:\FFmpeg\bin\' + $entry.Name
        Write-Host "解压: $($entry.Name)"
        $stream = $entry.Open()
        $fileStream = [System.IO.File]::Create($destPath)
        $stream.CopyTo($fileStream)
        $fileStream.Close()
        $stream.Close()
    }
}
$zip.Dispose()

# 删除zip文件
Remove-Item 'D:\ffmpeg.zip' -ErrorAction SilentlyContinue

# 验证
Write-Host "`n验证安装..."
& 'D:\FFmpeg\bin\ffmpeg.exe' -version | Select-Object -First 3

# 设置环境变量
Write-Host "`n设置环境变量..."
$currentPath = [Environment]::GetEnvironmentVariable('Path', 'User')
if ($currentPath -notlike '*D:\FFmpeg\bin*') {
    [Environment]::SetEnvironmentVariable('Path', $currentPath + ';D:\FFmpeg\bin', 'User')
    Write-Host '环境变量已添加，请重启终端生效'
} else {
    Write-Host '环境变量已存在'
}

Write-Host "`nFFmpeg 安装完成!"
