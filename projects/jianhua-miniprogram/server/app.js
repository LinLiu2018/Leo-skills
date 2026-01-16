require('dotenv').config();
const express = require('express');
const cors = require('cors');

const authRoutes = require('./routes/auth');
const userRoutes = require('./routes/user');
const giftRoutes = require('./routes/gift');
const appointmentRoutes = require('./routes/appointment');

const app = express();

app.use(cors());
app.use(express.json());

// 路由
app.use('/api/v1/auth', authRoutes);
app.use('/api/v1/user', userRoutes);
app.use('/api/v1/gift', giftRoutes);
app.use('/api/v1/appointment', appointmentRoutes);

// 健康检查
app.get('/health', (req, res) => {
  res.json({ status: 'ok', time: new Date().toISOString() });
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});
