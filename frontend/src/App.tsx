import './App.scss';
import React from "react";
import { Route,BrowserRouter,Routes, createBrowserRouter, RouterProvider } from'react-router-dom';
const Home = React.lazy(() => import('./pages/home/home.tsx'));
const Login = React.lazy(() => import('./pages/login/login.tsx'));
const Register = React.lazy(() => import('./pages/register/register.tsx'));
const Forget = React.lazy(() => import('./pages/forget/forget.tsx'));
const Upload = React.lazy(() => import('./pages/upload/upload.tsx'));
const Analyse = React.lazy(() => import('./pages/analyse/analyse.tsx'));

const router = createBrowserRouter([
  { path: '*', element: <Home /> },
  { path: '/', element: <Home /> },
  { path: '/home', element: <Home /> },
  { path: '/login', element: <Login /> },
  { path: '/register', element: <Register /> },
  { path: '/forget', element: <Forget /> },
  { path: '/upload', element: <Upload /> },
  { path: '/analyse', element: <Analyse /> },
])

function App() {
  return (
    <div className="App">
        <React.Suspense fallback={<div>Loading...</div>}>
          <RouterProvider router={router}></RouterProvider>
        </React.Suspense>      

    </div>
  );
}

export default App;
