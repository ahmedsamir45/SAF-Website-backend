import React, { useState } from 'react';
import { subscribeToNewsletter, confirmSubscription } from '../services/newsletterApi';

const SubscribePage = () => {
  const [email, setEmail] = useState('');
  const [confirmationCode, setConfirmationCode] = useState('');
  const [message, setMessage] = useState({ text: '', type: '' });
  const [showConfirmation, setShowConfirmation] = useState(false);
  const [isLoading, setIsLoading] = useState(false);

  const handleSubscribe = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    setMessage({ text: '', type: '' });
    
    try {
      await subscribeToNewsletter(email);
      setShowConfirmation(true);
      setMessage({
        text: 'Confirmation email sent! Please check your inbox.',
        type: 'success'
      });
    } catch (error) {
      setMessage({
        text: error.response?.data?.email?.[0] || 'An error occurred while subscribing.',
        type: 'error'
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleConfirm = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    setMessage({ text: '', type: '' });
    
    try {
      await confirmSubscription(email, confirmationCode);
      setMessage({
        text: 'Thank you for subscribing to our newsletter!',
        type: 'success'
      });
      setShowConfirmation(false);
      setEmail('');
      setConfirmationCode('');
    } catch (error) {
      setMessage({
        text: error.response?.data?.detail || 'Invalid confirmation code. Please try again.',
        type: 'error'
      });
    } finally {
      setIsLoading(false);
    }
  };

  const Alert = ({ message }) => (
    <div className={`rounded-md p-4 mb-4 ${
      message.type === 'error' 
        ? 'bg-red-50 text-red-700' 
        : 'bg-green-50 text-green-700'
    }`}>
      <p className="text-sm">{message.text}</p>
    </div>
  );

  return (
    <div className="bg-white shadow overflow-hidden sm:rounded-lg">
      <div className="px-4 py-5 sm:p-6">
        <h2 className="text-2xl font-bold text-gray-900 mb-6">Subscribe to Our Newsletter</h2>
        
        {message.text && <Alert message={message} />}
        
        {!showConfirmation ? (
          <form onSubmit={handleSubscribe} className="space-y-6">
            <div>
              <label htmlFor="email" className="block text-sm font-medium text-gray-700">
                Email address
              </label>
              <div className="mt-1">
                <input
                  id="email"
                  name="email"
                  type="email"
                  autoComplete="email"
                  required
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="appearance-none block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                  placeholder="you@example.com"
                />
              </div>
            </div>

            <div>
              <button
                type="submit"
                disabled={isLoading}
                className="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {isLoading ? 'Subscribing...' : 'Subscribe'}
              </button>
            </div>
          </form>
        ) : (
          <form onSubmit={handleConfirm} className="space-y-6">
            <div>
              <label htmlFor="confirmationCode" className="block text-sm font-medium text-gray-700">
                Confirmation Code
              </label>
              <div className="mt-1">
                <input
                  id="confirmationCode"
                  name="confirmationCode"
                  type="text"
                  required
                  value={confirmationCode}
                  onChange={(e) => setConfirmationCode(e.target.value)}
                  className="appearance-none block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                  placeholder="Enter the code sent to your email"
                />
              </div>
            </div>

            <div className="flex space-x-3">
              <button
                type="submit"
                disabled={isLoading}
                className="flex-1 justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {isLoading ? 'Confirming...' : 'Confirm Subscription'}
              </button>
              <button
                type="button"
                onClick={() => {
                  setShowConfirmation(false);
                  setMessage({ text: '', type: '' });
                }}
                className="flex-1 justify-center py-2 px-4 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
              >
                Cancel
              </button>
            </div>
          </form>
        )}
      </div>
    </div>
  );
};

export default SubscribePage;
