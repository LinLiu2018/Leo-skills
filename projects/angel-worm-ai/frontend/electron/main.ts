import { app, BrowserWindow, ipcMain } from 'electron'
import path from 'path'

// 保持窗口对象的全局引用，防止被垃圾回收
let mainWindow: BrowserWindow | null = null

function createWindow() {
  // 创建浏览器窗口
  mainWindow = new BrowserWindow({
    width: 1400,
    height: 900,
    minWidth: 1200,
    minHeight: 700,
    title: '天使虫AI操盘手系统',
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      contextIsolation: true,
      nodeIntegration: false,
    },
    // 隐藏默认标题栏，使用自定义样式
    titleBarStyle: 'hiddenInset',
    show: false, // 先不显示，等加载完成再显示
  })

  // 加载应用
  if (process.env.VITE_DEV_SERVER_URL) {
    // 开发环境
    mainWindow.loadURL(process.env.VITE_DEV_SERVER_URL)
    mainWindow.webContents.openDevTools()
  } else {
    // 生产环境
    mainWindow.loadFile(path.join(__dirname, '../dist/index.html'))
  }

  // 窗口准备好后显示
  mainWindow.once('ready-to-show', () => {
    mainWindow?.show()
  })

  // 窗口关闭时清理引用
  mainWindow.on('closed', () => {
    mainWindow = null
  })
}

// Electron 初始化完成
app.whenReady().then(() => {
  createWindow()

  app.on('activate', () => {
    // macOS: 点击dock图标时重新创建窗口
    if (BrowserWindow.getAllWindows().length === 0) {
      createWindow()
    }
  })
})

// 所有窗口关闭时退出应用
app.on('window-all-closed', () => {
  // macOS: 除非用户主动退出，否则保持应用运行
  if (process.platform !== 'darwin') {
    app.quit()
  }
})

// IPC 通信处理
ipcMain.handle('get-app-version', () => {
  return app.getVersion()
})

ipcMain.handle('minimize-window', () => {
  mainWindow?.minimize()
})

ipcMain.handle('maximize-window', () => {
  if (mainWindow?.isMaximized()) {
    mainWindow.unmaximize()
  } else {
    mainWindow?.maximize()
  }
})

ipcMain.handle('close-window', () => {
  mainWindow?.close()
})
