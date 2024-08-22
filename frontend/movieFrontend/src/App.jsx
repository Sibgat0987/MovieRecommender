import React, { useState, useEffect } from 'react';
import Select from 'react-select';

function App() {
    const [movies, setMovies] = useState([]);
    const [selectedMovie, setSelectedMovie] = useState(null);
    const [recommendations, setRecommendations] = useState([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    useEffect(() => {
        const fetchMovies = async () => {
            try {
                const response = await fetch('http://127.0.0.1:5000/movies');
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                const data = await response.json();
                const movieOptions = data.movies.map(movie => ({
                    value: movie,
                    label: movie,
                }));
                setMovies(movieOptions);
            } catch (error) {
                setError(error.message);
            }
        };

        fetchMovies();
    }, []);

    const getRecommendations = async () => {
        setLoading(true);
        setError(null);
        try {
            const response = await fetch('http://127.0.0.1:5000/recommend', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ movie: selectedMovie.value }),
            });
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            const data = await response.json();
            setRecommendations(data.recommendations);
        } catch (error) {
            setError(error.message);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className='h-screen bg-black text-white flex flex-col items-center justify-center'>
            <h1 className='text-5xl font-bold mb-4'>Movie Recommender</h1>
            <div className='w-full max-w-lg mb-4'>
                <Select
                    options={movies}
                    value={selectedMovie}
                    onChange={setSelectedMovie}
                    placeholder="Enter movie title"
                    isClearable
                    styles={{
                        control: (base) => ({
                            ...base,
                            '@apply': 'border-2 border-red-600 bg-black text-white min-h-11',
                            backgroundColor: 'black',
                            color: 'white',
                        }),
                        singleValue: (base) => ({
                            ...base,
                            '@apply': 'text-white',
                            color: 'white',
                        }),
                        input: (base) => ({
                            ...base,
                            '@apply': 'text-white',
                            color: 'white',
                        }),
                        menu: (base) => ({
                            ...base,
                            '@apply': 'bg-black text-white',
                            backgroundColor: 'black',
                            color: 'white',
                        }),
                        option: (base, state) => ({
                            ...base,
                            '@apply': state.isSelected ? 'bg-red-800' : state.isFocused ? 'bg-red-600' : 'bg-black text-white',
                            backgroundColor: state.isSelected ? 'red' : state.isFocused ? 'darkred' : 'black',
                            color: 'white',
                        }),
                        multiValue: (base) => ({
                            ...base,
                            '@apply': 'bg-red-600 text-white',
                            backgroundColor: 'red',
                            color: 'white',
                        }),
                        multiValueLabel: (base) => ({
                            ...base,
                            '@apply': 'text-white',
                            color: 'white',
                        }),
                        multiValueRemove: (base) => ({
                            ...base,
                            '@apply': 'text-white',
                            color: 'white',
                        }),
                    }}
                />
            </div>
            <button 
                onClick={getRecommendations} 
                disabled={!selectedMovie} 
                className='bg-red-600 text-white px-4 py-2 rounded hover:bg-red-800'>
                Get Recommendations
            </button>
            {loading && <p>Loading...</p>}
            {error && <p style={{ color: 'red' }}>Error: {error}</p>}
            <h2 className='mt-6 text-3xl mb-6'>Recommendations</h2>
            <div className='mt-2 flex space-x-4'>
                {recommendations.map((movie, index) => (
                    <div key={index} className='flex flex-col items-center'>
                        <img src={movie.poster_url} alt={movie.title} className='w-40 h-60 mb-2' />
                        <p>{movie.title}</p>
                    </div>
                ))}
            </div>
        </div>
    );
}

export default App;

