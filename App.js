// frontend/src/App.js
import React, { useState } from 'react';
import { BrowserRouter as Router, Routes, Route, Link, Navigate } from 'react-router-dom';
import axios from 'axios';

const Home = () => (
  <div>
    <h1>منصة دراجو للتعلم</h1>
    <p>تعلم مهارات جديدة مع أفضل الدورات التعليمية.</p>
    <Link to="/courses">تصفح الدورات</Link>
  </div>
);

const Courses = () => {
  const [courses, setCourses] = useState([]);
  React.useEffect(() => {
    axios
      .get('http://localhost:5000/api/courses')
      .then(res => setCourses(res.data))
      .catch(err => console.error(err));
  }, []);
  return (
    <div>
      <h2>الدورات</h2>
      <ul>
        {courses.map(course => (
          <li key={course._id}>{course.title}</li>
        ))}
      </ul>
    </div>
  );
};

const Login = ({ setAuth }) => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const handleLogin = async (e) => {
    e.preventDefault();
    try {
      const res = await axios.post('http://localhost:5000/api/auth/login', { username, password });
      localStorage.setItem('token', res.data.token);
      setAuth({ user: res.data.user, token: res.data.token });
    } catch (err) {
      alert('حدث خطأ أثناء تسجيل الدخول');
    }
  };
  return (
    <div>
      <h2>تسجيل الدخول</h2>
      <form onSubmit={handleLogin}>
        <div>
          <label>اسم المستخدم:</label>
          <input value={username} onChange={e => setUsername(e.target.value)} />
        </div>
        <div>
          <label>كلمة المرور:</label>
          <input type="password" value={password} onChange={e => setPassword(e.target.value)} />
        </div>
        <button type="submit">دخول</button>
      </form>
    </div>
  );
};

const AdminDashboard = ({ auth }) => {
  const [courses, setCourses] = useState([]);
  const [newCourse, setNewCourse] = useState({ title: '', description: '', content: '' });
  
  // جلب الدورات
  React.useEffect(() => {
    axios
      .get('http://localhost:5000/api/courses')
      .then(res => setCourses(res.data))
      .catch(err => console.error(err));
  }, []);
  
  const addCourse = async () => {
    try {
      const res = await axios.post('http://localhost:5000/api/courses', newCourse, {
        headers: { Authorization: auth.token }
      });
      setCourses([...courses, res.data.course]);
      setNewCourse({ title: '', description: '', content: '' });
    } catch (err) {
      alert('حدث خطأ أثناء إضافة الدورة');
    }
  };
  
  // هنا يمكنك إضافة مكونات إضافية لإدارة المستخدمين (مثلاً عمليات الحظر والإلغاء)
  return (
    <div>
      <h2>لوحة تحكم الأدمن</h2>
      <div>
        <h3>إضافة دورة جديدة</h3>
        <input
          placeholder="عنوان الدورة"
          value={newCourse.title}
          onChange={e => setNewCourse({ ...newCourse, title: e.target.value })}
        />
        <input
          placeholder="الوصف"
          value={newCourse.description}
          onChange={e => setNewCourse({ ...newCourse, description: e.target.value })}
        />
        <textarea
          placeholder="المحتوى"
          value={newCourse.content}
          onChange={e => setNewCourse({ ...newCourse, content: e.target.value })}
        />
        <button onClick={addCourse}>إضافة الدورة</button>
      </div>
      <div>
        <h3>قائمة الدورات</h3>
        <ul>
          {courses.map(course => (
            <li key={course._id}>{course.title}</li>
          ))}
        </ul>
      </div>
      <div>
        <h3>إدارة المستخدمين</h3>
        <p>يمكن هنا تنفيذ عمليات حظر وإلغاء الحظر للمستخدمين</p>
      </div>
    </div>
  );
};

function App() {
  const [auth, setAuth] = useState(null);
  
  const logout = () => {
    localStorage.removeItem('token');
    setAuth(null);
  };
  
  return (
    <Router>
      <nav>
        <Link to="/">الرئيسية</Link> | <Link to="/courses">الدورات</Link> |{' '}
        {auth ? (
          <>
            {auth.user.role === 'admin' && <Link to="/admin">لوحة الأدمن</Link>}
            <button onClick={logout}>تسجيل الخروج</button>
          </>
        ) : (
          <Link to="/login">تسجيل الدخول</Link>
        )}
      </nav>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/courses" element={<Courses />} />
        <Route path="/login" element={<Login setAuth={setAuth} />} />
        <Route
          path="/admin"
          element={auth && auth.user.role === 'admin' ? <AdminDashboard auth={auth} /> : <Navigate to="/login" />}
        />
      </Routes>
    </Router>
  );
}

export default App;
