import './App.scss';
import React from "react";
import { Route,BrowserRouter,Routes, createBrowserRouter, RouterProvider } from'react-router-dom';
import ProtectedRoute from './components/ProtectedRoute/ProtectedRoute.tsx';
import { useAuthStore } from './store';
import { useUserStore } from './store';
import { useEffect } from 'react';
import { Navigate, useLocation } from "react-router-dom";
const Home = React.lazy(() => import('./pages/home/home.tsx'));
const Login = React.lazy(() => import('./pages/login/login.tsx'));
const Register = React.lazy(() => import('./pages/register/register.tsx'));
const Forget = React.lazy(() => import('./pages/forget/forget.tsx'));
const Upload = React.lazy(() => import('./pages/upload/upload.tsx'));
const Analyse = React.lazy(() => import('./pages/analyse/analyse.tsx'));
const User = React.lazy(() => import('./pages/user/user.tsx'));

function App() {
  const { isAuthenticated } = useAuthStore();
  const { fetchUserProfile, getTheme } = useUserStore();
  useEffect(() => {
    if (isAuthenticated) {
      fetchUserProfile(); // 初始化 currentUser
      getTheme(); // 初始化 userTheme
      // console.log("已登录，获取用户信息");
    }
  }, [isAuthenticated]);

const router = createBrowserRouter([

  {
      path: "*",
      element: isAuthenticated ? (
        <Navigate to="/user/market" replace />
      ) : (
        <Navigate to="/login" replace />
      ),
  },
  {
    path: '/',
    element:
      <ProtectedRoute>
        <Home />
      </ProtectedRoute> 
  },
  { 
    path: '/home',
    element:
      // <ProtectedRoute>
        <Home /> 
      // </ProtectedRoute>
  },
  { 
    path: '/login',
    element:
        <Login />
    },
  { 
    path: '/register', 
    element: 
      <Register /> 
  },
  { 
    path: '/forget', 
    element: 
      <Forget />
   },
  { 
    path: '/upload', 
    element: 
    // <ProtectedRoute>
      <Upload />
    // </ProtectedRoute>
   },
  { 
    path: '/analyse', 
    element: 
    // <ProtectedRoute>
      <Analyse />    
    // </ProtectedRoute>
   },
  { 
    path: '/user', 
    element: 
    // <ProtectedRoute>
      <User />
    // </ProtectedRoute>
   },
])
  return (
    <div className="App">
        <React.Suspense fallback={<div>Loading...</div>}>
          <RouterProvider router={router}></RouterProvider>
        </React.Suspense>      

    </div>
  );
}

export default App;
