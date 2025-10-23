import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { API_BASE_URL } from '../config';
import NewsletterForm from '../components/NewsletterForm';

export default function HomePage() {
  const [featuredPrograms, setFeaturedPrograms] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchFeaturedPrograms = async () => {
      try {
        const response = await fetch(`${API_BASE_URL}/programs/featured/`);
        if (!response.ok) {
          throw new Error('Failed to fetch featured programs');
        }
        const data = await response.json();
        setFeaturedPrograms(data);
      } catch (err) {
        console.error('Error fetching programs:', err);
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchFeaturedPrograms();
  }, []);

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Hero Section */}
      <div className="bg-blue-700 text-white py-20">
        <div className="container mx-auto px-4 text-center">
          <h1 className="text-4xl md:text-5xl font-bold mb-4">Welcome to SAF</h1>
          <p className="text-xl mb-8">Empowering communities through education and support</p>
          <div className="space-x-4">
            <Link 
              to="/programs" 
              className="bg-white text-blue-700 px-6 py-3 rounded-lg font-medium hover:bg-blue-50 transition-colors"
            >
              Explore Programs
            </Link>
            <Link 
              to="/register" 
              className="border-2 border-white text-white px-6 py-3 rounded-lg font-medium hover:bg-white hover:bg-opacity-10 transition-colors"
            >
              Join Us
            </Link>
          </div>
        </div>
      </div>

      {/* Featured Programs */}
      <div className="py-16 bg-white">
        <div className="container mx-auto px-4">
          <h2 className="text-3xl font-bold text-center mb-12">Featured Programs</h2>
          
          {loading ? (
            <div className="flex justify-center">
              <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500"></div>
            </div>
          ) : error ? (
            <div className="text-center text-red-500">{error}</div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
              {featuredPrograms.map((program) => (
                <div key={program.id} className="bg-white rounded-lg shadow-md overflow-hidden hover:shadow-lg transition-shadow">
                  <div className="h-48 bg-gray-200">
                    {program.image && (
                      <img 
                        src={program.image} 
                        alt={program.title} 
                        className="w-full h-full object-cover"
                      />
                    )}
                  </div>
                  <div className="p-6">
                    <h3 className="text-xl font-semibold mb-2">{program.title}</h3>
                    <p className="text-gray-600 mb-4 line-clamp-3">{program.description}</p>
                    <Link 
                      to={`/programs/${program.id}`}
                      className="text-blue-600 hover:text-blue-800 font-medium"
                    >
                      Learn More →
                    </Link>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Newsletter Section */}
      <div className="py-16 bg-gray-50">
        <div className="container mx-auto px-4 max-w-3xl">
          <div className="bg-white p-8 rounded-lg shadow-md">
            <h2 className="text-2xl font-bold text-center mb-6">Stay Updated</h2>
            <p className="text-center text-gray-600 mb-8">
              Subscribe to our newsletter to receive the latest updates and news about our programs.
            </p>
            <NewsletterForm />
          </div>
        </div>
      </div>

      {/* Call to Action */}
      <div className="bg-blue-800 text-white py-16">
        <div className="container mx-auto px-4 text-center">
          <h2 className="text-3xl font-bold mb-4">Ready to Make a Difference?</h2>
          <p className="text-xl mb-8 max-w-2xl mx-auto">
            Join our community and be part of something bigger than yourself.
          </p>
          <Link 
            to="/register"
            className="bg-white text-blue-800 px-8 py-3 rounded-lg font-medium hover:bg-gray-100 transition-colors inline-block"
          >
            Get Started
          </Link>
        </div>
      </div>
    </div>
  );
}
