import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { API_BASE_URL } from '../config';
import { toast } from 'react-toastify';

export default function ProgramsPage() {
  const [programs, setPrograms] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [category, setCategory] = useState('all');
  const [categories, setCategories] = useState(['all']); // Initialize with 'all'

  useEffect(() => {
    const fetchPrograms = async () => {
      try {
        console.log('Fetching programs from:', `${API_BASE_URL}/programs/`);
        
        // First, try to fetch programs
        const programsResponse = await fetch(`${API_BASE_URL}/programs/`);
        console.log('Programs response status:', programsResponse.status);
        
        if (!programsResponse.ok) {
          const errorData = await programsResponse.json().catch(() => ({}));
          console.error('Programs API error:', errorData);
          throw new Error(`Failed to fetch programs: ${programsResponse.status} ${programsResponse.statusText}`);
        }
        
        const responseData = await programsResponse.json();
        console.log('API Response data:', responseData);
        
        // Handle paginated response (results array) or direct array
        const programsData = Array.isArray(responseData) 
          ? responseData 
          : (responseData.results || []);
        
        console.log('Extracted programs:', programsData);
        
        // Try to fetch categories from a dedicated endpoint
        let categoriesData = [];
        try {
          console.log('Fetching categories from:', `${API_BASE_URL}/programs/categories/`);
          const categoriesResponse = await fetch(`${API_BASE_URL}/programs/categories/`);
          
          if (categoriesResponse.ok) {
            const categoriesRes = await categoriesResponse.json();
            console.log('Categories response:', categoriesRes);
            
            // Handle both direct array and paginated response
            const categoriesArray = Array.isArray(categoriesRes) 
              ? categoriesRes 
              : (categoriesRes.results || []);
              
            categoriesData = categoriesArray.map(cat => 
              typeof cat === 'object' && cat !== null ? cat.name || cat.category || 'Uncategorized' : String(cat)
            );
          }
        } catch (categoriesError) {
          console.warn('Error fetching categories, will extract from programs:', categoriesError);
        }
        
        // If no categories from endpoint, extract from programs
        if (categoriesData.length === 0) {
          const programCategories = programsData
            .map(p => p.category)
            .filter(Boolean)
            .map(cat => typeof cat === 'string' ? cat.trim() : String(cat).trim())
            .filter(cat => cat.length > 0);
          
          categoriesData = [...new Set(programCategories)];
        }
        
        console.log('Final programs data to set:', programsData);
        console.log('Final categories to set:', ['all', ...new Set(categoriesData)]);
        
        setPrograms(programsData);
        setCategories(['all', ...new Set(categoriesData)]);
      } catch (err) {
        console.error('Error fetching data:', err);
        const errorMsg = err.message || 'Failed to load programs. Please try again later.';
        console.error('Error details:', errorMsg);
        toast.error(errorMsg);
        setError(errorMsg);
      } finally {
        setLoading(false);
      }
    };

    fetchPrograms();
  }, []);

  // Debug log the programs and filter values
  console.log('Current programs:', programs);
  if (programs && programs.length > 0) {
    console.log('First program image URL:', programs[0].image);
    console.log('Is first program image valid?', 
      programs[0].image && 
      !programs[0].image.includes('/None/') && 
      !programs[0].image.endsWith('None') &&
      (programs[0].image.startsWith('http') || programs[0].image.startsWith('/'))
    );
  }
  console.log('Search term:', searchTerm);
  console.log('Selected category:', category);
  
  // Ensure programs is an array before filtering
  const filteredPrograms = Array.isArray(programs) ? programs.filter(program => {
    if (!program) {
      console.log('Skipping null/undefined program');
      return false;
    }
    
    console.log('Processing program:', program);
    
    const title = program.title ? String(program.title).toLowerCase().trim() : '';
    const desc = program.description ? String(program.description).toLowerCase().trim() : '';
    const programCategory = program.category ? String(program.category).toLowerCase().trim() : '';
    
    const searchTermLower = searchTerm.toLowerCase().trim();
    const matchesSearch = searchTerm === '' || 
                         title.includes(searchTermLower) || 
                         desc.includes(searchTermLower);
    
    const matchesCategory = category === 'all' || 
                          programCategory === category.toLowerCase().trim();
    
    console.log(`Program '${title}': matchesSearch=${matchesSearch}, matchesCategory=${matchesCategory}`);
    
    return matchesSearch && matchesCategory;
  }) : [];
  
  console.log('Filtered programs:', filteredPrograms);

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading programs...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center p-4">
        <div className="max-w-md w-full bg-white p-6 rounded-lg shadow-md text-center">
          <div className="text-red-500 mb-4">
            <svg xmlns="http://www.w3.org/2000/svg" className="h-12 w-12 mx-auto" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
            </svg>
          </div>
          <h2 className="text-xl font-bold text-gray-800 mb-2">Error Loading Programs</h2>
          <p className="text-gray-600 mb-6">{error}</p>
          <div className="flex justify-center space-x-4">
            <button 
              onClick={() => window.location.reload()}
              className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 transition-colors"
            >
              Try Again
            </button>
            <button 
              onClick={() => window.location.href = '/'}
              className="px-4 py-2 border border-gray-300 text-gray-700 rounded hover:bg-gray-50 transition-colors"
            >
              Back to Home
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="text-center mb-12">
          <h1 className="text-4xl font-extrabold text-gray-900 sm:text-5xl sm:tracking-tight lg:text-6xl">
            Our Programs
          </h1>
          <p className="mt-5 max-w-xl mx-auto text-xl text-gray-500">
            Discover our range of programs designed to empower and support our community.
          </p>
        </div>

        {/* Search and Filter */}
        <div className="mb-8 bg-white p-6 rounded-lg shadow-md">
          <div className="flex flex-col md:flex-row gap-4">
            <div className="flex-1">
              <label htmlFor="search" className="sr-only">Search programs</label>
              <div className="relative rounded-md shadow-sm">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <svg className="h-5 w-5 text-gray-400" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                    <path fillRule="evenodd" d="M8 4a4 4 0 100 8 4 4 0 000-8zM2 8a6 6 0 1110.89 3.476l4.817 4.817a1 1 0 01-1.414 1.414l-4.816-4.816A6 6 0 012 8z" clipRule="evenodd" />
                  </svg>
                </div>
                <input
                  type="text"
                  id="search"
                  className="focus:ring-blue-500 focus:border-blue-500 block w-full pl-10 pr-3 py-2 border border-gray-300 rounded-md"
                  placeholder="Search programs..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                />
              </div>
            </div>
            <div className="w-full md:w-64">
              <label htmlFor="category" className="sr-only">Category</label>
              <select
                id="category"
                className="block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm rounded-md"
                value={category}
                onChange={(e) => setCategory(e.target.value)}
              >
                {categories.map((cat) => (
                  <option key={cat} value={cat}>
                    {cat.charAt(0).toUpperCase() + cat.slice(1)}
                  </option>
                ))}
              </select>
            </div>
          </div>
        </div>

        {/* Programs Grid */}
        {filteredPrograms.length > 0 ? (
          <div className="grid gap-8 md:grid-cols-2 lg:grid-cols-3">
            {filteredPrograms.map((program) => (
              <div key={program.id} className="bg-white rounded-lg shadow-md overflow-hidden flex flex-col h-full">
                <div className="h-48 bg-gray-200 overflow-hidden relative">
                  {(() => {
                    // Get the image URL and clean it up
                    let imageUrl = program.image;
                    
                    // Debug: Log original URL
                    console.log('Original image URL:', imageUrl);
                    
                    // If no image URL, show placeholder
                    if (!imageUrl) {
                      console.log('No image URL provided');
                      return (
                        <div className="w-full h-full bg-gradient-to-br from-gray-100 to-gray-200 flex items-center justify-center">
                          <div className="text-center p-4">
                            <svg 
                              className="h-12 w-12 text-gray-400 mx-auto mb-2" 
                              fill="none" 
                              viewBox="0 0 24 24" 
                              stroke="currentColor"
                            >
                              <path 
                                strokeLinecap="round" 
                                strokeLinejoin="round" 
                                strokeWidth={1} 
                                d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" 
                              />
                            </svg>
                            <p className="text-sm text-gray-500">No image available</p>
                          </div>
                        </div>
                      );
                    }
                    
                    // Process the image URL
                    try {
                      // If the URL contains '/None/', try to fix it
                      if (imageUrl.includes('/None/')) {
                        console.log('Found /None/ in URL, attempting to fix...');
                        const parts = imageUrl.split('/None/');
                        if (parts.length > 1) {
                          imageUrl = parts[0] + parts[1];
                          console.log('Fixed image URL:', imageUrl);
                        }
                      }
                      
                      // If it's a relative URL, make it absolute
                      if (!imageUrl.startsWith('http') && !imageUrl.startsWith('data:')) {
                        if (imageUrl.startsWith('/')) {
                          imageUrl = `${window.location.origin}${imageUrl}`;
                        } else {
                          imageUrl = `${window.location.origin}/media/${imageUrl.replace(/^\/+/, '')}`;
                        }
                        console.log('Converted to absolute URL:', imageUrl);
                      }
                      
                      return (
                        <div className="relative w-full h-full">
                          <img 
                            src={imageUrl}
                            alt={program.title || 'Program image'}
                            className="w-full h-full object-cover hover:scale-105 transition-transform duration-300"
                            onError={(e) => {
                              console.error('Failed to load image:', imageUrl);
                              e.target.style.display = 'none';
                              const placeholder = document.createElement('div');
                              placeholder.className = 'absolute inset-0 flex items-center justify-center bg-gray-100';
                              placeholder.innerHTML = `
                                <div class="text-center p-4">
                                  <svg class="h-10 w-10 text-gray-400 mx-auto mb-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                                  </svg>
                                  <p class="text-xs text-gray-500">Image not available</p>
                                  <p class="text-xs text-red-500 mt-1 break-all">${imageUrl}</p>
                                </div>
                              `;
                              e.target.parentNode.appendChild(placeholder);
                            }}
                            onLoad={(e) => {
                              console.log('Image loaded successfully:', imageUrl);
                            }}
                          />
                        </div>
                      );
                      
                    } catch (error) {
                      console.error('Error processing image URL:', error);
                      return (
                        <div className="w-full h-full bg-gradient-to-br from-gray-100 to-gray-200 flex items-center justify-center">
                          <div className="text-center p-4">
                            <svg 
                              className="h-12 w-12 text-gray-400 mx-auto mb-2" 
                              fill="none" 
                              viewBox="0 0 24 24" 
                              stroke="currentColor"
                            >
                              <path 
                                strokeLinecap="round" 
                                strokeLinejoin="round" 
                                strokeWidth={1} 
                                d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" 
                              />
                            </svg>
                            <p className="text-sm text-gray-500">Error loading image</p>
                            <p className="text-xs text-red-500 mt-1">Please check the console for details</p>
                          </div>
                        </div>
                      );
                    }
                    
                    // Try to load the image with error handling
                    return (
                      <div className="relative w-full h-full">
                        <img 
                          src={imageUrl} 
                          alt={program.title || 'Program image'}
                          className="w-full h-full object-cover hover:scale-105 transition-transform duration-300"
                          onError={(e) => {
                            console.error('Failed to load image:', imageUrl, e);
                            // If image fails to load, show placeholder
                            e.target.style.display = 'none';
                            const placeholder = e.target.nextElementSibling;
                            if (placeholder) {
                              placeholder.style.display = 'flex';
                            }
                          }}
                          onLoad={(e) => {
                            console.log('Image loaded successfully:', imageUrl);
                          }}
                        />
                        <div 
                          className="absolute inset-0 hidden items-center justify-center bg-gradient-to-br from-gray-100 to-gray-200"
                          style={{ display: 'none' }}
                        >
                          <div className="text-center p-4">
                            <svg 
                              className="h-10 w-10 text-gray-400 mx-auto mb-2" 
                              fill="none" 
                              viewBox="0 0 24 24" 
                              stroke="currentColor"
                            >
                              <path 
                                strokeLinecap="round" 
                                strokeLinejoin="round" 
                                strokeWidth={1} 
                                d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" 
                              />
                            </svg>
                            <p className="text-xs text-gray-500">Image not available</p>
                          </div>
                        </div>
                      </div>
                    );
                  })()}
                </div>
                <div className="p-6 flex-1 flex flex-col">
                  <div className="flex-1">
                    <div className="flex justify-between items-start">
                      <h2 className="text-xl font-semibold text-gray-900 mb-2">
                        {program.title || 'Untitled Program'}
                      </h2>
                      {program.category && (
                        <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                          {program.category}
                        </span>
                      )}
                    </div>
                    <p className="text-gray-600 mb-4 line-clamp-3">
                      {program.description || 'No description available.'}
                    </p>
                    <div className="mt-4">
                      <Link
                        to={`/programs/${program.id}`}
                        className="text-blue-600 hover:text-blue-800 font-medium text-sm inline-flex items-center"
                      >
                        Learn more <span className="ml-1">→</span>
                      </Link>
                    </div>
                  </div>
                  <div className="mt-4 pt-4 border-t border-gray-200">
                    <div className="flex items-center justify-between">
                      <div className="text-sm text-gray-500">
                        <span className="font-medium">Cost:</span> {program.cost || 'Free'}
                        {program.start_date && (
                          <span className="ml-2">
                            <span className="font-medium">Starts:</span> {new Date(program.start_date).toLocaleDateString()}
                          </span>
                        )}
                      </div>
                      <Link
                        to={`/programs/${program.id}`}
                        className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
                      >
                        Learn More
                      </Link>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="text-center py-12 bg-white rounded-lg shadow">
            <svg
              className="mx-auto h-12 w-12 text-gray-400"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={1}
                d="M9.172 16.172a4 4 0 015.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
              />
            </svg>
            <h3 className="mt-2 text-lg font-medium text-gray-900">No programs found</h3>
            <p className="mt-1 text-gray-500">
              We couldn't find any programs matching your search criteria.
            </p>
            <div className="mt-6">
              <button
                type="button"
                onClick={() => {
                  setSearchTerm('');
                  setCategory('all');
                }}
                className="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
              >
                <svg className="-ml-1 mr-2 h-5 w-5" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                  <path fillRule="evenodd" d="M4 2a1 1 0 011 1v2.101a7.002 7.002 0 0111.601 2.566 1 1 0 11-1.885.666A5.002 5.002 0 005.999 7H9a1 1 0 010 2H4a1 1 0 01-1-1V3a1 1 0 011-1zm.008 9.057a1 1 0 011.276.61A5.002 5.002 0 0014.001 13H11a1 1 0 110-2h5a1 1 0 011 1v5a1 1 0 11-2 0v-2.101a7.002 7.002 0 01-11.601-2.566 1 1 0 01.61-1.276z" clipRule="evenodd" />
                </svg>
                Reset filters
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
