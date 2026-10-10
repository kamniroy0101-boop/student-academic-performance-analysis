import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/useAuth';

export default function Navbar({ title }: { title: string }) {
  const { logout } = useAuth();
  const navigate = useNavigate();

  function handleLogout() {
    logout();
    navigate('/login');
  }

  return (
    <nav className="bg-white border-b border-gray-200 px-6 py-3 flex items-center justify-between shadow-sm">
      <h1 className="text-lg font-bold text-gray-800">{title}</h1>
      <button
        onClick={handleLogout}
        className="text-sm text-red-500 hover:text-red-700 font-medium transition"
      >
        Logout
      </button>
    </nav>
  );
}
