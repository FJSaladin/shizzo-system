import Sidebar from './Sidebar';
import Navbar from './Navbar';

export default function Layout({ children }) {
  return (
    <div className="min-h-screen bg-gray-100">
      <Sidebar />
      <div className="ml-64">
        <Navbar />
        <main className="pt-16">
          <div className="p-6">
            {console.log('Layout children:', children)}
            {children}
          </div>
        </main>
      </div>
    </div>
  );
}