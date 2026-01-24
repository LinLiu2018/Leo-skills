# 建华观园小程序部署指南（小白版）

## 📋 准备清单

### 1. 需要准备的东西

- [ ] 一台云服务器（推荐阿里云/腾讯云，最低配置：1核2G）
- [ ] 一个已备案的域名（如：api.yourdomain.com）
- [ ] 微信小程序账号（已认证）
- [ ] MySQL数据库（可以和服务器在一起）

### 2. 需要安装的软件

- [ ] Node.js 16+
- [ ] MySQL 5.7+
- [ ] Nginx（用于反向代理）
- [ ] PM2（用于进程管理）

---

## 第一步：服务器准备

### 1.1 购买云服务器

- 推荐：阿里云ECS或腾讯云CVM
- 配置：1核2G，带宽1M起
- 系统：Ubuntu 20.04 或 CentOS 7+

### 1.2 连接服务器

```bash
# Windows用户使用 PuTTY 或 Xshell
# Mac/Linux用户使用终端
ssh root@你的服务器IP
```

### 1.3 安装Node.js

```bash
# 下载Node.js安装脚本
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -

# 安装Node.js
sudo apt-get install -y nodejs

# 验证安装
node -v
npm -v
```

### 1.4 安装MySQL

```bash
# 安装MySQL
sudo apt-get update
sudo apt-get install mysql-server -y

# 启动MySQL
sudo systemctl start mysql
sudo systemctl enable mysql

# 设置root密码（记住这个密码！）
sudo mysql_secure_installation
```

### 1.5 安装PM2

```bash
# 全局安装PM2
sudo npm install -g pm2

# 验证安装
pm2 -v
```

### 1.6 安装Nginx

```bash
# 安装Nginx
sudo apt-get install nginx -y

# 启动Nginx
sudo systemctl start nginx
sudo systemctl enable nginx
```

---

## 第二步：数据库初始化

### 2.1 登录MySQL

```bash
mysql -u root -p
# 输入你刚才设置的密码
```

### 2.2 创建数据库

```sql
-- 在MySQL命令行中执行
CREATE DATABASE jianhua_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- 创建专用用户（更安全）
CREATE USER 'jianhua'@'localhost' IDENTIFIED BY '你的数据库密码';
GRANT ALL PRIVILEGES ON jianhua_db.* TO 'jianhua'@'localhost';
FLUSH PRIVILEGES;

-- 退出MySQL
EXIT;
```

### 2.3 导入数据表

```bash
# 上传init.sql到服务器（使用FTP工具或scp命令）
# 然后执行：
mysql -u jianhua -p jianhua_db < /path/to/init.sql
```

---

## 第三步：部署后端代码

### 3.1 上传代码到服务器

```bash
# 在服务器上创建项目目录
mkdir -p /var/www/jianhua
cd /var/www/jianhua

# 方式1：使用git（推荐）
git clone 你的代码仓库地址
cd jianhua-miniprogram/server

# 方式2：使用FTP工具上传
# 使用FileZilla等工具上传server文件夹
```

### 3.2 配置环境变量

```bash
# 复制配置文件
cp .env.example .env

# 编辑配置文件
nano .env
```

在.env文件中填写：

```env
PORT=3000
DB_HOST=localhost
DB_PORT=3306
DB_USER=jianhua
DB_PASSWORD=你的数据库密码
DB_NAME=jianhua_db
JWT_SECRET=随机生成一个长字符串
WX_APPID=你的小程序AppID
WX_SECRET=你的小程序Secret
```

保存：按 `Ctrl+X`，然后按 `Y`，再按 `Enter`

### 3.3 安装依赖

```bash
npm install
```

### 3.4 测试运行

```bash
# 测试启动
npm start

# 如果看到 "Server running on port 3000" 说明成功
# 按 Ctrl+C 停止
```

### 3.5 使用PM2启动

```bash
# 启动应用
pm2 start app.js --name jianhua-api

# 查看状态
pm2 status

# 查看日志
pm2 logs jianhua-api

# 设置开机自启
pm2 startup
pm2 save
```

---

## 第四步：配置Nginx反向代理

### 4.1 创建Nginx配置

```bash
sudo nano /etc/nginx/sites-available/jianhua
```

粘贴以下内容：

```nginx
server {
    listen 80;
    server_name api.yourdomain.com;  # 改成你的域名

    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

### 4.2 启用配置

```bash
# 创建软链接
sudo ln -s /etc/nginx/sites-available/jianhua /etc/nginx/sites-enabled/

# 测试配置
sudo nginx -t

# 重启Nginx
sudo systemctl restart nginx
```

### 4.3 配置HTTPS（必需！）

```bash
# 安装certbot
sudo apt-get install certbot python3-certbot-nginx -y

# 申请SSL证书
sudo certbot --nginx -d api.yourdomain.com

# 按提示操作，选择自动重定向HTTPS
```

---

## 第五步：微信小程序配置

### 5.1 登录微信公众平台

访问：<https://mp.weixin.qq.com>

### 5.2 配置服务器域名

1. 进入"开发" -> "开发管理" -> "开发设置"
2. 找到"服务器域名"
3. 添加：
   - request合法域名：`https://api.yourdomain.com`
   - uploadFile合法域名：`https://api.yourdomain.com`
   - downloadFile合法域名：`https://api.yourdomain.com`

### 5.3 获取AppID和Secret

1. 在"开发设置"页面找到
2. AppID：直接显示
3. AppSecret：点击"生成"并保存（只显示一次！）
4. 把这两个值填入服务器的 `.env` 文件

---

