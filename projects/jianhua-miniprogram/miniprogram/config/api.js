// API配置文件
// 开发环境使用本地地址，生产环境使用线上地址

const DEV_API_BASE = 'http://localhost:3000/api/v1';
const PROD_API_BASE = 'https://api.yourdomain.com/api/v1'; // 改成你的域名

// 自动判断环境
const API_BASE = PROD_API_BASE; // 上线时使用这个

module.exports = {
  API_BASE,

  // 认证相关
  AUTH: {
    PHONE_LOGIN: `${API_BASE}/auth/phone-login`
  },

  // 用户相关
  USER: {
    INFO: `${API_BASE}/user/info`,
    INVITES: `${API_BASE}/user/invites`
  },

  // 礼品相关
  GIFT: {
    PROGRESS: `${API_BASE}/gift/progress`,
    CLAIM: `${API_BASE}/gift/claim`,
    LIST: `${API_BASE}/gift/list`,
    DYNAMICS: `${API_BASE}/gift/dynamics`
  },

  // 预约相关
  APPOINTMENT: {
    CREATE: `${API_BASE}/appointment/create`,
    INFO: `${API_BASE}/appointment/info`,
    CANCEL: `${API_BASE}/appointment/cancel`
  }
};
