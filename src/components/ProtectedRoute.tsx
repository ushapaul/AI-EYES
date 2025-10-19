import { Navigate } from 'react-router-dom';

interface ProtectedRouteProps {
  children: React.ReactNode;
}

export default function ProtectedRoute({ children }: ProtectedRouteProps) {
  // Check if user is logged in
  const user = localStorage.getItem('user');
  
  if (!user || user === 'undefined' || user === 'null') {
    // User is not logged in, redirect to login page
    return <Navigate to="/login" replace />;
  }

  // User is logged in, render the protected content
  return <>{children}</>;
}
