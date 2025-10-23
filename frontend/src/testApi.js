// Test script to check API responses
const testApi = async () => {
  try {
    // Test programs endpoint
    const programsResponse = await fetch('http://localhost:8000/api/programs/');
    const programsData = await programsResponse.json();
    console.log('Programs API Response:', programsData);
    
    // Test featured programs endpoint
    const featuredResponse = await fetch('http://localhost:8000/api/programs/featured/');
    const featuredData = await featuredResponse.json();
    console.log('Featured Programs API Response:', featuredData);
    
    // Test categories endpoint
    const categoriesResponse = await fetch('http://localhost:8000/api/programs/categories/');
    const categoriesData = await categoriesResponse.json();
    console.log('Categories API Response:', categoriesData);
    
  } catch (error) {
    console.error('Error testing API:', error);
  }
};

testApi();