## 第六步：更新小程序前端代码

### 6.1 创建API配置文件

在小程序项目中创建 `miniprogram/config/api.js`：

```javascript
// 开发环境
const DEV_API_BASE = 'http://localhost:3000/api/v1';

// 生产环境
const PROD_API_BASE = 'https://api.yourdomain.com/api/v1';

// 根据环境自动切换
const API_BASE = process.env.NODE_ENV === 'production' ? PROD_API_BASE : DEV_API_BASE;

module.exports = {
  API_BASE,
  // API端点
  AUTH: {
    PHONE_LOGIN: `${API_BASE}/auth/phone-login`
  },
  USER: {
    INFO: `${API_BASE}/user/info`,
    INVITES: `${API_BASE}/user/invites`
  },
  GIFT: {
    PROGRESS: `${API_BASE}/gift/progress`,
    CLAIM: `${API_BASE}/gift/claim`,
    LIST: `${API_BASE}/gift/list`,
    DYNAMICS: `${API_BASE}/gift/dynamics`
  },
  APPOINTMENT: {
    CREATE: `${API_BASE}/appointment/create`,
    INFO: `${API_BASE}/appointment/info`,
    CANCEL: `${API_BASE}/appointment/cancel`
  }
};
```

### 6.2 创建请求工具

创建 `miniprogram/utils/request.js`：

```javascript
const { API_BASE } = require('../config/api');

function request(url, options = {}) {
  const token = wx.getStorageSync('token');

  return new Promise((resolve, reject) => {
    wx.request({
      url: url,
      method: options.method || 'GET',
      data: options.data || {},
      header: {
        'Content-Type': 'application/json',
        'Authorization': token ? `Bearer ${token}` : ''
      },
      success: (res) => {
        if (res.statusCode === 200) {
          resolve(res.data);
        } else if (res.statusCode === 401) {
          wx.removeStorageSync('token');
          wx.showToast({ title: '请重新登录', icon: 'none' });
          reject(res.data);
        } else {
          wx.showToast({ title: res.data.message || '请求失败', icon: 'none' });
          reject(res.data);
        }
      },
      fail: (err) => {
        wx.showToast({ title: '网络错误', icon: 'none' });
        reject(err);
      }
    });
  });
}

module.exports = { request };
```

### 6.3 更新app.js

修改 `miniprogram/app.js`，替换phoneLogin方法：

```javascript
const { request } = require('./utils/request');
const API = require('./config/api');

App({
  globalData: {
    userInfo: null,
    isLogin: false,
    inviteCode: ''
  },

  phoneLogin(code) {
    return request(API.AUTH.PHONE_LOGIN, {
      method: 'POST',
      data: {
        code: code,
        inviteCode: this.globalData.inviteCode
      }
    }).then(res => {
      if (res.success) {
        this.globalData.isLogin = true;
        this.globalData.userInfo = res.user;
        wx.setStorageSync('token', res.token);
        wx.setStorageSync('userInfo', res.user);
      }
      return res;
    });
  }
});
```

---

## 第七步：测试

### 7.1 测试后端API

```bash
# 在服务器上测试
curl https://api.yourdomain.com/health

# 应该返回：{"status":"ok","time":"..."}
```

### 7.2 测试小程序

1. 打开微信开发者工具
2. 填入真实的AppID
3. 点击"编译"
4. 测试各个功能：
   - 一键登录
   - 分享邀请
   - 预约到访
   - 个人中心

---

## 第八步：上线发布

### 8.1 小程序代码上传

1. 在微信开发者工具中点击"上传"
2. 填写版本号和备注
3. 登录微信公众平台
4. 进入"版本管理"
5. 提交审核

### 8.2 审核通过后发布

1. 审核通过后点击"发布"
2. 用户即可搜索到你的小程序

---

## 常见问题

### Q1: 数据库连接失败

```bash
# 检查MySQL是否运行
sudo systemctl status mysql

# 检查用户权限
mysql -u jianhua -p
```

### Q2: 端口被占用

```bash
# 查看3000端口占用
sudo lsof -i :3000

# 杀死进程
sudo kill -9 进程ID
```

### Q3: Nginx配置错误

```bash
# 查看错误日志
sudo tail -f /var/log/nginx/error.log

# 测试配置
sudo nginx -t
```

### Q4: PM2进程崩溃

```bash
# 查看日志
pm2 logs jianhua-api

# 重启进程
pm2 restart jianhua-api
```

### Q5: 小程序请求失败

- 检查服务器域名是否配置
- 检查HTTPS证书是否有效
- 检查API地址是否正确

---

## 监控和维护

### 查看服务状态

```bash
# 查看PM2进程
pm2 status

# 查看实时日志
pm2 logs jianhua-api --lines 100

# 查看Nginx状态
sudo systemctl status nginx
```

### 数据库备份

```bash
# 每天自动备份
crontab -e

# 添加以下行（每天凌晨2点备份）
0 2 * * * mysqldump -u jianhua -p你的密码 jianhua_db > /backup/jianhua_$(date +\%Y\%m\%d).sql
```

### 更新代码

```bash
cd /var/www/jianhua/jianhua-miniprogram/server
git pull
npm install
pm2 restart jianhua-api
```

---

## 🎉 完成

恭喜你完成部署！现在你的小程序已经可以正常运行了。

如果遇到问题，可以：

1. 查看服务器日志：`pm2 logs`
2. 查看Nginx日志：`sudo tail -f /var/log/nginx/error.log`
3. 检查数据库连接：`mysql -u jianhua -p`

祝你的小程序运营顺利！🚀
