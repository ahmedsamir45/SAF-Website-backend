import React, { useState, useEffect } from 'react';
import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000/api/blog/newsletter';

const AdminPanel = () => {
  const [subscriptions, setSubscriptions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [token, setToken] = useState(localStorage.getItem('token') || '');

  const fetchSubscriptions = async () => {
    try {
      const response = await axios.get(API_BASE_URL + '/', {
        headers: { 'Authorization': `Token ${token}` }
      });
      setSubscriptions(response.data);
      setError('');
    } catch (error) {
      setError('Failed to fetch subscriptions. Make sure you are logged in as admin.');
      console.error('Error:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (token) {
      fetchSubscriptions();
    } else {
      setLoading(false);
    }
  }, [token]);

  const handleDelete = async (email) => {
    if (window.confirm(`Are you sure you want to delete subscription for ${email}?`)) {
      try {
        await axios.delete(`${API_BASE_URL}/${email}/`, {
          headers: { 'Authorization': `Token ${token}` }
        });
        setSubscriptions(subscriptions.filter(sub => sub.email !== email));
      } catch (error) {
        console.error('Error deleting subscription:', error);
        setError('Failed to delete subscription');
      }
    }
  };

  if (!token) {
    return (
      <div className="max-w-md mx-auto p-6 bg-white rounded-lg shadow-md">
        <h2 className="text-2xl font-bold mb-4">Admin Login Required</h2>
        <p className="mb-4">Please log in to access the admin panel.</p>
        <input
          type="password"
          placeholder="Enter admin token"
          value={token}
          onChange={(e) => setToken(e.target.value)}
          className="w-full p-2 border rounded mb-2"
        />
        <button
          onClick={() => {
            localStorage.setItem('token', token);
            fetchSubscriptions();
          }}
          className="w-full bg-blue-500 text-white py-2 px-4 rounded hover:bg-blue-600"
        >
          Login
        </button>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto p-6 bg-white rounded-lg shadow-md">
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-2xl font-bold">Newsletter Subscriptions</h2>
        <button
          onClick={() => {
            localStorage.removeItem('token');
            setToken('');
          }}
          className="text-red-500 hover:text-red-700"
        >
          Logout
        </button>
      </div>

      {loading ? (
        <p>Loading subscriptions...</p>
      ) : error ? (
        <div className="p-3 bg-red-100 text-red-800 rounded">{error}</div>
      ) : (
        <div className="overflow-x-auto">
          <table className="min-w-full bg-white">
            <thead>
              <tr className="bg-gray-100">
                <th className="py-2 px-4 border-b">Email</th>
                <th className="py-2 px-4 border-b">Status</th>
                <th className="py-2 px-4 border-b">Subscribed On</th>
                <th className="py-2 px-4 border-b">Actions</th>
              </tr>
            </thead>
            <tbody>
              {subscriptions.map((sub) => (
                <tr key={sub.email} className="hover:bg-gray-50">
                  <td className="py-2 px-4 border-b">{sub.email}</td>
                  <td className="py-2 px-4 border-b">
                    <span className={`inline-block px-2 py-1 rounded-full text-xs font-semibold ${
                      sub.is_active ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'
                    }`}>
                      {sub.is_active ? 'Active' : 'Inactive'}
                    </span>
                  </td>
                  <td className="py-2 px-4 border-b">
                    {new Date(sub.created_at).toLocaleDateString()}
                  </td>
                  <td className="py-2 px-4 border-b">
                    <button
                      onClick={() => handleDelete(sub.email)}
                      className="text-red-500 hover:text-red-700"
                      title="Delete subscription"
                    >
                      Delete
                    </button>
                  </td>
                </tr>
              ))}
              {subscriptions.length === 0 && (
                <tr>
                  <td colSpan="4" className="py-4 text-center text-gray-500">
                    No subscriptions found
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
};

export default AdminPanel;
