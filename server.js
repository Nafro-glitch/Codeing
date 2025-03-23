// backend/server.js
const express = require('express');
const mongoose = require('mongoose');
const bcrypt = require('bcryptjs');
const jwt = require('jsonwebtoken');
const cors = require('cors');
const app = express();
const PORT = process.env.PORT || 5000;
const JWT_SECRET = 'your_jwt_secret'; // يُفضّل تخزينها في متغير بيئي في الإنتاج

// إعداد الميدلوير
app.use(express.json());
app.use(cors());

// تعريف نماذج Mongoose
const userSchema = new mongoose.Schema({
  username: { type: String, unique: true },
  password: String,
  role: { type: String, enum: ['admin', 'user'], default: 'user' },
  banned: { type: Boolean, default: false }
});

const courseSchema = new mongoose.Schema({
  title: String,
  description: String,
  content: String,
  createdAt: { type: Date, default: Date.now }
});

const User = mongoose.model('User', userSchema);
const Course = mongoose.model('Course', courseSchema);

// إنشاء حساب الأدمن إذا لم يكن موجوداً
const createAdmin = async () => {
  const adminUsername = 'drago44152';
  const adminPassword = 'Abdo7474@13';
  let admin = await User.findOne({ username: adminUsername });
  if (!admin) {
    const hashedPassword = await bcrypt.hash(adminPassword, 10);
    admin = new User({ username: adminUsername, password: hashedPassword, role: 'admin' });
    await admin.save();
    console.log('تم إنشاء حساب الأدمن');
  } else {
    console.log('حساب الأدمن موجود مسبقاً');
  }
};

// مسار التسجيل
app.post('/api/auth/register', async (req, res) => {
  const { username, password } = req.body;
  try {
    const hashed = await bcrypt.hash(password, 10);
    const user = new User({ username, password: hashed });
    await user.save();
    res.json({ message: 'تم التسجيل بنجاح' });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// مسار تسجيل الدخول
app.post('/api/auth/login', async (req, res) => {
  const { username, password } = req.body;
  try {
    const user = await User.findOne({ username });
    if (!user || user.banned)
      return res.status(401).json({ error: 'بيانات الدخول غير صحيحة أو الحساب محظور' });
    const isMatch = await bcrypt.compare(password, user.password);
    if (!isMatch)
      return res.status(401).json({ error: 'بيانات الدخول غير صحيحة' });
    const token = jwt.sign({ id: user._id, role: user.role }, JWT_SECRET, { expiresIn: '1d' });
    res.json({ token, user: { username: user.username, role: user.role } });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// ميدلوير للتحقق من التوكن
const authMiddleware = (req, res, next) => {
  const token = req.headers['authorization'];
  if (!token)
    return res.status(401).json({ error: 'لم يتم توفير التوكن' });
  jwt.verify(token, JWT_SECRET, (err, decoded) => {
    if (err)
      return res.status(401).json({ error: 'توكن غير صالح' });
    req.user = decoded;
    next();
  });
};

// ميدلوير للتحقق من صلاحيات الأدمن
const adminMiddleware = (req, res, next) => {
  if (req.user.role !== 'admin')
    return res.status(403).json({ error: 'تم رفض الوصول' });
  next();
};

// مسارات الدورات
app.get('/api/courses', async (req, res) => {
  const courses = await Course.find();
  res.json(courses);
});

// إضافة دورة (للمستخدمين ذوي صلاحية الأدمن فقط)
app.post('/api/courses', authMiddleware, adminMiddleware, async (req, res) => {
  const { title, description, content } = req.body;
  try {
    const course = new Course({ title, description, content });
    await course.save();
    res.json({ message: 'تم إنشاء الدورة بنجاح', course });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// مسارات الأدمن لإدارة المستخدمين (مثال على حظر المستخدم)
app.put('/api/admin/ban/:userId', authMiddleware, adminMiddleware, async (req, res) => {
  try {
    await User.findByIdAndUpdate(req.params.userId, { banned: true });
    res.json({ message: 'تم حظر المستخدم بنجاح' });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// لمسار إلغاء الحظر
app.put('/api/admin/unban/:userId', authMiddleware, adminMiddleware, async (req, res) => {
  try {
    await User.findByIdAndUpdate(req.params.userId, { banned: false });
    res.json({ message: 'تم إلغاء الحظر بنجاح' });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// الاتصال بقاعدة البيانات وتشغيل الخادم
mongoose
  .connect('mongodb://localhost:27017/dragoLearn', {
    useNewUrlParser: true,
    useUnifiedTopology: true
  })
  .then(() => {
    console.log('تم الاتصال بقاعدة البيانات');
    createAdmin();
    app.listen(PORT, () => {
      console.log(`الخادم يعمل على المنفذ ${PORT}`);
    });
  })
  .catch(err => console.log(err));
