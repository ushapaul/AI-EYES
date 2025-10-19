
import type { RouteObject } from "react-router-dom";
import NotFound from "../pages/NotFound";
import Home from "../pages/home/page";
import Login from "../pages/login/page";
import Signup from "../pages/signup/page";
import Dashboard from "../pages/dashboard/page";
import Profile from "../pages/profile/page";
import Settings from "../pages/settings/page";
import SurveillanceDashboard from "../pages/surveillance/SurveillanceDashboard";
import SurveillanceConfig from "../pages/surveillance/SurveillanceConfig";
import ProtectedRoute from "../components/ProtectedRoute";

const routes: RouteObject[] = [
  {
    path: "/",
    element: <Home />,
  },
  {
    path: "/login",
    element: <Login />,
  },
  {
    path: "/signup",
    element: <Signup />,
  },
  {
    path: "/dashboard",
    element: (
      <ProtectedRoute>
        <Dashboard />
      </ProtectedRoute>
    ),
  },
  {
    path: "/surveillance",
    element: (
      <ProtectedRoute>
        <SurveillanceDashboard />
      </ProtectedRoute>
    ),
  },
  {
    path: "/surveillance/config",
    element: (
      <ProtectedRoute>
        <SurveillanceConfig />
      </ProtectedRoute>
    ),
  },
  {
    path: "/profile",
    element: (
      <ProtectedRoute>
        <Profile />
      </ProtectedRoute>
    ),
  },
  {
    path: "/settings",
    element: (
      <ProtectedRoute>
        <Settings />
      </ProtectedRoute>
    ),
  },
  {
    path: "*",
    element: <NotFound />,
  },
];

export default routes;
