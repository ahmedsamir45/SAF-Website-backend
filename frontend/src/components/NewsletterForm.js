import React, { useState, useEffect } from 'react';
import { 
  subscribeToNewsletter, 
  confirmSubscription,
  checkSubscriptionStatus
} from '../services/newsletterApi';

const NewsletterForm = () => {
  const [email, setEmail] = useState('');
  const [message, setMessage] = useState({ text: '', type: '' });
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [confirmationCode, setConfirmationCode] = useState('');
  const [showConfirmation, setShowConfirmation] = useState(false);
  const [isCheckingStatus, setIsCheckingStatus] = useState(false);
  const [isSubscribed, setIsSubscribed] = useState(false);

  // ✅ Added: function to clear message (fixes the undefined error)
  const clearMessage = () => setMessage({ text: '', type: '' });

  // Check subscription status when component mounts or email changes
  useEffect(() => {
    const checkStatus = async () => {
      if (!email) return;
      
      try {
        setIsCheckingStatus(true);
        const response = await checkSubscriptionStatus(email);
        setIsSubscribed(response.data.is_active);
        
        if (response.data.is_active) {
          setMessage({ 
            text: 'You are already subscribed to our newsletter!', 
            type: 'success' 
          });
        } else if (response.data.email) {
          setShowConfirmation(true);
          setMessage({ 
            text: 'Please check your email to confirm your subscription.', 
            type: 'info' 
          });
        }
      } catch {
        console.log('No existing subscription found');
      } finally {
        setIsCheckingStatus(false);
      }
    };

    // Debounce: wait 1 second before checking
    const timer = setTimeout(() => {
      if (email && email.includes('@')) checkStatus();
    }, 1000);

    return () => clearTimeout(timer);
  }, [email]);

  const handleSubscribe = async (e) => {
    e.preventDefault();
    
    if (!email) {
      setMessage({ text: 'Please enter your email', type: 'error' });
      return;
    }

    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
      setMessage({ text: 'Please enter a valid email address', type: 'error' });
      return;
    }

    setIsSubmitting(true);
    setMessage({ text: '', type: '' });
    
    try {
      const response = await subscribeToNewsletter(email);
      
      setMessage({ 
        text: response.data.detail || 'Confirmation email sent! Please check your inbox.', 
        type: 'success' 
      });
      
      if (response.data.requires_confirmation !== false) {
        setShowConfirmation(true);
      } else {
        setIsSubscribed(true);
      }
    } catch (error) {
      console.error('Subscription error:', error);
      
      const errorMessage = error.response?.data?.email?.[0] || 
                           error.response?.data?.detail || 
                           error.message ||
                           'An error occurred while subscribing. Please try again later.';
      
      setMessage({ text: errorMessage, type: 'error' });
      
      if (error.response?.status === 400 && error.response.data?.email?.[0]?.includes('already subscribed')) {
        setIsSubscribed(true);
      }
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleConfirm = async (e) => {
    e.preventDefault();
    
    if (!confirmationCode) {
      setMessage({ text: 'Please enter the confirmation code', type: 'error' });
      return;
    }

    setIsSubmitting(true);
    setMessage({ text: 'Confirming your subscription...', type: 'info' });
    
    try {
      const response = await confirmSubscription(email, confirmationCode);
      
      setMessage({ 
        text: response.data.detail || 'Subscription confirmed successfully!', 
        type: 'success' 
      });
      
      setIsSubscribed(true);
      setShowConfirmation(false);
      
      setTimeout(() => {
        setEmail('');
        setConfirmationCode('');
        clearMessage();
      }, 3000);
      
    } catch (error) {
      console.error('Confirmation error:', error);
      
      const errorMessage = error.response?.data?.detail || 
                           error.response?.data?.confirmation_code?.[0] ||
                           error.message ||
                           'Invalid confirmation code. Please try again.';
      
      setMessage({ text: errorMessage, type: 'error' });
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleResetForm = () => {
    setEmail('');
    setConfirmationCode('');
    setShowConfirmation(false);
    clearMessage();
  };

  const getMessageClass = (type) => {
    const base = 'mt-4 p-3 rounded transition-all duration-300';
    switch (type) {
      case 'error': return `${base} bg-red-100 text-red-800 border-l-4 border-red-500`;
      case 'success': return `${base} bg-green-100 text-green-800 border-l-4 border-green-500`;
      case 'info': return `${base} bg-blue-50 text-blue-800 border-l-4 border-blue-500`;
      default: return `${base} bg-gray-100 text-gray-800`;
    }
  };

  // === UI Rendering ===

  if (isCheckingStatus) {
    return (
      <div className="max-w-md mx-auto p-6 bg-white rounded-lg shadow-md text-center">
        <div className="animate-pulse">
          <div className="h-6 bg-gray-200 rounded w-3/4 mx-auto mb-4"></div>
          <div className="h-4 bg-gray-200 rounded w-1/2 mx-auto"></div>
        </div>
      </div>
    );
  }

  if (isSubscribed) {
    return (
      <div className="max-w-md mx-auto p-6 bg-white rounded-lg shadow-md text-center">
        <div className="text-green-500 mb-4">
          <svg 
            className="w-16 h-16 mx-auto" 
            fill="none" 
            stroke="currentColor" 
            viewBox="0 0 24 24"
          >
            <path 
              strokeLinecap="round" 
              strokeLinejoin="round" 
              strokeWidth="2" 
              d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
            ></path>
          </svg>
        </div>
        <h2 className="text-2xl font-bold mb-2">You're Subscribed!</h2>
        <p className="text-gray-600 mb-6">Thank you for subscribing to our newsletter.</p>
        <button
          onClick={handleResetForm}
          className="text-blue-500 hover:text-blue-600 font-medium focus:outline-none"
        >
          Subscribe with a different email
        </button>
      </div>
    );
  }

  return (
    <div className="max-w-md mx-auto p-6 bg-white rounded-lg shadow-md">
      <h2 className="text-2xl font-bold mb-4 text-gray-800">
        {showConfirmation ? 'Confirm Your Subscription' : 'Subscribe to Our Newsletter'}
      </h2>
      
      <p className="text-gray-600 mb-6">
        {showConfirmation 
          ? 'We\'ve sent a confirmation code to your email. Please enter it below to verify your subscription.'
          : 'Stay updated with our latest news, offers, and updates. No spam, we promise!'}
      </p>
      
      {!showConfirmation ? (
        <form onSubmit={handleSubscribe} className="space-y-4">
          <div>
            <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-1">
              Email Address
            </label>
            <div className="relative">
              <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                <svg className="h-5 w-5 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path 
                    strokeLinecap="round" 
                    strokeLinejoin="round" 
                    strokeWidth="1.5" 
                    d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"
                  />
                </svg>
              </div>
              <input
                type="email"
                id="email"
                value={email}
                onChange={(e) => setEmail(e.target.value.trim())}
                className="block w-full pl-10 pr-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                placeholder="your@email.com"
                required
                disabled={isSubmitting}
                autoComplete="email"
              />
            </div>
          </div>
          
          <button
            type="submit"
            disabled={isSubmitting || !email}
            className={`w-full flex justify-center py-2 px-4 rounded-md text-sm font-medium text-white ${
              isSubmitting || !email
                ? 'bg-blue-400 cursor-not-allowed'
                : 'bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500'
            }`}
          >
            {isSubmitting ? (
              <>
                <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                Processing...
              </>
            ) : (
              'Subscribe Now'
            )}
          </button>
          
          <p className="text-xs text-gray-500 text-center">
            We respect your privacy. Unsubscribe at any time.
          </p>
        </form>
      ) : (
        <form onSubmit={handleConfirm} className="space-y-4">
          <div>
            <label htmlFor="confirmationCode" className="block text-sm font-medium text-gray-700 mb-1">
              Confirmation Code
            </label>
            <input
              type="text"
              id="confirmationCode"
              value={confirmationCode}
              onChange={(e) => setConfirmationCode(e.target.value.trim())}
              className="block w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              placeholder="Enter the code from your email"
              required
              disabled={isSubmitting}
              autoComplete="one-time-code"
            />
            <p className="mt-1 text-xs text-gray-500">
              Check your email for the confirmation code we just sent to {email}
            </p>
          </div>
          
          <div className="flex space-x-2">
            <button
              type="button"
              onClick={() => setShowConfirmation(false)}
              className="flex-1 bg-gray-300 text-gray-800 py-2 px-4 rounded hover:bg-gray-400 focus:outline-none focus:ring-2 focus:ring-gray-500 focus:ring-offset-2 transition-colors"
            >
              Back
            </button>
            <button
              type="submit"
              disabled={isSubmitting || !confirmationCode}
              className="flex-1 bg-green-500 text-white py-2 px-4 rounded hover:bg-green-600 disabled:opacity-50 focus:outline-none focus:ring-2 focus:ring-green-500 focus:ring-offset-2 transition-colors"
            >
              {isSubmitting ? 'Confirming...' : 'Confirm'}
            </button>
          </div>
        </form>
      )}

      {message.text && (
        <div className={getMessageClass(message.type)}>
          {message.text}
        </div>
      )}
    </div>
  );
};

export default NewsletterForm;
